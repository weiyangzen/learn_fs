# sources/distributed-fs/ceph-client/include/net/sch_priv.h

## Purpose
This private scheduler header declares common helpers for multiqueue qdiscs. It is shared by mq-like scheduler implementations that manage one leaf qdisc per hardware transmit queue.

## Important APIs, Types, And Functions
`struct mq_sched` stores the leaf qdisc array. `mq_init_common()` initializes a multiqueue root with child qdiscs, while `mq_destroy_common()`, `mq_attach()`, and `mq_dump_common()` handle teardown, device attachment, and netlink dump state. Class operations include `mq_select_queue()`, `mq_leaf()`, `mq_find()`, `mq_dump_class()`, `mq_dump_class_stats()`, and `mq_walk()`.

## Control Flow
The root mq qdisc delegates class-like operations to hardware queue leaves. During init, child qdiscs are allocated using the supplied `Qdisc_ops`; attach installs them on netdev queues. Dump and walk callbacks expose each queue as a class to tc.

## State And Persistence
Persistent state is only the `qdiscs` pointer array in qdisc private data. Each child qdisc owns its normal queue and stats lifecycle.

## Dependencies And Integration Points
It depends on `sch_generic.h` and integrates with `mq_qdisc_ops`, `mqprio` style class traversal, netdev queue selection, and tc dump/stat APIs.

## Risks And Test Signals
Risks include mismatched real transmit queue counts, child qdisc leaks, invalid class IDs, and stale queue mappings after device reconfiguration. Test signals are multiqueue device activation, `real_num_tx_queues` changes, tc class dump/walk, and qdisc replacement on individual queues.
