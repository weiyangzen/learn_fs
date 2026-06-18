# File Research: sources/cow-pools/bcachefs-tools/linux/siphash.c

## Purpose
Linux SipHash/HalfSipHash implementation for keyed hash/PRF use.

## Key Responsibilities
- Implements SipHash2-4 for secure 64-bit keyed hashing.
- Implements HalfSipHash1-3 / SipHash1-3 variants for hash-table use.
- Provides aligned and, when needed, unaligned implementations.
- Provides fixed-argument helpers for 1-4 `u64` and selected `u32` inputs.

## Important APIs
- `__siphash_aligned()`, `__siphash_unaligned()`
- `siphash_1u64()` through `siphash_4u64()`
- `siphash_1u32()`, `siphash_3u32()`
- `__hsiphash_aligned()`, `__hsiphash_unaligned()`
- `hsiphash_1u32()` through `hsiphash_4u32()`

## Implementation Notes
- 64-bit builds implement HalfSipHash using a reduced-round 64-bit SipHash path for performance.
- 32-bit builds implement true 32-bit HalfSipHash rounds.
- Tail bytes are folded with little-endian loads or byte-by-byte switch fallthrough.
- Exports symbols for kernel-compatible linkage.

## Dependencies
Uses `linux/siphash.h`, bit operations, unaligned access helpers, and optional word-at-a-time dcache helpers.
