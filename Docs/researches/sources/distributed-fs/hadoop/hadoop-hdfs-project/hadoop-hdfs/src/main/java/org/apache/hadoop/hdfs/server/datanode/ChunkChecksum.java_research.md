# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ChunkChecksum.java

## Purpose

`ChunkChecksum` is a small immutable holder for the checksum bytes of the last checksum chunk and the data length at which that checksum applies. It lets write-side or replica state hand a coherent partial-chunk checksum to `BlockSender`.

## Important APIs, types, and functions

- `ChunkChecksum(long dataLength, byte[] checksum)` stores the visible data length and checksum bytes. The checksum may be `null` when unavailable.
- `getDataLength()` returns the block length associated with the checksum.
- `getChecksum()` returns the raw checksum byte array.

## Control flow

The class has no internal branching. `BlockSender` consumes it during construction to determine the safe readable end offset and during the last data packet to overwrite the last checksum read from disk with the current in-memory checksum when needed.

## State and persistence behavior

The holder is immutable by field reference, but it does not defensively copy the checksum array. Callers must treat the byte array as stable or avoid mutating it after construction. It does not perform I/O or persistence.

## Dependencies and integration points

`ChunkChecksum` is in the DataNode package and is used by `ReplicaInPipeline.getLastChecksumAndDataLen`, `FinalizedReplica.getLastPartialChunkChecksum`, and `BlockSender`. It represents the contract between mutable replica write state and packetized read state.

## Risks and edge cases

Because `getChecksum()` exposes the backing array, accidental mutation could corrupt the checksum substituted into a read packet. A null checksum is a valid signal and must be handled by consumers by falling back to on-disk or NULL-checksum behavior. The `dataLength` must match the checksum's logical chunk end; inconsistent producer state can make `BlockSender` reject otherwise valid requested ranges.

## Test signals

Tests are mostly integration-level: RBW and finalized partial-chunk reads should verify that the last packet uses the current partial checksum and that null checksum values do not crash the sender. A focused unit test could assert simple accessor behavior, but correctness is mainly proven through `BlockSender` and replica tests.
