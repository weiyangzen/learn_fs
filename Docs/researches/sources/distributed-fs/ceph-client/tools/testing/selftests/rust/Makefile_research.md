<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rust/Makefile

## Purpose

Tiny kselftest make fragment that registers the Rust sample probe script as the Rust selftest program.

## Important APIs, Types, and Functions

Uses TEST_PROGS += test_probe_samples.sh and includes ../lib.mk so install/run targets pick up the shell test.

## Control Flow and Integration

The kselftest build includes this Makefile, installs the script, and delegates execution to the common selftest runner.

## State and Persistence Behavior

No runtime state; only build metadata.

## Dependencies and Integration Points

Depends on tools/testing/selftests/lib.mk and the neighboring test_probe_samples.sh.

## Risks and Edge Cases

If TEST_PROGS is wrong the Rust module smoke test silently disappears from kselftest runs.

## Test Signals

`make -C tools/testing/selftests/rust run_tests` should execute test_probe_samples.sh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rust/Makefile -->
