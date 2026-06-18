<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.c -->
# sources/distributed-fs/orangefs/src/common/security/certcache.c

## Purpose
Implements a server-side certificate-to-identity cache under `ENABLE_CERTCACHE`. It maps certificate subjects to resolved uid and group arrays, reducing repeated LDAP or trust-store mapping work.

## Important APIs, Types, And Functions
Exports `PINT_certcache_init`, `PINT_certcache_finalize`, `PINT_certcache_lookup`, and `PINT_certcache_insert`. Internal helpers extract X509 subject strings, duplicate certificate expiration time, allocate `certcache_data_t`, hash by subject with Murmur3, compare subjects, free ASN1/group data, and print debug information.

## Control Flow
Insert converts the internal certificate to X509, copies its subject, uid, groups, and notAfter timestamp into a `certcache_data_t`, then inserts that data into `seccache`. Lookup builds a temporary `certcache_data_t` from the queried certificate, searches `seccache` by subject, then frees the temporary data. Expiration is set to now plus cache timeout but forced to expired if the certificate expires before that time.

## State And Persistence
Runtime state is the global `seccache_t *certcache`. Entries own duplicated group arrays and ASN1 expiration strings. No disk persistence occurs.

## Dependencies And Integration Points
Depends on OpenSSL X509/ASN1 APIs, `cert-util`, `seccache`, Murmur3, server config, and `gossip`. `pint-uid-map.c` uses it to cache LDAP mapping results; `pint-security.c` can cache the CA certificate as root.

## Risks And Test Signals
`certcache_data_t` is allocated with `malloc` and in the zero-group path `group_array` is not explicitly initialized before cleanup checks it, which is a memory-safety risk. Other risks include subject-string collisions or non-canonical subject forms, ASN1 time handling, and duplicate entries. Tests should cover zero-group inserts, lookup hit/miss, certificate-expiration clamping, CA-root cache insertion, and repeated finalize after populated cache use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/certcache.c -->
