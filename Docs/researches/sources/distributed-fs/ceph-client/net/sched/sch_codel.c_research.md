# sources/distributed-fs/ceph-client/net/sched/sch_codel.c

## Purpose
`sch_codel.c` adapts the generic Controlled Delay AQM implementation to a simple FIFO qdisc. It timestamps packets on enqueue, delegates drop/mark scheduling to `net/codel_impl.h`, and exposes CoDel configuration and stats through traffic-control netlink.

## Important APIs, Types, and Functions
`struct codel_sched_data` contains `codel_params`, `codel_vars`, `codel_stats`, and an overlimit drop counter. CoDel-specific callbacks passed to the generic implementation are `dequeue_func()` and `drop_func()`. Qdisc callbacks are `codel_qdisc_enqueue()`, `codel_qdisc_dequeue()`, `codel_change()`, `codel_init()`, `codel_dump()`, `codel_dump_stats()`, and `codel_reset()`.

## Control Flow
Initialization sets the default packet limit to 1000, initializes CoDel params/vars/stats, captures device MTU, applies optional netlink configuration, enables bypass when the limit is nonzero, and marks the qdisc as having dequeue-side drops. Enqueue succeeds while `qdisc_qlen(sch) < sch->limit`: it records enqueue time and appends to the tail. Over-limit enqueue increments `drop_overlimit` and drops with `QDISC_DROP_OVERLIMIT`.

Dequeue calls `codel_dequeue()` with backlog pointer, parameter/state/stat structures, packet length and enqueue time accessors, and the local drop/dequeue callbacks. The generic CoDel code may drop one or more packets before returning an skb; if so, `codel_qdisc_dequeue()` propagates drop count/bytes to parent qdiscs with `qdisc_tree_reduce_backlog()`, then clears deferred counters. Successful dequeue updates byte stats.

Configuration parses target, limit, interval, ECN enable, and CE threshold. It updates fields under `sch_tree_lock()` and, if the new limit is below current qlen, dequeues and drops excess packets, then reduces parent backlog. Dump serializes current params and only emits CE threshold when enabled.

## State and Persistence
The FIFO queue is the embedded `sch->q`. CoDel runtime state includes count, lastcount, drop_next, dropping flag, latest delay, max packet, ECN/CE stats, and deferred drop counters. This state resets on qdisc reset and is not persisted beyond qdisc lifetime. Netlink dumps expose configuration and current algorithm stats only.

## Dependencies and Integration Points
The file depends on `net/codel.h`, `net/codel_impl.h`, and `net/codel_qdisc.h` for the algorithm. It uses qdisc core queue helpers, gnet stats, netlink `TCA_CODEL_*` attributes, and `qdisc_tree_reduce_backlog()` from the scheduler API. It registers qdisc id `codel`.

## Risks
Most algorithmic risk is in the generic CoDel implementation, but this adapter must maintain backlog correctly because CoDel drops occur during dequeue. Limit changes can drop many packets while locked, so byte counters must match. Time units are shifted CoDel time units; incorrect microsecond-to-CoDel conversion would change control behavior. `drop_func()` updates qdisc drop stats, while parent backlog reduction is deferred, so both paths must remain paired.

## Test Signals
Test default init/dump, target/interval/limit/ECN/CE-threshold changes, enqueue over limit, limit reduction with queued packets, dequeue-side dropping under persistent delay, ECN marking when enabled, reset clearing queue and CoDel vars, and parent backlog consistency after deferred drops.
