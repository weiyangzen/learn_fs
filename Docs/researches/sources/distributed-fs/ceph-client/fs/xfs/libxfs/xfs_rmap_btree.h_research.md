# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rmap_btree.h

## Purpose
`xfs_rmap_btree.h` declares the reverse mapping btree block layout macros and cursor/geometry functions for on-disk and in-memory rmap btrees.

## Important APIs and layout
`XFS_RMAP_BLOCK_LEN` is the v5 short btree header length. `XFS_RMAP_REC_ADDR`, `XFS_RMAP_KEY_ADDR`, `XFS_RMAP_HIGH_KEY_ADDR`, and `XFS_RMAP_PTR_ADDR` address records, low keys, high keys, and pointers in a block. The two-key-per-pointer layout reflects overlapping btree geometry. Public functions cover cursor creation, staged commit, max record counts, mount maxlevel computation, size/reserve calculation, cursor-cache lifecycle, and in-memory btree cursor/init helpers.

## Control flow and state
The header supports normal rmapbt mutation, mount-time geometry setup, online repair staging, and memory-backed rmap indexes. Persistent state remains rooted in AGF fields, while the macros define exact on-disk block offsets that kernel and userspace libxfs code must share.

## Dependencies, risks, and test signals
The declarations depend on generic btree, mount, transaction, perag, staged fake-root, and `xfbtree` types. Risks are layout drift and incorrect handling of overlapping high-key storage. Tests should validate block layout calculations, in-memory cursor availability under config gates, and staged-tree callers.
