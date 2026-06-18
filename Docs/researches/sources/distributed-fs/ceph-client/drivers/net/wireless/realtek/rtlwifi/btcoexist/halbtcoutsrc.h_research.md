# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.h

## Purpose
Defines the generic BT coexistence interface shared by rtlwifi front-end code and chip-specific coexistence algorithms. It provides enums, constants, state structures, callback signatures, macros for retrieving contexts, and Wi-Fi-only support types.

## Important APIs, Types, and Functions
The header defines antenna paths, RF paths, coexistence modes, RSSI states and helper macros, Wi-Fi roles/frequencies/bandwidth/traffic direction, notification enums, BT operation opcodes and request numbers, `BTC_GET_*` and `BTC_SET_*` request IDs, debug display IDs, and rate constants. `struct btc_board_info`, `btc_bt_info`, `btc_stack_info`, `btc_statistics`, `btc_bt_link_info`, and especially `struct btc_coexist` form the shared runtime contract. `struct btc_coexist` contains board facts, BT/Wi-Fi state caches, counters, power-mode bytes, a completion for BT MP commands, and callback pointers for MMIO, BB/RF, H2C, debug, get/set, BT register access, and BT information queries. Wi-Fi-only mode is represented by `struct wifi_only_cfg` and `struct wifi_only_haldata`.

## Control Flow
This file is declarative, but it establishes the callback pattern: generic wrappers call chip modules through `exhalbtc_*`; chip modules call back into the generic layer through `btc_get`, `btc_set`, register accessors, and H2C helpers. Wi-Fi-only helpers use `halwifionly_phy_set_bb_reg()` to map a `wifi_only_cfg` adapter back to `rtl_set_bbreg()`.

## State and Persistence Behavior
The header defines all state containers but does not allocate them. `btc_coexist` state is per allocated context, while some chip modules add their own static state. State persists for the lifetime of the rtlwifi adapter context and is freed by `rtl_btc_deinit_variables()`.

## Dependencies and Integration Points
Includes `../wifi.h` and depends on Realtek hardware enums, `rtl_priv`, `seq_file`, `completion`, `enum dm_info_query`, and kernel integer/boolean types. It is included by `rtl_btc.h`, `halbtcoutsrc.c`, and chip-specific coexistence files.

## Risks and Test Signals
The interface is broad and weakly typed: `btc_get`/`btc_set` use `u8` request IDs and `void *` buffers, so type mismatches are compile-time invisible. Many constants mirror firmware encodings and register policy magic values. Tests should include compile coverage for all callback signatures, get/set type correctness, initialization of every function pointer before chip code runs, Wi-Fi-only context setup, and bounds for BT temporary buffers and C2H data.
