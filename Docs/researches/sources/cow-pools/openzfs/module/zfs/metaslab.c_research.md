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
