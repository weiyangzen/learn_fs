# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/assert.c

## Purpose
This file implements the KVM selftest assertion failure path. It prints contextual failure information, emits a stack trace when possible, and exits with the selftest-expected status.

## Important APIs, Types, and Functions
`test_assert()` is the exported noinline assertion handler behind `TEST_ASSERT`. `test_dump_stack()` gathers up to 20 frames with `backtrace()` and runs `addr2line` on the current executable. `_gettid()` wraps `SYS_gettid` for thread-specific diagnostics.

## Control Flow
If an expression is false, `test_assert()` prints file, line, expression, PID, TID, errno, and strerror, dumps the resolved stack, prints optional formatted details, and exits. `EACCES` maps to `KSFT_SKIP`; other assertion failures exit with 254.

## State, Dependencies, and Integration
There is no persistent state. It depends on libc backtrace support, `addr2line`, `kselftest.h`, and `test_util.h`. All KVM selftest libraries and programs rely on this behavior for hard failure reporting.

## Risks and Test Signals
The stack trace uses `system()` and `/proc/$PPID/exe`, so symbolization is best-effort and environment-dependent. The important signal is deterministic process termination with either skip or failure status.
