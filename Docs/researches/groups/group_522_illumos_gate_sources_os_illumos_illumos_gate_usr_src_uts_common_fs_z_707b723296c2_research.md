# Group Research: group_522_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_z_707b723296c2

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/metaslab.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/metaslab.c

## Scope

This file implements the core ZFS metaslab allocator for illumos: metaslab classes, metaslab groups, per-metaslab range-tree state, allocator policies, weight/fragmentation scoring, allocation and free paths, sync-time spacemap persistence, log spacemap flushing, checkpoint accounting, indirect-vdev remapping, and allocation throttling. The file was read completely.

## APIs And Entry Points

- Lifecycle and stats: `metaslab_stat_init()`, `metaslab_stat_fini()`, `metaslab_init()`, `metaslab_fini()`, `metaslab_load()`, `metaslab_unload()`, `metaslab_load_wait()`, `metaslab_flush_wait()`.
- Class/group management: `metaslab_class_create()`, `metaslab_class_destroy()`, `metaslab_class_validate()`, class space getters, `metaslab_class_fragmentation()`, `metaslab_class_expandable_space()`, `metaslab_class_evict_old()`, `metaslab_group_create()`, `metaslab_group_destroy()`, `metaslab_group_activate()`, `metaslab_group_passivate()`, `metaslab_group_initialized()`, `metaslab_sync_reassess()`.
- Allocation: `metaslab_alloc()`, `metaslab_alloc_dva()`, `metaslab_group_alloc()`, `metaslab_group_alloc_normal()`, `metaslab_block_alloc()`, plus dynamic-fit, cursor-fit, and new-dynamic-fit allocator ops.
- Free/claim/remap: `metaslab_free()`, `metaslab_free_dva()`, `metaslab_free_concrete()`, `metaslab_unalloc_dva()`, `metaslab_claim()`, `metaslab_claim_impl()`, `spa_remap_blkptr()`.
- Sync/persistence: `metaslab_sync()`, `metaslab_sync_done()`, `metaslab_flush()`, `metaslab_set_unflushed_txg()`, `metaslab_unflushed_txg()`.
- Debug/support: allocation tracing, `metaslab_check_free()`, histogram verification, disabled-metaslab controls, allocation-throttle reserve/unreserve helpers.

## Control Flow

Metaslab classes represent allocation classes such as normal, special, or dedup and maintain a rotor of active metaslab groups. Groups represent top-level vdev allocation domains and maintain an AVL tree of metaslabs sorted by active state and weight. Group eligibility is recalculated from vdev free capacity, fragmentation, activation state, and allocation throttle queue depth.

Each metaslab has multiple range trees for distinct TXG states: currently allocatable space, allocations in each TXG, frees being synced, freed/deferred frees, checkpointing, unflushed alloc/free deltas, and trim candidates. `metaslab_init()` creates the metaslab object, opens an existing spacemap if present, creates the initial allocatable/trim trees, joins the group, and initializes space accounting when the metaslab is immediately available. `metaslab_sync_done()` lazily creates the remaining TXG trees for newly available metaslabs.

Loading a metaslab reads its space map up to `ms_synced_length`, builds the in-core allocatable tree and size-sorted auxiliary tree, applies unflushed deltas, removes deferred/freed ranges that are not usable yet, recalculates weight, and updates `ms_max_size`. Loading coordinates with `ms_loading`, `ms_flushing`, and `ms_sync_lock` because sync, flush, and load may all touch related on-disk and in-core state.

Allocation begins at the class rotor, selects candidate metaslab groups with capacity/fragmentation/throttle filtering, then selects or activates a metaslab. Active metaslabs are tracked per allocator as primary or secondary; claim activation is separate for import/ZIL claim paths. The selected allocation policy removes a range from `ms_allocatable`, records it in the current TXG’s `ms_allocating` tree, clears overlapping trim candidates, dirties the metaslab, and updates queue-depth tracking.

