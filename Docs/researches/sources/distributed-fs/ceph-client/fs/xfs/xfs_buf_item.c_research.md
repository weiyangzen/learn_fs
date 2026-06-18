# sources/distributed-fs/ceph-client/fs/xfs/xfs_buf_item.c

Purpose: Implements XFS buffer log items for dirty metadata buffers, including dirty-region bitmap tracking, CIL vector formatting, buffer pin/unpin lifetime, AIL push, and stale/cancelled buffer handling.

Important APIs, types, and functions: Defines `xfs_buf_item_cache` and log item ops. Public helpers are `xfs_buf_item_init()`, `xfs_buf_item_put()`, `xfs_buf_item_log()`, `xfs_buf_item_dirty_format()`, `xfs_buf_item_done()`, `xfs_buf_log_check_iovec()`, and `xfs_buf_inval_log_space()`. Internal code sizes and formats `xfs_buf_log_format` records, handles discontiguous buffer maps, and finishes stale items.

Control flow: Initialization attaches one format record per buffer map. Logging marks byte ranges in `XFS_BLF_CHUNK` bitmaps. Formatting emits a format record and contiguous dirty chunk iovecs, or only cancel records for stale buffers. Pinning holds both the BLI and buffer; unpin releases references, wakes waiters, finishes stale buffers, or routes aborted buffers through I/O failure. AIL push queues cleanly locked buffers for delayed writeback.

State and persistence: Persistent log state is the buffer log format plus dirty chunks. In-core state is `bli_flags`, refcount, format count, segment bitmaps, and the buffer attachment. Stale buffers persist `XFS_BLF_CANCEL`; inode buffers may carry `XFS_BLF_INODE_BUF` for restricted recovery.

Dependencies and integration points: Integrated with `xfs_trans`, CIL formatting, AIL writeback, buffer cache locks/refcounts, verifier precommit checks, inode/dquot iodone, log recovery cancel handling, and tracepoints.

Risks and test signals: Watch refcount races across unpin/AIL/shutdown, dirty bitmap off-by-ones, stale inode cleanup, ordered-buffer accounting, and verifier-triggered shutdown. Test discontiguous buffers, repeated relogging, forced shutdown during checkpoint completion, inode allocation/free recovery, quota buffers, and AIL pressure.
