<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReportBadBlockAction.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReportBadBlockAction.java

## Purpose

`ReportBadBlockAction` is a `BPServiceActorAction` that reports a bad local block to the NameNode. It packages block, storage UUID, storage type, and DataNode registration into a `LocatedBlock` for the `reportBadBlocks` RPC.

## Important APIs, Types, And Functions

- Constructor stores `ExtendedBlock`, storage UUID, and `StorageType`.
- `reportTo(DatanodeProtocolClientSideTranslatorPB, DatanodeRegistration)` builds a single-element `LocatedBlock[]` and calls `bpNamenode.reportBadBlocks`.
- `RemoteException` is logged but not rethrown; other `IOException` instances are wrapped in `BPServiceActorActionException`.
- `equals`, `hashCode`, and `toString` make actions comparable and loggable.

## Control Flow

If the block-pool registration is null, the action returns immediately. Otherwise it creates a `DatanodeInfo` from the registration, associates the storage UUID and type, and sends the bad-block report. Remote NameNode-side exceptions are logged as informational events, while transport/local I/O failures propagate as action failures.

## State And Persistence

The action is immutable after construction. It does not persist data locally; its only durable effect is the NameNode receiving and processing a bad-block report.

## Dependencies And Integration Points

It is issued by DataNode block-pool service logic and uses the protocol translator, `DatanodeRegistration`, `LocatedBlock`, `DatanodeInfoBuilder`, and storage metadata. `VolumeScanner.ScanResultHandler` can ultimately trigger bad-block reporting through `DataNode.handleBadBlock`.

## Risks And Edge Cases

Ignoring `RemoteException` can hide NameNode rejection from callers, relying on logs for diagnostics. Null storage UUID or type can be encoded and compared but may reduce NameNode-side precision. Equality includes storage identity, so duplicate reports for the same block on different storage are distinct.

## Test Signals

Tests should verify null-registration no-op, correct `LocatedBlock` construction, RPC invocation, `RemoteException` logging behavior, wrapping of generic I/O failures, and equality/hash behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReportBadBlockAction.java -->
