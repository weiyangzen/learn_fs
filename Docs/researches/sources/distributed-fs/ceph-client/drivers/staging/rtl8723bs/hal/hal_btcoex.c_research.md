# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/hal_btcoex.c

## Purpose

`hal_btcoex.c` is the adapter-facing Bluetooth coexistence glue for rtl8723bs. It owns the global coexistence context, binds it to an adapter, implements the callback table expected by chip-specific coexistence code, translates driver notifications into coexistence events, and exposes wrapper APIs used by the wider HAL. The file was read as a complete 1333-line source.

## Important APIs, Types, and Functions

Global state is `struct btc_coexist GLBtCoexist`, plus scan/IQK globals `GLBtcWiFiInScanState` and `GLBtcWiFiInIQKState`. Initialization and binding are handled by `hal_btcoex_Initialize` and `EXhalbtcoutsrc_BindBtCoexWithAdapter`. Callback implementations include `halbtcoutsrc_Get`, `halbtcoutsrc_Set`, raw register accessors, BB/RF accessors, BT register H2C write, and H2C fill. External dispatchers include `EXhalbtcoutsrc_PowerOnSetting`, `EXhalbtcoutsrc_InitHwConfig`, `EXhalbtcoutsrc_InitCoexDm`, IPS/LPS/scan/connect/media/special-packet/BT-info/halt/PnP/periodical notification functions, antenna setters, and public `hal_btcoex_*` wrappers.

## Control Flow

`hal_btcoex_Initialize` clears the global context, sets SDIO interface type, binds the adapter, and installs callback pointers. Public `hal_btcoex_*` wrappers call `EXhalbtcoutsrc_*`, which validate binding/manual-control state, update statistics and global scan state, translate driver enums into BTC enums, and dispatch to either 2-antenna or 1-antenna chip-specific handlers based on `boardInfo.btdmAntNum`. `halbtcoutsrc_Get` answers chip policy queries from mlme, security, firmware version, bandwidth, traffic counters, RSSI, channel, AP count, and power mode. `halbtcoutsrc_Set` updates BT/coex flags or triggers actions such as LPS enter/leave, low-power disable, aggregation control, or RA mask refresh. IO callbacks perform register, BB/RF, local SDIO, and H2C accesses.

## State and Persistence Behavior

The file uses singleton global state for adapter binding, board antenna info, BT flags, statistics counters, power mode command bytes, callback table, scan state, and IQK state. Hardware-visible persistence comes from register writes, BB/RF writes, H2C commands, LPS/low-power control calls, aggregation rejection toggles, and RA mask updates. `hal_btcoex_HaltNotify` unbinds the global context via the chip-specific halt path.

## Dependencies and Integration Points

It includes `<hal_data.h>`, `<hal_btcoex.h>`, and `<Mp_Precomp.h>`. It integrates with mlme state (`check_fwstate`, `WIFI_ASOC_STATE`, `WIFI_AP_STATE`, `WIFI_UNDER_LINKING`), power management (`rtw_btcoex_LPS_Enter`, `rtw_btcoex_LPS_Leave`, `rtw_register_task_alive`, `rtw_unregister_task_alive`), register IO (`rtw_read8/16/32`, `rtw_write8/16/32`), PHY helpers (`PHY_SetBBReg`, `PHY_QueryBBReg`, `PHY_SetRFReg`, `PHY_QueryRFReg`), firmware H2C (`rtw_hal_fill_h2c_cmd`), station/RA mask helpers, and chip-specific `EXhalbtc8723b1ant_*`/`EXhalbtc8723b2ant_*` modules.

## Risks and Edge Cases

Global singleton state prevents safe multi-adapter coexistence. Many callbacks assume `pBtcContext`, adapter, and output pointers are valid. Several get/set cases return false or are stubs, including HS operation/RSSI, MP mode, MIMO PS, BT info control, BT coexist control, antenna control, and `halbtcoutsrc_GetBtReg`. `halbtcoutsrc_SetBtReg` writes only low bytes through two H2C commands with a 200 ms sleep and ignores `RegType`. `hal_btcoex_RecordPwrMode` copies `cmdLen` bytes into a 10-byte array without a local clamp. Scan state is tracked by a global rather than firmware state to avoid stale flags, but this still depends on balanced notifications.

## Test Signals

Callback table initialization tests, wrapper dispatch tests for one-antenna/two-antenna board settings, `BTC_GET`/`BTC_SET` payload tests, register/H2C trace tests, LPS/low-power interaction tests, scan/IQK gating tests for BT info notification, bounds tests for power mode recording, and multi-adapter negative tests are useful signals.
