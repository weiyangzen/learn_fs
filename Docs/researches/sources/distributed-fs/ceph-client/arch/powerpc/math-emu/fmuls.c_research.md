<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c

## Purpose
Implements single-precision result floating multiply.

## Important APIs, types, and functions
`int fmuls(void *frD, void *frA, void *frB)` uses double unpack/multiply and `__FP_PACK_DS`.

## Control flow
It unpacks operands, flags invalid zero/infinity multiply, multiplies, then rounds/packs as a single result.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FMULS`.

## Risks and edge cases
Single-precision result rounding and invalid exception flags are the main risks.

## Test signals
Single product representation and FPSCR flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmuls.c -->
