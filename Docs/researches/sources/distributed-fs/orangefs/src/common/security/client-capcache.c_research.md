<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.c -->
# sources/distributed-fs/orangefs/src/common/security/client-capcache.c

## Purpose
Implements the client-side capability cache. It stores per-object, per-user capabilities in `PINT_tcache`, synchronizes access with a mutex, and publishes performance counters for cache occupancy and hit/miss/update behavior.

## Important APIs, Types, And Functions
Exports `PINT_client_capcache_initialize`, `PINT_client_capcache_finalize`, `PINT_client_capcache_get_info`, `PINT_client_capcache_set_info`, `PINT_client_capcache_get_cached_entry`, `PINT_client_capcache_update`, `PINT_client_capcache_invalidate`, and `PINT_client_capcache_get_pc`. Internal types are `client_capcache_payload` and `client_capcache_key`; internal callbacks compare keys, hash by handle plus uid, free payloads, and set defaults.

## Control Flow
Initialization creates the underlying tcache, sets hard/soft/reclaim defaults, and initializes perf counters. Lookup checks enablement, searches by object reference and uid, counts hit or miss, invalidates timed-out entries, and deep-copies the cached capability for the caller. Update refuses soon-expiring capabilities, computes an expiration bounded by capability timeout minus a buffer, deletes an old entry if present, deep-copies the new capability into a payload, inserts it, and updates performance counters. Invalidate looks up and deletes one entry.

## State And Persistence
State is process-local: global tcache pointer, mutex, timeout flag, performance counter pointer, and entry payloads. No persistence exists; entries own copied capability internals.

## Dependencies And Integration Points
Depends on `tcache`, `quickhash`, `quicklist`, `gen-locks`, `pint-perf-counter`, `pint-util`, `security-util`, client sysint utilities, and gossip debug. It is included in `LIBSRC` by the security module makefile.

## Risks And Test Signals
Risks include dereferencing `client_capcache` before initialization, ignored or partially handled `PINT_copy_capability` failures on new inserts, leaks after update-copy failures, simple hash distribution and integer overflow, and an unused `client_capcache_timeout_flag`. Tests should cover init/finalize, disabled mode, hit/miss counters, timeout invalidation, replacement and purge counters, update of existing entries, soon-expiring capabilities, and copy-failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.c -->
