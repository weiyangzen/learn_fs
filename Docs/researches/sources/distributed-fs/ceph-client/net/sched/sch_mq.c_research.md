# sources/distributed-fs/ceph-client/net/sched/sch_mq.c

Purpose: implements the root `mq` classful multiqueue scheduler. It is a structural qdisc that exposes one class per TX queue and attaches one child qdisc to each device queue, while aggregating stats at the root.

Important APIs, types, and functions: the file uses `struct mq_sched` from scheduler internals. `mq_init_common`, `mq_destroy_common`, `mq_attach`, `mq_dump_common`, `mq_select_queue`, `mq_leaf`, `mq_find`, `mq_dump_class`, `mq_dump_class_stats`, and `mq_walk` are exported in the `NET_SCHED_INTERNAL` namespace and reused by related schedulers. `mq_offload`, `mq_offload_stats`, `mq_graft`, and `mq_dump` implement mq-specific offload and class operations. `mq_qdisc_ops` registers id `mq`.

Control flow: init requires `TC_H_ROOT` and a multiqueue device, preallocates an array sized by `dev->num_tx_queues`, and creates default child qdiscs with minor handles `1..num_tx_queues`. Attach grafts those children onto the corresponding netdev queues, hashes real TX queues, then frees the temporary array. Graft deactivates the device if needed, replaces a queue's sleeping qdisc, marks the new qdisc as one-TX-queue/no-parent, reactivates the device, and notifies hardware offload.

State and persistence behavior: before attach, child qdisc references live in `priv->qdiscs`; after attach the array is freed and the durable runtime state is in `netdev_queue->qdisc_sleeping`. Root qstats are reconstructed on dump by locking each child and summing per-CPU/basic/queue stats. Configuration is device-derived; there is no persistent storage or tunable netlink payload.

Dependencies and integration points: depends on multiqueue netdev APIs, `dev_graft_qdisc`, default qdisc selection, qdisc hash management, `qdisc_offload_dump_helper`, and `ndo_setup_tc(TC_SETUP_QDISC_MQ)`. It is also a library provider for shared mq root behavior.

Risks: init can return after partial child allocation and relies on destroy cleanup for allocated qdiscs. `mq_queue_get` must reject out-of-range class IDs or graft/leaf paths would dereference invalid queues. Stats aggregation must handle both lockless and locked child qdisc accounting. Offload support must tolerate `-EOPNOTSUPP`.

Test signals: create on non-root or single-queue devices should fail; multiqueue create should expose one class per TX queue. Test graft while device is up, stats aggregation across child qdiscs, class walking skip/stop behavior, offload create/destroy/graft/stats callbacks, and real TX queue count changes through `mq_change_real_num_tx`.
