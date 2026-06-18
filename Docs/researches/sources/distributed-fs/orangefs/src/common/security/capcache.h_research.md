<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.h -->
# sources/distributed-fs/orangefs/src/common/security/capcache.h

## Purpose
Declares the server-side capability cache API and default timeout when `ENABLE_CAPCACHE` is enabled.

## Important APIs, Types, And Functions
Defines `CAPCACHE_TIMEOUT` defaulting to 10 seconds and declares `PINT_capcache_init`, `PINT_capcache_finalize`, `PINT_capcache_lookup`, `PINT_capcache_insert`, and `PINT_capcache_quick_sign`.

## Control Flow
Callers initialize the cache during server security setup, insert verified or newly signed capabilities, lookup by capability, optionally reuse signatures through quick-sign, and finalize on shutdown.

## State And Persistence
The header defines no state directly; the implementation owns the global `capcache` and entry memory.

## Dependencies And Integration Points
Includes `pvfs2-config.h`, standard integer/time headers, and `seccache.h`. All declarations are hidden unless `ENABLE_CAPCACHE` is set.

## Risks And Test Signals
Risks are build-mode drift and callers assuming these symbols exist in non-capcache builds. Compile tests should cover enabled and disabled configurations; runtime tests should validate each declared function through the server security lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.h -->
