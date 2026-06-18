<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.c -->
# sources/distributed-fs/orangefs/src/common/security/capcache.c

## Purpose
Implements the server-side capability cache when `ENABLE_CAPCACHE` is defined. It stores signed `PVFS_capability` objects in the generic `seccache` framework and supports a quick-sign path that reuses a cached signature for an equivalent capability.

## Important APIs, Types, And Functions
Exports `PINT_capcache_init`, `PINT_capcache_finalize`, `PINT_capcache_lookup`, `PINT_capcache_insert`, and `PINT_capcache_quick_sign`. Internal methods implement expiration clamped to capability timeout, Murmur3 hashing over issuer/fsid/op mask/handles, signature-based compare, cleanup, debug output, and field-based quick compare.

## Control Flow
Initialization creates a global `capcache` with a method table and sets its timeout from server configuration. Insert deep-copies the capability then passes it to `PINT_seccache_insert`. Lookup delegates to `PINT_seccache_lookup`. Quick-sign hashes the unsigned or partially populated capability, locks the cache, searches the bucket by stable capability fields, and if a non-expired cached capability is found copies timeout and signature back to the caller.

## State And Persistence
State is process-local in the global `seccache_t *capcache`; entries own duplicated capability memory and are freed by `PINT_cleanup_capability`. No disk persistence exists.

## Dependencies And Integration Points
Depends on `seccache`, `security-util`, Murmur3, server configuration, `pint-util`, `gossip`, and PVFS security types. It is selected by `security/module.mk.in` under `ENABLE_CAPCACHE`.

## Risks And Test Signals
Risks include dereferencing `capcache` before initialization, stale duplicate entries because insertion does not replace existing equivalent capabilities, hash/compare mismatch because the normal compare is signature-based while the hash is field-based, and quick-sign behavior around expired entries. Tests should cover init/finalize, insert/lookup by signature, null capability handling, quick-sign hit/miss/expired paths, and timeout clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/capcache.c -->
