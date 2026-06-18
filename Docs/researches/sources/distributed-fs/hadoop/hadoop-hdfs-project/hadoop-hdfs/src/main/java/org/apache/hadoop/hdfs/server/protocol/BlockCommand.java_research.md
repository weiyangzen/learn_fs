<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java

## Purpose

`BlockCommand` is a heartbeat command from NameNode to DataNode for block operations such as transfer/replication or invalidation. It carries blocks and optional target DataNode/storage information.

## Important APIs and types

- Extends `DatanodeCommand`.
- `NO_ACK` sentinel marks deletion commands that do not require explicit DataNode acknowledgment.
- Constructors accept either `List<BlockTargetPair>`, blocks only, or fully formed block/target/storage arrays.
- Getters expose block pool id, blocks, targets, target storage types, and target storage ids.

## Control flow

For transfer commands, the constructor converts `DatanodeStorageInfo` targets into parallel arrays of `DatanodeInfo`, `StorageType`, and storage ids. For block-only actions it uses empty target arrays. DataNode command handling interprets the action code inherited from `DatanodeCommand`.

## State and persistence behavior

The command is a mutable-array DTO but fields are final references. It does not persist state; it is serialized over DataNode protocol and acted on by DataNodes.

## Dependencies and integration points

Used by block management heartbeat scheduling, replication, invalidation, and protobuf conversion. Depends on `Block`, `DatanodeInfo`, `StorageType`, and `DatanodeStorageInfo` conversion helpers.

## Risks and edge cases

Parallel arrays must remain length-aligned with `blocks`. `NO_ACK` assumes no real block size equals `Long.MAX_VALUE`. Array contents are not defensively copied, so callers must avoid later mutation.

## Test signals

Signals include heartbeat handling tests, block manager replication/invalidation tests, and PB helper conversion tests for DataNode commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockCommand.java -->
