# sources/distributed-fs/orangefs/src/client/windows/client-service/fs.c

## Purpose
`fs.c` is the OrangeFS abstraction layer used by the Dokany adapter. It hides direct `PVFS_sys_*` calls behind path-oriented helpers for initialization, lookup, create, remove, rename, truncation, attributes, IO, directory listing, statfs, and shutdown.

## Important APIs, Types, And Functions
The global `tab` stores the parsed pvfstab. Public functions include `fs_initialize`, `fs_get_mntent`, `fs_resolve_path`, `fs_lookup`, `fs_create`, `fs_remove`, `fs_rename`, `fs_truncate`, `fs_getattr`, `fs_setattr`, `fs_mkdir`, `fs_io`, `fs_io2`, `fs_flush`, `fs_find_files`, `fs_get_diskfreespace`, `fs_get_id`, `fs_get_name`, and `fs_finalize`. Internal helpers include `split_path`, `sys_lookup_follow_links`, and `sys_get_symlink_attr`.

## Control Flow
Initialization parses a tab file, starts the PVFS system interface, and adds the first mount entry. Path resolution strips an optional drive prefix and translates backslashes to forward slashes. Namespace-changing calls split the requested path into parent and entry name, follow symlinks on the parent, then call the appropriate `PVFS_sys_create`, `PVFS_sys_mkdir`, `PVFS_sys_remove`, or `PVFS_sys_rename`. Attribute, truncate, flush, and deprecated path IO calls first resolve the target to an object ref. `fs_io2` bypasses lookup and operates on a supplied object ref for the Dokany IO cache. Directory listing uses `PVFS_sys_readdirplus`, copies names and attributes, and tries to repair stat failures with `PVFS_sys_getattr`.

## State And Persistence
All durable state changes occur in OrangeFS. Local state is limited to the parsed mount table and temporary heap buffers. The implementation currently assumes one filesystem: `fs_get_mntent`, `fs_get_id`, and `fs_get_name` ignore their numeric inputs and use the first mount entry.

## Dependencies And Integration Points
This file depends on OrangeFS `pvfs2.h`, `str-utils.h`, and `client-service.h`. It is called by `dokany-interface.c` and indirectly exercised by the Windows client tests through the mounted drive.

## Risks And Test Signals
Symlink following is manual and capped at `FS_MAX_LINKS`, which is useful but creates complex memory ownership around copied attributes. Several allocation-failure branches leak sibling buffers or use uninitialized pointers in cleanup labels, especially in `fs_rename`. `fs_getattr` copies attributes from `sys_lookup_follow_links` then immediately calls `PVFS_util_release_sys_attr(attr)`, which is subtle because callers still rely on scalar fields. Directory attr arrays are also released after copying, so consumers must not expect allocated attr fields to remain valid. Tests cover common create, move, delete, directory listing, IO, flush, stat time, and statfs paths, but not symlink resolution or multi-filesystem behavior.
