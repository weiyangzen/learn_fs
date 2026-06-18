# sources/distributed-fs/ceph-client/include/net/fq.h

Purpose: declares reusable fair-queueing data structures used by wireless and qdisc-style code that embeds fair queue logic. The design groups packet queues into traffic “tins” and per-flow queues, with DRR++ deficit accounting.

Important types: `struct fq_flow` owns a queue, backlog bytes, deficit, owner tin, and list node. `struct fq_tin` owns new/old flow lists, a default collision flow, backlog counters, collision/overlimit/flow counters, and transmit statistics. `struct fq` owns the flow array, flow bitmap, tin backlog list, spinlock, queue and memory limits, quantum, global backlog, overlimit/overmemory counters, and collision count. Callback typedefs let embedders provide dequeue, free, and filter behavior.

Control flow and state: this header only defines storage and callback contracts; `fq_impl.h` supplies inline/static implementation to includers. All mutable queue state is in memory under `fq->lock`. There is no on-disk persistence.

Dependencies and integration: depends on skb queues, spinlocks, and Linux list/bitmap conventions. It integrates with MAC/qdisc code that wants common flow hashing and deficit round-robin without a standalone object file.

Risks: callers must initialize every queue/list/counter consistently before using `fq_impl.h` helpers. Flow collisions fall back to `default_flow`, so tests need multiple tins with identical flow indexes. Test signals include limit enforcement, memory accounting, fairness between new and old flows, filter/drop callbacks, and lockdep coverage around `fq->lock`.
