# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/InterDatanodeProtocol.proto

## Purpose

`InterDatanodeProtocol.proto` defines the private stable RPC contract used between DataNodes for block replica recovery. The source was read as a complete 91-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `InterDatanodeProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages include `InitReplicaRecoveryRequestProto`, `InitReplicaRecoveryResponseProto`, `UpdateReplicaUnderRecoveryRequestProto`, and `UpdateReplicaUnderRecoveryResponseProto`. The service `InterDatanodeProtocolService` exposes `initReplicaRecovery` and `updateReplicaUnderRecovery`.

## Control Flow

During lease/block recovery, a coordinating DataNode asks peers to initialize recovery for a `RecoveringBlockProto`. A peer replies whether a replica exists and, if so, provides its replica state and block metadata. The coordinator can then request an update under recovery with the recovery ID/new generation stamp, new length, and optional new block ID for truncate/copy recovery. The response may include the storage UUID that holds the updated replica.

## State and Persistence Behavior

The schema drives DataNode replica state transitions from write/recovery states to updated finalized or under-recovery metadata. It does not persist by itself, but implementations update on-disk block metadata and replica generation stamps/lengths.

## Dependencies and Integration Points

It integrates with lease recovery, DataNode replica maps, block metadata files, NameNode recovery orchestration, and shared recovery messages from `HdfsServer.proto`.

## Risks and Edge Cases

Recovery correctness depends on matching generation stamps, lengths, optional truncate block IDs, and replica state. Missing optional response fields are valid when no replica is found. Changing required request fields risks recovery protocol incompatibility.

## Test Signals

Tests should cover successful recovery, no-replica responses, generation-stamp updates, truncate/new-block-ID recovery, storage UUID propagation, and mixed-version decoding of optional fields.
