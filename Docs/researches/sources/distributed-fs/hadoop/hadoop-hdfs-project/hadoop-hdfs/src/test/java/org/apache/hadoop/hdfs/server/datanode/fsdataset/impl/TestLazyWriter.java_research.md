<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java

Purpose: tests the DataNode lazy writer and RAM_DISK eviction lifecycle: saving lazy-persist blocks to disk, synchronous and LRU eviction, protecting unsaved blocks from eviction, delete-before/after-persist cleanup, and HDFS used-space accounting.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `makeTestFile`, `makeRandomTestFile`, `ensureFileReplicasOnStorageType`, `ensureLazyPersistBlocksAreSaved`, `waitForMetric`, `verifyRamDiskJMXMetric`, `verifyDeletedBlocks`, `verifyReadRandomFile`, `FsDatasetTestUtil.stopLazyWriter`, `DFSTestUtil.readFile`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testLazyPersistBlocksAreSaved` writes a ten-block lazy file, verifies RAM_DISK placement, waits for `RamDiskBlocksLazyPersisted`, and checks saved disk copies. Synchronous eviction writes one block, waits for persistence, writes another under one-block memory, and expects eviction metrics. Unsaved-block protection stops lazy writer, writes a RAM_DISK file, writes a second file, and verifies the first stays on RAM_DISK while the second falls back to DEFAULT. LRU eviction writes several files, waits for persistence, reads them in shuffled order to establish access order, then writes replacements and verifies each touched file moves to DEFAULT in LRU order while later ones remain RAM_DISK. Delete tests remove files before and after lazy persistence and verify corresponding block deletion and metrics. DFS usage test checks `fs.getUsed()` increases by one block on create, does not double-count after lazy persistence, and returns to the pre-create value after delete.

State and persistence behavior: covers transient RAM_DISK replicas, persistent lazy copies, eviction LRU metadata, RAM_DISK JMX counters, deleted block state, read-hit tracking, and NameNode used-space accounting.

Dependencies and integration points: integrates lazy writer background thread, RAM_DISK eviction policy, HDFS read path for access-order updates, client delete, NameNode block deletion, and located-block storage-type reporting.

Risks: LRU ordering depends on reads updating RAM_DISK replica access state deterministically. Tests rely on metric counters being reset with each cluster and on lazy writer timing.

Test signals: failures catch unsaved replica eviction, missing lazy-persist disk copies, broken eviction metrics/order, block deletion leaks, or namespace usage double-counting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyWriter.java -->
