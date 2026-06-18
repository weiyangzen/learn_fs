<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c

## Purpose
Implements single-precision result negative multiply-add.

## Important APIs, types, and functions
`int fnmadds(void *frD, void *frA, void *frB, void *frC)` mirrors `fnmadd` and packs with `__FP_PACK_DS`.

## Control flow
The handler computes multiply-add, conditionally flips non-NaN result sign, and rounds/packs as single precision.

## State and persistence behavior
Destination FPR and exception flags are updated.

## Dependencies and integration points
Dispatched for `FNMADDS`.

## Risks and edge cases
Single-result rounding and NaN sign preservation are key edge cases.

## Test signals
Expected single negated result and exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fnmadds.c -->
