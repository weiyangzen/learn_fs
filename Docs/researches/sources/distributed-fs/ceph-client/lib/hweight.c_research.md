# sources/distributed-fs/ceph-client/lib/hweight.c

## Purpose
`hweight.c` implements software Hamming-weight/popcount helpers for 8-, 16-, 32-, and 64-bit words. These are fallback routines for architectures or call sites that do not use faster native popcount instructions.

## Important APIs, Types, and Functions
The exported functions are `__sw_hweight8()`, `__sw_hweight16()`, `__sw_hweight32()`, and `__sw_hweight64()`. The 32- and 64-bit versions have `CONFIG_ARCH_HAS_FAST_MULTIPLIER` paths that use multiplication by byte-summing constants; fallback paths use shift/add reductions.

## Control Flow, State, and Persistence
Each function is pure arithmetic with no persistent state. The algorithms fold adjacent bit counts into fields using masks, then sum fields to produce the number of set bits. On 32-bit `BITS_PER_LONG`, `__sw_hweight64()` computes the sum of two 32-bit halves; on 64-bit it processes the full word directly.

## Dependencies and Integration Points
The file includes `<linux/bitops.h>`, `<asm/types.h>`, and exports generic software helpers used by bitops implementations and callers needing architecture-independent popcount behavior.

## Risks and Test Signals
Risks are low but include type-width assumptions, constant suffix correctness on 32- versus 64-bit builds, and configuration-specific code paths. Tests should compare all functions against compiler builtins or exhaustive ranges for 8/16-bit, plus representative 32/64-bit patterns such as zero, all ones, alternating bits, single-bit values, and random values on both fast-multiplier and fallback builds.
