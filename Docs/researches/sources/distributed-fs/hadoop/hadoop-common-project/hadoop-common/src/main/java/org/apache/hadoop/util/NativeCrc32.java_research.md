# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/NativeCrc32.java

## Purpose

`NativeCrc32` exposes native CRC32/CRC32C checksum calculation and verification routines used by Hadoop data paths when native code is available and the platform is supported.

## Important APIs, Types, And Functions

The class declares native methods for chunked checksum calculation and verification over byte arrays or direct buffers. Java wrappers pass buffer positions, lengths, file names, base offsets, and a verify/calculate flag through to JNI. It also exposes checksum constants copied from `DataChecksum`.

## Control Flow, State, And Persistence

`isAvailable()` returns false on SPARC and otherwise follows `NativeCodeLoader.isNativeCodeLoaded()`. Calculation and verification methods delegate directly to JNI and do not mutate buffer position, limit, or mark. Checksum mismatch is surfaced as `ChecksumException`. There is no Java mutable state or persistence.

## Dependencies And Integration Points

It depends on `DataChecksum`, `ChecksumException`, `ByteBuffer`, native Hadoop libraries loaded through `NativeCodeLoader`, and JNI symbols. It integrates with HDFS block read/write and local filesystem checksum verification.

## Risks And Test Signals

Native/Java behavior must match exactly across endian, direct-buffer, and byte-array paths. Tests should compare native results with Java checksum implementations, cover invalid checksum size/type, buffer offset/length boundaries, direct and heap buffers, and disabled-native fallback.
