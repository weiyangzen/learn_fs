<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c

## Purpose
Implements single-precision result multiply-subtract.

## Important APIs, types, and functions
`int fmsubs(void *frD, void *frA, void *frB, void *frC)` mirrors `fmsub` and packs via `__FP_PACK_DS`.

## Control flow
It computes `A*C`, flips non-NaN `B`, handles invalid special cases, adds, and rounds to a single-precision destination.

## State and persistence behavior
Destination FPR and soft-fp exception state are updated.

## Dependencies and integration points
Dispatched for `FMSUBS`.

## Risks and edge cases
Single rounding, NaN handling, and invalid infinity cases require close ISA parity.

## Test signals
Single result bits and FPSCR exception state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsubs.c -->
