<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_dualstack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_dualstack.c

## Purpose

`reuseport_dualstack.c` tests dual-stack reuseport socket selection. It verifies that IPv4 traffic prefers AF_INET reuseport sockets over AF_INET6 wildcard sockets when both groups are bound to equivalent local addresses, including group creation order variations and large UDP groups.

## Important APIs, Types, and Functions

Helpers are `build_rcv_fd`, `send_from_v4`, `receive_once`, `test`, and `setup_netns`. The program uses `SO_REUSEPORT`, AF_INET/AF_INET6 sockets, UDP/TCP, `SO_DOMAIN` getsockopt, epoll, accept/recv, and network namespace unshare. Fixed port is `8888`.

## Control Flow

Main creates a private namespace and runs six cases: UDP IPv4 receivers before IPv6, UDP IPv6 before IPv4, large UDP IPv4 before IPv6, large UDP IPv6 before IPv4, TCP IPv4 before IPv6, and TCP IPv6 before IPv4. Each case creates both AF_INET and AF_INET6 reuseport receivers, sends one IPv4 loopback message, uses epoll to find the receiver, queries the receiver domain with `SO_DOMAIN`, and requires AF_INET.

## State and Persistence Behavior

State is a private netns, loopback state, receiver sockets, epoll FD, and short-lived sender sockets. All FDs are closed after each case.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include IPv4/IPv6 support, reuseport, epoll, TCP/UDP, and namespace privileges. Integration points are dual-stack socket lookup ordering and reuseport fast selection for large UDP groups. Risks include IPv6 disabled, port conflicts if namespace setup fails, and kernels changing v4-over-v6 wildcard precedence. Signals are no domain mismatch errors and final `SUCCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_dualstack.c -->
