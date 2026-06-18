# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestDataNodeExit.java

## Purpose
`TestDataNodeExit` verifies DataNode liveness behavior as block-pool services exit in a federated cluster, and verifies shutdown tolerates an exception while sending out-of-band messages to peers.

## Important APIs, Types, and Functions
- `MiniDFSNNTopology.simpleFederatedTopology(3)` starts three nameservices.
- `DataNode#getAllBpOs`, `getBpOsCount`, and `isDatanodeUp` expose block-pool service state.
- `BPOfferService#stop` is used to stop selected block-pool services.
- `DataXceiverServer#sendOOBToPeers` is spied to throw in shutdown coverage.

## Control Flow and Behavior
Setup creates a federated three-NameNode MiniDFSCluster and waits for all namespaces active. `testBPServiceState` iterates DataNodes and BPOfferServices and asserts each BPOS is alive. `testBPServiceExit` stops one BPOS and expects the DataNode to remain up, then stops two more and expects the DataNode to go down once all block-pool services are gone. `testSendOOBToPeers` replaces the DataNode xceiver server with a spy that throws `NullPointerException` from `sendOOBToPeers`, then calls `shutdown` and fails if the exception escapes.

## State and Persistence
State is the MiniDFSCluster's live DataNode and BPOfferService threads. No user files are needed. The helper waits up to roughly thirty seconds for BPOS count changes.

## Dependencies and Integration Points
The test integrates DataNode lifecycle management, federated block-pool services, MiniDFSCluster topology, DataXceiverServer shutdown hooks, and Mockito spies.

## Risks and Edge Cases
Covered risks include DataNode exiting too early when only some block pools fail, failing to exit when all block pools are stopped, and shutdown being disrupted by peer OOB notification failures. It does not cover partial restart of a stopped BPOS.

## Test Signals
Signals are all BPOS instances initially alive, exact BPOS count reductions after stop calls, `isDatanodeUp` true after partial stop and false after all services stop, and no thrown exception during shutdown with a failing xceiver server hook.
