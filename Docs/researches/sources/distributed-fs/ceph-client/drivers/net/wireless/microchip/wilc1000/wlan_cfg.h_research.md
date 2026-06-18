<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h

## Purpose
This header declares the WILC configuration cache data structures and the public WID serialization/parsing functions implemented by `wlan_cfg.c`.

## Important APIs, Types, And Functions
It defines `struct wilc_cfg_byte`, `struct wilc_cfg_hword`, `struct wilc_cfg_word`, `struct wilc_cfg_str`, `struct wilc_cfg_str_vals`, and `struct wilc_cfg`. The public API consists of `wilc_wlan_cfg_set_wid()`, `wilc_wlan_cfg_get_wid()`, `wilc_wlan_cfg_get_val()`, `wilc_wlan_cfg_indicate_rx()`, `wilc_wlan_cfg_init()`, and `wilc_wlan_cfg_deinit()`.

## Control Flow
The header has no execution path. It specifies the shape used by initialization to allocate caches, by config packet construction to serialize WIDs, and by RX config demux to update cached values and notify waiters.

## State And Persistence
`struct wilc_cfg` is embedded in `struct wilc` and holds dynamically allocated arrays plus `struct wilc_cfg_str_vals`, which persists firmware version, MAC address, and association response buffers while the WILC object is alive.

## Dependencies And Integration Points
This header depends on `WILC_MAX_ASSOC_RESP_FRAME_SIZE` from `wlan_if.h` via including contexts and forward-declares `struct wilc`. It is included by `wlan.c` and `wlan_cfg.c`.

## Risks
The declarations encode buffer sizes and cache ownership expectations; changing them requires matching allocation/free and parser updates. Consumers must call init before config traffic and deinit during common cleanup to avoid NULL dereferences or leaks.

## Test Signals
Build coverage catches API drift. Runtime validation comes from WID get/set success, association response retrieval, firmware version retrieval, and clean WILC teardown under leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.h -->
