## sources/distributed-fs/ceph-client/tools/perf/tests/tests-scripts.h

Purpose: header declaring shell script test-suite discovery.
Important API: `struct test_suite **create_script_test_suites(void);`.
Control flow: no executable code; included by harness code that wants dynamic shell test suites.
State and persistence: returned array ownership is defined by implementation rather than the header.
Dependencies and integration: forward-declares `struct test_suite` and includes only the guard.
Risks: minimal header gives no lifetime contract for returned suites; callers must know implementation conventions.
Test signals: compile-time integration with `tests-scripts.c`.
