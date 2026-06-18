<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c

## Purpose

`sk_connect_zero_addr.c` tests that an IPv6 TCP client can connect to a listener bound to the wildcard zero address on the same port.

## Important APIs, Types, and Functions

It uses `socket`, `setsockopt(SO_REUSEADDR)`, `bind([::]:20000)`, `listen`, `connect` to the same zero sockaddr, and `close`.

## Control Flow

The program creates a listening socket on `[::]:20000`, then creates a second socket and calls `connect` using the same zero-address sockaddr. Success requires the kernel to resolve that corner case consistently enough for loopback-style connection establishment.

## State and Persistence Behavior

State is per-process socket state and local TCP listen/connect state. It does not alter sysctls, devices, or files.

## Dependencies and Integration Points

It depends on IPv6 TCP and local socket routing behavior. It is a narrow socket API regression test in the net selftest suite.

## Risks and Edge Cases

Port collisions can cause false failure. The error label says `bind fd2` for a connect failure, so diagnostics are slightly misleading. The test does not accept a connection; it only verifies `connect` return behavior.

## Test Signals

Zero exit indicates connect-to-zero-address behavior remains accepted for the tested listener setup. Any syscall failure returns nonzero with `error(3)` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_connect_zero_addr.c -->
