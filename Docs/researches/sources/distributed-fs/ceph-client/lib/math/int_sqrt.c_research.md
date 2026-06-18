# sources/distributed-fs/ceph-client/lib/math/int_sqrt.c

Purpose: Computes floor square root for unsigned long, and on 32-bit builds also for 64-bit input.

Important APIs/types/functions: Exports `int_sqrt(unsigned long x)` and conditionally `int_sqrt64(u64 x)`.

Control flow: Uses the shift-and-subtract algorithm. It selects the highest even power-of-four bit at or below the input, then iteratively tests/subtracts and shifts to build the root.

State and persistence: Stateless.

Dependencies/integration: Used by prime-number trial division and other math callers.

Risks: Correctness around word-size boundaries and `ULONG_MAX` depends on bit scanning and type widths.

Test signals: `tests/int_sqrt_kunit.c` covers zero/one, perfect and non-perfect squares, neighbors around powers, and 32-bit maximum inputs.
