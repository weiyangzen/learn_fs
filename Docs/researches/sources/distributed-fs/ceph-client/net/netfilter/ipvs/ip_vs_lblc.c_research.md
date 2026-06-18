# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblc.c

## Purpose
Implements the IPVS `lblc` scheduler, locality-based least connection. It caches each requested destination address to one real server so repeated requests for the same destination keep locality, while falling back to weighted least-connection selection when the cached server is unavailable or overloaded.

## Important APIs, Types, and Functions
The module registers `ip_vs_lblc_scheduler` through `register_ip_vs_scheduler()` and also registers per-netns sysctl state when `CONFIG_SYSCTL` is enabled. `struct ip_vs_lblc_entry` stores destination-address to `ip_vs_dest` mappings with an RCU callback. `struct ip_vs_lblc_table` is per-service scheduler state with hash buckets, a GC timer, entry counters, and a dead flag. `ip_vs_lblc_schedule()` is the scheduler entry point, `__ip_vs_lblc_schedule()` does weighted least-connection fallback, `ip_vs_lblc_new()` creates or replaces a cache entry, and `ip_vs_lblc_check_expire()` plus `ip_vs_lblc_full_check()` expire stale cache entries.

## Control Flow
Service bind calls `ip_vs_lblc_init_svc()`, allocating the hash table, initializing buckets, and arming a periodic timer. Scheduling first looks up `iph->daddr` in the cache. A cached destination is reused only when it is marked available, has positive weight, and `is_overloaded()` does not find a much less loaded peer. Otherwise the code scans the service destination list for the minimum `ip_vs_dest_conn_overhead(dest) / weight` using cross multiplication, then updates the destination-address cache under `svc->sched_lock`. The timer periodically does a full expiration every `COUNT_FOR_FULL_EXPIRATION` ticks or partial GC when entries exceed `max_size`.

## State and Persistence
State is in `svc->sched_data`, not persisted beyond service lifetime. Cache entries hold references to real servers through `ip_vs_dest_hold()` and release them in RCU callbacks via `ip_vs_dest_put_and_free()`. Per-netns `sysctl_lblc_expiration` defaults to 24 hours and controls full-expiry age; table pressure uses a shorter `ENTRY_TIMEOUT`. `timer_shutdown_sync()` and `ip_vs_lblc_flush()` clear service state on scheduler unbind.

## Dependencies and Integration Points
Depends on IPVS service/destination data structures, RCU hlist traversal, service scheduler locks, jiffies timers, hash helpers, netns sysctl registration, and the scheduler registry in `ip_vs_sched.c`. It integrates with destination availability and weight updates through the shared destination list and with user tuning through `/proc/sys/net/ipv4/vs/lblc_expiration`.

## Risks
Correctness depends on RCU lifetime of cached destinations and on decrementing `entries` for every deletion path. The cache can keep traffic pinned to a weak server until overload criteria trigger. Expiration and scheduling both touch hash buckets, so lock coverage around deletion and `dead` handling is important. IPv6 hashing folds all address words into one value, so collisions are expected and must remain harmless. Sysctls are hidden for unprivileged net namespaces by passing zero table size.

## Test Signals
Useful tests create an `lblc` service, repeatedly hit the same destination IP, and verify stable real-server selection until weight, overload, or availability changes. Exercise zero-weight quiescing, table expiry through `lblc_expiration`, service teardown under active cache entries, IPv4 and IPv6 destination keys, and logs from `ip_vs_scheduler_err()` when no destination is available.