Sync writes TXG allocation/free deltas either to the pool-wide log spacemap or directly to the metaslab spacemap. It updates allocated-space counters, checkpoint spacemaps, histograms, auxiliary histograms, unflushed delta trees, and deferral state. `metaslab_sync_done()` returns deferred frees to circulation when allowed, updates class/vdev accounting, recalculates weight, and unloads old inactive metaslabs. `metaslab_flush()` writes accumulated log-spacemap deltas back into a metaslab’s own spacemap; if the metaslab should condense, it rewrites a compact spacemap instead.

Freeing validates the target DVA, routes indirect vdev mappings through `vdev_op_remap`, handles removing-vdev obsolete accounting, and adds concrete ranges to `ms_freeing` or `ms_checkpointing`. Immediate unallocation removes the range from `ms_allocating` and returns it to `ms_allocatable`. Claim paths dry-run first, then remove claimable ranges from free space and dirty allocation state.

## State And Dependencies

The file depends heavily on `range_tree.c`, space maps, DMU transactions, SPA config locks, vdev state, ZIO allocation flags, blkptr/DVA helpers, AVL trees, btrees, multilists, and ZFS feature flags such as spacemap histograms, log spacemap, obsolete counts, and checkpoints.

Important state includes class counters (`mc_alloc`, `mc_deferred`, `mc_space`, histograms, rotor, allocation slots), group state (`mg_metaslab_tree`, primaries/secondaries, allocatable flags, fragmentation, disabled counts, queue-depth refcounts), and per-metaslab state (`ms_allocatable`, TXG trees, unflushed trees, `ms_weight`, `ms_fragmentation`, `ms_max_size`, loading/flushing/condensing flags, spacemap object, deferred-space accounting).

## Risks And Invariants

- Lock ordering is critical. The code uses spa config locks, group locks, metaslab locks, `ms_sync_lock`, multilist sublist locks, and disabled-metaslab locks with carefully documented drop/reacquire points.
- Loaded and unloaded metaslabs intentionally compute weights from different sources: loaded range-tree histograms versus on-disk spacemap histograms adjusted by auxiliary defer histograms.
- Log spacemap mode changes load, sync, and flush behavior. Incorrect unflushed delta handling can double-count or lose allocations/frees.
- `ms_condensing` prevents allocations while compacting a spacemap because the in-core free tree is being committed in a special form.
- Free deferral is bypassed near slop space or during vdev removal, which changes when freed space returns to allocatable state.
- Indirect vdev remapping intentionally avoids dedup, gang, embedded, and split-block cases; remapping changes DVA[0] and physical birth.
- Allocation throttling uses debug refcounts and per-vdev queue depth; failures for gang block minimum size mark groups as having no free space.
- Metaslab disable/enable limits the number of disabled metaslabs per group to avoid total allocation starvation during initialize/TRIM work.

## Summary

`metaslab.c` is the illumos ZFS allocator’s central implementation. It converts pool/vdev free-space metadata into weighted metaslab selection, performs allocation and free bookkeeping across TXGs, persists that bookkeeping through space maps and log space maps, and coordinates with checkpoints, vdev removal, trim, gang allocation, and import-time claiming. Its highest-risk areas are concurrency, on-disk/in-core space accounting consistency, and feature-dependent spacemap behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/metaslab.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/mmp.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/mmp.c

## Scope

This file implements ZFS Multi-Modifier Protection, which writes periodic MMP heartbeat uberblocks so another host can detect that a multihost pool is active before importing it. The file was read completely.

## APIs And Entry Points

- Lifecycle: `mmp_init()`, `mmp_fini()`, `mmp_thread_start()`, `mmp_thread_stop()`.
- Uberblock state: `mmp_update_uberblock()` copies the last synced uberblock into MMP state and refreshes timestamp/delay tracking.
- Thread signaling: `mmp_signal_all_threads()` wakes active pool MMP threads after tunable changes.
- Internal flow: `mmp_thread()`, `mmp_write_uberblock()`, `mmp_next_leaf()`, `mmp_delay_update()`, `mmp_write_done()`.

