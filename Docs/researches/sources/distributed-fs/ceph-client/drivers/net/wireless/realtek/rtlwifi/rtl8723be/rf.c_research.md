<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c

## Purpose
Implements RTL8723BE RF6052 radio configuration and transmit-power programming. It adjusts RF channel bandwidth, CCK/OFDM TX power per RF path, regulatory/channel power limits, dynamic TX power tracking, and RF parameter loading from vendor table data.

## Important APIs, Types, And Functions
- Public APIs exported through `rf.h`: `rtl8723be_phy_rf6052_set_bandwidth`, `rtl8723be_phy_rf6052_set_cck_txpower`, `rtl8723be_phy_rf6052_set_ofdm_txpower`, and `rtl8723be_phy_rf6052_config`.
- Internal helpers: `rtl8723be_phy_get_power_base`, `_rtl8723be_get_txpower_writeval_by_regulatory`, `_rtl8723be_write_ofdm_power_reg`, and `_rtl8723be_phy_rf6052_config_parafile`.
- Uses `struct rtl_priv`, `struct rtl_phy`, `struct rtl_mac`, `struct rtl_efuse`, `struct bb_reg_def`, `enum radio_path`, `RF_CHNLBW`, `RF90_PATH_A/B`, `RF6052_MAX_TX_PWR`, `HT_CHANNEL_WIDTH_20`, and `HT_CHANNEL_WIDTH_20_40`.
- Integrates with dynamic management via `rtl8723be_dm_txpower_track_adjust`.

## Control Flow
Bandwidth changes update `rtlphy->rfreg_chnlval[0]` and write RF channel/bandwidth bits on path A. CCK power setup builds four-byte AGC words per RF path, changes behavior during scanning and by EEPROM regulatory mode, clamps each byte to `RF6052_MAX_TX_PWR`, applies thermal/power-tracking adjustment, then writes CCK AGC BB registers. OFDM setup first computes OFDM and MCS base power for path A/B, derives per-rate write values using regulatory mode and channel group, applies dynamic high-power and thermal adjustments, clamps bytes, and writes six rate-group registers per path. RF configuration sets total RF path count, enables RF serial interface state per path, loads RF tables with `rtl8723be_phy_config_rf_with_headerfile`, restores prior RF interface state, and fails if a table load fails.

## State And Persistence
The file mutates `rtlpriv->phy.rfreg_chnlval`, `rtlpriv->phy.num_total_rfpath`, BB TXAGC registers, RF channel/bandwidth registers, and RF serial-interface control registers. It consumes EEPROM/EFUSE regulatory and power-group data, current bandwidth/channel state, scanning state, dynamic high-power level, and thermal tracking output. Hardware register writes persist until channel/power changes, reset, suspend, or full reinitialization.

## Dependencies And Integration Points
Called from PHY channel/bandwidth and hardware initialization paths. Depends on register constants from `reg.h`, chip data from `def.h`, RF/PHY helpers from `phy.h`, dynamic-management code in `dm.h`, and RF table arrays selected by `rtl8723be_phy_config_rf_with_headerfile`. It also depends on shared rtlwifi BB/RF accessors and EFUSE fields initialized earlier in probe.

## Risks And Edge Cases
TX power calculations are packed byte-wise into 32-bit values; overflow, underflow, or missing clamps can program illegal power. Regulatory mode handling differs across EEPROM modes 0 to 3, so channel-group boundaries and customer power limits need careful review. Dynamic high-power subtraction can underflow unsigned packed words. RF path B is handled even though some hardware is 1T1R, so path-count setup must remain correct. Failed RF table loading must prevent partially initialized radio operation.

## Test Signals
Signals include correct association on 20 MHz and 40 MHz channels, sane TX power across channels 1 to 14 and regulatory modes, stable scans without excessive power, thermal power tracking logs, no RF init failure, no out-of-range TXAGC values, and throughput/RSSI behavior after channel switches and suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/rf.c -->
