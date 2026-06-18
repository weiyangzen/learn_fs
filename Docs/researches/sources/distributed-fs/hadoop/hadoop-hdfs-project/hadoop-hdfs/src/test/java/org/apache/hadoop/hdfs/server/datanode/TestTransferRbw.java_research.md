# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestTransferRbw.java

Purpose: This test verifies transferring a replica-being-written from one DataNode to another while preserving block identity, generation stamp, and visible length.

Important APIs/types/functions: `ReplicaBeingWritten`, `LocalReplicaInPipeline`, `FsDatasetTestUtil.getReplicas`, `DFSTestUtil.transferRbw`, `DFSClientAdapter.getDFSClient`, `BlockOpResponseProto`, `Status.SUCCESS`, and `DFS_DATANODE_DATA_WRITE_BANDWIDTHPERSEC_KEY`.

Control flow: The test starts one DataNode, creates `/foo`, writes random data with repeated `hflush` while leaving the stream open, retrieves the RBW from the original DataNode, then starts a second DataNode with bandwidth throttling enabled. It obtains live DataNode reports, maps the new and old registrations, invokes the RBW transfer helper, and reads the new node’s RBW state.

State and persistence behavior: A real under-construction HDFS block remains open during transfer. The test inspects physical dataset replica state and xceiver write throttler configuration on both DataNodes.

Dependencies and integration points: It covers DataTransferProtocol RBW transfer, DFS client/DataNode identity mapping, DataNode write throttling, and FsDataset RBW materialization.

Risks and test signals: Signals are transfer `SUCCESS`, exactly one RBW on each relevant node, and matching block ID/generation/visible length. Risks include random data size and polling for replica appearance with fixed sleeps.
