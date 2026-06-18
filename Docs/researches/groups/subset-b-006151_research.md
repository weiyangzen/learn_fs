# subset-b-006151 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vmstat.c -->
# sources/distributed-fs/ceph-client/mm/vmstat.c

## Purpose
`mm/vmstat.c` is the kernel VM statistics aggregation and reporting hub. It keeps zone, node, NUMA, and VM event counters cheap on hot allocation/reclaim paths by batching updates in per-CPU differentials, folding them periodically into global atomics, and exposing snapshots through `/proc`, sysctl, and debugfs. It also owns fragmentation diagnostics used by compaction tooling and initializes the shared `mm_percpu_wq` used by VM per-CPU maintenance.

## Important APIs, types, and functions
The exported counter APIs are `__mod_zone_page_state()`, `mod_zone_page_state()`, `inc_zone_page_state()`, `dec_zone_page_state()`, `__mod_node_page_state()`, `mod_node_page_state()`, `inc_node_page_state()`, and `dec_node_page_state()`. They update `vm_zone_stat[]`, `vm_node_stat[]`, and per-zone/per-node per-CPU `s8` diff buckets. `all_vm_events()` and `vm_events_fold_cpu()` aggregate `vm_event_states`. NUMA helpers include `fold_vm_numa_events()`, `sum_zone_node_page_state()`, and `sum_zone_numa_event_state()`. Fragmentation helpers include `extfrag_for_order()` and `fragmentation_index()`. Initialization runs through `init_mm_internals()`, `vmstat_late_init()`, CPU hotplug callbacks, and optional `extfrag_debug_init()`.

## Control flow
Fast-path accounting adds deltas to per-CPU diff arrays until a threshold is crossed, then flushes the diff into zone/node atomics. SMP builds prefer `this_cpu_try_cmpxchg()` when available; otherwise updates are serialized with interrupt disabling and the `__mod_*` helpers. `refresh_cpu_vm_stats()` drains current-CPU differentials, optionally decays/drains per-CPU page lists, and folds global deltas. Per-CPU delayed work (`vmstat_update`) reschedules only while counters keep changing; the shepherd worker scans quiet CPUs and queues flushes where needed, skipping isolated CPUs. CPU hotplug disables work before down, folds dead CPU diffs, refreshes thresholds, and tracks `N_CPU` node state.

Reporting flows create snapshot arrays in `vmstat_start()`, populate zone, NUMA, node, dirty-limit, memmap, and event counters, then emit one `vmstat_text[]` line per counter. `/proc/buddyinfo`, `/proc/pagetypeinfo`, and `/proc/zoneinfo` iterate online nodes/zones via seq operations and print allocator state while taking zone locks where needed. Debugfs `extfrag` files compute unusable/free fragmentation indexes per order.

## State and persistence
State is in memory only: global atomic counters, per-zone/per-node atomics, per-CPU differentials, `vm_event_states`, NUMA event arrays, `nr_memmap_*` atomics, delayed work items, and sysctl values. No persistent storage is written. Userspace-visible state is synthesized through procfs/sysctl/debugfs on demand. NUMA stats can be disabled through sysctl, which also clears NUMA counters and toggles `vm_numa_stat_key`.

## Dependencies and integration points
This file integrates with the page allocator, reclaim, compaction, writeback, memcg-facing stat naming, CPU hotplug, NOHZ isolation, procfs, sysctl, and debugfs. The `NR_ZSPAGES` name is present when zsmalloc is enabled, and zswap event counters (`ZSWPIN`, `ZSWPOUT`, `ZSWPWB`) are exported through `/proc/vmstat` when configured.

## Risks and invariants
The main invariant is that per-CPU drift remains bounded by thresholds so global snapshots are acceptably approximate without breaching allocator watermarks. Byte-valued node stats are stored as pages in global counters and must be page-aligned. Locking must preserve hot-path performance and PREEMPT_RT correctness; the comments around `preempt_disable_nested()`, cmpxchg loops, and IRQ-safe zone walking are important. Diagnostic proc files intentionally trade precision for bounded lock hold time, for example capping free-list walks.

