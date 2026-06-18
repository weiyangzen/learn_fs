# sources/distributed-fs/openafs/src/afs/NBSD/osi_vnodeops.c

## Purpose
NetBSD vnode operation glue for the OpenAFS cache manager. It registers the `afs_vnodeop_entries` table, allocates NetBSD vnodes for `struct vcache`, bridges NetBSD VOP calls into common AFS routines, and manages UVM/genfs interactions.

## Important APIs, Types, and Functions
Exports `afs_vnodeop_p`, `afs_vnodeop_opv_desc`, and vnode handlers `afs_nbsd_lookup`, `create`, `open`, `close`, `access`, `getattr`, `setattr`, `read`, `write`, `ioctl`, `fsync`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, `readdir`, `readlink`, `inactive`, `reclaim`, `lock`, `unlock`, `bmap`, `strategy`, `pathconf`, and `advlock`. `afs_nbsd_getnewvnode` attaches a `struct nbvdata` to `v_data`, initializes genfs state, and sets vnode size to zero.

## Control Flow
Most VOP handlers translate NetBSD argument structs into calls to core AFS operations under `AFS_GLOCK`. Lookup copies `componentname`, optionally checks the NetBSD name cache, calls `afs_lookup`, and returns locked vnodes while handling dot-dot and create/rename `EJUSTRETURN`. Mutating directory operations copy names, call the corresponding AFS operation, then release or unlock parent/child vnodes according to NetBSD VFS rules. Read/write call `afs_read`/`afs_write`; write updates the UVM vnode size if the file grew. Reclaim flushes the vcache, destroys genfs state, frees `v_data`, and detaches `avc->v`.

## State and Persistence
Persistent state is remote AFS file state and local cache state held in vcaches/dcaches. Local kernel state includes vnode refs, `v_data`, UVM object size, genfs node state, name cache entries, and vcache flags such as `CUnlinked` and `CVInit`. No disk format is owned here.

## Dependencies and Integration Points
Depends on NetBSD VFS, UVM, genfs, `componentname`, `getnewvnode`, lock APIs, and OpenAFS core routines. Integrates with `afs_globalVFS`, `afs_xvcache`, `afs_ustrategy`, `HandleIoctl`, and AFS lockctl. Conditional branches cover NetBSD 5/6 lock and namei API changes.

## Risks
Highest-risk areas are vnode lock ordering during lookup/rename, reference release on error paths, UVM page invalidation via `VNP_UNCACHE`, stale `v_data` during reclaim, and the pathconf function returning `0` even after setting `code = EINVAL`. Kernel API drift across NetBSD releases is also significant.

## Test Signals
Exercise mount/root lookup, create/remove/rename including cross-mount failures, symlink/readlink, readdir with cookies, mmap/read/write file growth, vnode reclaim under cache pressure, advisory locks, fsync, and unlinked-open file behavior. Kernel diagnostics should not report lock assertion or vnode refcount failures.
