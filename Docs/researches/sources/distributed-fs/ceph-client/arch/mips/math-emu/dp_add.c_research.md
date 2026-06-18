<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c

Purpose: Adds two IEEE754 double precision values with MIPS exception and rounding semantics.

Important APIs/types/functions: `ieee754dp_add(x, y)`.

Control flow: Clears exception state, flushes denormals as configured, handles NaN/infinity/zero class pairs, normalizes denormals, aligns exponents with guard/round/sticky bits, adds or subtracts mantissas by sign, normalizes cancellation, and formats the rounded result.

State and persistence: Uses global `ieee754_csr` exception and rounding state.

Dependencies and integration: Used by FPU emulator arithmetic, sqrt refinement, and legacy abs/neg paths.

Risks: Signed zero depends on rounding mode and operand signs. Mantissa alignment and sticky shifts are precision-sensitive.

Test signals: IEEE add vectors should cover NaNs, inf-inf invalid, signed zeros, denormals, cancellation, overflow, underflow, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_add.c -->
