<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c

## Purpose
Implements floating convert to signed integer word with rounding toward zero.

## Important APIs, types, and functions
`int fctiwz(u32 *frD, void *frB)` temporarily rewrites the soft-fp FPSCR rounding mode to `FP_RND_ZERO`.

## Control flow
It saves `__FPU_FPSCR`, forces round-to-zero, unpacks and converts the source double to a 32-bit signed integer, stores `frD[1]`, then restores FPSCR.

## State and persistence behavior
Destination FPR word is updated. FPSCR rounding mode is restored after conversion.

## Dependencies and integration points
Dispatched from `do_mathemu` for `FCTIWZ`.

## Risks and edge cases
Exception propagation across the temporary FPSCR save/restore is subtle; conversion edge cases include NaN and out-of-range values.

## Test signals
Signals are truncation behavior independent of current rounding mode and no persistent rounding-mode change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fctiwz.c -->
