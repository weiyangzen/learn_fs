# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ee/dm.c

Purpose: Implements RTL8192EE dynamic management: false-alarm sampling, DIG/CCA tuning, RSSI reporting, EDCA turbo, EDCCA/adaptivity, primary CCA handling, CFO/ATC crystal tracking, TX power tracking init, rate-adaptive mask refresh, ARFB fallback selection, and watchdog orchestration.

Important APIs/functions: `rtl92ee_dm_init()` initializes DIG, RA mask, primary CCA, EDCA, TX power tracking, and ATC. `rtl92ee_dm_watchdog()` runs periodic tuning when RF is on and firmware is awake. `rtl92ee_dm_false_alarm_counter_statistics()` reads/resets OFDM/CCK counters. `rtl92ee_dm_dig()`, `rtl92ee_dm_write_dig()`, and `rtl92ee_dm_write_cck_cca_thres()` adjust gain and CCK CCA. `rtl92ee_dm_check_rssi_monitor()` sends RSSI H2C reports and updates minimum RSSI. `rtl92ee_dm_check_edca_turbo()`, `rtl92ee_dm_dynamic_edcca()`, `rtl92ee_dm_dynamic_primary_cca_check()`, `rtl92ee_dm_dynamic_atc_switch()`, and `rtl92ee_dm_refresh_rate_adaptive_mask()` tune runtime PHY/MAC behavior. `rtl92ee_dm_dynamic_arfb_select()` writes ARFB fallback registers from firmware RA reports.

Control flow: Hardware setup calls `rtl92ee_dm_init()`. The watchdog queries firmware power-save state and P2P PS, locks `rf_ps_lock`, and, if safe, updates common link info, samples false alarms, reports RSSI, updates DIG/adaptivity/CCA/rate/EDCA/CFO, and releases the lock.

State and persistence: Mutates `rtlpriv->dm`, `dm_digtable`, `falsealm_cnt`, `primarycca`, `ra`, `stats`, and hardware/FW registers. Some static counters persist across watchdog calls. No disk persistence.

Dependencies/integration: rtlwifi core, mac80211 opmode/link state, PCI/core helpers, RTL8192EE registers, `fw.c` H2C commands, `def.h` rate codes, Bluetooth coexistence ops, and HAL callbacks.

Risks: Threshold-heavy hardware algorithms can regress performance. Static EDCA counters are function-scope, not per-device. H2C RSSI reporting while iterating station list under spinlock may need lock-context scrutiny. Watchdog power gating can suppress tuning. Crystal-cap and EDCA changes can affect coexistence and latency.

Test signals: Observe false alarms, IGI, CCK CCA, EDCA BE, RSSI H2C, rate-table updates, CFO/ATC adjustments, Bluetooth coexistence, P2P PS, and watchdog behavior through suspend/resume/LPS.
