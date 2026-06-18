# sources/distributed-fs/ceph-client/arch/sh/lib/udivsi3_i4i-Os.S

Purpose: size-optimized i4i implementation of unsigned and signed 32-bit division helpers.

Important symbols: `__udivsi3_i4i`, `__sdivsi3_i4i`, `sdiv_small_divisor`, `large_divisor`, and sign-adjustment labels.

Control flow: unsigned division handles small and large divisors with compact loops. Signed division normalizes operand signs, delegates to division logic, then conditionally negates the result.

State and persistence: register-only arithmetic.

Dependencies and integration: selected by Kbuild when optimizing for size on SH4-style cores.

Risks: compact control flow increases risk around sign normalization and `INT_MIN / -1`-style edge cases. ABI compatibility is mandatory.

Test signals: signed/unsigned division runtime tests, especially negative operands and small divisors.
