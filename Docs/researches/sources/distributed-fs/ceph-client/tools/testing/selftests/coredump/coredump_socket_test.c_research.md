# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_test.c

## Purpose

`coredump_socket_test.c` validates the simpler `@/path` coredump socket mode. It confirms kernel-originated coredump clients are distinguishable from normal userspace clients, coredump bytes can be captured over AF_UNIX sockets, missing or non-listening sockets suppress core dumps, invalid socket paths are rejected, and pidfd coredump signal/code metadata is correct.

## Important APIs, Types, and Functions

The file uses the coredump fixture from `coredump_test.h`, helper functions from `coredump_test_helpers.c`, `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `get_pidfd_info()`, `SO_PEERPIDFD`, `PIDFD_GET_INFO`, `PIDFD_INFO_COREDUMP`, `PIDFD_INFO_COREDUMP_SIGNAL`, and `PIDFD_INFO_COREDUMP_CODE`. It uses AF_UNIX `socketpair()`, `bind()`, `listen()`, `accept4()`, `connect()`, and normal file I/O to copy coredump bytes.

## Control Flow

The main socket test sets `core_pattern` to `@/tmp/coredump.socket`, starts a listener child, accepts the kernel coredump connection, checks `PIDFD_COREDUMPED`, copies bytes to `/tmp/coredump.file`, and verifies that file is non-empty. `socket_detect_userspace_client` connects a normal child to the same socket and checks that `PIDFD_COREDUMPED` is not set. `socket_enoent` and `socket_no_listener` verify missing and unlistened sockets do not produce coredumps. Signal tests crash by NULL dereference or `abort()` and verify SIGSEGV/SEGV_MAPERR or SIGABRT/SI_TKILL. `socket_invalid_paths` writes malformed `@`/`@@` patterns and expects `set_core_pattern()` failure.

## State and Persistence Behavior

The fixture saves/restores `/proc/sys/kernel/core_pattern`, creates a detached tmpfs, tracks the coredump server pid, and removes `/tmp/coredump.socket` and `/tmp/coredump.file` in teardown. Tests create pidfds and short-lived children; one userspace-client test kills a paused child via pidfd.

## Dependencies and Integration Points

It depends on root-level `core_pattern` writes, AF_UNIX socket support, pidfd metadata support, kselftest harness infrastructure, and `coredump_test_helpers.c`. It integrates directly with kernel core dump routing and pidfd coredump state.

## Risks and Edge Cases

The path validation tests are ABI-sensitive because they expect traversal, spaces, double-at misuse, and triple-at patterns to fail. `socket_no_listener` distinguishes a bound socket path without `listen()` from an active server. Coredump status can be affected by core ulimits or unrelated system policy if the environment blocks dumps.

## Test Signals

Pass signals include server exit status 0, non-empty core file only for true kernel coredumps, no created core file for userspace clients, `WCOREDUMP()` true or false as expected, pidfd coredump flags matching client type, and rejected invalid path writes.