## Control Flow

When enabled by the pool’s `multihost` property, `mmp_thread()` periodically selects a writable leaf vdev without an outstanding MMP write and writes a copy of the last synced uberblock into one of the reserved MMP uberblock slots near the end of a randomly chosen label. It updates `ub_mmp_magic`, `ub_mmp_delay`, and `ub_mmp_config`, including sequence, interval, and fail interval values.

`mmp_next_leaf()` rotates through spa leaves under `SCL_STATE` and `mmp_io_lock`, skipping non-writable leaves and leaves with pending MMP writes. `mmp_write_done()` updates delay statistics, clears pending flags on the vdev, exits the spa config lock acquired for the write, and frees the ABD buffer.

The thread recalculates interval and failure thresholds each loop. It writes more aggressively after tunable changes so importers observe new parameters sooner. If multihost is enabled and no MMP write succeeds within the configured fail interval window, the pool is suspended with `ZIO_SUSPEND_MMP`.

## State And Dependencies

Core state lives in `spa->spa_mmp`: thread pointer/exit flag/CV, `mmp_io_lock`, last leaf and leaf-list generation, last synced MMP uberblock copy, sequence counter, delay estimate, last successful write time, skip error, kstat IDs, and root zio.

Dependencies include ABD buffers, vdev label writes, uberblock layout/macros, SPA namespace iteration, spa config locks, vdev writability, leaf lists, `zio_suspend()`, CPR thread support, and tunables `zfs_multihost_interval`, `zfs_multihost_import_intervals`, and `zfs_multihost_fail_intervals`.

## Risks And Invariants

- Import safety depends on visible on-disk heartbeat changes and conservative import wait-time calculation from MMP config/delay fields.
- MMP writes must not overwrite normal txg_sync uberblocks; reserved slots are used.
- Pending writes are per-leaf. A leaf with a stuck MMP write is skipped to avoid piling up writes, but prolonged failures may suspend the pool.
- `mmp_delay` is deliberately not averaged downward too quickly; sudden latency spikes must remain visible to importers.
- `mmp_delay` is set to zero when multihost is off so future imports can skip the activity test.
- `mmp_thread_stop()` waits for the thread and then waits for outstanding MMP zios before clearing the root.

## Summary

`mmp.c` provides the runtime heartbeat half of ZFS multihost protection. It does not prove all possible multi-writer misuse cases, but it gives import code observable disk activity, tunable-derived wait windows, and fail-stop pool suspension when configured heartbeat writes stop succeeding.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/mmp.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/multilist.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/multilist.c

## Scope

This file implements `multilist_t`, a sharded list abstraction used by ZFS to reduce lock contention while preserving normal list operations within independently locked sublists. The file was read completely.

## APIs And Entry Points

- Creation/destruction: `multilist_create()`, internal `multilist_create_impl()`, `multilist_destroy()`.
- Whole-list operations: `multilist_insert()`, `multilist_remove()`, `multilist_is_empty()`, `multilist_get_num_sublists()`, `multilist_get_random_index()`.
- Sublist operations: `multilist_sublist_lock()`, `multilist_sublist_lock_obj()`, `multilist_sublist_unlock()`, insert head/tail, remove, move forward, head/tail/next/prev.
- Link helpers: `multilist_link_init()`, `multilist_link_active()`.

## Control Flow

A multilist owns an array of `multilist_sublist_t`, each with its own mutex and illumos `list_t`. The creator supplies the object size, offset of the embedded `multilist_node_t`, and an index function that maps objects to sublists. `multilist_create()` chooses the sublist count from `zfs_multilist_num_sublists` or defaults to at least four and typically CPU count.

Insert and remove compute the target sublist from the index function, acquire the sublist lock if the caller does not already hold it, and operate on the embedded list node. Sublist APIs expose explicit locking so callers can traverse or batch operations on a shard without locking the whole multilist. `multilist_is_empty()` checks each sublist independently, so concurrent mutation means its result is a moment-in-time approximation rather than a globally locked snapshot.

