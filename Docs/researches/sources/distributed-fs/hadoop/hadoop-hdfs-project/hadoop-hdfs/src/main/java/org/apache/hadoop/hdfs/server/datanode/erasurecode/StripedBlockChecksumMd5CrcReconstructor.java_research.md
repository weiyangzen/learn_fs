<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumMd5CrcReconstructor.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumMd5CrcReconstructor.java

## Purpose

`StripedBlockChecksumMd5CrcReconstructor` computes the legacy MD5-of-CRC digest for a missing striped internal block by reconstructing data and digesting the generated chunk CRC bytes.

## Important APIs, Types, And Functions

- Extends `StripedBlockChecksumReconstructor`.
- `prepareDigester()` obtains an `MD5Hash` message digester.
- `updateDigester(byte[], int)` feeds CRC bytes to the MD5 digest; the data length parameter is irrelevant for MD5-of-CRC.
- `commitDigest()` creates an `MD5Hash`, writes it to the checksum output, and exposes it via `getDigestObject()`.

## Control Flow

The base class reads minimum EC sources, decodes the target data, and calculates chunk checksums. This subclass wraps those checksum bytes in a running MD5 digest and commits after the requested block length is covered.

## State And Persistence

Runtime state is the `MessageDigest` and final `MD5Hash`. Output is written to the provided `DataOutputBuffer`; no block files are modified.

## Dependencies And Integration Points

It integrates with HDFS block checksum RPC behavior, `MD5Hash`, `DataOutputBuffer`, and the generic striped checksum reconstruction base.

## Risks And Edge Cases

Update or commit before prepare raises `IOException`. Partial requested lengths rely on the base class to calculate partial CRC bytes correctly. MD5-of-CRC is format-sensitive, so changing checksum chunk ordering breaks compatibility.

## Test Signals

Tests should compare against checksums from available blocks, cover partial final chunks, multiple requested lengths, digest object exposure, and missing digester error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedBlockChecksumMd5CrcReconstructor.java -->
