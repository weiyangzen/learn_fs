<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swab.h -->
# sources/distributed-fs/ceph-client/include/linux/swab.h

## Purpose

`swab.h` is the kernel-facing byte-swap convenience header. It re-exports UAPI byte/halfword swap primitives under shorter kernel names and adds array helpers for 16-, 32-, and 64-bit buffers.

## Important APIs, types, and functions

Macros map `swab16`, `swab32`, `swab64`, `swab`, `swahw32`, `swahb32`, pointer variants, and in-place variants to `__swab*` UAPI definitions. `swab16_array()`, `swab32_array()`, and `swab64_array()` walk word counts and call in-place swap helpers.

## Control flow

Array helpers perform a simple decrementing loop over typed pointers, swapping one element at a time. Scalar macros defer to compile-time or architecture-optimized implementations in `uapi/linux/swab.h`.

## State and persistence behavior

The array helpers mutate caller-provided buffers in place. There is no global state.

## Dependencies and integration points

It depends on UAPI swab definitions and kernel integer types. It integrates broadly with endian conversion code, binary parsers, filesystems, drivers, and protocol implementations that need explicit byte swapping.

## Risks and test signals

Risks are primarily caller-side: passing byte counts instead of word counts, unaligned typed pointers on strict architectures, double-swapping data, or using in-place helpers on read-only memory. Tests should validate scalar and array swaps for representative patterns, odd word counts, alignment-sensitive callers, and compile-time constant folding where expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/swab.h -->
