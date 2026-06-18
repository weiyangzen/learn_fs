<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c

## Purpose
Implements double-precision floating subtract.

## Important APIs, types, and functions
`int fsub(void *frD, void *frA, void *frB)` uses `FP_SUB_D` and `__FP_PACK_D`.

## Control flow
Source operands are unpacked, soft-fp subtraction is performed, and the double result is packed.

## State and persistence behavior
Destination FPR image and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FSUB`.

## Risks and edge cases
Rounding, cancellation, NaNs, infinities, underflow, and inexact status depend on soft-fp macros.

## Test signals
Subtract result and FPSCR exception status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fsub.c -->
