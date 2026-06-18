<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c

## Purpose
Implements double-precision square root.

## Important APIs, types, and functions
`int fsqrt(void *frD, void *frB)` uses `FP_SQRT_D` and `__FP_PACK_D`.

## Control flow
It unpacks the source double, flags `EFLAG_VXSQRT` for negative nonzero/non-NaN inputs, computes the soft-fp square root, and packs the result.

## State and persistence behavior
Destination FPR and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for `FSQRT`.

## Risks and edge cases
Negative zero, negative finite, NaN, and trap-enabled invalid cases require exact classification.

## Test signals
Square-root result and FPSCR invalid square-root flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsqrt.c -->
