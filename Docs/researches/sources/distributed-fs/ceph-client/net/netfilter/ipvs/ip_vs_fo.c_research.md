# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_fo.c

## Purpose
`ip_vs_fo.c` implements the IPVS weighted failover scheduler named `fo`. It always chooses the available real server with the highest configured weight, making weight act as a priority rather than a load-sharing proportion.

## Important APIs, types, and functions
The main scheduler callback is `ip_vs_fo_schedule()`. The module defines `ip_vs_fo_scheduler` with name `fo`, module ownership, scheduler list head, and schedule callback. Lifecycle functions are `ip_vs_fo_init()` and `ip_vs_fo_cleanup()`, which register and unregister the scheduler.

## Control flow
For each new connection, the scheduler walks `svc->destinations` under the caller's RCU-side scheduler context. It tracks the highest positive weight seen so far, ignoring destinations marked `IP_VS_DEST_F_OVERLOAD`. If a candidate exists, it logs the selected server and returns it. If no destination has a weight greater than zero or all candidates are overloaded, it reports a scheduler error and returns NULL to the core scheduling path.

## State and persistence behavior
The scheduler has no per-service `sched_data` and no persistent state beyond module registration. It reads live destination flags and atomic weights each time scheduling is invoked. Active connection counts are only logged; they do not influence selection.

## Dependencies and integration points
It integrates with the IPVS scheduler registry, service destination lists from the control plane, RCU list traversal, atomic destination weights, `IP_VS_DEST_F_OVERLOAD`, debug logging, and the core scheduler contract that NULL means no destination is available.

## Risks and edge cases
Equal weights pick the first destination encountered because the comparison is strictly greater than the current high weight. A destination with weight zero is never selected. The scheduler ignores active/inactive connection counts and health beyond overload flag/weight, so priority failover is deterministic but not balancing. If the highest-priority server becomes overloaded, selection moves to the next lower non-overloaded weight.

## Test signals
Test ordering with distinct, equal, zero, and changing weights; overload flag transitions; empty destination lists; selected destination stability while active connection counts change; and module load/unload with scheduler lookup by name `fo`.
