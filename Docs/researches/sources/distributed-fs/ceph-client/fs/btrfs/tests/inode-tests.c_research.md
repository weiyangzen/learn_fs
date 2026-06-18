# sources/distributed-fs/ceph-client/fs/btrfs/tests/inode-tests.c

## Purpose

`inode-tests.c` validates Btrfs inode extent lookup and outstanding delalloc extent accounting. It constructs synthetic file extent items that cover inline extents, holes, regular extents, prealloc extents, split extents, compressed extents, and implied holes, then checks `btrfs_get_extent()` output.

## Important APIs, Types, And Functions

- `insert_extent()` inserts a `BTRFS_EXTENT_DATA_KEY` item into a dummy leaf and initializes a `btrfs_file_extent_item`.
- `insert_inode_item_key()` inserts a minimal inode item key used by the hole-first test.
- `setup_file_extents()` builds a complex synthetic extent layout covering inline data, explicit and implied holes, regular/prealloc/compressed extents, and split extents with offsets.
- `test_btrfs_get_extent()` walks through the synthetic layout and validates `struct extent_map` fields returned by `btrfs_get_extent()`.
- `test_hole_first()` validates a file whose first range is an implied hole before a real extent.
- `test_extent_accounting()` validates `BTRFS_I(inode)->outstanding_extents` while setting, clearing, splitting, merging, and refilling delalloc ranges.
- `btrfs_test_inodes()` initializes expected flag masks and runs the three groups.

## Control Flow

`test_btrfs_get_extent()` creates a dummy inode/fs/root/leaf, first confirms that an empty tree returns a hole, then populates the leaf with `setup_file_extents()`. It calls `btrfs_get_extent()` sequentially from offset to offset, verifying each returned extent map’s `disk_bytenr`, `start`, `len`, flags, offset, block start, and compression type.

`test_hole_first()` inserts a blank inode item and one regular extent starting at `sectorsize`, then verifies a hole for `[0, sectorsize)` and a real extent after it. `test_extent_accounting()` mutates the inode `io_tree` with `btrfs_set_extent_delalloc()` and `btrfs_clear_extent_bit()` and validates outstanding extent counts after each split/merge shape.

## State And Persistence Behavior

The tests use a dummy inode root and in-memory extent buffer as the subvolume tree leaf. Extent maps are allocated and freed in memory; no disk persistence occurs. Delalloc accounting state lives in the inode’s `io_tree` and `outstanding_extents` counter and is cleared on failure and at the end.

## Dependencies And Integration Points

This file depends on Btrfs file extent item accessors, `btrfs_get_extent()`, compression flags, extent-map helpers, dummy inode/root/fs allocation, extent I/O tree delalloc helpers, and Btrfs inode accounting. It protects read path mapping and writeback reservation accounting behavior.

## Risks

The expected values are tightly coupled to the synthetic layout in `setup_file_extents()`, as the file comments warn. The tests are broad for mapping types but still single-leaf and single-threaded. The global static expected flag masks are updated with `|=`, so repeated invocations rely on idempotent bit setting.

## Test Signals

Failures report the exact unexpected extent-map field, compression type, flags, block start, or outstanding extent count. A zero return from `btrfs_test_inodes()` means extent lookup and delalloc accounting passed for the requested sectorsize/nodesize.
