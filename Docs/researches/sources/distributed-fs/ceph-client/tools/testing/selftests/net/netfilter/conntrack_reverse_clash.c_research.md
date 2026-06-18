## sources/distributed-fs/ceph-client/tools/testing/selftests/net/netfilter/conntrack_reverse_clash.c

Purpose: UDP loopback stress helper for verifying that NAT null bindings do not unexpectedly rewrite source ports during reverse-direction conntrack clashes.

Important APIs and types: uses UDP sockets, `SO_RCVTIMEO`, `bind`, `sendto`, `recvfrom`, `fork`, `wait`, `inet_pton`, and IPv4 sockaddr checks.

Control flow: creates two UDP sockets bound to 127.0.0.11:56789 and 127.0.0.12:56790, forks, and for five seconds both parent and child send fixed-size datagrams to each other. Each side receives on the opposite socket and validates the peer source port is exactly the expected original port. `die_port()` prints the unexpected address/port and exits failure if NAT changed it.

State and persistence: process-local sockets only; no external files. It expects the shell wrapper to install NAT null-binding rules and conntrack flushing. Dependencies are loopback routing for 127/8, socket timeouts, and concurrent execution. Risks include `fork() == 0` without explicit fork failure handling, random receive timeouts treated as fatal, and uninitialized payload content being irrelevant but sent. Test signal is exit 0 if no port changes occur.
