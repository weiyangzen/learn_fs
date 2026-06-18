# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/dm.c

Purpose: Implements rtl8192de-specific dynamic-management initialization and watchdog flow around shared RTL8192D DM helpers.

Important APIs/functions: `rtl92de_dm_init()` initializes driver-owned DM mode, DIG bounds, dynamic TX power, EDCA turbo, rate adaptive mask, and power tracking. `rtl92de_dm_watchdog()` gates periodic DM work on RF/power-save state. Internal helpers handle dynamic TX high-power level selection and PWDB RSSI reporting to firmware.

Control flow: Init sets `dm_type = DM_TYPE_BYDRIVER`, calls common DIG init, sets DIG gain min/max, then initializes dynamic TX power, EDCA, RA mask, and thermal tracking. Watchdog exits unless RF is on, firmware power-save is treated awake, and RF change is not in progress. When allowed, it reports PWDB to firmware/register, collects false alarms, finds minimum RSSI, runs DIG, adjusts dynamic TX power, and checks EDCA turbo.

State and persistence: Mutates `rtlpriv->dm.dynamic_txpower_enable`, `last_dtp_lvl`, `dynamic_txhighpower_lvl`, `dm_type`, `useramask`, `undec_sm_pwdb`, `entry_min_undec_sm_pwdb`, and `dm_digtable` thresholds. Dynamic TX power may call `rtl92d_phy_set_txpower_level()` to write runtime TX power registers.

Dependencies and integration: Depends on rtl8192d common DM/PHY/FW helpers, rtlwifi core/base, mac80211 link/opmode state, current band/channel, and firmware H2C command support. The sw/ops layer calls these during init and watchdog.

Risks: `fw_current_inpsmode` and `fwps_awake` are hard-coded local values in this file, so actual firmware power-save status is not consulted here. Dynamic TX power thresholds differ for 2.4/5 GHz and use smoothed PWDB; incorrect PWDB can over-reduce transmit power. Thermal tracking call is commented out in watchdog.

Test signals: Watchdog traces during link/unlink, TX power level transitions near thresholds, firmware RSSI report command, DIG false-alarm response, and EDCA changes under uplink/downlink traffic.
