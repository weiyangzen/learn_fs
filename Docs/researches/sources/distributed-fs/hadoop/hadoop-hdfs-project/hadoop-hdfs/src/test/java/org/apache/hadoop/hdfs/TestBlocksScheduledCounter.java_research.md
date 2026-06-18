<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java

Purpose: Tests `DatanodeDescriptor.getBlocksScheduled()` accounting for normal writes, abandoned blocks, deleted files, and truncation while reconstruction work is pending.

Important APIs, types, and functions: `DatanodeManager.fetchDatanodes`, `DatanodeDescriptor.getBlocksScheduled`, `BlockManager`, `BlockManagerTestUtil.computeAllPendingWork/updateState/waitForMarkedDeleteQueueIsEmpty`, `NameNodeAdapter.getBlockLocations`, `findAndMarkBlockAsCorrupt`, `DataNodeTestUtils.setHeartbeatsDisabledForTests`, `DistributedFileSystem.truncate`, and namesystem block-manager write locks.

Control flow: The basic test creates a file, writes and `hflush`es to allocate a block, checks one scheduled block, then closes and checks zero. The abandoned-block test stops one DataNode before a replicated write and ensures the stopped target is not left scheduled while live targets are. The deleted-block test creates a replicated file, disables heartbeats, marks replicas corrupt under the BM write lock, computes pending reconstruction, deletes the file, drains the delete queue, and sums scheduled counts. The truncate test stops/restarts a DataNode to create under-replication, disables heartbeats, computes pending work, truncates the file, and checks scheduled counts clear.

State and persistence behavior: The tests target in-memory NameNode block-management counters and pending reconstruction queues. They also manipulate DataNode heartbeat state and corruption metadata. There is no restart persistence check; correctness is immediate counter cleanup when lifecycle events happen.

Dependencies and integration points: Integrates client writes, hflush block allocation, DataNode liveness, corruption marking, block reconstruction scheduling, file deletion, truncation, and internal NameNode locking.

Risks: These tests depend on internal block manager APIs and manual lock discipline. Timing is controlled by disabling heartbeats and direct state updates, but the surrounding cluster behavior can still be sensitive to asynchronous deletion and reconstruction queues.

Test signals: Success means scheduled block counters increment only while work is genuinely scheduled and return to zero after close, abandon, delete, or truncate clears pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestBlocksScheduledCounter.java -->
