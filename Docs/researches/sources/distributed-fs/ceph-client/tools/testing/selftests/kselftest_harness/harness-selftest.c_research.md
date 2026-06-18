# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.c

Purpose: this C program is the behavioral regression test for `kselftest_harness.h`. It deliberately defines passing, failing, signal, fixture, timeout, exit-code, and low-level result-code tests so the harness output can be compared with a golden file.

Important APIs and functions: it includes `kselftest_harness.h` after forcing `TH_LOG_STREAM stdout` for deterministic output. It defines `test_helper()`, standalone `TEST()` cases, `TEST_SIGNAL()` cases, fixture-based `TEST_F()` cases, `TEST_F_TIMEOUT()`, fixtures with normal child teardown and parent teardown, a setup-failure fixture, tests exiting with `KSFT_*` codes, and tests calling `ksft_test_result_*()` helpers. `main()` disables dumpability/core dumps, sets `RLIMIT_CORE` to zero, and calls `test_harness_run()`.

Control flow: constructors from the harness register all tests, then `main()` runs them through the standard harness. Several cases intentionally fail or abort so the harness exercises failure classification. The timeout test sleeps longer than its one-second timeout. The signal tests verify expected-signal handling. Fixture tests show setup, teardown, and same-process/parent-process teardown behavior.

State and persistence: no durable state is stored. The only process state change is disabling core dumps to keep intentional `abort()` assertions from producing core files. Fixture state stores `pid_t testpid` to validate where teardown runs.

Dependencies and integration points: depends on POSIX resource/prctl APIs and the harness header. It is not meant to be interpreted by its binary exit code alone; the companion shell script captures stdout and compares it against `harness-selftest.expected`.

Risks: because failures are intentional, running the binary directly can look alarming. Changes in line numbers, logging format, or output stream routing will alter the golden output. The test also validates that low-level ksft result functions are not misused from inside harness tests, so harness internals and public kselftest APIs are coupled here.

Test signals: expected output contains PASS, FAIL, SKIP, XFAIL, XPASS, timeout, assertion, and signal cases. The key signal is whether the full transcript remains stable and whether `test_harness_run()` returns the expected aggregate failure status consumed by the shell wrapper.
