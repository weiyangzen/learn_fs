# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/krb5common.c

## Purpose
Provides Kerberos 5 helper routines for the AFS NetIDMgr plugin, especially context/cache initialization and finding the best credential cache for a NetIDMgr identity.

## Important APIs, Types, And Functions
`khm_krb5_error()` optionally formats an error and frees context/cache. `khm_krb5_initialize()` initializes a krb5 context, enables DES CRC enctype if valid, resolves an identity-specific cache, optionally falls back to default cache depending on build flags, and sets cache flags. `khm_get_identity_expiration_time()` validates cache principal against a NetIDMgr identity and finds TGT end/renewal expiration. `khm_krb5_find_ccache_for_identity()` scans collection caches, optional MSLSA, and configured FILE caches to pick the cache with the best expiration.

## Control Flow
Cache selection starts with the krb5 collection cursor, then reads Kerberos plugin parameters `MsLsaList` and `FileCCList` from NetIDMgr config. Each candidate cache is opened, checked for matching principal and valid TGT, and compared by expiration. The winning cache name is returned as Unicode.

## State And Persistence
Reads NetIDMgr Kerberos plugin configuration but writes no persistent state. It mutates caller-owned `krb5_context` and `krb5_ccache` pointers.

## Dependencies And Integration Points
Depends on dynamically imported Kerberos functions, NetIDMgr identity/config APIs, string conversion helpers, and `dynimport.h`. Called by `afsfuncs.c` when acquiring tokens from Kerberos credentials.

## Risks
`khm_krb5_get_error_string()` is declared in the header but not implemented here. Error handling is compiled differently under `NO_KRB5` and optional message-box flags. Cache principal string comparison must match NetIDMgr identity formatting exactly. Small fixed cache-name buffers can truncate unusual cache identifiers.

## Test Signals
Test identities with collection, MSLSA, and file caches; valid, expired, renewable, and mismatched TGTs; missing cache files; no default fallback builds; and DES enctype compatibility.
