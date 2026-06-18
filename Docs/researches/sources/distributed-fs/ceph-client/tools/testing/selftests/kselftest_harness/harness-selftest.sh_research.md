# sources/distributed-fs/ceph-client/tools/testing/selftests/kselftest_harness/harness-selftest.sh

Purpose: this shell script is the executable kselftest entry point for the harness selftest. It normalizes execution through a wrapper so the intentionally failing C test binary can still be judged by output comparison.

Important APIs and commands: it uses `/bin/sh`, `set -e`, `readlink -f "$0"` to locate its directory, runs `"$DIR"/harness-selftest > harness-selftest.seen || true`, and then invokes `diff -u "$DIR"/harness-selftest.expected harness-selftest.seen`.

Control flow: the script resolves the directory containing itself, executes the compiled `harness-selftest` binary while capturing stdout into `harness-selftest.seen`, ignores the binary's nonzero exit status because failures are intentional, and fails or passes based on the unified diff result.

State and persistence: it creates or overwrites `harness-selftest.seen` in the current working directory, not necessarily in `$DIR`. The Makefile lists this file in `EXTRA_CLEAN`. No other state is kept.

Dependencies and integration points: depends on the compiled binary and `harness-selftest.expected` being installed together by the Makefile. It integrates with kselftest as `TEST_PROGS`, so runner status comes from the shell script's `diff` result.

Risks: writing `harness-selftest.seen` relative to the caller can be surprising if the runner changes cwd. Output comparison is intentionally brittle to catch format regressions; harmless whitespace or line-number shifts can fail the test.

Test signals: successful execution produces no diff output and exits zero. Any harness behavior change appears as a `diff -u` failure.
