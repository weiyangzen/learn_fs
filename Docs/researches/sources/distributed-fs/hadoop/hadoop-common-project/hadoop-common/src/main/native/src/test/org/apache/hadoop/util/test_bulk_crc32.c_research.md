# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/test/org/apache/hadoop/util/test_bulk_crc32.c

## Purpose
`test_bulk_crc32.c` is the native unit and timing test for `bulk_crc`. It verifies that compute mode followed by verify mode succeeds for multiple CRC algorithms, data lengths, and bytes-per-checksum settings, then prints simple timing results.

## Important APIs, types, and functions
The test uses `bulk_crc`, `CRC32C_POLYNOMIAL`, `CRC32_ZLIB_POLYNOMIAL`, and `crc32_error_t`. Helpers are `testBulkVerifyCrc`, `timeBulkCrc`, and `EXPECT_ZERO`.

## Control flow
Each verification test allocates deterministic byte data, allocates enough checksum entries, computes checksums, verifies the same data, and frees memory. `main` covers 4096-byte buffers, 256-byte buffers with one-byte chunks, tiny one/two/seventeen-byte cases, and both CRC types where specified. It then runs two high-iteration timing loops over 16 KiB data with 512-byte chunks.

## State and persistence
The test owns temporary heap buffers and writes timing output to stdout/stderr. No state persists after process exit.

## Dependencies and integration points
It links against `bulk_crc32.c` and the selected architecture-specific CRC implementation in the native CMake test target. It validates both software and hardware-dispatched paths depending on host CPU support.

## Risks and test signals
Risks include no negative mismatch test, no malloc failure checks, and performance loops that can be long on slow machines. Passing output is a strong smoke signal for compute/verify consistency across chunk sizes and both polynomial constants, but it does not prove known-vector correctness independently of compute mode.
