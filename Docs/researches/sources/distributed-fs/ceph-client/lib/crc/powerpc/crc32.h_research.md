# sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/powerpc/crc32.h` dispatches PowerPC CRC32C to VPMSUM vector crypto acceleration. Plain little- and big-endian CRC32 remain generic on this architecture header.

## Important APIs, Types, and Functions

It defines `VMX_ALIGN`, `VMX_ALIGN_MASK`, `VECTOR_BREAKPOINT`, static key `have_vec_crypto`, assembly declaration `__crc32c_vpmsum`, inline `crc32c_arch`, `crc32_mod_init_arch`, and `crc32_optimizations_arch`. `crc32_le_arch` and `crc32_be_arch` alias to generic base functions.

## Control Flow

`crc32c_arch()` falls back to generic for short buffers, missing vector crypto, or disallowed SIMD. Otherwise it consumes a generic prealignment prefix, disables preemption and page faults, enables kernel Altivec, calls `__crc32c_vpmsum()` on the aligned multiple, disables Altivec, then finishes the tail generically. Init enables the static key on POWER8-class vector crypto support.

## State and Persistence Behavior

Persistent state is the static key. Vector state is protected per call by preemption/pagefault disabling and Altivec context management.

## Dependencies and Integration Points

Dependencies include PowerPC SIMD context helpers, feature flags, generic CRC32C base code, and `powerpc/crc32c-vpmsum_asm.S`.

## Risks and Edge Cases

Only CRC32C is accelerated, so optimization reporting must not claim CRC32 LE/BE. Alignment splitting and tail handling must preserve generic semantics. SIMD context misuse can corrupt vector state or fault in disabled contexts.

## Test Signals

Signals include CRC32C generic equivalence across unaligned, threshold, and tail lengths; fallback without vector crypto; `crc32_optimizations()` reporting only CRC32C; and PPC vector context stress tests.

## Read Coverage

Source read size: 70 lines, 1757 bytes.
