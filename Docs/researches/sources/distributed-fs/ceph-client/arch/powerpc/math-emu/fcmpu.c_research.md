<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c

## Purpose
Implements unordered double-precision floating compare.

## Important APIs, types, and functions
`int fcmpu(u32 *ccr, int crfD, void *frA, void *frB)` uses `FP_CMP_D`, updates FPSCR FPCC bits, and writes a CR field.

## Control flow
Operands are unpacked, compared, mapped through the local CR bit table, and written to FPSCR/CCR. Unlike ordered compare it returns zero and does not explicitly raise invalid on NaN.

## State and persistence behavior
Mutates `__FPU_FPSCR` FPCC bits and `*ccr`; no destination FPR is changed.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FCMPU`.

## Risks and edge cases
NaN/unordered mapping must match PPC unordered compare semantics, with no ordered invalid exception.

## Test signals
Observed CR field and FPCC bits after emulated `fcmpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fcmpu.c -->
