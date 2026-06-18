# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-map-tests.c

## Purpose

`extent-map-tests.c` validates the Btrfs in-memory extent map tree. It covers overlap handling in `btrfs_add_extent_mapping()`, dropping/splitting ranges, pinned compressed extents, compressed offset adjustment, reverse physical-to-logical mapping, and extent-map reference cleanup.

## Important APIs, Types, And Functions

- `free_extent_map_tree()` removes all mappings from a Btrfs inode and, under debug builds, checks extent-map reference counts.
- `test_case_1()` through `test_case_4()` simulate concurrent buffered/direct I/O races where adding an extent map collides with an existing broader or split mapping and should return a usable existing/adjusted map rather than fail.
- `add_compressed_extent()` inserts compressed mappings that do not merge.
- `valid_ranges[][]` and `validate_range()` define expected extent-map tree state after range drops.
- `test_case_5()` validates `btrfs_drop_extent_map_range()` front, back, double split, and full-drop behavior.
- `test_case_6()` checks that add-gap logic does not create an unwanted bridging map when adjacent unmerged maps exist.
- `test_case_7()` is a regression test for `skip_pinned=true` drop logic.
- `test_case_8()` is a regression test for compressed extent offset adjustment after partial overlap.
- `struct rmap_test_vector`, `test_rmap_block()`, and `btrfs_test_extent_map()` validate `btrfs_rmap_block()` using dummy chunk maps/devices.

## Control Flow

The entry point allocates a dummy 4 KiB `fs_info`, dummy inode, and dummy root, assigns the root to the inode, and runs eight extent-map cases. Each case builds a specific map layout, calls the production operation, inspects returned maps or rb-tree contents, and then frees the tree. After extent-map cases, it runs reverse mapping vectors by building chunk maps with dummy devices, adding them to the mapping tree, calling `btrfs_rmap_block()` for a superblock physical offset, and checking logical outputs.

## State And Persistence Behavior

State is in `BTRFS_I(inode)->extent_tree`, chunk mapping trees, and dummy device lists. No disk is touched. Extent maps use reference counting, pinned flags, compressed flags, offsets, disk byte ranges, and rb-tree nodes, so cleanup is part of the correctness check.

## Dependencies And Integration Points

The tests depend on Btrfs inode extent-map APIs, chunk map allocation and mapping-tree insertion/removal, dummy device allocation, block-group/volume definitions, and rb-tree locking around extent-map operations. They protect behavior used by buffered reads, direct I/O, encoded writes, compressed extents, and device superblock scanning.

## Risks

Many cases encode historical race/regression scenarios. They are single-threaded simulations of concurrent outcomes, so they validate final-state logic but not locking races themselves. Fixed 4 KiB assumptions in the extent-map runner are intentional because the hard-coded extents are based on 4 KiB units.

## Test Signals

Failures report unexpected return codes, wrong returned extent map ranges, missing or extra rb-tree entries, wrong block starts/offsets, leaked refs under debug, or incorrect reverse-mapped logical addresses.
