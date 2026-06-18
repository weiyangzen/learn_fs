# sources/distributed-fs/ceph-client/net/sched/sch_drr.c

## Purpose
`sch_drr.c` implements a classful Deficit Round Robin scheduler. Each class owns a child qdisc and a quantum; active classes are served round-robin using per-class deficits so variable-sized packets receive approximately fair service.

## Important APIs, Types, and Functions
`struct drr_class` stores class common metadata, byte/queue stats, optional rate estimator, active-list node, child qdisc, quantum, and deficit. `struct drr_sched` stores the active class list, classifier block/list, and class hash table.

Class management functions are `drr_change_class()`, `drr_delete_class()`, `drr_search_class()`, `drr_graft_class()`, `drr_class_leaf()`, `drr_qlen_notify()`, `drr_dump_class()`, `drr_dump_class_stats()`, and `drr_walk()`. Filter integration is through `drr_tcf_block()`, `drr_bind_tcf()`, and `drr_unbind_tcf()`. Datapath callbacks are `drr_enqueue()` and `drr_dequeue()`, with lifecycle handled by `drr_init_qdisc()`, `drr_reset_qdisc()`, and `drr_destroy_qdisc()`.

## Control Flow
Qdisc initialization obtains a tc filter block, initializes the class hash, and initializes the active list. Creating a class requires options, parses optional `TCA_DRR_QUANTUM`, defaults quantum to device MTU, allocates a class, creates a default `pfifo` child (or uses `noop_qdisc`), optionally installs a rate estimator, inserts the class into the hash under the tree lock, and grows the hash if needed. Updating an existing class can replace the estimator and quantum.

On enqueue, classification first honors `skb->priority` when its major matches the qdisc handle, then runs tc filters. Classifier actions can consume/drop packets before class selection. A selected class receives the packet through its child qdisc. If enqueue succeeds and the class was inactive, it is appended to the active list and its deficit is reset to its quantum. Parent qlen/backlog are incremented.

On dequeue, the scheduler repeatedly inspects the first active class and peeks at its child. If the head packet length is within the class deficit, the packet is dequeued, deficit is reduced, an empty class is removed from active list, class and parent stats are updated, and the skb is returned. If the packet is too large, the class gains another quantum and moves to the active-list tail. `drr_qlen_notify()` removes a class from the active list when a child reports it became empty.

## State and Persistence
All state is in memory. Class definitions, child qdiscs, deficits, active-list membership, stats, and rate estimators persist only for the qdisc lifetime. Class hash membership tracks configured classes; active list membership tracks classes with non-empty child queues. There is no disk persistence.

## Dependencies and Integration Points
DRR depends on class hash helpers from `sch_api.c`, tc classifier blocks, gnet stats/rate estimators, default `pfifo` child qdiscs, qdisc grafting, and netlink `TCA_DRR_QUANTUM`. It registers class operations so generic tc class commands can create/delete/graft/dump classes and bind filters.

## Risks
Fairness depends on child `peek()` being reliable; a non-work-conserving child returning `NULL` while queued triggers `qdisc_warn_nonwc()` and can stall dequeue. Active-list state must stay synchronized with child qlen on enqueue, dequeue, reset, delete, and qlen notifications. Deleting a class with bound filters or references is blocked by `qdisc_class_in_use()`, but missing bind/unbind would risk use-after-free. Quantum zero is rejected; very small quantums can cause many list rotations before large packets are sent.

## Test Signals
Test class create/change/delete, zero quantum rejection, default MTU quantum, filter classification by classid and direct class pointer, `skb->priority` classification, classifier shot/stolen actions, child graft replacement, active-list rotation fairness with different packet sizes, class deletion while in use, reset clearing active list and child queues, and stats showing deficit only for non-empty classes.
