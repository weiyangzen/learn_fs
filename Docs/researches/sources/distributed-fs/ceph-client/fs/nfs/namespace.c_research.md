# sources/distributed-fs/ceph-client/fs/nfs/namespace.c

## Purpose
`namespace.c` handles NFS namespace path reconstruction and automatic client submounts when crossing server-side filesystem boundaries or NFSv4 referrals. It also manages expiry of NFS automounts and exposes a module parameter controlling the expiry timeout.

## Important APIs, Types, And Functions
`nfs_path()` reconstructs a server pathname from a dentry by walking parents under RCU and `rename_lock`, prepending the root dentry's `d_fsdata` export path, and optionally canonicalizing slashes. `nfs_d_automount()` creates a submount filesystem context, inherits parent mount flags, credentials, network namespace, protocol version, server address, port, and selected NFS module, then calls the version-specific `submount` method and creates a mount. `nfs_do_submount()` clones an `nfs_server`, builds a source string with `nfs_devname()`, parses it into the filesystem context, and calls `vfs_get_tree()`. `nfs_submount()` performs a fresh lookup to populate the mount filehandle and attributes before delegating to `nfs_do_submount()`.

The file also defines `nfs_mountpoint_inode_operations`, `nfs_referral_inode_operations`, `nfs_expire_automounts()`, `nfs_release_automount_timer()`, and custom `param_set_nfs_timeout()` / `param_get_nfs_timeout()` handlers.

## Control Flow And Integration Points
Automount starts from VFS dentry operations via `nfs_d_automount()`. A new fs_context is created with `fs_context_for_submount()`, NFS-specific clone data is filled, and `client->rpc_ops->submount()` is called. For normal NFSv3-style boundaries, `nfs_submount()` revalidates the child by lookup. The created mount is placed on `nfs_automount_list` and a delayed work item calls `mark_mounts_for_expiry()`.

## State And Persistence Behavior
Persistent state includes the global `nfs_automount_list`, `nfs_automount_task`, and `nfs_mountpoint_expiry_timeout`. Per-submount state lives in `struct nfs_fs_context` until mount creation and then in the cloned `nfs_server` and superblock. `nfs_path()` is read-only apart from returning a pointer into the caller buffer.

## Dependencies
The file depends on VFS dcache/mount/fs_context APIs, NFS client/server structures, `nfs_alloc_fattr()`, `nfs_clone_server()`, RPC ops, module parameters, workqueues, and parent dentry locking conventions.

## Risks And Edge Cases
Path reconstruction races with rename and must retry on sequence mismatch. Buffer exhaustion returns `-ENAMETOOLONG`. Root automount attempts return `-ESTALE`. `nfs_d_automount()` manually transfers credentials and network namespace references; mistakes leak or under-reference them. Submounts deliberately inherit only `NFS_SB_MASK` flags. Timeout parameter changes can cancel or reschedule expiry work while mounts remain on the list.

## Test Signals
Test nested exports, NFSv4 referrals, rename races while reading `/proc/mounts`, source path canonicalization, automount expiry disabled/enabled, root mountpoint handling, network namespace propagation, and security flavor inheritance across submounts.
