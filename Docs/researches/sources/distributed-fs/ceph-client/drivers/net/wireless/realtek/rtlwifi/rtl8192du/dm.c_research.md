# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/dm.c

## Purpose
Implements RTL8192DU dynamic-management initialization and watchdog behavior. It initializes DIG/rate-adaptive/EDCA/thermal tracking state, periodically reports RSSI to firmware or registers, runs common false-alarm/RSSI/DIG/EDCA/thermal logic, and applies a USB-specific 1R CCA power-saving heuristic on 5G single-PHY devices.

## Important APIs, Types, And Functions
`rtl92du_dm_init()` initializes driver-owned dynamic management. `rtl92du_dm_watchdog()` is the periodic runtime callback. Private helpers are `rtl92du_dm_init_1r_cca()`, `rtl92du_dm_1r_cca()`, and `rtl92du_dm_pwdb_monitor()`. The 1R CCA logic uses `dm_pstable->pre_ccastate`, `cur_ccasate`, RSSI/PWDB thresholds 35 and 30, and BB register `ROFDM0_TRXPATHENABLE`.

## Control Flow
Initialization sets `dm_type`, calls common DIG init with initial gain `0x20`, sets DIG gain bounds, initializes EDCA turbo, initializes 1R CCA state, initializes rate-adaptive mask, and initializes TX power tracking. Watchdog exits early when RF is not on, firmware power-save/race guards indicate unsafe I/O, or RF change is in progress. Otherwise it reports PWDB, updates false-alarm counters, minimum RSSI, DIG, thermal TX power tracking, EDCA turbo, and finally runs 1R CCA.

## State And Persistence
Persistent state lives in `rtlpriv->dm`, `rtlpriv->dm_digtable`, `rtlpriv->dm_pstable`, and common DM fields such as undecorated PWDB/RSSI and `useramask`. The 1R CCA state is intended to be hysteretic through previous/current CCA fields, though this implementation changes `cur_ccasate` and does not visibly update `pre_ccastate` in the local function.

## Dependencies And Integration Points
Depends on common rtl8192d DM and firmware helpers, BB register access, rtlwifi core state, and mac80211 opmode. It is called from DU hardware init and the DU operation table in the driver.

## Risks
The watchdog must not race RF-off or power-save transitions; the early guards are important. The local `fw_current_inpsmode` and `fwps_awake` variables are fixed constants, so firmware power-save suppression is effectively disabled here. The 1R CCA state may repeatedly write or never advance if `pre_ccastate` is not updated by common code elsewhere. RSSI report behavior differs depending on `useramask`.

## Test Signals
Association in station mode should produce H2C RSSI reports or register writes. Watch false-alarm counters, DIG behavior, EDCA turbo changes, thermal TX power tracking, and 1R/2R CCA transitions on 5G single-PHY hardware under strong and weak signal levels. RF-off and suspend paths should show no unsafe DM I/O.
