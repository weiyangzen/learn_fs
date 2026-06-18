<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDataChecksum.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDataChecksum.java

## Purpose

`TestDataChecksum.java` validates chunked checksum calculation and verification for `DataChecksum` over direct and heap buffers.

## Important APIs, Types, and Functions

It uses `DataChecksum.newDataChecksum`, `calculateChunkedSums`, `verifyChunkedSums`, `ChecksumException`, helper `Harness`, `directify`, `corruptBufferOffset`, `uncorruptBufferOffset`, and tests for CRC32/CRC32C equality/string behavior.

## Control Flow

`testBulkOps` iterates CRC32 and CRC32C, data lengths around chunk boundaries, and direct/heap buffer modes. The harness creates buffers with leading/trailing padding, calculates checksums, verifies good data, corrupts padding to ensure it is ignored, corrupts checksum bytes at beginning/end to assert failure positions, and resets buffers for each variant.

## State and Persistence Behavior

State is in-memory byte buffers and checksum objects. No persistence exists.

## Dependencies and Integration Points

It integrates with Hadoop checksum code, native or pure Java CRC implementations through `DataChecksum`, Java `ByteBuffer`, and `ChecksumException` position reporting.

## Risks and Edge Cases

Important risks are wrong buffer position/limit handling, direct-buffer parity with heap arrays, off-by-one data lengths, checksum trailer padding, and incorrect error positions.

## Test Signals

Signals include successful verification for valid sums, ignored corruption outside active ranges, expected `ChecksumException` positions for first/last checksum corruption, and CRC32-specific behavior checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestDataChecksum.java -->
