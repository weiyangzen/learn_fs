# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestMetaSave.java

## Purpose
Integration tests for NameNode `metaSave` output generation, including live/dead DataNode summaries, under-replication/delete queues, overwrite semantics, and concurrent calls to the same output file.

## Important APIs, Types, and Functions
- Exercises `NamenodeProtocols.metaSave`, `setReplication`, and `delete`.
- Uses `MiniDFSCluster`, `FileSystem`, `DFSTestUtil.createFile`, `BlockManagerTestUtil.noticeDeadDatanode`, `isDatanodeRemoved`, and `waitForMarkedDeleteQueueIsEmpty`.
- Reads output files from `System.getProperty("hadoop.log.dir")`.
- `MetaSaveThread` extends `SubjectInheritingThread` and invokes `metaSave` concurrently.

## Control Flow
- `setUp` starts a two-DataNode cluster with long redundancy interval, short heartbeat/recheck interval, and stale DataNode interval.
- `testMetaSave` creates replicated files, stops one DataNode, increases replication for one file, runs `metaSave`, and validates exact header/live/dead lines plus a file-status line.
- `testMetasaveAfterDelete` creates files, stops a DataNode, sets replication, deletes files, waits for delete queue drain, and checks metasave output for zero reconstruction/missing counts and deletion/corrupt/datanode sections.
- `testMetaSaveOverwrite` calls `metaSave` twice on the same file and asserts only one `Live Datanodes` line exists.
- `testConcurrentMetaSave` starts 10 threads writing the same metasave file and applies the same non-append check.
- `stopDatanodeAndWait` stops a DataNode, notifies NameNode, and waits until it is removed.

## State and Persistence Behavior
- `metaSave` writes diagnostic files in the Hadoop log directory and should overwrite rather than append.
- Cluster state includes dead DataNode detection, replication changes, pending deletions, and block manager queues.
- Concurrent output exercises file write serialization/overwrite behavior.

## Dependencies and Integration Points
- Integrates NameNode RPC, block manager queue accounting, DataNode liveness, test log directory, and filesystem file creation/deletion.
- Uses ordered first test for `testMetaSave`, though each test rebuilds cluster in `BeforeEach`.

## Risks and Edge Cases
- Exact output line assertions are brittle to metasave formatting changes.
- Dead DataNode detection is timing-sensitive and depends on heartbeat/recheck settings.
- Concurrent metasave test swallows IOExceptions inside worker threads, so it primarily detects append corruption, not individual call failures.

## Test Signals
- Strong signal for metasave diagnostic shape, delete-queue accounting, overwrite behavior, and basic concurrency behavior.
