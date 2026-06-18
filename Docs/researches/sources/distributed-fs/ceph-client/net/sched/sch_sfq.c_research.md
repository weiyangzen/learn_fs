# sources/distributed-fs/ceph-client/net/sched/sch_sfq.c

Purpose: implements the Linux `sfq` qdisc, using stochastic flow hashing plus deficit round-robin service to provide cheap best-effort fairness. It optionally applies RED/ECN decisions per hashed flow and periodically perturbs the hash key to reduce long-lived collision bias.

Important APIs/types/functions: `struct sfq_sched_data` owns limits, hash divisor, perturbation key, tc filter block, `ht[]`, `slots[]`, RED state, depth lists, active ring tail, quantum, and timer. `struct sfq_slot` represents one hashed flow queue with skb intrusive list, queue length, depth-list node, hash index, deficit allotment, backlog, and RED vars. `sfq_classify()` maps packets by classid, tc filters, or perturbed skb hash. `sfq_enqueue()` classifies, allocates slots, applies RED/ECN, enforces per-flow/global limits, and drops from the longest slot. `sfq_dequeue()` serves the active ring with quantum refill. `sfq_rehash()` drains and rebuilds slots on perturbation. Lifecycle/dump/class access is through `sfq_init()`, `sfq_destroy()`, `sfq_dump()`, and `sfq_class_ops`.

Control flow: init seeds default depth/divisor/flows/quantum and the perturbation key, sets up the classifier block and timer, optionally parses options, then allocates the hash and slot arrays. Enqueue turns a packet into a bucket, creates a flow slot from `dep[0]` if needed, queues it, and inserts new flows into the round-robin ring. Dequeue rotates past exhausted slots, refills allotment, removes one skb, and removes empty flows from the hash table. Timer perturbation changes the SipHash key under qdisc locking and rehashes queued packets when no filters are installed.

State and persistence: all state is volatile qdisc memory. Slot membership is maintained in both depth lists and the active ring, so `sfq_inc()`/`sfq_dec()` are central invariants. RED averages and perturbation key live only for the qdisc lifetime. Destroy releases the classifier block, timer, hash/slot arrays, and RED parameters.

Dependencies/integration: qdisc core, class ops, tc filters, RED helpers, skb hashing, qdisc stats/backlog helpers, netlink scheduler ABI, timers, and module alias `NET_SCH("sfq")`.

Risks: hash collisions intentionally merge flows; perturbation rehash can drop if the rebuilt layout exceeds limits; RED/headdrop accounting depends on exact packet-length deltas; `sfq_qdisc_ops.change` is `NULL` despite an implemented `sfq_change()`, so runtime reconfiguration may be unavailable in this snapshot.

Test signals: tc add/dump with default and RED options, filter-directed class ids, perturbation with queued traffic, per-flow depth/global limit pressure, headdrop versus taildrop, ECN mark counters, class stats, and qlen/backlog/tree reduction after all drop paths.
