# sources/distributed-fs/lustre-release/lustre/llite/acl.c

## Purpose
`acl.c` implements llite POSIX ACL get/set support by bridging VFS ACL callbacks to Lustre xattr and metadata RPC operations.

## Important APIs, Types, and Functions
`ll_get_acl_common()` handles shared ACL retrieval. `ll_get_inode_acl()` and `ll_get_acl()` adapt to kernel ACL callback signatures. `ll_set_acl()` serializes ACLs and sends `md_setxattr()`. It uses `ll_xattr_list()`, `lli_replace_acl()`, `lli_install_acl()`, VFS ACL caches, and `struct ll_inode_info`.

## Control Flow
Reads reject RCU lookup, use the cached access ACL when valid, otherwise map ACL type to a Lustre xattr, fetch and decode it, install access ACL cache state, and duplicate the ACL for VFS ownership. Writes validate type, reject default ACLs on non-directories unless clearing, serialize the ACL, call `md_setxattr()`, clear `lli_synced_to_mds` on success, and update or forget caches depending on the result.

## State and Persistence Behavior
Persistent ACLs live as xattrs on the MDS. Client state includes VFS ACL cache, `lli_posix_acl` under `lli_lock`, `LLIF_ACL_VALID`, and `lli_synced_to_mds`.

## Dependencies and Integration Points
The file integrates with Linux POSIX ACL APIs, Lustre xattr helpers, metadata exports, ptlrpc request lifetimes, and kernel compatibility macros for ACL signatures.

## Risks and Edge Cases
Cache validity must stay coherent with metadata changes, stack-vs-heap xattr buffers need coverage, request references must be dropped, and compatibility branches need build coverage.

## Test Signals
Test access/default ACL get/set/clear, non-directory default ACL rejection, missing/unsupported xattrs, large ACL xattrs, RCU behavior, failed write cache invalidation, and builds across supported kernel ACL APIs.
