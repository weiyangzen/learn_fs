# sources/distributed-fs/ceph-client/samples/bpf/hbm_out_kern.c

Purpose: cgroup egress BPF program that enforces bandwidth with a virtual credit/token bucket.

Important APIs/types/functions: `SEC("cgroup_skb/egress") int _hbm_out_cg`, maps and helpers from `hbm_kern.h`, per-cgroup `hbm_vqueue` credit state, and queue stats updates.

Control flow: skips loopback when configured, extracts packet info, obtains local queue state, initializes if needed, locks and refreshes credits based on elapsed time, subtracts packet length, unlocks, applies rate updates from userspace, decides congestion/drop/CWR based on negative credit thresholds and packet type, attempts ECN CE marking, updates stats, restores credit if packet is dropped, and returns cgroup-skb verdict flags.

State and persistence: per-cgroup credit, timestamp, and rate live in `queue_state`; user-visible counters/config live in `queue_stats`.

Dependencies and integration: default program loaded by `hbm.c`, shares ABI with `hbm.h`, requires cgroup skb egress support and BPF spin locks.

Risks: virtual queue does not actually queue, so behavior relies on mark/drop/CWR feedback. Thresholds and `MAX_CREDIT` are fixed. Packet length excludes some link overhead. Concurrent stats updates may skew exact counters.

Test signals: run HBM at a low rate and observe drops/marks, verify `hbm.N.out` counters, and inspect TCP congestion response under ECN and non-ECN flows.
