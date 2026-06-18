<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java

Purpose: verifies DataNode restart behavior for lazy-persist replicas depending on whether the RAM_DISK block had already been saved to persistent storage.

Important APIs/types/functions: extends `LazyPersistTestCase`; uses `FSNamesystem`, `NameNodeAdapter.getDatanode`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `DataNode.triggerBlockReport`, `BlockReportOptions`, `FsDatasetImpl.getNonPersistentReplicas`, `FsDatasetTestUtil.stopLazyWriter`, helper `waitForBlockReport`, and storage types `RAM_DISK` and `DEFAULT`.

Control flow: `testDnRestartWithSavedReplicas` creates a lazy RAM_DISK file, waits until `FsDatasetImpl.getNonPersistentReplicas()` reaches zero, confirming the lazy writer saved the block while it remains on RAM_DISK, restarts the DataNode, triggers and waits for a block report count change, then expects the block to be reported on DEFAULT persistent storage. `testDnRestartWithUnsavedReplicas` stops the lazy writer before creating the file, verifies the block is on RAM_DISK, restarts the DataNode, waits for cluster activity, and expects storage type to remain RAM_DISK because there is no saved persistent copy to promote.

State and persistence behavior: distinguishes non-persistent RAM_DISK replica state from saved persistent replica state. Restart should recover saved replicas as persistent storage, while unsaved replicas remain transient in block-location reporting.

Dependencies and integration points: integrates DataNode restart, lazy writer, block reports, NameNode `DatanodeDescriptor` storage report counters, and located-block storage type verification from the shared test case.

Risks: assumes block report count changes on the first storage info after trigger. Timing depends on lazy writer interval and DataNode restart speed.

Test signals: failures indicate DataNode restart incorrectly loses saved lazy-persist replicas, incorrectly promotes unsaved transient replicas, or fails to update NameNode storage-type state after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestLazyPersistReplicaRecovery.java -->
