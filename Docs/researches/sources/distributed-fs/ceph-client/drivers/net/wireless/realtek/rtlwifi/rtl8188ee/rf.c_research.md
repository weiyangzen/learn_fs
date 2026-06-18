# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/rf.c

`rf.c` implements RTL8188EE RF6052 radio configuration and transmit-power programming. It translates channel bandwidth, per-path power tables, EEPROM regulatory modes, thermal tracking adjustments, and dynamic high-power limits into RF and baseband register writes.

Key functions are `rtl88e_phy_rf6052_set_bandwidth()`, `rtl88e_phy_rf6052_set_cck_txpower()`, `rtl88e_phy_rf6052_set_ofdm_txpower()`, and `rtl88e_phy_rf6052_config()`. Internal helpers compute OFDM/MCS power bases, apply regulatory modes 0-3, clamp packed per-rate power bytes to `RF6052_MAX_TX_PWR`, write TX AGC registers, and configure RF paths by enabling RF environment bits before loading RF table data.

State comes from `rtlpriv->phy`, `rtlpriv->dm`, `rtlpriv->mac80211`, and `rtl_efuse`: current bandwidth/channel, original MCS offsets, power groups, regulatory mode, scanning state, dynamic high-power level, and thermal tracking direction/value. Integration points are `reg.h`, PHY RF/BB accessor functions, `rtl88e_phy_config_rf_with_headerfile()`, and DM thermal tracking.

Risks include off-by-one channel indexing, regulatory-power mistakes, underflow after dynamic power subtraction, and path-B writes on reduced RF configurations. Test signals include RF init success, channel/bandwidth switching, per-rate TX power on channels 1-14, scan behavior, thermal tracking, and compliance-oriented power checks.
