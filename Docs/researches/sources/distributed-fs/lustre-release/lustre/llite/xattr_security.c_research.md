<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c -->
# sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c

## Purpose
`xattr_security.c` handles Lustre security-label integration. It discovers which `security.*` xattr is managed by the active LSM, initializes create-time security contexts, stores or filters the context xattr name, and notifies the Linux security layer when server-provided contexts are applied.

## Important APIs, Types, And Functions
Public functions include `ll_dentry_init_security()`, `ll_inode_init_security()`, `ll_inode_notifysecctx()`, `ll_secctx_name_free()`, `ll_secctx_name_store()`, `ll_secctx_name_get()`, and `ll_security_secctx_name_filter()`. `ll_initxattrs()` is the callback passed to `security_inode_init_security()`.

## Control Flow
At mount/setup time, `ll_secctx_name_store()` asks the LSM for the security xattr name using `security_inode_listsecurity()`, validates the `security.` prefix, and stores it in `ll_sb_info`. Create paths call `ll_dentry_init_security()` or `ll_inode_init_security()` only when security xattrs are wanted. The dentry path asks `security_dentry_init_security()` for context bytes and validates returned xattr name on kernels that provide it. The inode path uses `security_inode_init_security()` with `ll_initxattrs()` to set each returned security xattr through the Lustre VFS setxattr wrapper.

## State And Persistence
The cached policy name is stored in `sbi->ll_secctx_name` and `ll_secctx_name_size`. Security context values themselves are server xattrs or LSM-managed inode state; this file only allocates temporary names/contexts and frees the cached name at teardown.

## Dependencies And Integration Points
The file depends on Linux LSM hooks, kernel-version compatibility around `lsm_context`, llite security/xattr predicates, `ll_vfs_setxattr()`, `LL_SBI_FILE_SECCTX`, and the security-name filter used by `xattr.c` and MDC packing.

## Risks And Edge Cases
Older kernels may not return the xattr name, so the code relies on SELinux conventions. Unsupported LSM hooks return success with no context. Name mismatches are rejected to avoid storing under a label Lustre did not request. `ll_inode_notifysecctx()` deliberately avoids `inode_lock()` to prevent a client deadlock.

## Test Signals
Test SELinux enabled/disabled, no LSM security xattr, name mismatch, create-time context setting, server-provided context notification, kernels with and without `lsm_context`, filtering of unmanaged security labels, and teardown freeing/replacing cached names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/llite/xattr_security.c -->
