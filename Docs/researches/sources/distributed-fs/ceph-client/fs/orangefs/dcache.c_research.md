## sources/distributed-fs/ceph-client/fs/orangefs/dcache.c

### Purpose
This file implements OrangeFS dentry revalidation, ensuring cached positive and negative dentries remain consistent with the distributed server namespace.

### Important APIs, types, and functions
- `orangefs_revalidate_lookup()` performs a server lookup for the parent/name pair and compares the returned handle to a positive dentry inode, or expects `-ENOENT` for a negative dentry.
- `orangefs_d_revalidate()` checks the dentry timeout, rejects RCU revalidation when blocking I/O is needed, skips root handle validation, and calls `orangefs_inode_check_changed()` for positive dentries.
- `orangefs_dentry_operations` exports `.d_revalidate`.

### Control flow
If the dentry timeout stored in `d_fsdata` has not expired, revalidation succeeds locally. Otherwise non-RCU lookup issues `ORANGEFS_VFS_OP_LOOKUP` through `service_operation()`. Positive dentries are dropped on lookup error or handle mismatch; negative dentries are trusted only when lookup still returns `-ENOENT`. Positive entries then issue getattr/change validation before final success.

### State and persistence behavior
Dentry validity is cached by storing an expiration jiffy in `dentry->d_fsdata` through `orangefs_set_timeout()`. No metadata is persisted locally; validation is always backed by server lookup/getattr once the timeout expires.

### Dependencies and integration points
Depends on `op_alloc()`, `service_operation()`, `match_handle()`, `is_root_handle()`, `orangefs_inode_check_changed()`, and timeout globals from `orangefs-kernel.h`. It integrates with VFS dcache lookup and path walk through `d_revalidate`.

### Risks
Short timeout values reduce stale dentries but increase daemon round trips. RCU path walks receive `-ECHILD`, forcing slower ref-walks. A daemon or server error drops dentries, which is conservative but can degrade lookup-heavy workloads.

### Test signals
Test cross-client create/delete/rename visibility, negative dentry invalidation, root dentry stability, RCU path fallback, and behavior when the client daemon restarts while dentries are expired.
