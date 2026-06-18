# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/hal/HalBtcOutSrc.h

## Purpose

`HalBtcOutSrc.h` is the shared Bluetooth coexistence abstraction header for the RTL8723BS HAL. It defines common coexistence constants, Wi-Fi/BT state query and set IDs, callback function pointer types, shared BT/coexistence state structures, and adapter-layer external APIs. The file was read as a complete 426-line header.

## Important APIs, Types, and Functions

Key macros include `NORMAL_EXEC`, `FORCE_EXEC`, RF path IDs, antenna-path IDs, Wi-Fi link-status bits, RSSI state helpers, and power/scan/media notification IDs. It defines `enum btc_chip_interface`, `struct btc_board_info`, `struct btc_bt_info`, `struct btc_stack_info`, `struct btc_bt_link_info`, `struct btc_statistics`, and central `struct btc_coexist`. The callback typedefs (`BFP_BTC_R1`, `BFP_BTC_W1`, `BFP_BTC_SET_BB_REG`, `BFP_BTC_GET_RF_REG`, `BFP_BTC_FILL_H2C`, `BFP_BTC_GET`, `BFP_BTC_SET`, and BT register callbacks) form the hardware/OS abstraction used by chip policy files. Exported APIs are `EXhalbtcoutsrc_*` functions and global `GLBtCoexist`.

## Control Flow

This header defines the dispatch contract but contains no runtime code. Runtime flow is implemented in `hal_btcoex.c`, which fills the function pointers, and in chip-specific modules, which call the callback table and receive translated notifications.

## State and Persistence Behavior

`struct btc_coexist` is the persistent in-memory context: it stores binding state, adapter pointer, board antenna data, BT metadata, profile/link info, interface type, lifecycle flags, statistics counters, last power-mode command bytes, and callback pointers. The header also defines smaller state containers for BT firmware/control state and stack profile state.

## Dependencies and Integration Points

It integrates the coexistence code with the broader rtl8723bs driver through adapter callbacks, firmware H2C sending, BB/RF accessors, raw register IO, LPS/IPS state, scan/media/connect notifications, and antenna configuration. It assumes Realtek driver enums such as `SINGLEMAC_SINGLEPHY`, `DUALMAC_DUALPHY`, `enum rt_media_status`, `BIT*`, `u8`, `u16`, and `u32`.

## Risks and Edge Cases

Many `BTC_GET_*` and `BTC_SET_*` values are untyped IDs whose payload type must match caller expectation. Incorrect callback initialization can turn chip policy actions into null dereferences. Global `GLBtCoexist` creates singleton behavior. The header contains a duplicate `enum {` line before scan notification constants, which is accepted only if the surrounding source as included remains syntactically valid in this tree; it is a fragile area for refactoring.

## Test Signals

Compile with all coexistence users enabled, callback initialization checks in `hal_btcoex_Initialize`, smoke tests for every `BTC_GET_*` and `BTC_SET_*` case, and notification routing tests for 1-antenna versus 2-antenna board settings provide coverage.
