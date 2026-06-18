# File Research: sources/cow-pools/openzfs/module/zfs/range_tree.c

## Summary
Implements ZFS range trees: B-tree-backed interval sets used for free space and allocation-range tracking. It supports add/remove with automatic adjacent extent merging, extent splitting, traversal, clearing, swapping, and set-like XOR/remove-add operations.

## Main Responsibilities
- Creates and destroys range trees over `ZFS_RANGE_SEG32`, `ZFS_RANGE_SEG64`, and `ZFS_RANGE_SEG_GAP` segment encodings.
- Maintains total tracked space and a size histogram.
- Adds ranges by creating, extending, or merging segments.
- Removes ranges by deleting, shortening, or splitting segments.
- Supports gap-bridging trees with fill accounting for scan-style coalescing.
- Calls optional `zfs_range_tree_ops_t` hooks around create, destroy, add, remove, and vacate operations.

## Key APIs
- `zfs_range_tree_create()`, `zfs_range_tree_create_gap()`, `zfs_range_tree_create_flags()`, `zfs_range_tree_destroy()`.
- `zfs_range_tree_add()`, `zfs_range_tree_remove()`, `zfs_range_tree_remove_fill()`, `zfs_range_tree_resize_segment()`.
- `zfs_range_tree_find()`, `zfs_range_tree_contains()`, `zfs_range_tree_find_in()`, `zfs_range_tree_clear()`.
- `zfs_range_tree_walk()`, `zfs_range_tree_vacate()`, `zfs_range_tree_first()`.
- `zfs_range_tree_remove_xor_add_segment()`, `zfs_range_tree_remove_xor_add()`.
- `zfs_range_tree_space()`, `zfs_range_tree_numsegs()`, `zfs_range_tree_min()`, `zfs_range_tree_max()`, `zfs_range_tree_span()`.

## Important Behavior
Segments compare as non-overlapping intervals; overlap returns equality for B-tree lookup. Normal trees reject overlapping adds and missing removes with panic-recover diagnostics. Gap trees may merge nearby non-touching segments and track actual populated bytes through `fill`, but only support complete physical segment removal unless `zfs_range_tree_remove_fill()` can adjust fill.

`zfs_range_tree_vacate()` can either invoke a callback for every removed range while destroying B-tree nodes, or clear the tree directly. `zfs_range_tree_remove_xor_add_segment()` removes overlapping portions from one tree and adds uncovered portions to another.

## Risks
The implementation assumes callers provide external synchronization. Gap-tree semantics are stricter than normal interval trees; partial physical removes are illegal unless represented as fill changes. Callback users must tolerate remove/add callbacks around in-place segment resizing and fill adjustments.
