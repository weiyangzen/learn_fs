# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hal_bt_coexist.h

## Purpose
`hal_bt_coexist.h` defines RTL8723AE coexistence register addresses, state bitmaps, RSSI states, profile/mechanism IDs, BT info bits, and helper prototypes.

## APIs, Types, And Constants
Key constants include high/low priority BT counter registers, RSSI thresholds/tolerance, Wi-Fi/BT/profile state bits, BT counter levels, AGC/backoff/FW NAV toggles, coexistence mechanism IDs, debug profile IDs, and BT info byte bits for FTP/A2DP/HID/SCO/ACL/inquiry/connection. Function declarations expose all shared helper and all-off operations.

## Control Flow, State, And Persistence
The header has no flow. Its bit definitions are the state language stored in `rtlpriv->btcoexist.cstate` and `cstate_h`; its mechanism IDs classify the selected profile action. Helper prototypes lead to persistent H2C, MAC, BB, and RF changes in implementation files.

## Dependencies And Integration Points
It includes `../wifi.h` and is shared by `btc.h`, `hal_btc.h`, `hal_bt_coexist.c`, `hal_btc.c`, and DM code. It bridges firmware BT info parsing and hardware coexistence programming.

## Risks And Test Signals
Risks are bit collisions, wrong profile classification, threshold tuning regressions, and prototype drift. Signals are clean builds, coherent debug bitmaps, BT profile detection, correct AGC/PTA/TDMA policy selection, and Wi-Fi/BT coexistence behavior.
