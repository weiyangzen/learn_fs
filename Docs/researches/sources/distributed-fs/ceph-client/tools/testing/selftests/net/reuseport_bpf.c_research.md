<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf.c

## Purpose

`reuseport_bpf.c` validates classic and extended BPF selectors attached to `SO_REUSEPORT` groups. It checks that incoming packets are dispatched to the socket index returned by the BPF program across IPv4, IPv6, IPv4-mapped IPv6, UDP, TCP with Fast Open, small and large UDP groups, filter replacement, and several invalid filter attachment cases.

## Important APIs, Types, and Functions

`struct test_params` describes address families, protocol, group size, receive port, and send-port base. Helpers include `new_any_sockaddr`, `new_loopback_sockaddr`, `attach_ebpf`, `attach_cbpf`, `build_recv_group`, `send_from`, `test_recv_order`, `test_reuseport_ebpf`, `test_reuseport_cbpf`, `test_extra_filter`, `test_filter_no_reuseport`, `test_filter_without_bind`, `enable_fastopen`, and `setup_netns`. It uses `SO_REUSEPORT`, `SO_ATTACH_REUSEPORT_EBPF`, `SO_ATTACH_REUSEPORT_CBPF`, `bpf(BPF_PROG_LOAD)`, socket-filter BPF instructions, `MSG_FASTOPEN`, `TCP_FASTOPEN`, epoll, `RLIMIT_MEMLOCK`, and `/proc/sys/net/ipv4/tcp_fastopen`.

## Control Flow

Main unshares a network namespace, brings loopback up, then runs grouped test blocks. For each normal BPF case, receivers are created with `SO_REUSEPORT`; the first socket gets a BPF program returning `first_word % mod`; senders bind incrementing source ports and send network-byte-order data; epoll identifies the receiving socket; and the expected socket is `sport % mod`. The test then reattaches a new filter with half the modulus and repeats. Edge cases check two filters in one group fail at bind with `EADDRINUSE`, reuseport filters on non-reuseport sockets fail with `EINVAL`, and filters can be attached before bind.

## State and Persistence Behavior

State is a private network namespace, loopback state, receiver groups, sender sockets, loaded BPF program FDs, temporarily raised `RLIMIT_MEMLOCK`, and possibly a modified TCP Fast Open sysctl in the namespace. Sockets and BPF FDs are closed; the memlock limit is restored by a destructor.

## Dependencies, Integration Points, Risks, and Test Signals

Dependencies include namespace privileges, loopback, BPF syscall support, socket filter verifier support, TCP Fast Open sysctl access, epoll, IPv6, and mapped IPv4 behavior. Integration points are reuseport BPF attachment/replacement, TCP and UDP lookup paths, large UDP reuseport group lookup, and invalid attachment error paths. Risks include missing BPF permissions, memlock limit changes failing silently, Fast Open sysctl not writable, source-port collisions if not isolated, and exact errno assumptions. Signals are per-packet `Socket N: data` lines matching `sport % mod`, expected `EADDRINUSE`/`EINVAL` failures, and final `SUCCESS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/net/reuseport_bpf.c -->
