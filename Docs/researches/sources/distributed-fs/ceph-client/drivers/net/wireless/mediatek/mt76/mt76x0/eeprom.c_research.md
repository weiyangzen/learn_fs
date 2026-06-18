# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/eeprom.c

Purpose: this file loads, validates, and interprets MT76x0 EEPROM/efuse calibration data. It initializes MAC address, hardware capabilities, frequency/temp offsets, RX gain, per-rate TX power, and channel target power used by the PHY code.

Important functions: `mt76x0_eeprom_init` is the entry point called during common hardware init. `mt76x0_load_eeprom` tries `mt76_eeprom_init`, validates chip IDs with `mt76x0_check_eeprom`, falls back to efuse after `mt76x0_efuse_physical_size_check`, and reads `MT76X0_EEPROM_SIZE` bytes. `mt76x0_set_chip_cap`, `mt76x0_set_freq_offset`, and `mt76x0_set_temp_offset` populate device calibration/capability fields. Exported helpers `mt76x0_read_rx_gain`, `mt76x0_get_tx_power_per_rate`, and `mt76x0_get_power_info` feed channel switching and txpower programming.

Control flow: initialization loads EEPROM data, warns on unsupported version, copies the factory MAC, applies override data, programs the MAC address, then derives chip caps and offsets. TX power computation decodes CCK/OFDM/HT/VHT per-rate fields from EEPROM, applies BW deltas unless TSSI is enabled, then channel-specific power is selected from a channel map or target-power field.

State and persistence behavior: EEPROM contents are persistent hardware calibration data copied into `dev->mt76.eeprom.data`. Derived runtime state includes `dev->mphy.macaddr`, band capability flags, `dev->cal.rx.freq_offset`, `dev->cal.rx.temp_offset`, `dev->cal.rx.lna_gain`, RSSI offsets, and rate power tables. The code does not write EEPROM.

Dependencies and integration: it uses mt76 core EEPROM helpers, mt76x02 EEPROM offsets and parser helpers, Linux MTD/OF includes for platform EEPROM sources, and mac80211 channel data. PHY code calls these helpers on channel changes and txpower recalculation.

Risks: bad or unsupported EEPROM data can misconfigure bands, power, gain, or MAC address. Efuse size checking rejects default/empty efuse with fewer than five used blocks, which protects against bogus defaults but can block unusual hardware. Signed 6-bit and 8-bit decoding is error-prone. TSSI and non-TSSI code paths produce different target-power behavior.

Test signals: probe logs should show EEPROM version/FAE and valid ASIC IDs. Test with EEPROM file override and efuse fallback, MT7610/MT7630/MT7650 IDs, 2 GHz/5 GHz channels, TSSI enabled/disabled, and invalid EEPROM data. Regulatory/SAR-visible max power should align with decoded channel values.
