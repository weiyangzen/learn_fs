# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8188ee/dm.c

## Purpose

`dm.c` implements RTL8188EE dynamic-management logic that runs after hardware initialization and periodically from the driver watchdog. It adjusts receiver gain, CCK packet detection thresholds, EDCA parameters, transmit power tracking, rate-adaptive masks, and antenna diversity based on RSSI, false-alarm counters, thermal readings, link state, Bluetooth coexistence state, and power-save state. It is the main feedback-loop file for keeping the 8188EE PHY/MAC usable across changing RF conditions.

## Important APIs, Types, And Functions

The public entry points exported through `dm.h` are `rtl88e_dm_init()`, `rtl88e_dm_watchdog()`, `rtl88e_dm_write_dig()`, `rtl88e_dm_init_edca_turbo()`, `rtl88e_dm_check_txpower_tracking()`, `rtl88e_dm_init_rate_adaptive_mask()`, `rtl88e_dm_txpower_track_adjust()`, `rtl88e_dm_set_tx_ant_by_tx_info()`, `rtl88e_dm_ant_sel_statistics()`, and `rtl88e_dm_fast_antenna_training_callback()`. Initialization seeds driver-controlled DM mode, DIG state, EDCA state, rate-mask state, TX-power tracking, baseband power-saving state, and antenna-diversity registers.

Key private helpers include `rtl88e_dm_false_alarm_counter_statistics()` for reading and resetting OFDM/CCK false-alarm counters; `rtl88e_dm_dig()` for dynamic initial gain; `rtl88e_dm_cck_packet_detection_thresh()` for CCK CCA threshold selection; `rtl92c_dm_dynamic_txpower()` for near-field TX-power reductions; `dm_txpower_track_cb_therm()` for thermal swing/TXAGC adjustment and LCK/IQK scheduling; `rtl88e_dm_refresh_rate_adaptive_mask()` for RSSI-tiered station rate updates; and `rtl88e_dm_antenna_diversity()` plus its hardware/fast-training helpers for selecting RX idle and TX antennas.

The static `ofdmswing_table`, `cck_tbl_ch1_13`, and `cck_tbl_ch14` are calibration lookup tables used by TX-power tracking. The implementation uses shared `struct rtl_dm`, `struct dig_t`, `struct false_alarm_statistics`, `struct rate_adaptive`, `struct fast_ant_training`, and `struct rtl_ps_ctl` state defined outside this file.

## Control Flow

`rtl88e_dm_init()` is called from `rtl88ee_hw_init()` after MAC/BB/RF setup, IQK/LCK, and firmware download. It reads the current OFDM initial-gain register and initializes all dynamic-management submodules. After that, `rtl88e_dm_watchdog()` is the normal control loop. The watchdog first queries `HW_VAR_FW_PSMODE_STATUS` and `HW_VAR_FWLPS_RF_ON`, forces `fw_ps_awake` false during P2P power-save mode, takes `rf_ps_lock`, and only runs dynamic updates when RF is on, firmware is not in power-save mode, firmware RF is awake, and no RF change is in progress.

Within a watchdog pass, the order is meaningful: `rtl88e_dm_pwdb_monitor()` updates RSSI/PWDB aggregate state, `rtl88e_dm_dig()` adjusts initial gain using the prior false-alarm counters, `rtl88e_dm_false_alarm_counter_statistics()` samples counters for the next pass, dynamic TX power and thermal tracking run, the rate mask is refreshed if RSSI tier changed, EDCA turbo may alter BE parameters, and antenna diversity may update RX/TX antenna selection. Because false-alarm sampling follows DIG, DIG decisions are one watchdog interval behind the latest hardware counters.

Thermal tracking is a two-phase loop through `rtl88e_dm_check_txpower_tracking()`: the first call triggers the RF thermal meter, the next call reads it and invokes `dm_txpower_track_cb_therm()`. That callback averages thermal readings, compares them with EEPROM and previous LCK/IQK baselines, invokes `rtl88e_phy_lc_calibrate()` or `rtl88e_phy_iq_calibrate()` when deltas exceed thresholds, and adjusts TX power through `rtl88e_phy_set_txpower_level()` when swing indices change.

## State And Persistence Behavior

Most state is volatile driver runtime state in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, `rtlpriv->falsealm_cnt`, and `rtlpriv->dm.fat_table`. Persistent calibration baselines originate from EEPROM/EFUSE fields exposed in `rtl_efuse`, especially thermal meter, antenna-diversity type, OEM ID, and TX-power tables loaded by `hw.c`. The file writes hardware registers directly and therefore has side effects in MAC, BB, and RF blocks: IGI register `ROFDM0_XAAGCCORE1`, CCK CCA registers, EDCA BE parameter, RF thermal trigger, TXAGC/swing-dependent RF power programming, antenna mapping/selection registers, and firmware RSSI monitor register `0x4fe`.

Some local static counters in `rtl88e_dm_pwdb_monitor()` and `rtl88e_dm_check_edca_turbo()` persist across calls to compute deltas in unicast bytes and Bluetooth EDCA values. These are file-local process lifetime variables and are not per-device, which is a subtle multi-adapter risk.

## Dependencies And Integration Points

`dm.c` depends on `wifi.h`, `base.h`, `pci.h`, `core.h`, device register definitions, PHY helpers from `phy.c`, firmware command support from `fw.c`, and TX descriptor helpers from `trx.h`. It calls `rtl_get_bbreg()`, `rtl_set_bbreg()`, `rtl_get_rfreg()`, `rtl_set_rfreg()`, raw MMIO helpers, `rtl_find_sta()`, driver ops such as `update_rate_tbl()`, and calibration functions exported by `phy.c`. It integrates with mac80211 station state through `rtl_find_sta()` and `rtl_sta_info`, with AP/adhoc peers through `entry_list`, with Bluetooth coexistence fields through `rtlpriv->btcoexist`, and with firmware LPS state through `get_hw_reg()`.

## Risks And Edge Cases

The watchdog is register-heavy and assumes RF/MAC blocks are accessible after the power-state checks; missed or stale power-save state can cause invalid MMIO/RF accesses. Several heuristics depend on magic thresholds for false alarms, RSSI, and thermal deltas; regressions can appear as throughput collapse, high packet loss, or unstable TX power rather than simple failures. Antenna diversity indexes arrays by `mac_id` and walks `entry_list`; incorrect station counts or IDs can corrupt per-station antenna statistics. The static byte counters in `rtl88e_dm_pwdb_monitor()` and EDCA static state are shared across adapters. `rtl88e_dm_txpower_track_adjust()` has an unsigned subtraction path in the OFDM branch when `ofdm_val > ofdm_base`, which deserves care if reused.

## Test Signals

Useful signals include watchdog execution under linked and unlinked states, false-alarm counter resets, IGI changes, CCK CCA threshold changes, thermal tracking toggling trigger/read phases, LCK/IQK invocation after forced thermal deltas, EDCA BE register changes for RX-heavy/TX-heavy traffic, rate-mask H2C updates after RSSI tier changes, and antenna selection changes with controlled per-antenna RSSI. Hardware or emulation tests should include RF off, firmware LPS, P2P power-save, scanning, AP/adhoc station lists, HP OEM path, Bluetooth coexistence EDCA overrides, and channel 14 CCK swing selection.