## Test signals
Useful checks are boot/init without CPU hotplug warnings, stable `/proc/vmstat` counter names/counts, `echo` or `cat` of `/proc/sys/vm/stat_refresh` with no unexpected negative-counter warnings, CPU online/offline cycles, NUMA stat toggling, and reading `/proc/buddyinfo`, `/proc/pagetypeinfo`, `/proc/zoneinfo`, plus debugfs `extfrag/*` when `CONFIG_COMPACTION` and `CONFIG_DEBUG_FS` are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/vmstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/workingset.c -->
# sources/distributed-fs/ceph-client/mm/workingset.c

## Purpose
`mm/workingset.c` implements refault-based workingset detection. It records eviction timestamps as xarray shadow entries, compares later refault distance against resident workingset size, and decides whether a faulted folio should be activated or restored as part of the active workingset. It also owns the LRU and shrinker for xarray nodes that contain only shadow entries.

## Important APIs, types, and functions
Public entry points include `workingset_age_nonresident()`, `workingset_eviction()`, `workingset_test_recent()`, `workingset_refault()`, `workingset_activation()`, and `workingset_update_node()`. `pack_shadow()` and `unpack_shadow()` encode/decode memcg id, NUMA node id, eviction timestamp, and workingset bit into xarray value entries. `shadow_nodes` is the global `list_lru` of shadow-only xarray nodes. `workingset_init()` calculates timestamp bucket orders and registers the `mm-shadow` shrinker.

## Control flow
On eviction, the caller supplies a locked, refcount-free folio. With multi-gen LRU enabled, `lru_gen_eviction()` records generation/tier data and returns a packed shadow. Otherwise `workingset_eviction()` samples `lruvec->nonresident_age`, shifts by the bucket order, ages nonresident pages by the folio size, and returns a shadow entry for the page cache or swap table. On refault, `workingset_refault()` records refault statistics, calls `workingset_test_recent()`, and activates/restores the folio when the computed refault distance fits within active/inactive competing pages. `workingset_activation()` ages nonresident counters on ordinary activation.

Shadow node maintenance is synchronous with xarray updates: `workingset_update_node()` adds nodes with only shadow values to `shadow_nodes` and removes nodes once pages reappear or the node is freeing. The shrinker estimates an allowed shadow-node budget and reclaims excess nodes by inverting from the LRU lock into the mapping `i_pages` lock, validating that the node still contains only values, and deleting it.

## State and persistence
All state is volatile: lruvec `nonresident_age`, packed shadow values stored in xarrays, per-lruvec workingset statistics, optional multi-gen LRU histograms, and the `shadow_nodes` list_lru. Memcg ids in shadows may become stale or be recycled; the code handles that as a speculative activation risk rather than persistent identity.

## Dependencies and integration points
The implementation sits between reclaim, page cache xarrays, swap shadow tables, memcg, lruvec accounting, multi-gen LRU, inode shrink/lru behavior, and vmstat counters such as `WORKINGSET_REFAULT_*`, `WORKINGSET_ACTIVATE_*`, `WORKINGSET_RESTORE_*`, `WORKINGSET_NODES`, and `WORKINGSET_NODERECLAIM`.

## Risks and invariants
Shadow packing is bit constrained; changes to `NODES_SHIFT`, memcg id bits, swap count bits, or LRU generation widths can break timestamp range or encoding. Refault decisions are intentionally approximate and can be wrong after counter wrap, memcg deletion, or id reuse. The shrinker relies on xarray node/value invariants under `i_pages` and inode locks; lock ordering and retry paths are critical.

## Test signals
Look for `/proc/vmstat` workingset counters increasing under page-cache and anonymous thrashing workloads, no lockdep reports from shadow-node reclaim, stable behavior with memcg deletion/recreation, multi-gen LRU enabled/disabled coverage, and shrinker activity that reduces `workingset_nodes` without corrupting page cache mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/workingset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zpdesc.h -->
# sources/distributed-fs/ceph-client/mm/zpdesc.h

## Purpose
`mm/zpdesc.h` defines `struct zpdesc`, the zsmalloc-specific descriptor overlay for pages that back zspages. It isolates zsmalloc metadata from direct `struct page` field access while preserving the current layout contract with the MM core.

## Important APIs, types, and functions
`struct zpdesc` overlays page fields used by zsmalloc: flags, `lru`, movable operations, `next` or huge-page `handle`, `zspage`, `first_obj_offset`, and refcount. Static offset assertions (`ZPDESC_MATCH`) enforce layout compatibility with `struct page`. Conversion helpers are `zpdesc_page()`, `zpdesc_folio()`, and `page_zpdesc()`. Inline wrappers provide lock, trylock, unlock, wait, get/put, local kmap, PFN conversion, movable/zsmalloc page-type marking, zone lookup, and lock-state testing.

