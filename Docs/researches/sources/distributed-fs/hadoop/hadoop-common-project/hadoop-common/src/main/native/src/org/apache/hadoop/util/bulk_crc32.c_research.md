# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32.c

## Purpose
`bulk_crc32.c` implements Hadoop's native chunked CRC engine. It can compute or verify sequential CRC values over fixed-size chunks using CRC32C or zlib CRC32, with software slicing-by-8 defaults and architecture-specific function-pointer overrides.

## Important APIs, types, and functions
The public API is `bulk_crc`. Global function pointers `pipelined_crc32c_func` and `pipelined_crc32_zlib_func` default to software helpers and may be overwritten by CPU-specific constructor code. Important helpers include `store_or_verify`, `crc_val`, `crc32c_sb8`, `crc32_zlib_sb8`, `pipelined_crc32c_sb8`, and `pipelined_crc32_zlib_sb8`. Lookup-table dependencies are `crc32c_tables.h` and `crc32_zlib_polynomial_tables.h`.

## Control flow
`bulk_crc` determines whether it is computing or verifying from whether `error_info` is null, selects the polynomial implementation, processes complete chunks three at a time through the pipelined function, handles one or two remaining full chunks, then handles a smaller final chunk. Each raw CRC starts at `0xffffffff`, is finalized by bitwise inversion, converted with `ntohl`, and stored or compared. On mismatch, it fills `crc32_error_t` with got/expected values and a pointer to the failing data chunk.

## State and persistence
Only the two global function pointers are process state. They start as portable software implementations and may be changed during library load by architecture files. The caller owns data and checksum storage.

## Dependencies and integration points
This file is called by `NativeCrc32.c` and native tests. CMake links the matching architecture source for x86, AArch64, or RISC-V so constructors can replace the default implementation when CPU support is detected.

## Risks and test signals
Risks include unaligned 32-bit loads in slicing-by-8 code, endian conversion compatibility with Java checksum layout, function-pointer initialization races at load time, invalid checksum type handling, and relying on callers to size `sums` correctly. Test signals include `test_bulk_crc32`, Java `DataChecksum` tests, CRC32 and CRC32C vectors, one-byte chunks, final remainders, mismatch reporting, and architecture-specific accelerator parity against software.
