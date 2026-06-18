# sources/distributed-fs/ceph-client/net/sched/sch_gred.c

## Purpose
`sch_gred.c` implements the Generic Random Early Detection qdisc. It multiplexes packets into virtual queues selected by `skb->tc_index`, each with RED parameters, and supports RIO and WRED modes plus optional hardware offload.

## Important APIs, Types, And Functions
`struct gred_sched` stores the virtual queue table, global flags, default DP, global RED flags, shared WRED variables, and offload scratch. `struct gred_sched_data` stores per-VQ limit, DP, RED flags, byte/packet counters, backlog, priority, RED params/vars/stats. Packet functions are `gred_enqueue()`, `gred_dequeue()`, and `gred_reset()`. Configuration functions include `gred_change_table_def()`, `gred_change_vq()`, `gred_change()`, VQ-list validation/apply helpers, `gred_init()`, `gred_dump()`, and `gred_destroy()`.

## Control Flow
Initialization accepts only table-level options, sets qdisc limit, allocates offload scratch if possible, then configures DP count/default and mode. VQ configuration validates RED parameters and either creates or updates one `gred_sched_data`. Enqueue chooses DP from low bits of `skb->tc_index`, falls back to default DP, or passes through unconfigured traffic if no default VQ exists and the qdisc limit permits. It computes RED average using either per-VQ backlog or shared WRED backlog, includes lower-priority qavg in RIO mode, then applies RED action: no mark, probabilistic ECN/drop, or forced ECN/drop. Accepted packets are queued in the parent FIFO queue and per-VQ backlog is updated. Dequeue removes from the shared FIFO and adjusts the selected VQ backlog/idle state.

## State And Persistence
State is volatile per-qdisc VQ state plus shared WRED RED vars. Netlink dump emits table-level options, legacy all-in-one VQ parameter records, structured VQ list entries, RED flags, and counters. Hardware stats dump may add driver-provided bstats/qstats/xstats into software state under the tree lock.

## Dependencies And Integration Points
GRED depends on `net/red.h`, netlink nested attributes, tc index classification, generic qdisc FIFO storage, ECN helpers, optional `ndo_setup_tc(TC_SETUP_QDISC_GRED)`, and qdisc offload stats helpers. It uses qdisc-level `sch->limit` as the hard global queue length/default pass-through bound.

## Risks
Misconfigured or absent default VQs can intentionally pass traffic through, which differs from strict classifier failure dropping. WRED mode shares qavg/idle state across VQs with equal priorities, while RIO adds lower-priority qavgs; mode transitions must keep flags coherent. Per-qdisc RED flags and per-VQ flags are mutually constrained. Offload stats are additive even if driver stat dump returns failure, which can surprise tests. Backlog correction depends on `tc_index` surviving requeue/dequeue.

## Test Signals
Cover table validation for zero/too many DPs and invalid default DP, VQ RED parameter validation, per-qdisc versus per-VQ RED flag conflicts, unconfigured DP fallback/pass-through, RIO/WRED mode selection, probabilistic and forced ECN/drop paths, per-VQ limit drops, dequeue backlog/idle updates, shrinking DPs destroying shadowed VQs, legacy and structured dump content, offload replace/destroy/stats commands, and hardware stat merge behavior.
