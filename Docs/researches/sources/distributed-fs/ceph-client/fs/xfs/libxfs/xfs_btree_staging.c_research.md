# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_staging.c

## Purpose
This file implements staged btree construction and bulk loading.  It lets callers build a completely new AG-rooted or inode-rooted btree behind a fake root, using preallocated blocks, then atomically commit the new root into normal metadata.  This supports online repair and rebuild paths where a partially loaded tree must not become visible.

## Important APIs And Functions
`xfs_btree_stage_afakeroot` / `xfs_btree_commit_afakeroot` switch AG-rooted cursors into and out of staging mode.  `xfs_btree_stage_ifakeroot` / `xfs_btree_commit_ifakeroot` do the same for inode-rooted btrees.  `xfs_btree_bload_compute_geometry` calculates height and block count from record count, min/max geometry, root constraints, and slack.  `xfs_btree_bload` creates leaves and nodes, fills records, derives parent keys, links siblings, writes delayed buffers, and records fake-root state.

## Control Flow
A caller stages a cursor, configures `struct xfs_btree_bload`, computes geometry, preallocates all blocks, then calls `xfs_btree_bload`.  The loader fills leaf blocks from sorted `get_records` callbacks, remembers the leftmost child, then builds each node level by reading child blocks and copying child keys/pointers.  After the root level, fake-root fields are updated and dirty buffers are submitted.  Inode-rooted btrees recompute geometry to distinguish root capacity from normal block capacity and can allocate an in-core fake inode root.

## State And Persistence Behavior
Staging mode sets `XFS_BTREE_STAGING`, keeps construction transactionless, and redirects root storage to fake root structures.  Bulk loading uses a delayed-write buffer list and marks buffers uptodate before queuing them.  Callers must preallocate blocks and log owner metadata before commit functions convert the cursor back to normal operation.

## Dependencies And Integration Points
This file relies on generic btree layout helpers, block initialization, sibling setters, key derivation, buffer read/get helpers, delayed-write APIs, and tree-specific bulk-load callbacks.  It integrates with repair flows and with `xfs_btree.c` guardrails that reject normal allocation/freeing for staging cursors.

## Risks And Test Signals
Risks include unsorted records, wrong preallocation counts, bad slack, dirty buffer submission failures, inode root capacity miscalculation, and exposing fake-root state too early.  Tests should cover zero records, single-root trees, multi-level trees, uneven distribution, dirty threshold flushing, callback failures, and post-build sibling/key verification.
