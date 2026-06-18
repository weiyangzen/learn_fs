# sources/distributed-fs/ceph-client/fs/ecryptfs/dentry.c

## Purpose

`dentry.c` provides eCryptfs dentry operations. It keeps upper dentries synchronized with lower dentry validity and releases the lower dentry reference stored in `d_fsdata`. This is the dcache glue that lets eCryptfs remain a stacked filesystem while deferring authoritative object validity to the lower filesystem when needed.

## Important APIs, types, and functions

The file defines `ecryptfs_d_revalidate()`, `ecryptfs_d_release()`, and exports `const struct dentry_operations ecryptfs_dops`. `ecryptfs_d_revalidate()` is the primary operation installed as `.d_revalidate`; `ecryptfs_d_release()` is installed as `.d_release`.

## Control flow

On dcache revalidation, the VFS calls `ecryptfs_d_revalidate()`. RCU lookup is not handled directly and returns `-ECHILD`. For non-RCU lookup, the function obtains the lower dentry from `ecryptfs_dentry_to_lower()`. If the lower dentry has `DCACHE_OP_REVALIDATE`, it snapshots the lower name and invokes the lower filesystem's `d_revalidate()` using the lower parent inode. For positive upper dentries it copies all lower inode attributes to the upper inode and invalidates the upper dentry when the upper inode has zero links.

On final dentry release, `ecryptfs_d_release()` simply `dput()`s the lower dentry reference held in `d_fsdata`.

## State and persistence behavior

The file does not define on-disk state. Runtime state is the upper dentry's `d_fsdata` pointer, which stores the lower dentry reference established during lookup or root mount setup. Revalidation refreshes upper inode metadata from lower inode metadata but does not persist data itself.

## Dependencies and integration points

This file depends on VFS dentry APIs, lower inode accessors from `ecryptfs_kernel.h`, `fsstack_copy_attr_all()`, and lower filesystem dentry operations. `main.c` installs `ecryptfs_dops` as the default dentry operations for the eCryptfs superblock. `inode.c` populates each upper dentry's lower dentry with `ecryptfs_set_dentry_lower()` during lookup and mount setup.

## Risks

Correct reference ownership is critical: every `d_fsdata` lower dentry must be a valid reference because release unconditionally `dput()`s it. Revalidation uses name snapshots to call lower operations, but behavior depends on lower filesystems honoring their own locking and lookup semantics. Returning stale-positive dentries after lower unlink would corrupt metadata visibility, so the zero-link invalidation path is an important regression point.

## Test signals

Tests should cover lookup cache hits against lower filesystems with and without `d_revalidate`, lower unlink followed by upper lookup/stat, RCU path fallback, mount/unmount dentry release reference balance, and attribute propagation after lower chmod/chown/timestamp changes.
