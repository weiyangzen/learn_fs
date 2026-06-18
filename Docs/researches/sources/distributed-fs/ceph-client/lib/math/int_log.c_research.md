# sources/distributed-fs/ceph-client/lib/math/int_log.c

Purpose: Provides fixed-point base-2 and base-10 logarithms for 32-bit inputs.

Important APIs/types/functions: Exports `intlog2(u32 value)` and `intlog10(u32 value)`. Uses a 256-entry log table and returns `log(value) * 2^24`.

Control flow: `intlog2()` rejects zero with `WARN_ON`, finds the most significant bit, normalizes the significand, indexes the lookup table, interpolates within the table bucket, and combines integer/fractional parts. `intlog10()` multiplies the base-2 result by fixed-point `log10(2)`.

State and persistence: Stateless, read-only lookup table.

Dependencies/integration: Depends on bitops and exported for fixed-point kernel consumers.

Risks: Zero returns 0 after warning although logarithm is undefined. Results are approximate and tests account for table error.

Test signals: `tests/int_log_kunit.c` covers zero, powers, representative values, and `U32_MAX` for both bases.
