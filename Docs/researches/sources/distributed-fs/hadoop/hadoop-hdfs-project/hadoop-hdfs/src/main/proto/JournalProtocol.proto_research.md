# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/proto/JournalProtocol.proto

## Purpose

`JournalProtocol.proto` defines the private stable RPC used by an active NameNode to stream edit-log records to a remote journal receiver, historically a BackupNode, and to fence a journal receiver. The source was read as a complete 130-line file for this report.

## Important APIs, Types, and Functions

The file uses `proto2`, package `hadoop.hdfs`, Java outer class `JournalProtocolProtos`, generic services, and imports `hdfs.proto` and `HdfsServer.proto`. Messages include `JournalInfoProto`, `JournalRequestProto`, `JournalResponseProto`, `StartLogSegmentRequestProto`, `StartLogSegmentResponseProto`, `FenceRequestProto`, and `FenceResponseProto`. The service `JournalProtocolService` exposes `journal`, `startLogSegment`, and `fence`.

## Control Flow

The active NameNode sends `journal` requests containing journal identity, first transaction ID, transaction count, serialized edit-log bytes, and epoch. It sends `startLogSegment` when rolling to a new edit-log segment. A fencing request supplies journal info, epoch, and optional debug info; the receiver replies with previous epoch, last transaction ID, and whether it is in sync.

## State and Persistence Behavior

The protocol carries serialized edit-log records that are persisted by the receiver. Epoch fields fence stale writers and protect against split-brain edit-log streams. Journal identity ties the stream to cluster/layout/namespace information.

## Dependencies and Integration Points

It integrates with NameNode edit log output streams, BackupNode/checkpointing infrastructure, journal receivers, storage layout information, and failover fencing. It shares storage and edit-log manifest types through `HdfsServer.proto`.

## Risks and Edge Cases

Incorrect epoch handling can allow stale writes. `records` is opaque serialized edit-log data, so sender and receiver must agree on edit-log layout. Optional fields in `JournalInfoProto` and `FenceResponseProto` require careful default handling. Transaction ID and count mismatches can corrupt or reject journal streams.

## Test Signals

Tests should cover streaming edits, starting new log segments, fencing stale writers, transaction count validation, epoch monotonicity, receiver restart recovery, and mixed-version behavior for optional journal info fields.
