<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c

## Purpose
Implements single-precision result floating divide from double-format FPR operands.

## Important APIs, types, and functions
`int fdivs(void *frD, void *frA, void *frB)` mirrors `fdiv` but packs with `__FP_PACK_DS`.

## Control flow
It handles invalid `0/0` and `inf/inf`, handles divide-by-zero trap checks, performs double soft-fp division, then rounds/packs as single precision.

## State and persistence behavior
Destination FPR image and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FDIVS`.

## Risks and edge cases
Single-result rounding and exception ordering around divide-by-zero traps are the main risks.

## Test signals
Signals are single-precision quotient representation and correct FPSCR exception bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fdivs.c -->
