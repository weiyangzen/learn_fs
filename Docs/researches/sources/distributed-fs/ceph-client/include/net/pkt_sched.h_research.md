# sources/distributed-fs/ceph-client/include/net/pkt_sched.h

Purpose: declares packet scheduler core helpers, time conversion, qdisc watchdogs, qdisc registration/lookup, default FIFO helpers, and qdisc offload structures for CBS, ETF, mqprio, taprio, and related stats.

Important APIs and types: `qdisc_walker`, `qdisc_priv()`, `psched_time_t` conversion macros, `struct qdisc_watchdog`, FIFO qdisc ops, qdisc registration/default/hash APIs, rate/stab helpers, and `qdisc_run()`. Offload descriptors include `tc_query_caps_base`, CBS/ETF/mqprio/taprio caps and options, taprio schedule entries/stats, and helper functions for taprio refcounting. Other helpers compute MTU, qdisc netns, consume txtime, dump stats, warn non-work-conserving qdiscs, peek length, and init/uninit qdisc locks.

Control flow: qdiscs register ops, enqueue/dequeue under scheduler core, watchdogs schedule future dequeue, qdisc lookup maps handles, and offload structs carry netlink-derived configuration to drivers.

State and persistence: qdisc objects, timers, lock classes, hash membership, rate tables, and driver offload state are runtime-only.

Dependencies and integration points: depends on qdisc core, hrtimers, netdevices, rtnetlink policies, lockdep, VLAN, pkt_sched UAPI, and TC setup callbacks.

Risks and test signals: risks include time unit conversion errors, watchdog cancellation races, lock class leaks, non-work-conserving peek behavior, and flexible taprio offload lifetime. Test qdisc register/unregister, FIFO defaults, watchdog schedule/cancel, qdisc lookup/hash, taprio refcount, txtime timestamp clearing, stats walkers, and lockdep for nested qdiscs.
