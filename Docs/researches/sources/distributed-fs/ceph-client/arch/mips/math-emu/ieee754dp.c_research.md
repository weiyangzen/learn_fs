# sources/distributed-fs/ceph-client/arch/mips/math-emu/ieee754dp.c

Purpose: double-precision common implementation for classification, signaling-NaN quieting, and final result formatting with rounding, underflow, overflow, and exception flag handling.

Important APIs/functions: `ieee754dp_class()` returns the internal class; `ieee754dp_nanxcpt()` raises invalid operation and converts an sNaN to qNaN according to legacy or NaN-2008 mode; `ieee754dp_format(int sn, int xe, u64 xm)` turns an unbiased exponent plus guard/round/sticky mantissa into a final `union ieee754dp`.

Control flow: `ieee754dp_format()` handles tiny results first, respecting `ieee754_csr.nod`, then sets inexact/underflow if GRS bits exist, rounds by `ieee754_csr.rm`, adjusts exponent on carry, detects overflow, and finally builds normal or denormal output.

State and persistence: updates `ieee754_csr.cx` and sticky `sx` through `ieee754_setcx()`. It has no global mutable state.

Dependencies and integration: used by all double-precision arithmetic/conversion helpers; depends on `ieee754dp.h` and internal macros from `ieee754int.h`.

Risks and test signals: rounding and tininess behavior are fragile. Exercise all rounding modes, underflow with `nod`, exponent overflow, qNaN/sNaN conversion under both NaN modes, exact denormals, and exceptions masked/unmasked through FCR31.
