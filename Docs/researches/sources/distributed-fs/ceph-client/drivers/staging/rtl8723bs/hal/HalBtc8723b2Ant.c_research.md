# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtc8723b2Ant.c

## Purpose

`HalBtc8723b2Ant.c` implements the RTL8723B two-antenna Bluetooth/Wi-Fi coexistence policy engine. It consumes BT C2H status reports, Wi-Fi state queried through `struct btc_coexist`, and board antenna metadata, then programs firmware H2C commands, PTA coexistence tables, antenna path registers, RF gain/filter tweaks, DAC swing, AGC table shifts, and Rx aggregation controls. The file was read as a complete 2630-line source.

## Important APIs, Types, and Functions

External entry points are `EXhalbtc8723b2ant_PowerOnSetting`, `EXhalbtc8723b2ant_InitHwConfig`, `EXhalbtc8723b2ant_InitCoexDm`, `EXhalbtc8723b2ant_IpsNotify`, `EXhalbtc8723b2ant_LpsNotify`, `EXhalbtc8723b2ant_ScanNotify`, `EXhalbtc8723b2ant_ConnectNotify`, `EXhalbtc8723b2ant_MediaStatusNotify`, `EXhalbtc8723b2ant_SpecialPacketNotify`, `EXhalbtc8723b2ant_BtInfoNotify`, `EXhalbtc8723b2ant_HaltNotify`, `EXhalbtc8723b2ant_PnpNotify`, and `EXhalbtc8723b2ant_Periodical`. Core internal helpers include RSSI hysteresis (`halbtc8723b2ant_BtRssiState`, `halbtc8723b2ant_WifiRssiState`), BT profile classification (`halbtc8723b2ant_UpdateBtLinkInfo`, `halbtc8723b2ant_ActionAlgorithm`), policy application (`halbtc8723b2ant_RunCoexistMechanism`), firmware controls (`halbtc8723b2ant_SetFwPstdma`, `halbtc8723b2ant_SetFwDacSwingLevel`, `halbtc8723b2ant_SetFwDecBtPwr`, `halbtc8723b2ant_SetFwIgnoreWlanAct`), and hardware controls (`halbtc8723b2ant_SetAntPath`, `halbtc8723b2ant_CoexTableWithType`, `halbtc8723b2ant_AgcTable`, `halbtc8723b2ant_RfShrink`, `halbtc8723b2ant_DacSwing`). Static singletons `GLCoexDm8723b2Ant` and `GLCoexSta8723b2Ant` hold current/preconfigured coexistence state.

## Control Flow

Initialization backs up RF register `0x1e`, configures antenna path and PTA registers, enables counters, and resets PS-TDMA and software mechanisms. Runtime begins when `EXhalbtc8723b2ant_BtInfoNotify` parses C2H bytes: source, retry count, RSSI, extended flags, inquiry/page bit, profile bits, TX/RX mask, and BT reset hints. It updates `pBtCoexist->btLinkInfo`, sets broad BT status, mirrors busy/DIG flags through `BTC_SET`, then calls `halbtc8723b2ant_RunCoexistMechanism`. The policy runner checks manual control and IPS, handles BT inquiry/page specially, performs common idle/disconnected handling when possible, otherwise dispatches by algorithm to SCO/HID/A2DP/PAN combinations. Each action chooses PTA table type, PS-TDMA pattern, BT power decrement, firmware DAC swing, RF path mask, Rx aggregation policy, and software mechanisms based on Wi-Fi bandwidth, Wi-Fi RSSI, BT RSSI, AP count, and BT retry history.

## State and Persistence Behavior

State is in static process-global structures, not file-backed persistence. `coex_dm_8723b_2ant` stores previous and current settings so duplicate register/H2C writes can be skipped, plus backup values for RF `0x1e` and register `0x948`. `coex_sta_8723b_2ant` stores BT link flags, LPS/IPS state, RSSI hysteresis state, C2H history, retry count, and inquiry/page state. Hardware-visible state persists in MAC/BB/RF registers and firmware coexistence settings until rewritten, reset, IPS/halt paths, or adapter teardown.

## Dependencies and Integration Points

The file includes `Mp_Precomp.h` and relies on `HalBtcOutSrc.h` callback pointers for register IO, BB/RF access, H2C sending, and Wi-Fi state queries. It integrates with the adapter-facing `hal_btcoex.c` layer, firmware H2C commands `0x60` through `0x66` and `0x69`/`0x6e`, Realtek PTA registers such as `0x6c0`, `0x6c4`, `0x6c8`, `0x6cc`, antenna path registers `0x948`, `0x92c`, `0x4c`, and RF registers including `0x1`, `0x1e`, `0x3b`, `0x40`, `0xed`, and `0xef`.

## Risks and Edge Cases

The policy is highly stateful and global, so multiple adapters or unexpected concurrent notifications can corrupt assumptions. H2C and register constants are magic values with no local validation. BT register access depends on a partial H2C implementation in `hal_btcoex.c`, and `fBtcGetBtReg` is a stub. `EXhalbtc8723b2ant_BtInfoNotify` writes `length` bytes into fixed `[10]` C2H storage without a local length clamp. Several notify hooks for scan/connect/special packet are empty, so temporary traffic states may only affect policy through adapter-layer globals. Incorrect antenna path or firmware version detection can route Wi-Fi/BT to the wrong switch path.

## Test Signals

Useful signals are compile coverage for the staging driver, BT info C2H parsing tests with all profile bit combinations, regression tests for algorithm selection, H2C payload capture for PS-TDMA/DAC/channel-info commands, register trace checks for init/IPS/halt paths, concurrency or repeated-notification tests for previous/current state suppression, and real hardware coexistence validation for SCO, HID, A2DP, PAN(EDR), PAN(HS), inquiry/page, scan, LPS, and IPS scenarios.
