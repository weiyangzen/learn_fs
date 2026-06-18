<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java

Purpose: functional tests for lazy-persist files on RAM_DISK, focusing on disallowed file operations, corrupt-file scrubbing, NameNode restart behavior, concurrent reads/writes, and volume-reference release when lazy persistence scheduling fails.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, `makeRandomTestFile`, `ensureFileReplicasOnStorageType`, `waitForRedundancyMonitorCycle`, `waitForScrubberCycle`, `waitForFile`, `waitForLowRedundancyCount`, `waitForCorruptBlock`, `triggerBlockReport`, `WriterRunnable`, `DataNodeTestUtils`, `FsDatasetImpl.asyncLazyPersistService`, and `FsDatasetSpi.FsVolumeReferences`.

Control flow: operation-denial tests create lazy-persist files and expect `append` or `truncate` to fail. Scrubber tests create a RAM_DISK lazy file, stop DataNodes, wait for NameNode corruption detection, and verify the lazy-persist scrubber either deletes the file or leaves it when disabled; a NameNode restart variant verifies the file is not discarded merely because the NameNode restarted. Concurrent read creates a seeded random RAM_DISK file and spawns multiple reader threads verifying contents. Concurrent write starts four writer tasks, each writing several lazy-persist files while eviction/lazy writer activity may run, then waits for completion. The reference-release test shuts down `asyncLazyPersistService`, records per-volume reference counts, writes a lazy file, waits through lazy-writer retries, and asserts reference counts do not grow unbounded.

State and persistence behavior: tests transient RAM_DISK replicas, lazy persisted disk copies, NameNode corrupt/low-redundancy state, scrubber deletion state, and `FsVolumeImpl` reference counts. Lazy persisted files should be discarded differently from normal corrupt files when replicas are lost.

Dependencies and integration points: depends on `LazyPersistTestCase` cluster configuration, DataNode lazy writer, NameNode redundancy monitor and scrubber, HDFS client append/truncate/create APIs, and block reports.

Risks: concurrency and timing are central; lazy-writer interval sleeps and scrubber cycles can be sensitive to runtime load. The reference-count assertion allows one extra reference because the lazy writer can keep retrying.

Test signals: failures catch illegal lazy-persist mutation acceptance, scrubber policy regressions, data corruption under concurrent RAM_DISK reads/writes, and leaked volume references on async service failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistFiles.java -->
