# sources/distributed-fs/ceph-client/fs/tracefs/event_inode.c

## Purpose
This file implements eventfs, the dynamic tracefs subtree that lazily creates inodes and dentries for tracing event directories and files from tracing metadata.

## Important APIs, Types, and Functions
Key exported/internal APIs are `eventfs_create_events_dir()`, `eventfs_create_dir()`, `eventfs_remove_dir()`, `eventfs_remove_events_dir()`, `eventfs_remount()`, `eventfs_d_release()`, `eventfs_remount_lock()`, and `eventfs_remount_unlock()`. Important structures are `eventfs_inode`, `eventfs_attr`, and `eventfs_root_inode`. Synchronization uses `eventfs_mutex`, static SRCU `eventfs_srcu`, krefs, and RCU list removal.

## Control Flow and State
Eventfs stores metadata in `eventfs_inode` objects rather than creating all dentries immediately. Lookup under an eventfs directory searches child eventfs directories first, then file entries, invokes the entry callback for file mode/data/fops, and creates an inode/dentry only on demand. Directory iteration emits dynamic file names and child directories while using SRCU and mutex checks to avoid freed metadata. Attribute changes save mode/uid/gid overrides in per-directory or per-entry caches so recreated dentries preserve user changes.

Top-level `eventfs_create_events_dir()` creates a persistent `events` dentry in tracefs, assigns eventfs inode state to `tracefs_inode.private`, and stores default ownership from the parent. Removal recursively marks eventfs metadata freed, deletes list links with RCU, invalidates the top dentry, and makes it discardable.

## Persistence, Dependencies, and Integration
Eventfs state is in-memory tracing metadata. It depends on tracefs inode allocation, security lockdown, fsnotify, VFS lookup/readdir/setattr, SRCU, krefs, and tracing-provided `eventfs_entry` callbacks. Remount integration resets inherited UID/GID overrides when tracefs remount options request that.

## Risks and Test Signals
Risk concentrates in lifetime and locking: callbacks are called under eventfs locks, dentry `d_fsdata` holds krefs, `is_freed` must be observed correctly, and readdir must remain stable while events disappear. Tests should stress event registration/removal during lookup/readdir/open, remount UID/GID changes, chmod/chown persistence on dynamic files, lockdown behavior, and lockdep/SRCU/RCU validation.
