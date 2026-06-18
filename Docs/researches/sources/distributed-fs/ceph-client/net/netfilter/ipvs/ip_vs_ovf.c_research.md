# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_ovf.c

## Purpose
Implements the IPVS overflow scheduler `ovf`. It keeps traffic on the highest-weight destination until its active connections exceed its weight, then overflows to the next highest eligible destination.

## Important APIs, Types, and Functions
`ip_vs_ovf_schedule()` is the scheduler callback. It compares destination weights, active connection counts, and overload flags. `ip_vs_ovf_scheduler` registers scheduler name `ovf`.

## Control Flow
Each schedule call scans all destinations. A destination is skipped if it is overloaded, has zero weight, or has active connections greater than its weight. Among remaining destinations, the highest weight wins. If no destination satisfies the threshold, the scheduler reports no destination available.

## State and Persistence
No scheduler-private state is maintained. Behavior depends only on live active connection counters and configured weights.

## Dependencies and Integration Points
Uses IPVS scheduler registration, service destination RCU traversal, atomic destination fields, and shared logging. It is invoked by the normal IPVS scheduler path for services using `ovf`.

## Risks
The algorithm uses active connections only, so it may be unsuitable for UDP-like traffic where active counts do not represent queued work. The comparison condition allows active connections equal to weight but rejects greater than weight. It is intentionally biased toward highest weights and may leave lower-weight servers idle until overflow.

## Test Signals
Verify highest-weight selection under threshold, overflow when active connections exceed weight, zero-weight and overload exclusion, equality-at-threshold behavior, and no-destination logging when every destination is over threshold.
