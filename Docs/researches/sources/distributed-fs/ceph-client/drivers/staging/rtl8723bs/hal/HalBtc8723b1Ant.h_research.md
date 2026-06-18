# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b1Ant.h

## Purpose
`HalBtc8723b1Ant.h` defines the state, profile bit masks, enums, thresholds, and external notification API for the RTL8723B one-antenna Bluetooth coexistence module implemented by `HalBtc8723b1Ant.c`. It is the contract between the generic coexistence framework and the chip/profile-specific policy code.

## Important APIs, Types, And Functions
The header defines BT info profile bits for FTP/PAN, A2DP, HID, SCO busy, ACL busy, inquiry/page, SCO/eSCO, and connection presence. It defines `BT_INFO_8723B_1ANT_A2DP_BASIC_RATE()`, `BTC_RSSI_COEX_THRESH_TOL_8723B_1ANT`, and `BT_8723B_1ANT_WIFI_NOISY_THRESH`. Enums classify BT info sources, BT status values, Wi-Fi status values, and coexistence algorithm IDs. `struct coex_dm_8723b_1ant` stores dynamic mechanism state, while `struct coex_sta_8723b_1ant` stores observed station/profile/counter state.

The exported API prototypes are `EXhalbtc8723b1ant_PowerOnSetting()`, `EXhalbtc8723b1ant_InitHwConfig()`, `EXhalbtc8723b1ant_InitCoexDm()`, `EXhalbtc8723b1ant_IpsNotify()`, `EXhalbtc8723b1ant_LpsNotify()`, `EXhalbtc8723b1ant_ScanNotify()`, `EXhalbtc8723b1ant_ConnectNotify()`, `EXhalbtc8723b1ant_MediaStatusNotify()`, `EXhalbtc8723b1ant_SpecialPacketNotify()`, `EXhalbtc8723b1ant_BtInfoNotify()`, `EXhalbtc8723b1ant_HaltNotify()`, `EXhalbtc8723b1ant_PnpNotify()`, and `EXhalbtc8723b1ant_Periodical()`.

## Control Flow
The header has no executable flow, but the API shape reflects the runtime state machine. Power and init calls establish antenna/coex defaults. Notification calls feed Wi-Fi power-save, scan, connection, media, and special-packet transitions into the coexistence mechanism. BT info notification feeds asynchronous C2H BT profile reports. Periodical notification drives counter monitoring and adaptive TDMA decisions.

## State, Dependencies, And Integration
The two structs are designed for persistent module-level state. `coex_dm` carries previous/current fields so the implementation can suppress redundant hardware writes and restore backed-up Wi-Fi register values. `coex_sta` carries observed profile and counter state across notifications and periodic ticks. The header assumes common Realtek BTC definitions for `struct btc_coexist`, `BIT*` macros, boolean and integer typedefs, RSSI state constants, antenna/path constants, notification enum values, and Wi-Fi/BT status sources.

## Risks And Test Signals
Adding or reordering enum values can silently break action dispatch if implementation tables assume numeric values. The singleton-oriented state structs are not naturally multi-adapter safe. Struct fields are tightly coupled to firmware H2C formats and raw register decisions in the C file. Build tests should verify prototypes match the C file. Behavioral tests should confirm BT info bits map to expected profile flags, enum values trigger intended action paths, previous/current state suppression works, and periodical/notification sequences mutate `coex_dm` and `coex_sta` consistently.
