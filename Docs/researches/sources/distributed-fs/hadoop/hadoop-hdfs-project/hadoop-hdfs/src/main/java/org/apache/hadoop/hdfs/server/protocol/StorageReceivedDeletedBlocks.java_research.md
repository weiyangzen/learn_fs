<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java

## Purpose

`StorageReceivedDeletedBlocks` groups incremental block-report entries for one DataNode storage.

## Important APIs and types

It stores `DatanodeStorage storage` and `ReceivedDeletedBlockInfo[] blocks`. The deprecated constructor accepts a storage ID string and wraps it in a new `DatanodeStorage`; `getStorageID()` is also deprecated. New code uses `getStorage()` and the `DatanodeStorage` constructor.

## Control flow

DataNodes send arrays of these values to `DatanodeProtocol.blockReceivedAndDeleted`. The NameNode applies each block status in the context of the specified storage.

## State and persistence behavior

The object is immutable in references but does not copy the block array. It transiently reports DataNode storage changes.

## Dependencies and integration points

It depends on `DatanodeStorage`, `ReceivedDeletedBlockInfo`, and incremental block-report processing. Deprecated methods preserve wire/source compatibility.

## Risks and test signals

Risks include array mutation after construction, storage ID compatibility, and null block arrays. Tests should cover deprecated/new constructors, toString output, per-storage incremental updates, and NameNode behavior for mixed received/deleted entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/StorageReceivedDeletedBlocks.java -->
