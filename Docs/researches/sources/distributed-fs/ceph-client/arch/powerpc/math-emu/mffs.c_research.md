<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c

## Purpose
Implements move from FPSCR to floating register.

## Important APIs, types, and functions
`int mffs(u32 *frD)` writes `__FPU_FPSCR` into `frD[1]`.

## Control flow
Straight-line copy with optional DEBUG logging.

## State and persistence behavior
Destination FPR low word is updated; FPSCR is not changed.

## Dependencies and integration points
Dispatched by `do_mathemu` for `MFFS`.

## Risks and edge cases
Upper word handling is not explicit; the emulator expects the FPSCR value in the low word of the FPR image.

## Test signals
Destination FPR contains the current FPSCR low word.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/mffs.c -->
