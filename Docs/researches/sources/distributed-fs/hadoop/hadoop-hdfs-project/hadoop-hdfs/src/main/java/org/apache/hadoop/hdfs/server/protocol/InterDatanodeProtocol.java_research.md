<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java

## Purpose

`InterDatanodeProtocol` defines private DataNode-to-DataNode RPCs used during replica recovery. It lets one DataNode inspect and update a replica on another DataNode.

## Important APIs and types

The interface is secured with DataNode Kerberos principals and declares `versionID = 6L`. Methods are `initReplicaRecovery(RecoveringBlock)` returning `ReplicaRecoveryInfo` or null, and `updateReplicaUnderRecovery(ExtendedBlock, recoveryId, newBlockId, newLength)` returning a storage ID string.

## Control flow

Recovery begins by asking each candidate DataNode for replica state. Once the recovery coordinator selects a length/generation, it calls `updateReplicaUnderRecovery` to bump generation stamp, adjust length, and possibly rename the block ID on the target replica.

## State and persistence behavior

Implementations read and mutate persistent on-disk replica metadata and block files. The interface itself stores no state.

## Dependencies and integration points

It uses `BlockRecoveryCommand.RecoveringBlock`, `ReplicaRecoveryInfo`, `ExtendedBlock`, and DataNode RPC/protobuf translators. It integrates with lease recovery, block generation-stamp management, and DataNode storage.

## Risks and test signals

Risks include updating the wrong replica, accepting stale recovery IDs, inconsistent lengths across replicas, and authentication errors between DataNodes. Tests should cover missing replicas, finalized/rbw/rwr states, recovery ID ordering, storage ID return values, and protobuf compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/InterDatanodeProtocol.java -->
