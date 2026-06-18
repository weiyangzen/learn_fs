# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.c

## Purpose
Implements the RTL8821AE/RTL8812AE RF6052 radio power and RF-parameter setup path. It programs RF bandwidth bits, builds CCK and OFDM/MCS transmit-power register values from EEPROM/efuse tables and dynamic power tracking, clamps values to chip limits, and invokes the generated RF table loaders selected by hardware type and RF path.

## Important APIs, Types, And Functions
The external entry points are `rtl8821ae_phy_rf6052_set_bandwidth`, `rtl8821ae_phy_rf6052_set_cck_txpower`, `rtl8821ae_phy_rf6052_set_ofdm_txpower`, and `rtl8821ae_phy_rf6052_config`. Internal helpers are `rtl8821ae_phy_get_power_base`, `get_txpower_writeval_by_regulatory`, `_rtl8821ae_write_ofdm_power_reg`, and `_rtl8821ae_phy_rf6052_config_parafile`. The code depends on `struct rtl_priv`, `struct rtl_phy`, `struct rtl_mac`, `struct rtl_efuse`, `struct rtl_hal`, RF path IDs, baseband TX AGC registers, `RF_CHNLBW`, and `RF6052_MAX_TX_PWR`.

## Control Flow
Bandwidth setup switches on `HT_CHANNEL_WIDTH_20`, `HT_CHANNEL_WIDTH_20_40`, and `HT_CHANNEL_WIDTH_80` and writes RF channel-bandwidth bits on paths A and B. CCK power setup builds one packed byte-per-rate AGC word per RF path, using max scan power while scanning unless regulatory mode disables that behavior, adding original offsets in unrestricted mode, clamping every byte, applying `rtl8821ae_dm_txpower_track_adjust`, and writing the A/B CCK AGC registers. OFDM power setup first expands OFDM, HT20, and HT40 base power arrays into packed words, then for six OFDM/MCS register groups computes regulatory-adjusted write values and sends them through `_rtl8821ae_write_ofdm_power_reg`. RF config sets `num_total_rfpath` from `rf_type` and walks each active RF path, selecting RTL8812AE or RTL8821AE table configuration callbacks according to `rtlhal->hw_type`.

## State And Persistence
No durable storage is touched. Runtime state is programmed into RF and BB registers and into `rtlphy->num_total_rfpath`. TX power computation reads persistent calibration/regulatory state from efuse/EEPROM-derived fields such as `eeprom_regulatory`, `mcs_txpwrlevel_origoffset`, per-channel power groups, and dynamic TX high-power level.

## Dependencies And Integration Points
This file is called by the PHY channel/bandwidth/power routines, especially channel switching and RF initialization in `phy.c`. It consumes calibration arrays declared in `table.h` indirectly through the PHY table loaders, uses BB/RF register accessors from the rtlwifi HAL, and integrates with dynamic management through `rtl8821ae_dm_txpower_track_adjust`.

## Risks And Edge Cases
Per-byte arithmetic is packed in 32-bit words, so underflow from dynamic high-power backoff or power-tracking subtraction can wrap if the value is already low. Regulatory mode 3 indexes efuse arrays with `channel - 1`, so callers must pass valid 1-based channels. Path B is programmed in bandwidth and power functions even when `RF_1T1R` later limits `num_total_rfpath`. Invalid bandwidth only logs an error and leaves prior RF state in place. Power limit decisions depend heavily on efuse fields being initialized before calls.

## Test Signals
Useful validation is hardware bring-up on RTL8821AE and RTL8812AE, channel switching across 20/40/80 MHz, scan power behavior, regulatory modes 0 through 3, thermal power tracking, and RF path A/B transmit verification. Kernel logs should show no RF config failure messages, and over-the-air tests should confirm expected CCK/OFDM/MCS output power per channel.
