# sources/distributed-fs/ceph-client/tools/include/linux/bits.h

## Purpose

This header exposes kernel-style bit and bitmask construction macros to tools code.

## APIs, State, and Dependencies

It includes vdso and UAPI bit definitions, defines `BIT_MASK`, `BIT_WORD`, `BIT_ULL_MASK`, `BIT_ULL_WORD`, `BITS_PER_BYTE`, and `BITS_PER_TYPE`, then provides typed `GENMASK_*` and `BIT_U*` macros with compile-time input checks in C contexts. It depends on build-bug, compiler, and overflow helpers. There is no state.

## Risks and Test Signals

The macros are ABI- and type-width-sensitive. Bad high/low ordering or out-of-range bit indexes intentionally trigger build errors where possible. Tests should cover typed masks for u8/u16/u32/u64/u128 and assembly inclusion paths where checks are disabled.