## Control flow
The header itself has no runtime control flow beyond inline wrappers. zsmalloc allocates normal pages, casts the head page to `zpdesc`, fills zsmalloc metadata, and calls these helpers when it must interact with folio/page APIs, migration, kmap, zone accounting, or page flags.

## State and persistence
`zpdesc` state is the live page descriptor state for zsmalloc pages. It persists only while the backing page is allocated. `PG_private` marks the first component page, `PG_locked` is used by migration/page lock code, and `PageZsmalloc` is sticky until the page returns to the buddy allocator.

## Dependencies and integration points
The header depends on folio/page APIs, migration support, and pagemap helpers. It is consumed by `zsmalloc.c` to bridge zsmalloc internals with generic MM operations such as page migration and zone statistics.

## Risks and invariants
The layout must not grow into `struct page` fields that zsmalloc does not own, especially memcg-related overlap. `first_obj_offset` has only 24 usable bits because upper bits encode page type. Callers must avoid arbitrary casts and use helpers so future representation changes remain possible.

## Test signals
Build-time static assertions are the first signal. Runtime coverage comes from zsmalloc allocation/free, migration/compaction, highmem kmap paths, and debug VM checks around `PageZsmalloc`, first-page marking, and page locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zpdesc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zsmalloc.c -->
# sources/distributed-fs/ceph-client/mm/zsmalloc.c

## Purpose
`mm/zsmalloc.c` implements the zsmalloc compressed-object allocator used by zswap and other in-kernel compressed memory users. It packs variable-size objects into zspages composed of one or more order-0 pages, stores handles for stable object references, supports migration/compaction, and exposes pool statistics and a shrinker-driven compaction hook.

## Important APIs, types, and functions
External APIs include `zs_create_pool()`, `zs_destroy_pool()`, `zs_malloc()`, `zs_free()`, `zs_obj_read_begin()`, `zs_obj_read_end()`, `zs_obj_read_sg_begin()`, `zs_obj_read_sg_end()`, `zs_obj_write()`, `zs_compact()`, `zs_pool_stats()`, `zs_get_total_pages()`, `zs_lookup_class_index()`, and `zs_huge_class_size()`. Core structures are `struct zs_pool`, `struct size_class`, `struct zspage`, `struct zspage_lock`, `struct link_free`, and `struct zpdesc`. Module init creates `zs_handle` and `zspage` caches and registers movable page operations when compaction is enabled.

## Control flow
Pool creation computes size classes from `ZS_MIN_ALLOC_SIZE` through `PAGE_SIZE`, merges compatible classes, initializes fullness lists, creates optional debugfs stats, and registers a shrinker. Allocation adds a handle-sized header to the requested size, finds a class, reuses a zspage from the fullest non-full group if possible, or allocates a new zspage chain. `obj_malloc()` removes the first free object, records the handle in the object header or huge-page descriptor, updates the zspage free list and in-use count, and records the encoded PFN/object index in the external handle.

Freeing resolves the handle under `pool->lock`, takes the class lock, returns the object to the zspage free list, updates fullness, and frees empty zspages immediately if page locks can be acquired; otherwise deferred work frees them later. Object reads/writes hold the custom zspage read lock to prevent migration, then map/copy either one page or two pages when an object crosses a page boundary. Compaction isolates sparse source and dense destination zspages, migrates allocated objects by copying data and updating handles, then frees empty pages.

## State and persistence
Pool state includes size class lists, class stats, zspage metadata, handle objects in a slab cache, allocated page counts, compaction counters, deferred free work, and optional debugfs dentries. All state is in memory. Object identity persists only through zsmalloc handles until `zs_free()`; backing pages may migrate while handles are updated under locks.

## Dependencies and integration points
zsmalloc uses page allocation/free, highmem local mapping, scatterlists, shrinkers, debugfs, workqueues, movable page operations, zone page state `NR_ZSPAGES`, and `zpdesc` helpers. zswap depends on zsmalloc handles and scatterlist read support for compressed swap storage.

## Risks and invariants
The lock order is page lock, pool lock, class lock, zspage lock. Handle encoding depends on PFN/object-index bit widths and page size. Free objects must not span pages in a way that breaks `struct link_free`; class sizes and alignment enforce this. Migration must update every allocated object handle before the old page is reset. Empty zspage freeing cannot sleep in `zs_free()`, so deferred freeing must be reliable.

