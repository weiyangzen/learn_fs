# sources/distributed-fs/ceph-client/fs/btrfs/backref.h

## Purpose
`backref.h` declares the public Btrfs back-reference walking interface. It defines the context passed into the backref engine, callback contracts for inode iteration and optional caching/filtering, sharedness-check cache state, inode path container helpers, and exported functions used by logical-inode queries, fiemap sharedness checks, qgroups, relocation, and extent-tree backref parsing.

## Important APIs, types, and functions
- `BTRFS_ITERATE_EXTENT_INODES_STOP` is a non-error stop code that iterator callbacks may return to end backref iteration early.
- `iterate_extent_inodes_t` is the callback signature for inode/file-offset/root results.
- `struct btrfs_backref_walk_ctx` is the central argument block. Callers set `bytenr`, `extent_item_pos`, `ignore_extent_item_pos`, `trans`, `fs_info`, `time_seq`, output `refs`/`roots`, optional cache callbacks, optional early indirect-ref iterator, optional extent-item checker, optional data-ref skip callback, and `user_ctx`.
- `struct inode_fs_paths` carries the path, root, and result container for inode-to-path lookup.
- `struct btrfs_backref_share_check_ctx` stores reusable fiemap-style state: a working `ulist`, current/previous leaf bytenrs, per-level path cache entries, and a small previous-extent result cache.
- `btrfs_alloc_backref_share_check_ctx()` and `btrfs_free_backref_share_ctx()` manage sharedness context lifetime.
- `extent_from_logical()`, `iterate_extent_inodes()`, and `iterate_inodes_from_logical()` expose logical address to inode/root enumeration.
- `paths_from_inode()`, `btrfs_ref_to_path()`, `init_data_container()`, and `init_ipath()` expose inode path construction helpers.
- `btrfs_find_all_leafs()` and `btrfs_find_all_roots()` expose lower-level parent/root discovery.
- `btrfs_find_one_extref()` scans extended inode refs.
- `tree_backref_for_extent()` exposes tree-backref extraction from extent items.
- `btrfs_is_data_extent_shared()` exposes the optimized sharedness query.
- `btrfs_prelim_ref_init()` and `btrfs_prelim_ref_exit()` are module init/exit hooks for the private prelim-ref cache.

## Control flow
Callers normally allocate and initialize a `btrfs_backref_walk_ctx`, set `fs_info`, `bytenr`, and data-offset options, and choose the required output path. Leaf discovery calls `btrfs_find_all_leafs()` and reads `ctx->refs`. Root discovery calls `btrfs_find_all_roots()` and reads `ctx->roots`. Inode enumeration calls `iterate_extent_inodes()` with a callback, and optional cache callbacks can avoid re-resolving roots for leaves that were seen before.

For user-facing logical lookup, callers can use `iterate_inodes_from_logical()`, which internally maps the logical address to an extent, rejects metadata extents, and invokes the generic inode iterator. For path lookup, callers create an `inode_fs_paths` with `init_ipath()`, then call `paths_from_inode()` and read paths stored in the embedded `btrfs_data_container`.

For sharedness, callers allocate one `btrfs_backref_share_check_ctx` and reuse it across adjacent file extent items, updating `curr_leaf_bytenr` before each `btrfs_is_data_extent_shared()` call. The context caches tree-path sharedness and repeated data-extent results, so repeated fiemap-style scans do not pay full recursive backref costs every time.

## State and persistence behavior
This header defines only in-memory contracts. `btrfs_backref_walk_ctx` is per-walk and mostly caller-owned. `refs` and `roots` are `ulist` outputs or temporaries depending on the called helper. `btrfs_backref_share_check_ctx` is reusable but still volatile; it must be freed with `btrfs_free_backref_share_ctx()`. No state is persisted outside normal Btrfs metadata read by the implementation.

The `time_seq` and `trans` fields encode consistency requirements. A tree-mod-log sequence lets the implementation use old-tree views plus delayed refs; `BTRFS_SEQ_LAST` selects commit-root behavior and deliberately skips delayed refs for commit-time qgroup usage.

## Dependencies and integration points
The header depends on Linux rbtrees/lists/slab types, Btrfs UAPI tree definitions, extent buffers, locking, disk I/O, and core `ctree` definitions. Its declarations are consumed by backref-heavy features outside `backref.c`, including fiemap, logical-inode ioctls, qgroups, relocation, and extent-tree metadata parsers.

## Risks and test signals
API misuse risks include failing to initialize mandatory fields, passing a `refs` pointer where the callee expects `NULL`, forgetting to free returned ulists or inode path containers, using `BTRFS_SEQ_LAST` when delayed refs matter, enabling `indirect_ref_iterator` without cache callbacks, or letting cache callbacks return stale root IDs. Tests should cover each exported helper with initialized and intentionally missing context fields, transaction and commit-root modes, callback early-stop behavior, sharedness context reuse across leaves, short path containers, and logical addresses that map to data, metadata, and no extent.
