# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/DatanodeProtocol.proto

## Purpose

`DatanodeProtocol.proto` defines the private stable protobuf RPC contract from DataNodes to the NameNode. It covers registration, heartbeats, block reports, cache reports, incremental block notifications, error reports, bad block reports, version requests, and lease-recovery block synchronization. The source was read as a complete 484-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs.datanode`, Java outer class `DatanodeProtocolProtos`, generic services, and imports `hdfs.proto`, `erasurecoding.proto`, and `HdfsServer.proto`. Major messages include `DatanodeRegistrationProto`, `DatanodeCommandProto` with command-type one-of-style optional fields, `BlockCommandProto`, `BlockIdCommandProto`, `BlockRecoveryCommandProto`, `BlockECReconstructionCommandProto`, registration request/response, `VolumeFailureSummaryProto`, `HeartbeatRequestProto`, `HeartbeatResponseProto`, block report context/report messages, cache report messages, received/deleted block info, error report, bad block report, slow peer/disk reports, and `CommitBlockSynchronizationRequestProto`. The service `DatanodeProtocolService` exposes nine RPCs.

## Control Flow

A DataNode registers with identity, storage info, block keys, and software version. It then sends periodic heartbeats carrying storage reports, transfer counts, cache usage, volume failures, full block report lease requests, slow peer reports, and slow disk reports. The NameNode replies with zero or more typed commands, HA state, rolling-upgrade status, full block report lease ID, and slow-node flag. Separate block report and cache report RPCs send bulk block state. Incremental `blockReceivedAndDeleted` reports communicate newly receiving, received, or deleted blocks. Error and bad block RPCs notify exceptional conditions. `commitBlockSynchronization` finalizes lease recovery with new generation stamp/length and target storage metadata.

## State and Persistence Behavior

The proto defines the wire state that drives NameNode in-memory block maps, datanode descriptors, cache state, liveness, and recovery state. Some received information leads to persistent namespace or block-map effects through NameNode edit logging and metadata updates, but the proto file itself is only a generated-code schema.

## Dependencies and Integration Points

It integrates with NameNode block management, DataNode registration, block-token key distribution, erasure-coding reconstruction commands, storage reports, HA status, rolling upgrades, full block report leasing, and slow-node/disk diagnostics. It shares common server messages from `HdfsServer.proto` and block/storage definitions from `hdfs.proto`.

## Risks and Edge Cases

Required fields make old/new compatibility sensitive; optional defaults preserve rolling-upgrade behavior for fields like `minBlockSize` in related protocols and heartbeat counters here. The command union is not enforced by protobuf, so translators must keep `cmdType` consistent with the matching optional command body. Packed block arrays and block buffers are performance-critical and easy to misinterpret. Typos in field names such as `registartion` and `newTaragets` are part of the generated API and cannot be casually renamed.

## Test Signals

Tests should cover generated translator round trips, DataNode registration and heartbeat command handling, full block report leasing, incremental block reports, cache reports, block synchronization, erasure-coding reconstruction commands, slow peer/disk fields, and protobuf compatibility with missing optional fields during rolling upgrade.
