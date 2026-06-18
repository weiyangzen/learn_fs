# sources/distributed-fs/ceph-client/net/sched/sch_fq_codel.c

## Purpose
`sch_fq_codel.c` implements Fair Queue CoDel: a stochastic fixed-flow-table fair queue whose per-flow queues are managed by CoDel active queue management. It prioritizes newly active flows over old flows and bounds both packet count and memory usage.

## Important APIs, Types, And Functions
`struct fq_codel_sched_data` owns classifier state, fixed flow array, per-flow backlog array, quantum, packet/memory/drop limits, CoDel params/stats, memory counters, and new/old flow lists. `struct fq_codel_flow` stores an skb FIFO, DRR deficit, list node, and CoDel variables. Main functions are `fq_codel_classify()`, `fq_codel_enqueue()`, `fq_codel_drop()`, `fq_codel_dequeue()`, `dequeue_func()`, `drop_func()`, `fq_codel_change()`, `fq_codel_init()`, and class stat dump/walk functions.

## Control Flow
Classification accepts explicit classids under the qdisc handle, otherwise uses an external filter if present, then falls back to `skb_get_hash()` scaled to `flows_cnt`. Enqueue records CoDel enqueue time, appends to the selected flow, activates new flows with initial deficit, updates per-flow backlog and memory usage, then checks `sch->limit` and `memory_limit`. If over limit, `fq_codel_drop()` linearly finds the fattest flow and drops up to `drop_batch_size` packets or half that flow’s backlog. Dequeue selects `new_flows` before `old_flows`, replenishes deficit by quantum, calls `codel_dequeue()` with qdisc-specific callbacks, moves empty flows off the list, and propagates CoDel drop accounting to parents.

## State And Persistence
The flow table and backlog array are allocated once during init; flow count cannot change after allocation. Runtime state includes per-flow skb lists, CoDel variables, memory usage, drop counters, and new/old flow chains. Netlink dump exposes CoDel target/interval/ECN/CE threshold, qdisc limit, flows, quantum, batch size, and memory limit. Per-class stats expose individual flow backlog, CoDel delay/drop state, and deficit.

## Dependencies And Integration Points
The qdisc depends on `net/codel*.h`, classifier blocks, generic qdisc class ops, netlink policy parsing, `kvzalloc_objs()`, and generic queue/stat helpers. It exposes a class-like view over hash slots for `tc` stats and filters but has no child qdiscs.

## Risks
Hash collisions combine unrelated flows. `fq_codel_drop()` is intentionally linear over all flows; large `flows_cnt` raises CPU cost in overload. Flow count is immutable after allocation and change rejects late flow-count changes. Memory accounting uses `skb->truesize` saved in CoDel skb CB, so all dequeue/drop paths must subtract it exactly. Classifier actions that steal/drop packets must keep qdisc drop stats consistent.

## Test Signals
Test hash and explicit classid classification, external filter steal/shot paths, new-flow priority over old flows, deficit rollover, CoDel ECN/drop behavior, memory-limit drops, packet-limit drops, fattest-flow batch drop selection, limit shrink by `fq_codel_change()`, immutable flow count, class walk/stat dumps, reset clearing all flows and memory, and destroy freeing arrays and classifier block.
