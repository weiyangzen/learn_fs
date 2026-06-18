<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c

## Purpose
Implements ordered double-precision floating compare and condition register update.

## Important APIs, types, and functions
`int fcmpo(u32 *ccr, int crfD, void *frA, void *frB)` uses `FP_CMP_D` and maps compare outcomes to PowerPC CR bits.

## Control flow
It unpacks both operands, raises `EFLAG_VXVC` if either is NaN, computes compare state, writes FPSCR FPCC bits, updates the requested CR field, and returns current exceptions.

## State and persistence behavior
It mutates `__FPU_FPSCR` comparison bits and the caller-provided CCR image.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FCMPO`; exception recording happens later in `math.c`.

## Risks and edge cases
Ordered compare must signal invalid for NaN while preserving condition code mapping for less/greater/equal/unordered.

## Test signals
CR field bits, FPSCR FPCC bits, and invalid exception status are the observable signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpo.c -->
