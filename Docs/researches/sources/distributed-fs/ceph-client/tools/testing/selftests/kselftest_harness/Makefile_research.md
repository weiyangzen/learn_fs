# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/Makefile

Purpose: this small kselftest makefile defines the build and run artifacts for the harness selftest.

Important APIs and variables: `TEST_GEN_PROGS_EXTENDED := harness-selftest` builds the C binary but does not make it a direct default program test. `TEST_PROGS := harness-selftest.sh` makes the shell wrapper the test entry point. `TEST_FILES := harness-selftest.expected` installs the golden output file alongside the script. `EXTRA_CLEAN := harness-selftest.seen` removes the captured output. `include ../lib.mk` delegates standard kselftest build, install, and clean behavior.

Control flow: kselftest make infrastructure compiles `harness-selftest` from `harness-selftest.c`, installs the expected-output file, and runs `harness-selftest.sh`. The shell wrapper executes the binary, captures output, and diffs it against the expected fixture.

State and persistence: generated state is limited to the compiled binary and `harness-selftest.seen`; both are build artifacts, not source state. The expected output is treated as a test fixture.

Dependencies and integration points: depends on the selftests `lib.mk` convention for `TEST_GEN_PROGS_EXTENDED`, `TEST_PROGS`, `TEST_FILES`, and `EXTRA_CLEAN`. It integrates with `make kselftest`, `make install`, and the top-level selftest runner.

Risks: if the expected file is missing or harness output changes intentionally, the shell test fails until the fixture is updated. Marking the C binary as extended is important because running it directly is expected to produce failing cases as part of the golden transcript.

Test signals: a passing run is a clean `diff -u` between `harness-selftest.expected` and `harness-selftest.seen`; any stdout formatting drift, TAP count change, timeout change, or result-code classification change appears as a diff.
