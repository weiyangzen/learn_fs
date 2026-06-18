# sources/distributed-fs/ceph-client/fs/xfs/xfs_trans_buf.c

## Purpose
`xfs_trans_buf.c` attaches metadata buffers to transactions, records which buffer byte ranges or semantic types must be logged, and controls buffer lifetime while transactions commit, cancel, or invalidate blocks.

## Important APIs, types, and functions
Important entry points are `xfs_trans_get_buf_map`, `xfs_trans_read_buf_map`, `xfs_trans_getsb`, `xfs_trans_getrtsb`, `xfs_trans_bjoin`, `xfs_trans_brelse`, `xfs_trans_bdetach`, `xfs_trans_bhold`, `xfs_trans_bhold_release`, `xfs_trans_dirty_buf`, `xfs_trans_log_buf`, `xfs_trans_binval`, `xfs_trans_inode_buf`, `xfs_trans_stale_inode_buf`, `xfs_trans_inode_alloc_buf`, `xfs_trans_ordered_buf`, `xfs_trans_buf_set_type`, `xfs_trans_buf_copy_type`, and `xfs_trans_dquot_buf`. It mainly manipulates `struct xfs_buf`, `struct xfs_buf_log_item`, and transaction item lists.

## Control flow
Buffer lookup first searches the transaction item list for an already joined buffer and increments `bli_recur` if found. New buffers are read or allocated through the buffer cache, initialized with a buf log item, refcounted, and joined to the transaction. Logging a buffer marks the transaction dirty, sets log item dirty state, and records byte ranges. Invalidating a buffer marks it stale, clears logged data maps, sets cancel flags for recovery, and keeps the item dirty until commit/cancel can safely resolve pins.

## State and persistence
Runtime state includes `bp->b_transp`, buffer lock recursion, log item refcounts, stale/hold/logged/ordered/inode-buffer flags, buffer iodone callbacks, and per-format dirty bitmaps. Persistent effects are journal records describing metadata buffer contents, cancellation records for freed buffers, and buffer type tags that guide log recovery.

## Dependencies and integration points
This code is the transaction-facing side of the XFS buffer cache and buf item subsystem. It integrates with metadata verifiers, shutdown handling, log recovery buffer type flags, inode and dquot buffer iodone callbacks, reflink/ordered buffer semantics, and quota buffer replay filtering.

## Risks and test signals
Risk areas include recursive buffer accounting, stale-buffer relogging, freeing clean log items too early, missing verifier errors on buffers already in a transaction, ordered buffer misuse after data ranges were logged, and recovery type flag mismatches. Test signals include repeated get/read of the same buffer in one transaction, dirty then brelse behavior, binval of pinned buffers, shutdown read paths, dquot/inode buffer recovery, and ordered-buffer assertions.
