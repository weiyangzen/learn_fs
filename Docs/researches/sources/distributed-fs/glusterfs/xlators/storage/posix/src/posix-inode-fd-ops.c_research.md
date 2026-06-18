# sources/distributed-fs/glusterfs/xlators/storage/posix/src/posix-inode-fd-ops.c

## Purpose

This is the main inode and file-descriptor operation implementation for the GlusterFS `storage/posix` translator. It maps Gluster fops onto backend POSIX syscalls, converts Gluster loc/fd/inode state into backend GFID handle paths or raw file descriptors, fills pre/post `struct iatt` results, manages xdata responses, performs cloudsync/object-state maintenance hooks, and updates the separate ctime metadata xattr when enabled.

The file covers stat/setattr, fallocate/discard/zerofill, open/read/write/copy_file_range, statfs, flush/release/fsync, xattr operations, access/truncate/fstat, lock/lease stubs, readdir/readdirp, rchecksum, and inode forget cleanup. Its behavior is central to brick-side correctness because it is the syscall boundary for most data and metadata operations.

## Important APIs, Types, and Functions

Important helpers include `MAKE_INODE_HANDLE`, `MAKE_REAL_PATH`, and `MAKE_HANDLE_PATH` from the handle layer, `posix_fd_ctx_get`, `posix_pstat`, `posix_fdstat`, `posix_xattr_fill`, `posix_cs_maintenance`, `posix_set_ctime`, `posix_update_utime_in_mdata`, and `posix_update_ctime_in_mdata`.

Top-level fops implemented here include `posix_stat`, `posix_setattr`, `posix_fsetattr`, `posix_glfallocate`, `posix_discard`, `posix_zerofill`, `posix_seek`, `posix_opendir`, `posix_readlink`, `posix_truncate`, `posix_open`, `posix_readv`, `posix_writev`, `posix_copy_file_range`, `posix_statfs`, `posix_flush`, `posix_fsync`, `posix_setxattr`, `posix_getxattr`, `posix_fgetxattr`, `posix_fsetxattr`, `posix_removexattr`, `posix_fremovexattr`, `posix_fsyncdir`, `posix_xattrop`, `posix_fxattrop`, `posix_access`, `posix_ftruncate`, `posix_fstat`, lock/lease stubs, `posix_readdir`, `posix_readdirp`, `posix_rchecksum`, and `posix_forget`.

Private state used from `struct posix_private` includes the export base path, creation masks, forced create/directory modes, O_DIRECT policy, disk reserve/full flags, shared-brick statfs scaling, batch fsync queues, ctime enablement, gfid2path and pgfid behavior, FIPS rchecksum behavior, and byte counters. FD state is stored in `struct posix_fd`, which can hold either a backend fd or `DIR *`, flags, EOF offsets, list linkage for janitor cleanup, and a back-reference for deferred close.

## Control Flow

Most fops follow a common flow: validate inputs; optionally switch fsuid/fsgid; resolve a `loc_t` through `MAKE_INODE_HANDLE` or obtain a `struct posix_fd`; collect pre-operation state; apply disk-space, cloudsync, internal-write, or atomic-write guards; run the backend syscall; collect post-operation state and update ctime metadata; fill xdata; restore fs identity; unwind.

Path operations use GFID handles except for absolute directory locs that can be safely mapped to the export path. FD operations rely on the fd context established by `posix_open` or `posix_opendir`. Directory release and file release enqueue `posix_fd` objects onto `ctx->janitor_fds`.

Read/write control flow has additional branches. `posix_readv` allocates an aligned iobuf, optionally runs cloudsync maintenance, issues `sys_pread`, updates the read counter, returns an iovec/iobref, then fstats and uses `ENOENT` as the EOF signal. `posix_writev` runs disk-reserve checks, internal-write checks, optional append/update-atomic locking, pre-stats, cloudsync maintenance, an O_DIRECT-aware write loop, response xdata fill, post-stat, ctime update, optional fsync, and ENOSPC overwrite retry checks.

Xattr control flow is broad. `posix_setxattr` filters immutable internal keys, handles legacy ctime metadata seeding, has a cloudsync upload-complete path that stores remote object metadata and truncates the local file, delegates normal key setting through `posix_handle_pair`, optionally syncs backend custom xattrs, and returns pre/post iatt details and ACL xdata. `posix_getxattr` and `posix_fgetxattr` synthesize virtual xattrs before falling back to syscall traversal. `posix_common_removexattr` enforces disallowed keys and supports bulk removexattr.

Directory reads use `posix_fill_readdir` under `fd->lock` to protect shared offsets, filter hidden entries, optionally skip directories, fill unknown dtypes with `fstatat`, track EOF offset, and return `gf_dirent_t` entries. `posix_readdirp_fill` resolves per-entry stats and xattrs. `GET_ANCESTRY_DENTRY_KEY` redirects `posix_readdirp` into ancestry reconstruction.

## State and Persistence Behavior

Persistent backend effects are direct syscalls on files, directories, and xattrs: chmod/chown/utimes/ftruncate/fallocate/punch-hole/zero-fill/write/copy/fsync and xattr set/remove. The file also updates Gluster-specific metadata xattrs through `posix_set_ctime` and related functions, handles cloudsync object xattrs, and maintains virtual responses for pathinfo, node UUID, GFID-to-path, ancestry, ACLs, object signatures, fd counts, and checksums.

In-memory state includes fd contexts, inode contexts for xattrop and atomic-write locks, fd cleanup queues, inode mdata context pointers, byte counters, directory EOF offsets, and unlink-deferred flags. `posix_release` and `posix_forget` both may remove a renamed/unlinked backend file when delayed unlink is pending.

## Dependencies and Integration Points

This file depends on Gluster core APIs: dictionaries, iobuf/iobref pools, inode/fd contexts, loc/inode tables, logging/message IDs, locks, xdata keys, stack unwind macros, and POSIX syscall wrappers. It integrates with the handle layer, ctime metadata, cloudsync helpers, ACL helpers, gfid2path/pgfid ancestry helpers, disk reserve checks, DHT migration xdata, shard atomic write expectations, AFR/WORM timestamp behavior, and the janitor thread for released fds.

## Risks

The largest correctness risks are errno/sign handling, lock lifetime, and feature parity. Several helpers return negative errno while syscalls use `-1` with `errno`; mistakes can leak wrong errors to clients. Atomic-write and xattrop locks must always unlock on every error branch. Xattr filtering is security-sensitive. Disk-reserve overwrite retry logic must avoid admitting real space-growing writes when the brick is full. `copy_file_range` performs one syscall and explicitly notes that short copies may need follow-up handling. Readdir offset behavior is subtle because heal code relies on next-entry offsets. O_DIRECT write fallback copies into aligned buffers but still relies on aligned sizes/offsets accepted by the kernel.

## Test Signals

Useful tests include stat/setattr/fsetattr pre/post iatt validation; chmod/chown/utimes on files, directories, and symlinks; O_DIRECT aligned and unaligned read/write; append and `GLUSTERFS_WRITE_UPDATE_ATOMIC` behavior under concurrent writers; ENOSPC overwrite retries; fallocate/discard/zerofill with and without kernel support; cloudsync object status/repair xdata; xattr list/get/set/remove including protected keys, bulk remove, ACLs, pathinfo, node UUID, gfid2path, ancestry, and object signatures; readdir/readdirp offset resumption and `GF_READDIR_SKIP_DIRS`; rchecksum in FIPS and non-FIPS modes; deferred unlink on release/forget; and lock/lease fallback behavior when higher lock translators are absent.
