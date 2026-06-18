# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_aarch64.c

## Purpose
`bulk_crc32_aarch64.c` provides AArch64 hardware-accelerated implementations for Hadoop's bulk CRC engine. It replaces the portable slicing-by-8 functions when the CPU advertises CRC32 instructions.

## Important APIs, types, and functions
Static functions `pipelined_crc32c` and `pipelined_crc32_zlib` process one to three independent blocks with ARMv8 CRC instructions. Inline-assembly macros include `LDP`, `CRC32CX`, `CRC32CW`, `CRC32CH`, `CRC32CB`, and zlib-polynomial variants `CRC32ZX`, `CRC32ZW`, `CRC32ZH`, `CRC32ZB`. The constructor `init_cpu_support_flag` checks `getauxval(AT_HWCAP)` and `HWCAP_CRC32`.

## Control flow
The pipelined functions receive initial CRC values and a contiguous data region containing one, two, or three blocks. They use a switch on `num_blocks`, process most data with 128-bit pair loads and 64-bit CRC operations, then consume remaining 8-, 4-, 2-, and 1-byte tails. On library load, if hardware support is present, the file assigns `pipelined_crc32c_func` and `pipelined_crc32_zlib_func` to these accelerated functions.

## State and persistence
The only state mutation is updating the global function pointers declared in `bulk_crc32.c`. No per-call state persists beyond output CRC values.

## Dependencies and integration points
It depends on AArch64 assembler support, Linux auxiliary-vector hardware capabilities, `bulk_crc32.h`, and branch prediction macros. CMake selects this file for AArch64 native builds.

## Risks and test signals
Risks include assembler compatibility, unaligned loads in tail handling, incorrect `HWCAP_CRC32` definitions on non-Linux platforms, and any mismatch between ARM CRC instructions and Hadoop's expected polynomial/endian layout. Test signals include disassembly/performance checks noted in comments, `test_bulk_crc32` on CRC-capable and non-capable AArch64 CPUs, odd chunk sizes, and parity against software fallback.
