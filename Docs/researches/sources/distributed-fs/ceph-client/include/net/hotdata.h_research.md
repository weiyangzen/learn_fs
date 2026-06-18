# sources/distributed-fs/ceph-client/include/net/hotdata.h

Purpose: groups read-mostly networking fast-path globals into `struct net_hotdata` to improve cache locality. It includes protocol/offload registrations, skb caches, RPS state, deferred skb queues, and common sysctl-derived budget/limit values.

Important APIs/types: `struct skb_defer_node` stores a lockless deferred skb list and count, cacheline-aligned per CPU. `struct net_hotdata` contains IPv4/IPv6 packet offloads and protocol descriptors when INET is enabled, global offload list, skb slab caches, RPS tables/mask, per-CPU defer nodes, GRO normal batch, netdev budgets, backlog, qdisc burst/weights, max skb fragments, defer max, and per-CPU memory reserve. Macros expose hash secrets through protocol/offload fields.

Control flow and state: this header declares the global `net_hotdata`; runtime initialization populates protocol tables, caches, budgets, and sysctl values. Fast paths read these fields frequently, often through `READ_ONCE()`.

Dependencies and integration: depends on linked lists, netdevice, protocol/offload definitions, and optional RPS types. It integrates with GRO batching, protocol lookup, hash functions, skb allocation, and network sysctls.

Risks: because fields are global fast-path state, false sharing and unsynchronized mutation can hurt performance or correctness. Tests should exercise sysctl updates, GRO batch thresholds, protocol registration, RPS enabled/disabled builds, hash secret initialization, and deferred skb pressure.
