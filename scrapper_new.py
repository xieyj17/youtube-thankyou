from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import requests
import time

def parse_currency(amount_str):
    if not amount_str or not amount_str.strip():
        return None, 0
    
    amount_str = amount_str.strip()
    
    # Comprehensive currency map (100+ currencies)
    currency_map = {
        # Dollar variants (check longer symbols first)
        'A$': 'AUD', 'AU$': 'AUD', 'AUD$': 'AUD', 'AUD ': 'AUD',
        'CA$': 'CAD', 'C$': 'CAD', 'CAD$': 'CAD', 'CAD ': 'CAD',
        'US$': 'USD', 'USD$': 'USD', 'USD ': 'USD',
        'NZ$': 'NZD', 'NZD$': 'NZD', 'NZD ': 'NZD',
        'HK$': 'HKD', 'HKD$': 'HKD', 'HKD ': 'HKD',
        'S$': 'SGD', 'SG$': 'SGD', 'SGD$': 'SGD', 'SGD ': 'SGD',
        'NT$': 'TWD', 'TWD$': 'TWD', 'TWD ': 'TWD',
        'MX$': 'MXN', 'MXN$': 'MXN', 'MXN ': 'MXN',
        'BR$': 'BRL', 'R$': 'BRL', 'BRL ': 'BRL',
        'AR$': 'ARS', 'ARS ': 'ARS',
        'CL$': 'CLP', 'CLP ': 'CLP',
        'CO$': 'COP', 'COP ': 'COP',
        'TT$': 'TTD', 'TTD ': 'TTD',
        'BB$': 'BBD', 'BBD ': 'BBD',
        'BZ$': 'BZD', 'BZD ': 'BZD',
        'J$': 'JMD', 'JMD ': 'JMD',
        'Z$': 'ZWL', 'ZWL ': 'ZWL',
        'L$': 'LRD', 'LRD ': 'LRD',
        'NAD ': 'NAD', 'N$': 'NAD',
        'FJ$': 'FJD', 'FJD ': 'FJD',
        'EC$': 'XCD', 'XCD ': 'XCD',
        '$': 'USD',  # Default dollar to USD
        
        # Euro
        '€': 'EUR', 'EUR': 'EUR', 'EUR ': 'EUR',
        
        # Pound variants
        '£': 'GBP', 'GBP': 'GBP', 'GBP ': 'GBP',
        'EGP': 'EGP', 'EGP ': 'EGP', 'E£': 'EGP',
        'LBP': 'LBP', 'LBP ': 'LBP', 'L£': 'LBP',
        'SYP': 'SYP', 'SYP ': 'SYP', 'S£': 'SYP',
        
        # Yen/Yuan variants
        '¥': 'JPY', 'JPY': 'JPY', 'JPY ': 'JPY', '円': 'JPY',
        'CNY': 'CNY', 'CNY ': 'CNY', 'RMB': 'CNY', '元': 'CNY',
        
        # Rupee variants
        '₹': 'INR', 'INR': 'INR', 'INR ': 'INR', '₨': 'INR', 'Rs.': 'INR', 'Rs ': 'INR',
        'PKR': 'PKR', 'PKR ': 'PKR',
        'LKR': 'LKR', 'LKR ': 'LKR',
        'NPR': 'NPR', 'NPR ': 'NPR',
        'BTN': 'BTN', 'BTN ': 'BTN',
        'MVR': 'MVR', 'MVR ': 'MVR',
        'SCR': 'SCR', 'SCR ': 'SCR',
        'MUR': 'MUR', 'MUR ': 'MUR',
        'IDR': 'IDR', 'IDR ': 'IDR', 'Rp': 'IDR', 'Rp ': 'IDR',
        
        # Won/Korean
        '₩': 'KRW', 'KRW': 'KRW', 'KRW ': 'KRW', '원': 'KRW',
        'KPW': 'KPW', 'KPW ': 'KPW',
        
        # Ruble variants
        '₽': 'RUB', 'RUB': 'RUB', 'RUB ': 'RUB', 'руб': 'RUB',
        'BYN': 'BYN', 'BYN ': 'BYN',
        
        # Middle East/Africa
        '₪': 'ILS', 'ILS': 'ILS', 'ILS ': 'ILS', 'NIS': 'ILS',
        'AED': 'AED', 'AED ': 'AED', 'DH': 'AED', 'د.إ': 'AED',
        'SAR': 'SAR', 'SAR ': 'SAR', 'SR': 'SAR', 'ر.س': 'SAR',
        'QAR': 'QAR', 'QAR ': 'QAR', 'ر.ق': 'QAR',
        'OMR': 'OMR', 'OMR ': 'OMR', 'ر.ع.': 'OMR',
        'BHD': 'BHD', 'BHD ': 'BHD', '.د.ب': 'BHD',
        'KWD': 'KWD', 'KWD ': 'KWD', 'د.ك': 'KWD',
        'JOD': 'JOD', 'JOD ': 'JOD', 'د.أ': 'JOD',
        'IRR': 'IRR', 'IRR ': 'IRR', '﷼': 'IRR',
        'AFN': 'AFN', 'AFN ': 'AFN', '؋': 'AFN',
        
        # African currencies
        'ZAR': 'ZAR', 'ZAR ': 'ZAR', 'R ': 'ZAR',
        'NGN': 'NGN', 'NGN ': 'NGN', '₦': 'NGN',
        'GHS': 'GHS', 'GHS ': 'GHS', '₵': 'GHS',
        'KES': 'KES', 'KES ': 'KES', 'KSh': 'KES',
        'UGX': 'UGX', 'UGX ': 'UGX', 'USh': 'UGX',
        'TZS': 'TZS', 'TZS ': 'TZS', 'TSh': 'TZS',
        'ETB': 'ETB', 'ETB ': 'ETB',
        'MAD': 'MAD', 'MAD ': 'MAD', 'DH': 'MAD',
        'TND': 'TND', 'TND ': 'TND', 'د.ت': 'TND',
        'DZD': 'DZD', 'DZD ': 'DZD', 'د.ج': 'DZD',
        'EGP': 'EGP', 'EGP ': 'EGP', 'ج.م': 'EGP',
        'BWP': 'BWP', 'BWP ': 'BWP', 'P': 'BWP',
        'ZMW': 'ZMW', 'ZMW ': 'ZMW',
        'MWK': 'MWK', 'MWK ': 'MWK',
        'LSL': 'LSL', 'LSL ': 'LSL',
        'SZL': 'SZL', 'SZL ': 'SZL',
        
        # Southeast Asia
        '₫': 'VND', 'VND': 'VND', 'VND ': 'VND', 'đ': 'VND',
        '₱': 'PHP', 'PHP': 'PHP', 'PHP ': 'PHP', '₱': 'PHP',
        'MYR': 'MYR', 'MYR ': 'MYR', 'RM': 'MYR', 'RM ': 'MYR',
        'THB': 'THB', 'THB ': 'THB', '฿': 'THB',
        'LAK': 'LAK', 'LAK ': 'LAK', '₭': 'LAK',
        'KHR': 'KHR', 'KHR ': 'KHR', '៛': 'KHR',
        'MMK': 'MMK', 'MMK ': 'MMK',
        'BND': 'BND', 'BND ': 'BND', 'B$': 'BND',
        
        # European currencies
        'CHF': 'CHF', 'CHF ': 'CHF', 'Fr': 'CHF', 'SFr': 'CHF',
        'SEK': 'SEK', 'SEK ': 'SEK', 'kr': 'SEK',
        'NOK': 'NOK', 'NOK ': 'NOK',
        'DKK': 'DKK', 'DKK ': 'DKK',
        'PLN': 'PLN', 'PLN ': 'PLN', 'zł': 'PLN',
        'CZK': 'CZK', 'CZK ': 'CZK', 'Kč': 'CZK',
        'HUF': 'HUF', 'HUF ': 'HUF', 'Ft': 'HUF',
        'RON': 'RON', 'RON ': 'RON', 'lei': 'RON',
        'BGN': 'BGN', 'BGN ': 'BGN', 'лв': 'BGN',
        'HRK': 'HRK', 'HRK ': 'HRK', 'kn': 'HRK',
        'RSD': 'RSD', 'RSD ': 'RSD', 'дин': 'RSD',
        'BAM': 'BAM', 'BAM ': 'BAM', 'KM': 'BAM',
        'MKD': 'MKD', 'MKD ': 'MKD', 'ден': 'MKD',
        'ALL': 'ALL', 'ALL ': 'ALL', 'L': 'ALL',
        'ISK': 'ISK', 'ISK ': 'ISK',
        'UAH': 'UAH', 'UAH ': 'UAH', '₴': 'UAH',
        'MDL': 'MDL', 'MDL ': 'MDL',
        'GEL': 'GEL', 'GEL ': 'GEL', '₾': 'GEL',
        'AMD': 'AMD', 'AMD ': 'AMD', '֏': 'AMD',
        'AZN': 'AZN', 'AZN ': 'AZN', '₼': 'AZN',
        
        # Turkish Lira
        'TRY': 'TRY', 'TRY ': 'TRY', '₺': 'TRY', 'TL': 'TRY',
        
        # Latin America
        'CLP': 'CLP', 'CLP ': 'CLP',
        'COP': 'COP', 'COP ': 'COP',
        'PEN': 'PEN', 'PEN ': 'PEN', 'S/': 'PEN',
        'BOB': 'BOB', 'BOB ': 'BOB', 'Bs': 'BOB',
        'UYU': 'UYU', 'UYU ': 'UYU', '$U': 'UYU',
        'PYG': 'PYG', 'PYG ': 'PYG', '₲': 'PYG',
        'VES': 'VES', 'VES ': 'VES', 'Bs.S': 'VES',
        'GYD': 'GYD', 'GYD ': 'GYD', 'G$': 'GYD',
        'SRD': 'SRD', 'SRD ': 'SRD', 'Sr$': 'SRD',
        'GTQ': 'GTQ', 'GTQ ': 'GTQ', 'Q': 'GTQ',
        'HNL': 'HNL', 'HNL ': 'HNL', 'L': 'HNL',
        'NIO': 'NIO', 'NIO ': 'NIO', 'C$': 'NIO',
        'CRC': 'CRC', 'CRC ': 'CRC', '₡': 'CRC',
        'PAB': 'PAB', 'PAB ': 'PAB', 'B/.': 'PAB',
        'DOP': 'DOP', 'DOP ': 'DOP', 'RD$': 'DOP',
        'HTG': 'HTG', 'HTG ': 'HTG', 'G': 'HTG',
        'CUP': 'CUP', 'CUP ': 'CUP',
        
        # Oceania
        'FJD': 'FJD', 'FJD ': 'FJD', 'FJ$': 'FJD',
        'TOP': 'TOP', 'TOP ': 'TOP', 'T$': 'TOP',
        'WST': 'WST', 'WST ': 'WST', 'WS$': 'WST',
        'VUV': 'VUV', 'VUV ': 'VUV', 'VT': 'VUV',
        'SBD': 'SBD', 'SBD ': 'SBD', 'SI$': 'SBD',
        'PGK': 'PGK', 'PGK ': 'PGK', 'K': 'PGK',
        
        # Other
        '¢': 'USD',  # Cents
    }
    
    # Extract number
    amount_match = re.search(r'[\d,]+\.?\d*', amount_str)
    if not amount_match:
        return None, 0
    
    try:
        amount = float(amount_match.group().replace(',', ''))
    except ValueError:
        return None, 0
    
    # Find currency (check longer symbols first)
    sorted_symbols = sorted(currency_map.keys(), key=len, reverse=True)
    for symbol in sorted_symbols:
        if symbol in amount_str:
            return currency_map[symbol], amount
    
    # Default to USD if no symbol found
    return 'USD', amount

