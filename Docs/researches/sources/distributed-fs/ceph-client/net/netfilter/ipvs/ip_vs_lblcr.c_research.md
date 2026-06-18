# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lblcr.c

## Purpose
Implements the IPVS `lblcr` scheduler, locality-based least connection with replication. Instead of caching one real server per destination address, it caches a set of real servers, allowing a hot destination to replicate across multiple servers and later shrink the set after inactivity.

## Important APIs, Types, and Functions
The module exposes `ip_vs_lblcr_scheduler` with `init_service`, `done_service`, and `schedule` callbacks, plus per-netns `lblcr_expiration` sysctl registration. `struct ip_vs_dest_set` and `struct ip_vs_dest_set_elem` manage the replicated server set with RCU list deletion. `struct ip_vs_lblcr_entry` maps a destination address to that set, while `struct ip_vs_lblcr_table` holds hash buckets, timer state, entry counters, and service backpointer. Key helpers are `ip_vs_dest_set_min()`, `ip_vs_dest_set_max()`, `ip_vs_dest_set_insert()`, `ip_vs_dest_set_erase()`, `ip_vs_lblcr_new()`, `ip_vs_lblcr_check_expire()`, and `ip_vs_lblcr_schedule()`.

## Control Flow
Service initialization allocates a hash table and starts periodic GC. On schedule, the code looks up `iph->daddr`; if an entry exists, it selects the weighted least loaded available server inside that entry's set. If the set has more than one server and has not been modified for the configured expiration interval, it removes the most loaded member to reduce replication. If the selected member is missing or overloaded, global weighted least-connection selection picks a new server and inserts it into the set. If no entry exists, global selection creates a new entry containing the selected server.

## State and Persistence
Per-service state is the LBLCR hash table in `svc->sched_data`. Each destination-set element holds an IPVS destination reference until RCU cleanup. `lastuse` controls whole-entry expiration and `set.lastmod` controls replicated-set shrinkage. The per-netns expiration sysctl defaults to 24 hours; table pressure expiration uses six-minute idle age. State is volatile and rebuilt from traffic.

## Dependencies and Integration Points
Uses IPVS scheduler registration, destination reference management, service locks, RCU list/hlist primitives, jiffies timers, kernel sysctl registration, and address/hash helpers from `net/ip_vs.h`. It is selected by services configured with scheduler name `lblcr`, and it observes real-server state through destination flags, weights, and active/inactive connection counters.

## Risks
The scheduler mixes RCU readers with locked mutation of entry lists and destination sets, so delayed frees and counter updates must stay paired. `ip_vs_dest_set_eraseall()` schedules RCU frees without resetting `set.size`, which is acceptable during entry destruction but would be risky if reused elsewhere. Replication can grow hot entries until shrink timers run. Global and per-set weighted comparisons must avoid zero-weight destinations. Cache expiry under traffic is timer-driven, so tests need to account for jiffies and delayed RCU reclamation.

## Test Signals
Validate that a repeated destination starts with one server, gains another when the cached server is overloaded, and later drops the most loaded replicated member after `lblcr_expiration`. Cover unavailable/zero-weight servers, IPv6 hash keys, full-table expiry, service removal, duplicate insertion protection, and error handling when all destinations are overloaded.
