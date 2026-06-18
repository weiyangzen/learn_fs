# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723be/dm.c

## Purpose
Implements RTL8723BE dynamic-management logic run after hardware initialization and periodically from the driver watchdog. It adapts receive gain, CCK packet-detection thresholds, EDCA parameters, firmware RSSI reporting, rate masks, CFO/crystal tracking, thermal TX power tracking, and calibration triggers based on link state, RSSI, false alarms, traffic direction, power-save state, and Bluetooth coexistence.

## Important APIs, Types, And Functions
Public entry points are `rtl8723be_dm_init()`, `rtl8723be_dm_watchdog()`, `rtl8723be_dm_write_dig()`, `rtl8723be_dm_check_txpower_tracking()`, `rtl8723be_dm_init_rate_adaptive_mask()`, and `rtl8723be_dm_txpower_track_adjust()`. Important internals include `rtl8723be_dm_dig()` for initial-gain control, `rtl8723be_dm_false_alarm_counter_statistics()` for OFDM/CCK false-alarm accounting, `rtl8723be_dm_check_rssi_monitor()` for station RSSI aggregation and H2C RSSI reports, `rtl8723be_dm_refresh_rate_adaptive_mask()` for RA mask changes, `rtl8723be_dm_check_edca_turbo()` for BE EDCA tuning, `rtl8723be_dm_dynamic_atc_switch()` for CFO/XTAL and ATC toggling, and `rtl8723be_dm_txpower_tracking_callback_thermalmeter()` for thermal swing-table adjustment and IQK/LCK scheduling.

## Control Flow
Initialization sets driver-controlled DM mode, initializes common DIG/EDCA/BB power saving/dynamic TX power state, seeds OFDM/CCK swing indexes, thermal tracking, and crystal-cap/CFO state. The watchdog verifies RF is on, firmware is not sleeping, P2P PS is not holding the device asleep, and RF changes are not in progress. It then updates one-entry state, samples false alarms, updates RSSI minimums, adjusts DIG, EDCCA, CCK CCA threshold, rate masks, EDCA turbo, ATC/CFO state, thermal tracking, and clears beacon debug counters.

## State And Persistence
The code mutates `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->falsealm_cnt`, `rtlpriv->ra`, `rtlpriv->stats`, and pieces of `rtlhal`. Persistent state includes current/pre IGI, forbidden IGI and recovery counters, RSSI smoothed values, rate-adaptive state, thermal averages and base swing indexes, CFO tails/packet counters, crystal cap, ATC status, EDCA turbo state, and one-entry-only detection. Hardware state persists in BB/RF/MAC registers until overwritten by later DM iterations or reset.

## Dependencies And Integration Points
Depends on rtlwifi common DM helpers, BB/RF accessors, `fw.c` H2C command submission, `phy.c` TX-power/IQK/LC calibration, mac80211 link/opmode state, station RSSI lists protected by `entry_list_lock`, PCI/power locks, and Bluetooth coexistence callbacks. Rate-adaptive updates call the configured hardware op `update_rate_tbl()`.

## Risks
The watchdog writes live radio registers and must stay gated by RF/power-save state. DIG thresholds can reduce sensitivity or cause false alarms if RSSI accounting is wrong. Thermal tracking uses swing-table bounds and signed deltas; bad EFUSE thermal data or index handling can over/under-drive TX power. EDCA turbo rewrites BE parameters based on traffic deltas and can hurt QoS. CFO/ATC crystal changes interact with Bluetooth coexistence and should not churn on noisy packet counts.

## Test Signals
Probe and associate while watching DIG, false-alarm, CCK CCA, and RSSI logs. Test low/high RSSI roaming, scan pause/resume, AP/adhoc station lists, power-save entry/exit, P2P PS, Bluetooth active/inactive, thermal changes, and sustained UL/DL traffic. Useful failures include stuck low throughput after EDCA changes, unstable RSSI near thresholds, repeated IQK/LCK triggers, firmware H2C RSSI errors, or lockdep warnings around RF PS and entry-list locks.
