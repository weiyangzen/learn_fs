# sources/distributed-fs/ceph-client/fs/ocfs2/dcache.c

## Purpose

`dcache.c` implements OCFS2 dentry-cache validation and cluster dentry-lock attachment. It keeps VFS dentries coherent with remote unlink/rename activity by associating positive dentries with cluster lock resources scoped to a parent directory block number and inode. It also gives negative dentries a generation-based validity check tied to the parent directory lock generation.

## Important APIs, Types, and Functions

`ocfs2_dentry_attach_gen()` stores the parent directory lock generation in a negative dentry's `d_fsdata`. `ocfs2_dentry_revalidate()` is the VFS `d_revalidate` callback. It rejects RCU lookup, validates negative dentry generation, rejects deleted/bad/root/orphaned positive dentries, and forces relookup when a positive dentry lacks lock data.

`ocfs2_find_local_alias()` scans an inode's aliases for a dentry with usable `d_fsdata` and the requested parent block. It is used to share a single `struct ocfs2_dentry_lock` across multiple local aliases for links in the same directory.

`ocfs2_dentry_attach_lock()` attaches or reuses a cluster dentry lock for a positive dentry. It handles negative-to-positive conversion, alias reuse, fresh allocation, lock resource initialization, attachment under `dentry_attach_lock`, acquisition/release of the PRMODE dentry lock, and cleanup on failure.

`ocfs2_dentry_lock_put()` decrements the shared dentry-lock attach count and calls `ocfs2_drop_dentry_lock()` when the last local dentry releases it. `ocfs2_dentry_iput()` is the VFS `d_iput` callback and drops the dentry lock before `iput()`. `ocfs2_dentry_move()` updates lock association during cross-directory rename before calling `d_move()`.

## Control Flow

Lookup creates negative dentries with a generation snapshot or positive dentries that later call `ocfs2_dentry_attach_lock()` while the parent directory semaphore and parent cluster lock are held. For positive dentries, the function first reuses an alias lock if an inode already has a dentry under the same parent; otherwise it allocates `ocfs2_dentry_lock`, grabs the inode, stores the parent block, and initializes the lock resource.

The actual `dentry->d_fsdata` update is protected by the global `dentry_attach_lock` because final `dput()` may run asynchronously. After attachment, the code obtains and releases the dentry cluster lock to establish the local PRMODE hold. Remote unlink/rename can then trigger downconvert handling elsewhere, which will delete/unhash local dentries.

Revalidation is deliberately lightweight. Negative dentries are valid only if their stored generation equals the parent `ip_dir_lock_gen`. Positive dentries rely on inode flags/link count and the presence of dentry lock data; they do not take a cluster lock in the revalidate callback.

Rename uses `ocfs2_dentry_move()`. In same-directory renames, the lock identity is unchanged. In cross-directory renames, the old dentry lock is dropped, `d_fsdata` is cleared, a new lock is attached for the new parent block, and then `d_move()` updates the VFS dentry relationship.

## State and Persistence Behavior

State is in-memory only. `dentry->d_fsdata` is overloaded: negative dentries store a parent generation cast to pointer, while positive dentries store `struct ocfs2_dentry_lock *`. The `ocfs2_dentry_lock` holds an inode reference and an `ocfs2_lock_res` until the last local attached dentry releases it.

Persistent filesystem state is not directly modified here. The cluster-visible effect is lock ownership: a node that looked up a positive name holds a protected-read dentry lock until final dput, and unlink/rename upgrades to exclusive mode elsewhere to force other nodes to drop dentries.

## Dependencies and Integration Points

This file depends on VFS dentry operations, inode alias lists, OCFS2 inode/super structures, dlm glue for dentry locks, inode flags such as `OCFS2_INODE_DELETED`, and tracepoints. It integrates with lookup/namei paths, rename, final dput/iput, and remote dentry deletion/downconvert logic implemented outside this file.

## Risks and Edge Cases

The most important edge case is the `d_fsdata` type switch between negative generation and positive lock pointer. `ocfs2_dentry_attach_lock()` explicitly clears old negative data when converting to positive. Any path that interprets `d_fsdata` without knowing dentry polarity can corrupt state.

Alias reuse assumes that an alias found with a matching parent and lock data has a valid dentry-lock reference. Races with pruning are controlled by inode/dentry locks and `dentry_attach_lock`, but cross-directory rename and dput concurrency remain sensitive. On attach failure after allocating a new lock, manual cleanup is required because `d_instantiate()` may never occur.

Missing `d_fsdata` on a positive connected dentry is logged as an error in `ocfs2_dentry_iput()`, except for disconnected or unhashed dentries. That is a strong invariant signal for lookup/attach regressions.

## Test Signals

Test with clustered lookup/unlink/rename from multiple nodes, negative lookup then remote create, positive lookup then remote unlink, hard links in the same directory sharing lock state, cross-directory rename, dcache pruning under memory pressure, final dput after failed attach, and RCU lookup fallback returning `-ECHILD`. Tracepoints for revalidate, attach, alias finding, deletion, and orphaned inode paths are useful signals.
