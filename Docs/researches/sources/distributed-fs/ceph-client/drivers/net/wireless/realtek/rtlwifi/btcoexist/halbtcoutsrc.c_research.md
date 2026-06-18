# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtcoutsrc.c

## Purpose
Implements the generic Realtek BT coexistence glue layer. It binds a `btc_coexist` context to `rtl_priv`, exposes hardware/register/H2C callbacks to chip-specific coexistence modules, translates rtlwifi/mac80211 state into `BTC_GET_*` results, applies `BTC_SET_*` side effects, and dispatches lifecycle notifications to the correct chip/antenna implementation.

## Important APIs, Types, and Functions
Key helpers are `halbtc_get()` and `halbtc_set()`, the callback table initializers `exhalbtc_initlize_variables()` and `exhalbtc_initlize_variables_wifi_only()`, adapter binding `exhalbtc_bind_bt_coex_withadapter()`, and notification wrappers `exhalbtc_*_notify()`. Register access callbacks include byte/word/dword MMIO, BB/RF access, local register writes, H2C fill, BT mailbox operations, BT register set/get placeholders, and BT MP query helpers for firmware version, AFH map, BLE scan data, supported features, and forbidden slots.

## Control Flow
`rtl_btc.c` allocates a coexistence context, calls `exhalbtc_initlize_variables()`, then binds it to the adapter. Binding derives chip interface, BT chip type, antenna count, antenna position, single-antenna path, package type, RFE type, and defaults. Later wrappers check availability and manual-control state, normalize rtlwifi events into BTC notification enums, temporarily leave low power when needed, dispatch by hardware type and antenna count, and restore low-power behavior.

The `halbtc_get()` switch reads current Wi-Fi connection, scan, link, roam, 4-way, band, AP mode, encryption, B mode, RSSI, bandwidth, traffic direction, firmware version, link status, BT patch/features, IQK counters, channel, AP count, and LPS mode. `halbtc_set()` mutates shared BT/coexistence state and triggers actions such as LPS enter/leave, aggregation update, low-power disable, and RA mask update. BT MP operations send H2C command `0x67` and optionally wait for `bt_mp_comp`, which is completed by `rtl_btc_btmpinfo_notify()`.

## State and Persistence Behavior
State is kept in `struct btc_coexist`: bind flag, adapter pointer, board info, BT info, stack info, link info, manual/initialized flags, statistics counters, last power-mode command, completion object, and callback function pointers. Wi-Fi-only mode uses `struct wifi_only_cfg`. Register and firmware writes persist in hardware. Aggregation changes are rate-limited by a static `pre_time`, and BT query results are cached in `bt_info`.

## Dependencies and Integration Points
Depends on `rtl_priv`, `rtl_mac`, `rtl_phy`, `rtl_hal`, mac80211 opmodes/link states, Realtek register accessors, firmware H2C ops, LPS helpers, AMPDU update, hardware-type macros, and all chip-specific `ex_btc*` functions. It is the central integration point between `rtl_btc.c` and files such as `halbtc8821a2ant.c`.

## Risks and Test Signals
Several hooks are stubs or TODOs: Wi-Fi-only init/notifications, BT register read, PHYDM version/counters, low-power transitions, P2P link status, and debug statistics/link sections. LPS helpers include comments questioning whether blocking is allowed in the current context. `halbtc_get()` returns false for unsupported queries but many callers may not inspect the return value. BT MP response parsing relies on external completion and fixed command sequencing. Tests should verify every wrapper dispatches to the expected chip path, manual control suppresses notifications, low-power transitions do not sleep in invalid contexts, C2H timeout behavior, aggregation rate limiting, and debug output consistency.
