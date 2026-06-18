# sources/distributed-fs/ceph-client/arch/x86/math-emu/div_Xsig.S

## Purpose
This assembly file divides 96-bit fixed-point `Xsig` quantities for transcendental polynomial code. It trades exact 96-bit division for an approximation intended to exceed normal 64-bit precision.

## Important APIs, Types, and Functions
The exported function is `div_Xsig(Xsig *a, const Xsig *b, Xsig *dest)`. Local storage tracks a four-word accumulator and three-word result. PARANOID builds can call `FPU_exception()` with internal codes `0x240` to `0x242` when arithmetic invariants fail.

## Control Flow
The routine halves the dividend to avoid overflow, computes the first two quotient words using augmented-divisor estimates and correction subtracts, then estimates the third word after accounting for the low divisor word. It writes the three-word result to `dest`. Error labels in PARANOID mode report logic failures and still return through the normal epilogue.

## State and Persistence
There is no persistent state in the normal build; temporaries live on the stack unless `NON_REENTRANT_FPU` selects static storage. The result mutates the caller-provided `Xsig`.

## Dependencies and Integration Points
It depends on the `Xsig` layout from `poly.h`, i386 calling conventions from `fpu_asm.h`/`fpu_emu.h`, and exception reporting. It is used by `poly_2xm1.c`, `poly_atan.c`, `poly_l2.c`, and `poly_tan.c`.

## Risks and Test Signals
Risks include divisor normalization assumptions, quotient correction mistakes, stack/static reentrancy choices, and precision loss affecting transcendental functions. Test signals include polynomial helper accuracy, PARANOID builds without internal exceptions, and comparison of `f2xm1`, `fpatan`, `fyl2x`, `fyl2xp1`, and `fptan` against hardware x87.
