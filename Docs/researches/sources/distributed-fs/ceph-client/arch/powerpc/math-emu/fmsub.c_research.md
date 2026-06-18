<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c

## Purpose
Implements double-precision multiply-subtract, effectively `frA * frC - frB`.

## Important APIs, types, and functions
`int fmsub(void *frD, void *frA, void *frB, void *frC)` uses double soft-fp math and packs with `__FP_PACK_D`.

## Control flow
It unpacks operands, flags invalid zero/infinity multiply, multiplies `A*C`, flips `B` sign unless `B` is NaN, detects opposite infinity invalid subtraction, adds, and packs the result.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched from `math.c` for `FMSUB`.

## Risks and edge cases
NaN sign handling is intentionally skipped for NaN `B`; invalid infinity subtraction and rounding are sensitive.

## Test signals
Result bits and VXIMZ/VXISI exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmsub.c -->
