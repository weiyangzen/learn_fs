<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c

## Purpose
`tcp_cong_kern.c` demonstrates selecting DCTCP congestion control and requesting ECN for same-datacenter IPv6 TCP connections through cgroup sock_ops.

## Important APIs, Types, And Functions
`bpf_cong()` handles `BPF_SOCK_OPS_NEEDS_ECN`, `BPF_SOCK_OPS_ACTIVE_ESTABLISHED_CB`, and `BPF_SOCK_OPS_PASSIVE_ESTABLISHED_CB`. It uses `bpf_setsockopt()` with `TCP_CONGESTION`, `bpf_ntohl()`, and `skops->reply`.

## Control Flow
After a port `55601` gate and IPv6 prefix check, the program returns `1` for `NEEDS_ECN` and sets `TCP_CONGESTION` to `"dctcp"` for both active and passive established callbacks. Unsupported operations return `-1`.

## State And Persistence
No maps are present. The persistent effect is per-socket congestion-control state and ECN negotiation behavior.

## Dependencies And Integration Points
It requires cgroup sock_ops attachment and a kernel with DCTCP congestion control available. It integrates with TCP ECN decision callbacks and established socket option updates.

## Risks And Edge Cases
If DCTCP is unavailable, `bpf_setsockopt()` will fail and its error is propagated through `reply`. The address heuristic is IPv6-only and hard-coded. Incorrect deployment can force unsuitable congestion control.

## Test Signals
Connections matching port and prefix should request ECN and show `dctcp` congestion control after establishment. Non-matching traffic should receive `reply = -1` and retain default congestion control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_cong_kern.c -->
