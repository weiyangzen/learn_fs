# Group Research: group_1440_openzfs_sources_cow_pools_openzfs_module_zfs_metaslab_c_sources_cow_1fd086bfd6a0

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/metaslab.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/metaslab.c

## Scope

Core OpenZFS metaslab allocator implementation. This file manages metaslab classes, metaslab groups, per-metaslab range trees, allocator policies, space-map loading/unloading, weight and fragmentation scoring, log spacemap flushing, condensing, allocation/free/claim entry points, checkpoint accounting, vdev removal remapping, allocation throttling, tracing, and module tunables.

## Main Interfaces

- Stats/lifecycle: `metaslab_stat_init()`, `metaslab_stat_fini()`.
- Class management: `metaslab_class_create()`, `metaslab_class_destroy()`, `metaslab_class_balance()`, `metaslab_class_fragmentation()`, `metaslab_class_expandable_space()`, class alloc/deferred/space accessors, throttle reserve/unreserve.
- Group management: `metaslab_group_create()`, `metaslab_group_destroy()`, `metaslab_group_activate()`, `metaslab_group_passivate()`, `metaslab_group_initialized()`, `metaslab_group_get_space()`, `metaslab_group_fragmentation()`, `metaslab_sync_reassess()`.
- Metaslab lifecycle: `metaslab_init()`, `metaslab_fini()`, `metaslab_load()`, `metaslab_unload()`, `metaslab_sync()`, `metaslab_sync_done()`, `metaslab_flush()`.
- Allocation policies: dynamic-fit `metaslab_df_alloc()`, cursor-fit `metaslab_cf_alloc()`, disabled new-dynamic `metaslab_ndf_alloc()`, selected by `spa_set_allocator()` / `metaslab_allocator()`.
- Public block operations: `metaslab_alloc()`, `metaslab_alloc_range()`, `metaslab_alloc_dva()`, `metaslab_free()`, `metaslab_free_dva()`, `metaslab_unalloc_dva()`, `metaslab_claim()`, `metaslab_claim_impl()`, `metaslab_check_free()`.
- Vdev removal/remap: `spa_remap_blkptr()`, `metaslab_free_impl()` and remap callbacks.
- Disable/enable for initialize/TRIM: `metaslab_disable()`, `metaslab_enable()`.
- Log-spacemap metadata: `metaslab_unflushed_bump()`, `metaslab_set_unflushed_txg()`, `metaslab_unflushed_txg()`, `metaslab_unflushed_dirty()`.

## State And Control Flow

A `metaslab_class_t` owns allocation rotors, per-allocator queues, class-wide histograms, aggregate space counters, and the allocation policy. A `metaslab_group_t` represents one top-level vdev within a class, tracks activation state, allocation eligibility, histograms, disabled metaslab counts, and per-allocator active primary/secondary metaslabs. Each `metaslab_t` owns its spacemap, allocation/deferred/freeing/checkpoint/trim range trees, unflushed log-spacemap deltas, weight/fragmentation/cache fields, selected-txg list node, and load/flush/condense synchronization.

Allocation starts at a class rotor, chooses a metaslab group while respecting allocatable state, health, no-free-space, fragmentation, hints, gang/ditto placement, and try-hard mode, then chooses or activates a metaslab from the group AVL sorted by weight. Active metaslabs are marked primary, secondary, or claim. `metaslab_block_alloc()` calls the selected allocator policy, removes the range from `ms_allocatable`, records it in the txg-specific `ms_allocating[]` tree, dirties the vdev metaslab, and updates cached maximum segment size.

Metaslab weights can be space-based or segment-based. Space weighting uses free space, fragmentation, active state, and optional LBA bias. Segment weighting encodes the highest free-segment histogram bucket and count, using loaded range-tree histograms when available and spacemap histograms plus deferred-free histograms when unloaded. Segment-based active metaslabs may be passivated after enough high buckets are exhausted.

Loading reads the metaslab spacemap up to `ms_synced_length`, constructs `ms_allocatable` plus its size-sorted B-tree, applies unflushed alloc/free deltas, removes deferred/freed ranges that are not yet allocatable, recalculates weight, and updates maximum segment size. Unloading vacates the in-core allocatable tree, clears active state, removes the metaslab from the txg-age multilist, and recalculates weight from on-disk state. Memory pressure can evict older loaded metaslabs.

Sync creates spacemap objects on first use, writes allocation/free deltas either to the pool-wide log spacemap or the per-metaslab spacemap, maintains unflushed delta trees, writes checkpoint frees to the vdev checkpoint spacemap, refreshes histograms, moves `ms_freeing` to `ms_freed`, and clears the txg allocation tree. `metaslab_sync_done()` returns deferred frees to circulation after the delay, updates vdev/class accounting, handles low-space/removal cases where deferral is disabled, updates autotrim ranges, marks new metaslabs ready, and resorts weights.

