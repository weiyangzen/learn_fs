<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c -->
# sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c

## Purpose
`mdc_acl.c` unpacks POSIX ACL metadata from MDT replies into Linux `struct posix_acl` objects for llite metadata consumers.

## Important APIs, Types, And Functions
The single exported function is `mdc_unpack_acl(struct req_capsule *pill, struct lustre_md *md)`. It uses `struct mdt_body::mbo_aclsize`, request-capsule field `RMF_ACL`, `posix_acl_from_xattr()`, and `posix_acl_valid()`.

## Control Flow
If the MDT body reports zero ACL size, the function sets `md->posix_acl` to NULL and returns success. Otherwise it retrieves the exact-sized ACL buffer from the server capsule, converts the xattr-format bytes to a POSIX ACL object in the initial user namespace, validates the ACL, and stores it in `md->posix_acl`. Conversion or validation failures log an error and release partially built ACL state.

## State And Persistence
The function does not own persistent cache state. It transfers a referenced `struct posix_acl` to `lustre_md`; callers must release it according to Lustre metadata lifetime rules.

## Dependencies And Integration Points
It is compiled only when POSIX ACL support is enabled through the MDC Makefile. It integrates with MDT reply unpacking, llite inode preparation, Linux ACL conversion/validation helpers, and Lustre request capsules.

## Risks And Edge Cases
The MDT can legally set ACL-valid bits with zero ACL size, which must not be treated as protocol failure. Missing `RMF_ACL` with nonzero size is a protocol error. Invalid ACL data must be rejected before reaching VFS inode state.

## Test Signals
Cover replies with no ACL, valid access/default ACLs, missing ACL capsules, malformed xattr bytes, invalid ACL entries, memory allocation failures in conversion, and caller cleanup of returned ACL references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/mdc_acl.c -->
