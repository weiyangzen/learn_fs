# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDatanodeProtocolRetryPolicy.java

Purpose: verifies DataNode protocol retry behavior when a NameNode asks a DataNode to re-register and `registerDatanode` transiently fails with `EOFException`.

Important APIs and types: `DataNode`, `DatanodeProtocolClientSideTranslatorPB`, `DatanodeRegistration`, `NamespaceInfo`, `HeartbeatResponse`, `RegisterCommand`, `NNHAStatusHeartbeat`, `StorageLocation`, `MiniDFSCluster` base directories, Mockito answers, and `GenericTestUtils.waitFor`.

Control flow: setup creates a standalone DataNode data directory, configures DN RPC/HTTP/IPC ports to random, sets default URI to a fake NN address, disables IPC client connect retries, and stores one `StorageLocation`. The test mocks the NameNode protocol: first registration succeeds, re-registration attempts 2 through 4 throw `EOFException`, later attempts succeed with a new registration; the first heartbeat returns `RegisterCommand.REGISTER`, later heartbeats return no commands. A custom `DataNode` overrides `connectToNN` to return the mock protocol. The test triggers a heartbeat and waits until a block report reaches the mock NN, proving retry and re-registration recovered.

State and persistence behavior: local data dir is created and deleted; DataNode BP service state and registration state are live in process. Integration points include BPOfferService heartbeat loop, protocol retry policy, NN HA status, and block report emission. Risks include async timing, fixed fake NN address comparisons, and static registration mutation. Test signals are mock invocation verification for `blockReport` after transient registration failures.
