# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/include/cgroup_util.h

## Purpose

`cgroup_util.h` is the public header for the cgroup kselftest utility library. It declares cgroupfs helpers, process-launch helpers, procfs helpers, wait helpers, constants, and small tolerance utilities shared by the cgroup controller tests. The complete 100-line file was read.

## Important APIs, Types, and Functions

Key constants/macros are `PAGE_SIZE`, `MB(x)`, `USEC_PER_SEC`, `NSEC_PER_SEC`, `TEST_UID`, `CG_THREADS_FILE`, `CG_NAMED_NAME`, `CG_PATH_FORMAT`, and `DEFAULT_WAIT_INTERVAL_US`. Inline helpers `values_close()` and `values_close_report()` compare expected and actual numeric metrics with percentage tolerance. The header declares all exported functions from `cgroup_util.c`, including cgroup path, read/write, process migration, clone3, kill, mount-feature, proc-read, and inotify wait APIs.

## Control Flow

The header has no standalone runtime flow. It shapes caller control flow by providing a uniform cgroup operation vocabulary and kselftest-friendly comparison helpers used in assertions across CPU, memory, freezer, pids, zswap, and cpuset tests.

## State and Persistence Behavior

No storage is owned by the header. It declares external `cg_test_v1_named`, which changes thread-file and `/proc/*/cgroup` path formatting for named v1 cgroup tests.

## Dependencies and Integration Points

It includes `stdbool.h` and `stdlib.h`; prototypes also require surrounding translation units to provide POSIX types such as `ssize_t`, `pid_t`, and `useconds_t`. It is consumed through `libcgroup.mk` and by cgroup test C sources.

## Risks and Edge Cases

`MB(x)` is a left shift and depends on integer width/type at the call site. `values_close()` divides by `(a + b)` and can understate tolerance for small values; `values_close_report()` handles zero only for reporting. The header omits `extern` on a few declarations but remains valid C.

## Test Signals

Compile coverage for all cgroup selftest binaries is the primary signal. Runtime signal comes from tolerance helpers accepting expected accounting variance while still catching controller regressions.