Condensing rewrites an inefficient spacemap into a compact representation by truncating it, writing an all-allocated record followed by current free/deferred ranges, clearing unflushed state, and treating condense as a flush. Log-spacemap flushing writes `ms_unflushed_allocs` and `ms_unflushed_frees` back to the metaslab spacemap and updates top-vdev on-disk unflushed txg metadata.

Freeing validates target ranges, handles vdev removal and indirect vdev remapping, sends checkpoint-protected frees to `ms_checkpointing`, and ordinary frees to `ms_freeing`. Claiming loads/activates the metaslab if needed, verifies the range is free, removes it from `ms_allocatable`, and records it as allocated for the txg. Public `metaslab_alloc_range()` unwinds partial DVA allocations on failure.

## Dependencies

Depends on SPA/vdev class state, DMU transactions and MOS objects, space maps and log space maps, range-tree and B-tree infrastructure, vdev removal/indirect mappings, checkpoint state, ZIO allocation flags, BRT clone detection, ARC memory accounting, taskqs, multilist, kstats, module parameter plumbing, and debug verification flags.

## Correctness Notes

The file is lock-heavy: `ms_lock` protects per-metaslab state, `ms_sync_lock` blocks vdev removal from observing partially synced state, group/class locks protect AVL/histogram/rotor state, and load/flush condition variables serialize conflicting spacemap operations. `metaslab_load()` and `metaslab_flush()` must not race because unflushed delta interpretation depends on a stable view. Histograms are removed from group/class totals before destructive updates and re-added afterward. Allocation deliberately avoids condensing, disabled, and not-yet-ready metaslabs. `metaslab_claim()` performs a dry run before real claim so partial claim failure does not need unwinding. Remapping refuses dedup, gang, embedded, and BRT-referenced cloned blocks because other subsystems depend on stable DVA identity.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/metaslab.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/mmp.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/mmp.c

## Scope

OpenZFS Multi-Modifier Protection implementation. This file maintains MMP heartbeat uberblock writes while a multihost pool is imported, records delay/config data in MMP-reserved uberblock slots, supports claim writes during import, suspends pools when configured heartbeat deadlines are missed, and exposes tunables for MMP timing.

## Main Interfaces

- Lifecycle: `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`.
- Uberblock state: `mmp_update_uberblock()`.
- Import claim: `mmp_claim_uberblock()`.
- Thread signaling: `mmp_signal_all_threads()`.
- Internal write path: `mmp_next_leaf()`, `mmp_delay_update()`, `mmp_write_uberblock()`, `mmp_write_done()`.
- Tunables: `zfs_multihost_interval`, `zfs_multihost_import_intervals`, `zfs_multihost_fail_intervals`.

## State And Control Flow

`spa->spa_mmp` contains the MMP thread, condition variable, I/O lock, last selected leaf, latest synced uberblock copy, sequence number, delay estimate, last successful write time, skip error state, kstat IDs, and outstanding root zio.

When a pool is writable, `mmp_thread_start()` creates `mmp_thread()`. The thread tracks multihost state, suspension state, interval/fail-interval tunables, and leaf count. If multihost is enabled and the pool is not suspended, it writes heartbeat uberblocks roughly once per configured interval per leaf. Tunable changes cause accelerated writes so peers can see the new configuration quickly.

`mmp_write_uberblock()` enters `SCL_STATE`, chooses a writable leaf without a pending MMP write, fills the cached uberblock with `MMP_MAGIC`, delay, interval/fail-interval config, timestamp, and sequence, then writes it to a random label and MMP-reserved uberblock slot. Completion updates delay, clears leaf pending state, exits the config lock, records history, and frees the ABD.

`mmp_delay_update()` stores a conservative write-delay estimate: spikes are recorded immediately, successful shorter delays decay slowly, and the minimum stays at the expected per-leaf write cadence. If multihost is off, delay is cleared so later import can skip activity checks.

`mmp_claim_uberblock()` is used during import claiming. It writes the candidate MMP uberblock to label 0 of all writable leaves under `SCL_ALL`, flushes, and requires enough successful writes for topology visibility: one for singletons, two for mirrors, and parity plus one for raidz/draid.

If no successful MMP write lands for `fail_intervals * interval`, `mmp_thread()` suspends the pool with `ZIO_SUSPEND_MMP`. Fail interval 0 disables suspension but still records failures.

## Dependencies

Depends on SPA/vdev config locking, vdev leaf lists and writeability, uberblock layout macros, ABD and ZIO label writes/flushes, spa MMP history/kstats, pool multihost property state, callb CPR thread hooks, and module parameter callbacks.

## Correctness Notes

MMP writes use uberblock slots reserved away from normal txg-sync uberblocks, preserving historical txg slots. Leaf selection skips offline, detached, unwritable, dRAID spare, and pending-write leaves. `mmp_write_done()` holds enough state to clear pending writes and exit `SCL_STATE` exactly once. Import claim requires topology-specific write quorum to reduce false ownership claims. The timestamp/sequence handling resets sequence on timestamp change to preserve `uberblock_compare()` ordering.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/mmp.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/multilist.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/multilist.c

## Scope

