# sources/distributed-fs/ceph-client/net/netfilter/nf_conncount.c

## Purpose
`nf_conncount.c` maintains per-key counts of active conntrack entries, backing connlimit-style rules and nftables expressions that count connections matching an arbitrary key such as source address or subnet.

## Important APIs, Types, And Functions
`struct nf_conncount_tuple` stores a tracked tuple, zone, insertion CPU, and jiffies stamp. `struct nf_conncount_rb` stores one counted key, an `nf_conncount_list`, and an RCU rb node. `struct nf_conncount_data` owns 256 rb-tree buckets, a GC work item, pending tree bitmap, net pointer, and key length.

Exported APIs are `nf_conncount_init()`, `nf_conncount_destroy()`, `nf_conncount_count_skb()`, `nf_conncount_add_skb()`, `nf_conncount_gc_list()`, `nf_conncount_list_init()`, and `nf_conncount_cache_free()`. Internal flow is split between tuple extraction, list add/GC, tree insertion/counting, and background cleanup.

## Control Flow
For an skb-backed count, the code extracts an existing conntrack or derives a tuple, then hashes the key into one of 256 rb trees. Existing keys update their list under `list_lock`; missing keys allocate an rb node plus first tuple and insert under the bucket lock. Lists are periodically scanned to remove tuples whose conntrack can no longer be found or whose TCP state is TIME_WAIT/CLOSE. Empty rb nodes are removed with RCU freeing. Calls without an skb count an existing key after a GC pass.

## State And Persistence
State is in-memory per `nf_conncount_data` instance and persists for the lifetime of the rule/expression using it. Two slab caches store rb nodes and tuple nodes. Stale entries are tolerated briefly to avoid racing unconfirmed conntracks that are about to be inserted.

## Dependencies And Integration Points
The module depends on conntrack tuple parsing/lookup, zones, TCP state, rbtree/list APIs, RCU, spinlocks, workqueues, jhash, and per-net namespace conntrack state. It exports services to rule modules rather than registering packet hooks itself.

## Risks
Concurrency risk is high: lookups are RCU-visible while bucket/list mutation uses spinlocks. Stale tuple eviction intentionally waits for two jiffies or same-CPU provenance to avoid dropping entries before confirmation. Allocation failures can return zero counts for hotdrop-like behavior. Tree GC must preserve the two-phase remove-under-lock model.

## Test Signals
Exercise duplicate SYN trains, loopback confirmed-before-rule cases, TCP close/TIME_WAIT cleanup, UDP/non-TCP retention, zone-aware counting, concurrent inserts for the same key, rb-node removal under RCU, allocation failure behavior, destroy while GC work is pending, and key length validation.
