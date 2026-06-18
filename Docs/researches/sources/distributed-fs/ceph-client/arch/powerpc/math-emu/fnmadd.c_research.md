<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c

## Purpose
Implements double-precision negative multiply-add, negating the non-NaN result of `frA * frC + frB`.

## Important APIs, types, and functions
`int fnmadd(void *frD, void *frA, void *frB, void *frC)` uses soft-fp multiply/add then flips `R_s` when the result is not NaN.

## Control flow
It unpacks operands, handles invalid zero/infinity multiply and infinity subtraction, computes multiply-add, conditionally negates the result sign, and packs a double.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMADD`.

## Risks and edge cases
Conditional result sign inversion must not alter NaN signs incorrectly; invalid special cases mirror `fmadd`.

## Test signals
Negated result bits and FPSCR invalid flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadd.c -->
