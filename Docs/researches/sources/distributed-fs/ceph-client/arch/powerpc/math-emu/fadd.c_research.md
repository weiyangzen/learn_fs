<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c

## Purpose
Implements double-precision floating add for full math emulation.

## Important APIs, types, and functions
`int fadd(void *frD, void *frA, void *frB)` uses `FP_DECL_D`, `FP_UNPACK_DP`, `FP_ADD_D`, and `__FP_PACK_D`.

## Control flow
It unpacks source double values, performs soft-fp addition, packs the result into the destination FPR image, and returns `FP_CUR_EXCEPTIONS`.

## State and persistence behavior
The destination FPR image is updated; exception flags are accumulated in soft-fp state for `math.c` to record in FPSCR.

## Dependencies and integration points
Called by `do_mathemu` for `FADD` and depends on `asm/sfp-machine.h` and `math-emu/double.h`.

## Risks and edge cases
NaN propagation, rounding, overflow, underflow, and inexact behavior rely entirely on soft-fp macros.

## Test signals
Correct result bits and FPSCR exception updates through `do_mathemu` are the expected signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/fadd.c -->
