<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInPipeline.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInPipeline.java

## Purpose

`ReplicaInPipeline` is the interface for replicas currently participating in a write pipeline. It extends `Replica` with writer, acknowledgement, disk-length, reservation, checksum, and stream operations needed by `BlockReceiver`.

## Important APIs, Types, And Functions

- Writer lifecycle: `setWriter`, `getWriter`, `interruptThread`, `stopWriter`, and `attemptToSetWriter`.
- Length tracking: `setNumBytes`, `getBytesAcked`, `setBytesAcked`, `getBytesOnDisk`, `setLastChecksumAndDataLen`, `getLastChecksumAndDataLen`.
- Space accounting: `getBytesReserved()` and `releaseAllBytesReserved()`.
- Stream creation: `createStreams(boolean isCreate, DataChecksum requestedChecksum)` returns `ReplicaOutputStreams`.
- `getReplicaInfo()` exposes the concrete `ReplicaInfo`.

## Control Flow

Write-pipeline code uses this contract to claim a writer, append data and checksums, update acked and disk lengths, and release reservations. Recovery and interruption paths can stop or replace the writer and inspect the last partial chunk checksum state.

## State And Persistence

Implementations persist block data and metadata through output streams and maintain mutable in-memory state for writer ownership, bytes acked, bytes on disk, reserved bytes, and last checksum information.

## Dependencies And Integration Points

It connects `BlockReceiver`, checksum code (`DataChecksum`), `ReplicaOutputStreams`, and the local replica hierarchy. `ReplicaBeingWritten` and temporary local pipeline replicas are the main implementations.

## Risks And Edge Cases

Writer ownership races, partial checksum handling, and reservation release are subtle. Incorrect acked-byte updates can expose uncommitted data, while leaked reservations can make a volume appear full.

## Test Signals

Tests should stress writer claim/replacement, interruption, stream creation for create versus append, last partial checksum propagation, reservation release on success/failure, and visible-length behavior through RBW implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaInPipeline.java -->
