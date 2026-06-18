# Group Research: group_894_linux_sources_os_linux_linux_mm_memblock_c_sources_os_linux_linux_mm_4956e2869b39

Scope: `Docs/research_subset_a.md`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memblock.c -->
# File Research: sources/os/linux/linux/mm/memblock.c

## Purpose

Implements Linux `memblock`, the early-boot physical memory region allocator and map manager used before the normal slab and buddy allocators are ready. It tracks usable memory, reserved allocations, and optionally the physical memory map through sorted region arrays.

This file owns the lifecycle from firmware-discovered physical ranges, through early boot reservations and allocations, to final release of free pages into the buddy allocator.

## Core State

The global `memblock` object contains:

- `memblock.memory`: usable physical memory ranges.
- `memblock.reserved`: allocated or otherwise reserved ranges.
- `memblock.current_limit`: upper bound for accessible early allocations.
- `memblock.bottom_up`: allocation direction policy.

Optional state includes:

- `physmem` under `CONFIG_HAVE_MEMBLOCK_PHYS_MAP`.
- `kho_scratch_only` under `CONFIG_MEMBLOCK_KHO_SCRATCH`.
- `system_has_some_mirror` for mirrored-memory preference.
- `memblock_can_resize`, plus slab-origin flags for dynamically grown region arrays.
- `memblock_memory`, a retained pointer used by iterators and nulled by `memblock_discard()` when memblock is not kept after init.

Initial static region arrays are sized by `INIT_MEMBLOCK_MEMORY_REGIONS`, `INIT_MEMBLOCK_RESERVED_REGIONS`, and `INIT_PHYSMEM_REGIONS`.

## Region Model

Each `struct memblock_region` has a base, size, flags, and NUMA node id. The region arrays are maintained as sorted, non-overlapping, minimal ranges where neighboring compatible entries are merged.

Important internal operations:

- `memblock_cap_size()` prevents physical address overflow.
- `memblock_add_range()` adds a possibly overlapping range using a two-pass algorithm: first count needed splits, then insert and merge.
- `memblock_isolate_range()` splits boundary-crossing regions so a target interval can be modified exactly.
- `memblock_remove_range()` isolates and removes a range.
- `memblock_merge_regions()` coalesces adjacent regions with matching node and flags.
- `memblock_double_array()` grows region arrays, using slab if available or memblock allocation otherwise, and reserves the new backing storage when needed.

The file uses `BUG_ON()` and `WARN_ON()` heavily to enforce invariants such as sorted ordering, compatible merge boundaries, and array capacity.

## Public Memory Map APIs

The main map mutation APIs are:

- `memblock_add_node()`: add memory with an explicit NUMA node.
- `memblock_add()`: add memory without a NUMA node.
- `memblock_remove()`: remove memory from the memory map.
- `__memblock_reserve()`: add a reserved range with node and flags.
- `memblock_physmem_add()`: add to optional `physmem`.
- `memblock_set_node()`: assign NUMA node ids to isolated ranges.

Query APIs include:

- `memblock_is_reserved()`
- `memblock_is_memory()`
- `memblock_is_map_memory()`
- `memblock_is_region_memory()`
- `memblock_is_region_reserved()`
- `memblock_search_pfn_nid()`
- `memblock_start_of_DRAM()`
- `memblock_end_of_DRAM()`
- `memblock_phys_mem_size()`
- `memblock_reserved_size()`
- `memblock_reserved_kern_size()`
- `memblock_estimated_nr_free_pages()`

## Allocation Flow

Allocation is based on intersections between `memory` and the inverse of `reserved`.

Key functions:

- `__memblock_find_range_bottom_up()`
- `__memblock_find_range_top_down()`
- `memblock_find_in_range_node()`
- `memblock_alloc_range_nid()`
- `memblock_phys_alloc_range()`
- `memblock_phys_alloc_try_nid()`
- `memblock_alloc_internal()`
- `memblock_alloc_exact_nid_raw()`
- `memblock_alloc_try_nid_raw()`
- `memblock_alloc_try_nid()`
- `__memblock_alloc_or_panic()`

`memblock_alloc_range_nid()` is the central allocator. It chooses memory flags, finds a suitable free range, reserves it as `MEMBLOCK_RSRV_KERN`, records kmemleak metadata unless disabled with `MEMBLOCK_ALLOC_NOLEAKTRACE`, and calls `accept_memory()` for platforms that require guest memory acceptance.

Fallback behavior includes:

