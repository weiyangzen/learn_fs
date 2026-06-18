<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netport.c -->
# sources/distributed-fs/ceph-client/security/selinux/netport.c

## Purpose
Caches SELinux SIDs for network ports by protocol and port number. This reduces policy lookup overhead for socket and packet checks involving labeled ports.

## Important APIs, Types, and Functions
Public functions are `sel_netport_sid()`, `sel_netport_flush()`, and `sel_netport_init()`. Helpers include `sel_netport_hashfn()`, `sel_netport_find()`, `sel_netport_insert()`, and `sel_netport_sid_slow()`. `struct sel_netport` stores `netport_security_struct`, list linkage, and RCU callback state.

## Control Flow
The fast path performs an RCU hash lookup by port bucket and protocol. Misses lock the table, recheck, call `security_port_sid(protocol, pnum, sid)`, allocate a cache node, and insert it. Buckets are capped at 16 entries; inserting at a full bucket removes the tail.

## State and Persistence
The cache is a 256-bucket global hash table protected by `sel_netport_lock` for writes and RCU for reads. Entries persist until explicit flush, bucket eviction, or policy reload paths that call the flush function.

## Dependencies and Integration Points
Depends on SELinux policy portcon lookup, object security structures, RCU, spinlocks, and network/socket hooks. It shares the cache design used by `netnode.c`.

## Risks
Heavy use of many ports sharing low bits can cause eviction churn. Protocol is part of equality but not the hash, so TCP/UDP/SCTP collisions for the same low port bits share buckets. Allocation failure makes lookup correct but uncached. Unsupported protocol validation is deferred to `security_port_sid()`.

## Test Signals
Verify TCP/UDP/SCTP policy mappings, cache hits after first lookup, eviction at bucket limit, flush on policy reload, failed policy lookup warnings, and concurrent lookup/flush safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/netport.c -->
