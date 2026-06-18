# sources/distributed-fs/ceph-client/include/linux/bits.h

## Purpose
`bits.h` defines common bit and mask construction macros used throughout the kernel. It layers Linux-specific type-checked mask helpers over VDSO and UAPI definitions while keeping assembly-compatible fallbacks.

## Important APIs, Types, And Functions
The basic helpers are `BIT_MASK()`, `BIT_WORD()`, `BIT_ULL_MASK()`, `BIT_ULL_WORD()`, `BITS_PER_BYTE`, and `BITS_PER_TYPE(type)`. In C contexts, `GENMASK_TYPE()` creates a contiguous mask for a specified unsigned type, with public variants `GENMASK()`, `GENMASK_ULL()`, `GENMASK_U8()`, `GENMASK_U16()`, `GENMASK_U32()`, `GENMASK_U64()`, and `GENMASK_U128()`. Fixed-width single-bit macros are `BIT_U8()`, `BIT_U16()`, `BIT_U32()`, and `BIT_U64()`.

## Control Flow And State
There is no runtime state. Compile-time control is performed through `GENMASK_INPUT_CHECK()` and `BIT_INPUT_CHECK()`, which use `BUILD_BUG_ON_ZERO(const_true(...))` and compiler shift diagnostics to catch inverted ranges or out-of-width bit numbers. In assembly mode, typed helpers requiring `sizeof()` are unavailable, so the header maps `GENMASK()` and `GENMASK_ULL()` directly to UAPI-style `__GENMASK()` and `__GENMASK_ULL()`.

## Dependencies And Integration Points
The header includes `vdso/bits.h` and `uapi/linux/bits.h` for foundational `BIT()`/`BIT_ULL()` and mask macros. C-only checks depend on `linux/build_bug.h`, `linux/compiler.h`, and `linux/overflow.h`. It underpins `bitops.h`, `bitmap.h`, block request flags, queue feature flags, and nearly every register or mask definition in the tree.

## Risks And Test Signals
Risks are invalid macro arguments with side effects, negative bit numbers, width overflow, and assembly users accidentally depending on C-only typed helpers. Test signals are compile-time build failures for `GENMASK(15, 20)`, `GENMASK_U32(33, 15)`, and `BIT_U8(8)`, plus successful mask values for boundary cases such as bit 0, the top bit of each type, and full-width masks.
