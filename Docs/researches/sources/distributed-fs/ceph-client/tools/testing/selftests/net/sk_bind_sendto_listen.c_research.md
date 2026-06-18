<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c

## Purpose

`sk_bind_sendto_listen.c` is a regression test for IPv6 TCP sockets bound to the wildcard address when `MSG_FASTOPEN` send attempts happen before a later `listen`.

## Important APIs, Types, and Functions

The program uses `socket(AF_INET6, SOCK_STREAM, IPPROTO_IP)`, `setsockopt(SO_REUSEADDR)`, `bind` to `[::]:20000`, `sendto(..., MSG_FASTOPEN, ...)`, `listen`, and `close`. It uses `error(3)` for diagnostics.

## Control Flow

It creates `fd1`, enables reuse, binds, and performs a zero-length fast-open `sendto` to the same wildcard address. Then it creates `fd2`, enables reuse, binds to the same address, expects a second `MSG_FASTOPEN` `sendto` to fail, and finally verifies that `listen(fd2, 0)` succeeds. Cleanup closes both descriptors.

## State and Persistence Behavior

Only local socket binding state exists. `SO_REUSEADDR` permits the second bind in the tested state. No persistent network configuration is changed.

## Dependencies and Integration Points

It depends on IPv6 TCP support and the kernel TCP Fast Open send path accepting `MSG_FASTOPEN` semantics. It integrates with socket bind/listen state transition regression coverage.

## Risks and Edge Cases

The test intentionally uses wildcard `::` as a destination, which is unusual but targets a specific kernel corner case. It expects the second fast-open send to fail; if it succeeds, that is a failure even though success would look superficially harmless. Port 20000 conflicts could make the first bind fail.

## Test Signals

Zero exit means first bind/send path and second bind/listen path behaved as expected. Nonzero exit pinpoints which socket operation violated the expected state transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/sk_bind_sendto_listen.c -->
