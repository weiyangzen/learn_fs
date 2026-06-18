<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java

Purpose: tests initial placement and fallback rules for lazy-persist replicas, including RAM_DISK success, no-transient-storage fallback, synchronous eviction, full/partial memory-budget fallback, and ensuring RAM_DISK is not used by normal files.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `getClusterBuilder`, `makeTestFile`, `ensureFileReplicasOnStorageType`, `verifyRamDiskJMXMetric`, `waitForMetric`, `triggerBlockReport`, client `getLocatedBlocks`, `LocatedBlock.getStorageTypes`, storage types `RAM_DISK`, `DEFAULT`, and custom `StorageType[]` cluster setup.

Control flow: basic placement creates a lazy-persist file and expects RAM_DISK. Size-limited RAM_DISK capacity still admits two files when capacity is set to three replicas. No transient storage builds a cluster without RAM_DISK and expects DEFAULT placement without error. Synchronous eviction writes one RAM_DISK block, waits for lazy persistence, writes another block with limited locked memory, and expects `RamDiskBlocksEvictedWithoutRead`. Full fallback sets max locked memory below block size and expects DEFAULT plus write-fallback metric. Partial fallback writes a five-block file with room for two RAM_DISK blocks, waits for lazy writer/block report, then counts two RAM_DISK and three DEFAULT blocks. The final test configures only RAM_DISK storage but creates a non-lazy file and expects placement failure.

State and persistence behavior: state includes block placement storage types in located blocks, RAM_DISK eviction/fallback JMX metrics, transient locked-memory budget, and persistent copies created by the lazy writer before eviction.

Dependencies and integration points: integrates NameNode block placement policy, DataNode RAM_DISK volumes, locked-memory limits, lazy writer timing, block reports, and HDFS located-block storage-type reporting.

Risks: partial fallback depends on asynchronous eviction timing but asserts exact 2/3 distribution after sleeping. Metrics are global to the test cluster and require clean setup per test.

Test signals: failures catch incorrect lazy-persist placement, accidental RAM_DISK use for normal writes, eviction/fallback metric regressions, or storage-type reporting mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaPlacement.java -->
