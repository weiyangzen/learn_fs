# sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/free-space-tree.h` declares the public interface and bitmap sizing constants for the Btrfs persistent free-space tree. It is consumed by extent allocation/free paths, block-group lifecycle code, mount-time cache loading, and feature-management paths. The file was read as a complete 62-line header.

## Important APIs, Types, and Functions

The header defines `BTRFS_FREE_SPACE_BITMAP_SIZE` as the default 256-byte bitmap payload size and `BTRFS_FREE_SPACE_BITMAP_BITS` as its bit capacity. Public APIs declare threshold calculation, create/delete/rebuild lifecycle operations, free-space tree loading, block-group add/remove hooks, range add/remove hooks, orphan cleanup, free-space info search, and root selection. Under `CONFIG_BTRFS_FS_RUN_SANITY_TESTS`, it exposes internal add/remove and conversion helpers plus `btrfs_free_space_test_bit`.

## Control Flow

The header shapes three flows: feature lifecycle (`btrfs_create_free_space_tree`, `btrfs_delete_free_space_tree`, `btrfs_rebuild_free_space_tree`), normal transaction updates (`btrfs_add_to_free_space_tree`, `btrfs_remove_from_free_space_tree`, block-group add/remove hooks), and mount-time load (`btrfs_load_free_space_tree`). `btrfs_search_free_space_info()` and `btrfs_free_space_root()` are utility entry points shared across those flows.

## State and Persistence Behavior

The constants define the default granularity for newly created bitmap items, but callers must not assume every existing bitmap has that exact size because the last bitmap in a block group can be truncated. The persisted state itself is held in free-space tree btree items, not in this header. The APIs take transaction handles and paths where mutation or COW may be required.

## Dependencies and Integration Points

The header includes `linux/bits.h` for bit sizing and forward declares `btrfs_caching_control`, `btrfs_fs_info`, `btrfs_path`, `btrfs_block_group`, and `btrfs_trans_handle`. Integration points are block-group threshold setup, transaction-time extent accounting, free-space tree feature toggles, and sanity tests that need internal conversion behavior.

## Risks and Edge Cases

The bitmap size constants are defaults rather than universal invariants; code that assumes fixed bitmap item size would mishandle truncated tail bitmaps. The add/remove APIs are no-ops when the compat-ro feature is not active, so callers must not assume persistent free-space-tree state exists on every filesystem. Sanity-test exports expose internals and should not become de facto production APIs.

## Test Signals

Compile coverage should validate declarations against `free-space-tree.c` and call sites. Runtime tests should cover feature enable/disable/rebuild, threshold conversion, truncated final bitmap items, and sanity-test helpers when `CONFIG_BTRFS_FS_RUN_SANITY_TESTS` is enabled.
