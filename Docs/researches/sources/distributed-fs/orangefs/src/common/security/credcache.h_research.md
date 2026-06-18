<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.h -->
# sources/distributed-fs/orangefs/src/common/security/credcache.h

## Purpose
Declares the server-side credential cache API under `ENABLE_CREDCACHE`.

## Important APIs, Types, And Functions
Defines `CREDCACHE_TIMEOUT` defaulting to 300 seconds and declares `PINT_credcache_init`, `PINT_credcache_finalize`, `PINT_credcache_lookup`, `PINT_credcache_insert`, and `PINT_credcache_remove`.

## Control Flow
Callers initialize the cache, insert verified credentials, lookup by credential, optionally remove entries, and finalize on shutdown.

## State And Persistence
No state is defined here; implementation state is a global `seccache_t`.

## Dependencies And Integration Points
Includes `pvfs2-config.h`, PVFS types, and `seccache.h`. It is visible only for `ENABLE_CREDCACHE` builds.

## Risks And Test Signals
The declared remove function lacks a matching implementation in `credcache.c`, creating a possible link-time failure if used. Compile and link tests in credential-cache builds are the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.h -->
