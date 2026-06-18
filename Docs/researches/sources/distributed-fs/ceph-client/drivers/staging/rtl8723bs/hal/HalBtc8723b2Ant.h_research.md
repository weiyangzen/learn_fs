# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.h

## Purpose

`HalBtc8723b2Ant.h` declares the RTL8723B two-antenna coexistence status bits, algorithms, state structures, and notification entry points consumed by `HalBtc8723b2Ant.c` and dispatched through `hal_btcoex.c`. The file was read as a complete 146-line header.

## Important APIs, Types, and Functions

Important definitions include BT info bit masks such as `BT_INFO_8723B_2ANT_B_FTP`, `BT_INFO_8723B_2ANT_B_A2DP`, `BT_INFO_8723B_2ANT_B_HID`, `BT_INFO_8723B_2ANT_B_SCO_BUSY`, `BT_INFO_8723B_2ANT_B_ACL_BUSY`, `BT_INFO_8723B_2ANT_B_INQ_PAGE`, `BT_INFO_8723B_2ANT_B_SCO_ESCO`, and `BT_INFO_8723B_2ANT_B_CONNECTION`. It defines BT info sources, coarse BT statuses, coexistence algorithms, `struct coex_dm_8723b_2ant`, `struct coex_sta_8723b_2ant`, and all `EXhalbtc8723b2ant_*` prototypes.

## Control Flow

The header has no executable control flow. It defines the constants and state layout used by the implementation's event-driven control flow: power-on/init, IPS/LPS, media status, BT info, halt, PnP, and periodic notifications.

## State and Persistence Behavior

The state structs define in-memory persistence for previous/current coexistence decisions, PS-TDMA parameters, firmware/software mechanism states, last algorithm, BT status, Wi-Fi channel info, backup registers, profile flags, RSSI hysteresis, C2H history, retry count, and extended BT info. Actual instances are static in `HalBtc8723b2Ant.c`.

## Dependencies and Integration Points

The header assumes kernel/driver types and bit macros are already available via the precompiled include chain. It depends on `struct btc_coexist` from `HalBtcOutSrc.h`; inclusion ordering is provided by `Mp_Precomp.h`.

## Risks and Edge Cases

There is no include guard in this header, so repeated direct inclusion would rely on the current include pattern not to create conflicts. State array dimensions, especially `btInfoC2h[][10]`, must match parser behavior in the C file. Algorithm enum values are part of switch dispatch and debug interpretation, so reordering is risky.

## Test Signals

Compile coverage through `Mp_Precomp.h`, enum/switch exhaustiveness review against `HalBtc8723b2Ant.c`, static checks for include reuse, and tests that feed all BT info bit combinations through the parser are the main signals.
