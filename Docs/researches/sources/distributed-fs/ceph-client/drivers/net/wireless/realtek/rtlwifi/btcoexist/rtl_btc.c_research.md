# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.c

## Purpose
Provides the rtlwifi-facing BT coexistence operations table and thin wrappers around the generic coexistence core. It is the adapter-level API used by the rest of rtlwifi to allocate/deallocate coexistence contexts, notify power/link/scan events, consume C2H BT information, and query coexistence decisions such as limited DIG, LPS/RPWM, AMPDU control, and EDCA behavior.

## Important APIs, Types, and Functions
`rtl_btc_operation` initializes `struct rtl_btc_ops` with all public wrappers. Allocation helpers create either `struct btc_coexist` or `struct wifi_only_cfg` with `kzalloc_obj()`, and deinit frees both possible contexts. Public functions include `rtl_btc_init_variables()`, `rtl_btc_init_variables_wifi_only()`, `rtl_btc_init_hw_config()`, all notification wrappers, `rtl_btc_btinfo_notify()`, `rtl_btc_btmpinfo_notify()`, `rtl_btc_is_limited_dig()`, `rtl_btc_is_disable_edca_turbo()`, `rtl_btc_is_bt_disabled()`, `rtl_btc_get_ampdu_cfg()`, `rtl_btc_display_bt_coex_info()`, `rtl_btc_get_ops_pointer()`, `mgnt_link_status_query()`, and `rtl_get_hwpg_bt_exist()`.

## Control Flow
Initialization allocates the context, initializes generic callbacks through `exhalbtc_initlize_variables()`, and binds the adapter. Hardware config reads efuse BT existence, passes `wifi_only` to `exhalbtc_init_hw_config()`, then initializes coexistence DM. Notifications check context presence and forward to `exhalbtc_*`; IPS leave additionally sends a synthetic scan-start/finish pair to refresh coexistence state. Wi-Fi-only scan and band-switch wrappers derive `is_5g` from current or requested band and call Wi-Fi-only generic wrappers. `rtl_btc_btmpinfo_notify()` parses extended C2H responses from BT firmware, updates cached BT firmware/version/AFH/BLE/device information, and completes the BT MP wait.

## State and Persistence Behavior
This file owns the lifetime of `rtlpriv->btcoexist.btc_context` and `wifi_only_context`. It records last power-mode command bytes in `btc_coexist`, cached BT MP response fields, and EDCA register `0x504` when BT HS uplink/downlink policy is applied. Null contexts return safe defaults.

## Dependencies and Integration Points
Depends on `../wifi.h`, `halbt_precomp.h`, `rtl_btc.h`, Linux module/vmalloc headers, `rtl_priv`, `rtl_btc_ops`, firmware C2H definitions, and generic `exhalbtc_*` functions. It exports `rtl_btc_get_ops_pointer()` for driver registration and module metadata for the rtlwifi core.

## Risks and Test Signals
`rtl_btc_get_ampdu_cfg()` writes `*reject_agg` and `*ctrl_agg_size` in the null-context branch without null checks even though the non-null branch checks each pointer. `rtl_btc_is_disable_edca_turbo()` always returns true and writes EDCA magic values when current value differs. `rtl_btc_is_bt_disabled()` comments that `bt_disabled` appears never initialized or set. BT MP parsing assumes adequate packet length for all sequence cases after only checking `length >= 4`; several cases read bytes beyond four. Tests should cover null-context callers, short C2H packets for every sequence, IPS synthetic scan behavior, EDCA write policy, wifi-only context setup, and module ops table completeness.
