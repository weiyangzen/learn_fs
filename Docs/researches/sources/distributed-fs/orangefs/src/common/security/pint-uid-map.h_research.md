<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h -->
# sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h

## Purpose
Declares the credential-to-uid/group mapping API.

## Important APIs, Types, And Functions
Declares `PINT_map_credential(PVFS_credential *cred, PVFS_uid *uid, uint32_t *num_groups, PVFS_gid *group_array)`.

## Control Flow
Server authorization paths call this after credential verification to obtain POSIX-style identity information used by permission checks and request processing.

## State And Persistence
No state is declared. Mapping may consult caches or LDAP in the implementation depending on build mode.

## Dependencies And Integration Points
Includes PVFS config and types. Integrated with `pint-security`, LDAP mapping, and certificate cache code.

## Risks And Test Signals
Risks are caller-provided buffer sizing and feature-mode differences. Tests should validate key-mode and cert-mode mapping outputs and failure codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/pint-uid-map.h -->
