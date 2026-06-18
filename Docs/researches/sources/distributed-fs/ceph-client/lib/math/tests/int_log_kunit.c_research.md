# sources/distributed-fs/ceph-client/lib/math/tests/int_log_kunit.c

Purpose: Parameterized KUnit tests for fixed-point `intlog2()` and `intlog10()`.

Important APIs/types/functions: Defines separate parameter arrays for base-2 and base-10 outputs, generator macros, `intlog2_test()`, `intlog10_test()`, and suite `math-int_log`.

Control flow: Each KUnit case compares the helper output to precomputed fixed-point values that include known approximation error.

State and persistence: Stateless test vectors.

Dependencies/integration: Uses `linux/int_log.h` and KUnit.

Risks: Zero-input cases expect 0 despite implementation warning, so warning behavior should be considered when running.

Test signals: Covers powers, non-powers, zero, and `U32_MAX`.
