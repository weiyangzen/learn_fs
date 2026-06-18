# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump_test.c

## Purpose

`stackdump_test.c` verifies that pipe-style coredump helpers can inspect all threads of a crashing process and read nonzero stack pointer values from procfs during coredump handling.

## Important APIs, Types, and Functions

The test uses the coredump fixture, `crashing_child()`, `readlink("/proc/self/exe")`, `dirname()`, writes `/proc/sys/kernel/core_pattern`, forks a crashing process, waits for `WCOREDUMP()`, then reads `stack_values` with `getline()` and `strtoull()`.

## Control Flow

Fixture setup saves the original `core_pattern` and creates detached tmpfs. The test computes the test binary directory, writes a pipe pattern invoking `stackdump %P stack_values`, forks a child that spawns 128 threads and crashes, waits for the coredump, polls up to 10 seconds for the output file, then validates every stack value is nonzero and the count equals `1 + NUM_THREAD_SPAWN`.

## State and Persistence Behavior

It temporarily rewrites host `core_pattern`, creates/removes `stack_values`, and uses many child threads. Teardown restores `core_pattern`, kills any leftover server pid, unlinks temporary files, and closes detached tmpfs.

## Dependencies and Integration Points

It depends on root-level core_pattern writes, procfs task visibility, the `stackdump` helper script installed next to the binary, and kselftest harness timeouts.

## Risks and Edge Cases

The test is race-sensitive around helper completion and procfs task state. System coredump policy, core ulimits, or missing script installation can prevent output creation. The expected thread count relies on all pthread creations succeeding.

## Test Signals

Success requires signaled child termination with core dump, output file creation, all stack values nonzero, and exact line count. Failures indicate pipe helper invocation, procfs stack reporting, or multithreaded coredump visibility regressions.
