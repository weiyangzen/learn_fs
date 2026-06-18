<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/permission.c -->
# sources/distributed-fs/ceph-client/security/keys/permission.c

## Purpose
`permission.c` centralizes permission and validity checks for keys. It converts requested key operations into permission-bit masks, applies owner/group/other/possessor permissions, then delegates final policy to the LSM layer.

## Important APIs, Types, and Functions
`key_task_permission()` checks a `key_ref_t` against a supplied `cred` and `enum key_need_perm`. `key_validate()` checks invalidated, revoked, dead, and expired state. Both are exported to other key subsystem and kernel consumers.

## Control Flow
Permission checks select the user, group, or other permission byte based on `fsuid`, `fsgid`, and supplementary groups. Possessor permissions from the top permission byte are ORed in when the key reference carries possession. Special needs such as unlink, sysadmin override, auth-token override, and deferred permission skip normal bit masks and go directly to `security_key_permission()`.

## State and Persistence
The file owns no state. It reads immutable or lock-protected fields from `struct key`: UID, GID, permission mask, flags, and expiry. Validation compares expiry against real time.

## Dependencies and Integration Points
It is used by keyring search, lookup, keyctl operations, request-key destination selection, and persistent keyring linking. LSM integration is mandatory through `security_key_permission()`.

## Risks
Possessor semantics are additive and easy to misapply if callers construct `key_ref_t` incorrectly. Special permission modes deliberately bypass bit checks but not LSM checks; new call sites must choose them narrowly. Expiry checks must match GC and search behavior.

## Test Signals
Test every permission class: possessor, owner, group by fsgid, group by supplementary groups, other, LSM denial, and special override modes. Validate expired, revoked, dead, and invalidated keys return the expected errno across read/search/link/update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/permission.c -->
