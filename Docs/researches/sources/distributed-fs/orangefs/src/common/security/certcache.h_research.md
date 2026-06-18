<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.h -->
# sources/distributed-fs/orangefs/src/common/security/certcache.h

## Purpose
Declares the certificate cache API and the cached identity data structure when `ENABLE_CERTCACHE` is enabled.

## Important APIs, Types, And Functions
Defines `CERTCACHE_SUBJECT_SIZE` and `certcache_data_t`, which stores ASN1 expiration, subject, uid, group count, and group array. Declares `PINT_certcache_init`, `PINT_certcache_finalize`, `PINT_certcache_lookup`, and `PINT_certcache_insert`.

## Control Flow
Callers initialize the cache during security startup, insert certificate identity mappings after LDAP/trust resolution, lookup mappings before repeating LDAP work, and finalize on shutdown.

## State And Persistence
No global state is declared here, but the struct defines the per-entry memory owned by the implementation.

## Dependencies And Integration Points
Includes OpenSSL ASN1, `seccache.h`, and PVFS types. It is used only in certificate-cache builds.

## Risks And Test Signals
Risks include consumers depending on mutable `seccache_entry_t` internals and mismatched group-array ownership. Compile tests for enabled/disabled feature modes and runtime mapping-cache tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.h -->
