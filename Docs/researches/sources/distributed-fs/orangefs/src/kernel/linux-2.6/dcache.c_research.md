## sources/distributed-fs/orangefs/src/kernel/linux-2.6/dcache.c

Purpose: Implements PVFS2 Linux VFS dentry operations, especially mandatory dentry revalidation against the userspace OrangeFS client and server metadata.

Important APIs and functions: `pvfs2_d_revalidate_common` validates a dentry by optionally issuing a PVFS2 lookup under the parent and then refreshing inode attributes. `pvfs2_d_delete` tells the VFS to discard dentries whose inode was marked as revalidation-failed. `pvfs2_d_revalidate` adapts to several kernel callback signatures and rejects RCU lookup mode with `-ECHILD`. `pvfs2_d_hash` leaves default hash behavior. `pvfs2_d_compare` implements exact name comparison across old and new kernel signatures. `pvfs2_dentry_operations` exports the callbacks.

Control flow: Revalidation rejects missing dentries/inodes/parents. For non-root handles it allocates a `PVFS2_VFS_OP_LOOKUP`, fills parent reference and child name, sends it through `service_operation`, and compares the returned handle with the inode. Lookup failure or handle mismatch sets `PVFS2_I(inode)->revalidate_failed`, drops the dentry, and returns invalid. Successful lookup or root-handle skip is followed by `pvfs2_inode_getattr`; only successful getattr returns valid.

State and persistence: No persistent state. It updates per-inode `revalidate_failed`, refreshes cached inode attributes, and drops invalid dentries from the kernel dcache.

Dependencies and integration points: Depends on PVFS2 kernel op allocation/release, lookup upcall/downcall protocol, handle conversion/matching helpers, `service_operation`, superblock fs ID, interruptible flag helpers, and Linux VFS dentry operation signatures.

Risks: Revalidating every dentry with lookup plus getattr is correct but expensive. `parent_inode` is not explicitly checked after `dentry->d_parent->d_inode`. `strncpy` to the upcall name buffer relies on protocol buffer sizing and may not NUL-terminate on long names. Debug buffer allocations are not checked before use. Error handling avoids `make_bad_inode` due historical oopses, so correctness relies on `revalidate_failed` and `d_drop`.

Test signals: Exercise valid and stale dentries, rename/unlink races, root handle revalidation, parent reference fallback paths, interrupted service operations, RCU lookup, long names, d_delete after revalidation failure, and performance under repeated path walks.
