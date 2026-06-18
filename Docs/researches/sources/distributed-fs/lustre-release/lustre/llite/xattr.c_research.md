<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr.c

## Purpose
`xattr.c` implements llite VFS extended-attribute handlers. It filters namespaces, forwards get/set/list operations to MDT metadata RPCs or the client xattr cache, handles Lustre layout xattrs (`lov`, `lmv`, `dmv`, `lma`, `link`), ACL shortcuts, security-label filtering, and list sanitization.

## Important APIs, Types, And Functions
Important functions are `get_xattr_type()`, `ll_xattr_set_common()`, `ll_xattr_set()`, `ll_xattr_list()`, `ll_xattr_get_common()`, `ll_getxattr_lov()`, `ll_listxattr()`, and handlers in `ll_xattr_handlers[]`. Layout helpers include `ll_adjust_lum()` and `ll_setstripe_ea()`.

## Control Flow
Set paths validate namespace support, ACL ownership, trusted capability, user.* inode type, security context policy, and special cases. `lov` sets regular-file striping or directory defaults, with copied layout offsets reset and release flags cleared unless HSM archived. Generic sets call `md_setxattr()`, disabling user_xattr if the server rejects it. Get paths serve cached ACLs, call `ll_xattr_cache_get()` when safe, or request MDT xattrs with `md_getxattr()`. `lov` gets are synthesized from cl object layout or directory default stripe data and sanitized before userspace sees them. List paths filter unsupported namespaces and append virtual `lustre.lov`.

## State And Persistence
The file updates server-side xattrs through MDT RPCs and marks `lli_synced_to_mds` false after successful set/remove. It may clear `LL_SBI_USER_XATTR` on server incompatibility. It reads cached ACL and xattr cache state but does not own the cache memory.

## Dependencies And Integration Points
It integrates with Linux xattr handlers, llite security helpers, POSIX ACL conversion, MDC metadata RPCs, LOV/LMV layout structures, HSM state ioctls, cl object layout get, directory stripe helpers, project ID inheritance, and llite operation statistics.

## Risks And Edge Cases
Layout xattrs are binary ABI surfaces with endian and size checks. Exposing `security.c` encryption context is blocked for compatibility. `trusted.projid` is hidden on inherited-project trees. `lov` layout generation is sanitized so archive tools do not restore stale stripe offsets. Cache bypass is required for ACLs, security labels, SOM, and pinned Lustre xattrs.

## Test Signals
Test user/trusted/security/system/lustre namespaces, capability and ownership failures, POSIX ACL get/set, `lov`/`lmv`/`dmv` layout xattrs, endian-swapped input, HSM released layout copies, encrypted-file security.c denial, xattr list filtering, cache and no-cache paths, and server `-EOPNOTSUPP` disabling user_xattr.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr.c -->
