## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterRpcStoragePolicySatisfier.java

Purpose: verifies that Router RPC forwards `satisfyStoragePolicy` correctly to an HDFS cluster configured for external Storage Policy Satisfier (SPS). It uses one nameservice and a datanode with `ARCHIVE` and `DISK` storage types.

Important APIs and types include `MiniRouterDFSCluster`, `ClientProtocol`, `DistributedFileSystem`, `StorageType`, `BlockStoragePolicy`, `HdfsConstants.StoragePolicySatisfierMode.EXTERNAL`, `NameNodeConnector`, `StoragePolicySatisfier`, `ExternalSPSContext`, and `DFSTestUtil.waitExpectedStorageType`.

Control flow: `globalSetUp()` configures the NameNode for external SPS, short SPS datanode cache refresh, one datanode, Router metrics/RPC services, mock locations, and starts an external `StoragePolicySatisfier` using a `NameNodeConnector`. The test creates a file through the Router, waits until it is on `DISK`, sets the file storage policy to `COLD`, verifies the policy through Router protocol, invokes `satisfyStoragePolicy`, and waits for the block to move to `ARCHIVE` via both Router and NameNode filesystems.

State and persistence behavior is HDFS block placement and storage policy metadata. SPS runs as an external service in the test JVM and performs asynchronous movement, so assertions wait up to fixed timeouts. The Router itself is not persisting state; it forwards policy commands to the owning NameNode.

Dependencies and integration points include Router RPC, HDFS storage policy APIs, external SPS lifecycle, block movement monitoring, and MiniDFS storage type configuration. Risks covered include Router accepting policy set but failing to invoke satisfier, asynchronous SPS not seeing Router-created files, and Router/NameNode views diverging. Test signals are storage policy name equality and eventual storage-type assertions on both federated and backend filesystems.
