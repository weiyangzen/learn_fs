# sources/distributed-fs/ceph-client/include/net/inetpeer.h

Purpose: declares the inet peer cache, a per-destination store for long-lived peer metadata such as route metrics, ICMP rate limiting, redirects, and fragment receive ids.

Important APIs/types: `struct inetpeer_addr` stores IPv4 or IPv6 keys with family. `struct inet_peer` is an rb-tree node containing destination address, metrics, rate tokens, redirect count, last rate time, either atomic fragment id or RCU hook, deletion time, and refcount. `struct inet_peer_base` owns the rb-tree, seqlock, and total count. Helpers set/get IPv4/IPv6 keys, compare peer addresses, get peers by generic/v4/v6 key, put peers, test ICMP rate limit allowance, and invalidate a tree.

Control flow and state: callers look up or create peers in a base, mutate metrics/rate state while referenced, then put. Unreferenced peers can be queued for RCU deletion, at which point the `rid` storage is unavailable. State persists in memory across packets for a destination.

Dependencies and integration: depends on IPv6, jiffies, spinlocks/seqlocks, rtnetlink, atomics, and route metrics. It integrates with IPv4/IPv6 routing, ICMP rate limiting, redirects, and fragmentation id generation.

Risks: rb-tree ordering, refcount/RCU reuse of storage, and seqlock updates are delicate. Tests should cover v4/v6 key comparisons, peer get/put races, metrics initialization, ICMP rate token behavior, tree invalidation, and fragment id access before deletion.
