# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/rtl_btc.h

## Purpose
Declares the rtlwifi-facing BT coexistence API implemented by `rtl_btc.c`, plus hardware parameter accessors and the link-status query helper.

## Important APIs, Types, and Functions
The header declares lifecycle functions, normal and Wi-Fi-only hardware init, IPS/LPS/scan/connect/media/periodic/halt/BT-info/special-packet/band-switch notifications, coexistence state queries, AMPDU config retrieval, debug display, power-mode recording, and `rtl_btc_get_ops_pointer()`. It also declares efuse/hardware package accessors for BT existence/type/antenna/path/package and `mgnt_link_status_query()`.

## Control Flow
This header has no executable flow. It defines the call surface used by rtlwifi core and chip drivers to reach coexistence behavior, with all implementation routed through `rtl_btc.c` and then `halbtcoutsrc.c`.

## State and Persistence Behavior
No state is declared directly. The functions operate on `struct rtl_priv`, which contains the allocated BT coexistence contexts and cached board information.

## Dependencies and Integration Points
Includes `halbt_precomp.h`, which supplies `struct btc_coexist`, `enum rt_media_status`, `struct rtl_priv`, and related Realtek definitions. The exported ops pointer integrates with the broader rtlwifi driver ops setup.

## Risks and Test Signals
Because this is a broad wrapper API, signature drift between `rtl_btc_ops`, this header, and `rtl_btc.c` would break runtime dispatch. Tests should compile-check every declaration, verify all ops-table members are populated, and exercise both normal coexistence and Wi-Fi-only notification paths.
