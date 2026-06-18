<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c

## Purpose
`tcp_dumpstats_kern.c` is a sock_ops sample that periodically prints selected TCP internal statistics for each socket during RTT callbacks.

## Important APIs, Types, And Functions
The `bpf_next_dump` `BPF_MAP_TYPE_SK_STORAGE` map stores the next dump timestamp per socket. `_sockops()` uses `bpf_sock_ops_cb_flags_set()`, `bpf_sk_storage_get()`, `bpf_ktime_get_ns()`, `bpf_tcp_sock()`, and `bpf_printk()`.

## Control Flow
On `TCP_CONNECT_CB`, it enables RTT callbacks and exits. On `RTT_CB`, it obtains `ctx->sk`, creates or finds per-socket storage, checks whether one second has elapsed, casts to `struct bpf_tcp_sock`, stores the next timestamp, and prints DSACK, delivered, ECN-delivered, and retransmit counters.

## State And Persistence
Per-socket BPF local storage persists while the socket exists and contains the next allowed dump time. Printed statistics are transient trace output.

## Dependencies And Integration Points
It depends on cgroup sock_ops, BPF socket local storage, RTT callback support, and `bpf_tcp_sock()` typed access. It references `samples/bpf/tcp_bpf.readme` for run instructions.

## Risks And Edge Cases
If socket local storage allocation or `bpf_tcp_sock()` fails, the callback silently returns. Trace printing at one-second cadence can still be noisy at scale. It only activates for sockets that receive `TCP_CONNECT_CB`.

## Test Signals
Attach to a cgroup, start TCP connections, and observe one-second `bpf_printk()` lines with `dsack_dups`, `delivered`, `delivered_ce`, and `icsk_retransmits`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcp_dumpstats_kern.c -->
