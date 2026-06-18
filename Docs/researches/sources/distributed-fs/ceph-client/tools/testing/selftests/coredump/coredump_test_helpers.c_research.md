# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test_helpers.c

## Purpose

`coredump_test_helpers.c` implements the shared helpers for the coredump selftests: creating crash workloads, mounting detached tmpfs, setting `core_pattern`, accepting AF_UNIX coredump sockets, extracting pidfd metadata, parsing the coredump socket protocol, and copying core data safely.

## Important APIs, Types, and Functions

Important functions are `do_nothing()`, `crashing_child()`, `create_detached_tmpfs()`, `create_and_listen_unix_socket()`, `set_core_pattern()`, `get_peer_pidfd()`, `get_pidfd_info()`, `recv_marker()`, `read_marker()`, `read_coredump_req()`, `send_coredump_ack()`, `check_coredump_req()`, `open_coredump_tmpfile()`, and `process_coredump_worker()`. It uses `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, `SO_PEERPIDFD`, `PIDFD_GET_INFO`, `O_TMPFILE`, `epoll`, and `MSG_WAITALL`.

## Control Flow

`crashing_child()` spawns 128 sleeping threads and deliberately dereferences NULL. Protocol reading peeks the request size, validates kernel size against `COREDUMP_ACK_SIZE_VER0` and `PAGE_SIZE`, reads the common part, and discards forward-compatible extra bytes. Ack sending can intentionally send smaller or larger structures to test kernel validation. `process_coredump_worker()` switches the coredump fd nonblocking, waits with edge-triggered epoll, drains available bytes into a core file, tolerates `ENOSPC` by continuing, and exits success at EOF.

## State and Persistence Behavior

Helpers create persistent kernel objects and fds: tmpfs mounts represented by fds, Unix socket filesystem entries, pidfds, temporary O_TMPFILE core files, and thread/process state. They write host-global `core_pattern`.

## Dependencies and Integration Points

The implementation depends on Linux fsopen/fsmount syscalls, AF_UNIX sockets, pidfd ioctls, coredump protocol structs, kselftest filesystem wrappers, and the helper declarations in `coredump_test.h`.

## Risks and Edge Cases

`read_coredump_req()` has a forward-compatibility discard path but must avoid blocking on wrong sizes; mismatches surface as protocol failures. `process_coredump_worker()` must close exactly its owned fds after fork. `set_core_pattern()` writes raw strings and relies on the caller to save/restore policy.

## Test Signals

Helper-level failure messages identify setup problems: socket bind/listen, pidfd retrieval, pidfd info ioctl, malformed request sizes/masks, marker mismatch, tmpfile creation, epoll/read/write failures, or worker exit failures.
