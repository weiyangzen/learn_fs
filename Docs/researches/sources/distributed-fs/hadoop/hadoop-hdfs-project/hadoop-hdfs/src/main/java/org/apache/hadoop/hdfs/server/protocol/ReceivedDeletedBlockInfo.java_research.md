<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java

## Purpose

`ReceivedDeletedBlockInfo` is the per-block entry used in incremental block reports to tell the NameNode that a DataNode is receiving, has received, or has deleted a block.

## Important APIs and types

The class stores `Block block`, `BlockStatus status`, and deletion hints. `BlockStatus` maps `RECEIVING_BLOCK`, `RECEIVED_BLOCK`, and `DELETED_BLOCK` to numeric codes with `fromCode(int)`. Methods include getters/setters for block and hints, `getStatus()`, `blockEquals`, `isDeletedBlock`, `equals`, `hashCode`, and `toString`.

## Control flow

DataNode storage code creates entries and wraps them in `StorageReceivedDeletedBlocks` for `DatanodeProtocol.blockReceivedAndDeleted`. The NameNode updates pending/received/deleted block state based on `status`.

## State and persistence behavior

The value is mutable and transient. It reflects DataNode on-disk block state but is not persisted directly.

## Dependencies and integration points

It depends on `Block` and integrates with incremental block reports, replication/deletion tracking, and protobuf encoding of status codes.

## Risks and test signals

`equals` requires non-null `delHints`; two otherwise equal entries with null hints compare false. `hashCode` intentionally asserts false and returns 0, so this type is unsafe for hash collections. Tests should cover status code mapping, null hints, deleted-block detection, and NameNode handling for each status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/ReceivedDeletedBlockInfo.java -->
