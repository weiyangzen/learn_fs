
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockReportLease.java

## Purpose
`TestBlockReportLease` validates NameNode full block report lease enforcement and compatibility behavior. It ensures leases are checked once per block-report request, expired leases can throw or be tolerated based on configuration, unregistered datanodes receive registration commands, and incomplete first block reports in safe mode are counted correctly per storage.

## Important APIs, Types, and Functions
The tests use `MiniDFSCluster`, `NamenodeProtocols.sendHeartbeat`, `NamenodeProtocols.blockReport`, `BlockReportContext`, `StorageBlockReport`, `BlockListAsLongs`, `BlockReportLeaseManager`, `InvalidBlockReportLeaseException`, `FinalizeCommand`, and `RegisterCommand`. `createReports` constructs fake block-list payloads for each `DatanodeStorage`. Mockito spies `BlockManager`, and `GenericTestUtils.DelayAnswer` blocks `processReport` to create lease-removal races.

## Control Flow and State
`testCheckBlockReportLease` obtains a lease from heartbeat, starts a block report, waits until `processReport`, removes the lease, then allows processing to complete and expects a `FinalizeCommand`, proving lease validation is request-level rather than per-storage. `testExceptionThrownWhenFBRLeaseExpired` removes the lease before reporting and expects `InvalidBlockReportLeaseException`. `testNoExceptionWhenRejectInvalidLeaseDisabled` sets `DFS_BLOCKREPORT_REJECT_INVALID_LEASE_KEY` false and expects no exception for an invalid lease. `testCheckBlockReportLeaseWhenDnUnregister` removes the datanode from the map and expects `RegisterCommand`. `testFirstIncompleteBlockReport` enters safe mode and sends per-storage reports, simulating a first report failure for the first storage and verifying block report count deltas.

## Dependencies and Integration Points
The file exercises DataNode registration, heartbeat lease issuance, NameNode RPC block-report handling, block manager report processing, safe mode, and rolling-upgrade compatibility configuration.

## Risks and Test Signals
Risks include deadlocks from delayed report processing, executor leaks, and synthetic block-list construction drift. The test signal is strong around lease boundary behavior, especially that mid-request lease removal does not partially reject batched storage reports, while pre-request expiration is handled according to config.