## Test signals
Exercise zswap/zram style allocate-write-read-free loops across sizes near class boundaries, objects crossing pages, huge-class allocations, compaction via the shrinker or manual `zs_compact()`, memory hotplug/NUMA allocation, `CONFIG_COMPACTION` migration, debugfs `zsmalloc/*/classes`, and vmstat `nr_zspages` accounting returning to baseline after pool destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zsmalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zswap.c -->
# sources/distributed-fs/ceph-client/mm/zswap.c

## Purpose
`mm/zswap.c` implements zswap, a compressed RAM cache for pages being swapped out. It intercepts swap writeout, compresses each page into a zsmalloc pool, indexes entries by swap offset, serves swapins from RAM, and writes cold entries back to the real swap device under pressure.

## Important APIs, types, and functions
Public MM integration functions include `zswap_is_enabled()`, `zswap_never_enabled()`, `zswap_total_pages()`, `zswap_store()`, `zswap_load()`, `zswap_invalidate()`, `zswap_swapon()`, `zswap_swapoff()`, `zswap_lruvec_state_init()`, `zswap_folio_swapin()`, and `zswap_memcg_offline_cleanup()`. Important types are `struct zswap_pool`, `struct zswap_entry`, and `struct crypto_acomp_ctx`. Tunables are module parameters `enabled`, `compressor`, `max_pool_percent`, `accept_threshold_percent`, and `shrinker_enabled`.

## Control flow
`zswap_setup()` creates the entry cache, CPU hotplug state for per-CPU compression contexts, shrink workqueue, memcg-aware list_lru, shrinker, and an initial compressor pool. Compressor parameter changes create or reuse pools and switch the current pool through the RCU-protected `zswap_pools` list, using `percpu_ref` to retire old pools after entries drain.

`zswap_store()` checks enablement, memcg zswap allowance, pool limits, and list_lru allocation. For each base page in the folio, `zswap_store_page()` allocates metadata, compresses or stores incompressible data through zsmalloc, inserts it into the swap xarray, frees stale entries, charges objcg memory, and adds the entry to the LRU. On failure or disablement it invalidates stale entries so writeback cannot later overwrite newer swap data.

`zswap_load()` looks up the swap xarray entry, rejects large folios, decompresses into the locked swapcache folio, marks it uptodate and dirty, erases the zswap entry, frees metadata/storage, and unlocks the folio. The shrinker walks the global LRU by memcg/node, gives referenced entries a second chance, then calls `zswap_writeback_entry()` to allocate swapcache, validate the xarray pointer, decompress, erase the entry, and issue `__swap_writepage()`.

## State and persistence
State is volatile: zswap entries in per-swap-type xarrays, compressed objects in zsmalloc pools, per-CPU crypto contexts, pool refs/list, global and memcg list_lru membership, objcg charges, debugfs counters, and rejection/writeback statistics. Swap devices remain persistent storage; zswap is only an in-memory cache and invalidates entries on swapoff or successful load/writeback.

## Dependencies and integration points
zswap depends on swapcache/swap device APIs, xarray, crypto acomp, zsmalloc, memcg/objcg zswap charging, list_lru, shrinkers, CPU hotplug, workqueues, debugfs, vm events (`ZSWPIN`, `ZSWPOUT`, `ZSWPWB`), and the folio swap path.

## Risks and invariants
The xarray entry must match the swap slot being loaded or written back; pointer revalidation prevents stale compressed data from overwriting newer swap content. Large folios are not supported on load. Pool lifetime depends on correct `percpu_ref` get/put and RCU removal. The lock ordering is `zswap_tree.lock` before pool LRU lock except writeback’s validated exception. Compression failure accounting is approximate by design.

## Test signals
Run swap workloads with zswap enabled/disabled, compressor changes at runtime, memcg writeback disabled/enabled, pool limit pressure, swapoff, CPU hotplug, and shrinker-triggered writeback. Observe `/sys/module/zswap/parameters/*`, debugfs `zswap/*`, vmstat `zswpin/zswpout/zswpwb`, objcg events, no stale-data warnings, and no decompression failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/zswap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/6lowpan_i.h -->
# sources/distributed-fs/ceph-client/net/6lowpan/6lowpan_i.h

