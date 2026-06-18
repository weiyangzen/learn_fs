# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.c

## Purpose
Implements selected logarithmic/exponential-class FPU emulator operations, with full square-root support and stubs for many transcendental functions.

## APIs, Flow, And State
Functions declared in `fp_log.h` operate on `struct fp_ext` operands. `fp_fsqrt()` normalizes input, rejects negative nonzero operands as NaN, handles zero/infinity, creates an initial approximation, and applies nine Newton iterations using existing add/div kernels before rebiasing the exponent. `fp_fgetexp()` converts the unbiased exponent to an extended integer value, while `fp_fgetman()` returns the mantissa with exponent set to one. `fp_fetoxm1`, `fp_fetox`, `fp_ftwotox`, `fp_ftentox`, `fp_flogn`, `fp_flognp1`, `fp_flog10`, and `fp_flog2` log unimplemented status through `uprint()`, run monadic checks, and return the copied source.

## Dependencies And Integration
Depends on `fp_arith.h` for Newton operations, `fp_emu.h` status/normalization, and dispatch entries in `fp_scan.S`.

## Risks And Test Signals
Many advertised operations are effectively unimplemented pass-throughs, so programs using transcendentals may get incorrect results without a hard fault. `fp_fsqrt()` modifies temporary operands through arithmetic helpers. Test signals include FSQRT accuracy/exception tests and explicit coverage showing which transcendental opcodes are unsupported.
