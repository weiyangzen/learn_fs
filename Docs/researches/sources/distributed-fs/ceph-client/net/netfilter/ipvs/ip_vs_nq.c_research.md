# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_nq.c

## Purpose
Implements the IPVS never-queue scheduler `nq`, a two-speed adaptive load sharing algorithm that immediately selects an idle eligible server when one exists and otherwise falls back to shortest expected delay.

## Important APIs, Types, and Functions
`ip_vs_nq_dest_overhead()` computes expected overhead as active connections plus one. `ip_vs_nq_schedule()` scans destinations and selects either the first idle eligible destination or the minimum `(activeconns + 1) / weight` destination. `ip_vs_nq_scheduler` registers the scheduler under name `nq`.

## Control Flow
The scheduler iterates `svc->destinations`, skipping overloaded and zero-weight servers. If it sees a server with zero active connections, it returns that server immediately. Otherwise it compares expected load with cross multiplication to avoid floating point. If no server is eligible, it logs a scheduler error and returns `NULL`.

## State and Persistence
No private state is kept. Decisions are computed from current destination weights, flags, and active connection counters.

## Dependencies and Integration Points
Uses IPVS service destination lists, atomic counters, destination flags, module registration, and the common scheduler callback contract. It is useful for heterogeneous pools where idle resources should be consumed before queueing on busier servers.

## Risks
Immediate return on the first idle destination makes list order important among idle servers. The algorithm ignores inactive connections in its cost function. Weight changes are read atomically during traversal and may change between selection and connection creation.

## Test Signals
Test that any idle eligible server is preferred over non-idle lower weighted-delay choices, that overloaded and zero-weight servers are skipped, that weighted SED comparison is used when all servers are busy, and that no-destination paths emit rate-limited scheduler errors.