## Purpose
`net/6lowpan/6lowpan_i.h` is the private header shared by the 6LoWPAN core, debugfs, neighbor discovery, and IPHC code. It centralizes link-layer type checks and optional debugfs hooks.

## Important APIs, types, and functions
`lowpan_is_ll()` checks the `struct lowpan_dev` link-layer type after the caller has established `dev->type == ARPHRD_6LOWPAN`. The header declares `lowpan_ndisc_ops`, `addrconf_ifid_802154_6lowpan()`, and debugfs lifecycle functions. When `CONFIG_6LOWPAN_DEBUGFS` is disabled, static inline no-op debugfs stubs keep core code unconditional.

## Control flow
The only runtime logic is the inline link-layer comparison and, depending on configuration, calls either into debugfs implementation functions or no-op stubs.

## State and persistence
This header owns no state. It exposes access to per-device `lowpan_dev(dev)->lltype` and declares functions that manipulate per-device context/debugfs state elsewhere.

## Dependencies and integration points
It depends on `linux/netdevice.h` and `net/6lowpan.h`. It connects `core.c`, `debugfs.c`, `iphc.c`, and `ndisc.c` without exporting these private helpers to unrelated networking code.

## Risks and invariants
Callers must only use `lowpan_is_ll()` on 6LoWPAN netdevices because it dereferences `lowpan_dev(dev)`. The debugfs stubs must match the real function signatures so configuration changes do not alter call sites.

## Test signals
Build both with and without `CONFIG_6LOWPAN_DEBUGFS`, and exercise registration of IEEE802154 and BTLE 6LoWPAN devices to ensure `lowpan_is_ll()` dispatch paths match the link type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/6lowpan_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/Kconfig -->
# sources/distributed-fs/ceph-client/net/6lowpan/Kconfig

## Purpose
`net/6lowpan/Kconfig` defines the configuration surface for the 6LoWPAN subsystem, optional debugfs controls, and next-header/generic-header compression modules.

## Important symbols
`6LOWPAN` is a tristate menuconfig depending on `IPV6`. `6LOWPAN_DEBUGFS` depends on `6LOWPAN` and `DEBUG_FS`. `6LOWPAN_NHC` is a tristate compression framework defaulting to enabled when 6LoWPAN is enabled. Under it, RFC6282 options include destination, fragment, hop-by-hop, IPv6, mobility, routing, and UDP NHC modules. RFC7400 generic header compression options cover hop, UDP, ICMPv6, destination, fragment, and routing headers.

## Control flow
Kconfig selection controls compilation only. The core module later requests common RFC6282 NHC modules with `request_module_nowait()`, while individual `obj-*` lines in the Makefile decide whether compression helpers are built-in, modules, or absent.

## State and persistence
There is no runtime state. Persistent effects are build configuration choices in kernel config files.

## Dependencies and integration points
The configuration integrates with IPv6, debugfs, the 6LoWPAN core module, the NHC registry, and link-layer providers such as IEEE 802.15.4 and Bluetooth 6LoWPAN.

## Risks and invariants
Disabling NHC modules can reduce compression coverage and cause IPHC to carry next headers inline. `6LOWPAN_DEBUGFS` exposes runtime context manipulation, so it must remain gated by `DEBUG_FS`.

## Test signals
Build matrix coverage should include 6LoWPAN built-in and module modes, debugfs on/off, `6LOWPAN_NHC=n`, and individual NHC/GHC modules as built-ins or modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/Makefile -->
# sources/distributed-fs/ceph-client/net/6lowpan/Makefile

## Purpose
`net/6lowpan/Makefile` maps the 6LoWPAN Kconfig symbols to kernel objects and determines which sources become the core `6lowpan` module versus separate compression modules.

## Important build rules
`obj-$(CONFIG_6LOWPAN) += 6lowpan.o` builds the core aggregate. `6lowpan-y` includes `core.o`, `iphc.o`, `nhc.o`, and `ndisc.o`; `debugfs.o` is conditionally added for `CONFIG_6LOWPAN_DEBUGFS`. RFC6282 NHC modules and RFC7400 GHC modules are emitted as separate objects controlled by their individual config symbols.

## Control flow
There is no runtime flow. Build-time object composition determines which module init/exit functions and compression descriptors are present.

## State and persistence
No runtime state is held here. The persistent result is the kernel build artifact layout.

## Dependencies and integration points
The Makefile ties Kconfig symbols to the core module and helper modules consumed by `core.c` autoload requests and `iphc.c` calls into the NHC registry.

