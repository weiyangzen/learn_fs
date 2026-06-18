<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.c -->
# sources/distributed-fs/orangefs/src/common/security/credcache.c

## Purpose
Implements a server-side credential cache under `ENABLE_CREDCACHE`, storing duplicated `PVFS_credential` objects in `seccache` to avoid repeated signature verification work.

## Important APIs, Types, And Functions
Exports `PINT_credcache_init`, `PINT_credcache_finalize`, `PINT_credcache_lookup`, and `PINT_credcache_insert`. Internal seccache methods set expiration clamped to credential timeout, hash issuer and signature with Murmur3, compare signatures, cleanup duplicated credentials, and emit debug logs.

## Control Flow
Initialization creates a global `credcache` and configures timeout from server configuration. Insert deep-copies the credential and inserts it into `seccache`. Lookup delegates to `PINT_seccache_lookup`, which checks expiration and refreshes live entries. Finalize cleans the generic cache.

## State And Persistence
State is the global in-memory `seccache_t *credcache`; each entry owns a deep copy of the credential and its issuer/signature/group/certificate buffers.

## Dependencies And Integration Points
Depends on `seccache`, `security-util`, Murmur3, server config, `pint-util`, and gossip. It is selected in `security/module.mk.in` when a real security mode and `ENABLE_CREDCACHE` are active.

## Risks And Test Signals
The header declares `PINT_credcache_remove`, but this file does not implement it. Other risks include null global usage before init, duplicate entries, signature-size mismatch handling, and config timeout units. Tests should cover insert/lookup/null credential behavior, expiration, duplicate signatures, finalize cleanup, and link checks for the declared remove symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/credcache.c -->
