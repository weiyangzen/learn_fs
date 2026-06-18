# sources/distributed-fs/ceph-client/tools/testing/selftests/core/unshare_test.c

## Purpose

`unshare_test.c` is a focused regression test for `unshare(CLONE_FILES)` returning `EMFILE` when a shared fd table contains a descriptor above the current `fs.nr_open` limit. It validates kernel behavior when the global maximum open fd count is reduced after a process already holds a high-numbered descriptor.

## Important APIs, Types, and Functions

The test uses `/proc/sys/fs/nr_open`, `getrlimit()/setrlimit(RLIMIT_NOFILE)`, `dup2()`, `sys_clone3()` with `CLONE_FILES`, `unshare(CLONE_FILES)`, `waitpid()`, and kselftest harness assertions. `struct __clone_args` is imported from the clone3 helper.

## Control Flow

The test reads the current `nr_open`, writes a larger value, raises `RLIMIT_NOFILE`, duplicates stderr to `nr_open + 64`, then clones a child sharing file descriptors. The child restores the original `nr_open` before calling `unshare(CLONE_FILES)`, expecting `-1` and `errno == EMFILE`. On every early parent-side setup failure, the original sysctl value is restored before exiting.

## State and Persistence Behavior

The test mutates global `/proc/sys/fs/nr_open`, process rlimits, a high fd slot, and the shared file table. Restoring `nr_open` is critical because the sysctl is host-global. Child exit status persists the result back to the harness.

## Dependencies and Integration Points

It must run as a privileged user able to write `/proc/sys/fs/nr_open`, raise rlimits, use `clone3`, and call `unshare(CLONE_FILES)`. It covers core fdtable allocation and limit validation paths.

## Risks and Edge Cases

The largest risk is environmental: insufficient privilege can leave the test failing or partially changing limits if cleanup paths are interrupted. The interesting kernel edge is a descriptor valid under the old larger limit but invalid after lowering `nr_open`; successful unshare would indicate the kernel copied an fd table beyond the allowed maximum.

## Test Signals

Success is a child exit status of 0 after observing `unshare(CLONE_FILES) == -1` with `errno == EMFILE`. Any different errno, successful unshare, failed restoration, or failed high-fd duplication is a regression signal.
