# sources/distributed-fs/ceph-client/tools/testing/selftests/clone3/clone3_selftests.h

## Purpose

`clone3_selftests.h` provides a local clone3 syscall ABI wrapper and support probe used by clone3 and cgroup tests. The complete 69-line file was read.

## Important APIs, Types, and Functions

It defines `ptr_to_u64()`, fallback `__NR_clone3`, local `struct __clone_args`, `sys_clone3()`, and `test_clone3_supported()`.

## Control Flow

`sys_clone3()` flushes stdio and invokes `syscall(__NR_clone3, args, size)`. `test_clone3_supported()` calls clone3 with an intentionally invalid `exit_signal`; if clone3 is unavailable it skips, if it unexpectedly creates a child it fails, otherwise it prints supported.

## State and Persistence Behavior

The header has no persistent state. The probe can create and reap a child only if the kernel incorrectly accepts an invalid signal, which is treated as failure.

## Dependencies and Integration Points

It depends on Linux scheduler/types headers, syscall numbers, kselftest helpers, and wait APIs. It is included by clone3 tests and by cgroup utility code for `CLONE_INTO_CGROUP`.

## Risks and Edge Cases

The local `struct __clone_args` must match the kernel ABI. Fallback syscall number 435 is architecture-sensitive but used when headers lack `__NR_clone3`. The support probe treats only `ENOSYS` as unsupported; other errors imply support.

## Test Signals

Compile success and `clone3() syscall supported` output are the primary signals; downstream tests validate the wrapper more deeply.
