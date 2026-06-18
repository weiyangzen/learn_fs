<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.h -->
# sources/distributed-fs/orangefs/src/common/security/client-capcache.h

## Purpose
Declares the client-side capability cache API and performance counter identifiers.

## Important APIs, Types, And Functions
Aliases `PINT_client_capcache_options` to `PINT_tcache_options`, defines client cache option macros, declares performance counter indexes, exposes `client_capcache_keys`, and declares lifecycle, get/set, lookup, update, invalidate, and perf-counter access functions.

## Control Flow
Client code initializes the cache, optionally adjusts tcache options, looks up cached capabilities before RPCs, updates the cache from server responses, invalidates stale object/user pairs, and finalizes during shutdown.

## State And Persistence
The header exposes no state except the external performance key table. Implementation state is in memory only.

## Dependencies And Integration Points
Includes PVFS types, locking, quicklist/quickhash, tcache, and performance counter headers. It bridges generic tcache behavior into client security and instrumentation.

## Risks And Test Signals
Risks are option alias drift if `PINT_tcache_options` changes and callers assuming thread safety beyond the wrapper API. Tests should compile against all option macros and validate performance counter names/ids remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/client-capcache.h -->
