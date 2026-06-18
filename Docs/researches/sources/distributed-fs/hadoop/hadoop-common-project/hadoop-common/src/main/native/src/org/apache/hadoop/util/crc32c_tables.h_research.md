# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/crc32c_tables.h

## Purpose
`crc32c_tables.h` contains the precomputed slicing-by-8 lookup tables for the software CRC32C implementation. It supplies Castagnoli-polynomial data used when no hardware CRC32C accelerator is selected.

## Important APIs, types, and functions
The header defines static `CRC32C_T8_*` lookup-table arrays. Each table has 256 32-bit entries used by `crc32c_sb8` in `bulk_crc32.c`. It does not declare functions or mutable objects.

## Control flow
There is no executable control flow. The software CRC32C loop indexes these tables for the lower and higher words of each eight-byte slice and for final tail bytes.

## State and persistence
The table data is immutable compiled state loaded with the native library. It is safe for concurrent reads and has no lifecycle.

## Dependencies and integration points
It is included by `bulk_crc32.c` and indirectly backs `NativeCrc32` when CRC32C computation falls back to software. Hardware x86 and AArch64 code should match this table-based result exactly.

## Risks and test signals
Risks include generated-table errors, mismatch with the Castagnoli polynomial expected by Hadoop's `CHECKSUM_CRC32C`, and silent corruption because the table is trusted by every software computation. Test signals include CRC32C known-answer tests, cross-checks against Java implementations, `test_bulk_crc32`, and hardware/software parity on supported CPUs.
