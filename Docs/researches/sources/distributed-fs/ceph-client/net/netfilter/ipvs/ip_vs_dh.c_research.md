# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_dh.c

## Purpose
`ip_vs_dh.c` implements the IPVS destination-hashing scheduler named `dh`. It maps each packet's destination IP address to one of a fixed number of scheduler buckets, where each bucket points at a real server destination. This is intended for cache-cluster style deployments where a given origin destination should consistently select the same cache server, often paired with IPVS cache-bypass when the chosen cache is unavailable.

## Important APIs, types, and functions
The local state types are `struct ip_vs_dh_bucket`, holding an RCU-protected `struct ip_vs_dest *`, and `struct ip_vs_dh_state`, holding the fixed bucket array plus an RCU head. Important functions are `ip_vs_dh_hashkey()`, `ip_vs_dh_get()`, `ip_vs_dh_reassign()`, `ip_vs_dh_flush()`, `ip_vs_dh_init_svc()`, `ip_vs_dh_done_svc()`, `ip_vs_dh_dest_changed()`, `is_overloaded()`, and `ip_vs_dh_schedule()`. The module registers `ip_vs_dh_scheduler` with scheduler callbacks for service init/done, destination add/delete, and scheduling.

## Control flow
When a service binds the scheduler, `ip_vs_dh_init_svc()` allocates scheduler state and calls `ip_vs_dh_reassign()` to fill the bucket array from the service's current destination list. Reassignment walks all buckets, drops any previous destination reference, and assigns destinations round-robin across buckets, taking a destination reference for every assigned bucket. Destination additions and deletions simply rebuild the whole fixed table. During scheduling, `ip_vs_dh_schedule()` hashes `iph->daddr`, fetches the bucket destination under RCU, rejects missing, unavailable, zero/negative-weight, or overloaded destinations, and returns the selected destination.

## State and persistence behavior
Scheduler state is per service in `svc->sched_data`. Every bucket holds a destination reference while assigned, so destinations are kept alive until bucket reassignment or scheduler teardown releases them. The table size defaults to 256 buckets unless `CONFIG_IP_VS_DH_TAB_BITS` changes it. The mapping is deterministic for a given destination-list ordering and destination address but is rebuilt wholesale when the destination set changes.

## Dependencies and integration points
The scheduler integrates with the common IPVS scheduler registry via `register_ip_vs_scheduler()` and `unregister_ip_vs_scheduler()`, service destination lists maintained by `ip_vs_ctl.c`, RCU destination access, destination refcount helpers, packet header data from `struct ip_vs_iphdr`, and generic scheduler error/debug helpers. IPv6 hashing folds the IPv6 address words before applying `hash_32()`.

## Risks and edge cases
The algorithm does not search for an alternate destination if the hashed bucket points to an unavailable, overloaded, or zero-weight real server; it returns NULL and relies on higher-level no-destination behavior such as cache bypass. Reassigning all buckets on every destination change is simple but can be disruptive and takes/release many references. Weighted behavior is not proportional: weights are only an eligibility check. IPv6 address folding can collide more aggressively than a full hash over all address bytes. Service list ordering affects the bucket map.

## Test signals
Test with stable source service/destination ordering to confirm repeatable destination-IP mapping, destination add/delete causing bucket reassignment, zero-weight and overloaded destinations returning no destination, IPv4 and IPv6 hash behavior, empty service tables, scheduler module load/unload with RCU grace, and cache-bypass behavior in the packet core when `dh` returns NULL for an unavailable cache.
