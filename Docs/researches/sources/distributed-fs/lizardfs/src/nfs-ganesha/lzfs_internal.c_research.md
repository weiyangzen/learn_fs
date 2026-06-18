# sources/distributed-fs/lizardfs/src/nfs-ganesha/lzfs_internal.c

## Purpose
Provides shared FSAL helpers for error conversion, credential context creation, static-info access, and FSAL object handle allocation/deletion.

## Important APIs, Types, And Functions
`lizardfs2fsal_error`, `lizardfs2nfs4_error`, `lzfs_fsal_last_err`, and `lzfs_nfs4_last_err` translate `liz_last_err`/LizardFS errors to FSAL or NFSv4 status. `lzfs_fsal_create_context` builds `liz_context_t` from Ganesha `user_cred`, including supplementary groups. `lzfs_fsal_staticinfo` returns module static info. `lzfs_fsal_new_handle` and `lzfs_fsal_delete_handle` allocate/finalize object handles.

## Control Flow
Context creation maps anonymous uid/gid to zero, builds a LizardFS user context, and updates groups from either a stack array or allocated array. New-handle initializes inode, unique key, Ganesha object handle, object ops, fsid, fileid, and export pointer.

## State And Persistence Behavior
No persistent remote state. It allocates FSAL handle memory and transient client contexts.

## Dependencies And Integration Points
Depends on FSAL conversion/commonlib, pNFS utils, LizardFS C API, and declarations in `lzfs_internal.h`. Used by nearly every FSAL source file.

## Risks And Edge Cases
Anonymous-to-root mapping is security-sensitive and depends on export permissions. If supplementary group allocation fails for large group lists, it falls through to the stack-limited path and silently truncates to 64 groups. Error conversion warns and maps missing errno to `EINVAL`, which can hide upstream bugs.

## Test Signals
Credential mapping tests, group-list length tests, error conversion tests, and object-handle lifecycle tests would validate this shared layer.