## State And Dependencies

State is limited to `ml_offset`, `ml_num_sublists`, `ml_index_func`, and the sublist array. It depends on `list_t`, kernel mutexes, ZFS allocation helpers, DTrace probes, CPU count, and `spa_get_random()` for random sublist selection.

In this group, `metaslab.c` uses multilists for the metaslab class TXG list, allowing eviction and selected-TXG ordering to scale across sublists.

## Risks And Invariants

- The index function must be stable for an object while inserted. Removing with a different computed sublist is undefined.
- Direct sublist insertion can place an object in a sublist that differs from its index function; callers must then avoid whole-list remove semantics unless the index matches.
- The lock recursion pattern depends on `MUTEX_HELD()` accurately reporting ownership by the current thread.
- `multilist_sublist_move_forward()` must only remove/reinsert the requested object; ARC eviction relies on that behavior.

## Summary

`multilist.c` is a small concurrency utility: it trades global list ordering for sharded locking and lower contention. Its correctness rests on stable object-to-sublist mapping and disciplined use of explicit sublist locks during traversal.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/multilist.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/range_tree.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/range_tree.c

## Scope

This file implements ZFS range trees, the extent set data structure used for free-space, deferred-free, allocation, trim, checkpoint, and other range accounting. It supports 32-bit, 64-bit, and gap-bridging segment encodings, btree storage, histograms, callbacks, walking/vacating, and set-difference style updates. The file was read completely.

## APIs And Entry Points

- Lifecycle: `range_tree_create()`, `range_tree_create_impl()`, `range_tree_destroy()`.
- Mutation: `range_tree_add()`, `range_tree_remove()`, `range_tree_remove_fill()`, `range_tree_clear()`, `range_tree_resize_segment()`, `range_tree_adjust_fill()`, `range_tree_swap()`, `range_tree_vacate()`.
- Queries/walks: `range_tree_find()`, `range_tree_contains()`, `range_tree_find_in()`, `range_tree_verify_not_present()`, `range_tree_walk()`, `range_tree_first()`, `range_tree_space()`, `range_tree_numsegs()`, `range_tree_is_empty()`, `range_tree_min()`, `range_tree_max()`, `range_tree_span()`.
- Verification and auxiliary btrees: `range_tree_stat_verify()`, `rt_btree_ops`.
- Delta operations: `range_tree_remove_xor_add_segment()`, `range_tree_remove_xor_add()`.

## Control Flow

A range tree stores non-overlapping segments in a `zfs_btree_t`. Adding a range finds adjacent or gap-near neighbors, merges with before/after segments when appropriate, updates fill counts for gap trees, adjusts histograms, invokes callbacks, and increments total represented space. Removing a range finds the containing segment, then deletes, shortens, or splits it while updating callbacks, histograms, and total space.

Gap trees bridge small holes between nearby ranges for scan-style I/O grouping. For these trees, fill can be less than segment span, and removals are restricted to complete segments unless `range_tree_remove_fill()` is adjusting fill. Normal trees require fill to equal extent size.

Callbacks in `range_tree_ops_t` allow users to maintain secondary structures such as a size-sorted btree. `rt_btree_ops` is the generic implementation for mirroring range-tree segments into another btree. `metaslab.c` provides its own callback set to maintain size-sorted allocation trees with a minimum segment-size floor.

`range_tree_remove_xor_add()` is used for log spacemap unflushed delta handling: each input segment removes overlapping portions from one tree and adds non-overlapping leftovers to another, effectively applying XOR-like alloc/free cancellation.

## State And Dependencies

Each `range_tree_t` contains a root btree, total `rt_space`, histogram buckets, optional ops/arg, segment type, logical start/shift for compact 32-bit encodings, optional btree comparator, and gap size. It depends on ZFS btrees, segment accessor macros, kmem allocation, panic/recovery helpers, and ZFS debug logging.

This file is foundational for `metaslab.c`; metaslab allocation correctness relies on range-tree merging/splitting, histogram accuracy, and callback updates.