- retrying non-exact NUMA allocations on any node;
- retrying mirrored allocations on non-mirrored memory with a ratelimited warning;
- falling back below `min_addr` in the virtual-address allocation helpers;
- using `kzalloc_node()` if a memblock allocation API is accidentally called after slab availability.

## Flags and Filtering

The file manages memory and reserved flags through `memblock_setclr_flag()` after isolating the affected range.

Memory flags handled here include:

- `MEMBLOCK_HOTPLUG`
- `MEMBLOCK_MIRROR`
- `MEMBLOCK_NOMAP`
- `MEMBLOCK_DRIVER_MANAGED`
- `MEMBLOCK_KHO_SCRATCH`

Reserved flags handled here include:

- `MEMBLOCK_RSRV_NOINIT`
- `MEMBLOCK_RSRV_KERN`

`should_skip_region()` centralizes iterator filtering. It skips regions based on NUMA node, movable-node hotplug behavior, mirror-only allocation, `NOMAP`, driver-managed memory, and KHO scratch-only allocation mode.

## Iterators

This file implements the generic range iteration backends used by memblock macros:

- `__next_mem_range()`: forward iteration over `type_a` excluding `type_b`.
- `__next_mem_range_rev()`: reverse iteration.
- `__next_mem_pfn_range()`: PFN range iteration for memory regions.

The iterator index packs two 32-bit cursors into a `u64`, allowing lockstep traversal of sorted included and excluded region arrays.

## Memory Limits and Trimming

Boot parameters and architecture setup can restrict available memory through:

- `memblock_enforce_memory_limit()`
- `memblock_cap_memory_range()`
- `memblock_mem_limit_remove_map()`
- `memblock_trim_memory()`
- `memblock_set_current_limit()`
- `memblock_get_current_limit()`

`__find_max_addr()` translates a byte limit over discontiguous memory ranges into a physical cutoff address.

## Reserved Memory Freeing

`free_reserved_area()` converts virtual addresses to physical addresses, optionally removes the range from `memblock.reserved` when memblock is kept, poisons pages when requested, and returns pages through `free_reserved_page()`.

`memblock_free()` and `memblock_phys_free()` release previous memblock allocations. If slab is available, physical free also releases pages to the buddy allocator via `__free_reserved_area()`.

## Transition to Buddy Allocator

`memblock_free_all()` performs the final early-memory handoff:

1. `free_unused_memmap()` releases unused portions of the `mem_map` array on applicable memory models.
2. `reset_all_zones_managed_pages()` clears zone managed page counters once.
3. `memblock_clear_kho_scratch_only()` disables scratch-only allocation mode.
4. `free_low_memory_core_early()` initializes reserved page metadata and frees non-reserved memory ranges.
5. `totalram_pages_add()` adds freed pages to global RAM accounting.

Reserved page initialization is handled by:

- `memmap_init_reserved_range()`
- `memmap_init_reserved_pages()`

These functions mark reserved and `NOMAP` pages as `PageReserved` and initialize deferred pages as needed.

## Named reserve_mem Support

The `reserve_mem=` setup parameter parses `reserve_mem=<size>:<align>:<name>` and allocates a named memblock reservation.

State is stored in a fixed `reserved_mem_table` with up to eight entries. Exported/runtime APIs include:

- `reserve_mem_find_by_name()`
- `reserve_mem_release_by_name()`

Access is protected by `reserve_mem_lock`.

Under `CONFIG_KEXEC_HANDOVER`, named reservations can be preserved and revived across kexec handover using an FDT subtree:

- `prepare_kho_fdt()`
- `reserved_mem_preserve()`
- `reserve_mem_kho_retrieve_fdt()`
- `reserve_mem_kho_revive()`
- `reserve_mem_init()`

## Debugging Interfaces

Boot-time debug is enabled by `memblock=debug` through `early_param()`.

Debug output includes:

- `memblock_dump()`
- `__memblock_dump_all()`
- `memblock_dump_all()`