## Risks and invariants
Core IPHC code assumes `nhc.o` is part of `6lowpan.o`; missing that object would break next-header compression dispatch. Optional modules must keep names aligned with `request_module_nowait()` and `module_lowpan_nhc()` registrations.

## Test signals
Check generated objects/modules for representative configs and verify `modprobe 6lowpan` can autoload common `nhc_*` modules when available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/core.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/core.c

## Purpose
`net/6lowpan/core.c` provides core registration and lifecycle glue for 6LoWPAN netdevices. It initializes per-device 6LoWPAN properties, registers notifier handling for link-local addressing and context reset, and initializes global debugfs and NHC autoload requests.

## Important APIs, types, and functions
Exported functions are `lowpan_register_netdevice()`, `lowpan_register_netdev()`, `lowpan_unregister_netdevice()`, `lowpan_unregister_netdev()`, and `addrconf_ifid_802154_6lowpan()`. The file also defines `lowpan_event()` as a netdevice notifier, `lowpan_notifier`, `lowpan_module_init()`, and `lowpan_module_exit()`.

## Control flow
Registration sets `addr_len` based on link-layer type, sets `ARPHRD_6LOWPAN`, clamps MTU to `IPV6_MIN_MTU`, initializes the IPHC context table ids and lock, installs 6LoWPAN neighbor discovery ops, registers the netdevice, and creates per-device debugfs. `lowpan_register_netdev()` wraps that in RTNL locking; unregister wrappers mirror it. The notifier adds an IEEE802154 short-address link-local address on `NETDEV_UP` or `NETDEV_CHANGE`, and clears active IPHC context flags on `NETDEV_DOWN`. Module init creates debugfs, registers the notifier, and asynchronously requests common NHC modules.

## State and persistence
State is per netdevice: link-layer type, IPHC context table ids/flags, neighbor discovery ops, debugfs dentries, and auto-configured link-local IPv6 addresses. Context active bits are volatile and cleared on device down.

## Dependencies and integration points
The file integrates with netdevice registration/RTNL, IPv6 addrconf, IEEE802154 address helpers, 6LoWPAN debugfs, neighbor discovery ops from `ndisc.c`, and NHC compression modules.

## Risks and invariants
`lowpan_unregister_netdevice()` calls `unregister_netdevice()` before debugfs cleanup, so debugfs users must not outlive device teardown unsafely. `addrconf_ifid_802154_6lowpan()` rejects invalid/all-zero short addressing and constructs the RFC-derived IID; mistakes here affect SLAAC. Context reset on `NETDEV_DOWN` avoids stale compression contexts.

## Test signals
Register/unregister IEEE802154 and BTLE 6LoWPAN devices, verify MTU/type/address length, check link-local address creation for valid short addresses, ensure context flags clear on down/up cycles, and verify debugfs directories are created/removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/debugfs.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/debugfs.c

## Purpose
`net/6lowpan/debugfs.c` exposes 6LoWPAN runtime inspection and tuning through debugfs, primarily for IPHC context table entries and IEEE802154 short-address visibility.

## Important APIs, types, and functions
Exported-to-core functions are `lowpan_dev_debugfs_init()`, `lowpan_dev_debugfs_exit()`, `lowpan_debugfs_init()`, and `lowpan_debugfs_exit()`. Per-context files use `lowpan_ctx_flag_active_*`, `lowpan_ctx_flag_c_*`, `lowpan_ctx_plen_*`, and `lowpan_ctx_pfx_*` handlers. `lowpan_context_show()` summarizes active contexts, and `lowpan_short_addr_get()` exposes the IEEE802154 short address.

## Control flow
Global init creates `/sys/kernel/debug/6lowpan`. Device init creates a directory named for the netdevice, a `contexts` directory, a summary `show` file, and one directory per context id with `active`, `compression`, `prefix`, and `prefix_len` files. Writes validate boolean flags, prefix length <= 128, or an eight-field IPv6 prefix string, then update context fields under the context-table spinlock where needed. IEEE802154 devices also get an `ieee802154/short_addr` file read under RTNL.

## State and persistence
Debugfs reflects and mutates live per-device IPHC context table state: active flag, compression flag, prefix, and prefix length. It does not persist across device removal or reboot. Dentries are tracked through `lowpan_debugfs` and per-device `iface_debugfs`.

