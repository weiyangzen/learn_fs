# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.h

## Purpose
This header declares the fake-root structures and bulk-load interface for staged btree rebuilds.  It is the public contract between concrete repair/rebuild code and the staging implementation in `xfs_btree_staging.c`.

## Important APIs And Types
`struct xbtree_afakeroot` stores an AG-rooted staged tree's root AG block number, height, and block count.  `struct xbtree_ifakeroot` stores a fake inode fork pointer, block count, height, and available fork size for inode-rooted staged trees.  The stage/commit functions switch cursors between normal and fake-root operation.

The bulk-load callback types define caller responsibilities: `get_records` provides sorted records into a leaf block, `claim_block` hands out preallocated blocks, and `iroot_size` sizes inode root memory.  `struct xfs_btree_bload` carries callbacks, record count, slack settings, computed block count, final height, flush threshold, and dirty-buffer accounting.

## Control Flow And State
The expected flow is stage cursor, compute geometry, preallocate `nr_blocks`, bulk-load blocks, log owner metadata, and commit fake root.  The header encodes staged state shape but leaves concrete btree setup and root logging to callers.

## Dependencies, Risks, And Test Signals
This interface depends on generic btree cursors, XFS inode forks, transactions, and buffers.  Risks center on callback contracts and geometry agreement.  Tests should verify fake-root initialization, commit restoration of cursor fields, geometry outputs, and error handling for callbacks that fail partway through a load.
