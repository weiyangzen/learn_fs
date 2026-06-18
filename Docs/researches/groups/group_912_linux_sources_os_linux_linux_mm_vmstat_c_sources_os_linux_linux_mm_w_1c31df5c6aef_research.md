# Group Research: group_912_linux_sources_os_linux_linux_mm_vmstat_c_sources_os_linux_linux_mm_w_1c31df5c6aef

Scope: `Docs/research_subset_a.md`

Files researched completely:

- `sources/os/linux/linux/mm/vmstat.c`
- `sources/os/linux/linux/mm/workingset.c`
- `sources/os/linux/linux/mm/zpdesc.h`
- `sources/os/linux/linux/mm/zsmalloc.c`
- `sources/os/linux/linux/mm/zswap.c`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/vmstat.c -->
# File Research: sources/os/linux/linux/mm/vmstat.c

## Purpose

`vmstat.c` implements Linux VM statistics collection, folding, export, and diagnostic reporting. It owns global zone, node, NUMA, and VM event counter storage, provides fast per-CPU update paths, periodically folds per-CPU deltas into global counters, and exposes the counters through `/proc`, sysctls, and debugfs fragmentation reports.

The file is performance-sensitive because many memory-management paths update these counters in allocation, reclaim, migration, compaction, and swap flows. It trades exactness for low contention by accumulating small per-CPU signed deltas and folding them only when thresholds are exceeded or background workers run.

## Main Data And State

- `vm_zone_stat[]`, `vm_node_stat[]`, and `vm_numa_event[]` are global atomic counter arrays.
- `vm_event_states` is a per-CPU event counter array when `CONFIG_VM_EVENT_COUNTERS` is enabled.
- Per-zone `per_cpu_zonestats` and per-node `per_cpu_nodestats` hold local counter deltas and thresholds.
- NUMA statistics can be enabled or disabled with `vm.numa_stat`; disabling clears zone and global NUMA counters.
- `nr_memmap_boot_pages` and `nr_memmap_pages` count pages consumed by `struct page` and page extension metadata.
- Under SMP, per-CPU delayed work and the `shepherd` work item keep vmstat deltas folded without waking isolated CPUs unnecessarily.

## Counter Update Paths

The file exports zone and node counter modification APIs used across the mm subsystem:

- `__mod_zone_page_state()`, `__inc_zone_state()`, `__dec_zone_state()`
- `__mod_node_page_state()`, `__inc_node_state()`, `__dec_node_state()`
- `mod_zone_page_state()`, `inc_zone_page_state()`, `dec_zone_page_state()`
- `mod_node_page_state()`, `inc_node_page_state()`, `dec_node_page_state()`

On systems with `CONFIG_HAVE_CMPXCHG_LOCAL`, updates use `this_cpu_try_cmpxchg()` to avoid disabling interrupts. Other systems serialize with `local_irq_save()`. On PREEMPT_RT, the internal update path uses `preempt_disable_nested()` so per-CPU RMW sequences remain safe even when local locks do not fully disable preemption.

Node counters that are logically byte counters are stored as page counts in the compact per-CPU delta arrays, with validation that global updates arrive in page-sized multiples.

## Folding And Thresholds

`calculate_normal_threshold()` scales per-CPU batching thresholds by online CPU count and zone size, capped at 125. `calculate_pressure_threshold()` lowers thresholds when watermark drift could hide pressure. `refresh_zone_stat_thresholds()` installs thresholds and computes `percpu_drift_mark` where drift can threaten low/min watermarks.

`refresh_cpu_vm_stats()` drains current CPU zone and node diffs, updates per-zone and per-node atomics, accumulates global deltas, and optionally decays or drains per-CPU pagesets. On NUMA systems, remote per-CPU pagesets can expire and drain to reduce remote free-page hoarding. `cpu_vm_stats_fold()` handles CPU-offline folding.

`quiet_vmstat()` is the NOHZ-facing path: if a CPU is going idle and has pending deltas, it refreshes counters without canceling outstanding delayed work. `vmstat_shepherd()` periodically scans online CPUs with disabled or idle workers and queues needed flushes, skipping isolated CPUs to avoid disturbance.

## Reporting Interfaces

