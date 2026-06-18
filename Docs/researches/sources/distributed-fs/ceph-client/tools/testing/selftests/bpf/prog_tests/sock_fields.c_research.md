<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c

Purpose: `sock_fields.c` validates BPF access to `struct bpf_sock`, `struct bpf_tcp_sock`, cgroup IDs, and socket-local storage counters from cgroup skb programs. It drives a real IPv6 TCP connection and checks that ingress/egress programs captured correct socket and TCP state.

Important APIs/types/functions: `check_result()` reads skeleton BSS snapshots of listener/server/client `bpf_sock` and `bpf_tcp_sock`, validates line-number error map entries, and compares cgroup IDs. `check_sk_pkt_out_cnt()` verifies socket storage counters for accepted and client sockets. `init_sk_storage()` seeds two sk_storage maps. `test()` creates the TCP flow and sends data. `serial_test_sock_fields()` sets up netns/cgroups and attaches BPF programs.

Control flow: serial setup unshares a network namespace, brings loopback up, joins parent and child cgroups, records cgroup IDs, opens/loads the skeleton, attaches egress/ingress/read-dst-port programs to the child cgroup, records map FDs, and runs `test()`. The flow listens on `::1:0xcafe`, connects, accepts, seeds storage for the accepted socket, sends two `MSG_EOR` messages from server to client, performs shutdown handshakes, then validates packet counters and captured fields.

State and persistence: state includes the process network namespace after `unshare(CLONE_NEWNET)`, cgroup FDs/IDs, skeleton maps `linum_map`, `sk_pkt_out_cnt`, `sk_pkt_out_cnt10`, BSS snapshots of socket fields, and three TCP socket FDs. No durable files are written.

Dependencies: depends on cgroup skb attach support, sk_storage with spin locks, BPF access to socket/tcp fields, IPv6 loopback TCP, cgroup helper APIs, and specific TCP state/metric behavior after two data packets and shutdown.

Integration points: ties cgroup ingress/egress programs to socket field snapshots, TCP accounting, socket storage counters, and cgroup identity propagation.

Risks: TCP metrics such as `snd_cwnd`, `bytes_acked`, `bytes_received`, and packet counters are kernel-behavior sensitive. The test expects a fixed listen port and therefore creates a dedicated netns. Packet coalescing is mitigated with `MSG_EOR` but remains a networking timing risk. The test is serial because it changes namespace and cgroup state.

Test signals: zero line-number failure for dst-port access, correct listener/server/client socket addresses and ports, sensible TCP counters, expected cgroup IDs, and storage counters at least `0xeB9F + 2/20` for passive and `0xeB9F + 4/40` for active sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/sock_fields.c -->
