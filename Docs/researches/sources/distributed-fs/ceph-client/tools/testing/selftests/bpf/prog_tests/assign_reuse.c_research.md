# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/assign_reuse.c

Purpose: tests BPF socket assignment and reuseport selection interaction for TCP/UDP over IPv4 and IPv6 inside a dedicated network namespace.

Important APIs/types/functions: `attach_reuseport` applies `SO_ATTACH_REUSEPORT_EBPF`; `cookie` reads `SO_COOKIE`; `echo_test_udp` and `echo_test_tcp` perform one-byte echo flows; `run_assign_reuse` loads `test_assign_reuse.skel.h`, attaches TC ingress and reuseport programs, drives drop and accept cases, and checks BPF-observed socket cookie.

Control flow: top-level creates netns `assign_reuse`, brings loopback up, enters it, and runs four subtests. Each subtest starts one reuseport server, first attaches a drop reuseport program and a TC ingress program that redirects/assigns via a socket map, verifies connection or datagram failure and one reuseport execution, then switches to an accept reuseport program and verifies echo success plus cookie match.

State and persistence behavior: state includes a temporary netns, TC hook on loopback, one server socket FD, one socket-map entry, and skeleton BSS counters. Cleanup detaches TC, destroys hooks, destroys skeleton, frees sockets, restores namespace, and deletes the netns.

Dependencies and integration points: uses `network_helpers.h`, libbpf TC APIs, socket map updates, generated skeleton, `ip netns` commands through `SYS` macros, and CAP/network privileges.

Risks: depends on netns support, loopback index 1, TC hook creation permissions, and timing/errno differences between TCP `ECONNREFUSED` and UDP `EAGAIN`. Cleanup paths must run to avoid lingering netns or TC hooks.

Test signals: drop path expected errors, accept path zero echo result, BPF `reuseport_executed == 1`, and `sk_cookie_seen` equal to userspace `SO_COOKIE`.
