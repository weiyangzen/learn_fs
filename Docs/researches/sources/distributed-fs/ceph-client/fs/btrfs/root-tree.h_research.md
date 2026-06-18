# sources/distributed-fs/ceph-client/fs/btrfs/root-tree.h

## Purpose
`root-tree.h` declares the root tree API for Btrfs modules that create, find, update, delete, reference, orphan-clean, and reserve metadata for roots. It is the public interface for the implementation in `root-tree.c`.

## Important APIs, Types, and Functions
The declarations expose `btrfs_find_root`, `btrfs_insert_root`, `btrfs_update_root`, `btrfs_del_root`, `btrfs_add_root_ref`, `btrfs_del_root_ref`, `btrfs_find_orphan_roots`, `btrfs_set_root_node`, `btrfs_check_and_init_root_item`, `btrfs_update_root_times`, and `btrfs_subvolume_reserve_metadata`.

The header forward-declares `fscrypt_str`, `extent_buffer`, `btrfs_key`, `btrfs_root`, `btrfs_root_item`, `btrfs_path`, `btrfs_fs_info`, `btrfs_block_rsv`, and `btrfs_trans_handle`, keeping callers decoupled from full structure definitions when only pointer types are needed.

## Control Flow
Callers use this API inside transaction-backed workflows. Root creation usually reserves metadata, fills a root item, calls `btrfs_insert_root`, and adds root refs if the root is linked into a parent. Root updates copy a live root node into the root item with `btrfs_set_root_node` and persist it with `btrfs_update_root`. Subvolume deletion or orphan cleanup removes refs with `btrfs_del_root_ref`, deletes root items with `btrfs_del_root`, and discovers incomplete deletions with `btrfs_find_orphan_roots`. Mount/open paths call `btrfs_check_and_init_root_item` to normalize legacy fields, and transaction paths call `btrfs_update_root_times` when root metadata changes.

## State and Persistence
The header has no state, but its functions operate on persistent tree-root records: root items, root refs/backrefs, orphan items, and root item time/generation fields. `btrfs_subvolume_reserve_metadata` operates on in-memory block reservations and qgroup counters that protect later persistent modifications.

## Dependencies and Integration Points
`root-tree.h` is included by relocation, transaction, disk I/O/root loading, subvolume, snapshot, orphan cleanup, and quota-related code. It depends only on Linux types plus forward declarations, allowing broad use without forcing every caller to include full root-tree implementation details.

## Risks and Edge Cases
Most functions require the caller to pass the correct tree root, transaction, and writable path context. Ref operations must be called in pairs consistent with directory entries or the root tree can retain dangling forward/back references. `btrfs_find_root` can return positive miss, zero found, or negative error; callers must not collapse positive miss into success. Metadata reservation callers must free or transfer qgroup reservation state consistently on later failure paths.

## Test Signals
Build coverage should verify all root-tree consumers compile through forward declarations. Behavioral tests should exercise root insert/update/delete, exact and inexact root lookup, root ref/backref pairing, orphan root scan at mount, legacy root item initialization, root timestamp persistence, and qgroup/global-reservation behavior during subvolume and snapshot operations.