The file defines `vmstat_text[]`, the exported text names for zone, NUMA, node, global VM, and VM event counters. It includes counters for workingset, reclaim, compaction, huge pages, zswap, zsmalloc, NUMA balancing, swap, ballooning, KSM, TLB flushes, stack usage, and architecture-specific direct-map events based on Kconfig.

`/proc/vmstat` is implemented by `vmstat_op`: `vmstat_start()` snapshots global counters, folds NUMA events, computes dirty limits, adds memmap counters, and folds per-CPU VM events. `vmstat_show()` prints name/value pairs and appends deprecated `nr_unstable 0` for userspace compatibility.

Other proc entries:

- `/proc/buddyinfo` prints free block counts by order.
- `/proc/pagetypeinfo` prints free pages and pageblocks by migrate type, and page-owner mixed block counts when available.
- `/proc/zoneinfo` prints node, zone, watermarks, reserves, per-zone stats, NUMA event stats, pagesets, and highatomic information.

Sysctls:

- `vm.stat_interval` controls vmstat delayed-work cadence.
- `vm.stat_refresh` forces per-CPU stat refresh and warns on unexpected negative counters.
- `vm.numa_stat` toggles NUMA accounting and clears counters when disabled.

Debugfs compaction entries under `extfrag/` expose unusable-free-space and external-fragmentation indexes.

## Fragmentation Helpers

With `CONFIG_COMPACTION`, `fill_contig_page_info()`, `fragmentation_index()`, and `extfrag_for_order()` derive diagnostic views of free memory layout by walking each zone's free areas. These are not migration predictors; they intentionally avoid expensive estimates of movable-page compaction potential.

## Integration Points

This file is central infrastructure for allocator, reclaim, compaction, zsmalloc, zswap, workingset, memcg, NUMA balancing, and procfs/debugfs observability. `init_mm_internals()` creates `mm_percpu_wq`, registers CPU hotplug callbacks, starts the shepherd timer, creates proc entries, and registers the sysctl table. `init_mm_internals()` is therefore a key mm bootstrap hook.

## Concurrency And Invariants

- Fast counter updates must preserve per-CPU atomicity while minimizing IRQ/preemption cost.
- Global counters are approximate and can transiently lag or be clamped for readers.
- Zone and node stat thresholds bound drift; pressure thresholds are tightened near watermarks.
- `vmstat_refresh()` deliberately warns on negative counters except for known transiently negative stats.
- Proc/debugfs walkers hold zone locks where needed, but some diagnostic reads use `data_race()` because the values are informational.
- CPU hotplug folding must run after worker disable and before offline CPU state disappears.

## Risks And Test Focus

Important risks are off-by-one enum/text table mismatches, counter drift hiding watermarks, negative counter regressions, isolated-CPU interference, and locking mistakes in diagnostic walkers. Validation should cover `/proc/vmstat` name count consistency, CPU hotplug folding, NUMA stat toggling, `stat_refresh` warnings, high CPU count threshold behavior, and fragmentation output under compaction-enabled builds.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/vmstat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/workingset.c -->
# File Research: sources/os/linux/linux/mm/workingset.c

## Purpose

`workingset.c` implements Linux workingset detection for page cache and anonymous memory refaults. It records eviction timestamps in xarray shadow entries, compares later refault distance against active/inactive memory dimensions, and decides whether a refaulting folio should be activated or restored as part of the working set. It also maintains and shrinks shadow-entry xarray nodes to prevent unbounded metadata growth.

The core idea is that the distance between eviction and refault approximates how much inactive-list space the page would have needed to remain resident. If that distance fits within the current workingset, activation is worthwhile.

## Shadow Entry Encoding

Shadow entries are xarray value entries produced by `pack_shadow()` and decoded by `unpack_shadow()`. They store:

- memcg private ID
- NUMA node ID
- eviction timestamp or multigenerational LRU token
- whether the evicted folio had `workingset` state

Bit allocation is constrained by `BITS_PER_XA_VALUE`, `NODES_SHIFT`, and `MEM_CGROUP_ID_SHIFT`. `bucket_order[WORKINGSET_FILE]` and `bucket_order[WORKINGSET_ANON]` reduce timestamp granularity when physical memory is larger than the available timestamp range.

