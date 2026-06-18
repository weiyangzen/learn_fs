<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c

## Purpose
Implements floating move by copying a double-format FPR image.

## Important APIs, types, and functions
`int fmr(u32 *frD, u32 *frB)` copies both 32-bit words from source to destination.

## Control flow
There is no branching except optional DEBUG logging.

## State and persistence behavior
Only the destination FPR image is changed; FPSCR is unaffected.

## Dependencies and integration points
Called by `do_mathemu` for `FMR`.

## Risks and edge cases
It intentionally preserves all payload/sign/exponent bits, including NaNs and signed zeros.

## Test signals
Bit-identical destination FPR after emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fmr.c -->
