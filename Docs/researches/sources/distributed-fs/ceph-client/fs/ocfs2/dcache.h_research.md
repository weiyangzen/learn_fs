# sources/distributed-fs/ceph-client/fs/ocfs2/dcache.h

## Purpose

`dcache.h` declares OCFS2's dentry-cache interface and defines `struct ocfs2_dentry_lock`, the per-parent/per-inode lock object shared by local dentries. It is the small contract between lookup/namei/rename code and the dcache implementation in `dcache.c`.

## Important APIs, Types, and Functions

`struct ocfs2_dentry_lock` contains a local attach count, parent directory block number, pinned inode pointer, and `struct ocfs2_lock_res` used by DLM glue. The inode reference keeps the lock resource's inode context alive until the lock resource is destroyed.

Exports include `ocfs2_dentry_ops`, `ocfs2_dentry_attach_lock()`, `ocfs2_dentry_lock_put()`, `ocfs2_find_local_alias()`, `ocfs2_dentry_move()`, global `dentry_attach_lock`, and `ocfs2_dentry_attach_gen()`.

## Control Flow

Name lookup uses `ocfs2_dentry_attach_gen()` for negative dentries and `ocfs2_dentry_attach_lock()` for positive dentries. VFS uses `ocfs2_dentry_ops` to call revalidate and iput hooks. Rename calls `ocfs2_dentry_move()` to keep dentry lock identity synchronized with parent directory changes.

## State and Persistence Behavior

The header defines runtime-only dcache/lock state. `dl_count` is a local reference count for dentries sharing the same lock object. `dl_parent_blkno` is part of the lock name identity, and `dl_lockres` is the cluster lock resource that gives remote coherency semantics. There is no direct on-disk persistence.

## Dependencies and Integration Points

The type embeds `struct ocfs2_lock_res`, so users must include DLM glue definitions before use through normal OCFS2 headers. The declarations integrate with VFS dentry lifecycle, OCFS2 namei, inode lifetime, and cluster locking.

## Risks and Edge Cases

Callers must not treat `dentry->d_fsdata` as always being an `ocfs2_dentry_lock`; negative dentries store a generation value. `dentry_attach_lock` must protect attach/detach count and pointer updates against asynchronous dput. Mismanaging `dl_count` can leak an inode reference or drop an active lock resource.

## Test Signals

Build and runtime signals include correct VFS dentry operations installation, no missing-lock errors during iput, balanced lock put/drop under dcache shrinkers, alias reuse for hard links, and correct lock reattachment for cross-directory rename.
