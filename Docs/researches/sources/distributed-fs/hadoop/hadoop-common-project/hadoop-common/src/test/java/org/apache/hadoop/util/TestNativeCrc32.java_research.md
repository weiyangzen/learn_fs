# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestNativeCrc32.java

Purpose: parameterized tests for native CRC32/CRC32C chunk verification and calculation entry points.

Important APIs and types: `NativeCrc32`, `DataChecksum.Type.CRC32`, `DataChecksum.Type.CRC32C`, `DataChecksum.newDataChecksum`, direct and heap `ByteBuffer`, `ChecksumException`, and JUnit `@ParameterizedTest`.

Control flow: setup skips all cases unless native CRC is available, reads bytes-per-checksum from configuration, and creates a checksum object. Tests verify success and failure for direct-buffer verification, odd bytes-per-checksum verification, heap-array verification, direct/array calculation APIs, and deprecated `nativeVerifyChunkedSums`. Helpers fill data buffers with monotonic byte values and write either matching or deliberately shifted checksum ints.

State and persistence: state is per-test data and checksum buffers. `flip()` boundaries and buffer positions are part of the tested contract.

Dependencies and integration points: covers native code paths used by HDFS checksum verification with both CRC algorithms and both memory layouts.

Risks: native availability makes coverage conditional; direct-buffer offsets, odd-size chunk tails, checksum type IDs, and byte-array positions are common bug sites. Test signals are no-exception success cases and `ChecksumException` for invalid checksums.
