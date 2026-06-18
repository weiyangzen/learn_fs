<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c

## Purpose
Implements emulated single-precision floating load, widening the loaded float into a double-format FPR image.

## Important APIs, types, and functions
`int lfs(void *frD, void *ea)` copies a `float` from user memory, unpacks it with `FP_UNPACK_S`, converts with `FP_CONV(D, S, ...)`, and packs a double.

## Control flow
It reads user memory, converts single to double using soft-fp, preserves NaN exponent handling through a raw pack path, and returns zero or `-EFAULT`.

## State and persistence behavior
Destination FPR image is updated; FPSCR exception return is zero.

## Dependencies and integration points
Dispatched for `LFS`, `LFSU`, `LFSX`, and `LFSUX` by `math.c`.

## Risks and edge cases
NaN conversion handling is special-cased; user access faults must not update a partial destination.

## Test signals
Correct double-format FPR after loading a float and fault return on bad addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/lfs.c -->
