<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c

## Purpose
Implements single-precision result form of floating add while reading operands from double-format FPR images.

## Important APIs, types, and functions
`int fadds(void *frD, void *frA, void *frB)` uses double soft-fp unpack/add and `__FP_PACK_DS` to round/pack as single precision in the destination image.

## Control flow
Sources are unpacked as doubles, added, optionally debug-logged, then packed with single-precision result semantics.

## State and persistence behavior
It mutates the destination FPR image and returns soft-fp exceptions for FPSCR recording.

## Dependencies and integration points
Dispatched from `do_mathemu` for `FADDS`, requiring `double.h` and `single.h`.

## Risks and edge cases
The extra rounding to single precision is the key risk; exception and NaN semantics must match PowerPC instruction behavior.

## Test signals
Signals are result single precision bits in the FPR image and correct exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadds.c -->
