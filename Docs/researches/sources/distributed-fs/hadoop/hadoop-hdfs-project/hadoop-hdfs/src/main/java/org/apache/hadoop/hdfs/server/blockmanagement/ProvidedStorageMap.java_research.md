<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java

## Purpose

`ProvidedStorageMap` multiplexes normal DataNode storage with HDFS `PROVIDED` storage, where block bytes live in an external storage system and DataNodes expose access to the same logical provided volume.

## Important APIs and types

The class reads provided-storage configuration, constructs a singleton provided `DatanodeStorageInfo`, loads a `BlockAliasMap`, and exposes `getStorage`, `updateStorage`, `removeDatanode`, `getCapacity`, `chooseProvidedDatanode`, `getAliasMap`, and `newLocatedBlocks`. Nested types include `ProvidedBlocksBuilder`, `ProvidedDescriptor`, `ProvidedDatanodeStorageInfo`, and `ProvidedBlockList`.

## Control flow

When disabled, the map returns normal builders and leaves provided fields null. When enabled, matching storage IDs of type `PROVIDED` are injected into reporting DataNodes and the first provided block report is synthesized from the alias map under the global write lock. `ProvidedBlocksBuilder` rewrites located-block responses: local replicas are preserved, provided replicas are expanded to one or more active provided DataNodes up to the default replication factor, excluding nodes that already host local replicas. `ProvidedDescriptor` tracks active provided DataNodes and randomly chooses live nodes first; replication commands are delegated to a chosen real DataNode.

## State and persistence behavior

The logical provided storage is in-memory NameNode state backed by the configured `BlockAliasMap` for block aliases. Active DataNodes are tracked in a concurrent map plus a selection list. If no active provided DataNodes remain, the provided block report count is reset and storage may transition to failed.

## Dependencies and integration points

It integrates `BlockManager`, `RwLock`, `BlockAliasMap`, `TextFileRegionAliasMap`, `DatanodeDescriptor`, `DatanodeStorageInfo`, `LocatedBlocks`, `BlockListAsLongs`, and `StorageType.PROVIDED`.

## Risks and edge cases

The design assumes a single provider storage ID. `ProvidedDescriptor.getProvidedStorage` appends to the random-choice list on each report, so duplicate DataNode entries must be controlled by caller/report behavior. Choosing provided locations is random and not topology-aware. `ProvidedBlockList` does not support legacy long-array or protobuf buffer access. Correct lock mode is asserted for report processing and removal.

## Test signals

Tests should cover disabled behavior, provided storage injection, first alias-map block report, active DataNode removal/failure state, location expansion with excluded UUIDs, replication delegation, duplicate reporting behavior, and unsupported `ProvidedBlockList` methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ProvidedStorageMap.java -->
