# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_lc.c

## Purpose
Implements the basic IPVS least-connection scheduler `lc`, selecting the available real server with the lowest connection overhead.

## Important APIs, Types, and Functions
`ip_vs_lc_schedule()` is the only scheduler operation. It scans `svc->destinations` and compares `ip_vs_dest_conn_overhead(dest)`, which weights active connections more heavily than inactive ones. `ip_vs_lc_scheduler` registers the module under scheduler name `lc`.

## Control Flow
On every scheduling request, the function traverses destinations under RCU list rules, skips overloaded servers and zero-weight quiesced servers, and tracks the destination with the smallest overhead. It returns `NULL` and emits `ip_vs_scheduler_err()` if no eligible destination exists. Module init and exit register and unregister the scheduler, with `synchronize_rcu()` after unregister.

## State and Persistence
This scheduler has no private per-service state. It relies entirely on live IPVS destination counters, flags, and weights. State changes are driven externally by connection tracking and service configuration.

## Dependencies and Integration Points
Depends on the IPVS scheduler registry, `struct ip_vs_service`, `struct ip_vs_dest`, RCU destination lists, atomic destination counters, and shared debug/error helpers. It is invoked by `ip_vs_schedule()` for services configured with scheduler `lc`.

## Risks
The algorithm ignores weights except for treating zero as quiesced, so heterogeneous backends should use `wlc`, `sed`, or related schedulers. It depends on accurate active/inactive counter transitions from protocol handlers. Tie-breaking favors the earliest destination in list order.

## Test Signals
Configure multiple real servers with different connection counters and verify the lowest overhead is chosen. Check zero-weight and `IP_VS_DEST_F_OVERLOAD` exclusion, no-destination error logs, and module load/unload registration messages.
