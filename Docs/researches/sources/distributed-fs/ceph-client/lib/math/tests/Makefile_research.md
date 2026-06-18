# sources/distributed-fs/ceph-client/lib/math/tests/Makefile

Purpose: Kbuild list for math KUnit test objects.

Important APIs/types/functions: Maps `CONFIG_GCD_KUNIT_TEST`, `CONFIG_INT_LOG_KUNIT_TEST`, `CONFIG_INT_POW_KUNIT_TEST`, `CONFIG_INT_SQRT_KUNIT_TEST`, `CONFIG_PRIME_NUMBERS_KUNIT_TEST`, and `CONFIG_RATIONAL_KUNIT_TEST` to corresponding objects.

Control flow: Build-time only.

State and persistence: No runtime state.

Dependencies/integration: Integrates the KUnit suites with `lib/math/Makefile`.

Risks: Tests are omitted unless the matching Kconfig symbols are enabled.

Test signals: The presence of each object line is the activation path for the corresponding suite.
