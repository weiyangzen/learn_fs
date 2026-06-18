# sources/distributed-fs/ceph-client/arch/parisc/math-emu/sfrem.c

Purpose: implements `sgl_frem`, single-precision IEEE-style floating-point remainder.

Important APIs and types: takes two single operands, destination, and status. Uses `Sgl_*` macros for exponent extraction, normalization, subtraction, sign inversion, and denormal result construction.

Control flow: the routine rejects invalid first-operand infinity and zero divisor, quiets or returns NaNs, and returns the dividend when divisor is infinity. It preserves the dividend sign for the result, normalizes denormal operands, computes the exponent difference, handles quotient magnitude below one, then iteratively subtracts divisor-aligned mantissas. The final remainder is adjusted for nearest quotient selection, including exact half-divisor tie behavior, normalized, and underflow-checked.

State and persistence: writes the result and invalid or underflow flags/traps. Remainder is treated as exact, so no inexact flag is set.

Dependencies and integration: called from `fpudispatch.c` for `FREM`. Relies on PA-RISC status macros and `sgl_float.h`.

Risks: quotient rounding semantics are subtle: sign may flip if the nearest integer quotient is above the truncated quotient, and exact half cases depend on the `roundup` state. Underflow trap wrapping must preserve the computed sign.

Test signals: test dividend smaller than divisor, exactly half divisor, slightly above half, exact zero remainder, negative dividends, subnormal results, infinity and zero invalid cases, divisor infinity, and underflow trap behavior.
