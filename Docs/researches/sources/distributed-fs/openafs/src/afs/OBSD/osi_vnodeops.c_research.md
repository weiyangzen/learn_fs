# sources/distributed-fs/openafs/src/afs/OBSD/osi_vnodeops.c

## Purpose
OpenBSD vnode operation table and VOP wrappers that adapt OpenBSD vnode calls to common OpenAFS cache-manager operations.

## Important APIs, Types, and Functions
Defines either `struct vops afs_vops` for newer OpenBSD or `afs_vnodeop_p`/`afs_vnodeop_entries` for older kernels. Handlers include `afs_obsd_lookup`, `create`, `open`, `close`, `access`, `getattr`, `setattr`, `read`, `write`, `ioctl`, `select`, `fsync`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, `readdir`, `readlink`, `inactive`, `reclaim`, `lock`, `unlock`, `bmap`, `strategy`, `print`, `islocked`, `pathconf`, and `advlock`.

## Control Flow
Name-based operations use `GETNAME`/`DROPNAME` to copy component names. Lookup calls `afs_lookup`, maps create/rename ENOENT to `EJUSTRETURN`, and returns the child locked while respecting parent lock flags. File operations wrap `afs_open`, `afs_close`, `afs_read`, `afs_write`, and metadata routines under GLOCK. Mutating directory operations release vnode refs carefully after core AFS calls. Strategy constructs a kernel `uio` over the buffer and calls `afs_rdwr`.

## State and Persistence
Maintains vnode locks, refs, namei buffers, vcache locks, and AFS file/cache state. Write invalidates VM pages first. Reclaim flushes vcaches but leaves on-disk cache data.

## Dependencies and Integration Points
Depends on OpenBSD VFS/vnode/namei APIs, `lockmgr`, OpenAFS core vnode operations, `afs_xvcache`, and platform macros from `osi_machdep.h`.

## Risks
Error-path reference handling in lookup/rename/link/remove is high risk. `afs_obsd_select` always returns ready. Strategy manually releases `tvc->lock` and vnode refs, so caller assumptions must match. Kernel-version conditionals increase maintenance cost.

## Test Signals
Vnode operation regression tests for lookup/create/remove/rename, lock/unlock recursion, mmap/write stale-page behavior, buffer strategy reads/writes, advlock, pathconf, and busy vnode reclaim under cache pressure.