## Classic LRU Workingset Flow

`workingset_eviction()` is called for a locked, fully exclusive folio being evicted. It reads the reclaiming lruvec's `nonresident_age`, buckets the value, ages the nonresident counter by the folio size, and returns a packed shadow entry.

`workingset_test_recent()` decodes a shadow entry, resolves the memcg and node lruvec, computes `refault_distance = refault_age - eviction_age` with masked unsigned arithmetic, and compares that distance with the relevant active and inactive list sizes. File and anon refaults use slightly different comparisons, and anon/file competition depends on available swap. It can flush memcg stats unless called from a context that cannot sleep.

`workingset_refault()` handles a newly allocated locked folio and a matching shadow entry. It records refault stats, tests recency, activates the folio if appropriate, ages nonresident state, and restores `workingset` state plus refault cost if the evicted folio had been active.

`workingset_activation()` advances nonresident age on folio activation, including ancestor lruvecs, so nonresident and resident LRU ages remain comparable.

## Multigenerational LRU Integration

When `CONFIG_LRU_GEN` is enabled:

- `lru_gen_eviction()` records generation sequence and reference tier in the shadow token and updates generation eviction histograms.
- `lru_gen_test_recent()` treats a token as recent if its generation sequence is within `MAX_NR_GENS`.
- `lru_gen_refault()` updates refault histograms, activation stats, and either restores workingset state or reference bits for the refaulting folio.

When multigenerational LRU is disabled, those helpers compile to stubs and the classic nonresident-age distance algorithm is used.

## Shadow Node Reclaim

Shadow entries occupy xarray nodes after folios are evicted. `workingset_update_node()` maintains the global `shadow_nodes` `list_lru`: a node is listed when all entries are values and no real folios remain. It increments or decrements `WORKINGSET_NODES`.

`count_shadow_nodes()` computes reclaimable shadow-node pressure. It caps shadow metadata based on either memcg lruvec size plus slab or node present pages, using a worst-case density compromise so shadow nodes do not consume excessive memory for streaming workloads.

`shadow_lru_isolate()` reclaims one shadow-only xarray node. It inverts lock order carefully by first holding the list_lru lock, then trylocking `mapping->i_pages`, and for page cache mappings also trylocking the inode lock. It validates that the node contains only values, deletes the node with `xa_delete_node()`, records `WORKINGSET_NODERECLAIM`, and requeues shrinkable inodes as needed.

`scan_shadow_nodes()` wires this into `list_lru_shrink_walk_irq()`.

## Initialization

`workingset_init()` computes timestamp bucket orders, logs the resulting bit budget, allocates a NUMA-aware and memcg-aware shrinker named `mm-shadow`, initializes `shadow_nodes` with a lock class key, assigns count and scan callbacks, and registers the shrinker.

## Integration Points

This file is used by reclaim, page cache, swap, memcg, xarray, list_lru, and lruvec statistics. Its counters are reported through vmstat names such as `workingset_refault_*`, `workingset_activate_*`, `workingset_restore_*`, `workingset_nodes`, and `workingset_nodereclaim`.

## Concurrency And Invariants

- Eviction folios must be locked, refcount-free, and off LRU when shadow entries are created.
- Refault folios must be locked so memcg ownership is stable.
- Deleted memcgs can make a shadow entry unusable; recycled IDs are tolerated as rare speculative noise.
- Shadow-node list updates require the xarray lock.
- Shadow-node reclaim relies on lock try-acquisition and retry status to avoid deadlocks with page cache and inode locking.

## Risks And Test Focus

Risks include shadow bitfield overflow, timestamp bucket miscalculation on large memory systems, incorrect memcg ref handling, stale shadow entries causing false activations, and xarray/list_lru locking regressions. Tests should stress memcg deletion/reuse, swap availability differences, file versus anon refaults, `CONFIG_LRU_GEN` and non-LRU_GEN builds, shadow-node shrinker pressure, and concurrent page-cache insertion/deletion.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/workingset.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/zpdesc.h -->
# File Research: sources/os/linux/linux/mm/zpdesc.h

## Purpose

