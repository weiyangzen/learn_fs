# sources/distributed-fs/ceph-client/net/sched/sch_skbprio.c

Purpose: implements `skbprio`, a bounded priority qdisc based directly on `skb->priority`. When full, a higher-priority incoming packet displaces a lower-priority queued packet, which is useful for congestion/DoS scenarios where priority admission matters more than fairness.

Important APIs/types/functions: `struct skbprio_sched_data` contains one `sk_buff_head` and `gnet_stats_queue` per priority plus cached highest/lowest non-empty priority. `calc_new_high_prio()` and `calc_new_low_prio()` rescan queues after an extrema queue drains. `skbprio_enqueue()` clamps priority, admits below `sch->limit`, drops incoming low-priority packets at limit, or admits high-priority packets and tail-drops from the lowest-priority queue. `skbprio_dequeue()` services the highest non-empty priority. `skbprio_change()`, `skbprio_init()`, `skbprio_dump()`, reset/destroy, and class ops provide the qdisc ABI.

Control flow: init creates all priority queues, zeros stats, defaults highest to 0, lowest to max, and limit to 64. Enqueue is O(1) unless extrema must be updated after a displaced low-priority queue becomes empty. Dequeue removes from the highest priority and resets extrema when the entire qdisc empties.

State and persistence: state is only in-memory queues, per-priority stats, and cached priority extrema. There are no timers, filters, child qdiscs, or persisted settings beyond the live qdisc instance.

Dependencies/integration: qdisc core, skb queue helpers, `gnet_stats`, `tc_skbprio_qopt`, class walking/dumping, and module alias `NET_SCH("skbprio")`. It relies on callers to set `skb->priority`.

Risks: stale `lowest_prio` can trigger the `BUG_ON(!to_drop)` invariant in the replacement path. Per-priority `qstats[].qlen` is not visibly maintained while used for stats copying. Runtime limit reductions do not proactively trim existing backlog. Priority convention is high numeric value equals higher service priority.

Test signals: enqueue below/at limit, full-queue replacement by high priority, incoming low-priority drops, dequeue ordering, extrema reset, runtime limit dump/change, and per-class stats for backlog/drops/overlimits.
