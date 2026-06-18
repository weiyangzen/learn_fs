<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/symlink.c -->
# sources/distributed-fs/lustre-release/lustre/llite/symlink.c

## Purpose
`symlink.c` implements Lustre llite symlink resolution and symlink-specific getattr. It fetches link targets from MDT metadata, validates and optionally decrypts them, caches usable targets in `lli_symlink_name`, and makes encrypted symlink `st_size` match the userspace-visible target.

## Important APIs, Types, And Functions
Key functions are `ll_readlink_internal()`, `ll_get_link()`, `ll_put_link()`, and `ll_getattr_link()`. The file exports `ll_fast_symlink_inode_operations` with `.get_link`, `.getattr`, `.setattr`, `.permission`, and `.listxattr`.

## Control Flow
`ll_get_link()` takes `lli_size_mutex`, calls `ll_readlink_internal()`, and returns either a cached target or a target backed by the MDT reply buffer with a delayed `ptlrpc_req_put()`. `ll_readlink_internal()` prepares metadata op data, requests `OBD_MD_LINKNAME`, checks the MDT body and expected length, retrieves `RMF_MDT_MD`, validates NUL termination for unencrypted links, and decrypts or no-key-encodes encrypted links through llcrypt helpers. `ll_getattr_link()` first delegates to `ll_getattr()` and, for encrypted links, resolves the link target to override `stat->size`.

## State And Persistence
The only durable local state is `ll_inode_info::lli_symlink_name`, allocated after a successful read. Encrypted no-key targets are intentionally not cached because adding the key later changes the visible target. RPC-backed buffers are held alive with delayed-call cookies until the VFS is done with the returned pointer.

## Dependencies And Integration Points
The file integrates with `md_getattr()`, request capsules (`RMF_MDT_BODY`, `RMF_MDT_MD`), llite inode metadata helpers, llcrypt symlink decoding, `ll_has_encryption_key()`, and normal llite attribute/permission/xattr operations.

## Risks And Edge Cases
Bad server replies are guarded by explicit protocol checks for missing `OBD_MD_LINKNAME`, mismatched `mbo_eadatasize`, missing target buffers, and missing NUL termination. `ll_get_link()` rejects RCU path-walk calls by returning `-ECHILD`. Encrypted symlink getattr is heavier than normal because it may need to read and decode the target.

## Test Signals
Cover cached and uncached symlink reads, malformed MDT reply handling, encrypted symlinks with and without keys, repeated `lstat()` size stability, request lifetime under delayed calls, `readlink()` races with inode eviction, and VFS path-walk behavior when `dentry` is NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/symlink.c -->
