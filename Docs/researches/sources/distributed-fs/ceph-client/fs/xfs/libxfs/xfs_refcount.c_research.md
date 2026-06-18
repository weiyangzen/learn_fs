# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_refcount.c

## Purpose
`xfs_refcount.c` implements the shared-block and copy-on-write reference count logic for XFS reflink filesystems. It is the high-level editor for refcount btree records, converting file extent mapping changes into persistent per-AG or per-realtime-group refcount records. Shared extents are represented only when `rc_refcount >= 2`; in-progress COW staging extents are deliberately represented as domain-specific records with refcount 1 so that crash recovery can find and free orphaned COW allocations.

## Important APIs, types, and functions
The exported lookup/query primitives are `xfs_refcount_lookup_le`, `xfs_refcount_lookup_ge`, `xfs_refcount_lookup_eq`, `xfs_refcount_get_rec`, `xfs_refcount_insert`, `xfs_refcount_has_records`, and `xfs_refcount_query_range`. They are thin wrappers over generic btree operations, but they set `cur->bc_rec.rc` and validate decoded records before exposing them to callers.

Mutation is staged through `struct xfs_refcount_intent` instances allocated from `xfs_refcount_intent_cache`. `xfs_refcount_increase_extent`, `xfs_refcount_decrease_extent`, `xfs_refcount_alloc_cow_extent`, and `xfs_refcount_free_cow_extent` enqueue deferred operations; `xfs_refcount_finish_one` and `xfs_rtrefcount_finish_one` execute those operations against an AG refcountbt cursor or realtime refcountbt cursor. COW allocation/free helpers also schedule matching rmap operations with `XFS_RMAP_OWN_COW`.

Internal helpers implement record surgery: `xfs_refcount_split_extent` splits records crossing an operation boundary; `xfs_refcount_find_left_extents` and `xfs_refcount_find_right_extents` synthesize implicit refcount-1 gaps; `xfs_refcount_merge_extents` tries center/left/right merges; `xfs_refcount_adjust_extents` performs the actual increment/decrement; and `xfs_refcount_adjust_cow_extents` adds or removes COW-domain records.

## Control flow
For normal shared-block changes, callers enqueue an increase or decrease intent. The finisher creates or reuses a cursor for the correct AG/RTG, converts the filesystem block to a group block, and calls `xfs_refcount_adjust`. Adjustment first splits any records crossing the left and right operation boundaries, then attempts boundary merges, then walks the remaining interval. Missing records inside the interval are treated as implicit refcount 1 because a file mapping already proves the blocks are allocated. Incrementing such a gap inserts a shared-domain record with refcount 2; decrementing a shared record to 1 deletes it; decrementing below 1 schedules the underlying blocks for free through `xfs_free_extent_later`.

COW staging follows the same split/merge shape, but operates in `XFS_REFC_DOMAIN_COW` and enforces exact allocation/free matches. `__xfs_refcount_cow_alloc` requires no overlapping COW record; `__xfs_refcount_cow_free` requires an exact refcount-1 COW record. `xfs_refcount_recover_cow_leftovers` scans the COW domain at mount/recovery time, gathers all orphaned COW records in an empty transaction to avoid buffer deadlocks, then commits real transactions that remove the COW record and free the physical blocks.

## State and persistence behavior
Persistent state is the refcount btree itself, plus deferred-intent log items created by the refcount item layer. Shared records encode domain in the high startblock bit via `xfs_refcount_encode_startblock`; record bodies store startblock, blockcount, and refcount. The code relies on transaction logging through the generic btree layer, and free operations are deferred with `xfs_free_extent_later`. The finisher may leave an intent partially complete by updating `ri_startblock` and `ri_blockcount` if the transaction reservation is nearly exhausted, as estimated by `xfs_refcount_still_have_space`.

Realtime refcount operations parallel the AG implementation but lock and join the realtime group with `XFS_RTGLOCK_REFCOUNT`, use `xfs_rtrefcountbt_init_cursor`, and validate ranges with `xfs_verify_rgbext` / `xfs_verify_rtbext`.

## Dependencies and integration points
This file depends on generic btree operations, refcount btree cursor construction, realtime refcount btree support, deferred operation infrastructure, block allocation/freeing, rmap updates, AG/RTG locking, tracing, error tags, and health marking. It is called from bmap/reflink paths that map, unmap, share, unshare, and complete COW extents. It also feeds scrub/repair through range query and `has_records` helpers.

## Risks and invariants
Key risks are off-by-one interval handling, implicit refcount-1 gap synthesis, overflow around `XFS_REFC_LEN_MAX`, and transaction reservation underestimation. Corruption checks enforce nonzero bounded blockcount, valid domain/refcount combinations, valid AG/RTG ranges, exact insert/delete success counts, and exact COW frees. Records with `XFS_REFC_REFCOUNT_MAX` are pinned and no longer incremented, which is an intentional saturation behavior.

## Test signals
Useful coverage includes reflink copy/unshare workloads, COW writeback crash recovery, log recovery with pending refcount intents, realtime reflink operations, forced transaction continuations via `XFS_ERRTAG_REFCOUNT_CONTINUE_UPDATE`, and corruption tests that inject malformed records or boundary-crossing extents. Tracepoints such as `trace_xfs_refcount_modify_extent`, finisher leftovers, and btree sick markings are important diagnostics.
