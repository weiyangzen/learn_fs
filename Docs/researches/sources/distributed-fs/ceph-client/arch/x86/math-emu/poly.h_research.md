# sources/distributed-fs/ceph-client/arch/x86/math-emu/poly.h

## Purpose
This header defines the 12-byte extended-significand (`Xsig`) arithmetic interface used by emulator polynomial approximations for transcendental instructions.

## Important APIs, Types, and Functions
The key type is `Xsig { lsw, midw, msw }`. Declarations include `polynomial_Xsig()`, `mul32_Xsig()`, `mul64_Xsig()`, `mul_Xsig_Xsig()`, `shr_Xsig()`, `round_Xsig()`, `norm_Xsig()`, and `div_Xsig()`. Macros include `LL_MSW()`, `MK_XSIG()`, and `XSIG_LL()`. Inline helpers are `mul_32_32()`, `add_Xsig_Xsig()`, `add_two_Xsig()`, and `negate_Xsig()`.

## Control Flow
The inline helpers perform fixed-point multiplication high-word extraction, 96-bit addition with optional exponent increment on carry, and subtraction from 1.0-style negation. They are intended to compile inline for performance in polynomial loops.

## State and Persistence
There is no global state. Helpers mutate caller-provided `Xsig` accumulators and sometimes caller-provided exponent variables.

## Dependencies and Integration Points
It depends on x86 inline assembly and `asmlinkage` assembly helper implementations. It is included by all `poly_*.c` files and bridges C polynomial logic with low-level fixed-point arithmetic.

## Risks and Test Signals
Risks include aliasing assumptions in `XSIG_LL()`, inline assembly constraints, overflow not always checked, and endian/word-order dependence. Test signals include 32-bit builds, polynomial accuracy tests, and compiler variation testing.
