<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c

## Purpose
Implements single-precision result negative multiply-subtract.

## Important APIs, types, and functions
`int fnmsubs(void *frD, void *frA, void *frB, void *frC)` is the single-result counterpart to `fnmsub`.

## Control flow
It performs multiply, subtract via sign flip, invalid checks, final non-NaN sign inversion, and single-result packing.

## State and persistence behavior
Destination FPR image and soft-fp exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMSUBS`.

## Risks and edge cases
Single rounding, NaN sign behavior, and invalid special-case ordering require careful parity with ISA semantics.

## Test signals
Single result bits and FPSCR exception state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsubs.c -->
