# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/wlcore.h

## Purpose
`wlcore.h` is the main common wlcore device header. It defines the chip operation vtable, partition/register enums, top-level `struct wl1271` runtime state, firmware/version helpers, quirk bits, hardware register constants, and public probe/remove/key/configuration APIs shared by TI WiLink wl12xx and wl18xx drivers.

## Important APIs, Types, And Fields
- `struct wlcore_ops` is the chip-family abstraction. It covers setup, chip/FW identification, boot, command/event transport, TX block calculation and descriptor filling, RX layout, completions, hardware init, scan/sched-scan, key installation, channel switch, pre-send aggregation padding, link priority, interrupts, RX BA filtering, smart config, CAC/DFS, and debugfs/static-data hooks.
- `struct wl1271` is the central device object stored as `ieee80211_hw->priv`. It holds hardware handles, runtime state, mutexes/spinlocks, firmware/NVS blobs, partition tables, roles/links/rate-policy maps, vif list, TX/RX queues, descriptor tracking, aggregate buffers, mailbox/status buffers, scan/ROC/sched-scan state, supported bands, AP power-save maps, quirks, watchdog work, chip ops, firmware names, capabilities, DFS state, RX filters, flush mutex, firmware-version minima, interface combinations, trace flags, and time-sync data.
- `struct wlcore_partition*` and `enum wlcore_registers` describe translated firmware/register windows used by bus helpers.
- Inline helpers `wlcore_set_ht_cap()` and `wlcore_set_min_fw_ver()` initialize capability/version arrays.
- Quirk bits alter bus transaction, TX/RX block alignment, firmware log availability, NVS layout, TX padding, TKIP header space, scheduled-scan behavior, probe templates, regulatory configuration, and AP session ID semantics.

## Control Flow And Integration
Lower drivers allocate and initialize `struct wl1271`, populate `wlcore_ops`, partition/register tables, firmware names, limits, rate tables, and quirks, then call `wlcore_probe()`. Common wlcore code calls ops through wrappers in `hw_ops.h`, allowing `tx.c`, `cmd.c`, `scan.c`, `event.c`, and `main.c` to share control flow while delegating chip-specific details.

TX integration is prominent: `tx.c` updates `tx_blocks_available`, `tx_allocated_blocks`, `tx_allocated_pkts[]`, `tx_frames_map`, `tx_frames[]`, `tx_queue_count[]`, `queue_stop_reasons[]`, `dummy_packet`, `aggr_buf`, `tx_res_if`, `fw_status`, and `links[]`. Runtime PM, watchdog, recovery, scan, and ROC paths are also coordinated through fields in this struct.

## State And Persistence Behavior
All state is in-memory kernel driver state. Some subregions are logically persistent across firmware reconfiguration, such as MAC addresses, firmware version requirements, vif private persistent tails, total freed packet counters used for PN tracking, and NVS/firmware blobs while the device is bound. No filesystem persistence is performed by this header.

## Dependencies
The header includes platform-device support plus wlcore internal headers `wlcore_i.h`, `event.h`, and `boot.h`. It depends heavily on mac80211/cfg80211 types, kernel workqueues, completions, mutexes, bitmaps, sk_buffs, debugfs, and endian-aware firmware structures.

## Risks And Test Signals
The main risk is shared-state coupling: many subsystems mutate `struct wl1271`, so invariants around locks, firmware state, TX/RX counters, role/link maps, and runtime PM must remain consistent. Chip ops must be fully populated for the selected family or wrappers must safely reject unsupported operations. Tests should cover probe/remove, firmware boot/version gating, suspend/resume, scan/ROC, TX/RX under load, AP/STA concurrency, recovery, debugfs state dumps, DFS/CAC where supported, and smart-config ops on wl18xx.
