<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumReconstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumReconstructor.java

## Purpose

`StripedBlockChecksumReconstructor` is the abstract base for computing checksums for missing striped internal blocks without writing reconstructed data to target DataNodes. It reconstructs data into a buffer and feeds chunk checksums into subclass-specific digesters.

## Important APIs, Types, And Functions

- Constructor accepts worker, reconstruction info, output buffer, and requested block length.
- `init()` initializes decoder, optional validator, reader, target buffer, max target length, and checksum buffers.
- `reconstruct()` loops over the requested length: read minimum sources, decode target data, checksum reconstructed output, update position, and clear buffers.
- Abstract hooks: `prepareDigester`, `updateDigester`, `commitDigest`, and `getDigestObject`.
- `getChecksumDataLen()` reports produced checksum byte count.

## Control Flow

The loop stops when requested length is consumed or target length ends. For each chunk, `StripedReader` supplies inputs; `reconstructTargets` decodes one target index into `targetBuffer`; `checksumWithTargetOutput` handles full and partial checksum chunks before calling the subclass digester.

## State And Persistence

State includes the target buffer, target indices, checksum buffer, checksum writer, checksum-data length, and remaining requested length. It does not write block data; the only output is checksum/digest bytes in memory.

## Dependencies And Integration Points

It reuses `StripedReconstructor`, `StripedReader`, raw erasure decoder, optional decoding validator, `DataChecksum`, and `DataOutputBuffer`. Subclasses implement composite CRC and MD5-of-CRC formats.

## Risks And Edge Cases

Only one output buffer is allocated even though `targetIndices` can contain multiple values; callers must use it consistently for checksum reconstruction scenarios. Partial-length handling copies data and recomputes partial CRCs, which is easy to get wrong. Direct-buffer extraction must preserve buffer position/limit semantics.

## Test Signals

Tests should cover requested length smaller than, equal to, and larger than buffer size; partial checksum chunks; validation enabled/disabled; direct buffers; multiple EC policies; and cleanup of reader/decoder buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumReconstructor.java -->
