# sources/distributed-fs/ceph-client/samples/bpf/hbm_edt_kern.c

Purpose: cgroup egress BPF program that enforces bandwidth using Earliest Departure Time (`skb->tstamp`) instead of token credits.

Important APIs/types/functions: `SEC("cgroup_skb/egress") int _hbm_out_cg`, `hbm_get_pkt_info`, `hbm_init_edt_vqueue`, `hbm_update_stats`, `BYTES_TO_NS`, queue storage map `queue_state`, and stats map `queue_stats`.

Control flow: retrieves stats and local cgroup queue state, skips loopback unless configured, parses packet/TCP/ECN info, initializes virtual queue, locks queue state, computes current schedule lag and send time, advances `lasttime` by packet serialization time, unlocks, writes `skb->tstamp`, updates rate if userspace changed it, marks/drops/CWRs packets based on latency thresholds, records stats, and rolls back scheduled time if dropping.

State and persistence: per-cgroup `hbm_vqueue` stores `lasttime` and rate; `queue_stats` stores configuration and counters.

Dependencies and integration: loaded by `hbm.c --edt`, requires cgroup skb egress attachment, fq/qdisc behavior honoring EDT, and helpers from `hbm_kern.h`.

Risks: correctness depends on `skb->tstamp` interpretation by the transmit path. Drop/mark thresholds are fixed constants. Concurrent updates are protected only around queue scheduling; stats use atomic adds. Very small or non-TCP flows have different drop behavior.

Test signals: EDT mode throughput tests, stats showing latency/credit values in milliseconds, verifier acceptance of spin lock and `skb->tstamp` writes, and comparison with non-EDT HBM.
