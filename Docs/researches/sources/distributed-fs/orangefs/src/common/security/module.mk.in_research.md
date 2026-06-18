<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/module.mk.in -->
# sources/distributed-fs/orangefs/src/common/security/module.mk.in

## Purpose
Controls which OrangeFS security source files are compiled into server and library builds based on feature macros.

## Important APIs, Types, And Functions
Adds `security-util.c` and `pint-uid-map.c` to `SERVERSRC`, adds `security-util.c` and `client-capcache.c` to `LIBSRC`, conditionally adds `seccache.c`, `capcache.c`, `pint-security.c`, `security-hash.c`, `pint-cert.c`, `cert-util.c`, `pint-ldap-map.c`, `credcache.c`, `certcache.c`, or `security-stubs.c`, and sets `MODCFLAGS_...pint-ldap-map.c := -DLDAP_DEPRECATED=1`.

## Control Flow
If key security is enabled, the build includes OpenSSL key-mode signing and optional credential cache. If certificate security is enabled, it includes certificate, LDAP, cache, and utility sources. If neither real mode is enabled, the server uses `security-stubs.c`.

## State And Persistence
No runtime state exists, but this file determines which security behavior is present in a binary.

## Dependencies And Integration Points
Integrates security code with the OrangeFS make system, server configuration, OpenSSL, LDAP, and optional caches.

## Risks And Test Signals
`NEEDCACHE = $(or ENABLE_CAPCACHE, ENABLE_CERTCACHE, ENABLE_CERTCACHE)` repeats `ENABLE_CERTCACHE` and omits `ENABLE_CREDCACHE`, so a credcache-only build may miss `seccache.c`. Build-matrix tests across key/cert/stub/cache combinations are the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/module.mk.in -->
