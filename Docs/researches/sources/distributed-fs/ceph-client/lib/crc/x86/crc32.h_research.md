# sources/distributed-fs/ceph-client/lib/crc/x86/crc32.h

## Purpose
This x86 arch header selects optimized CRC32 LE and CRC32C implementations using PCLMULQDQ, VPCLMULQDQ, SSE4.2 CRC32 instructions, and a long-buffer three-way CRC32C combiner.

## Important APIs, Types, and Functions
It defines static keys `have_crc32`, `have_pclmulqdq`, and `have_vpclmul_avx512`, declares `crc32_lsb` PCLMUL functions, defines `crc32_le_arch()`, `crc32c_arch()`, `crc32_mod_init_arch()`, and `crc32_optimizations_arch()`, and declares `crc32c_x86_3way()`.

## Control Flow
CRC32 LE first tries `CRC_PCLMUL()` and otherwise falls back to `crc32_le_base()`. CRC32C requires SSE4.2 CRC32 support; for long x86_64 buffers with usable FPU and PCLMUL, it uses either AVX512 VPCLMUL or `crc32c_x86_3way()`. Otherwise it emits scalar `crc32{q,l,w,b}` instructions over full words and tail bytes. Init enables static keys and updates the CRC32 LSB static call to AVX512 or AVX2 when supported.

## State and Persistence
Runtime feature state is persisted in static keys and a static-call target. Per-call state is local CRC, pointer, length, and loop counters.

## Dependencies and Integration Points
It depends on x86 CPU features, kernel FPU APIs, the PCLMUL template, and the scalar CRC32 instruction. It integrates with generic CRC32 hooks; CRC32 BE remains the base implementation on x86.

## Risks and Test Signals
Risks include FPU use in disallowed contexts, threshold regressions, unaligned word casts, static-branch feature mismatches, and differences between CRC32C scalar and PCLMUL-combined paths. KUnit CRC32/CRC32C, irq-context tests, and CPU feature matrix testing are required.
