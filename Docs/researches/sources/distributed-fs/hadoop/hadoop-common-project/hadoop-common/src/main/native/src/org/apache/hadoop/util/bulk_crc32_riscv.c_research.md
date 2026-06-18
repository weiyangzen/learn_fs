# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_riscv.c

## Purpose
`bulk_crc32_riscv.c` adds a RISC-V 64-bit zlib CRC32 accelerator using the Zbc carry-less multiply extension. It only accelerates the zlib polynomial path; CRC32C remains on the default implementation.

## Important APIs, types, and functions
Key helpers are `rv_clmul`, `rv_clmulh`, `rv_crc32_zlib_bitwise`, `rv_crc32_zlib_clmul`, and `pipelined_crc32_zlib`. Constants such as `RV_CRC32_CONST_R3`, `RV_CRC32_CONST_R4`, `RV_CRC32_CONST_R5`, and `RV_CRC32_POLY_TRUE_LE_FULL` drive folding and reduction. The constructor `init_cpu_support_flag` parses `/proc/cpuinfo` for `zbc` before assigning `pipelined_crc32_zlib_func`.

## Control flow
The accelerated CRC handles small buffers with a bitwise fallback, aligns the input to a 16-byte boundary, seeds two 64-bit lanes with the initial CRC, folds 16-byte blocks with `clmul` and `clmulh`, performs final reduction to a 32-bit CRC, and processes any remaining bytes bitwise. The pipelined wrapper calls that routine for one, two, or three chunks.

## State and persistence
The only persistent process state is the optional replacement of `pipelined_crc32_zlib_func`. Per-call state is local CRC lanes and pointers.

## Dependencies and integration points
It depends on a RISC-V 64-bit compiler that accepts inline `.option arch, +zbc`, `/proc/cpuinfo` availability, `bulk_crc32.h`, and the shared `bulk_crc32.c` function-pointer hooks. CMake selects this source on RISC-V builds.

## Risks and test signals
Risks include fragile feature detection by substring search, Linux-specific `/proc/cpuinfo` dependency, strict-aliasing/alignment concerns around 64-bit loads, absence of CRC32C acceleration, and correctness of polynomial constants. Test signals include software parity for varied lengths and alignments, systems with and without `zbc`, cross-checking zlib CRC vectors, and performance tests that confirm the constructor actually selects the accelerator.
