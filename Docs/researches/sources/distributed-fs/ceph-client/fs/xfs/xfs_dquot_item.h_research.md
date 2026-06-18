# sources/distributed-fs/ceph-client/fs/xfs/xfs_dquot_item.h

Purpose: Declares the in-core dquot log item that connects an XFS dquot to transaction logging and AIL flush state.

Important APIs, types, and functions: Defines `struct xfs_dq_logitem` with common `xfs_log_item`, `xfs_dquot` back pointer, `qli_flush_lsn`, `qli_lock`, and `qli_dirty`. Declares `xfs_qm_dquot_logitem_init()`.

Control flow: Initialized with each dquot and then used by transaction code for logging and by flush iodone for AIL cleanup.

State and persistence: Stores transient flush LSN and dirty/attached-buffer coordination state; persistent payload is emitted by `xfs_dquot_item.c`.

Dependencies and integration points: Included by dquot, quota transaction, and log item code.

Risks and test signals: Risks are races around `qli_dirty` and `li_buf` if callers bypass `qli_lock`. Test relogging while dqflush I/O is active.
