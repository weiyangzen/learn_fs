# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.c

## Purpose
`phy.c` implements shared PHY and RF logic for `rtw88`: rate-section tables, dynamic mechanisms run by the watchdog, DIG/false-alarm/RSSI handling, CCK packet detection tuning, rate adaptation support, CFO parsing/tracking hooks, RF register access, conditional PHY table parsing, BB/RF/MAC/AGC table loaders, TX power by-rate and regulatory limit parsing, TX power index computation, thermal power tracking helpers, and TX path diversity.

## Important APIs, Types, and Functions
- Exported rate tables: `rtw_cck_rates`, `rtw_ofdm_rates`, HT/VHT 1SS-4SS arrays, `rtw_rate_section[]`, and `rtw_rate_size[]`.
- Initialization and dynamic mechanism: `rtw_phy_init()`, `rtw_phy_dynamic_mechanism()`, `rtw_phy_dig_write()`, `rtw_phy_dig_set_max_coverage()`, and `rtw_phy_dig_reset()`.
- RSSI/rate helpers: `rtw_phy_rf_power_2_rssi()`, RA info update, RRSR mask update, and CFO parsing via `rtw_phy_parsing_cfo()`.
- RF I/O: `rtw_phy_read_rf()`, `rtw_phy_read_rf_sipi()`, `rtw_phy_write_rf_reg_sipi()`, `rtw_phy_write_rf_reg()`, and `rtw_phy_write_rf_reg_mix()`.
- Table condition/config parsing: `rtw_phy_setup_phy_cond()`, `rtw_parse_tbl_phy_cond()`, `rtw_parse_tbl_bb_pg()`, `rtw_parse_tbl_txpwr_lmt()`, `rtw_phy_cfg_mac()`, `rtw_phy_cfg_agc()`, `rtw_phy_cfg_bb()`, `rtw_phy_cfg_rf()`, and `rtw_phy_load_tables()`.
- TX power APIs: `rtw_phy_init_tx_power()`, `rtw_get_tx_power_params()`, `rtw_phy_get_tx_power_index()`, `rtw_phy_set_tx_power_level()`, `rtw_phy_tx_power_by_rate_config()`, and `rtw_phy_tx_power_limit_config()`.
- Power tracking/path diversity: `rtw_phy_config_swing_table()`, thermal delta helpers, `rtw_phy_pwrtrack_need_lck()`, `rtw_phy_pwrtrack_need_iqk()`, and `rtw_phy_tx_path_diversity()`.

## Control Flow
`rtw_phy_init()` resets dynamic mechanism history, reads the initial IGI value, initializes CCK PD state, clears IQK completion, and invokes chip-specific adaptivity/CFO/path-diversity initialization. The core watchdog calls `rtw_phy_dynamic_mechanism()`, which first refreshes RSSI and false-alarm/rate counters, then runs DIG, CCK PD, RA/RRSR updates, TX path diversity, CFO tracking, DPK tracking, power tracking, and adaptivity either through firmware or chip callbacks.

DIG computes a new initial gain index from false-alarm counts, link state, minimum RSSI, previous IGI history, and damping detection. During scans, `main.c` disables normal DIG and sets max coverage; scan completion restores the previous IGI. CCK PD runs only on 2.4 GHz and chooses a level from CCK false-alarm average, IGI, RSSI, and association state before calling the chip hook. RA tracking periodically resends station RA info and writes `REG_RRSR` based on the minimum reported station rate.

PHY table loading uses conditional table rows. `rtw_phy_setup_phy_cond()` builds the active condition from chip cut/pkg/interface/RFE/efuse fields. `rtw_parse_tbl_phy_cond()` evaluates IF/ELIF/ELSE/ENDIF-style encoded rows and applies matching config rows through the table's `do_cfg()` callback. BB power-group tables are parsed into by-rate offsets; TX power limit tables populate regulatory/channel/bandwidth/rate-section arrays, fill missing domains from alternates or worldwide defaults, and cross-reference missing HT/VHT 5 GHz limits.

TX power computation starts from efuse base indexes by channel group, applies by-rate offsets, regulatory limits, SAR limits, remnant power-tracking offsets, optional DPD disable adjustments, and chip max-power clamping. `rtw_phy_set_tx_power_level()` recomputes all rates per RF path under `hal.tx_power_mutex` and calls the chip hook to write hardware TX AGC.

## State and Persistence Behavior
PHY state is stored primarily in `rtwdev->dm_info`, `rtwdev->hal`, and `rtwdev->efuse`. Dynamic state includes false-alarm counts, RSSI levels, IGI/FA histories, damping state, CCK PD averages, CFO sums, packet counters, thermal EWMAs, TX AGC remnants, DPK/IQK/GAPK backups, and path-diversity RSSI accumulators. Power tables persist in `rtw_hal` arrays after efuse/table parsing and are reused for every channel/power update. RF/BB writes are hardware state, not filesystem persistence.

## Dependencies and Integration Points
`phy.c` depends on local register definitions, firmware feature checks, debug logging, regulatory helpers, SAR queries, chip-operation callbacks, mac80211 station/vif iterators, and per-chip table data declared through `rtw_table`. It is called by core initialization, channel setting, watchdog work, scan start/complete, RX descriptor processing for CFO/RSSI stats, and chip-specific calibration/power-tracking code.

## Risks
- Table parsing is dense and hardware-specific; malformed condition rows or RFE matching errors can apply the wrong RF/BB/MAC values.
- TX power math spans efuse, regulatory domain, SAR, bandwidth, rate section, channel group, path, NSS, DPD, and thermal remnants. Regressions may violate regulatory limits or reduce range.
- DIG and CCK PD feedback loops can oscillate; damping history reduces this risk but changes should be validated under noisy RF conditions.
- RF register access checks only `rf_phy_num`; wrong chip data can still direct writes to invalid addresses.
- Several dynamic mechanisms rely on optional chip callbacks; missing hooks can be benign or fatal depending on the call site.
- Path diversity assumes two-path support and resets accumulated samples each watchdog interval; wrong RX path state can cause ineffective or unstable path switching.

## Test Signals
- PHY table loading on every supported RFE/cut/interface combination, including unsupported RFE rejection.
- TX power index comparison against known-good tables for 2.4 GHz, 5 GHz, 20/40/80 MHz, HT/VHT, SAR, and alternative regulatory domains.
- Noisy-environment tests watching DIG, CCK PD, EDCCA/adaptivity, beacon loss, and throughput.
- Thermal chamber or simulated thermal updates validating LCK/IQK trigger thresholds and swing table selection.
- RX status tests validating RSSI conversion across 1-4 RF paths and CFO accumulation only for matching BSSID frames.
- Path-diversity tests on supported 2SS hardware with asymmetric path RSSI.
