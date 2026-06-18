# sources/distributed-fs/ceph-client/arch/m68k/math-emu/fp_trig.h

## Purpose
Declares trigonometric, inverse-trigonometric, hyperbolic, and `fsincos` helpers for the floating-point emulator.

## APIs, Flow, And State
The public prototypes are `fp_fsin`, `fp_fcos`, `fp_ftan`, `fp_fasin`, `fp_facos`, `fp_fatan`, `fp_fsinh`, `fp_fcosh`, `fp_ftanh`, `fp_fatanh`, and `fp_fsincos0` through `fp_fsincos7`. All use the emulator’s internal `struct fp_ext *dest, *src` convention. The header contains no state.

## Dependencies And Integration
Includes `fp_emu.h`. It is used by `fp_trig.c`; assembly dispatch references the emitted C symbols through the operation table.

## Risks And Test Signals
The prototypes imply broad operation coverage, but the implementation is placeholder. Test signals are compile-time declaration matching and runtime instruction tests documenting unsupported trig behavior until real algorithms are implemented.
