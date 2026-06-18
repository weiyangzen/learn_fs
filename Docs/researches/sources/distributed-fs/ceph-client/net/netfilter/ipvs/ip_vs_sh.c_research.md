# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_sh.c

## Purpose
Implements the IPVS source hashing scheduler `sh`. It maps a hash of the client-side source address, optionally including a port, to a fixed per-service bucket table for stable client affinity.

## Important APIs, Types, and Functions
`struct ip_vs_sh_state` contains a fixed bucket array of RCU destination pointers. `ip_vs_sh_reassign()` rebuilds bucket assignments according to destination list order and weights. `ip_vs_sh_get()` selects a bucket directly, while `ip_vs_sh_get_fallback()` searches deterministically when the selected server is unavailable. `ip_vs_sh_get_port()` extracts TCP/UDP/SCTP ports when port hashing is enabled. `ip_vs_sh_schedule()` is the scheduler callback, and `ip_vs_sh_scheduler` handles service init, teardown, destination changes, and schedule.

## Control Flow
Service initialization allocates state and fills buckets by walking destinations, repeating each destination by weight. Destination add/delete/update triggers full reassignment. Scheduling chooses `iph->saddr` or `iph->daddr` depending on inverse direction, optionally extracts a transport port, hashes into the bucket table, and returns the selected destination if available. If fallback flag is set, unavailable buckets trigger a bounded deterministic search through alternate hashes.

## State and Persistence
Per-service state is the bucket table in `svc->sched_data`. Each occupied bucket holds a destination reference, released during reassignment and teardown. The table is volatile and rebuilt on destination changes.

## Dependencies and Integration Points
Uses IPVS scheduler flags `IP_VS_SVC_F_SCHED_SH_PORT` and fallback, destination reference management, RCU, hash helpers, and SKB transport header parsing. It integrates with cache-bypass style deployments where strict affinity can intentionally return no destination when the assigned cache is unavailable.

## Risks
Table size is fixed by config and collision/weight behavior depends on bucket count. Reassignment repeats destinations by weight but does not validate negative or rapidly changing weights beyond atomic reads. Without fallback, a single unavailable bucket returns no destination even if other servers are healthy. Port extraction fails to zero on truncated headers.

## Test Signals
Verify stable client-to-server mapping, weight-influenced bucket counts, fallback on overloaded or zero-weight assigned servers, strict no-fallback behavior, destination add/delete reassignment, IPv6 folded hashing, port hashing, and RCU cleanup on service removal.
