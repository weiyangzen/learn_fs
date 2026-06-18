# subset-b-006133 mm memory-management research

This grouped report covers the requested memory-management source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memblock.c -->
# sources/distributed-fs/ceph-client/mm/memblock.c

## Purpose

This file implements Linux's early-boot memblock allocator and region database. It tracks usable physical memory, reserved allocations, and optionally the architecture physical memory map before slab and the buddy allocator are fully available. It is responsible for adding/removing memory ranges, reserving boot-time allocations, finding free physical ranges with NUMA/flag constraints, handing free memory to the buddy allocator during boot, exposing optional debugfs state, and supporting named `reserve_mem=` allocations including kexec handover preservation.

## Important APIs, types, and functions

The central state is the global `struct memblock memblock` with `memory` and `reserved` `struct memblock_type` arrays, plus optional `struct memblock_type physmem`. Region entries carry base, size, NUMA node, and `enum memblock_flags` such as `MEMBLOCK_HOTPLUG`, `MEMBLOCK_MIRROR`, `MEMBLOCK_NOMAP`, `MEMBLOCK_DRIVER_MANAGED`, `MEMBLOCK_RSRV_NOINIT`, `MEMBLOCK_RSRV_KERN`, and `MEMBLOCK_KHO_SCRATCH`.

Important mutators are `memblock_add()`, `memblock_add_node()`, `memblock_remove()`, `__memblock_reserve()`, `memblock_physmem_add()`, `memblock_set_node()`, `memblock_mark_hotplug()`, `memblock_clear_hotplug()`, `memblock_mark_mirror()`, `memblock_mark_nomap()`, `memblock_clear_nomap()`, `memblock_reserved_mark_noinit()`, `memblock_reserved_mark_kern()`, `memblock_mark_kho_scratch()`, and `memblock_clear_kho_scratch()`. They are built on `memblock_add_range()`, `memblock_isolate_range()`, `memblock_setclr_flag()`, `memblock_insert_region()`, `memblock_remove_region()`, and `memblock_merge_regions()`.

Allocation APIs include `memblock_alloc_range_nid()`, `memblock_phys_alloc_range()`, `memblock_phys_alloc_try_nid()`, `memblock_alloc_exact_nid_raw()`, `memblock_alloc_try_nid_raw()`, `memblock_alloc_try_nid()`, and `__memblock_alloc_or_panic()`. Allocation search flows through `memblock_find_in_range_node()`, `__memblock_find_range_bottom_up()`, and `__memblock_find_range_top_down()`, using `choose_memblock_flags()` for mirrored-memory and KHO scratch-only policy.

Iteration and query helpers include `__next_mem_range()`, `__next_mem_range_rev()`, `__next_mem_pfn_range()`, `memblock_addrs_overlap()`, `memblock_overlaps_region()`, `memblock_is_reserved()`, `memblock_is_memory()`, `memblock_is_map_memory()`, `memblock_search_pfn_nid()`, `memblock_is_region_memory()`, `memblock_is_region_reserved()`, `memblock_phys_mem_size()`, `memblock_reserved_size()`, `memblock_reserved_kern_size()`, `memblock_estimated_nr_free_pages()`, `memblock_start_of_DRAM()`, and `memblock_end_of_DRAM()`.

Boot handoff and cleanup are handled by `free_reserved_area()`, `memblock_free()`, `memblock_phys_free()`, `memblock_discard()`, `free_unused_memmap()`, `memmap_init_reserved_pages()`, `free_low_memory_core_early()`, `reset_all_zones_managed_pages()`, and `memblock_free_all()`. Named reservations use `reserve_mem()`, `reserved_mem_add()`, `reserve_mem_find_by_name()`, and `reserve_mem_release_by_name()`. Kexec handover support adds `reserved_mem_preserve()`, `prepare_kho_fdt()`, `reserve_mem_init()`, `reserve_mem_kho_retrieve_fdt()`, and `reserve_mem_kho_revive()`.

## Control flow

Architecture boot code populates memory with `memblock_add()` or `memblock_add_node()`, optionally records physical memory in `physmem`, and reserves early allocations through `memblock_alloc*()` or `__memblock_reserve()`. Range addition is a two-pass operation: `memblock_add_range()` first counts pieces not covered by existing sorted regions, resizes the array if needed, then inserts only uncovered spans and merges neighboring regions that have matching node and flags.

