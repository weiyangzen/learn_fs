# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_wlc.c

## Purpose
Implements the IPVS weighted least-connection scheduler `wlc`, selecting the eligible real server with the lowest connection overhead divided by destination weight.

## Important APIs, Types, and Functions
`ip_vs_wlc_schedule()` scans destinations and compares `ip_vs_dest_conn_overhead(dest) / weight` using cross multiplication. `ip_vs_wlc_scheduler` registers scheduler name `wlc`.

## Control Flow
The scheduler finds the first non-overloaded destination with positive weight and uses it as the initial least-loaded server. It then scans the remaining destinations, skipping overloaded ones, and chooses a new least server when `old_overhead * new_weight > new_overhead * old_weight`. It returns `NULL` with a scheduler error if no positive-weight destination exists.

## State and Persistence
No private state exists. It relies on live destination weight, active connection, inactive connection, overload, and refcount data.

## Dependencies and Integration Points
Uses IPVS destination lists, `ip_vs_dest_conn_overhead()`, atomic weights/counters, scheduler registration, and shared debug output. It is the weighted counterpart to `lc`.

## Risks
Weight reads are not locked against concurrent configuration changes, so a weight can change between initial filtering and later comparison. The second pass skips overload but does not explicitly skip zero weight in the comparison path, relying on destination state assumptions after the seeded positive weight. Distribution depends on accurate active/inactive counters.

## Test Signals
Test heterogeneous weights with controlled active/inactive counters, zero-weight quiescing, overload exclusion, no eligible destination, concurrent weight update behavior, and comparison against `lc` for equal weights.
