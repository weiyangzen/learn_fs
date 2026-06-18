<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netnode.c -->
# sources/distributed-fs/ceph-client/security/selinux/netnode.c

## Purpose
Caches SELinux node SIDs for IPv4 and IPv6 addresses to avoid repeated policy lookups on packet paths. The cache maps address family plus address to a SID with bounded per-bucket growth.

## Important APIs, Types, and Functions
Public APIs are `sel_netnode_sid()`, `sel_netnode_flush()`, and `sel_netnode_init()`. Helpers include `sel_netnode_hashfn_ipv4()`, `sel_netnode_hashfn_ipv6()`, `sel_netnode_find()`, `sel_netnode_insert()`, and `sel_netnode_sid_slow()`. `struct sel_netnode_bkt` tracks bucket size, and `struct sel_netnode` wraps `netnode_security_struct`.

## Control Flow
Fast path looks up the address under RCU. On miss, `sel_netnode_sid_slow()` locks the hash, rechecks, allocates a node, calls `security_node_sid()` with correct address length, and inserts the result. Insert adds new entries at the head and evicts the RCU-protected tail when the bucket reaches `SEL_NETNODE_HASH_BKT_LIMIT`.

## State and Persistence
Persistent state is a 256-bucket global hash table, bucket sizes, and nodes freed by RCU. Entries survive until eviction or explicit flush, typically after policy changes. There is no namespace key; address labels are policy-global.

## Dependencies and Integration Points
Depends on IPv4/IPv6 address structures, SELinux `security_node_sid()`, object security structures, spinlocks, RCU, and packet hooks needing node labels.

## Risks
Hashing only low address bits is fast but can concentrate some address patterns. Bucket eviction is approximate LRU by insertion order and may churn under scans. Unsupported address families call `BUG()`, so callers must validate family. Memory allocation failure avoids caching but still returns the policy result if lookup succeeds.

## Test Signals
Test IPv4 and IPv6 labels, repeated hit/miss behavior, bucket-limit eviction, flush after policy reload, unsupported-family guard behavior in debug tests, and concurrent readers during flush/eviction under RCU diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netnode.c -->
