<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c

## Purpose
Implements LDAP integration for certificate-mode identity mapping and user/password authentication. It maps X509 certificate subjects to PVFS uid/gid values and authenticates users when retrieving certificates.

## Important APIs, Types, And Functions
Exports `PINT_ldap_initialize`, `PINT_ldap_map_credential`, `PINT_ldap_authenticate`, and `PINT_ldap_finalize`. Internal helpers log LDAP errors, load bind passwords from files, validate numeric attributes, parse certificate CNs, and convert OpenSSL slash-style subjects into LDAP DNs.

## Control Flow
Initialization opens the configured LDAP URI list, sets LDAPv3, loads an optional bind password, and binds as configured or anonymously. Mapping converts the credential certificate to X509, reads its subject, builds either a CN search filter or direct DN lookup, requests uid/gid attributes, retries searches after reconnect on LDAP failures, and returns mapped uid/group data or access denial. Authentication searches for a user DN, then creates a second LDAP handle and binds as that DN with the supplied password.

## State And Persistence
State is the global LDAP handle protected only during initialize/finalize. Passwords may be read from disk via `file:` configuration. No mapping results are persisted here; `certcache` may cache them.

## Dependencies And Integration Points
Depends on OpenLDAP, OpenSSL X509, server configuration, `cert-util`, `pint-security` error macros, `gen-locks`, and gossip. It is compiled with `LDAP_DEPRECATED=1` in certificate-security builds.

## Risks And Test Signals
`PINT_ldap_initialize` has early error returns that do not release `ldap_mutex`, LDAP searches use the global handle without locking, filters are built without escaping user/CN text, and DN conversion is simplistic. Tests should cover anonymous and bound init, password-file permissions, CN and DN search modes, retry/reconnect behavior, missing/non-numeric attributes, multi-entry warnings, authentication success/failure, and finalize after failed init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.c -->
