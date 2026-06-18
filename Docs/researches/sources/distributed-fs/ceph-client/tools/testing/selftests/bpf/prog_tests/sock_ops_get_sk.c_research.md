<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c

Purpose: `sock_ops_get_sk.c` verifies that a sock_ops BPF program can obtain and use a socket reference through the get-sk helper path during a TCP connection.

Important APIs/types/functions: `run_sock_ops_test()` attaches a sock_ops program to a cgroup with `bpf_prog_attach(BPF_CGROUP_SOCK_OPS)`, starts an IPv6 TCP server, connects a client, and closes both sockets. `test_ns_sock_ops_get_sk()` loads `sock_ops_get_sk.skel.h`, joins `/sock_ops_get_sk`, runs the helper test, and destroys the skeleton.

Control flow: load skeleton, join cgroup, obtain program FD for `sockops_get_sk`, attach to cgroup, create server and client connection, then close sockets and cgroup FD. Assertions ensure program attach and socket operations succeed.

State and persistence: state is limited to a cgroup FD, BPF program attachment, server/client socket FDs, and skeleton lifetime. No durable state is written.

Dependencies: requires cgroup sock_ops attach support, IPv6 loopback TCP, the paired skeleton, and selftest network/cgroup helpers.

Integration points: connects sock_ops cgroup hooks with real TCP connection establishment so the BPF-side helper can be exercised in kernel context.

Risks: userspace does not inspect BPF-side counters, so detailed helper correctness must be asserted by the BPF object or verifier. If the program loads and attaches but silently does not observe the expected callback, this wrapper may not detect it unless BPF-side state causes failure.

Test signals: successful skeleton load, cgroup join, sock_ops attach, server start, and client connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_ops_get_sk.c -->
