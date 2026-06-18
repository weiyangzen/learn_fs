# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/LocatedBlocksRefresher.java

`LocatedBlocksRefresher` is a client-context daemon that periodically refreshes cached `LocatedBlocks` for registered `DFSInputStream`s, mainly streams with dead nodes or missing local replicas.

Its APIs are `addInputStream()`, `removeInputStream()`, `isInputStreamTracked()`, `shutdown()`, `getRunCount()`, `getRefreshCount()`, and `getInterval()`. Internals include jittered `waitForInterval()` and synchronized snapshotting of registered streams.

Construction reads the configured interval and thread count, creates a daemon pool with context-specific thread names, and names the main thread. `work()` sleeps for interval plus +/-10% jitter, snapshots weakly registered streams, shares an address cache, submits refresh tasks, waits through a `Phaser`, then updates run and refresh counters. Each task verifies the stream remains tracked before calling `DFSInputStream.refreshBlockLocations()`.

State is process-local: weakly referenced input streams, executor, counters, interval/jitter, and per-pass address cache. Dependencies include `DfsClientConf`, HDFS refresh config keys, `DFSInputStream`, `Daemon.DaemonFactory`, `Phaser`, `ThreadLocalRandom`, and `Time`.

Risks include invalid jitter bounds if a zero interval daemon is started, weak references disappearing between passes, shutdown without awaiting worker-pool termination, and skipped additions/removals during snapshot windows. Test signals include registration/removal, tracked checks, interrupt handling, refresh counters, skipped removed streams, shared address cache, thread naming, and shutdown.
