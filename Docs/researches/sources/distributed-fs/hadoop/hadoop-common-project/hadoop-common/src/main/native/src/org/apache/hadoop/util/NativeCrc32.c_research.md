# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/NativeCrc32.c

## Purpose
`NativeCrc32.c` is the JNI bridge between Java `NativeCrc32`/`DataChecksum` and the native `bulk_crc` engine. It computes or verifies chunked CRC32 and CRC32C checksums for direct `ByteBuffer`s and Java byte arrays.

## Important APIs, types, and functions
The primary exported method is `nativeComputeChunkedSums`; wrappers include `nativeVerifyChunkedSums` and `nativeComputeChunkedSumsByteArray`. Helpers are `convert_java_crc_type` and `throw_checksum_exception`, which constructs `org.apache.hadoop.fs.ChecksumException`. The code accepts Hadoop checksum constants and maps them to `CRC32_ZLIB_POLYNOMIAL` or `CRC32C_POLYNOMIAL`.

## Control flow
For direct buffers, the method validates non-null buffers, direct-address availability, nonnegative offsets/lengths, and positive `bytes_per_checksum`; then it casts checksum storage to `uint32_t *` and calls `bulk_crc` either in compute or verify mode. For byte arrays, it uses `GetPrimitiveArrayCritical` in bounded iterations of about 1 MiB of data to avoid long critical sections. Verification failures are translated into `ChecksumException` with filename, absolute data position, expected CRC, and observed CRC.

## State and persistence
The JNI layer has no persistent state. It mutates the supplied checksum buffer or array in compute mode and reads it in verify mode. Byte-array critical sections are released after every iteration.

## Dependencies and integration points
It depends on Hadoop-generated JNI headers, `bulk_crc32.h`, branch prediction macros, Java `NativeCrc32`, `DataChecksum`, and `ChecksumException`. It is the high-performance path used by checksum calculation and verification in Hadoop I/O.

## Risks and test signals
Risks include missing upper-bound validation for offsets against actual buffer/array length, unaligned `uint32_t *` checksum casts, JNI critical-section constraints, endian assumptions via `bulk_crc`, and assertion failures if `bulk_crc` returns an unexpected code. Test signals include direct and heap byte-array checksum tests, invalid checksum type, null/non-direct buffers, partial final chunks, intentional checksum mismatch position, and large arrays that require multiple critical-section iterations.