## Dependencies and integration points
The file depends on debugfs, seq_file helpers, user copy/parsing, RTNL for reading IEEE802154 short address, and the 6LoWPAN IPHC context definitions in `net/6lowpan.h`.

## Risks and invariants
Input validation is intentionally minimal but must reject invalid booleans, overlong prefixes, malformed prefix strings, and copy faults. Prefix and prefix length reads/writes must stay synchronized with IPHC compression/decompression readers through `ctx.lock`. Debugfs entries are diagnostic/control-plane only and should not be assumed present in production configs.

## Test signals
With `CONFIG_6LOWPAN_DEBUGFS`, create a 6LoWPAN device and read/write every context file. Verify invalid values return `-EINVAL`, prefix writes round-trip, active contexts appear in `contexts/show`, short address reads work for IEEE802154, and recursive removal happens on device unregister and module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/iphc.c -->
# sources/distributed-fs/ceph-client/net/6lowpan/iphc.c

## Purpose
`net/6lowpan/iphc.c` implements RFC6282 IPv6 header compression and decompression for 6LoWPAN. It converts between full IPv6 headers and compact IPHC encodings, supports stateless and context-based address compression, handles multicast forms, delegates next-header compression to NHC modules, and adapts link-layer address reconstruction for IEEE802154, BTLE, EUI-48, and EUI-64 cases.

## Important APIs, types, and functions
The exported entry points are `lowpan_header_compress()` and `lowpan_header_decompress()`. Important helpers include context lookup (`lowpan_iphc_ctx_get_by_id()`, `lowpan_iphc_ctx_get_by_addr()`, `lowpan_iphc_ctx_get_by_mcast_addr()`), address reconstruction (`lowpan_iphc_uncompress_addr()`, `lowpan_iphc_uncompress_ctx_addr()`, multicast variants, and link-layer helpers), address compression (`lowpan_compress_addr_64()`, `lowpan_compress_ctx_addr()`, multicast variants), and traffic-class/flow-label compression/decompression (`lowpan_iphc_tf_compress()`, `lowpan_iphc_tf_decompress()`). Numerous `LOWPAN_IPHC_*` masks define dispatch byte fields.

## Control flow
Decompression consumes the IPHC bytes from the skb, optional CID byte, traffic class/flow label, optional inline next header, hop limit, source address, destination address, and optional NHC-compressed next-header data. It reconstructs an `ipv6hdr`, sets packet type for multicast versus host traffic, computes payload length, pushes the IPv6 header back onto the skb, and resets MAC/network headers. Context-based branches hold the per-device context-table spinlock while resolving and using a context.

Compression starts from an IPv6 skb, reserves a small local header buffer, looks up destination and source compression contexts under the context lock and copies selected context entries locally, emits CID if needed, compresses traffic class/flow label, tries NHC next-header compression, compresses hop limit, source address, destination address, and finally applies NHC compression if selected. It removes the IPv6 header from the skb and pushes the compact IPHC header in its place.

## State and persistence
The function-level state is transient skb/header data. Persistent runtime inputs are per-device IPHC contexts (`id`, active/compression flags, prefix, prefix length), link-layer addresses passed by callers, and registered NHC handlers. The code mutates skb data/headroom and packet type, but does not store data beyond debug traces.

## Dependencies and integration points
The implementation depends on `net/6lowpan.h` helpers for skb fetch/push and address utilities, `net/ipv6.h`, `nhc.h` registry functions, IEEE802154 address conversions, `lowpan_dev(dev)->ctx`, and callers in 6LoWPAN link-layer transmit/receive paths.

## Risks and invariants
Every compressed field fetch must bounds-check skb data; failures return `-EINVAL`/`-EIO`. Context ids must refer to active contexts, and compression must copy contexts out from under the lock before using them later. Link-local zero-padding checks and IID reconstruction must match RFC address forms. The local header buffer must be large enough for worst-case compressed output. Compression and decompression must remain symmetric across stateless, context, multicast, and NHC paths.

## Test signals
Use packet-level tests for full inline IPv6 headers, all TF modes, hop limits 1/64/255/inline, stateless link-local IID compression modes, context-based source/destination compression, multicast 8/32/48/128-bit forms, multicast context compression, IEEE802154 short/long address reconstruction, BTLE/EUI-48 cases, malformed truncated skbs, and NHC present/absent behavior. Verify round-trip packets with debug dumps and IPv6 payload length correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/6lowpan/iphc.c -->
