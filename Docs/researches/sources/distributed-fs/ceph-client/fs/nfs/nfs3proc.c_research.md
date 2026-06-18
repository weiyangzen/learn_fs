# sources/distributed-fs/ceph-client/fs/nfs/nfs3proc.c

## Purpose
`nfs3proc.c` implements the client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation vector consumed by common NFS VFS code. It translates VFS operations into NFSv3 RPC messages, handles post-op attribute refresh, ACL setup after object creation, lockd integration, localio probing, and NFSv3-specific retry behavior.

## Important APIs, Types, And Functions
The file defines per-procedure helpers for root/fsinfo, getattr, setattr, lookup/lookupp, access, readlink, create, remove/unlink, rename, link, symlink, mkdir, rmdir, readdir/readdirplus, mknod, statfs, fsinfo, pathconf, read/write/commit setup and completion, lock operations, and delegation stubs. `nfs3_rpc_wrapper()` wraps synchronous calls to retry `-EJUKEBOX` after `NFS_JUKEBOX_RETRY_TIME`; `nfs3_async_handle_jukebox()` restarts async calls and increments `NFSIOS_DELAY`.

`struct nfs3_createdata` bundles create-family RPC arguments, response filehandle/fattrs, and directory WCC attrs. `nfs3_alloc_createdata()`, `nfs3_do_create()`, and `nfs3_free_createdata()` support create, mkdir, symlink, and mknod flows. `nlmclnt_fl_close_lock_ops` integrates close-time unlock with NFS I/O counters.

## Control Flow And Integration Points
The `nfs_v3_clientops` table wires these functions into the common NFS client. Object creation first applies POSIX ACL creation rules, performs the NFSv3 RPC, then applies ACLs using `nfs3_proc_setacls()`. Exclusive create falls back from `EXCLUSIVE` to `GUARDED` to `UNCHECKED` if the server returns `-ENOTSUPP`, and then performs a post-create setattr for requested attributes. Read/write completion updates inode attributes and can trigger localio probing after successful normal RPC I/O. Readdir stores raw directory pages for later decoding by `nfs3_decode_dirent()`.

## State And Persistence Behavior
The file updates inode attribute caches through `nfs_refresh_inode()`, `nfs_post_op_update_inode()`, and `nfs_writeback_update_inode()`. Directory and file inode operation tables persist as static structures. `nfs3_localio_probe_throttle` is a module parameter that controls periodic localio reprobe. Close unlock paths temporarily hold open and lock contexts while waiting for outstanding I/O.

## Dependencies
Dependencies include SunRPC, NFSv3 XDR procedure metadata, NFS page I/O, POSIX ACLs, lockd/NLM, iostat counters, VFS inode operations, localio optional hooks, and common NFS helpers for dentry/inode/cache management.

## Risks And Edge Cases
`EJUKEBOX` retry loops must remain killable/freezable. Attribute refresh after failed operations relies on WCC data. Create fallback changes semantics and must not leak ACL references or dentry aliases. Localio probing is throttled with a power-of-two mask but the parameter text warns users must choose a power of two. Lock close handling must not release contexts before async unlock can wait for I/O. Delegation is mostly unsupported for v3, so return paths flush writes.

## Test Signals
Exercise all NFSv3 VFS operations, exclusive create fallback, ACL inheritance, readdirplus, server `EJUKEBOX`, softreval getattr/lookup timeouts, read/write/commit completions, lock/unlock on close with pending I/O, localio reprobe throttling, and xfstests over rename/link/remove WCC behavior.
