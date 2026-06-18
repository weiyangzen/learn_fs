# sources/distributed-fs/ceph-client/lib/math/tests/int_pow_kunit.c

Purpose: Parameterized KUnit tests for `int_pow()`.

Important APIs/types/functions: Defines `struct test_case_params`, vector table, `KUNIT_ARRAY_PARAM(int_pow, ...)`, `int_pow_test()`, and suite `math-int_pow`.

Control flow: Runs one assertion per base/exponent vector.

State and persistence: Stateless test data.

Dependencies/integration: Uses `linux/math.h` and KUnit.

Risks: Tests document unsigned overflow behavior only lightly; no randomized coverage.

Test signals: Covers exponent zero/one, base zero/one, common powers, max base passthrough, and `2^63`.