def convert_to_usd(amount, from_currency):
    if not from_currency or from_currency == 'USD':
        return amount
    
    try:
        url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/{from_currency.lower()}.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if 'usd' in data[from_currency.lower()]:
            rate = data[from_currency.lower()]['usd']
            return amount * rate
        else:
            return 0
    except Exception:
        return 0

def count_thanks_in_page(driver):
    """Count thanks payments currently visible on the page"""
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    price_elements = soup.find_all('span', {'id': 'comment-chip-price'})
    return len([el for el in price_elements if el.get_text(strip=True)])

def get_youtube_thanks_total(video_url):
    # Setup Selenium
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get(video_url)
        
        # Skip ads
        try:
            skip_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".ytp-skip-ad-button, .ytp-ad-skip-button"))
            )
            skip_button.click()
        except:
            pass
        
        # Scroll to comments section
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(3)
        
        # Smart scrolling - stop when no new thanks found
        last_thanks_count = 0
        no_new_thanks_scrolls = 0
        
        print("Loading comments and thanks payments...")
        
        while no_new_thanks_scrolls < 10:
            # Scroll down
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
            
            # Count current thanks payments
            current_thanks_count = count_thanks_in_page(driver)
            
            if current_thanks_count > last_thanks_count:
                print(f"Found {current_thanks_count} thanks payments so far...")
                last_thanks_count = current_thanks_count
                no_new_thanks_scrolls = 0  # Reset counter
            else:
                no_new_thanks_scrolls += 1
                print(f"No new thanks found (scroll {no_new_thanks_scrolls}/10)")
        
        print(f"Stopped scrolling - no new thanks found in last 10 scrolls")
        
        # Calculate total
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        price_elements = soup.find_all('span', {'id': 'comment-chip-price'})
        
        total_usd = 0
        valid_payments = 0
        
        for element in price_elements:
            amount_str = element.get_text(strip=True)
            if amount_str:
                currency, amount = parse_currency(amount_str)
                if currency and amount > 0:
                    usd_amount = convert_to_usd(amount, currency)
                    total_usd += usd_amount
                    valid_payments += 1
        
        print(f"\nFinal result:")
        print(f"Found {valid_payments} valid thanks payments")
        print(f"Total amount: ${total_usd:.2f} USD")
        return total_usd
        
    finally:
        driver.quit()

# Usage
video_url = "https://www.youtube.com/watch?v=z5m6HXKx0Wo"
total = get_youtube_thanks_total(video_url)