# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_protocol_test.c

## Purpose

`coredump_socket_protocol_test.c` validates the extended coredump socket protocol selected by `@@/path` in `kernel.core_pattern`. It tests request/ack negotiation, coredump data delivery, reject/userspace modes, invalid ack handling, signal metadata exposure through pidfd info, and multiple concurrent crashing tasks.

## Important APIs, Types, and Functions

The file uses the shared coredump fixture and helpers from `coredump_test.h`: `set_core_pattern()`, `create_and_listen_unix_socket()`, `get_peer_pidfd()`, `get_pidfd_info()`, `read_coredump_req()`, `check_coredump_req()`, `send_coredump_ack()`, `read_marker()`, `open_coredump_tmpfile()`, and `process_coredump_worker()`. Kernel protocol types and constants come from `<linux/coredump.h>`, including `struct coredump_req`, `COREDUMP_KERNEL`, `COREDUMP_USERSPACE`, `COREDUMP_REJECT`, `COREDUMP_WAIT`, and `COREDUMP_MARK_*`.

## Control Flow

Each fixture setup saves `core_pattern` and creates a detached tmpfs for temporary core files. A server process binds `/tmp/coredump.socket`, signals readiness to the parent via a socketpair, accepts one or more coredump connections, validates peer pidfd coredump info, reads the request, sends an ack, and then either reads core bytes or expects no bytes depending on the ack.

The individual tests cover kernel-delivered core data, userspace-only ack, explicit reject, conflicting ack flags, unknown ack flags, too-small and too-large ack sizes, SIGSEGV and SIGABRT metadata, five sequential crashing coredumps, and five coredumps copied by forked epoll workers. Parent processes fork crashing children, open pidfds, wait for signal/core status, and validate `PIDFD_INFO_COREDUMP` fields.

## State and Persistence Behavior

The tests temporarily rewrite `/proc/sys/kernel/core_pattern`, create/unlink `/tmp/coredump.socket` and `/tmp/coredump.file`, create anonymous tmpfs files, and spawn crash children, coredump servers, and worker processes. `self->pid_coredump_server` tracks server lifetime for teardown. Runtime protocol state is carried on the accepted AF_UNIX connection.

## Dependencies and Integration Points

The tests require coredump socket support, AF_UNIX sockets, pidfd support including `SO_PEERPIDFD` and `PIDFD_GET_INFO`, tmpfs fsopen/fsmount helpers, and the kselftest harness. They integrate with kernel coredump plumbing, pidfd metadata, and the protocol ABI in `linux/coredump.h`.

## Risks and Edge Cases

The tests are sensitive to privilege because writing `core_pattern` is usually root-only. Timing matters around server readiness and crash completion. Protocol compatibility is checked using minimum sizes and masks, so kernel additions should not break request reading, but unsupported markers or size limits should be surfaced. Concurrent coredumps stress server serialization, pidfd reference handling, and worker fd ownership.

## Test Signals

Positive signals include successful request validation, expected marker receipt, non-empty core files for `COREDUMP_KERNEL`, no data for userspace/reject paths, correct `WCOREDUMP()` results, correct `coredump_signal` and `coredump_code`, and all worker/server exits with status 0. Failures isolate protocol negotiation, pidfd metadata, marker selection, data streaming, or concurrency regressions.
