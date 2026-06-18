# sources/distributed-fs/ceph-client/arch/microblaze/lib/modsi3.S

Purpose: provides signed 32-bit modulo helper `__modsi3`.

Important APIs and state: arguments are r5 dividend and r6 divisor; remainder is returned in r3. Saves r28-r31.

Control flow: zero divisor or dividend returns 0. The routine normalizes signs, performs shift/subtract division while keeping the remainder, then applies the dividend sign to the result.

State and persistence: pure arithmetic.

Dependencies and integration: used by compiler-generated `%` operations and exported to modules.

Risks and test signals: division by zero returns 0. Test sign rules (`-a % b`), zero cases, INT_MIN, and no-hardware-div builds.
