# File Research: sources/cow-pools/openzfs/module/zfs/dsl_deadlist.c

## Role

`dsl_deadlist.c` implements OpenZFS deadlists and livelists. Deadlists track blocks that died after particular transaction group boundaries and are needed for snapshot, clone, and destroy accounting. Livelists reuse the same data structure to track clone-specific ALLOC/FREE block pointer history so clone deletion can avoid traversing the full block tree.

## Major Responsibilities

- Allocate, open, close, clone, free, and mutate deadlist objects.
- Support old-format `bpobj` deadlists and newer ZAP-backed deadlists.
- Maintain per-deadlist used/compressed/uncompressed accounting.
- Lazily load full AVL trees for mutation and sparse cache trees for range space queries.
- Add/remove transaction group keys and merge/move deadlist contents.
- Process livelist sublists by matching FREE and ALLOC records.
- Provide tunables for livelist sublist sizing and disable thresholds.

## Data Model

New-format deadlists are ZAP objects keyed by minimum txg. Each key maps to a `bpobj` containing block pointers for that txg interval. The bonus buffer stores `dsl_deadlist_phys_t`, including aggregate used/compressed/uncompressed counts.

Old-format deadlists are direct `bpobj` objects. Most functions branch on `dl_oldfmt` to preserve compatibility.

The in-memory form uses:

- `dl_tree`: full AVL tree of `dsl_deadlist_entry_t`, used for mutation.
- `dl_cache`: sparse AVL tree of non-empty `bpobj` entries, used for faster space-range queries.
- `dl_lock`: protects lazy loading, tree/cache state, and aggregate counters.

## Important Functions

- `dsl_deadlist_open()` / `dsl_deadlist_close()`: initialize or release old/new-format deadlist handles.
- `dsl_deadlist_alloc()` / `dsl_deadlist_free()`: allocate or recursively destroy deadlist storage.
- `dsl_deadlist_load_tree()`: loads all ZAP entries, prefetches bpobjs, opens them, and builds the mutation AVL.
- `dsl_deadlist_load_cache()`: loads only non-empty bpobjs and their space stats for efficient range queries.
- `dsl_deadlist_insert()`: inserts a block pointer into the correct txg interval and updates aggregate counters.
- `dsl_deadlist_add_key()` / `dsl_deadlist_remove_key()`: split or collapse txg ranges.
- `dsl_deadlist_remove_entry()` / `dsl_deadlist_clear_entry()`: delete or reset individual deadlist entries.
- `dsl_deadlist_clone()`: creates a new deadlist with matching txg keys up to `maxtxg`.
- `dsl_deadlist_space()` / `dsl_deadlist_space_range()`: return total or txg-range deadlist space.
- `dsl_deadlist_merge()`: merges another deadlist into this one and clears the source.
- `dsl_deadlist_move_bpobj()`: moves entries newer than a txg into a pool-level `bpobj`, used by destroy paths.
- `dsl_process_sub_livelist()`: reduces a livelist sublist into block pointers that still need freeing.

## Livelist Behavior

The file documents livelists as clone-specific histories of block pointer ALLOC and FREE events. Deleting a clone can process these records instead of walking the entire object tree. Livelists are split into sublists by txg to bound memory and allow incremental deletion.

`dsl_livelist_iterate()` uses an AVL tree keyed by DVA vdev/offset. FREE records create or increment a tracked entry. ALLOC records either cancel a prior FREE or are appended to the `to_free` bplist. The refcount handling supports dedup and block cloning cases where the same block pointer may appear multiple times.

## Concurrency

The file states the core concurrency contract:

- Deadlists are modified only from syncing context.
- Except for `dsl_deadlist_insert()`, modification requires `dp_config_rwlock` as writer.
- Accessors may run from open context with config lock as reader.
- `dl_lock` protects aggregate stats, lazy tree/cache loading, and concurrent insertion/stat collection.

`bpobj_t` provides its own internal locking where needed.

## Interactions

- `dsl_dataset.c` uses deadlists for block death, snapshots, remap deadlists, promotion, clone swap, written-space calculations, and livelist flushing.
- `dsl_destroy.c` uses deadlists to destroy snapshots, collapse txg keys, move freeable blocks to pool free queues, and process livelists.
- `dsl_pool` provides `dp_empty_bpobj`, pool free bpobj, and metadata object set state.
- `bpobj` is the lower-level persistent block pointer list container.

## Tunables

- `zfs_livelist_max_entries`: threshold for creating new livelist sublists.
- `zfs_livelist_min_percent_shared`: threshold below which clone livelists are disabled because the clone has diverged too far from the origin.
