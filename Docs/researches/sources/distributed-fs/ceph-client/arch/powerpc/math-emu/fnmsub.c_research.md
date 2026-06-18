<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c

## Purpose
Implements double-precision negative multiply-subtract, negating the non-NaN result of `frA * frC - frB`.

## Important APIs, types, and functions
`int fnmsub(void *frD, void *frA, void *frB, void *frC)` uses double soft-fp multiply/add and sign manipulation.

## Control flow
It flags invalid zero/infinity multiply, multiplies `A*C`, flips non-NaN `B`, checks invalid infinity subtraction, adds, conditionally negates non-NaN result, and packs a double.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched by `do_mathemu` for `FNMSUB`.

## Risks and edge cases
Correct ordering of B sign flip, invalid infinity checks, and final sign inversion is critical.

## Test signals
Result sign/value and VXIMZ/VXISI flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmsub.c -->