`zpdesc.h` defines `struct zpdesc`, the zsmalloc-specific descriptor overlay for pages that back zsmalloc pool memory. It is a transitional abstraction over `struct page`/`struct folio` fields used by zsmalloc while letting zsmalloc code express its own metadata model directly.

## Data Layout

`struct zpdesc` overlays selected `struct page` fields and must not grow beyond `struct page`. Static assertions verify field offsets:

- `flags` overlays page flags.
- `lru` is indirectly used by page migration.
- `movable_ops` overlays `mapping` for movable-page operations.
- `next` and `handle` overlay `__folio_index`; `next` links component pages in normal zspages, while `handle` stores the allocation handle for huge zspages.
- `zspage` overlays `private` and points to the owning zspage metadata.
- `first_obj_offset` overlays `page_type`; lower 24 bits hold the first object offset and upper bits reserve the zsmalloc page type.
- `_refcount` overlays the page reference count.

Documented page flags:

- `PG_private` identifies the first component page of a zspage.
- `PG_locked` is used by page migration.

## Conversion Helpers

The header provides type-generic conversion helpers:

- `zpdesc_page()` converts a zpdesc to the first underlying `struct page`.
- `zpdesc_folio()` converts to the backing folio.
- `page_zpdesc()` converts a known head or order-0 page into a zpdesc.
- `pfn_zpdesc()` and `zpdesc_pfn()` bridge PFNs and descriptors.

The conversion macros are explicit because the representation may change as zsmalloc continues moving away from raw `struct page` assumptions.

## Operations

Inline wrappers expose folio/page operations in zpdesc terms:

- Locking: `zpdesc_lock()`, `zpdesc_trylock()`, `zpdesc_unlock()`, `zpdesc_wait_locked()`, `zpdesc_is_locked()`
- Lifetime: `zpdesc_get()`, `zpdesc_put()`
- Mapping: `kmap_local_zpdesc()`
- Page type and migration setup: `__zpdesc_set_movable()`, `__zpdesc_set_zsmalloc()`
- Zone lookup: `zpdesc_zone()`

## Integration Points

`zsmalloc.c` uses this header for all zspage component-page operations: allocation, free, chain construction, object copy, migration, compaction, page-state accounting, and highmem mapping. The header also interfaces with generic migration through `SetPageMovableOps()` and with zsmalloc page typing through `__SetPageZsmalloc()`.

## Invariants And Risks

The central invariant is that `struct zpdesc` must exactly match the `struct page` fields zsmalloc overlays. Changing `struct page`, folio internals, or zsmalloc metadata without updating these static assertions can corrupt unrelated page metadata. The 24-bit `first_obj_offset` field limits direct offset representation to pages up to 16 MiB. Callers must use helpers rather than accessing overlay fields through casts or direct `struct page` internals.

Test focus should include build-time assertions across architecture page models, zsmalloc allocation/free, page migration, highmem mapping, and large `PAGE_SIZE` configurations.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/zpdesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/zsmalloc.c -->
# File Research: sources/os/linux/linux/mm/zsmalloc.c

## Purpose

`zsmalloc.c` implements the zsmalloc allocator, a compact allocator for compressed objects that are typically smaller than a page and may span page boundaries. It is used by zswap and zram-like compressed-memory users. The allocator groups physical pages into zspages, divides each zspage into fixed-size chunks by size class, tracks fullness for allocation and compaction, and supports page migration through movable operations.

## Core Data Structures

- `struct zs_pool` is a named allocator pool with size-class table, allocated-page count, compaction stats, shrinker, optional debugfs stats, deferred free work, pool migration lock, and compaction-in-progress guard.
- `struct size_class` owns one allocation size, zspage geometry, fullness lists, a spinlock, and class stats.
- `struct zspage` describes a chain of one or more `zpdesc` pages: class index, fullness group, in-use count, free-object head, first descriptor, pool pointer, list node, and custom read/write lock.
- `struct link_free` is embedded in free chunks and stores either the next free object index or the allocated object's handle.

Handles point to separately allocated `zs_handle` objects. The handle stores an encoded object location composed of PFN and object index. Allocated chunk headers store the handle with `OBJ_ALLOCATED_TAG`; huge single-object zspages store the handle in the first zpdesc.

## Size Classes And Fullness

