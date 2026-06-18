# sources/distributed-fs/ceph-client/fs/nfs/nfs3_fs.h

## Purpose
`nfs3_fs.h` is the NFSv3-specific private header. It declares NFSv3 ACL operations, server creation/cloning helpers, and the NFSv3 subversion object used by module registration and pNFS data-server client setup.

## Important APIs, Types, And Functions
When `CONFIG_NFS_V3_ACL` is enabled, it declares `nfs3_get_acl()`, `nfs3_set_acl()`, `nfs3_proc_setacls()`, and `nfs3_listxattr()`. Without ACL support it provides a zero-success stub for `nfs3_proc_setacls()` and defines `nfs3_listxattr` as `NULL`. It also declares `nfs3_create_server()`, `nfs3_clone_server()`, and extern `struct nfs_subversion nfs_v3`.

## Control Flow And Integration Points
`nfs3client.c` implements server creation/cloning and ACL client initialization. `nfs3acl.c` implements the ACL functions when configured. `nfs3proc.c` installs ACL hooks into inode operations and calls `nfs3_proc_setacls()` after create/mkdir/mknod. `nfs3super.c` exports `nfs_v3` for registration and data-server setup.

## State And Persistence Behavior
This header holds no state. It controls compile-time behavior through configuration stubs, preserving common NFSv3 call sites even when ACL support is absent.

## Dependencies
The header depends on POSIX ACL types, NFS subversion registration, NFS filehandles/attributes, RPC auth flavors, and the common NFS server type.

## Risks And Edge Cases
The ACL-disabled stub returns success, which deliberately makes ACL setup a no-op; callers must not infer ACL support from `nfs3_proc_setacls()` alone. Declaration changes affect `nfs3client.c`, `nfs3acl.c`, `nfs3proc.c`, and `nfs3super.c`.

## Test Signals
Build with and without `CONFIG_NFS_V3_ACL`, verify xattr listing behavior, create files and directories with default ACLs, and confirm NFSv3 server cloning preserves or disables ACL capability correctly.
