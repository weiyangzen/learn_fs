# sources/distributed-fs/ceph-client/fs/nfs/nfs3acl.c

## Purpose
`nfs3acl.c` implements POSIX ACL get/set/list behavior for NFSv3 using the separate Sun NFS ACL protocol. It bridges Linux VFS ACL APIs and xattr listing to `ACLPROC3_GETACL` and `ACLPROC3_SETACL` RPCs.

## Important APIs, Types, And Functions
Public functions are `nfs3_get_acl()`, `nfs3_proc_setacls()`, `nfs3_set_acl()`, and `nfs3_listxattr()`. Cache-race helpers `nfs3_prepare_get_acl()`, `nfs3_complete_get_acl()`, and `nfs3_abort_get_acl()` use POSIX ACL sentinels so concurrent `get_acl()` callers coordinate correctly. `__nfs3_proc_setacls()` performs the actual RPC and page allocation for large ACL payloads. `nfs3_list_one_acl()` contributes ACL xattr names only if an ACL is present.

## Control Flow And Integration Points
`nfs3_get_acl()` rejects RCU mode, checks `NFS_CAP_ACLS`, revalidates inode change state, requests access and/or default ACLs as needed, allocates an fattr, installs cache sentinels, performs a synchronous call on `server->client_acl`, frees XDR-allocated pages, refreshes inode attributes, normalizes unsupported errors to `-EOPNOTSUPP`, and completes or aborts ACL cache updates. `nfs3_set_acl()` combines access/default ACL state for directories and synthesizes an access ACL from inode mode if needed before calling `__nfs3_proc_setacls()`.

## State And Persistence Behavior
ACL values are cached in `inode->i_acl` and `inode->i_default_acl`. `server->caps` can be modified to clear `NFS_CAP_ACLS` if the extension is not supported. Set operations zap the NFS access cache and ACL cache after the RPC. Temporary pages used for XDR payloads are always freed before return.

## Dependencies
The file depends on POSIX ACL core helpers, NFS ACL XDR structures, `server->client_acl` created in `nfs3client.c`, NFS inode revalidation/refresh helpers, page allocation, and the configured ACL procedure table in `nfs3xdr.c`.

## Risks And Edge Cases
ACL cache sentinel handling must be exact to avoid caching stale ACLs or leaking references. Unsupported server responses disable capability and are converted to Linux ACL semantics. `__nfs3_proc_setacls()` treats too many ACL entries as `-ENOSPC` and allocates pages only when inline buffers are insufficient. `nfs3_proc_setacls()` masks `-EOPNOTSUPP` as success so create paths do not fail solely due to missing ACL protocol support.

## Test Signals
Run ACL get/set/list xattr tests on files and directories, concurrent ACL lookups, servers without NFS ACL support, ACL payloads above inline size, ACL entry limit overflow, create/mkdir with inherited default ACLs, and cache invalidation after chmod/setfacl.
