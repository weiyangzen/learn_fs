<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h

## Purpose
Declares LDAP identity-mapping and authentication functions used by certificate-mode OrangeFS security.

## Important APIs, Types, And Functions
Defines `PVFS2_LDAP_SEARCH_CN`, `PVFS2_LDAP_SEARCH_DN`, and `PVFS2_LDAP_RETRIES`, and declares `PINT_ldap_initialize`, `PINT_ldap_map_credential`, `PINT_ldap_authenticate`, and `PINT_ldap_finalize`.

## Control Flow
The lifecycle is initialize connection, map certificate credentials during request validation, authenticate users for certificate retrieval, and finalize the LDAP connection.

## State And Persistence
No state is declared in the header; the implementation owns a global LDAP connection handle.

## Dependencies And Integration Points
Includes PVFS config and types. It is consumed by `pint-security.c` and `pint-uid-map.c`.

## Risks And Test Signals
Risks are feature-mode exposure and fixed retry semantics. Compile tests for certificate builds and LDAP integration tests validate the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-ldap-map.h -->
