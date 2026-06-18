# sources/distributed-fs/ceph-client/net/rds/transport.c

## Purpose
Maintains the registry of RDS transports, handles lazy module loading, chooses preferred transports for local addresses, releases transport module references, and aggregates transport-specific stats.

## Important APIs, Types, and Functions
Exports `rds_trans_register()`, `rds_trans_unregister()`, `rds_trans_put()`, `rds_trans_get_preferred()`, and `rds_trans_get()`. `rds_trans_stats_info_copy()` is used by stats export. State is `transports[RDS_TRANS_COUNT]`, `rds_trans_modules[]`, and `rds_trans_sem`.

## Control Flow
Registration validates transport name length and installs one transport per type under write lock. Lookup by type first checks the registry, drops the read lock to `request_module()` if a known module is absent, then reacquires the lock and takes a module reference. Preferred lookup returns the loopback transport for loopback addresses; otherwise it scans registered transports and selects the first whose `laddr_check()` succeeds and whose module reference can be acquired. Stats aggregation unmaps the info iterator, walks registered transports under read lock, and lets each transport copy as many counters as available.

## State and Persistence
The registry is runtime global memory protected by an rwsem. Module references persist until released by callers through `rds_trans_put()`.

## Dependencies and Integration
Depends on module loading, IPv6/IPv4 address helpers, RDS loopback transport, transport callback structures, and RDS info iterator utilities.

## Risks and Test Signals
Risks include module reference leaks, out-of-range transport type callers, duplicate registration, and preferred-transport ambiguity when multiple transports accept the same local address. Test signals are lazy loading of `rds_tcp`, loopback preference, duplicate registration logging, transport unregister during module unload, and stats aggregation across registered transports.
