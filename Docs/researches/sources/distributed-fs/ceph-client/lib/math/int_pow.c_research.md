# sources/distributed-fs/ceph-client/lib/math/int_pow.c

Purpose: Computes unsigned integer exponentiation.

Important APIs/types/functions: Exports GPL-only `int_pow(u64 base, unsigned int exp)`.

Control flow: Standard exponentiation by squaring: multiply result when the current exponent bit is set, shift exponent right, square base each iteration.

State and persistence: Stateless.

Dependencies/integration: Included in core math object list for kernel users needing simple powers.

Risks: Silent `u64` overflow is expected C unsigned arithmetic; no saturation or error reporting.

Test signals: `tests/int_pow_kunit.c` covers exponent zero/one, base zero/one, small powers, `U64_MAX`, and a high power boundary.
