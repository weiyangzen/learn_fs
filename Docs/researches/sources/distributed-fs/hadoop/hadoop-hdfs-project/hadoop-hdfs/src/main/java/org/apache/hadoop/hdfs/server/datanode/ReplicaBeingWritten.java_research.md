<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBeingWritten.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBeingWritten.java

## Purpose

`ReplicaBeingWritten` represents an RBW replica created by a client write pipeline. It is a local in-pipeline replica whose visible bytes are the bytes already acknowledged by the pipeline.

## Important APIs, Types, And Functions

- Constructors support zero-length creation with reserved space, creation from a `Block` plus writer thread, explicit block id/length/generation stamp, and copy construction.
- `getVisibleLength()` returns `getBytesAcked()`, not the full bytes received or reserved.
- `getState()` returns `ReplicaState.RBW`.
- Equality and hash code delegate to the superclass implementation.

## Control Flow

Creation delegates to `LocalReplicaInPipeline`, which owns writer tracking, reservation, and local file paths. During reads, consumers use visible length so only acknowledged bytes are exposed. State-based dispatch in `ReplicaBuilder` creates this type for `RBW`.

## State And Persistence

Persistent bytes and metadata are stored in local block and meta files managed by the superclass. Runtime state includes the writer thread, bytes acknowledged, bytes on disk, and disk reservation inherited from `LocalReplicaInPipeline`.

## Dependencies And Integration Points

It integrates with write pipelines, block receivers, volume space reservation, and replica-state transitions to finalized or recovery states. `ReplicaBuilder.buildRBW()` enforces compatible copy construction and writer requirements for some paths.

## Risks And Edge Cases

The distinction between acknowledged bytes and bytes on disk is safety-critical. Exposing bytes received but not acknowledged can violate client write semantics. Copy construction requires the source actually be RBW; incompatible state is rejected by the builder.

## Test Signals

Tests should verify RBW state, visible-length updates through acked-byte changes, reservation behavior, writer-thread preservation, and transitions to finalized or recovery paths after pipeline interruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBeingWritten.java -->
