<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java

## Purpose

`BlockAlias` is the minimal interface for objects that expose an HDFS `Block` from an external alias map, primarily for provided-storage loading.

## Important APIs and types

The interface has one method, `getBlock()`, returning `org.apache.hadoop.hdfs.protocol.Block`.

## Control flow

There is no control flow. Alias-map readers iterate implementations and feed blocks to block-report processing or provided-storage metadata consumers.

## State and persistence behavior

The interface owns no state. Implementations such as `FileRegion` hold alias metadata and may be backed by text files, LevelDB, or other alias-map stores.

## Dependencies and integration points

It integrates with `BlockAliasMap`, `ProvidedStorageMap.ProvidedBlockList`, and external storage region descriptors.

## Risks and edge cases

The interface only exposes the block, not the external location. Consumers that need location metadata must downcast or use richer implementation APIs.

## Test signals

Tests should ensure alias-map implementations return stable `Block` values and that block-report wrappers consume only the interface method.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/BlockAlias.java -->
