<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c

## Purpose
Implements single-precision result floating subtract.

## Important APIs, types, and functions
`int fsubs(void *frD, void *frA, void *frB)` uses double unpack/subtract and `__FP_PACK_DS`.

## Control flow
It unpacks source FPRs, subtracts through soft-fp, then rounds/packs to single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FSUBS`.

## Risks and edge cases
Single-result rounding, cancellation, signed zero, NaN propagation, and exceptions.

## Test signals
Expected single subtract result and FPSCR flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsubs.c -->
