# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192d/hw_common.c

Purpose: Implements shared RTL8192D hardware management: generic HW variable get/set, LLT writes, hardware security, EEPROM/efuse parsing, rate-table/rate-mask updates, channel access settings, GPIO radio switch checks, and CAM key programming.

Important APIs/functions: `rtl92d_get_hw_reg()`/`rtl92d_set_hw_reg()` handle common `HW_VAR_*` requests. `rtl92d_llt_write()` writes linked-list table entries. `rtl92d_enable_hw_security_config()` enables hardware crypto. `rtl92d_read_eeprom_info()` reads chip version, autoload state, MAC/PHY mode, MAC addresses, channel plan, and TX power data. `rtl92d_update_hal_rate_tbl()` selects firmware RA mask or hardware ARFR table. `rtl92d_gpio_radio_on_off_checking()` tracks hardware radio switch state. `rtl92d_set_key()` maps mac80211 keys to CAM entries.

Control flow: EEPROM flow reads chip version from `REG_SYS_CFG`, determines EEPROM/efuse boot from `REG_9346CR`, fetches hwinfo, updates cut version from efuse, configures MAC/PHY mode, programs MAC address, parses TX power/thermal/regulatory data, and chooses a channel plan. Rate control computes supported rate bitmaps from mac80211 station capabilities, current band, wireless mode, RF type, MIMO power-save, RSSI level, and bandwidth; with `useramask` it sends `H2C_RA_MASK`, otherwise it writes `REG_ARFR0`. Key programming clears all CAM entries, deletes empty keys, or adds WEP/group/pairwise keys at default, broadcast, AP-free, or fixed pairwise positions.

State and persistence: Fills `rtl_efuse` power tables, thermal and regulatory values, `rtl_hal` version/macphymode/band fields, `rtl_phy` TX-power dependencies, `rtl_pci` RCR through bus-specific wrappers, `rtl_ps_ctl` RF switch state, and `rtlpriv->sec` key buffers. Device state persists only until reset/poweroff.

Dependencies and integration: Depends on rtlwifi CAM, efuse, regulatory, PCI, firmware H2C, DM, and PHY common helpers. Bus-specific rtl8192de code wraps common get/set for PCI-only variables. mac80211 station capabilities and nl80211 interface modes drive rate and key behavior.

Risks: Autoload failure path only logs in `rtl92d_read_eeprom_info()` and does not call adapter-info parsing, so callers must tolerate default/uninitialized values. TX-power parsing is offset-heavy and covers both 2.4/5 GHz groups. Rate-mask logic special-cases `macid` 0/1 and short-GI behavior. Hardware radio switch uses locks and mutable power-state flags; races with IPS/SW RF changes can suppress transitions. CAM key indexing is sensitive for AP mode and default-key modes.

Test signals: EEPROM/efuse dump logs, MAC address programming, TX power table validation per channel, association in STA/AP/ADHOC modes, hardware crypto with WEP/TKIP/AES, RF kill switch toggles, rate-mask H2C traces, and RCR/filter correctness under Cisco/IOT cases.
