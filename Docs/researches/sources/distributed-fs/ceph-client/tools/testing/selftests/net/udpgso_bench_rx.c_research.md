# sources/distributed-fs/ceph-client/tools/testing/selftests/net/udpgso_bench_rx.c

Purpose: Receiver and verifier for UDP/TCP GSO/GRO benchmark tests. It binds IPv4 or IPv6 sockets, optionally enables UDP_GRO, accepts TCP, drains receive queues, validates datagram lengths/counts/GRO cmsgs and optional payload patterns, and prints throughput.

Important APIs/functions: uses `SO_RCVBUF`, `SO_REUSEPORT`, `UDP_GRO`, `recvmsg()` with `MSG_TRUNC|MSG_DONTWAIT`, cmsg parsing for `SOL_UDP/UDP_GRO`, `poll`, TCP `accept`, and `SIGINT` interruption. Config flags cover family, bind address, port, TCP, verify, read-all, GRO segment, expected packet count/length/GSO size, connect timeout, and receive timeout.

Control flow: `main()` parses options, installs SIGINT handler, and calls `do_recv()`. `do_socket()` creates/binds sockets and accepts TCP if needed. `do_recv()` optionally sets UDP_GRO, polls with initial connect timeout then receive timeout, flushes TCP or UDP, reports throughput once per second when no fixed expected count is set, and at exit checks expected packet count.

State and persistence: global config plus `packets` and `bytes` counters. No persistent files. State resets per process invocation.

Dependencies and integration: paired with `udpgso_bench_tx.c` and shell wrappers. Requires UDP_GRO kernel support for `-G` and usual socket privileges.

Risks: UDP flush has a budget of 256 datagrams per poll iteration, so extremely bursty traffic is processed over multiple loops. Verify mode only supports UDP, not TCP. Expected GSO cmsg `-S -1` is used by callers to assert no cmsg.

Test signals: exits nonzero on bad length, packet count, GRO cmsg size, payload pattern, socket errors, or poll anomalies. Throughput lines are informational when not in fixed-count mode.
