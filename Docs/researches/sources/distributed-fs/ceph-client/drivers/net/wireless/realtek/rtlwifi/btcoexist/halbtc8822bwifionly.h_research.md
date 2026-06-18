# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.h

## Purpose
Declares the RTL8822B Wi-Fi-only coexistence/antenna configuration entry points.

## Important APIs, Types, and Functions
The header declares hardware configuration, scan notification, band-switch notification, and antenna switch helpers for `struct wifi_only_cfg`: `ex_hal8822b_wifi_only_hw_config()`, `ex_hal8822b_wifi_only_scannotify()`, `ex_hal8822b_wifi_only_switchbandnotify()`, and `hal8822b_wifi_only_switch_antenna()`.

## Control Flow
This header has no executable flow. It lets a Wi-Fi-only dispatcher initialize RTL8822B hardware and call the same antenna-switch helper for scan and band-change events.

## State and Persistence Behavior
No state is declared here. Persistent effects are BB register writes performed by the C implementation.

## Dependencies and Integration Points
Depends on `struct wifi_only_cfg` and `u8` being visible before inclusion, normally through `halbt_precomp.h`/`halbtcoutsrc.h`. It integrates with the generic Wi-Fi-only context allocated by `rtl_btc_init_variables_wifi_only()`.

## Risks and Test Signals
The header does not indicate valid `is_5g` values beyond `u8`; misuse can silently choose the 2.4 GHz path for zero and 5 GHz for nonzero. Tests should compile-check inclusion ordering and exercise both notification declarations through the generic Wi-Fi-only path.
