<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h -->
# sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h

## Purpose
`nf_conntrack_count.h` declares helpers for counting concurrent conntracks per arbitrary key, used by match modules such as connlimit.

## Important APIs, types, and functions
It defines `struct nf_conncount_list`, opaque `struct nf_conncount_data`, and APIs to init/destroy data, count/add skb-derived connections, initialize/gc/free lists.

## Control flow
Consumers hash policy keys to lists. Packet evaluation counts existing live conntracks matching a key, optionally adds the skb's conntrack, and periodically garbage-collects dead entries from the list.

## State and persistence
Runtime state includes per-key lists with spinlock, last GC jiffies, current count, and last GC count plus global data hidden in implementation.

## Dependencies and integration points
It depends on conntrack tuples, zones, net namespace, skb, list, and spinlocks. It integrates conntrack with rule-level connection count limits.

## Risks and test signals
Risks include stale entries if GC misses dying conntracks, list lock contention, zone mismatch, key length errors, and count/add races. Tests should cover concurrent new connections, GC, zones, IPv4/IPv6 tuples, and destroy under active lists.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h` completely for this pass (38 lines, 1179 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netfilter/nf_conntrack_count.h -->
