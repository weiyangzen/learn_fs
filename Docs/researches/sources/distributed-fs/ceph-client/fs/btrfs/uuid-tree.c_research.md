# sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/uuid-tree.c` maintains the Btrfs UUID tree, an auxiliary metadata tree mapping subvolume UUIDs and received UUIDs to root object ids. It supports lookup consistency, send/receive and ioctl workflows, cleanup of stale mappings, and initial UUID tree creation/rescan. The file was read as a complete 566-line source file for this report.

## Important APIs, Types, and Functions

Public functions are `btrfs_uuid_tree_add()`, `btrfs_uuid_tree_remove()`, `btrfs_uuid_tree_check_overflow()`, `btrfs_uuid_tree_iterate()`, `btrfs_uuid_scan_kthread()`, and `btrfs_create_uuid_tree()`. Private helpers include `btrfs_uuid_to_key()`, `btrfs_uuid_tree_lookup()`, `btrfs_uuid_iter_rem()`, and `btrfs_check_uuid_tree_entry()`.

UUIDs are converted to Btrfs keys by interpreting the first and second 64-bit chunks as little-endian `objectid` and `offset`, with the supplied UUID item type as `key.type`. UUID-tree item payloads are arrays of little-endian `u64` subvolume ids.

## Control Flow

`btrfs_uuid_tree_add()` first checks whether the UUID/type/subid tuple already exists. If not, it inserts a new item containing one subid or extends an existing item and appends the subid. `btrfs_uuid_tree_remove()` searches with transaction intent, scans the item payload for the subid, deletes the whole item when it was the only entry, or memmoves following entries down and truncates the item.

`btrfs_uuid_tree_check_overflow()` searches an existing UUID item and returns `-EOVERFLOW` if appending one more subid would exceed the leaf data size. This allows ioctl paths to reject duplicate/overflow-prone received UUID operations before starting a modification that would later fail in the add path.

`btrfs_uuid_tree_iterate()` walks UUID-tree items forward, validates item sizes, reconstructs the UUID from the key, and checks every subid against the referenced subvolume root. Stale entries are removed in a short transaction, then the search restarts because the btree changed. `btrfs_uuid_scan_kthread()` walks the tree root for live root items, reads each root item, and adds non-empty normal and received UUIDs to the UUID tree in small transactions. `btrfs_create_uuid_tree()` creates the UUID tree, commits it, then starts the rescan kthread.

## State and Persistence Behavior

Unlike the other helper containers in this group, the UUID tree is persistent on-disk Btrfs metadata stored under `BTRFS_UUID_TREE_OBJECTID`. Items are keyed by UUID-derived key fields and type, and values are packed arrays of root ids. The code mutates this tree in normal Btrfs transactions and updates `fs_info->uuid_root`.

The scan thread is coordinated with `fs_info->uuid_tree_rescan_sem`, notices filesystem closing, and sets `BTRFS_FS_UPDATE_UUID_TREE_GEN` after a complete scan so generation tracking can be updated. Stale mapping removal is persistent and transaction-backed.

## Dependencies and Integration Points

This file uses Btrfs transaction, ctree search/insert/extend/truncate/delete helpers, path management, root lookup/reference handling, unaligned UUID helpers, kthreads, and fs closing checks. Callers include subvolume creation in `transaction.c`, UUID changes and received-subvolume handling in `ioctl.c`, root rename/exchange behavior in `inode.c`, and mount/open cleanup in `disk-io.c`.

## Risks and Edge Cases

UUID item sizes must be aligned to `sizeof(u64)`; malformed sizes are warned about and treated as missing/stale. Append operations can overflow a leaf, so callers should use the overflow check when user-visible operations need preflight validation. Removal performs in-item memmove and truncation, so offset and size arithmetic must remain exact. The iterate path intentionally restarts after deletion to avoid stale path state, which is correct but can be expensive if many stale entries exist.

The scan thread uses small transactions and must exit cleanly on filesystem closing. Failure to set or clear the rescan semaphore would block future scans. `btrfs_uuid_tree_lookup()` warns on missing `uuid_root`, so callers must only use the add/remove API after UUID tree creation or with filesystems that have the tree available.

## Test Signals

Useful tests include subvolume create/delete, snapshot, send/receive, setting received UUID, UUID collision and duplicate-subid scenarios, leaf-overflow preflight, mount-time UUID tree creation/rescan, stale-entry cleanup after deleted roots, and forced close during rescan. Corruption tests should cover misaligned UUID item sizes and missing referenced roots.
