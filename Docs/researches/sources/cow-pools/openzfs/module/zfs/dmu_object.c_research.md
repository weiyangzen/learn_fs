# File Research: sources/cow-pools/openzfs/module/zfs/dmu_object.c

## Scope

DMU object allocation, claiming, reclaiming, freeing, iteration, and zapification helpers. This file manages object ID selection across per-CPU allocation chunks, dnode slot sizing, explicit object claims, object reuse, spill removal, object free, next-object scans, and extensible-dataset ZAP conversion.

## Main Interfaces

- Allocation: `dmu_object_alloc()`, `dmu_object_alloc_ibs()`, `dmu_object_alloc_dnsize()`, `dmu_object_alloc_hold()`.
- Claim/reclaim: `dmu_object_claim()`, `dmu_object_claim_dnsize()`, `dmu_object_reclaim()`, `dmu_object_reclaim_dnsize()`.
- Removal: `dmu_object_rm_spill()`, `dmu_object_free()`.
- Iteration: `dmu_object_next()`.
- ZAP conversion: `dmu_object_zapify()`, `dmu_object_free_zapified()`.
- Tunable: `dmu_object_alloc_chunk_shift`.

## State And Control Flow

`dmu_object_alloc_impl()` is the common allocator. It chooses a CPU-specific next-object pointer, normalizes requested dnode slots, clamps allocation chunk size between one dnode block and one L1 metadnode span, and hands out object IDs atomically. When a per-CPU chunk boundary is reached, it takes `os_obj_lock`, pulls from `os_obj_next_chunk`, and may rescan sparse metadnode regions using `dnode_next_offset()` when polishing off an L1 span or when `os_rescan_dnodes` requests reuse.

For each candidate object, it calls `dnode_hold_impl(... DNODE_MUST_BE_FREE ...)`, locks the dnode structure, rechecks that the dnode is still free, allocates it, adds it to the transaction’s new-object list, and either returns a held dnode to the caller or releases it. Races with another allocator bump a stat and continue. Errors advance to the next valid starting point, often the next dnode block.

Claim functions allocate a specific free object, with special protection for `DMU_META_DNODE_OBJECT` unless the transaction is private. Reclaim functions require an allocated object and reallocate it to a new type/blocksize/bonus layout, optionally preserving spill. `dmu_object_rm_spill()` removes spill state only when the spill flag is present. `dmu_object_free()` frees all ranges first to avoid leaking indirect blocks, then frees the dnode.

`dmu_object_next()` returns the next allocated object or hole after a starting object. With large dnodes active, it first scans remaining slots in the current metadnode block using `dmu_object_info()` so multi-slot dnodes and holes are handled accurately, then falls back to `dnode_next_offset()`.

`dmu_object_zapify()` converts a syncing-context MOS object from an old type into `DMU_OTN_ZAP_METADATA`. It initializes the ZAP payload before changing the dnode type so concurrent “is zapified” checks can rely on type as completion marker, dirties the dnode, and increments `SPA_FEATURE_EXTENSIBLE_DATASET`. `dmu_object_free_zapified()` decrements that feature if needed before freeing.

## Dependencies

Uses dnode allocation/reallocation/free internals, objset allocation cursors and locks, DMU transactions, metadnode scanning, ZAP mini-create implementation, DSL dataset feature checks, and SPA feature reference counting.

## Correctness Notes

The per-CPU chunk allocator reduces hot lock contention but preserves traversal assumptions by using multiple metadnode blocks before aggressive reuse. Large-dnode iteration must skip the full slot count of allocated dnodes when looking for holes. Object freeing first frees the entire data range so syncing-context dnode free does not leak indirect blocks. Zapification is syncing-context-only and orders initialization before type change to make type checks safe.