## Risks And Invariants

- `rt_space` and histograms must match btree contents after every add/remove/split/merge. `range_tree_stat_verify()` exists to catch drift.
- Removing a non-existent segment calls `zfs_panic_recover()`, because that implies space accounting corruption.
- Gap trees have special fill semantics and cannot safely support arbitrary partial removals.
- Callback users must tolerate temporary remove/add sequences around resize, fill adjustment, split, merge, and vacate operations.
- `range_tree_vacate()` can either discard segments or walk them into another consumer while destroying btree nodes.
- Compact 32-bit segment trees rely on correct `start` and `shift` normalization from callers.

## Summary

`range_tree.c` supplies the extent algebra underneath ZFS allocator state. Its job is not policy; it provides precise merged ranges, accounting, histograms, and callback hooks that higher layers such as metaslabs use for allocation choice and sync-time persistence.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/range_tree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/refcount.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/refcount.c

## Scope

This file implements ZFS debug refcount tracking under `ZFS_DEBUG`. In non-debug builds this file contributes no compiled implementation because the entire body is conditional. The file was read completely.

## APIs And Entry Points

- Global lifecycle: `zfs_refcount_init()`, `zfs_refcount_fini()`.
- Creation/destruction: `zfs_refcount_create()`, `zfs_refcount_create_tracked()`, `zfs_refcount_create_untracked()`, `zfs_refcount_destroy()`, `zfs_refcount_destroy_many()`.
- Counting: `zfs_refcount_count()`, `zfs_refcount_is_zero()`.
- Add/remove: `zfs_refcount_add_many()`, `zfs_refcount_add()`, `zfs_refcount_add_few()`, `zfs_refcount_remove_many()`, `zfs_refcount_remove()`, `zfs_refcount_remove_few()`.
- Ownership and inspection: `zfs_refcount_transfer()`, `zfs_refcount_transfer_ownership_many()`, `zfs_refcount_transfer_ownership()`, `zfs_refcount_held()`, `zfs_refcount_not_held()`.

## Control Flow

A refcount can be tracked or untracked. Untracked refcounts update `rc_count` atomically and do not remember individual holders. Tracked refcounts allocate `reference_t` records from a kmem cache and store them in an AVL tree keyed by holder pointer and reference number. This lets debug builds detect removing a hold that was never added and query whether a specific holder is present.

Removal in tracked mode finds the exact holder/count record, removes it from the AVL tree, decrements `rc_count`, and optionally keeps recently removed references in `rc_removed` for postmortem history. The history length is controlled by `reference_history`.

Transfer operations move all references from one refcount to another, including active tree entries and removed-history entries. Ownership-transfer operations retag an existing holder to a new holder without changing the count.

## State And Dependencies

Global state includes `reference_tracking_enable`, `reference_history`, and two kmem caches. Each `zfs_refcount_t` contains a mutex, AVL tree of live references, list of removed-history records, count fields, and a tracked flag.

In this group, `metaslab.c` uses tracked refcounts for allocation slots and metaslab group allocation queue depth, giving debug visibility into allocation throttle reservations.

## Risks And Invariants

- `zfs_refcount_destroy_many()` asserts the expected final count, so callers must drain holds or pass the expected residual count.
- Tracked removal panics if the holder/count pair does not exist, which is intentional debug enforcement.
- In untracked mode, holder-specific queries are conservative: “held” means count is nonzero, and “not held” always returns true because individual holders are unknown.
- `zfs_refcount_add_few()` and remove-few split into individual records in tracked mode so later per-holder removals can match one hold at a time.
- Transfer merges AVL entries into the destination and preserves removed-history lists; callers must avoid conflicting live holder/count identities.

## Summary

`refcount.c` is a debug-only accountability layer around reference counts. It lets ZFS use cheap atomic counts when tracking is disabled and detailed holder records when diagnosing leaks, double-removes, or allocation-throttle bookkeeping errors.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/refcount.c -->