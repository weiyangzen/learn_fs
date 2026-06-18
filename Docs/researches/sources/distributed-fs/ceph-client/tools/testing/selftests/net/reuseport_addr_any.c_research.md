<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_addr_any.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_addr_any.c

## Purpose

`reuseport_addr_any.c` tests socket selection preference in `SO_REUSEPORT` groups. It verifies that sockets bound to a specific destination address receive traffic before sockets bound to wildcard addresses, across UDP, TCP, IPv4, IPv6, and IPv4-mapped IPv6.

## Important APIs, Types, and Functions

Key helpers are `build_rcv_fd`, `connect_and_send`, `receive_once`, `test`, `run_one_test`, and `test_proto`. Constants are `127.0.0.1`, `::1`, `::ffff:127.0.0.1`, and port `8888`. The program uses `SO_REUSEPORT`, `bind`, `listen`, `connect`, `send`, `epoll`, `accept`, and `recv`.

## Control Flow

For each protocol family case, `run_one_test` creates wildcard IPv4 and IPv6 sockets before and after a single address-specific socket, registers all sockets in epoll, sends one message to the target address, and checks that the ready FD is the specific-address socket. `test_proto` runs this for UDP IPv4, UDP IPv6, UDP mapped IPv4-to-IPv6, then repeats for TCP.

## State and Persistence Behavior

State is transient sockets on port 8888 in the current namespace and an epoll FD. The program closes all receiver sockets after each case. It does not create its own namespace; the shell wrapper runs it under `in_netns.sh`.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include IPv4/IPv6 loopback, `SO_REUSEPORT`, epoll, and TCP/UDP support. Integration points are reuseport lookup ordering and address-specific versus wildcard selection. Risks are port conflicts outside a namespace, IPv6 disabled, mapped IPv4 behavior varying with sysctls, and a three-millisecond epoll timeout making failures terse. Signals are each case printing `pass` and final `SUCCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_addr_any.c -->
