<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c

## Purpose

`socket.c` is a compact syscall validation test for expected success and failure combinations of socket domain/type/protocol arguments.

## Important APIs, Types, and Functions

`struct socket_testcase` records `domain`, `type`, `protocol`, expected result, and whether `EAFNOSUPPORT` is acceptable. `tests[]` covers invalid `AF_MAX`, TCP stream, TCP datagram mismatch, UDP datagram, and UDP stream mismatch. `run_tests` calls `socket`, compares `errno`, and closes successful fds.

## Control Flow

`main` calls `run_tests` and returns its result. The loop continues until a mismatch, then prints the expected and actual error strings and exits nonzero.

## State and Persistence Behavior

Only transient file descriptors are created. There is no persistent state or network configuration mutation.

## Dependencies and Integration Points

It depends on standard socket syscall behavior and kselftest's `ARRAY_SIZE`. It allows `EAFNOSUPPORT` for configured protocol families so kernels without IPv4 support can skip those cases implicitly.

## Risks and Edge Cases

The error message for unexpected success uses `strerror_r(errno)` after a successful socket call, where `errno` may be stale. The expected matrix is intentionally small and does not cover IPv6 or raw sockets.

## Test Signals

Zero exit means all socket argument combinations matched expectations. Nonzero output identifies the first mismatch with domain, type, protocol, expected error, and actual error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/socket.c -->
