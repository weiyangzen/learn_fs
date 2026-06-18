# sources/distributed-fs/ceph/src/mds/RecoveryQueue.h

Purpose: declares `RecoveryQueue`, the MDCache helper that schedules file size recovery probes for authoritative inodes.

Important APIs and types: public methods are `enqueue(CInode*)`, `advance()`, `prioritize(CInode*)`, and `set_logger()`. Private callbacks `_start()` and `_recovered()` are used by the `C_MDC_Recover` I/O context in the implementation.

State and persistence: the class owns two intrusive `elist<CInode*>` queues, normal and priority, size counters, a map of active recoveries to restart flags, an `MDSRank*`, optional perf counter logger, and a `Filer`. There is no persistent journal or disk state.

Dependencies and integration: depends on `include/elist.h`, `Filer`, `CInode`, `MDSRank`, and perf counters. It relies on `CInode` list items `item_dirty_dirfrag_dir` and `item_dirty_dirfrag_nest` as queue hooks.

Risks and test signals: correctness depends on each inode being on at most one queue and on active recoveries being represented in `file_recovering`. Tests should assert list membership transitions, logger initialization before enqueue, and `prioritize()` behavior when the inode is already active or not queued.
