# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/dm.c

## Purpose
This file implements RTL8192SE dynamic management. It periodically adjusts EDCA turbo settings, transmit-power tracking, rate-adaptive masks, baseband MRC, false-alarm/DIG initial gain, and dynamic TX power based on link state, traffic direction, RSSI/PWDB, RF type, firmware version, and counters.

## Important APIs, Types, And Functions
Public entry points are `rtl92s_dm_init()`, `rtl92s_dm_watchdog()`, and `rtl92s_dm_init_edca_turbo()`. Internal workers include `_rtl92s_dm_check_edca_turbo()`, `_rtl92s_dm_check_txpowertracking_thermalmeter()`, `_rtl92s_dm_txpowertracking_callback_thermalmeter()`, `_rtl92s_dm_refresh_rateadaptive_mask()`, `_rtl92s_dm_switch_baseband_mrc()`, `_rtl92s_dm_false_alarm_counter_statistics()`, `_rtl92s_dm_initial_gain_sta_beforeconnect()`, `_rtl92s_dm_ctrl_initgain_byrssi()`, and `_rtl92s_dm_dynamic_txpower()`.

Static EDCA tables provide vendor-specific uplink/downlink BE parameters for peers identified by `mac->vendor`. DIG and rate-adaptive state use shared `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->ra`, and `rtlpriv->falsealm_cnt`.

## Control Flow
`rtl92s_dm_init()` sets driver-controlled DM, initializes dynamic TX power, EDCA turbo, RA mask state, thermal tracking, DIG thresholds, and enables firmware CCA checking. `rtl92s_dm_watchdog()` runs the periodic policy sequence: EDCA turbo, thermal tracking, initial gain, dynamic TX power, RA refresh, and MRC switch.

EDCA turbo compares unicast TX/RX byte deltas against previous watchdog counters, chooses uplink or downlink BE parameters, and resets to normal AC parameters when non-BE traffic is seen. Thermal tracking alternates between triggering RF thermal measurement and reading/reporting it to firmware. DIG reads false-alarm counters, decides connected/disconnected state, disables/enables firmware DIG as needed, and writes OFDM initial gains. Dynamic TX power lowers transmit power in near-field conditions by recalculating channel power when thresholds cross.

## State And Persistence
Persistent state includes static previous TX/RX counters in EDCA logic, `dm.current_turbo_edca`, `dm.is_cur_rdlstate`, `dm.txpowercount`, `dm.tm_trigger`, `dm.thermalvalue`, `dm.useramask`, `dm.dynamic_txhighpower_lvl`, `dm.last_dtp_lvl`, DIG thresholds and previous values, and MRC switch state. Register writes to EDCA, BB AGC, CCA, RF thermal meter, and WFM firmware command registers persist until changed by watchdog, scan backup/restore, power transitions, or reinitialization.

## Dependencies And Integration Points
This file depends on rtlwifi statistics, mac80211 link/opmode state, PHY RF helpers, firmware command helpers in `phy.c`, rate table updates in `hw.c`, EFUSE thermal calibration, and BB register definitions. It integrates with scan paths via firmware DM pause/resume commands and with RX processing because RSSI/PWDB and non-BE counters drive decisions.

## Risks
Static counters in EDCA turbo are shared across device instances, which can be risky if multiple 8192SE devices are present. Firmware-version branches choose different command mechanisms; unsupported or failed firmware commands leave DM state stale. DIG directly writes initial gain and toggles firmware control, so scan, link transition, or RF-off races can affect sensitivity. Dynamic TX power is disabled for 2T2R but active for other RF types; bad thresholds can reduce throughput or violate expected power behavior. `useramask` is computed then forcibly disabled in init, making RA mask code mostly dormant unless changed.

## Test Signals
Signals include watchdog running without register-command timeouts, EDCA changes only for BE-dominated traffic, stable throughput in uplink/downlink tests, thermal tracking WFM completion, correct RA refresh on RSSI transitions, MRC toggling for 1T2R RSSI differences, and no DIG oscillation during scan/connect/disconnect. RF-off and scan stress should verify watchdog does not write invalid registers while stopped.
