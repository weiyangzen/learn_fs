# sources/distributed-fs/ceph-client/fs/ocfs2/dir.h

## Purpose

`dir.h` declares the OCFS2 directory manipulation interface and defines the lookup-result structures shared between name lookup, insertion, deletion, and update code. It hides whether a directory is inline, unindexed extent-backed, or indexed behind common helper APIs.

## Important APIs, Types, and Functions

`struct ocfs2_dx_hinfo` stores the major and minor hash values used by indexed directory lookup and insertion. `struct ocfs2_dir_lookup_result` stores buffer heads and pointers for the unindexed dirent, dx root, dx leaf, dx entry, computed hash, and previous free-list leaf.

The main APIs are `ocfs2_find_entry()`, `ocfs2_delete_entry()`, `__ocfs2_add_entry()`, inline `ocfs2_add_entry()`, `ocfs2_update_entry()`, `ocfs2_check_dir_for_entry()`, `ocfs2_empty_dir()`, `ocfs2_find_files_on_disk()`, `ocfs2_lookup_ino_from_name()`, `ocfs2_readdir()`, `ocfs2_dir_foreach()`, `ocfs2_prepare_dir_for_insert()`, `ocfs2_fill_new_dir()`, `ocfs2_dx_dir_truncate()`, and `ocfs2_dir_trailer_from_size()`.

## Control Flow

Callers typically allocate a zeroed `ocfs2_dir_lookup_result`, call `ocfs2_find_entry()` for lookup/delete/update or `ocfs2_prepare_dir_for_insert()` before `ocfs2_add_entry()`, then release all held buffers with `ocfs2_free_dir_lookup_result()`. `ocfs2_add_entry()` is a dentry-friendly wrapper around `__ocfs2_add_entry()`.

## State and Persistence Behavior

The header does not mutate state directly. It defines the buffer ownership contract: lookup result fields hold references that must be released. The APIs declared here mutate persistent directory contents only in the corresponding `dir.c` implementation under journaling.

## Dependencies and Integration Points

This interface is consumed by OCFS2 namei, inode creation/removal, rename, orphan directory logic, VFS readdir, and truncate paths. It depends on buffer heads, journal handles, inode/dentry structures, OCFS2 on-disk dirent/dx types, and allocation contexts.

## Risks and Edge Cases

Callers must not free or dirty buffers in `ocfs2_dir_lookup_result` independently unless the called API documents it. Passing a lookup result from one directory mode after the directory has been converted or modified can corrupt the wrong buffers. `ocfs2_prepare_dir_for_insert()` may allocate blocks and return dx/free-list context that `ocfs2_add_entry()` expects to consume.

## Test Signals

API-level signals include balanced `ocfs2_free_dir_lookup_result()` use, correct behavior for inline and indexed directories through the same public calls, lookup/add/delete/update after directory expansion, and no leaked buffer references under failure paths.
