<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c

## Purpose
Implements a two-word unsigned division/remainder helper for soft-fp 128-bit style arithmetic.

## Important APIs, types, and functions
`void _fp_udivmodti4(_FP_W_TYPE q[2], _FP_W_TYPE r[2], _FP_W_TYPE n1, _FP_W_TYPE n0, _FP_W_TYPE d1, _FP_W_TYPE d0)` computes quotient and remainder using soft-fp word macros such as `udiv_qrnnd`, `umul_ppmm`, `sub_ddmmss`, and `__FP_CLZ`.

## Control flow
The routine handles one-word denominators separately from two-word denominators, normalizes when required, computes high/low quotient words, corrects overestimates, and writes quotient/remainder arrays. A zero divisor intentionally triggers division by zero.

## State and persistence behavior
Only the output arrays are written; all arithmetic state is local.

## Dependencies and integration points
Used by soft-fp support code for wide division where compiler runtime helpers are unavailable or unsuitable in-kernel.

## Risks and edge cases
Normalization shift counts, quotient correction, zero denominator behavior, and word-size assumptions are critical. The code derives from libgcc and must stay aligned with soft-fp word macro semantics.

## Test signals
Soft-fp operations requiring wide division should produce exact quotient/remainder bits across normalized and unnormalized cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/math-emu/udivmodti4.c -->