Objects are aligned to `ZS_ALIGN`, include `ZS_HANDLE_SIZE` overhead, and are capped at `ZS_MAX_ALLOC_SIZE == PAGE_SIZE`. Size classes are derived from `ZS_MIN_ALLOC_SIZE`, `ZS_SIZE_CLASS_DELTA`, and `CLASS_BITS`. During pool creation, adjacent logical classes can share one `size_class` if they have the same `pages_per_zspage` and `objs_per_zspage`, reducing metadata.

Fullness groups range from empty to 10 percent bands through 99 percent and 100 percent. Allocation searches high-utilization groups first via `find_get_zspage()`, while compaction chooses sparse source pages and dense destination pages.

## Allocation And Free

`zs_malloc()` validates size, allocates a handle, finds the size class, and tries to allocate from an existing zspage. If none is available, it allocates a new zspage, initializes its free list, inserts it into the correct fullness group, marks pages movable when compaction is enabled, updates stats, and returns the handle.

`obj_malloc()` removes the first free object from the zspage free list, writes the tagged handle into the object header or huge-page descriptor, records the encoded object location in the handle, and increments `zspage->inuse`.

`zs_free()` resolves the handle to a zspage under `pool->lock`, locks the class, clears the object back to the free list with `obj_free()`, updates fullness and stats, and frees the whole zspage if it becomes empty. `free_zspage()` tries to lock all component pages; if it cannot do so from the non-sleepable free path, it schedules deferred free work.

## Object Access APIs

The exported access APIs are:

- `zs_obj_read_begin()` / `zs_obj_read_end()`
- `zs_obj_read_sg_begin()` / `zs_obj_read_sg_end()`
- `zs_obj_write()`

They resolve the handle under the pool read lock, acquire a zspage read lock to prevent migration, then map or copy the object. Objects fully contained in one page can be accessed by local kmap or a single scatterlist entry; cross-page objects are copied through a caller-provided buffer or represented as a two-entry scatterlist.

## Compaction And Migration

`zs_compact()` serializes pool compaction with `compaction_in_progress`, iterates size classes, and calls `__zs_compact()`. Compaction isolates a dense destination zspage and sparse source zspages, write-locks source zspages, migrates allocated objects with `migrate_zspage()`, frees empty source zspages, and periodically drops locks if the pool lock is contended.

`migrate_zspage()` finds allocated objects, allocates corresponding slots in the destination, copies object bytes with `zs_object_copy()`, updates handles to point at new object locations, and frees old object slots.

With `CONFIG_COMPACTION`, zsmalloc registers `zsmalloc_mops`:

- `zs_page_isolate()` accepts only still-live zsmalloc pages.
- `zs_page_migrate()` copies an individual physical page to a new page, updates every allocated handle on that subpage, replaces the subpage in the zspage chain, transfers zsmalloc/movable metadata, adjusts `NR_ZSPAGES` zone stats if the zone changes, and clears the old descriptor.
- `zs_page_putback()` is a no-op.

The custom `zspage_lock` allows sleeping readers and atomic trylock writers. This protects object access from migration while avoiding non-preemptible long read sections during compression or decompression users.

## Shrinker, Stats, And Lifecycle

`zs_register_shrinker()` installs a shrinker that estimates compactable pages with `zs_can_compact()` and frees pages through `zs_compact()`. Optional `CONFIG_ZSMALLOC_STAT` debugfs output exposes per-class fullness, allocation, usage, pages, and freeable counts under `zsmalloc/<pool>/classes`.

`zs_create_pool()` allocates the pool, builds size classes, initializes fullness lists, creates debugfs stats, and registers the shrinker. `zs_destroy_pool()` unregisters the shrinker, flushes deferred migration/free work, destroys debugfs stats, warns if fullness lists are not empty, and frees classes and pool metadata. Module init creates handle and zspage caches and registers movable page operations; exit undoes those registrations.

## Integration Points

The allocator exports pool creation/destruction, allocation/free, object read/write, compaction, total page count, huge-class size, size-class lookup, and stats. `zswap.c` uses zsmalloc pools for compressed page storage, and `vmstat.c` exposes `NR_ZSPAGES` when zsmalloc is enabled.

## Concurrency And Invariants

