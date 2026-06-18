# sources/distributed-fs/ceph-client/lib/xz/xz_crc32.c

## Purpose
Implements a compact internal IEEE 802.3 CRC32 routine for XZ decoder environments that do not use the kernel `crc32_le` helper, especially preboot decompression.

## APIs and control flow
`xz_crc32_init` fills `xz_crc32_table[256]` with the reflected polynomial `0xEDB88320`. `xz_crc32` complements the input CRC, table-folds each byte, and complements the final result.

## State, dependencies, and integration
The mutable state is the static CRC table, optionally marked by `STATIC_RW_DATA` for preboot placement. It includes `xz_private.h`; `xz_stream.h` can instead map `xz_crc32` to kernel CRC32 depending on build macros. The stream decoder uses this for header, footer, block, index, and check validation.

## Risks and test signals
Internal builds must initialize the table before validation. The implementation is small but slower than larger optimized CRC implementations. Tests should include known CRC vectors, `.xz` header/footer checks, full CRC32-checked stream decodes, and preboot initialization-order coverage.
