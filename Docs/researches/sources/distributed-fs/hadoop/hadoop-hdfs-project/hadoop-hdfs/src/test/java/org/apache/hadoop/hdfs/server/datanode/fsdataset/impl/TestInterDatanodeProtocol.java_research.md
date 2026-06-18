<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java

Purpose: tests Inter-DataNode protocol behavior for block metadata, replica recovery initialization/update, hostname-based DataNode communication, recovery error cases, and RPC timeout behavior.

Important APIs/types/functions: `InterDatanodeProtocol`, `DataNodeTestUtils.createInterDatanodeProtocolProxy`, `FsDatasetImpl.initReplicaRecovery`, `FsDatasetSpi.updateReplicaUnderRecovery`, `ReplicaRecoveryInfo`, `ReplicaUnderRecovery`, `RecoveringBlock`, `RecoveryInProgressException`, nested `TestServer`, helpers `checkMetaInfo`, `getLastLocatedBlock`, `createReplicaInfo`, `assertReplicaEquals`, and tests `testBlockMetaDataInfo`, `testBlockMetaDataInfoWithHostname`, `testInitReplicaRecovery`, `testUpdateReplicaUnderRecovery`, `testInterDNProtocolTimeout`.

Control flow: metadata tests build a three-DataNode cluster, write a replicated file, get its last block, connect to one DataNode through an inter-DN proxy, stop block scanners, verify stored block metadata, call `initReplicaRecovery`, then `updateReplicaUnderRecovery` with a shorter length and incremented generation stamp. They also verify missing block recovery returns null. Hostname mode advertises `localhost` and is Linux-only. Static recovery tests build a `ReplicaMap` with finalized external-volume replicas, transition one to `ReplicaUnderRecovery`, update recovery IDs, assert stale recovery IDs throw `RecoveryInProgressException`, assert missing replicas return null, and assert invalid generation-stamp combinations fail. Update tests use a real cluster, initialize recovery, verify RUR state and disk replica, reject mismatched length, then update successfully. Timeout test starts a sleeping RPC `Server` and expects `SocketTimeoutException`.

State and persistence behavior: mutates `ReplicaMap` entries from finalized to under-recovery, updates recovery IDs and replica lengths/generation stamps, and validates stored block metadata on DataNode disk. It also checks `DataSetLockManager` leak state after static recovery tests.

Dependencies and integration points: covers DFSClient NameNode block lookup, DataNode IPC addresses/hostnames, Hadoop RPC, MiniDFSCluster, external volume stubs, and recovery protocol contracts shared by NameNode-initiated lease recovery.

Risks: uses deprecated reflection-style `newInstance` in the test RPC server. Hostname variant is platform-gated. Recovery assertions rely on exact exception semantics and on `DFS_DATANODE_XCEIVER_STOP_TIMEOUT_MILLIS_DEFAULT`.

Test signals: failures indicate inter-DN block metadata mismatch, replica recovery state-machine regressions, recovery concurrency guard failures, or RPC timeout configuration breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/TestInterDatanodeProtocol.java -->
