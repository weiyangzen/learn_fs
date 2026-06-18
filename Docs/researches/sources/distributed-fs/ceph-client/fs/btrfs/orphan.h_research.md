# sources/distributed-fs/ceph-client/fs/btrfs/orphan.h

## Purpose
`orphan.h` declares the Btrfs orphan-item insertion and deletion helpers. The source was read as a complete 16-line header.

## Important APIs, Types, and Functions
It forward-declares `struct btrfs_trans_handle` and `struct btrfs_root`, and declares `btrfs_insert_orphan_item()` and `btrfs_del_orphan_item()` with a transaction, root, and u64 offset.

## Control Flow
There is no runtime flow in the header. Callers include it to create or remove zero-length `BTRFS_ORPHAN_ITEM_KEY` records through `orphan.c`.

## State and Persistence Behavior
The header defines no state. The declared functions mutate persistent orphan items in Btrfs trees.

## Dependencies and Integration Points
It includes `<linux/types.h>` for `u64` and integrates with Btrfs inode lifecycle, truncate/unlink, and orphan cleanup paths.

## Risks and Edge Cases
The small API hides required transaction reservation and caller policy for missing items. Prototype drift would break orphan cleanup users.

## Test Signals
Build coverage plus orphan recovery tests validate the header and implementation contract.
