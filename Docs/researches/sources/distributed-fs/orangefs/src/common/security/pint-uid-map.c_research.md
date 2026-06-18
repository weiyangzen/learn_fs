<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c -->
# sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c

## Purpose
Maps verified `PVFS_credential` objects to server-side uid and group arrays, using certificate cache/LDAP in certificate mode or direct credential fields in key mode.

## Important APIs, Types, And Functions
Exports `PINT_map_credential`. When certificate security is enabled without certcache, internal `check_ca_cert` detects whether a credential contains the trusted CA certificate for root mapping.

## Control Flow
The function validates required pointers, treats unsigned certificate-mode credentials as unmapped maximum uid/gid placeholders, then in certificate mode tries `certcache` first if available, falls back to LDAP mapping and caches successful results, or maps the CA certificate to root when certcache is disabled. In non-certificate mode it simply copies `userid`, `num_groups`, and `group_array` from the credential.

## State And Persistence
No state is owned here. It reads trust-store state, certificate cache state, LDAP configuration, and credential fields. Successful certificate-mode mappings may be persisted in memory through `certcache`.

## Dependencies And Integration Points
Depends on `pint-security`, `security-util`, optional OpenSSL trust store, `cert-util`, `pint-ldap-map`, and `certcache`. It is compiled into server builds by `security/module.mk.in`.

## Risks And Test Signals
The final no-groups check compares the `num_groups` pointer rather than `*num_groups`, so zero groups may not be rejected as intended. `group_array` is not null-checked before writes. Tests should cover unsigned credentials, certcache hit/miss, LDAP failure, CA root mapping, non-certificate direct copy, zero-group results, and group array bounds supplied by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.c -->
