# sources/distributed-fs/ceph-client/tools/testing/selftests/core/close_range_test.c

## Purpose

`close_range_test.c` is a kselftest harness program for Linux file descriptor table behavior around `close_range(2)`, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`, sparse fd tables, clone-shared file tables, and newer `fcntl()` query commands. It is regression-oriented: several cases reproduce syzkaller/bitmap bugs and verify the fd table remains internally consistent after range closing or close-on-exec marking.

## Important APIs, Types, and Functions

The file wraps `syscall(__NR_close_range, fd, max_fd, flags)` as `sys_close_range()` and uses `sys_clone3()` from `../clone3/clone3_selftests.h` with `CLONE_FILES` to create children sharing the parent's fd table. It uses `open()`, `dup2()`, `dup()`, `close()`, `fcntl(F_GETFL)`, `fcntl(F_GETFD)`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `getrlimit()/setrlimit(RLIMIT_NOFILE)`, `waitpid()`, `WIFEXITED()`, and `WEXITSTATUS()`. Test definitions come from `kselftest_harness.h`.

## Control Flow

`core_close_range` opens 101 `/dev/null` descriptors, verifies invalid flag handling, checks duplicate-file queries, closes selected ranges, verifies gaps do not matter, and confirms single-fd closure. `close_range_unshare` and `close_range_unshare_capped` repeat range close logic in a `CLONE_FILES` child with `CLOSE_RANGE_UNSHARE`, ensuring the child gets a private table before mutation. `close_range_cloexec` and `close_range_cloexec_unshare` set `FD_CLOEXEC` over two ranges and then from fd 3 to `UINT_MAX`, including under a low soft `RLIMIT_NOFILE`.

The syzbot regressions build sparse tables with descriptors at low fd and fd 1000, then exercise `CLOSE_RANGE_CLOEXEC` with and without `CLOSE_RANGE_UNSHARE`. The bitmap corruption test opens descriptors 2 through 127, unshares and truncates at 64 in a child, then verifies `dup(0)` reuses fd 64 rather than seeing the secondary bitmap as full. `fcntl_created` verifies `F_CREATED_QUERY` distinguishes existing `/dev/null`, a newly created temporary file, and reopening that file.

## State and Persistence Behavior

The main state is process fd table state: open/closed slots, shared versus unshared `files_struct`, close-on-exec bits, and fd allocation bitmaps. The test also temporarily changes the process soft `RLIMIT_NOFILE` in CLOEXEC cases and creates/unlinks temporary `aaaa_N` files. Child processes exit with success/failure to report table state back to the parent.

## Dependencies and Integration Points

The test requires `close_range(2)`, `clone3(2)`, `/dev/null`, kselftest harness support, and Linux-specific fcntl commands that may return `EINVAL` on kernels that lack them. It integrates with the kernel core selftests and targets fs/file-table implementation details, clone fd-table sharing, and exec inheritance semantics.

## Risks and Edge Cases

The tests intentionally stress gaps, `UINT_MAX`/`~0U` bounds, low rlimits, duplicate descriptors sharing the same file object, duplicated descriptors clearing `FD_CLOEXEC`, and descriptor-table shrinking. They skip only selected unsupported syscall/flag cases; environments without `clone3` or enough fd capacity can fail rather than skip. The syzbot tests are sensitive to whether `CLOSE_RANGE_UNSHARE` should isolate the parent from child-side mutations.

## Test Signals

Pass signals are exact `fcntl()` visibility checks, `FD_CLOEXEC` bit checks, child exit code 0, `WCOREDUMP`-independent process exit validation, and successful `F_CREATED_QUERY` results. Failures point to fd closure leaks, lost close-on-exec flags, incorrect unshare semantics, sparse-table corruption, or wrong created-file tracking.
