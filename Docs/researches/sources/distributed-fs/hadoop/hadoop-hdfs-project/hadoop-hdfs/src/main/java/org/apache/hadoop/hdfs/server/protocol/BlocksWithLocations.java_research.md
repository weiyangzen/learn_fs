<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java

## Purpose

`BlocksWithLocations` is a NameNode protocol DTO that returns blocks with their DataNode UUIDs, storage ids, and storage types. It also supports striped block group metadata for erasure-coded files.

## Important APIs and types

- Top-level holds `BlockWithLocations[]`.
- `BlockWithLocations` carries `Block`, `String[] datanodeUuids`, `String[] storageIDs`, and `StorageType[] storageTypes`.
- `StripedBlockWithLocations` extends it with `byte[] indices`, `short dataBlockNum`, and `int cellSize`.
- Getters expose all fields; `toString` formats locations as `[storageType]storageID@datanodeUuid`.

## Control flow

NameNode protocol methods construct these DTOs when clients such as the balancer request blocks for a DataNode. Striped variants wrap a base block-with-locations object and validate that the number of DataNode UUIDs matches the indices array.

## State and persistence behavior

The object is an immutable-reference DTO with mutable arrays. It does not persist state; it serializes over NameNode protocol/PB helpers.

## Dependencies and integration points

Used by `NameNodeRpcServer.getBlocks`, balancer/mover flows, and protobuf conversion tests. Depends on `Block`, `StorageType`, and Hadoop preconditions.

## Risks and edge cases

Parallel arrays must stay aligned. Only striped constructor length-checks UUIDs versus indices; it does not validate storage id/type lengths. Array mutability can cause post-construction changes. String formatting assumes aligned arrays.

## Test signals

`TestPBHelper.testConvertBlocksWithLocations`, balancer/mover tests, and NameNode RPC tests should cover replicated and striped DTO conversion, storage metadata preservation, and array alignment validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlocksWithLocations.java -->