Under `CONFIG_DEBUG_FS`, `memblock_init_debugfs()` creates `debugfs` entries for memblock arrays when `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled and for named `reserve_mem` entries when present.

## Integration Points

This file integrates with:

- architecture boot memory discovery and NUMA setup;
- kmemleak physical allocation tracking;
- KASAN tag reset during reserved-area poisoning;
- deferred struct page initialization;
- memory hotplug and movable-node policy;
- kexec handover preservation;
- debugfs reporting;
- the buddy allocator handoff path.

## Implementation Notes and Risks

The most important invariant is that region arrays remain sorted, non-overlapping, and merge-minimal. Allocation, reservation, flag mutation, NUMA assignment, and removal all depend on that property.

Most operations run during early boot and are not generally protected by global locks. The named reservation lookup/release path is an exception and uses a mutex because it can be queried after init.

Array resizing before all reserved ranges are known is dangerous; the file explicitly panics if resizing is attempted before `memblock_allow_resize()`.

`memblock_discard()` frees dynamic arrays and clears `memblock_memory` on configurations that do not keep memblock after init, so later code must not rely on discarded memblock metadata unless `CONFIG_ARCH_KEEP_MEMBLOCK` is enabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memcontrol-v1.c -->
# File Research: sources/os/linux/linux/mm/memcontrol-v1.c

## Purpose

Implements legacy cgroup v1 memory controller behavior that is no longer shared with the cgroup v2 memory controller. This includes soft limits, memory+swap accounting compatibility, threshold and OOM eventfd notifications, legacy cgroup files, force-empty support, per-memcg swappiness, kmem/tcp counters, and v1 statistics formatting.

## Major State

The file defines v1-specific state around:

- `soft_limit_tree`: per-NUMA-node RB-trees of cgroups exceeding soft limits.
- `memcg_oom_lock`: global spinlock for v1 OOM notification and OOM lock state.
- `memcg_oom_waitq`: waitqueue for userspace OOM handling.
- `memcg_max_mutex`: serializes updates to memory and memsw limits.
- `memcg1_events_percpu`: per-CPU page event counters and rate-limit targets.
- eventfd registration objects for cgroup v1 `cgroup.event_control`.

## Soft Limit Reclaim

Soft-limit tracking is built around `struct mem_cgroup_tree_per_node`, which stores an RB-tree and cached rightmost node for the largest soft-limit excess on each NUMA node.

Key functions:

- `soft_limit_excess()`: computes `memory.current - soft_limit`.
- `__mem_cgroup_insert_exceeded()`: inserts a per-node memcg entry by excess.
- `__mem_cgroup_remove_exceeded()`: removes an entry.
- `memcg1_update_tree()`: updates the soft-limit tree for a memcg and its ancestors.
- `memcg1_remove_from_trees()`: removes all per-node entries for a memcg.
- `memcg1_soft_limit_reclaim()`: selects over-limit cgroups and reclaims from them.

If multigenerational LRU is enabled, soft-limit tree reclaim is bypassed and `lru_gen_soft_reclaim()` is used from `memcg1_update_tree()`.

Soft-limit reclaim is best effort. It skips higher-order allocations, caps loops with `MEM_CGROUP_MAX_RECLAIM_LOOPS` and `MEM_CGROUP_MAX_SOFT_LIMIT_RECLAIM_LOOPS`, and tolerates races in tree state.

## Charge and Uncharge Events

`memcg1_commit_charge()` updates v1 event accounting on folio charge:

- counts `PGPGIN`;
- increments per-CPU page event counters;
- checks threshold and soft-limit events.

`memcg1_uncharge_batch()` does the corresponding batched page-out accounting and event checks.

Rate limiting is page-event based:

- threshold checks every `THRESHOLDS_EVENTS_TARGET` pages;
- soft-limit checks every `SOFTLIMIT_EVENTS_TARGET` pages.

On `CONFIG_PREEMPT_RT`, event checks are skipped for this v1 path.

## Swap and memsw Accounting

`do_memsw_account()` is true only on legacy hierarchy. This file provides v1-specific memory+swap lifetime handling:

- `memcg1_swapout()` transfers a folio's memsw charge to a swap entry, records the swap cgroup id, clears folio memcg data, adjusts memory/memsw counters, and updates page-out events.
- `memcg1_swapin()` removes duplicate swap-slot charge after a charged page enters swapcache.

The swapout path handles offlined memcgs by charging the closest online ancestor via `mem_cgroup_private_id_get_online()`.

## Threshold Notifications

Threshold notification support backs legacy eventfd monitoring of usage files.

Important functions:

- `mem_cgroup_usage()`: reads memory or memory+swap usage.
- `__mem_cgroup_threshold()`: detects crossed thresholds and signals eventfds.
- `mem_cgroup_threshold()`: applies threshold checks up the hierarchy.
- `__mem_cgroup_usage_register_event()`: parses threshold arguments, allocates and sorts threshold arrays, and publishes them through RCU.
- `__mem_cgroup_usage_unregister_event()`: rebuilds threshold arrays after eventfd removal.

Threshold arrays maintain a `current_threshold` index to avoid scanning the whole array unless usage crosses a boundary. Updates are protected by `thresholds_lock` and readers use RCU.

## cgroup.event_control Compatibility

The file implements the deprecated cgroup v1 `cgroup.event_control` ABI.

`memcg_write_event_control()` parses:

`<event_fd> <control_fd> <args>`

It resolves supported control files by name:

- `memory.usage_in_bytes`
- `memory.memsw.usage_in_bytes`
- `memory.oom_control`
- `memory.pressure_level`

It then installs callbacks in `struct mem_cgroup_event`, attaches to the eventfd poll waitqueue, and links the event into `memcg->event_list`.

Cleanup flow:

- `memcg_event_wake()` detects `EPOLLHUP`.
- `memcg_event_remove()` unregisters and frees from workqueue context.
- `memcg1_css_offline()` schedules removal of all remaining events on cgroup offline.

The comments explicitly mark this mechanism as deprecated and not for new files.

## OOM Handling

Legacy v1 supports OOM notifications and optional userspace OOM handling.

Key functions:

- `mem_cgroup_oom_notify()`: signals registered OOM eventfds for a subtree.
- `mem_cgroup_oom_trylock()`: marks a memcg subtree as OOM-locked.
- `mem_cgroup_oom_unlock()`: clears OOM locks.
- `mem_cgroup_mark_under_oom()` and `mem_cgroup_unmark_under_oom()`: maintain subtree `under_oom` counters.
- `memcg1_oom_prepare()`: prepares charge-path OOM handling.
- `memcg1_oom_finish()`: releases OOM lock state.
- `memcg1_oom_recover()`: wakes waiters after userspace or limit changes.
- `mem_cgroup_oom_synchronize()`: completes deferred userspace OOM handling at the end of a page fault.

If `oom_kill_disable` is set and the current task is in a user fault, the task stores `current->memcg_in_oom` and sleeps later, after page fault locks are released.

## Limit Updates and Force Empty

`mem_cgroup_resize_max()` updates memory or memsw maximums while preserving the invariant:

`memory.max <= memsw.max`

It drains per-CPU stocks once, attempts reclaim on failure, supports signal interruption, and wakes OOM waiters when limits are enlarged.

`mem_cgroup_force_empty()` drains LRU and stock state, then tries reclaim until the cgroup memory counter reaches zero or retries are exhausted. It backs the legacy `memory.force_empty` file and rejects root cgroup use.

## Legacy File Interface

The file defines `mem_cgroup_legacy_files[]`, the cgroup v1 memory files, including:

- `usage_in_bytes`
- `max_usage_in_bytes`
- `limit_in_bytes`
- `soft_limit_in_bytes`
- `failcnt`
- `stat`
- `force_empty`
- `use_hierarchy`
- `cgroup.event_control`
- `swappiness`
- `move_charge_at_immigrate`
- `oom_control`
- `pressure_level`
- `numa_stat` under `CONFIG_NUMA`
- `kmem.*`
- `kmem.tcp.*`
- `kmem.slabinfo` under `CONFIG_SLUB_DEBUG`

It also defines `memsw_files[]` for:

- `memsw.usage_in_bytes`
- `memsw.max_usage_in_bytes`
- `memsw.limit_in_bytes`
- `memsw.failcnt`

Handlers are dispatched through encoded `cftype.private` values using `MEMFILE_PRIVATE()`, `MEMFILE_TYPE()`, and `MEMFILE_ATTR()`.

Many writes emit deprecation warnings, including soft limits, non-hierarchical mode, move-charge-at-immigrate, `oom_control`, kmem limits, and TCP kmem limits.

## Statistics

`memcg1_stat_format()` emits cgroup v1 `memory.stat` content. It reports:

- local page states such as cache, rss, shmem, dirty, writeback, swap;
- local VM events such as pgpgin, pgpgout, pgfault, pgmajfault;
- local LRU sizes;
- hierarchical memory and memsw effective limits;
- hierarchical totals for the same states and events;
- optional debug VM reclaim cost information.

`reparent_memcg1_state_local()` and `reparent_memcg1_lruvec_state_local()` transfer local v1 stats during memcg reparenting.

Under `CONFIG_NUMA`, `memcg_numa_stat_show()` reports local and hierarchical per-node LRU totals.

## kmem and TCP Memory Accounting

`memcg1_account_kmem()` adjusts the legacy kmem page counter only when memory cgroup is not on the default hierarchy.

`memcg1_charge_skmem()` tries to charge TCP memory, sets `tcpmem_pressure` on failure, and honors `__GFP_NOFAIL` by force-charging.

`memcg_update_tcp_max()` updates the TCP max counter and enables the socket accounting static key before marking `tcpmem_active`.

## Initialization

`memcg1_alloc_events()` allocates per-CPU v1 event counters for a memcg, and `memcg1_free_events()` frees them.

`memcg1_memcg_init()` initializes per-memcg v1 lists and locks for OOM notifications, thresholds, and event registration.

`memcg1_init()` allocates one soft-limit RB-tree node per NUMA node and runs as a `subsys_initcall`.

## Integration Points

This file integrates with:

- `memcontrol.c` core memcg charge and reclaim paths;
- swap cgroup recording;
- page counters;
- VM reclaim and LRU vectors;
- eventfd and poll waitqueues;
- cgroup v1 kernfs file operations;
- vmpressure legacy notifications;
- per-node NUMA memory statistics;
- socket memory accounting static keys.

## Implementation Notes and Risks

This is compatibility-heavy code. Several exposed ABIs are deprecated but still must preserve userspace behavior.

The threshold notification path depends on careful RCU publication and spare-array swapping. The OOM event path depends on spinlock-protected subtree state and asynchronous workqueue cleanup to avoid sleeping from atomic context.

Soft-limit reclaim is explicitly best effort and race tolerant. It should not be treated as a strict enforcement mechanism.

Limit writes must maintain the memory/memsw invariant; violating it would break cgroup v1 memory+swap accounting semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memcontrol-v1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/memcontrol-v1.h -->
# File Research: sources/os/linux/linux/mm/memcontrol-v1.h

## Purpose

Declares the interface between generic memory cgroup code and the cgroup v1-specific implementation in `memcontrol-v1.c`. It also provides no-op stubs when `CONFIG_MEMCG_V1` is disabled, allowing shared memcg code to compile without scattering configuration checks.

## Common Declarations

The header defines iteration helpers used by both cgroup v1 and v2 paths:

- `for_each_mem_cgroup_tree(iter, root)`
- `for_each_mem_cgroup(iter)`

Both use `mem_cgroup_iter()` and require callers to use `mem_cgroup_iter_break()` if they exit early.

Common declarations include:

- `drain_all_stock()`
- `memcg_events()`
- `memory_stat_show()`
- `mem_cgroup_private_id_get_online()`

These are shared with the broader memcg implementation.

## CONFIG_MEMCG_V1 Interface

When cgroup v1 memory controller support is enabled, the header declares:

- `do_memsw_account()`: true on legacy hierarchy, false on cgroup v2 default hierarchy.
- event counter helpers: `memcg_events_local()`, `memcg_page_state_local()`, `memcg_page_state_local_output()`.
- allocation lifecycle: `memcg1_alloc_events()`, `memcg1_free_events()`, `memcg1_memcg_init()`.
- tree and lifecycle hooks: `memcg1_remove_from_trees()`, `memcg1_css_offline()`.
- soft-limit reset: `memcg1_soft_limit_reset()`.
- OOM hooks: `memcg1_oom_prepare()`, `memcg1_oom_finish()`, `memcg1_oom_recover()`.
- charge hooks: `memcg1_commit_charge()`, `memcg1_uncharge_batch()`.
- stats hooks: `memcg1_stat_format()`, `reparent_memcg1_state_local()`, `reparent_memcg1_lruvec_state_local()`.
- generic stat reparent helpers implemented elsewhere: `reparent_memcg_state_local()`, `reparent_memcg_lruvec_state_local()`.
- kmem and socket memory hooks: `memcg1_account_kmem()`, `memcg1_tcpmem_active()`, `memcg1_charge_skmem()`, `memcg1_uncharge_skmem()`.
- legacy cftype arrays: `memsw_files[]`, `mem_cgroup_legacy_files[]`.

It also defines `enum res_type` for encoding legacy control-file resource classes:

- `_MEM`
- `_MEMSWAP`
- `_KMEM`
- `_TCP`

## Disabled CONFIG_MEMCG_V1 Behavior

When `CONFIG_MEMCG_V1` is disabled, the header provides inline stubs:

- memsw accounting is always false;
- event allocation succeeds trivially;
- init, cleanup, soft-limit, OOM, charge, uncharge, stat, and kmem hooks become no-ops;
- socket memory charging always succeeds;
- TCP memory accounting is reported inactive.

This keeps callers simple while removing legacy behavior from builds that do not support it.

## Integration Notes

The header is included by shared memcg code and by `memcontrol-v1.c`. Its main role is to isolate legacy cgroup v1 behavior behind a compact API boundary.

The inline stubs are important because the rest of the memory controller can call `memcg1_*` hooks unconditionally without paying for cgroup v1 implementation when it is disabled.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/memcontrol-v1.h -->