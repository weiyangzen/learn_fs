<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c

## Purpose

`nfs-fops.c` is the low-level bridge between NFS protocol handlers and GlusterFS translator fops. It creates call frames from NFS user credentials, stores per-fop local state, winds translator operations, normalizes root inode attributes, injects gfid requests for create-like operations, expands auxiliary groups, forwards callbacks to protocol code, updates inode generation context, and destroys frames. Source read: complete 1630-line file.

## Important APIs, Types, and Functions

Core support functions are `nfs_fix_groups`, `nfs_fop_local_init`, `nfs_fop_local_wipe`, `nfs_frame_getctr`, `nfs_create_frame`, and `nfs_gfid_dict`. The exported fop wrappers include lookup, access, stat/fstat, opendir, flush, readdirp, statfs, create, setattr, mkdir, symlink, readlink, mknod, rmdir, unlink, link, rename, open, write, fsync, read, lk, getxattr, setxattr, and truncate. Each wrapper has a matching callback that restores program-local callback data and destroys the stack.

## Control Flow

Each wrapper validates required arguments, creates a frame with `nfs_create_frame`, initializes `nfs_fop_local` through macros from `nfs-fops.h`, saves root inode context if needed, optionally builds a `gfid-req` dictionary, and calls `STACK_WIND_COOKIE` to the child xlator fop. The callback reverses the hidden-local wrapping, fixes root inode numbers in returned `iatt` structures, updates generation on successful inode-returning operations, invokes the original protocol callback, and frees the fop local plus call stack.

Credential flow begins in `nfs_create_frame`: it copies uid, primary gid, auxiliary groups, lk owner, and identifier from `nfs_user_t` into the call stack, then `nfs_fix_groups` may replace groups with cached or freshly resolved server-side auxiliary groups.

## State and Persistence Behavior

Per-call state is stored in `struct nfs_fop_local` from an NFS mempool. It can hold original callback/local data, iobrefs, inode refs, fd refs for locks, gfid dict, root-normalization flags, paths, and lock state. There is no disk persistence. The file updates in-memory gid cache and fd lock state (`fd_lk_insert_and_merge`) and may update inode NFS generation context through `nfs_fix_generation`.

## Dependencies and Integration Points

The file depends on Gluster call frames, dicts, xlators, iobuf/iobref, call-stub semantics, semaphores, passwd/group lookup, NFSv3 helper conversion, NFS memory types, and `nfs-common.h`. Higher-level wrappers in `nfs-generics.c` and inode-aware wrappers in `nfs-inodes.c` call into this layer.

## Risks and Edge Cases

Error cleanup depends on `nfs_stack_destroy(nfl, frame)` receiving a valid `nfl`; failure before local initialization can be fragile if macros change. `nfs_fix_groups` copies up to `max_groups` but sets `root->ngrps = ngroups` after truncation, which can disagree with the copied count. `nfs_fop_write` casts `local` to `nfs3_call_state_t` to inspect `writetype`, making that wrapper less generic than its signature suggests. Root inode "funging" is necessary for stable NFS root ino but is easy to miss for new fops.

## Test Signals

Signals include NFSv3 operation tests across all wrappers, root directory stat/read/write/readdir stability after restart, create/mkdir/mknod/symlink gfid propagation, auxiliary group cache tests, lock merge tests, read/write sync mode tests, and fault injection for frame allocation, mempool allocation, dict allocation, and child fop errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/nfs-fops.c -->
