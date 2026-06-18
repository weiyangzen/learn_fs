<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c

## Purpose
Implements emulated `fabs` by clearing the sign bit of a double-precision FPR image.

## Important APIs, types, and functions
`int fabs(u32 *frD, u32 *frB)` copies the low word and masks `frB[0]` with `0x7fffffff`.

## Control flow
The handler performs a direct bit transform and returns zero; optional DEBUG logging dumps the result.

## State and persistence behavior
It writes the destination FPR image only and does not alter FPSCR.

## Dependencies and integration points
Called by `do_mathemu` for opcode `FABS`, using the thread FPR save area.

## Risks and edge cases
It preserves NaN payloads and the low word by design; endian assumptions follow the FPR word layout used by the math emulator.

## Test signals
Signals are correct sign clearing when `do_mathemu` dispatches `fabs` and no exception flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fabs.c -->
