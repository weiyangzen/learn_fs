# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192c/dm_common.c

`dm_common.c` implements shared dynamic-management logic for RTL8192C-family devices: digital initial gain, false alarm accounting, EDCA turbo, dynamic TX power, thermal TX power tracking, RF saving, rate adaptive mask initialization, and Bluetooth coexistence decisions.

Exported functions include `rtl92c_dm_init()`, `rtl92c_dm_watchdog()`, `rtl92c_dm_write_dig()`, `rtl92c_dm_init_edca_turbo()`, `rtl92c_dm_check_txpower_tracking()`, `rtl92c_dm_init_rate_adaptive_mask()`, `rtl92c_dm_rf_saving()`, `rtl92c_dm_dynamic_txpower()`, `rtl92c_dm_bt_coexist()`, and power-index backup/write/restore helpers. Static helpers collect false alarm counters, adjust initial gain by RSSI and false alarms, handle ad hoc/multi-station DIG, tune CCK packet detection, monitor PWDB, choose EDCA BE parameters from TX/RX byte deltas and BT state, apply thermal OFDM/CCK swing tables, trigger LC/IQ calibration, and classify BT service.

`rtl92c_dm_init()` initializes flags and baseline state. `rtl92c_dm_watchdog()` runs the management loop only when RF is on, firmware is awake/not in PS mode, and RF changes are idle. Persistent state lives in `rtlpriv->dm`, `dm_digtable`, `dm_pstable`, `falsealm_cnt`, `ra`, `stats`, `btcoexist`, `phy`, and cached BB registers.

Risks include static state shared across devices, hard-coded magic registers, thermal table bounds/arithmetic, BT coexistence heuristics, and watchdog gating. Test signals include watchdog traces, false alarm counters, stable RSSI/rates, EDCA changes under traffic, thermal tracking, BT coexistence, RF saving transitions, and multi-adapter tests.