Removal and flag changes first call `memblock_isolate_range()` so target boundaries align with region boundaries, then remove regions or mutate flags, and finally merge compatible neighbors. This keeps `memory` and `reserved` sorted and minimally split. Array growth uses `memblock_double_array()`, which either uses slab when available or allocates from memblock while avoiding a soon-to-be-reserved range for the reserved-array case.

Allocation starts in `memblock_alloc_range_nid()`: it rejects late use once slab is available with a warning and `kzalloc_node()` fallback, validates alignment, searches the requested node and range, reserves the chosen address as `MEMBLOCK_RSRV_KERN`, optionally falls back to any node, optionally retries without the mirror flag, registers the allocation with kmemleak unless `MEMBLOCK_ALLOC_NOLEAKTRACE` was used, and calls `accept_memory()` for confidential-computing guests. The virtual-address wrappers cap `max_addr` by `memblock.current_limit`, retry without the preferred lower bound, and optionally zero memory.

The free-range iterators compute intersections of an include type and the holes before an exclude type, normally `memory` minus `reserved`. `should_skip_region()` filters only `memblock.memory` for NUMA, hotplug, mirror, nomap, driver-managed, and KHO scratch flags. The reverse iterator mirrors the same logic from high addresses downward, giving top-down allocation deterministic high-address selection.

