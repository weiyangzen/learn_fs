# sources/distributed-fs/ceph-client/fs/btrfs/tests/free-space-tree-tests.c

## Purpose

`free-space-tree-tests.c` validates the on-tree free-space representation used by Btrfs free-space-tree support. It tests adding, removing, merging, format conversion between extent items and bitmap items, and complete cleanup for a dummy block group.

## Important APIs, Types, And Functions

- `struct free_space_extent` encodes expected free ranges.
- `__check_free_space_extents()` inspects the free-space tree item layout directly, handling both extent-item and bitmap formats.
- `check_free_space_extents()` checks current format, converts to the opposite format with `btrfs_convert_free_space_to_extents()` or `btrfs_convert_free_space_to_bitmaps()`, and checks again.
- Test cases include `test_empty_block_group()`, `test_remove_all()`, `test_remove_beginning()`, `test_remove_end()`, `test_remove_middle()`, `test_merge_left()`, `test_merge_right()`, `test_merge_both()`, and `test_merge_none()`.
- `run_test()` builds a dummy free-space-tree root, dummy block group, dummy transaction/path, and runs one case in either extent or bitmap initial format.
- `run_test_both_formats()` executes each case in both representations.
- `btrfs_test_free_space_tree()` runs all cases with sectorsize alignment and a page-based bitmap alignment.

## Control Flow

Each `run_test()` creates a dummy fs/root, enables the free-space-tree compat-ro flag, sets the root as `BTRFS_FREE_SPACE_TREE_OBJECTID`, allocates a single leaf, creates a dummy block group of `8 * alignment`, marks it as needing free-space population, and adds block-group free space. If requested, it converts the representation to bitmaps before running the test.

The individual test mutates the free-space tree through `__btrfs_remove_from_free_space_tree()` or `__btrfs_add_to_free_space_tree()`, then validates expected ranges. After each case, the block group free-space items are removed and the root leaf is expected to have zero items.

## State And Persistence Behavior

State is in a dummy Btree leaf representing the free-space tree and a dummy block group. Although the APIs are production tree-modification helpers, the tree is not persisted to disk. The tests explicitly check both logical free ranges and physical item cleanup.

## Dependencies And Integration Points

The file integrates with Btrfs ctree item accessors, free-space-tree search/add/remove/convert helpers, transaction handle scaffolding, block group state, path allocation, and dummy extent buffers. It protects code used by filesystems with `BTRFS_FEATURE_COMPAT_RO_FREE_SPACE_TREE`.

## Risks

The direct tree inspection is tightly coupled to free-space-tree item layout. Format conversion is checked, which is valuable but means changes to bitmap sizing or item ordering require test updates. The dummy tree is single-leaf, so it does not cover multi-leaf split/merge behavior.

## Test Signals

Failures report missing free-space info, wrong extent counts, invalid tree item layout, conversion failures, leftover free-space-tree items, or case-specific failures annotated with function pointer, representation, sectorsize, nodesize, and alignment.
