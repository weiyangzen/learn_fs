# sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.c` implements the persistent Btrfs free-space tree. It stores per-block-group free-space metadata as `BTRFS_FREE_SPACE_INFO_KEY` plus either free-space extent items or free-space bitmap items, supports converting between extents and bitmaps based on fragmentation thresholds, maintains the tree as extents are allocated/freed, creates/deletes/rebuilds the tree, and loads it into the in-memory block-group cache. The file was read as a complete 1825-line implementation.

## Important APIs, Types, and Functions

Exported entry points include `btrfs_free_space_root`, `btrfs_set_free_space_tree_thresholds`, `btrfs_search_free_space_info`, `btrfs_create_free_space_tree`, `btrfs_delete_free_space_tree`, `btrfs_rebuild_free_space_tree`, `btrfs_add_block_group_free_space`, `btrfs_remove_block_group_free_space`, `btrfs_add_to_free_space_tree`, `btrfs_remove_from_free_space_tree`, `btrfs_load_free_space_tree`, and `btrfs_delete_orphan_free_space_entries`. Under sanity tests it also exports `__btrfs_add_to_free_space_tree`, `__btrfs_remove_from_free_space_tree`, bitmap/extent conversion functions, and `btrfs_free_space_test_bit`.

Important internal helpers are `add_new_free_space_info`, `btrfs_search_prev_slot`, `free_space_bitmap_size`, `alloc_bitmap`, `le_bitmap_set`, `update_free_space_extent_count`, `free_space_modify_bits`, `free_space_next_bitmap`, `modify_free_space_bitmap`, `add_free_space_extent`, `remove_free_space_extent`, `using_bitmaps`, `populate_free_space_tree`, `clear_free_space_tree`, `__add_block_group_free_space`, `load_free_space_bitmaps`, `load_free_space_extents`, and `delete_orphan_free_space_entries`.

## Control Flow

Creation begins in `btrfs_create_free_space_tree()`: start a transaction, set `BTRFS_FS_CREATING_FREE_SPACE_TREE` and `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED`, create and register the free-space root, walk every block group, and call `populate_free_space_tree()`. Population inserts a free-space info item, scans the extent root for allocated extent/metadata items within the block group, and inserts free-space ranges between allocated regions through `__btrfs_add_to_free_space_tree()`. After all block groups are populated, it sets `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` compat-ro flags, commits, and clears the untrusted bit.

Normal updates are guarded by the compat-ro feature flag. `btrfs_add_to_free_space_tree()` and `btrfs_remove_from_free_space_tree()` look up the owning block group, take `block_group->free_space_lock`, ensure pending new block-group free-space items exist through `__add_block_group_free_space()`, choose extent or bitmap representation through `using_bitmaps()`, then either merge/split extent items or set/clear bits in bitmap items. Both wrappers abort the transaction on update failure.

Extent representation uses one key per contiguous free range. Adding free space searches left and right neighbors, deletes adjacent items when needed, inserts the merged item, and updates the extent count. Removing free space finds the containing extent, deletes it, reinserts left/right leftovers, and updates the count. Bitmap representation modifies bits across one or more bitmap items and computes the extent-count delta from the immediate neighboring bits around the modified range.

Representation conversion is automatic in `update_free_space_extent_count()`. If extent count exceeds the high threshold, `btrfs_convert_free_space_to_bitmaps()` walks extent items backwards, builds an in-memory little-endian bitmap, deletes extents, sets `BTRFS_FREE_SPACE_USING_BITMAPS`, and writes bitmap items. If the count falls below the low threshold, `btrfs_convert_free_space_to_extents()` reads bitmap items, deletes them, clears the bitmap flag, and reinserts extent keys for contiguous set-bit runs.

Loading starts in `btrfs_load_free_space_tree()`. It searches the commit root without locking, reads the free-space info item count and flags, then calls either `load_free_space_extents()` or `load_free_space_bitmaps()` to add ranges to the runtime block-group cache using `btrfs_add_new_free_space()`. Both loaders validate counted extents against the persisted expected count and wake the caching control waitqueue after enough free space has been discovered.

Deletion and rebuild are explicit lifecycle operations. `btrfs_delete_free_space_tree()` clears feature flags, deletes all tree items, deletes the root item, unregisters the global root, frees the root node, and commits. `btrfs_rebuild_free_space_tree()` clears existing items, repopulates from block groups over one or more transactions, skips block groups already added while rebuilding, restores feature flags, commits, and clears the untrusted flag. Orphan cleanup removes free-space tree entries before the first block group for non-extent-tree-v2 filesystems.

## State and Persistence Behavior

Persistent state lives in the free-space tree root selected by `btrfs_free_space_root()`. With extent tree v2, the root key offset uses `block_group->global_root_id`; otherwise the single global free-space tree root is used. Each block group has an info item keyed by block-group start and length, storing extent count and flags. Data entries are either extent keys with offset as length and no payload, or bitmap keys with payload bytes sized by sectors represented. Block-group runtime fields cache the bitmap mode and thresholds: `bitmap_high_thresh`, `bitmap_low_thresh`, `using_free_space_bitmaps`, and `using_free_space_bitmaps_cached`.

Feature flags `FREE_SPACE_TREE` and `FREE_SPACE_TREE_VALID` determine whether the tree is active and trusted. During create/rebuild, `BTRFS_FS_FREE_SPACE_TREE_UNTRUSTED` prevents trusting commit-root free-space data until a successful commit. `BLOCK_GROUP_FLAG_NEEDS_FREE_SPACE` and `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` coordinate new block groups and rebuild transactions.

## Dependencies and Integration Points

The file integrates with Btrfs btree item accessors, global roots, transactions, extent roots, block-group cache trees, the runtime free-space cache loader, and mount feature flags. Direct includes are `messages.h`, `ctree.h`, `disk-io.h`, `locking.h`, `free-space-tree.h`, `transaction.h`, `block-group.h`, `fs.h`, `accessors.h`, `extent-tree.h`, and `root-tree.h`. It is called from extent allocation/free hooks, block-group creation/removal, mount-time block-group caching, and feature conversion/remount paths.

## Risks and Edge Cases

Extent count is the main consistency guard: conversion, loading, add, and remove paths all depend on maintaining accurate deltas when ranges merge or split. Bitmap conversion uses little-endian bit layout and sector-size granularity, so size and alignment bugs can corrupt free-space meaning. `btrfs_search_prev_slot()` intentionally expects no exact key match; callers depend on specific key ordering and can return `-EIO` on surprising tree shapes. Rebuild can allocate new block groups while modifying the free-space tree; `BLOCK_GROUP_FLAG_FREE_SPACE_ADDED` avoids duplicate population. The untrusted flag must be cleared only after commit, otherwise mount-time caching could rely on an incomplete tree. Extent tree v2 uses per-global-root lookup and skips orphan cleanup because a single global scan would be ambiguous.

## Test Signals

Coverage should include xfstests with `space_cache=v2`/free-space-tree enabled, online conversion between extent and bitmap forms, block-group create/delete while the tree is active, rebuild after marking the tree untrusted, mount/load verification after crash injection, and fsck/btrfs-check cross-validation of free-space totals. Sanity tests should directly cover `__btrfs_add_to_free_space_tree`, `__btrfs_remove_from_free_space_tree`, extent-to-bitmap and bitmap-to-extent conversion thresholds, bit tests at bitmap boundaries, orphan entry deletion, extent tree v2 root selection, and transaction abort behavior on corrupted key types or count mismatches.
