<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c

## Purpose
Implements `frsp`, rounding a double-format FPR value to single precision and storing it back as a double-format image.

## Important APIs, types, and functions
`int frsp(void *frD, void *frB)` uses double unpack, conversion to single (`FP_CONV`), canonical packing, raw single packing, and re-unpacking/packing to double layout.

## Control flow
The handler converts the input double to a single representation, handles exceptions/traps, then stores the rounded result in the destination FPR image.

## State and persistence behavior
Destination FPR is updated and soft-fp exceptions are returned for FPSCR recording.

## Dependencies and integration points
Dispatched for `FRSP`, requiring `double.h` and `single.h`.

## Risks and edge cases
NaN, overflow, inexact, and trap-enabled exception cases need correct pack-suppression semantics.

## Test signals
Result equals single-rounded value in FPR format and FPSCR exception bits reflect conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/frsp.c -->
