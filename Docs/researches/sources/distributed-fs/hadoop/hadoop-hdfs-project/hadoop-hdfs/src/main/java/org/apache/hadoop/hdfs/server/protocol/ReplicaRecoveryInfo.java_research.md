<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java

## Purpose

`ReplicaRecoveryInfo` describes a replica's block identity, disk length, generation stamp, and original replica state during block recovery.

## Important APIs and types

The class extends `Block` and stores `ReplicaState originalState`. The constructor calls `set(blockId, diskLen, gs)`. It exposes `getOriginalReplicaState()` and appends length/state to `toString()`. Equality and hash code defer to `Block`.

## Control flow

`InterDatanodeProtocol.initReplicaRecovery` returns this value to the recovery coordinator, which compares replica states and lengths before deciding how to update replicas.

## State and persistence behavior

It is a transient snapshot of persistent DataNode replica metadata. Equality ignores original replica state because it delegates to `Block`.

## Dependencies and integration points

It depends on `Block` and `HdfsServerConstants.ReplicaState`, and integrates with lease recovery and DataNode replica update RPCs.

## Risks and test signals

Risks include state being ignored in equality, null `originalState` causing `toString()` failure, and mismatched disk length/generation values. Tests should cover each replica state, equality semantics, and recovery decisions when states differ but block IDs match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReplicaRecoveryInfo.java -->
