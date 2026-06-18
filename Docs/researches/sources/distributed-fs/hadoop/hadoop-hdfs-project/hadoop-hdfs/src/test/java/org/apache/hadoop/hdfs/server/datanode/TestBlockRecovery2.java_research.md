# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery2.java

## Purpose
`TestBlockRecovery2` extends block recovery coverage with race, timeout, EC lease recovery, and min-replication scenarios that are easier to express in separate cluster-level tests.

## Important APIs, Types, and Functions
- `startUp` creates a DataNode connected to a mocked active NameNode, similar to `TestBlockRecovery`.
- `testRaceBetweenReplicaRecoveryAndFinalizeBlock` uses a real one-DataNode cluster and concurrent `initReplicaRecovery` versus output-stream close.
- `testRecoveryTimeout` and `testRecoverySlowerThanHeartbeat` call `TestBlockRecovery.testRecoveryWithDatanodeDelayed`.
- `testEcRecoverBlocks` uses a spied `NamenodeProtocols`, `DFSClient`, default EC policy, and delayed `complete` RPC to force lease recovery while close is blocked.
- `testRecoveryWillIgnoreMinReplication` validates recovery when only one of three original replicas remains alive.

## Control Flow and Behavior
Most tests tear down the mocked DataNode fixture and start a MiniDFSCluster. The race test writes and hsyncs a file, starts a recovery thread that sleeps then calls `initReplicaRecovery`, closes the writer, tolerates expected write failure, and then calls `updateReplicaUnderRecovery`. Timeout tests inject delayed or initially lost `commitBlockSynchronization` responses and wait for recovery retry and completion. The EC test delays `complete`, starts stream close in a thread, then repeatedly invokes `recoverLease` until it succeeds before releasing the delayed complete. The min-replication test writes an under-construction replicated file, kills two of three replica DataNodes, expires the lease, waits for file closure, and then waits for replication to restore the target.

## State and Persistence
Tests create real HDFS files, under-construction blocks, leases, dead DataNode state, and EC block groups in MiniDFSCluster. The fixture DataNode has a real temporary data directory that is deleted in teardown.

## Dependencies and Integration Points
The file integrates DataNode recovery APIs, NameNode lease recovery, `DFSClient`, `DistributedFileSystem`, EC policy helpers, `FSNamesystem`, `BlockRecoveryCommand.RecoveringBlock`, heartbeats, and cluster DataNode lifecycle controls.

## Risks and Edge Cases
The suite targets race conditions between writer finalize and recovery, lost recovery commits, recovery work slower than heartbeat scheduling, EC file close blocked by NameNode completion, and recovery below configured `dfs.namenode.replication.min`. Timing waits are long because these are slow integration tests with lease expiration and DataNode death.

## Test Signals
Signals are successful recovery initialization despite close failure, completion under delayed or lost commit synchronization, successful EC `recoverLease` while close is delayed, `dfs.isFileClosed` becoming true after hard lease expiry, and final replication reaching the desired target.
