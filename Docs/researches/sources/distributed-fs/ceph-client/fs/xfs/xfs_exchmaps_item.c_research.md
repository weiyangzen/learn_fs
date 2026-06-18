# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchmaps_item.c

Purpose: Implements log intent/done items for atomic file mapping exchanges, including deferred operation integration, relogging, cancellation, and recovery of unfinished exchanges.

Important APIs, types, and functions: Defines `xfs_xmi_cache`, `xfs_xmd_cache`, XMI/XMD item ops, `xfs_exchmaps_defer_add()`, `xfs_exchmaps_defer_type`, and recovery ops `xlog_xmi_item_ops` and `xlog_xmd_item_ops`. Helpers create/release XMI and XMD items, finish/cancel deferred work, validate recovered formats, reconstruct recovery intents, and relog intents.

Control flow: XMI creation logs both inode numbers/generations, offsets, block count, sizes, and supported flags. XMD records completion and releases the XMI. Deferred finish calls `xfs_exchmaps_finish_one()` and retains on `-EAGAIN` for relogging. Recovery reconstructs XMI items, cancels them when matching XMDs appear, validates feature/flags/inodes/extents, reopens both inodes by generation, estimates resources, locks both inodes, ensures prerequisites, finishes the intent, and captures/commits deferred work.

State and persistence: Persistent log records are XMI redo and XMD done records. In-core XMI uses a two-reference lifecycle to handle commit/unpin versus done processing races.

Dependencies and integration points: Integrates with `xfs_defer`, exchange-range engines, bmap/reflink setup, inode recovery iget, transaction reservations, log recovery intent tracking, AIL matching, and tracepoints.

Risks and test signals: Risks include leaked or prematurely freed intents, stale inode generation replay, invalid flags/extents, two-inode locking deadlocks, log tail pinning, and incomplete crash recovery. Test crashes before/after XMD commit, generation mismatch, unsupported flags, large multi-transaction exchanges, reflink/extcount upgrades, and cancellation paths.
