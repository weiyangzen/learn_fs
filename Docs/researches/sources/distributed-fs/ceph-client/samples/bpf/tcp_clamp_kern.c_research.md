<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c

## Purpose
`tcp_clamp_kern.c` is a sock_ops sample that sets short SYN RTOs, 150 KB buffers, and a send congestion-window clamp for same-datacenter IPv6 TCP connections.

## Important APIs, Types, And Functions
`bpf_clamp()` handles `BPF_SOCK_OPS_TIMEOUT_INIT`, connect, active established, and passive established callbacks. It uses `bpf_setsockopt()` for `SO_SNDBUF`, `SO_RCVBUF`, and `TCP_BPF_SNDCWND_CLAMP`, plus `skops->reply`.

## Control Flow
The program filters to port `55601`, checks IPv6 prefix similarity, then returns timeout init `10`, sets buffers on active connect, sets the cwnd clamp on active established, and sets clamp plus buffers on passive established. Non-matching cases return `-1`.

## State And Persistence
There is no map state. Per-socket state changes persist as TCP options for the lifetime of the connection.

## Dependencies And Integration Points
It depends on cgroup sock_ops, TCP BPF setsockopt support, and the TCP `TCP_BPF_SNDCWND_CLAMP` option. It integrates with TCP handshake and established callbacks.

## Risks And Edge Cases
The sample hard-codes datacenter and port heuristics and can impose unsuitable RTO/clamp values outside the intended environment. One early unmatched-port branch returns `0` while setting reply `-1`, unlike most other samples. Return-code accumulation can hide partial setsockopt failures.

## Test Signals
Verify SYN/SYN-ACK timeout reply `10`, buffer sizes, and cwnd clamp for matching IPv6/port traffic. Non-matching prefixes or ports should leave TCP defaults unchanged.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_clamp_kern.c -->
