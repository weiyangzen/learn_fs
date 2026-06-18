# sources/distributed-fs/openafs/src/afs/FBSD/osi_vnodeops.c

## sources/distributed-fs/openafs/src/afs/FBSD/osi_vnodeops.c

Purpose: implements the FreeBSD vnode operation vector for AFS, translating FreeBSD VOP calls into the portable OpenAFS vnode/cache routines while handling FreeBSD VM pager integration. It is the main kernel-facing filesystem operation table for FreeBSD clients.

Important APIs/types/functions: `afs_vnodeops` registers handlers for lookup, create, open/close, read/write, `getpages`, `putpages`, ioctl, fsync, directory operations, reclaim, strategy, pathconf, and advisory locks. `GETNAME`/`DROPNAME` copy FreeBSD `componentname` names into NUL-terminated buffers. Compatibility helpers wrap changing FreeBSD VM object/page locking APIs and pbuf allocation. The operation bodies call core AFS APIs such as `afs_lookup`, `afs_create`, `afs_open`, `afs_close`, `afs_access`, `afs_getattr`, `afs_setattr`, `afs_read`, `afs_write`, `afs_remove`, `afs_link`, `afs_rename`, `afs_mkdir`, `afs_rmdir`, `afs_symlink`, `afs_readdir`, `afs_readlink`, `afs_fsync`, `afs_FlushVCache`, `afs_ustrategy`, and `afs_lockctl`.

Control flow: most VOPs acquire `AFS_GLOCK`, call the core AFS implementation with `VTOAFS`/`AFSTOV` conversions, and release the lock before returning. Lookup has special parent-directory lock ordering for `ISDOTDOT`, converts ENOENT during create/rename into `EJUSTRETURN`, and saves names when the namei operation needs them. Rename handles cross-mount rejection, same-vnode removal conversion, explicit vnode reference release, and core `afs_rename`. `getpages` maps FreeBSD VM pages into a pbuf kva range, builds a kernel `uio`, reads through `afs_read`, then marks pages valid/clean. `putpages` maps busy pages, selects a stored writer credential when available, writes via `afs_write`, undirties successful pages, and frees the held credential.

State/persistence: vnode state lives in `struct vcache` and FreeBSD `struct vnode`. Opens, writer credentials, VM object pages, and callback-derived cache state are updated through core AFS calls. Writes and pager writes persist through cache-manager store paths; `vn_pages_remove` invalidates written VM ranges. `reclaim` drops the vnode lock to avoid lock inversion, obtains `afs_xvcache`, calls `afs_FlushVCache`, clears `CVInit`, destroys the vnode object, and clears `v_data`.

Dependencies/integration: depends on FreeBSD VFS, namei, vnode pager, vm_page/vm_object APIs, pmap kva mapping, and OpenAFS global locking. It integrates with FreeBSD `vop_vector` registration and version-specific VM interfaces.

Risks/test signals: high-risk areas are lock ordering in lookup/reclaim/rename, credentials used during pager writeback, partial-page EOF handling, vnode-doomed close behavior, and FreeBSD-version compatibility macros. Test with pathname create/remove/rename/link/symlink, mmap read/write, fsync, forced vnode reclaim, pager writeback from syncer context, directory cookies, and advisory locks.
