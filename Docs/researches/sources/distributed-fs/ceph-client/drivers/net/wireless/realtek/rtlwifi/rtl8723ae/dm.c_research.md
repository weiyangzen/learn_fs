# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/dm.c

## Purpose
`dm.c` implements RTL8723AE dynamic management: DIG initial gain, false-alarm accounting, CCK packet-detection thresholds, dynamic TX power, EDCA turbo, RF/baseband power saving, rate-adaptive mask refresh, and BT coexistence watchdog entry.

## APIs, Types, And Functions
Public functions include `rtl8723e_dm_init`, `rtl8723e_dm_watchdog`, `rtl8723e_dm_write_dig`, `rtl8723e_dm_check_txpower_tracking`, `rtl8723e_dm_init_rate_adaptive_mask`, `rtl8723e_dm_rf_saving`, and `rtl8723e_dm_bt_coexist`. Internal helpers compute minimum RSSI, read/reset false alarm counters, adjust gain by RSSI/FA, update CCK thresholds, EDCA values, RF save/normal register sets, and rate masks.

## Control Flow, State, And Persistence
`rtl8723e_dm_init` seeds driver-managed DM tables. `rtl8723e_dm_watchdog` runs while RF is on, firmware is awake, and no RF change is active, under `rf_ps_lock`. It updates DIG, counters, power saving, TX power, rate masks, BT coexistence, and EDCA. State lives in `rtlpriv->dm`, `dm_digtable`, `dm_pstable`, `ra`, `falsealm_cnt`, `btcoexist`, and static cached BB registers. Writes persist in BB/MAC/RF registers.

## Dependencies And Integration Points
It depends on rtlwifi core, PCI, PHY, firmware, common RTL8723 DM helpers, BT coexistence, mac80211 link state, stats counters, and hardware register definitions.

## Risks And Test Signals
Risks are unstable gain loops, stale static state across devices, missed lock boundaries, bad EDCA overrides, incorrect near-field TX power, and BT coexistence interference. Signals include stable throughput, roaming/scan behavior, false alarm trends, rate-mask updates, low-power transitions, and concurrent Wi-Fi/BT performance.
