<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java

Purpose: slow, non-thread-safe tests for the normal locked-memory `FsDatasetCache` path. The file validates cache/uncache commands, retry behavior, page-size accounting, capacity failures, cancellation, unknown uncache handling, quiescence, and recaching after space is freed.

Important APIs/types/functions: `FsDatasetSpi`, `FsDatasetCache`, `CacheStats.PageRounder`, `DatanodeProtocolClientSideTranslatorPB`, `BlockIdCommand`, `DatanodeProtocol.DNA_CACHE`, `DNA_UNCACHE`, `NativeIO.POSIX.CacheManipulator`, `NoMlockCacheManipulator`, helper methods `setHeartbeatResponse`, `cacheBlocks`, `uncacheBlocks`, `getResponse`, `getBlockSizes`, and `testCacheAndUncacheBlock`.

Control flow: setup creates a one-DataNode cluster with cache capacity equal to typical locked-memory limits, page-sized block size, fast cache reports, and a spied NameNode protocol translator. The fault injector pauses BPServiceActor heartbeat work while tests replace heartbeat responses with synthetic cache/uncache commands. `testCacheAndUncacheBlock` writes five blocks, sends one cache command at a time, waits for expected used bytes and cached block count, then uncache commands each block. Other tests replace `mlock` to fail once then succeed, fill capacity with multiple files and assert failure log/metrics, uncache while `mlock` sleeps, uncache a never-cached block, verify small blocks round up to OS page size, ensure directive removal emits no extra cache operations, and verify a small directive gets cached after a full-cache file is uncached.

State and persistence behavior: state is volatile locked-memory accounting in `FsDatasetSpi`/`FsDatasetCache`, DataNode metrics counters, and NameNode cache directive stats. No PMEM or durable cache state is expected. Cleanup asserts cache usage returns to zero to avoid descriptor leaks.

Dependencies and integration points: integrates DataNode heartbeats, cache directives, DFS block readers, file-channel block size inspection, root log capture, NameNode FSImage transaction ID for heartbeat responses, and native cache manipulator abstraction.

Risks: timing-heavy waits and injected sleeping `mlock` can be flaky on overloaded hosts. Root logger appender matching a message substring couples the test to error text. Tests assume page rounding and configured cache capacity align with file layout.

Test signals: failures catch regressions in cache command idempotence, cache space reservation rollback, retry semantics, cancellation cleanup, metrics counters, and NameNode directive recache behavior after HDFS-6107-style pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestFsDatasetCache.java -->
