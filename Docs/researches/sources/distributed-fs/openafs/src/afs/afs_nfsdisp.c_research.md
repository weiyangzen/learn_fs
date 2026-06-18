# sources/distributed-fs/openafs/src/afs/afs_nfsdisp.c

## Purpose
`afs_nfsdisp.c` is the Solaris NFS translator dispatch interposer. It hooks NFSv2, NFSv3, and ACL dispatch tables, detects AFS file handles, invokes the AFS NFS-client credential handler before delegating to the original NFS implementation, and rewrites selected returned file handles to compact AFS `SmallFid` handles for root-only export mode.

## Important APIs, types, and functions
The file is compiled for `AFS_SUN5_ENV` when NFS translation is enabled. It defines local dispatch table descriptors, `afs_rfs_disp_tbl`, `afs_acl_disp_tbl`, `afs_rfs3_disp_tbl`, and `afs_acl3_disp_tbl`. Entry points `afs_xlatorinit_v2` and `afs_xlatorinit_v3` replace kernel dispatch procedures with AFS wrappers while retaining original procedure pointers.

Detection helpers are `is_afs_fh`, `is_afs_fh3`, `nfs2_to_afs_call`, `acl2_to_afs_call`, `nfs3_to_afs_call`, and `acl3_to_afs_call`. Credential dispatchers are `afs_nfs2_dispatcher` and `afs_nfs3_dispatcher`. Response helpers are `afs_nfs2_noaccess`, `afs_nfs3_noaccess`, `afs_nfs3_notsupp`, `afs_nfs2_smallfidder`, and `afs_nfs3_smallfidder`.

## Control flow
Initialization walks the kernel NFS and ACL dispatch tables, stores each original procedure in the AFS table, and installs AFS wrapper functions. Each wrapper temporarily sets `curthread->t_cred` to the request credential, calls the relevant dispatcher, denies access if the dispatcher reports rejection, otherwise calls the original kernel NFS/ACL procedure, then restores the saved thread credential.

The dispatchers identify the remote IPv4 client from the RPC transport, parse the operation-specific arguments to find one or two file handles, and check for the AFS VFS magic. For AFS calls, they trace the incoming `SmallFid`, capture the anonymous uid from exportinfo once, call `afs_nfsclient_reqhandler`, release the returned exporter, and use `call` return codes to indicate no AFS handling, normal AFS handling, or access denial.

For lookup/create/mkdir/symlink/mknod responses in `afs_NFSRootOnly` mode, smallfidder routines translate transient vnode-style handles into stable `SmallFid` data containing volume, cell index, unique, and vnode, then release the vnode reference.

## State and persistence behavior
The module mutates kernel dispatch tables in memory and records one-time initialization flags. It does not persist data. It temporarily mutates the current thread credential during wrapper execution and relies on `afs_nfsclient_reqhandler` for PAG/exporter state.

## Dependencies and integration points
Dependencies include Solaris NFS/NFS ACL kernel headers, exporter state, `afs_nfsclient_reqhandler`, vcache/vnode conversion, cell lookup, `SmallFid` layout, ICL tracing, and `afs_NFSRootOnly` policy. It directly complements `afs_nfsclnt.c` and `afs_osi_vget.c`.

## Risks and edge cases
Hooking kernel dispatch tables is ABI-sensitive. Every operation wrapper must preserve credentials and call the correct original procedure. File-handle parsing is operation-specific; missing a second-handle operation can bypass translator setup. `READDIRPLUS` is explicitly not supported for AFS calls under NFSv3. SmallFid conversion assumes returned handles are vnode-pointer handles marked with `AFS_XLATOR_MAGIC` and releases vnode refs based on `vrefCount`.

## Test signals
Test NFSv2/v3 operations with AFS and non-AFS handles, ACL get/set paths, access-denied behavior when export is disabled, thread credential restoration, root-only smallfid conversion on successful object-creating lookups, and `READDIRPLUS` returning not-supported for AFS.
