# sources/distributed-fs/ceph-client/fs/btrfs/orphan.c

## Purpose
`orphan.c` provides the minimal helpers for inserting and deleting Btrfs orphan items. Orphan items record objectids that need cleanup after unlink/truncate/crash recovery. The source was read as a complete 48-line file.

## Important APIs, Types, and Functions
The file exports `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()`. Both construct a key with `objectid = BTRFS_ORPHAN_OBJECTID`, `type = BTRFS_ORPHAN_ITEM_KEY`, and caller-provided `offset`.

## Control Flow
Insertion allocates a path and calls `btrfs_insert_empty_item()` with zero item size. Deletion allocates a path, searches with modification intent (`ins_len = -1`, cow allowed), returns search errors or `-ENOENT` if absent, and deletes the found item with `btrfs_del_item()`.

## State and Persistence Behavior
The helpers mutate persistent B-tree items inside the provided root and transaction. There is no local runtime state beyond the temporary path and key. Orphan cleanup elsewhere consumes these records after mount or subvolume lookup.

## Dependencies and Integration Points
The file depends on `ctree.h` for B-tree path/key/item operations and `orphan.h` for declarations. It is used by inode lifecycle and orphan cleanup code.

## Risks and Edge Cases
Callers must provide a valid transaction and root and reserve enough metadata. Deleting a missing orphan reports `-ENOENT`; callers must decide whether that is expected. Since item size is zero, the key is the entire persistent payload.

## Test Signals
Signals include orphan insert/delete round trips, mount recovery after crash with orphan items, deletion of absent items, allocation failure for `btrfs_alloc_path()`, and transaction abort handling in callers.
