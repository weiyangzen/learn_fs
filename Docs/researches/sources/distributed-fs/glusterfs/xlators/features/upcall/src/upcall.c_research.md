# sources/distributed-fs/glusterfs/xlators/features/upcall/src/upcall.c

## Purpose
Implements the public fop surface and lifecycle for the `upcall` translator. It wraps many filesystem operations, records clients that have touched inodes, and sends cache-invalidation notifications to other clients when data, metadata, dentries, or selected xattrs change.

## Important APIs, Types, and Functions
- `upcall_local_init()` allocates per-call state, refs inode/fd, copies locs, and optionally copies xattrs.
- `UPCALL_STACK_UNWIND()` via `upcall.h` wipes local state after unwinding.
- Read/access fops (`up_lookup`, `up_open`, `up_stat`, `up_readv`, `up_readdirp`, etc.) update client state with `UP_UPDATE_CLIENT`.
- Write fops (`up_writev`, `up_truncate`, `up_ftruncate`, `up_fallocate`, `up_discard`, `up_zerofill`) invalidate with `UP_WRITE_FLAGS`.
- Metadata fops (`up_setattr`, `up_fsetattr`) invalidate attribute flags and include `UP_XATTR` when mode changes may affect ACL-derived xattrs.
- Dentry operations (`up_create`, `up_mkdir`, `up_mknod`, `up_symlink`, `up_unlink`, `up_link`, `up_rmdir`, `up_rename`) invalidate parent and child caches with parent stat buffers.
- Xattr operations (`up_setxattr`, `up_fsetxattr`, `up_removexattr`, `up_fremovexattr`, `up_xattrop`, `up_fxattrop`) filter registered xattrs before notification.
- `up_ipc()` lets clients register xattrs for invalidation through `GF_IPC_TARGET_UPCALL`.
- Lifecycle: `mem_acct_init()`, `init()`, `reconfigure()`, `fini()`, `upcall_forget()`, `notify()`, fops/cbks/options/xlator API.

## Control Flow
Each fop checks `EXIT_IF_UPCALL_OFF()`. When disabled, it winds directly to the child with no local allocation. When enabled, it allocates `upcall_local_t`, winds to the child, then the callback examines success and calls `upcall_cache_invalidate()` with operation-specific flags and stat/xattr data before unwinding.

`readdirp` additionally iterates returned entries and updates client state for each entry inode. `rename` sends invalidations for the renamed inode, old parent, and new parent if distinct. Xattrop handling compares AFR pending xattrs from request and response to notify only when a pending xattr is first set. `up_ipc()` records requested xattr patterns in `priv->xattrs`.

`init()` allocates private state, creates the registered-xattr dict, reads enable/timeout options, initializes locks/lists, creates a local pool, and starts the reaper thread when cache invalidation is enabled. `fini()` stops the reaper, releases the xattr dict, destroys locks/pools, and frees private state.

## State and Persistence
Persistent runtime state is in `upcall_private_t`; per-call state is in `upcall_local_t`. No on-disk state is written by upcall. Client access histories and registered xattrs are memory-only and lost on graph restart.

## Dependencies and Integration Points
Depends on `upcall-internal.c` for invalidation mechanics, GlusterFS stack APIs, client identity, `gf_upcall` notification types, XDR/RPC libraries, and cache-invalidation option parsing. It integrates with clients through `GF_EVENT_UPCALL` notifications and with xattr registration through IPC.

## Risks
- Disabled path relies on the `out` labels being before `STACK_WIND`; accidental local assumptions can break no-op mode.
- Many callback signatures must exactly match child fops; signature drift can silently break compile.
- `up_setxattr_cbk()`/removal callbacks assume `xdata` may contain `GF_POSTSTAT`; null or missing poststat changes flag richness.
- Notification timing is best effort and synchronous in callback path.
- Registered xattr dictionary grows by IPC registration and has no unregister path.

## Test Signals
Exercise disabled passthrough, enabled client registration, read-only updates, write invalidations, rename/link/unlink parent invalidations, readdirp entry updates, xattr registration/filtering, AFR xattrop first-pending detection, reconfigure thread startup, notify failure logging, and fini cleanup.
