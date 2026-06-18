<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java

## Purpose

`StorageBlockReport` pairs one DataNode storage volume with its full block report payload.

## Important APIs and types

The immutable fields are `DatanodeStorage storage` and `BlockListAsLongs blocks`. Getters expose both. `BlockListAsLongs` encodes finalized and under-construction replicas compactly as longs.

## Control flow

DataNodes build an array of these objects for `DatanodeProtocol.blockReport`, one per storage. The NameNode reads storage identity and block list to reconcile its block map.

## State and persistence behavior

The object is transient. It reports persistent DataNode block state but does not persist or copy it.

## Dependencies and integration points

It depends on `DatanodeStorage`, `BlockListAsLongs`, `DatanodeProtocol`, and NameNode block-manager processing.

## Risks and test signals

Risks include null storage/block lists, wrong storage IDs, compact block-list decoding mistakes, and memory pressure from full reports. Tests should cover multi-storage reports, empty storages, under-construction encoding, and NameNode reconciliation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageBlockReport.java -->
