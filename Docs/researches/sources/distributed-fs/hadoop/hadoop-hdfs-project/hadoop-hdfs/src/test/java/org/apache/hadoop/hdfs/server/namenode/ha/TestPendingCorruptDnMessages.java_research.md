# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestPendingCorruptDnMessages.java

Purpose: verifies that standby NameNodes correctly manage pending DataNode block messages when reports arrive for replicas whose storage identity or referenced block state changes before failover.

Important APIs and types: `MiniDFSCluster`, `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `ExtendedBlock`, `DataNodeProperties`, `DataNodeTestUtils.runDirectoryScanner`, `BlockManager.getPendingDataNodeMessageCount`, `DatanodeDescriptor`, and `DatanodeReportType.ALL`.

Control flow: `testChangedStorageId` starts one DN and two NNs, creates a file, waits for standby catch-up, mutates the block generation stamp backward on the DataNode, runs the directory scanner, stops the DN, restarts the standby NN, and restarts the DN so the initial block report queues a corrupt pending message on the standby. It records the registered DN UUID, reformats and restarts the DN on the same transfer port, waits for the UUID to change, then asserts the pending message queue is cleared before failing over to the standby. `testRemoveBlockCleansUpPendingDNMessages` follows a similar setup but mutates the generation stamp into the future, queues a pending message, deletes the file on the active, rolls/tails edits, and verifies the standby pending queue is empty.

State and persistence behavior: the tests exercise standby-only pending DN message queues, DataNode UUID/storage identity changes caused by reformatting, block generation stamp metadata in replicas and edit logs, and deletion edits that remove pending messages for blocks no longer in the namespace.

Dependencies and integration points: these are MiniDFSCluster integration tests touching DataNode storage, directory scanning, NameNode restart, block reports, edit log tailing, and HA failover.

Risks and test signals: a leak in `pendingDNMessages` can block failover correctness or keep corrupt/future reports against obsolete storage. Signals include waiting for exactly one queued message, waiting for a changed DN UUID, asserting queue count returns to zero, and performing a final transition to active.
