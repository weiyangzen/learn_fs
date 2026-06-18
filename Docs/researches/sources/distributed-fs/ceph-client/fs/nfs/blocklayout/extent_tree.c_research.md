# sources/distributed-fs/ceph-client/fs/nfs/blocklayout/extent_tree.c

## Purpose
This file maintains the pNFS block layout extent trees. It stores read-only and read-write extents in red-black trees, supports overlap-safe insertion/removal/splitting/merging, tracks written invalid extents, and encodes layoutcommit updates for block and SCSI layouts.

## Important APIs, types, and functions
External entry points are `ext_tree_insert()`, `ext_tree_lookup()`, `ext_tree_remove()`, `ext_tree_mark_written()`, `ext_tree_prepare_commit()`, and `ext_tree_mark_committed()`. The code manipulates `struct pnfs_block_layout` roots `bl_ext_ro` and `bl_ext_rw`, `struct pnfs_block_extent` nodes, and `bl_lwb` last-written-byte state.

Important helpers include `__ext_tree_search()`, `__ext_tree_insert()`, `__ext_tree_remove()`, `ext_tree_split()`, `ext_can_merge()`, `ext_try_to_merge_left()`, and `ext_try_to_merge_right()`. Commit encoding is handled by `ext_tree_try_encode_commit()`, `ext_tree_encode_commit()`, `encode_block_extent()`, and `encode_scsi_range()`.

## Control flow
Insertion chooses the RO or RW tree based on extent state, locks `bl_ext_lock`, searches for overlap, and inserts only uncovered ranges while trimming or splitting the new extent around existing nodes. Removal searches the first covered node, trims left and/or right remnants, moves fully removed nodes to a temporary list, then drops deviceid references after the spinlock is released.

When writes complete, `ext_tree_mark_written()` removes COW/hole extents from the RO tree, splits invalid RW extents to the exact written range, tags them `EXTENT_WRITTEN`, merges adjacent compatible ranges, and advances `bl_lwb`. Layoutcommit preparation first tries a page-sized buffer that must fit all written extents. If it cannot, it allocates up to `server->wsize` and encodes as many extents as possible, tagging them `EXTENT_COMMITTING`. `ext_tree_mark_committed()` either reverts committing extents to written on RPC failure or promotes them to read-write data on success.

## State and persistence behavior
All state is volatile in the layout header. The durable server-visible transition happens through encoded layoutcommit payloads. Extents hold deviceid references and must drop them when removed or merged away. Commit state tags implement a small state machine: invalid and uncommitted, written, committing, then read-write data after successful layoutcommit.

## Dependencies and integration points
The file depends on Linux rbtree/list/vmalloc/page APIs, NFS layoutcommit structures, blocklayout-private types, XDR encoding, and pNFS deviceid reference helpers. It integrates with the block layout read/write path for lookup and write completion, and with NFS layoutcommit RPC assembly through `nfs4_layoutcommit_args`.

## Risks and test signals
Main risks are off-by-one sector ranges, failing to adjust virtual offsets during splits, leaking or over-dropping deviceid references, commit buffer overflow, and invalid `lastbytewritten` when partial commits are encoded. Test signals should include overlapping layout segments, adjacent merge cases, hole/COW removal, partial commit under small `wsize`, RPC-failure retry paths, and lockdep/KASAN coverage around spinlocked tree mutation.
