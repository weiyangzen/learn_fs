# sources/distributed-fs/ceph/src/mds/PurgeQueue.h

Purpose: declares `PurgeItem`, `PurgeItemCommitOp`, perf counter IDs, and `PurgeQueue`, the durable asynchronous deletion engine for strays and truncations.

Important APIs and types: `PurgeItem` contains `Action` (`NONE`, `PURGE_FILE`, `TRUNCATE_FILE`, `PURGE_DIR`), inode number, size, file layout, old pools, snap context, fragment tree, timestamp, and padding for journal splicing. `PurgeItemCommitOp` captures concrete `Filer` or `Objecter` operations. `PurgeQueue` exposes lifecycle (`init`, `activate`, `shutdown`, `create`, `open`), recovery waiters, `push()`, `drain()`, idle check, and config/map update hooks.

State and persistence: the class owns its own `Finisher`, `SafeTimer`, `Filer`, and `Journaler`, explicitly avoiding `MDSDaemon::mds_lock`. Persistent queue entries live in the Journaler; in-memory state tracks in-flight offsets, pending expiration offsets, throttle counters, delayed flushes, recovery completion, readonly mode, and journal item sizing.

Dependencies and integration: depends on Ceph context/config, `MDSMap`, `Objecter`, metadata pool id, `Journaler`, and the caller-provided `on_error` context. The header documents that there is one queue per MDS rank and that persistence completion is reported to submitters, not eventual deletion completion.

Risks and test signals: public callers must wait for recovery before pushing and must tolerate `-EROFS` after internal I/O failure. `drain()` intentionally raises `max_purge_ops` to finish quickly, so drain tests should check progress accounting and no lost expire positions. Encoding tests should include `PurgeItem` v1/v2, `NONE` padding, and all action variants.
