# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/coex.c

## Purpose
`coex.c` implements the `rtw88` Wi-Fi/Bluetooth coexistence policy engine. It collects Wi-Fi and BT state, interprets firmware BT info C2H messages, maintains scoreboard bits, selects antenna/GNT/table/TDMA/RF parameters, handles delayed state decay, and exposes debugfs reporting.

## Main control flow
The central function is `rtw_coex_run_coex()`. It requires `rtwdev->mutex`, exits if the device is not running, updates Wi-Fi link state and RSSI bands, monitors whether BT is enabled, honors manual/stop/IPS/freeze gates, then selects one action path. The decision tree first handles pure 5 GHz, then 2.4 GHz single-port cases: BT disabled, native LPS, game HID, WHQL test, BT relink, inquiry/page, BT idle, Wi-Fi link/scan, connected profile-specific coexistence, or not-connected Wi-Fi.

Profile-specific action functions map current state to antenna path, RF power/gain, coexistence table, and TDMA case. Examples include `rtw_coex_action_bt_hid()`, `rtw_coex_action_bt_a2dp()`, `rtw_coex_action_bt_pan()`, combinations such as `rtw_coex_action_bt_a2dp_pan_hid()`, Wi-Fi states such as `rtw_coex_action_wl_under5g()` and `rtw_coex_action_wl_linkscan()`, and fallback all-off or Wi-Fi-only actions. `rtw_coex_algorithm()` derives the profile algorithm from HFP/HID/A2DP/PAN presence bits.

## Important APIs and state
Exported entry points include power/init functions, IPS/LPS/scan/connect/media/switchband/status notifiers, BT info/HID/FW debug notifiers, BT info queries, scoreboard writes, indirect LTE coexistence register access, delayed-work callbacks, and debugfs display. State lives in `rtwdev->coex`: `coex->stat` stores BT profile bits, counters, scoreboard, TDMA/table state, RSSI-derived flags, power-save flags, mailbox/cache data, HID info, and Wi-Fi busy/link flags; `coex->dm` stores current decisions such as reason, TDMA parameters, table, antenna position, RSSI states, RF power/gain levels, and channel info; `coex->rfe` stores antenna/RFE properties populated by chip callbacks.

BT info processing in `rtw_coex_bt_info_notify()` handles multiple sources: BT IQK, BT scoreboard, H2C 0x60 echo, WL firmware reply, BT response, and BT active reports. It validates length, deduplicates repeated reports, decodes profile and status bits, updates RSSI, relink/inquiry/multilink timers, HID/BLE/A2DP/PAN/HFP state, then runs coexistence. Debugfs helpers request BT patch/supported versions and vendor registers through `rtw_coex_info_request()`, which sends an H2C mailbox query and waits on `coex->wait` for `rtw_coex_info_response()` to queue a response SKB.

## Dependencies and integration points
The module integrates with mac80211 lifecycle callbacks, firmware H2C/C2H helpers in `fw.c`, chip-specific coexistence ops, `ps.c` LPS helpers, BB/RF register access, debugfs, delayed work initialized in `main.c`, and SKB queues/waitqueues in `rtw_dev`. It also uses chip tables for shared/non-shared antenna TDMA and coexistence table cases.

## Risks and test signals
Risks include policy regressions from table/TDMA case changes, stale delayed-work state after disconnect or power transitions, deadlocks if mailbox queries run without `rtwdev->mutex`, scoreboard bit inversion differences across chips, and incorrect BT info decoding. Test signals include BT audio/HID/PAN traffic while Wi-Fi scans, associates, roams, enters LPS/IPS, switches 2.4/5 GHz, and runs high throughput; debugfs `coex_info`; H2C/C2H traces; lockdep for delayed work; and register snapshots for `REG_BT_COEX_TABLE*`, `REG_WIFI_BT_INFO`, LTE coexistence indirect registers, GNT state, and TDMA parameters.
