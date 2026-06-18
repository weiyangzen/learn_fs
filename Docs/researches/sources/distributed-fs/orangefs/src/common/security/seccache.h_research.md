<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.h -->
# sources/distributed-fs/orangefs/src/common/security/seccache.h

## Purpose
Declares the generic security cache data model, callback table, properties, stats, locking type, and public API.

## Important APIs, Types, And Functions
Defines default entry, size, hash, timeout, and stats-frequency values; `seccache_prop_t`; `seccache_entry_t`; `seccache_methods_t`; `seccache_stats_t`; and `seccache_t`. Declares all `PINT_seccache_*` operations and debug enter/exit macros.

## Control Flow
Specialized caches instantiate a `seccache_methods_t`, create a cache with `PINT_seccache_new`, configure timeout or stats, insert and lookup entries, and clean up at shutdown.

## State And Persistence
The header defines the layout of in-memory cache state and per-entry data. No disk persistence or serialization is described.

## Dependencies And Integration Points
Includes PVFS types, `llist.h`, and `gen-locks.h`. It is the shared substrate for `capcache`, `certcache`, and `credcache`.

## Risks And Test Signals
Risks include exposing internals to callers, callback contract mismatch, and units confusion around timeout comments versus use as seconds in cache clients. Compile tests for all specialized caches and runtime tests for callback edge cases are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/seccache.h -->
