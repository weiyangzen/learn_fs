# sources/distributed-fs/ceph-client/arch/sh/lib/div64-generic.c

Purpose: provides a C wrapper for 64-bit-by-32-bit division on SH using the architecture assembly helper.

Important API: `__div64_32`.

Control flow: calls `__xdiv64_32` with a pointer to the 64-bit dividend and 32-bit divisor; the helper updates the dividend with quotient and returns the remainder.

State and persistence: mutates the caller-provided 64-bit dividend in place; no global state.

Dependencies and integration: depends on `asm/div64.h` and `div64.S`; used by generic `do_div`-style arithmetic.

Risks: division-by-zero behavior is caller-defined/unsafe. ABI mismatch with `__xdiv64_32` corrupts quotient/remainder.

Test signals: 64-bit division tests across small, large, exact, and remainder-producing divisors.
