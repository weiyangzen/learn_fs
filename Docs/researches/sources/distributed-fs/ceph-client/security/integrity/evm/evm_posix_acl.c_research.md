<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c -->
# sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c

## Purpose
Provides a small helper that identifies POSIX ACL xattr names so EVM can treat ACL writes/removals as metadata-affecting operations even though they live under the `system.*` namespace.

## Important APIs, Types, And Functions
- `posix_xattr_acl(const char *xattr)` returns true for `XATTR_NAME_POSIX_ACL_ACCESS` and `XATTR_NAME_POSIX_ACL_DEFAULT`.

## Control Flow
The helper compares the requested xattr length and bytes against the two known POSIX ACL xattr names. It returns `1` on exact match and `0` otherwise.

## State And Persistence
This file has no persistent state. It only classifies names passed by EVM xattr and ACL hooks.

## Dependencies And Integration Points
It depends on Linux xattr constants and is consumed by `evm_main.c` when deciding whether an otherwise unprotected xattr operation can still require EVM revalidation because ACL updates may change mode bits protected by the EVM HMAC.

## Risks And Edge Cases
The function requires exact string length and content matches; aliases or future ACL xattr names would not be recognized. Because the return type is integer rather than bool, callers treat any nonzero value as true.

## Test Signals
Expected signals are that `system.posix_acl_access` and `system.posix_acl_default` trigger EVM ACL protections, while unrelated `system.*` xattrs do not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/evm/evm_posix_acl.c -->
