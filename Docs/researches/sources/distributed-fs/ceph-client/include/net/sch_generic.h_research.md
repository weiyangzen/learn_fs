# sources/distributed-fs/ceph-client/include/net/sch_generic.h

## Purpose
This is the central traffic-control scheduler header. It defines qdisc objects, qdisc/class/filter operations, classifier chains and blocks, queue/stat helper functions, packet drop handling, rate conversion helpers, mini-qdisc fast-path structures, and scheduler lifecycle APIs.

## Important APIs, Types, And Functions
Core state types include `struct Qdisc`, `struct Qdisc_ops`, `struct Qdisc_class_ops`, `struct tcf_proto_ops`, `struct tcf_proto`, `struct tcf_chain`, `struct tcf_block`, `struct qdisc_skb_head`, `struct qdisc_rate_table`, `struct qdisc_size_table`, `struct psched_ratecfg`, `struct psched_pktrate`, `struct mini_Qdisc`, and `struct mini_Qdisc_pair`. Inline APIs manage qdisc references, run serialization (`qdisc_run_begin/end()`), root lookup, tree locks, qlen/backlog accounting, enqueue/dequeue/drop, class hashes, and rate-to-time conversion. External lifecycle functions include `dev_init_scheduler()`, `dev_activate()`, `dev_deactivate()`, `qdisc_alloc()`, `qdisc_create_dflt()`, `qdisc_destroy()`, `qdisc_put()`, and offload helpers.

## Control Flow
Transmit scheduling enters qdisc enqueue callbacks, updates per-qdisc or per-cpu stats, and serializes dequeue through either root-lock `running` state or `TCQ_F_NOLOCK` `seqlock`/state bits. Missed work sets `__QDISC_STATE_MISSED` and reschedules at `qdisc_run_end()`. Classifier paths traverse `tcf_block` to chains and `tcf_proto` instances under RCU and explicit locks, while `mini_Qdisc` provides a reduced ingress/clsact fast path.

## State And Persistence
Qdisc state persists on `netdev_queue` objects and includes packet lists, GSO/deferred queues, refcounts, rate estimators, stats, RCU lifetime, lock classes, and private data. Class/filter state persists in chain lists, xarray ports, shared block indices, and offload counters. Packet metadata is carried in `skb->cb` through `qdisc_skb_cb`/`tc_skb_cb`.

## Dependencies And Integration Points
The file ties together `netdevice`, rtnetlink, generic stats, flow offload, packet scheduler/classifier UAPI, dynamic queue limits, RCU, per-cpu stats, and drop-reason reporting. Hardware offload paths integrate with `tc_setup_type` callbacks and block callback lists.

## Risks And Test Signals
High-risk areas are lock ordering between RTNL, qdisc root locks, seqlock no-lock qdiscs, RCU chain updates, deferred skb freeing, per-cpu stat aggregation, and `skb->cb` size pressure. Test signals include qdisc attach/detach, classful qdisc grafts, clsact ingress/egress, no-lock qdisc stress, offload add/remove, drop-reason accounting, and netdev queue count changes.