- Lock order is page lock, pool lock, class lock, zspage lock.
- `class->lock` protects fullness lists, class stats, and object allocation/free in a zspage.
- `pool->lock` protects races between handle resolution, migration, and free.
- Empty zspages can only be destroyed when all component pages are locked.
- Handles must be updated before old object storage is freed during compaction or page migration.
- `PageZsmalloc` remains sticky until the page returns to the buddy allocator.

## Risks And Test Focus

Risks include handle/object encoding overflow on unusual memory models, cross-page copy bugs, fullness-list stat drift, migration races with readers, deferred free leaks, and pool destruction with live objects. Tests should stress highmem, cross-page object sizes, huge classes, compaction under concurrent allocation/free/read/write, memory hotplug or page migration, shrinker invocation, and debugfs stat consistency.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/zsmalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/mm/zswap.c -->
# File Research: sources/os/linux/linux/mm/zswap.c

## Purpose

`zswap.c` implements zswap, a compressed RAM cache for swap pages. When a folio is being swapped out, zswap can compress each page and store it in a zsmalloc pool instead of immediately writing it to the swap device. On swapin, zswap decompresses the page from RAM. Under pressure or pool limits, it writes cold entries back to the real swap device.

## Tunables And Global State

Module parameters control:

- `enabled`
- `compressor`
- `max_pool_percent`
- `accept_threshold_percent`
- `shrinker_enabled`

`zswap_ever_enabled` is a static key used to avoid work when zswap was never active. `zswap_enabled` is the runtime gate. `zswap_init_state`, `zswap_init_lock`, and `zswap_has_pool` coordinate setup and parameter changes.

Statistics include stored pages, stored incompressible pages, pool limit hits, writebacks, reclaim failures, compression failures, poor compression, decompression failures, allocator failures, and metadata allocation failures. VM events `ZSWPIN`, `ZSWPOUT`, and `ZSWPWB` are counted on load, store, and writeback.

## Pools And Compression Contexts

`struct zswap_pool` combines:

- a zsmalloc `zs_pool`
- per-CPU async-compression contexts
- a percpu refcount
- RCU list membership
- deferred release work
- selected compressor name

Pool creation initializes zsmalloc, allocates per-CPU crypto contexts, registers CPU hotplug preparation callbacks, and initializes a percpu ref. Compressor parameter changes can create a new current pool, reuse an old matching pool by resurrecting its percpu ref, and retire the previous current pool by killing its ref. Empty retired pools are removed from the RCU list and destroyed after `synchronize_rcu()`.

Each CPU's `crypto_acomp_ctx` owns an acomp transform, request, wait object, temporary buffer, and mutex. `zswap_cpu_comp_prepare()` allocates these per pool and CPU.

## Entry Indexing And LRU

Each compressed page is tracked by `struct zswap_entry`:

- swap entry and xarray offset
- compressed length
- `referenced` second-chance bit
- pool pointer and zsmalloc handle
- objcg charge owner
- LRU list node

For each swap type, `zswap_swapon()` allocates an array of xarrays, one per 64M swap-space page range. `swap_zswap_tree()` maps a swap entry to the proper xarray. `zswap_swapoff()` verifies entries are gone and frees the xarray array.

`zswap_list_lru` is a global NUMA-aware, memcg-aware LRU for writeback candidates. Entries are added and deleted using memcg-aware list_lru helpers under RCU to tolerate memcg offlining.

## Store Path

`zswap_store()` requires a locked swapcache folio. It checks runtime enablement, objcg zswap allowance, pool limits, current pool availability, and memcg list_lru allocation. It then stores each base page in the folio using `zswap_store_page()`.

`zswap_store_page()` allocates entry metadata, compresses and stores the page, inserts the entry into the swap xarray, frees any stale old entry, grabs pool and objcg references, charges zswap memory, initializes entry fields, and adds the entry to the LRU.

`zswap_compress()` uses the current CPU's acomp context to compress into a per-CPU buffer. If compression fails, produces zero length, or does not shrink below `PAGE_SIZE`, zswap either rejects the page when memcg zswap writeback is disabled or stores the original page uncompressed with `length == PAGE_SIZE` so LRU writeback order is preserved. Compressed or uncompressed bytes are allocated in zsmalloc with NOWAIT/NORETRY/MOVABLE flags and written with `zs_obj_write()`.

