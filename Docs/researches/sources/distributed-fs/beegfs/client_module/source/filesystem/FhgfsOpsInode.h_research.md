# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsInode.h

## Purpose
`FhgfsOpsInode.h` declares the BeeGFS inode-operation interface and supplies compatibility shims/inlines for changing Linux kernel inode, time, ACL, idmapped mount, and VFS callback APIs. It also defines inline stat-to-inode application helpers used by inode creation and refresh.

## Important APIs, Types, And Functions
- Kernel time compatibility: `inode_timespec`, `inode_get_ctime*()`, `inode_set_ctime*()`, `inode_get_atime*()`, `inode_set_atime*()`, `inode_get_mtime*()`, `inode_set_mtime*()`, and `inode_set_mc_time()`.
- VFS operation declarations cover lookup, getattr, setattr, xattrs, ACLs, mkdir/mknod/create/atomic-open, rmdir/unlink/symlink/link, symlink follow/get-link, rename, and truncate.
- Inode cache/lifecycle declarations include `FhgfsOps_initInodeCache()`, `FhgfsOps_alloc_inode()`, `FhgfsOps_destroy_inode()`, `__FhgfsOps_newInodeWithParentID()`, and `__FhgfsOps_instantiateInode()`.
- Inline helpers include `__FhgfsOps_applyStatDataToInode()`, `__FhgfsOps_applyStatDataToInodeUnlocked()`, `__FhgfsOps_applyStatAttribsToInode()`, `__FhgfsOps_applyStatSizeToInode()`, `__FhgfsOps_newInode()`, `__FhgfsOps_isPagedMode()`, and `__FhgfsOps_refreshInode()`.
- `struct FhgfsInodeComparisonInfo` carries the generated inode hash and entry ID for `iget5_locked()` comparison.

## Control Flow
The header selects function signatures through `#if` blocks for kernel features such as `KERNEL_HAS_STATX`, `KERNEL_HAS_IDMAPPED_MOUNTS`, `KERNEL_HAS_USER_NS_MOUNTS`, `KERNEL_HAS_ATOMIC_OPEN`, `KERNEL_HAS_GET_LINK`, and ACL callback variants. This lets the implementation expose the exact callback prototypes expected by the target kernel.

The stat-application inlines first write mode, ownership, timestamps, link count, and block bits, then update size and block count under `i_lock`. `__FhgfsOps_applyStatSizeToInode()` contains the key paged-writeback protection: when regular files have page-write flags, it avoids decreasing `i_size` if no-decrease is set, writeback is active, or `FhgfsIsizeHints` indicate a concurrent update after the remote stat began. `__FhgfsOps_isPagedMode()` maps BeeGFS cache configuration to paged/native modes that require page-cache address-space operations.

## State And Persistence Behavior
The header modifies local inode fields through inline helpers but does not directly perform remoting. It controls local persistence of cached inode attributes, `i_size`, `i_blocks`, timestamps, and generated inode identity. The `i_size` decrease guard preserves local dirty/writeback data over potentially stale metadata-server sizes.

## Dependencies And Integration Points
The header integrates kernel compatibility macros from `FhgfsOps_versions.h`, BeeGFS `FhgfsInode`, `FsDirInfo`, `FsFileInfo`, remoting declarations, `NoAllocBufferStore`, and Linux VFS headers. It is included by inode, file, page-cache, and superblock operation code to keep callback signatures consistent with the build kernel.

## Risks
- The large compatibility matrix can hide compile-only bugs on kernel versions not covered by regular CI.
- Inline functions update inode state directly and depend on callers holding `i_lock` where required.
- The `i_size` decrease avoidance is intentionally conservative; bugs can cause stale size exposure or data-loss risk if it allows shrink during writeback.
- `__FhgfsOps_isPagedMode()` affects operation table selection and must remain aligned with all cache-type semantics.

## Test Signals
Kernel-version build matrix coverage, sparse/static checks for callback signatures, focused tests for `i_size` updates under writeback, and integration tests for paged/native/buffered cache mode inode creation provide the main validation signals.