Thread-scalable sharded list implementation. This file wraps multiple independently locked `list_t` sublists behind one `multilist_t`, providing lower-contention insertion/removal and explicit sublist operations for callers that need controlled traversal or locking.

## Main Interfaces

- Creation/destruction: `multilist_create()`, `multilist_destroy()`.
- Whole-multilist operations: `multilist_insert()`, `multilist_remove()`, `multilist_is_empty()`, `multilist_get_num_sublists()`, `multilist_get_random_index()`.
- Sublist locking: `multilist_sublist_lock()`, `multilist_sublist_lock_idx()`, `multilist_sublist_lock_obj()`, `multilist_sublist_unlock()`.
- Sublist mutation: `multilist_sublist_insert_head()`, `multilist_sublist_insert_tail()`, `multilist_sublist_insert_after()`, `multilist_sublist_insert_before()`, `multilist_sublist_move_forward()`, `multilist_sublist_remove()`.
- Sublist inspection: `multilist_sublist_is_empty()`, `multilist_sublist_is_empty_idx()`, `multilist_sublist_head()`, `multilist_sublist_tail()`, `multilist_sublist_next()`, `multilist_sublist_prev()`.
- Link helpers: `multilist_link_init()`, `multilist_link_active()`.
- Tunable: `zfs_multilist_num_sublists`.

## State And Control Flow

`multilist_create()` chooses the number of sublists from `zfs_multilist_num_sublists` or `MAX(boot_ncpus, 4)`, records object offset and caller-supplied index function, allocates `ml_sublists`, initializes one mutex and `list_t` per sublist.

`multilist_insert()` and `multilist_remove()` compute the target sublist with `ml_index_func`, lock it unless the current thread already holds it, then insert or remove. Direct sublist insert helpers require the sublist lock and allow callers to place objects at head, tail, or relative positions.

`multilist_is_empty()` checks each sublist under its lock one at a time, so it is safe against list corruption but only provides a fuzzy answer under concurrent mutation. `multilist_sublist_move_forward()` swaps an object with its previous list neighbor and is constrained to remove only the target object because ARC eviction code depends on that behavior.

## Dependencies

Depends on OpenZFS `list_t`, mutex primitives, `random_in_range()`, `boot_ncpus`, DTrace probes, and module parameter plumbing.

## Correctness Notes

The index function must be stable for each object and return a valid sublist index; otherwise `multilist_remove()` can remove from the wrong list. Whole-list insert/remove intentionally tolerate callers already holding the sublist mutex. Direct sublist insertion can violate index-function placement, so callers must ensure they later remove consistently. Destroy asserts all sublists are empty.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/multilist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/objlist.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/objlist.c

## Scope

Small ascending object-number list utility. It stores object IDs in increasing order and supports monotonic lookup that discards already-passed entries.

## Main Interfaces

- `objlist_create()` allocates and initializes an empty `objlist_t`.
- `objlist_destroy()` frees all remaining nodes and the list.
- `objlist_insert()` appends a new object number, with debug assertion that insertions are strictly ascending.
- `objlist_exists()` tests whether an object exists while pruning all list entries smaller than the lookup object.

## State And Control Flow

`objlist_t` wraps a `list_t` of `objlist_node_t` and records `ol_last_lookup`. Insertions append to the tail and must be in ascending order. Lookups must also be ascending: `objlist_exists()` asserts the requested object is at least the last lookup, removes and frees all head nodes smaller than the requested object, then returns whether the head equals the requested object.

## Dependencies

Uses OpenZFS list primitives, `kmem_alloc()` / `kmem_zalloc()` / `kmem_free()`, and debug assertions.

## Correctness Notes

This is a streaming membership structure, not a general set. Looking up object `N` permanently discards all stored objects smaller than `N`, and later lookup of a smaller object is invalid. Callers rely on sorted insert and sorted lookup for O(total nodes) behavior across a scan.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/objlist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/pathname.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/pathname.c

## Scope

Minimal pathname buffer allocation utility used by the OpenZFS portability layer. This file allocates and frees the storage inside a `struct pathname`.

## Main Interfaces

- `pn_alloc()` allocates a pathname buffer of `MAXPATHLEN`.
- `pn_alloc_sz()` allocates a pathname buffer of a caller-specified size and records `pn_bufsize`.
- `pn_free()` frees `pn_buf` using the recorded size and clears the pointer and size.

## State And Control Flow

Callers typically allocate `struct pathname` itself on the stack and call `pn_alloc()` or `pn_alloc_sz()` to allocate the internal buffer with `KM_SLEEP`. `pn_free()` releases that buffer and resets the structure fields to prevent stale reuse.

## Dependencies

Uses `struct pathname` definitions, `MAXPATHLEN`, and kernel memory allocation helpers from `sys/kmem.h`.

## Correctness Notes

`pn_free()` relies on `pn_bufsize` matching the original allocation size, which is why `pn_alloc_sz()` records it immediately. Allocation can sleep and must not be used from interrupt context.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/pathname.c -->