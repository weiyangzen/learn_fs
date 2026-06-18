<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java

Purpose: verifies locked-memory accounting for lazy-persist RAM_DISK replicas, including fallback when no locked memory is available, reservation on write, release on delete/eviction, page rounding for short blocks, and cleanup after client pipeline failure.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `FsDatasetSpi.getCacheUsed`, `FsDatasetImpl.evictLazyPersistBlocks`, `DataNodeTestUtils.triggerBlockReport`, `BlockManagerTestUtil.waitForMarkedDeleteQueueIsEmpty`, `DFSTestUtil.abortStream`, `DFSOutputStream`, helper `waitForLockedBytesUsed`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testWithNoLockedMemory` builds one DataNode with max locked memory zero, creates a lazy file, and expects DEFAULT storage. `testReservation` writes one block with max locked memory equal to block size and expects RAM_DISK plus `cacheUsed == BLOCK_SIZE`. Delete and eviction tests first reserve memory, then delete the file or lazy-persist and evict it, waiting for locked bytes to drop to zero. Short-block test writes one byte and expects OS page-size locked accounting. Pipeline failure test creates a lazy file stream, writes and syncs one byte, aborts the DFS output stream, waits for page-sized locked memory, deletes the file, drains marked-delete queue, triggers a block report, and waits for zero.

State and persistence behavior: locked memory is surfaced through `FsDatasetSpi.getCacheUsed`, the same metric used by cache code. RAM_DISK replicas consume locked bytes until deleted or evicted after persistent copy. Failed writes still reserve a rounded page until namespace/deletion cleanup releases it.

Dependencies and integration points: integrates client create flags `CREATE` and `LAZY_PERSIST`, DataNode RAM_DISK placement, block reports, NameNode delete queues, lazy writer metrics, and OS page-size behavior inherited from the test case.

Risks: `cacheUsed` doubles as locked-memory signal for lazy persist and can be affected by unrelated cache features if cluster setup changes. The pipeline failure path is timing-sensitive around aborted streams and block report/delete processing.

Test signals: failures indicate memory leaks, incorrect fallback to RAM_DISK without lock budget, bad page rounding, or missing release after deletion, eviction, or aborted writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistLockedMemory.java -->