If store fails or zswap is disabled, `zswap_store()` invalidates stale zswap entries for all page offsets covered by the folio so later writeback cannot overwrite newer swapfile data.

## Load And Invalidation

`zswap_load()` looks up the entry for a locked swapcache folio. Large folios are rejected because zswap may only have partial per-page entries. On success it decompresses into the folio, marks it uptodate and dirty, counts `ZSWPIN`, erases the entry from the xarray, frees zswap storage, and unlocks the folio. Missing entries return `-ENOENT` with the folio still locked.

`zswap_invalidate()` erases and frees a single entry, used when swap slots are invalidated.

`zswap_decompress()` reads the zsmalloc object as a one- or two-entry scatterlist. Uncompressed `PAGE_SIZE` entries are copied directly; compressed entries go through acomp decompression. It validates the output length and records decompression failures.

## Writeback And Shrinking

`zswap_writeback_entry()` resumes swap writeback for one compressed entry. It pins the swap device, allocates or finds a swapcache folio, skips if swapin or another shrinker already populated it, validates that the xarray still points to the same entry, decompresses into the folio, erases and frees the zswap entry, marks the folio uptodate and reclaim, and calls `__swap_writepage()`.

The shrinker uses three controls:

- A second-chance `referenced` bit, cleared on first scan and written back on later scan.
- Per-lruvec disk swapin counters to detect overshrinking and reduce reclaimable estimates.
- Compression ratio scaling, so highly compressed memory is less aggressively written back.

`zswap_shrinker_count()` computes reclaimable entries from list_lru count, memcg or global zswap backing size, stored pages, disk swapins, and compression savings. It refuses to run without IO/FS permission. `zswap_shrinker_scan()` walks the LRU and calls `shrink_memcg_cb()`.

When the pool limit is reached, `zswap_check_limits()` sets `zswap_pool_reached_full`; failed stores can queue `zswap_shrink_work`. `shrink_worker()` round-robins online memcgs with zswap writeback enabled and writes entries back until the accept threshold is reached or retry limits are hit. `zswap_memcg_offline_cleanup()` advances the shrink cursor if a memcg is being offlined.

## Debugfs And Initialization

With debugfs, `zswap_debugfs_init()` creates `zswap/` counters for rejection, decompression, writeback, total pool size, stored pages, and stored incompressible pages.

`zswap_setup()` creates the entry cache, registers CPU hotplug multi-state for compression context setup, creates the shrink workqueue, allocates and registers the shrinker, initializes the memcg-aware list_lru, creates the fallback/current pool, enables the static key if a pool exists, initializes debugfs, and marks setup successful. `zswap_init()` is a late initcall so crypto algorithms are available.

## Integration Points

`zswap.c` integrates swapcache, swap devices, zsmalloc, crypto acomp, memcg/objcg charging, list_lru, shrinkers, CPU hotplug, debugfs, vm events, and folio state. It depends on zsmalloc object APIs and contributes zswap event names through `vmstat.c`.

## Concurrency And Invariants

- Store and invalidation are serialized by the folio lock for a swap slot.
- Writeback drops LRU locks before IO but validates the xarray still contains the same entry before dereferencing.
- Pool list traversal is RCU protected; pool lifetime is guarded by percpu refs.
- Entry publication order matters: an entry enters the xarray before it is added to the LRU, so writeback cannot see partially initialized LRU entries.
- Large folio load is rejected because per-page zswap entries do not represent a whole large folio coherently.
- Memcg offlining must not leave `zswap_next_shrink` holding a stale reference.

## Risks And Test Focus

Risks include stale entry writeback overwriting newer swap data, compressor parameter races, per-CPU crypto hotplug failures, objcg charge leaks, memcg offline shrink cursor bugs, uncompressed-entry accounting drift, and large-folio partial-store hazards. Tests should cover store/load/invalidate, stale replacement, swapoff cleanup, writeback races with swapin, pool limit shrink work, compressor switching, memcg writeback disabled behavior, CPU hotplug, and debugfs/stat counter sanity.
<!-- END FILE RESEARCH: sources/os/linux/linux/mm/zswap.c -->