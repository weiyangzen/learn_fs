# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/prog_tests/tcp_rtt.c

Purpose: `tcp_rtt.c` validates that a BPF sockops program can read TCP RTT-related fields from `bpf_tcp_sock` and store them in socket local storage during connection establishment and after data delivery.

Important APIs/types/functions: `struct tcp_rtt_storage` mirrors values stored by the BPF program: invocation count, duplicate SACK count, delivered counts, ECN-delivered count, retransmits, measured RTT, and smoothed RTT. `send_byte()` writes one byte. `wait_for_ack()` polls `TCP_INFO.tcpi_unacked` until the byte is acknowledged. `verify_sk()` reads `socket_storage_map` with the client fd key and checks expected counters plus nonzero RTT fields. `run_test()` loads `tcp_rtt.skel.h`, attaches `_sockops` to a cgroup, opens a client connection to a server fd, verifies initial SYN-ACK state, sends a byte, waits for ACK, and verifies updated state. `test_tcp_rtt()` creates cgroup `/tcp_rtt` and a TCP server.

Control flow: the top-level test joins a cgroup, starts an IPv4 TCP server, and calls `run_test()`. The BPF program is attached as `BPF_CGROUP_SOCK_OPS`. After `connect_to_fd()`, `verify_sk()` expects one invocation and delivered count 1. After sending one byte and waiting for the ACK, `verify_sk()` expects two invocations and delivered count 2. Cleanup closes the client, destroys the skeleton, closes the server, and closes the cgroup fd.

State and persistence: state includes a temporary cgroup fd/link, a BPF socket-storage map keyed by socket fd, one server socket, one client socket, TCP_INFO polling state, and kernel TCP statistics. No files are written.

Dependencies: depends on generated `tcp_rtt.skel.h`, cgroup sockops support, BPF socket storage, IPv4 TCP sockets, `network_helpers.h`, and `TCP_INFO` reporting from the kernel.

Integration points: this userspace test validates a BPF sockops program's interaction with kernel TCP state and socket local storage. It is part of the broader TCP BPF selftest area.

Risks: RTT fields are timing-dependent, so the test only requires nonzero values rather than exact numbers. `wait_for_ack()` sleeps only 10 microseconds per retry for 100 retries, which can be tight on slow or loaded environments. It relies on socket fd keys for map lookup, which is the expected userspace side of the selftest but would fail if BPF storage keying changes.

Test signals: expected signals are successful cgroup join, server start, skeleton load, sockops attach, socket storage map lookup, `invoked` 1 then 2, delivered 1 then 2, zero dsack/CE/retransmit counts, and nonzero `mrtt_us` and `srtt`.
