## sources/distributed-fs/ceph-client/tools/perf/tests/tests.h

Purpose: central perf test harness declarations, assertion macros, suite registration macros, architecture gates, and workload declarations.
Important APIs/types/macros: `TEST_OK/FAIL/SKIP`, `TEST_ASSERT_VAL`, `TEST_ASSERT_EQUAL`, `struct test_case`, `struct test_suite`, `DECLARE_SUITE`, `TEST_CASE*`, `DEFINE_SUITE*`, `BP_SIGNAL_IS_SUPPORTED`, `struct test_workload`, `DECLARE_WORKLOAD`, and `DEFINE_WORKLOAD`.
Control flow: macros generate static test case arrays and suite objects around `test__name` functions; many `DECLARE_SUITE` entries expose suites defined across the tests directory.
State and persistence: no runtime state in the header, but it declares globals `dso_to_test` and `test_objdump_path`.
Dependencies and integration: used by nearly every C test file and harness registry.
Risks: assertion macros return immediately, so cleanup must be done before or via structured goto in tests; architecture gate disables breakpoint signal tests on several architectures.
Test signals: compile-time suite wiring and consistent result codes for the harness.
