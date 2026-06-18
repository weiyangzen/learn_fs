# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.h

## Purpose
`main.h` is the central mwifiex common header. It includes Linux and bus headers, declares global module state, defines core constants/macros, debug levels, hardware/power/interface enums, connection/security/rate/WMM/BA/reorder/station/TDLS data structures, bus operation callbacks, the main `mwifiex_private` and `mwifiex_adapter` state containers, and cross-file function prototypes.

## Important APIs, Types, and Functions
Core state types are `struct mwifiex_private`, `struct mwifiex_adapter`, `struct mwifiex_if_ops`, `struct mwifiex_bssdescriptor`, `struct mwifiex_current_bss_params`, `struct mwifiex_wmm_desc`, `struct mwifiex_ra_list_tbl`, `struct mwifiex_rx_reorder_tbl`, `struct mwifiex_sta_node`, `struct cmd_ctrl_node`, and `struct mwifiex_dbg`. Key enums/macros cover driver mode, interface type, hardware status, power-save state, debug masks, packet types, queue thresholds, scan timing, firmware dump sizes, and work flags. The prototype block exports nearly every cross-module driver operation for commands, scans, association, UAP, WMM, 11n/11ac, power, events, RX/TX, debug, TDLS, WoWLAN, DFS/CAC, and adapter lifecycle.

## Control Flow
This header establishes how modules call each other. Bus-specific drivers provide `mwifiex_if_ops`; `main.c` stores those callbacks in `mwifiex_adapter` and orchestrates lifecycle. Command code consumes `cmd_ctrl_node` queues and `mwifiex_send_cmd()` prototypes. Join, scan, UAP, WMM, 11n/11ac, power, and event handlers mutate fields in `mwifiex_private` and `mwifiex_adapter`. Inline helpers choose private contexts by BSS id/role, copy rate arrays, and decide whether queuing should be receiver-address based.

## State and Persistence
`mwifiex_adapter` is the device-wide volatile state: firmware name/blob, bus card pointer, interface ops, workqueues, command queues, interrupt/event flags, TX/RX queues and counters, scan/region settings, firmware capabilities, power-save and host-sleep state, cfg80211 wiphy, wake IRQ, coredump buffers, channel stats, bus aggregation, and coex/TDLS flags. `mwifiex_private` is per virtual interface: BSS identity, netdev/wdev, MAC, connection/security/rate state, WMM queues, station lists, BA/reorder tables, scan state, custom IE cache, AP settings, TDLS, DFS, memory access, bypass queue, and association response cache. No filesystem persistence exists.

## Dependencies and Integration Points
`main.h` ties together Linux netdev/cfg80211/skbuff/workqueue/timer/firmware/devcoredump APIs and mwifiex local headers `decl.h`, `ioctl.h`, `util.h`, `fw.h`, `pcie.h`, `usb.h`, and `sdio.h`. It is included by most mwifiex `.c` files, so changes here have driver-wide build and ABI effects.

## Risks and Edge Cases
Because this header defines shared state, field changes can silently break lock ordering, ownership, or bus implementations. Many fields are protected by specific spinlocks but the protection is documented only by comments and usage. `mwifiex_private` and `mwifiex_adapter` are large mutable structures used from workqueues, IRQ context, netdev callbacks, cfg80211 callbacks, and reset paths. Constants such as queue thresholds, buffer sizes, and IE limits must match firmware and caller assumptions.

## Test Signals
Build all mwifiex bus variants after header changes. Runtime signals include clean STA/AP/P2P virtual interface creation, command queue progress, RX/TX queue accounting, WMM/BA/reorder behavior, TDLS peer tracking, host sleep and wake, DFS/CAC work, firmware dump paths, debugfs/debug-info output, and lockdep/KASAN coverage during add/remove/reset/suspend.
