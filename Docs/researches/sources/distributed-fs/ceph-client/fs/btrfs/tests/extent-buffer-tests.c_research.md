# sources/distributed-fs/ceph-client/fs/btrfs/tests/extent-buffer-tests.c

## Purpose

`extent-buffer-tests.c` validates item splitting inside a Btrfs leaf extent buffer. It focuses on `btrfs_split_item()` preserving keys, item sizes, data contents, and slot ordering when a leaf item is split once and then split again with item movement.

## Important APIs, Types, And Functions

- `test_btrfs_split_item()` builds a dummy root, path, and extent buffer, inserts a checksum item containing `"mary had a little lamb"`, then splits it into expected string fragments.
- `btrfs_setup_item_for_insert()`, `write_extent_buffer()`, `read_extent_buffer()`, `btrfs_split_item()`, `btrfs_item_key_to_cpu()`, `btrfs_item_size()`, and `btrfs_item_ptr_offset()` are the production helpers under inspection.
- `btrfs_test_extent_buffer_operations()` is the exported selftest entry point.

## Control Flow

The test creates a single-node dummy tree with one item at slot 0. It splits the item at offset 17 with a new key offset of 3 and verifies two slots. It then splits slot 0 again at offset 4 with a new key offset of 1 and verifies three slots, including the item movement of the prior second fragment.

## State And Persistence Behavior

All state is in a dummy extent buffer and dummy root. Passing a `NULL` transaction handle is valid here because the tree is a single test leaf with enough room and no real persistence or COW path is needed.

## Dependencies And Integration Points

The test depends on dummy fs/root/path allocation, extent buffer allocation, Btrfs item layout accessors, and core ctree item manipulation. It indirectly protects code used by metadata updates that split leaf items.

## Risks

The test uses fixed string data and one item type, so it checks byte movement and slot metadata but not all item sizes or leaf-boundary conditions. It assumes `btrfs_split_item()` can safely run with `NULL` transaction in this constrained dummy setup.

## Test Signals

Failures report invalid keys, lengths, split return codes, or mismatched data fragments. A zero return from `btrfs_test_extent_buffer_operations()` means the split scenarios passed.
