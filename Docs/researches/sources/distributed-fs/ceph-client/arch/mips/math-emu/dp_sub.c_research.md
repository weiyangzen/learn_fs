<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c -->
# sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c

Purpose: Subtracts IEEE754 double precision operands with MIPS rounding and exception behavior.

Important APIs/types/functions: `ieee754dp_sub(x, y)`.

Control flow: Handles class pairs for NaN, infinity, and zero, flips y sign for normal arithmetic, aligns exponents with guard/round/sticky bits, adds or subtracts mantissas by resulting signs, normalizes cancellation, selects signed zero by rounding mode, and formats.

State and persistence: Uses and updates `ieee754_csr`.

Dependencies and integration: Used by FPU `SUB.D`, sqrt, and legacy sign operations.

Risks: Infinity subtraction invalid cases and signed-zero results are subtle. Mantissa cancellation can underflow if normalization is wrong.

Test signals: Cover x-x, +0/-0 combinations, inf-inf same sign invalid, denormals, cancellation, and all rounding modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/math-emu/dp_sub.c -->
