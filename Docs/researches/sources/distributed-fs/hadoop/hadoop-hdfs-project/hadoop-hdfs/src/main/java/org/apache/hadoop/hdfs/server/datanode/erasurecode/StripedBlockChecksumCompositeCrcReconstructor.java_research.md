<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumCompositeCrcReconstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumCompositeCrcReconstructor.java

## Purpose

`StripedBlockChecksumCompositeCrcReconstructor` computes a composite CRC for a missing striped internal block by reconstructing data in memory and composing chunk CRCs using EC cell boundaries.

## Important APIs, Types, And Functions

- Extends `StripedBlockChecksumReconstructor`.
- Stores EC policy cell size for striped CRC composition.
- `prepareDigester()` creates a `CrcComposer` with checksum type, bytes-per-checksum, and cell size.
- `updateDigester(byte[], int)` feeds chunk CRC bytes and their data length into the composer.
- `commitDigest()` writes the final composed digest to the checksum writer and exposes it through `getDigestObject()`.

## Control Flow

The base class reconstructs chunks and calculates CRC bytes over reconstructed output. This subclass initializes the striped composer before the loop, updates it for each chunk or partial chunk, and commits the final digest after requested length is processed.

## State And Persistence

Runtime state is `ecPolicyCellSize`, `digestValue`, and `digester`. The only output persistence is bytes written to the supplied `DataOutputBuffer`.

## Dependencies And Integration Points

It depends on `CrcComposer`, DataNode EC reconstruction infrastructure, `DataOutputBuffer`, and the checksum settings discovered by `StripedReader`. It serves checksum RPC paths that request composite CRCs for striped blocks.

## Risks And Edge Cases

Calling update or commit before preparation throws `IOException`. Partial chunks must pass the correct data length so composite CRC math remains valid. Cell-size mismatch would produce incorrect block checksums.

## Test Signals

Tests should compare reconstructed composite CRCs with known full-block checksums, cover partial requested lengths, direct and heap buffers, missing digester misuse, and policies with varied cell and checksum sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumCompositeCrcReconstructor.java -->
