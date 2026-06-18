# sources/distributed-fs/ceph-client/lib/math/tests/rational_kunit.c

Purpose: Parameterized KUnit tests for bounded rational approximation.

Important APIs/types/functions: Defines `struct rational_test_param`, vector table, generator, `rational_test()`, and suite `rational`.

Control flow: Each parameter calls `rational_best_approximation()` and checks numerator and denominator against expected outputs.

State and persistence: Stateless test data.

Dependencies/integration: Uses KUnit and `linux/rational.h`.

Risks: Covers many continued-fraction edge cases but not overflow extremes.

Test signals: Parameter names distinguish exact, near-zero, convergent, semi-convergent, numerator-limit, and denominator-limit scenarios.
