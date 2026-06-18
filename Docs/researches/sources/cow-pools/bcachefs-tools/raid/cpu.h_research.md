# File Research: sources/cow-pools/bcachefs-tools/raid/cpu.h

## Purpose
x86 CPU feature detection and microarchitecture heuristics for RAID implementation selection.

## Key Responsibilities
- Wraps `cpuid` and `xgetbv`.
- Extracts CPU vendor, family, and model.
- Detects SSE2, SSSE3, CRC32, AVX2, and AVX512BW capability.
- Checks OS XSAVE/XCR0 state before enabling AVX/AVX512 paths.
- Detects Intel Atom and related slow-operation heuristics.
- Detects slow extended SSE register cases, especially AMD Bulldozer and some Intel Atom models.

## Important APIs
- `raid_cpu_has_sse2()`
- `raid_cpu_has_ssse3()`
- `raid_cpu_has_crc32()`
- `raid_cpu_has_avx2()`
- `raid_cpu_has_avx512bw()`
- `raid_cpu_has_slowmult()`
- `raid_cpu_has_slowextendedreg()`

## Dependencies
Only active under `CONFIG_X86`; relies on inline assembly.
