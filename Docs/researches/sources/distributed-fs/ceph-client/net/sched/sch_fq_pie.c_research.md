# sources/distributed-fs/ceph-client/net/sched/sch_fq_pie.c

## Purpose
`sch_fq_pie.c` implements Flow Queue PIE: a stochastic fixed-flow-table fair queue where each flow uses PIE active queue management. Drops or ECN marks occur on enqueue, while dequeues use new/old flow DRR scheduling.

## Important APIs, Types, And Functions
`struct fq_pie_sched_data` stores classifier block, fixed flow table, PIE params/stats, adaptive timer, memory/flow counters, quantum, and new/old flow lists. `struct fq_pie_flow` stores per-flow PIE vars, deficit, backlog, qlen, list node, and skb FIFO. Main functions are `fq_pie_classify()`, `fq_pie_qdisc_enqueue()`, `fq_pie_qdisc_dequeue()`, `fq_pie_change()`, `fq_pie_timer()`, `fq_pie_init()`, `fq_pie_dump()`, and `fq_pie_dump_stats()`.

## Control Flow
Classification mirrors FQ-CoDel: explicit classid, optional external classifier, or hash fallback. Enqueue checks qdisc packet limit and memory limit, invokes `pie_drop_early()` with the selected flow’s PIE vars and backlog, optionally ECN-marks if PIE probability is below `ecn_prob`, then enqueues and activates the flow if accepted. Dequeue serves new flows before old flows, replenishes deficit by quantum, removes a head packet, updates qdisc and flow backlog/qlen/memory, and calls `pie_process_dequeue()`. The adaptive timer locks the root qdisc and updates PIE probability for up to 2048 flows per tick, rescheduling after a full pass.

## State And Persistence
The fixed flow table is allocated at init. PIE variables are per flow and reset with the qdisc. Runtime counters include memory usage, overmemory, packets in, drops, ECN marks, and new flow count. Configuration persists in memory via `pie_params`, `sch->limit`, `flows_cnt`, `quantum`, `memory_limit`, and `ecn_prob`, and is emitted by netlink dump.

## Dependencies And Integration Points
FQ-PIE depends on `net/pie.h`, classifier blocks, netlink validation, qdisc timers, qdisc root locking, `kvzalloc_objs()`, and generic queue/stat helpers. Unlike FQ-CoDel, it has no class ops for per-flow tc class stats.

## Risks
`flows_cnt` cannot change after allocation. The memory-limit check compares current usage against `memory_limit + skb->truesize`, which should be tested because it is easy to misread as post-enqueue accounting. The timer’s bounded 2048-flow loop spreads CPU work but means probability updates for large flow tables occur over multiple invocations. Timer teardown must set `tupdate` to zero and delete synchronously to avoid use-after-free. Reset clears flow queues/vars but does not explicitly zero all qdisc counters.

## Test Signals
Validate flow classification, classifier action paths, packet-limit and memory-limit drops, PIE early drop versus ECN mark paths, ECN probability threshold, new/old flow service and deficit movement, timer probability update cursor wrap, flow-count immutability, limit shrink drops in change, reset/destroy timer behavior, dump round trips, and stats for packets, overlimit, overmemory, drops, ECN marks, memory usage, and flow-list lengths.
