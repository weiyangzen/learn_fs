# sources/distributed-fs/ceph-client/include/uapi/linux/bits.h

## Purpose

`sources/distributed-fs/ceph-client/include/uapi/linux/bits.h` exports low-level bitmask construction macros for UAPI consumers. The complete 14-line header was read. It provides generic mask builders for unsigned long, unsigned long long, and 128-bit values.

## Important APIs, Types, and Functions

There are no functions or types. Exported macros are `__GENMASK(h, l)`, `__GENMASK_ULL(h, l)`, and `__GENMASK_U128(h, l)`. They depend on helper macros such as `_UL`, `_ULL`, `_BIT128`, `__BITS_PER_LONG`, and `__BITS_PER_LONG_LONG` that are expected from the surrounding Linux UAPI constant infrastructure.

## Control Flow

The header has no runtime flow. Compile-time expressions call the macros to generate contiguous masks from high bit `h` down to low bit `l`. The U128 variant forms a mask by subtracting the low-bit power from one past the high-bit power; the long and long-long variants use paired shifts against all-ones constants.

## State and Persistence Behavior

No state is stored or persisted. The macros influence compile-time constants and inline expressions in drivers, protocol headers, and userspace programs.

## Dependencies and Integration Points

This header integrates with Linux UAPI bit operations and constant macros, typically via includes that provide the `_UL`/`_ULL` wrappers and architecture bit widths. It is used by headers that need stable bit-field masks without manually writing architecture-width-dependent constants.

## Risks and Edge Cases

Callers must pass valid bit indexes where `h >= l` and both indexes fit the target width. Invalid shifts at or beyond the type width are undefined in C and can produce compiler warnings or wrong masks. The macros are prefixed with double underscores, so they are low-level building blocks rather than policy-checked public helpers. The U128 macro relies on `_BIT128()` support and should only be used where 128-bit constant handling is available.

## Test Signals

Useful signals include UAPI compile tests on 32-bit and 64-bit architectures, static assertions for representative masks such as single-bit, full-width, and subrange masks, compiler warning scans for invalid shift expressions, and build coverage for headers that consume `__GENMASK_U128`.