At boot handoff, `memblock_free_all()` frees unused memmap holes, resets zone managed-page accounting, clears KHO scratch-only allocation mode, initializes PageReserved state for reserved and NOMAP ranges, frees all non-reserved low memory ranges to the buddy allocator, and updates total RAM pages. Unless `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled, `memblock_discard()` later frees dynamically allocated memblock arrays and clears `memblock_memory`.

Named `reserve_mem=` parsing accepts `size:align:name`, validates capacity and name length, revives a prior KHO reservation if possible, otherwise allocates a physical memblock region, and stores it in a small fixed table. KHO preservation serializes named reservations into an FDT subtree and preserves the backing pages across kexec; revive validates compatibility, alignment, and size before reusing the old physical address.

## State and persistence behavior

Most state is early-boot global memory metadata in `memblock`, `physmem`, `max_low_pfn`, `min_low_pfn`, `max_pfn`, `max_possible_pfn`, resize/debug flags, and KHO scratch-only mode. Region arrays begin as static `__initdata_memblock` storage and may move to memblock-allocated pages or slab; `memblock_discard()` frees dynamic arrays when the architecture does not keep memblock data.

The allocator persists only until the buddy allocator takes ownership of free pages. The optional `CONFIG_ARCH_KEEP_MEMBLOCK` path keeps memblock arrays available for later debugfs and queries. Named `reserve_mem` entries persist in `reserved_mem_table` after boot and can be found or released by name. With `CONFIG_KEXEC_HANDOVER`, named reservations may persist across a kexec cycle through preserved pages and an FDT descriptor. Debug state is exposed under debugfs when enabled, including raw memblock arrays when memblock is kept and a `reserve_mem_param` listing when named reservations exist.

## Dependencies and integration points

The file depends on core kernel headers for init, slab, PFN conversion, kmemleak, debugfs, seq_file, mutexes, string formatting, and `linux/memblock.h`; it uses architecture hooks such as `__pa`, `__va`, `phys_to_virt`, `pfn_to_page`, `for_each_valid_pfn`, `memblock_free_pages`, `early_pfn_to_nid`, and `accept_memory()`. It integrates with NUMA, memory hotplug filtering, sparsemem/vmemmap behavior, deferred struct-page initialization, KASAN tag handling, kmemleak, confidential-computing memory acceptance, KHO/libfdt, debugfs, early parameters (`memblock=debug`), and boot command-line setup (`reserve_mem=`).

The allocator is used by architecture setup, early page-table/KASAN/initrd/reserved-memory code, zone/page allocator initialization, and subsystems needing physically contiguous boot memory before normal allocation is available. It also exports `contig_page_data` on non-NUMA builds and `reserve_mem_find_by_name()` for modules or built-in users of named reserved memory.

## Risks

The major correctness risk is corruption of sorted, non-overlapping memblock arrays: off-by-one errors in split/merge, address overflow around `base + size`, or incorrect resize reservations can leak, double reserve, or free boot-critical memory. Allocation policy is also delicate: `current_limit`, top-down/bottom-up mode, exact NUMA requests, mirror fallback, NOMAP/driver-managed filtering, and KHO scratch filtering all affect whether early allocations land in usable memory.

Late calls after slab is live are risky because memblock metadata may already be discarded, so the code warns and falls back only in `memblock_alloc_range_nid()`. `free_reserved_area()` refuses to operate with deferred page initialization, and misuse can release pages whose `struct page` state is not initialized. KHO and named reservation paths risk preserving stale or mis-sized memory if FDT validation or alignment checks miss a case. Debugfs array exposure depends on `CONFIG_ARCH_KEEP_MEMBLOCK`; without it, raw memory/reserved arrays are not valid after discard.

## Test signals

Useful test signals include early boot logs with `memblock=debug`, successful boot on NUMA and UMA machines, correct `/sys/kernel/debug/memblock/*` content when enabled, absence of memblock resize panics, no bootmem overlap with initrd/FDT/kernel image, stable `max_pfn` and zone managed-page accounting after `memblock_free_all()`, and kmemleak not reporting memblock allocations as leaks. Specific coverage should exercise memory limits (`mem=`, memblock cap/enforce paths), hotplug/movable-node memory, mirrored memory fallback, NOMAP reserved ranges, deferred struct-page init, confidential-computing memory acceptance, `reserve_mem=` find/release behavior, and KHO preserve/revive across kexec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memblock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memcontrol-v1.c -->
# sources/distributed-fs/ceph-client/mm/memcontrol-v1.c

## Purpose

This file contains cgroup v1-specific memory controller behavior that is split away from the shared memcg implementation. It implements legacy soft-limit reclaim, cgroup-v1 threshold and eventfd notification plumbing, legacy memory+swap accounting transitions, OOM notification and userspace OOM wait behavior, v1 cgroup file handlers, stats formatting, kmem/tcp accounting compatibility, and per-memcg event-counter allocation.

## Important APIs, types, and functions

Soft-limit state is represented by `struct mem_cgroup_tree_per_node`, `struct mem_cgroup_tree`, and the global `soft_limit_tree`, which keeps per-node rbtrees of `struct mem_cgroup_per_node` ordered by `usage_in_excess`. The key functions are `memcg1_update_tree()`, `memcg1_remove_from_trees()`, `memcg1_soft_limit_reclaim()`, `mem_cgroup_largest_soft_limit_node()`, and `mem_cgroup_soft_reclaim()`.

Legacy event plumbing uses `struct mem_cgroup_eventfd_list` for OOM notifiers and `struct mem_cgroup_event` for `cgroup.event_control` registrations. Registration helpers include `__mem_cgroup_usage_register_event()`, `mem_cgroup_usage_register_event()`, `memsw_cgroup_usage_register_event()`, `__mem_cgroup_usage_unregister_event()`, `mem_cgroup_oom_register_event()`, `mem_cgroup_oom_unregister_event()`, `memcg_write_event_control()`, `memcg_event_wake()`, and `memcg_event_remove()`.

Charge and swap hooks include `memcg1_commit_charge()`, `memcg1_swapout()`, `memcg1_swapin()`, and `memcg1_uncharge_batch()`. Per-cpu event state is `struct memcg1_events_percpu`, driven by `memcg1_charge_statistics()`, `memcg1_event_ratelimit()`, and `memcg1_check_events()`.

OOM handling uses `memcg_oom_lock`, `memcg_oom_waitq`, `struct oom_wait_info`, `mem_cgroup_oom_trylock()`, `mem_cgroup_oom_unlock()`, `mem_cgroup_mark_under_oom()`, `mem_cgroup_unmark_under_oom()`, `memcg_oom_wake_function()`, `memcg1_oom_recover()`, `mem_cgroup_oom_synchronize()`, `memcg1_oom_prepare()`, and `memcg1_oom_finish()`.

The v1 control-file layer is expressed by `MEMFILE_PRIVATE()`, `MEMFILE_TYPE()`, `MEMFILE_ATTR()`, `enum res_type`, the resource attribute enum, `mem_cgroup_read_u64()`, `mem_cgroup_write()`, `mem_cgroup_reset()`, `mem_cgroup_resize_max()`, `mem_cgroup_force_empty()`, `mem_cgroup_hierarchy_*()`, `mem_cgroup_swappiness_*()`, `mem_cgroup_oom_control_*()`, and the exported cftype arrays `mem_cgroup_legacy_files[]` and `memsw_files[]`. Stats helpers include `memcg_numa_stat_show()`, `reparent_memcg1_state_local()`, `reparent_memcg1_lruvec_state_local()`, and `memcg1_stat_format()`. Kmem/socket compatibility hooks are `memcg1_account_kmem()`, `memcg1_charge_skmem()`, `memcg1_alloc_events()`, `memcg1_free_events()`, and `memcg1_init()`.

## Control flow

Soft-limit tracking begins when charge or uncharge paths call `memcg1_commit_charge()` or `memcg1_uncharge_batch()`. Those update v1 PGPGIN/PGPGOUT and per-cpu page-event counters with interrupts disabled, then `memcg1_check_events()` periodically fires threshold checks and soft-limit tree updates. `memcg1_update_tree()` walks the charged memcg and ancestors, computes `soft_limit_excess()`, removes any existing rbnode, and reinserts it by excess if needed. On PREEMPT_RT, the event/soft-limit path is disabled; with multigenerational LRU enabled, excess cgroups call `lru_gen_soft_reclaim()` instead of maintaining the rbtrees.

Reclaim enters through `memcg1_soft_limit_reclaim()`, which ignores high-order requests and the LRU-gen case. It takes the per-node largest-excess rbnode, pins the memcg css, reclaims descendants with `mem_cgroup_soft_reclaim()`, reinserts the node if it remains over its soft limit, and advances to other nodes if no pages were reclaimed. The reclaim loops are bounded by `MEM_CGROUP_MAX_RECLAIM_LOOPS` and `MEM_CGROUP_MAX_SOFT_LIMIT_RECLAIM_LOOPS` because soft limits are best-effort.

Threshold notifications are registered through the legacy `cgroup.event_control` write path. `memcg_write_event_control()` parses eventfd/control-fd/args, validates that the control file belongs to the same memory cgroup, maps known file names to register/unregister callbacks, registers the event, polls the eventfd to attach a wake handler, and stores the event on `memcg->event_list`. Usage thresholds are stored as sorted RCU-protected arrays with a spare buffer for unregister; threshold checks signal eventfds when usage crosses entries in either direction. OOM and pressure events are separate callback types, with OOM events stored on `memcg->oom_notify`.

When an eventfd is closed, `memcg_event_wake()` sees `EPOLLHUP`, removes the event from the memcg list under `event_list_lock`, and schedules `memcg_event_remove()` to sleepably unregister callbacks, signal final notification, drop eventfd and css references, and free memory. `memcg1_css_offline()` removes remaining registered events asynchronously during cgroup offline.

Swapout for cgroup v1 transfers a page's memory+swap charge to a swap entry only when legacy memsw accounting is active. `memcg1_swapout()` finds an online ancestor if the original memcg was offlined, records the swap cgroup id, clears the folio's memcg data, adjusts memory and memsw page counters, updates stats, and drops the object cgroup reference. `memcg1_swapin()` removes duplicate swap-entry accounting after a charged page enters swapcache.

OOM control supports both kernel OOM killing and legacy userspace OOM handling. `memcg1_oom_prepare()` either records `current->memcg_in_oom` for user-fault completion when `oom_kill_disable` is set, or marks the hierarchy under OOM, tries to lock the subtree, and notifies eventfd listeners. `mem_cgroup_oom_synchronize()` runs at page-fault exit, waits on `memcg_oom_waitq` for userspace recovery, and cleans up task/css state. `memcg1_oom_recover()` wakes waiters when limits are raised or OOM killing is re-enabled.

Control-file writes parse byte values into pages and dispatch by encoded resource type and attribute. Limit writes call `mem_cgroup_resize_max()` for memory or memsw, which preserves the invariant `memory.max <= memsw.max`, drains stocks once, and attempts reclaim before failing busy. Kmem limit writes are accepted as deprecated no-ops, while TCP kmem limits update `tcpmem` and enable the socket-accounting static key in the right order. Soft-limit writes update `memcg->soft_limit` except on PREEMPT_RT. Reset writes clear watermarks or failcnts. Stats output flushes rstat-style memcg stats, prints v1-compatible local and hierarchical counters, LRU bytes, limits, events, and optional debug VM costs.

## State and persistence behavior

The file maintains per-node soft-limit rbtrees allocated at `subsys_initcall()` time, per-memcg event lists, per-memcg OOM notifier lists, per-memcg threshold arrays protected by mutex plus RCU, global `memcg_oom_lock`, a global OOM waitqueue, per-cpu v1 event counters allocated per memcg, and cgroup file state encoded in `cftype.private`.

All state is runtime kernel memory. It persists for the lifetime of the memory cgroup or boot, not across reboot. Threshold arrays and event registrations persist until eventfd close or css offline; unregister uses RCU grace periods before old arrays can be reused or freed. Soft-limit rbnode membership persists until usage falls below soft limit, the memcg is removed from trees, or reclaim temporarily removes/reinserts it. OOM `under_oom` and `oom_lock` markers are transient but hierarchy-wide. TCP memcg activation persists once enabled for a memcg because static-key activation is not undone here.

## Dependencies and integration points

The file depends on the shared memcg implementation and interfaces from `linux/memcontrol.h`, swap and swap cgroup code, pagewalk/backing-dev infrastructure, eventfd and poll APIs, sorting, file permission checks, `seq_buf`, `internal.h`, `swap.h`, and `memcontrol-v1.h`. It integrates with the cgroup core through `struct cftype`, kernfs open files, `css_tryget_online_from_dir()`, cgroup v1 file names, and cgroup offline callbacks.

It also integrates with reclaim (`mem_cgroup_shrink_node()`, `try_to_free_mem_cgroup_pages()`), LRU generation (`lru_gen_enabled()`, `lru_gen_soft_reclaim()`), page counters, memcg stats and events, swap slot ownership (`swap_cgroup_record()`, `mem_cgroup_uncharge_swap()`), object cgroups, vmpressure, socket memory accounting (`memcg_sockets_enabled_key`), global swappiness, and cgroup-v1 memory+swap file registration through `memsw_files[]`.

## Risks

This is compatibility-heavy code with several deprecated interfaces. Event-control parsing is intentionally tied to cgroup-v1 filenames and regular cgroupfs dentries; mistakes can leave css/eventfd references leaked or callbacks attached to the wrong memcg. Threshold arrays rely on a primary/spare RCU protocol; allocation, unregister, and current-threshold bookkeeping must stay synchronized with usage checks. OOM handling is sensitive to hierarchy locking and waitqueue wake matching, and bugs can strand page-faulting tasks when userspace OOM handling is enabled.

Soft-limit reclaim is best-effort and race-tolerant, so stale rbnode ordering is acceptable but tree corruption is not. PREEMPT_RT disables event-control and soft-limit behavior, so tests must account for `-EOPNOTSUPP`. Memory/memsw limit updates must preserve their invariant or accounting can become inconsistent. Swapout handles offlined memcgs by charging an online ancestor, and bugs there can leak memsw counts or record unusable private IDs. Socket memory activation requires static-key ordering before `tcpmem_active`; reordering can silently lose socket accounting.

## Test signals

Useful tests include cgroup-v1 memory controller boot and mount tests, reads/writes for `memory.limit_in_bytes`, `memory.memsw.limit_in_bytes`, `memory.soft_limit_in_bytes`, `memory.failcnt`, `memory.max_usage_in_bytes`, `memory.force_empty`, `memory.swappiness`, `memory.oom_control`, kmem/tcp compatibility files, and `memory.stat`. Functional coverage should trigger threshold eventfds on usage and memsw crossings, close eventfds and remove cgroups to verify async cleanup, exercise OOM notification and userspace OOM wait/recover paths, and run soft-limit reclaim under memory pressure on non-RT kernels without LRU-gen taking over.

Additional signals are correct `memory.numa_stat` output on NUMA builds, no leaked eventfd/css references after cgroup deletion, stable page counters through swapout/swapin and offlined memcgs, successful limit resize with stock draining and reclaim, and warnings only once for deprecated interfaces. Regression tests should include cgroup v2/default hierarchy builds where these v1 paths are either inactive or guarded by `do_memsw_account()` and cgroup mode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memcontrol-v1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memcontrol-v1.h -->
# sources/distributed-fs/ceph-client/mm/memcontrol-v1.h

## Purpose

This header declares the interface between the shared memory-controller code and the cgroup-v1-specific implementation in `memcontrol-v1.c`. It also provides common memcg iteration macros, shared declarations used by both cgroup v1 and v2 code, v1 resource-type encoding constants, and no-op stubs when `CONFIG_MEMCG_V1` is disabled.

## Important APIs, types, and functions

The common iteration macros are `for_each_mem_cgroup_tree(iter, root)` and `for_each_mem_cgroup(iter)`, both built on `mem_cgroup_iter()` and requiring `mem_cgroup_iter_break()` if the loop exits early. Common declarations include `drain_all_stock()`, `memcg_events()`, `memory_stat_show()`, and `mem_cgroup_private_id_get_online()`.

When `CONFIG_MEMCG_V1` is enabled, `do_memsw_account()` reports whether legacy memory+swap accounting is active by checking that the memory controller is not on the default hierarchy. The header declares v1 local stat/event readers, per-memcg event allocation, v1 memcg initialization/offline cleanup, soft-limit reset/removal, OOM prepare/finish/recover hooks, charge and uncharge hooks, stats formatting and reparenting helpers, kmem/tcp accounting helpers, and the `memsw_files[]` and `mem_cgroup_legacy_files[]` cftype arrays.

The `enum res_type` values `_MEM`, `_MEMSWAP`, `_KMEM`, and `_TCP` are used by cgroup-v1 file handlers to encode resource selection into `cftype.private`. Inline helpers include `memcg1_soft_limit_reset()`, `memcg1_tcpmem_active()`, and `memcg1_uncharge_skmem()` in v1 builds.

When `CONFIG_MEMCG_V1` is disabled, the header supplies static inline fallbacks that return success/false or do nothing: legacy memsw accounting is false, events allocation succeeds without allocation, v1 init/offline/OOM/charge/stat/kmem/tcp hooks are inert, and socket memory charges always succeed. This lets shared memcg code call v1 hooks without spreading preprocessor conditionals.

## Control flow

Shared memcg code includes this header and calls the declared hooks at lifecycle, charge, uncharge, swap, OOM, and stats points. In v1-enabled builds the calls resolve to `memcontrol-v1.c` behavior; in v1-disabled builds the compiler inlines the stubs and removes legacy behavior. `do_memsw_account()` is the runtime gate for legacy memory+swap accounting even when v1 support is compiled in, allowing the same kernel to distinguish default-hierarchy operation from legacy hierarchy operation.

The iteration macros start at `mem_cgroup_iter(root, NULL, NULL)` and feed each previous result back into `mem_cgroup_iter()`. The comment makes reference handling part of the contract: callers that break early must call `mem_cgroup_iter_break()` to release iterator references.

## State and persistence behavior

The header owns no standalone storage except inline effects on `struct mem_cgroup` fields. `memcg1_soft_limit_reset()` writes `PAGE_COUNTER_MAX` to `memcg->soft_limit`; `memcg1_tcpmem_active()` reads `memcg->tcpmem_active`; and `memcg1_uncharge_skmem()` decrements `memcg->tcpmem`. All persistent runtime state is stored in `struct mem_cgroup`, page counters, or implementation globals declared in the C file.

## Dependencies and integration points

The header depends on `linux/cgroup-defs.h` for cgroup subsystem declarations and on types supplied by surrounding memcg headers, including `struct mem_cgroup`, `struct folio`, `struct seq_file`, `struct seq_buf`, `struct cftype`, `gfp_t`, and page-counter primitives. It is an integration boundary between shared memcg code, cgroup core file registration, swap accounting, OOM handling, kernel memory accounting, TCP socket memory accounting, and cgroup-v1-only control files.

## Risks

The main risk is semantic drift between stubs and real v1 implementations. Stubs must preserve shared-code assumptions when v1 is disabled; for example, allocation hooks return success, OOM prepare returns true, and socket charges succeed so non-v1 builds do not fail legacy-only paths. `do_memsw_account()` must match cgroup hierarchy semantics or memory+swap accounting can be enabled in the wrong mode. The iteration macros can leak references if callers break without `mem_cgroup_iter_break()`.

The header also exposes `enum res_type` values used for `cftype.private` encoding in `memcontrol-v1.c`; adding or reordering values without updating file handlers would misroute reads and writes. Inline writes to memcg fields rely on the same concurrency expectations as the implementation file, including `WRITE_ONCE()` for soft-limit reset and page-counter operations for socket memory.

## Test signals

Build coverage should include `CONFIG_MEMCG_V1=y` and `CONFIG_MEMCG_V1=n`, with and without cgroup v2 as the default hierarchy. Runtime signals include successful registration of `mem_cgroup_legacy_files[]` and `memsw_files[]` in v1 mode, absence of those behaviors in non-v1 mode, correct memory+swap behavior gated by `do_memsw_account()`, and no link errors from shared memcg callers. Static analysis should flag early exits from `for_each_mem_cgroup*()` loops that omit `mem_cgroup_iter_break()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memcontrol-v1.h -->
