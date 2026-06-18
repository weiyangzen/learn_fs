# sources/distributed-fs/ceph-client/tools/testing/selftests/cgroup/lib/cgroup_util.c

## Purpose

`cgroup_util.c` is the shared implementation library for cgroup kselftests. It wraps text I/O against cgroupfs/procfs/sysfs, discovers cgroup v1/v2 roots, creates/destroys test cgroups, migrates processes and threads, starts child workloads inside cgroups, and provides polling/inotify helpers used by the cgroup test binaries. The complete 676-line file was read for this report.

## Important APIs, Types, and Functions

The file exports `read_text()`, `write_text()`, `cg_name()`, `cg_name_indexed()`, `cg_control()`, `cg_read()`, `cg_write()`, `cg_open()`, `cg_write_numeric()`, `cg_read_long()`, `cg_read_long_fd()`, `cg_read_key_long()`, `cg_read_key_long_poll()`, `cg_read_lc()`, `cg_read_strcmp*()`, `cg_read_strstr()`, `cg_find_controller_root()`, `cg_find_unified_root()`, `cg_create()`, `cg_destroy()`, `cg_enter*()`, `cg_run()`, `cg_run_nowait()`, `cg_wait_for_proc_count()`, `cg_killall()`, `clone_into_cgroup()`, `clone_reap()`, `clone_into_cgroup_run_wait()`, `dirfd_open_opath()`, `proc_mount_contains()`, `cgroup_feature()`, `proc_read_text()`, `proc_read_strstr()`, `cg_prepare_for_wait()`, `memcg_prepare_for_wait()`, and `cg_wait_for()`. Global `cg_test_v1_named` switches named-v1 compatibility paths.

## Control Flow

The library is intentionally synchronous and file-oriented. Test code builds paths, reads or writes controller files, and checks numeric or string state. Process helpers either fork then write the child PID to `cgroup.procs`, or use `clone3(CLONE_INTO_CGROUP)` when available and fall back to fork migration on `ENOSYS`. Cleanup retries `rmdir()` after killing cgroup members when `EBUSY` is observed. Wait helpers set inotify watches before triggering state changes, then poll for `POLLIN` with EINTR retry.

## State and Persistence Behavior

The only owned global state is `cg_test_v1_named`; all other state is kernel state exposed through cgroupfs, procfs, sysfs, child processes, and transient allocated path strings returned to callers. Functions persist cgroup hierarchy changes, controller settings, process membership, and sysfs writes until cleanup or kernel action reverses them.

## Dependencies and Integration Points

It depends on libc/POSIX APIs, inotify, poll, signals, waitid/waitpid, cgroupfs, `/proc/self/mounts`, `/proc/mounts`, `/sys/kernel/cgroup/features`, and the local `clone3_selftests.h` syscall wrapper. It is included through `libcgroup.mk` into most cgroup selftest binaries.

## Risks and Edge Cases

The helpers return a mix of `-errno`, `-1`, PIDs, and kselftest exit codes, so callers must know each function's contract. `cg_control()` allocations inside `__prepare_for_wait()` are not freed, acceptable for short tests but still a leak. Mount parsing uses `strtok()` over `/proc/self/mounts`; unusual escaping or long mount tables could stress assumptions. Several wait loops use fixed retry budgets, making slow or overloaded systems a source of false failures. The fallback path for `CLONE_INTO_CGROUP` intentionally masks unsupported clone3 features as `ENOSYS`.

## Test Signals

Coverage is indirect through every cgroup selftest. Strong signals include successful root discovery, cgroup creation/destruction under load, process count waits, controller string/numeric reads, `CLONE_INTO_CGROUP` paths, cgroup event inotify waits, and cleanup of spawned workloads without leaked test cgroups.
