# sources/distributed-fs/ceph-client/fs/btrfs/delayed-ref.c

## Purpose

`delayed-ref.c` implements transaction-time delayed reference tracking for Btrfs extents. Instead of updating extent-tree backrefs immediately while modifying file or metadata trees, callers queue reference additions, drops, extent insert accounting, and delayed extent operations. The transaction later selects ref heads, merges compatible ref nodes, runs them in a safe order, and commits the resulting extent-tree, qgroup, checksum, and reservation accounting changes.

## Important APIs, Types, and Functions

Reservation APIs include `btrfs_check_space_for_delayed_refs()`, `btrfs_delayed_refs_rsv_release()`, `btrfs_update_delayed_refs_rsv()`, block-group insert/update reservation adjusters, and `btrfs_delayed_refs_rsv_refill()`. Core queue APIs are `btrfs_init_tree_ref()`, `btrfs_init_data_ref()`, `btrfs_add_delayed_tree_ref()`, `btrfs_add_delayed_data_ref()`, and `btrfs_add_delayed_extent_op()`.

Processing helpers include `btrfs_select_ref_head()`, `btrfs_unselect_ref_head()`, `btrfs_delete_ref_head()`, `btrfs_select_delayed_ref()`, `btrfs_merge_delayed_refs()`, `btrfs_check_delayed_seq()`, `btrfs_find_delayed_ref_head()`, `btrfs_find_delayed_tree_ref()`, `btrfs_put_delayed_ref()`, and `btrfs_destroy_delayed_refs()`. Slab caches for heads, nodes, and extent operations are initialized and destroyed by `btrfs_delayed_ref_init()` and `btrfs_delayed_ref_exit()`.

## Control Flow

Adding a ref allocates a delayed ref node and head, optionally allocates/reserves a qgroup extent record, reserves xarray slots, initializes common fields, then inserts the head into `transaction->delayed_refs.head_refs` under the delayed refs spinlock. If a head already exists for the bytenr, `update_existing_head_ref()` merges aggregate counts, pending checksum-deletion accounting, owning root, `must_insert_reserved`, and delayed extent operations. The individual ref node is inserted into the head rbtree or merged with an equivalent node; add refs are also linked in `ref_add_list`.

Processing selects a head from the xarray starting at `run_delayed_start`, marks it processing, decrements ready counts, and locks the head mutex. Within a head, `btrfs_select_delayed_ref()` prefers add refs before drops so an extent item is not deleted before pending additions are applied. `btrfs_merge_delayed_refs()` merges compatible metadata refs when tree-mod-log sequence constraints allow it. After a head is fully processed, callers remove it with `btrfs_delete_ref_head()` and clean up accounting elsewhere.

Destruction during transaction abort walks all heads, locks each, drops all child refs, frees delayed extent ops, removes heads from the xarray, pins bytes for extents that had reserved insert accounting, performs cleanup accounting, and destroys qgroup extent records.

## State and Persistence Behavior

Delayed refs are in-memory transaction state. They represent future persistent changes to extent refs, extent item insertions, checksum item deletions, qgroup dirty extent records, and block-group reservation accounting. Persistent effects occur when the extent-tree processing code consumes selected refs before transaction commit. The file tracks reserve sizes in `fs_info->delayed_refs_rsv`, local transaction delayed reserves, `pending_csums`, `num_heads`, `num_heads_ready`, `run_delayed_start`, and per-head `ref_mod`/`total_ref_mod`.

## Dependencies and Integration Points

Dependencies include Btrfs transactions, extent-tree processing, qgroups, free-space-tree-aware reservation sizing, tree-mod-log sequence tracking, space-info accounting, block groups, xarrays, rbtrees, lists, spinlocks, mutexes, slab caches, and tracepoints. The qgroup integration records dirty extents when full accounting is enabled and can skip roots for snapshot accounting.

## Risks and Edge Cases

The xarray index is bytenr shifted by sectorsize bits; 32-bit builds reject delayed ref heads beyond the page-cache/xarray index limit. Ref merging must respect tree-mod-log sequence numbers or backref walking can observe wrong histories. Data refs are not aggressively merged because the code expects fewer of them. Pending csum deletion reservations depend on sign changes of aggregate data ref mods. Abort cleanup has to convert reserved extents into pinned bytes if they were never inserted. The lock order between delayed root spinlock, head mutex, and head spinlock is delicate, especially when `btrfs_delayed_ref_lock()` drops and reacquires the root lock.

## Test Signals

Useful validation includes snapshot/delete workloads with qgroups, heavy metadata churn that produces many merging tree refs, data extent drop paths that delete checksums, transaction abort after reserved extent insertion, 32-bit overflow coverage if supported, free-space-tree reservation sizing, zoned metadata reservation cap behavior, tree-mod-log backref walking concurrent with delayed refs, and slab allocation fault injection for head/node/qrecord allocations.
