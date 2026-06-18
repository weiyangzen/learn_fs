# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.h

## Purpose
`bulk_crc32.h` defines the public C contract for Hadoop's native bulk CRC implementation. It standardizes checksum type constants, verification return codes, error reporting, and the `bulk_crc` function signature.

## Important APIs, types, and functions
Constants are `CRC32C_POLYNOMIAL`, `CRC32_ZLIB_POLYNOMIAL`, `CHECKSUMS_VALID`, `INVALID_CHECKSUM_DETECTED`, and `INVALID_CHECKSUM_TYPE`. `crc32_error_t` reports `got_crc`, `expected_crc`, and `bad_data`. `bulk_crc` computes or verifies checksums over `data_len` bytes in `bytes_per_checksum` chunks.

## Control flow
Callers pass `error_info == NULL` for compute mode, where `sums` is written. They pass non-null `error_info` for verification mode, where `sums` is read and mismatch details are filled before returning `INVALID_CHECKSUM_DETECTED`.

## State and persistence
The header declares no global state. It defines how callers share data buffers, checksum buffers, and error metadata with the implementation.

## Dependencies and integration points
The header depends on `<stdint.h>` and, on Unix, `<unistd.h>` for `size_t`. It is included by JNI checksum code, portable CRC implementation, architecture accelerators, and native tests.

## Risks and test signals
Risks include callers providing insufficient checksum storage, zero or negative chunk sizes before validation, and interpreting compute-mode error codes as verification codes. Test signals are build coverage across Unix/Windows and consumers verifying both compute and verify modes for both polynomial constants.
