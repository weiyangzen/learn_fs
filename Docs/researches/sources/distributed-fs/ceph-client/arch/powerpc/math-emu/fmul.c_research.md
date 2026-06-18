<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c

## Purpose
Implements double-precision floating multiply.

## Important APIs, types, and functions
`int fmul(void *frD, void *frA, void *frB)` uses `FP_MUL_D` and `__FP_PACK_D`.

## Control flow
Sources are unpacked, invalid zero-times-infinity is flagged, soft-fp multiplication is performed, and the result is packed.

## State and persistence behavior
Destination FPR image and exception flags are updated.

## Dependencies and integration points
Dispatched by `math.c` for `FMUL`.

## Risks and edge cases
Invalid operation, NaN propagation, and rounding depend on soft-fp macros plus the explicit zero/infinity check.

## Test signals
Product bits and FPSCR exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmul.c -->
