<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java

## Purpose

`ReplicaUnderConstruction` records per-replica state for a block or block-group replica while a file is being written or recovered.

## Important APIs and types

It extends `Block` and adds an expected `DatanodeStorageInfo`, a mutable `HdfsServerConstants.ReplicaState`, and a `chosenAsPrimary` recovery flag. APIs expose expected storage location, state getter/setter, primary-selection getter/setter, `isAlive`, equality/hash inherited from `Block`, and a compact `ReplicaUC[...]` string.

## Control flow

The object is constructed from an existing block, assigned target storage, and reported replica state. Recovery code can mark a replica as chosen primary, update its state as reports arrive, and test whether the expected DataNode is alive.

## State and persistence behavior

State is mutable in memory and tied to block-under-construction metadata. The generation stamp and length inherited from `Block` are the DataNode-reported values. Persistence is indirect through namespace/block-under-construction serialization elsewhere.

## Dependencies and integration points

It integrates with `BlockUnderConstructionFeature`, lease recovery, pipeline construction, DataNode liveness checks, and the `HdfsServerConstants.ReplicaState` state machine.

## Risks and edge cases

The expected storage location is not proof the DataNode actually has the replica. Equality ignores expected location and state because it follows `Block` equality, so collections keyed by this object treat same block IDs as equal. `isAlive` assumes the expected location is non-null.

## Test signals

Tests should cover state mutation, primary selection, liveness pass-through, string rendering, equality semantics for same block/different storage, and recovery flows with stale or missing reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ReplicaUnderConstruction.java -->
