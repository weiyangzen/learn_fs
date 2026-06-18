# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/util/bulk_crc32_x86.c

## Purpose
`bulk_crc32_x86.c` provides an x86 SSE4.2 hardware implementation for the CRC32C path in Hadoop's bulk CRC engine. It avoids requiring a global `-msse4.2` compiler flag by using inline assembly and runtime CPU detection.

## Important APIs, types, and functions
Important helpers include `cpuid`, inline `_mm_crc32_u64`, `_mm_crc32_u32`, `_mm_crc32_u16`, `_mm_crc32_u8` shims, and the 64-bit or 32-bit `pipelined_crc32c` implementation selected at compile time. The constructor checks `CPUID_FEATURES` bit `SSE42_FEATURE_BIT` and assigns `pipelined_crc32c_func` when available.

## Control flow
At load time, CPUID determines whether SSE4.2 CRC instructions are supported. During CRC calculation, the pipelined function processes one to three chunks in lockstep, using `crc32q` on 64-bit builds or `crc32l` on 32-bit builds for full machine words, then byte-level CRC instructions for the remainder.

## State and persistence
State is limited to the global `pipelined_crc32c_func` pointer in `bulk_crc32.c`. The implementation does not accelerate zlib CRC32 on x86.

## Dependencies and integration points
It depends on GCC-style inline x86 assembly, CPUID, `bulk_crc32.h`, and branch prediction macros. It is linked for x86 native builds and consumed through the shared `bulk_crc` dispatch.

## Risks and test signals
Risks include inline assembly constraints, PIC handling on 32-bit EBX, unaligned machine-word loads, only accelerating CRC32C, and CPU feature detection in virtualized environments. Test signals include 32-bit and 64-bit builds, CPUs with and without SSE4.2, `test_bulk_crc32` for many chunk sizes, and parity against the portable slicing-by-8 implementation.
