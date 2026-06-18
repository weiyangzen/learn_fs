# sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif-core.S` implements ARM 32-bit NEON/crypto accelerated CRC-T10DIF folding routines. It supplies both PMULL64 final CRC computation and an 8-bit polynomial-multiply fallback that emits a 16-byte folded buffer for generic finishing.

## Important APIs, Types, and Functions

Exported assembly entry points are `crc_t10dif_pmull64` and `crc_t10dif_pmull8`; local helper `__pmull16x64_p8` implements pairwise 16-by-64 polynomial multiply using 8-bit NEON multiply. Important macros are `pmull16x64_p8`, `pmull16x64_p64`, `fold_32_bytes`, `fold_16_bytes`, and `crct10dif`.

## Control Flow

The shared `crct10dif` macro handles lengths at least 16 bytes. For 256 bytes and larger, it loads the first 128 bytes, byte-swaps into polynomial coefficient order, xors the initial CRC into the high half, then folds 128-byte chunks with precomputed constants. It reduces q0-q6 into q7, folds any remaining 16-byte blocks, and uses a byte-shift table for 1..15 byte tails. The PMULL64 entry then folds the final 128-bit value to 96 bits and applies Barrett reduction to return a 16-bit CRC. The PMULL8 entry stores the final 16-byte folded vector for generic completion.

## State and Persistence Behavior

The file owns read-only fold constants, Barrett constants, byte-shift table, and a p8 permutation table. Runtime state is entirely in NEON registers and caller registers; no global mutable state is stored here.

## Dependencies and Integration Points

It depends on ARM assembler macros, NEON, PMULL/crypto extensions, and the C dispatch in `arm/crc-t10dif.h`. The C wrapper controls SIMD availability and static keys before calling these routines.

## Risks and Edge Cases

The code assumes `len >= 16` and SIMD context is already allowed. Endianness handling through `CPU_LE`, vector swaps, partial-tail table indexes, and CRC bit placement are correctness-critical. Calling without saving/restoring SIMD context would corrupt kernel FPU state.

## Test Signals

Signals include CRC-T10DIF KUnit vectors across 16, 17..31, 32..255, 256+, unaligned caller buffers handled by C path, PMULL and NEON-only feature combinations, big-endian ARM builds, and comparison with `crc_t10dif_generic()`.

## Read Coverage

Source read size: 468 lines, 15008 bytes.
