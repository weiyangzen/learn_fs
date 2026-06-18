# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestStorageReport.java

Purpose: This integration test ensures DataNode heartbeat storage reports include configured storage type and normal storage state.

Important APIs/types/functions: `MiniDFSCluster.storageTypes`, `StorageReport`, `DatanodeStorage`, `StorageType.SSD`, `DataNodeTestUtils.triggerHeartbeat`, `DatanodeProtocolClientSideTranslatorPB.sendHeartbeat`, `SlowPeerReports`, and `SlowDiskReports`.

Control flow: Setup starts a one-DataNode cluster with two SSD storages. The test installs a spy on the DataNode-to-NameNode protocol, triggers a heartbeat, captures the `StorageReport[]` passed to `sendHeartbeat`, and asserts each report has the SSD type and `DatanodeStorage.State.NORMAL`.

State and persistence behavior: No file data is created. The relevant state is DataNode volume configuration, block-pool ID, and heartbeat payload metadata.

Dependencies and integration points: It tests storage-type propagation from cluster builder to DataNode storage reports and through the NameNode heartbeat RPC shape, including compatibility with slow peer/disk report parameters.

Risks and test signals: Signals are captured heartbeat arguments and per-report assertions. Risk is low but tied to Mockito signature matching; adding heartbeat parameters would require test updates.
