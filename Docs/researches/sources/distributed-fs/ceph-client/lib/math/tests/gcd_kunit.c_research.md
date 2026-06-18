# sources/distributed-fs/ceph-client/lib/math/tests/gcd_kunit.c

Purpose: Parameterized KUnit tests for `gcd()`.

Important APIs/types/functions: Defines `struct test_case_params`, `params`, `KUNIT_ARRAY_PARAM(gcd, ...)`, `gcd_test()`, and suite `math-gcd`.

Control flow: KUnit invokes `gcd_test()` once per parameter, comparing expected result to `gcd(val1, val2)`.

State and persistence: Stateless test data.

Dependencies/integration: Depends on KUnit and `linux/gcd.h`.

Risks: Covers representative values but not exhaustive performance/static-key behavior.

Test signals: Failures identify the named parameter description.
