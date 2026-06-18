# sources/distributed-fs/ceph-client/net/sched/sch_fq.c

## Purpose
`sch_fq.c` implements the Fair Queue qdisc with per-flow pacing. It is optimized for locally generated traffic where `skb->sk` identifies flows, and it enforces socket/qdisc pacing rates, EDT timestamps, per-flow packet limits, priority bands, and watchdog-based delayed transmission.

## Important APIs, Types, And Functions
`struct fq_sched_data` holds read-mostly configuration, per-band new/old flow queues, the internal fast path flow, flow hash-tree roots, delayed-flow RB tree, watchdog, counters, and statistics. `struct fq_flow` stores per-flow skb queues, timestamp RB tree, socket identity, credit, band, and delayed-tree state. Key functions are `fq_classify()`, `fq_enqueue()`, `fq_dequeue()`, `fq_check_throttled()`, `fq_flow_set_throttled()`, `fq_resize()`, `fq_change()`, `fq_dump()`, and `fq_dump_stats()`.

## Control Flow
Enqueue maps `skb->priority` through a compressed 2-bit priomap to a band, enforces per-band qdisc packet limit, computes `time_to_send` from `skb->tstamp` or current time, and drops or caps packets beyond the configured horizon. `fq_classify()` uses socket pointer identity when possible, hashes orphan/listener/TIME_WAIT-like traffic, may select the internal fast path flow, and otherwise looks up/allocates a `fq_flow` in an RB tree bucket with garbage collection of old detached flows. Dequeue serves the internal fast path first, unthrottles delayed flows whose pacing time has arrived, then iterates weighted bands and each band’s new/old flow lists by deficit. Packets not yet sendable are moved into the delayed RB tree and a qdisc watchdog is scheduled for the earliest delayed time.

## State And Persistence
All operational state is volatile: dynamically allocated `fq_flow` objects in hash buckets, detached flow ages for GC, per-band credits and packet counts, delayed RB-tree nodes, and watchdog state. User-visible configuration is retained in `sch->limit` and fields such as `flow_plimit`, `quantum`, `initial_quantum`, `flow_max_rate`, `horizon`, `offload_horizon`, and priomap/weights, then dumped over netlink. A module-level kmem cache `fq_flow_cachep` persists for the module lifetime.

## Dependencies And Integration Points
FQ integrates with socket pacing (`sk_pacing_rate`, `sk_max_pacing_rate`, `sk_pacing_status`), skb hashes/timestamps, qdisc watchdogs, generic stats and backlog accounting, netlink policies, TCP state helpers, and device `max_pacing_offload_horizon`. It uses `qdisc_peek_dequeued` for qdisc ops peek and `qdisc_dequeue_internal()` when shrinking limits.

## Risks
Flow identity relies on socket pointer lifetime plus `sk_hash` checks; reuse must refill credits and unthrottle stale state. Timestamp ordering is split between a FIFO list and RB tree, so incorrect `time_to_send` handling can reorder packets. Fast path must preserve ordering when delayed flows become eligible. Rate calculations clamp long delays and update `time_next_packet`; low rates force credit exhaustion. Reconfiguration unlocks around `fq_resize()`, so fields changed before resize must tolerate partial `-ENOMEM`. Horizon/offload horizon misconfiguration affects drops versus caps.

## Test Signals
Cover socket and orphan classification, flow allocation failure fallback to internal queue, flow packet limits, band packet limits and weighted band service, delayed-flow watchdog scheduling, offload horizon validation, horizon drop versus cap, CE marking after threshold, low-rate pacing behavior, `fq_resize()` rehash/GC, qdisc limit shrink drops, priomap and weight validation, and stats counters for throttled, GC, fastpath, band drops, horizon drops/caps, allocation errors, and packet-too-long clamps.
