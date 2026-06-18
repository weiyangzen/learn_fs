<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h

## Purpose
`hash.h` provides an m68k-optimized `__hash_32()` for original 68000/010-class CPUs that lack a long multiply instruction, preserving the generic `hash_32()` behavior without using unavailable `MULU.L`.

## Important APIs, Types, and Functions
It defines `HAVE_ARCH__HASH_32` and `static inline u32 __hash_32(u32 x)`. The function multiplies by the Linux golden ratio constant using a hand-written addition/shift chain plus a 16-bit `mulu.w` on the high factor.

## Control Flow, State, and Persistence
The function is pure and has no state. Inline assembly computes partial products into data registers and returns the combined 32-bit hash.

## Dependencies and Integration Points
It depends on `u32`/`u16` types from the including context and integrates with generic hash helpers that prefer architecture-provided `__hash_32()` when `HAVE_ARCH__HASH_32` is set.

## Risks
Inline assembly constraints are performance- and correctness-critical. Toolchain changes can affect register allocation, and the implementation assumes m68k instruction timing and semantics. The result must remain equivalent to multiplying by `GOLDEN_RATIO_32`.

## Test Signals
Compare `__hash_32()` against the generic multiplication implementation over representative and randomized values, especially on 68000-targeted compiler output. Build tests should cover constraints with GCC versions used by the tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hash.h -->
