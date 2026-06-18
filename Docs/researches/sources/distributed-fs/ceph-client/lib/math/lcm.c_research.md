# sources/distributed-fs/ceph-client/lib/math/lcm.c

Purpose: Implements least common multiple helpers.

Important APIs/types/functions: Exports GPL-only `lcm(a, b)` and `lcm_not_zero(a, b)`.

Control flow: `lcm()` returns `(a / gcd(a,b)) * b` when both inputs are nonzero, else 0. `lcm_not_zero()` returns the LCM if nonzero, otherwise the nonzero input.

State and persistence: Stateless.

Dependencies/integration: Depends on `gcd()` and exported for drivers/subsystems needing period/frequency composition.

Risks: Multiplication may overflow unsigned long silently.

Test signals: No dedicated KUnit file in this subset; indirectly relies on `gcd` coverage and consumer tests.
