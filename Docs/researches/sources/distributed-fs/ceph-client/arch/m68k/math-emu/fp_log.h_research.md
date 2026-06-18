# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_log.h

## Purpose
Declares logarithmic, exponential, square-root, and exponent/mantissa extraction helpers for the floating-point emulator.

## APIs, Flow, And State
The header declares `fp_fsqrt`, `fp_fetoxm1`, `fp_fetox`, `fp_ftwotox`, `fp_ftentox`, `fp_flogn`, `fp_flognp1`, `fp_flog10`, `fp_flog2`, `fp_fgetexp`, and `fp_fgetman`. All use the internal `struct fp_ext *dest, *src` convention and return `dest`. It defines no state.

## Dependencies And Integration
Includes `fp_emu.h` for `struct fp_ext` and emulator status definitions. It is included by `fp_log.c`; assembly dispatch resolves the compiled symbols.

## Risks And Test Signals
The declarations expose operations that are only partially implemented in `fp_log.c`. Consumers must not infer full Motorola 68881 transcendental accuracy from the prototypes. Test signals are compile-time prototype matching and runtime opcode tests that distinguish implemented FSQRT/FGETEXP/FGETMAN from pass-through unimplemented operations.
