# Group Research: group_1413_openbsd_src_sources_os_bsd_openbsd_src_sys_ufs_ext2fs_ext2fs_inode__1f4423bb9803

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_inode.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_inode.c

Implements ext2 inode size, lifetime, update, and truncation logic. It is derived from FFS inode code but maps ext2 on-disk fields through `i_e2fs_*`.

Key entry points:
- `ext2fs_size()` combines low and high size fields only for regular files.
- `ext2fs_setsize()` enforces `e2fs_maxfilesize`, updates high size for regular/new inodes, and marks large-file rocompat support when needed.
- `ext2fs_inactive()` truncates and frees zero-link inodes on last reference, sets deletion time, writes metadata, and recycles deleted/stale inodes.
- `ext2fs_update()` writes the in-memory dinode back to its inode-table block, including split 32-bit uid/gid storage.
- `ext2fs_truncate()` handles growth, shrink, page-cache invalidation, block pointer clearing, and block release.
- `ext2fs_indirtrunc()` recursively frees single, double, and triple indirect blocks.

Important behavior:
- Truncation first writes a shortened inode to disk, then frees removed blocks, reducing crash windows where live inode pointers reference freed blocks.
- Fast symlinks are stored in the inode and are zeroed directly when truncated to zero.
- Partial-block truncation zeroes bytes after EOF before freeing later blocks.
- Direct and indirect block accounting decrements `i_e2fs_nblock` using disk-block counts.
- Indirect block reads set `b_blkno` manually because bmap would fail after parent pointers have been removed.

Dependencies:
- Uses UFS vnode/inode scaffolding, buffer cache, `ext2fs_buf_alloc()`, `ext2fs_blkfree()`, and endian helpers.
- Closely parallels `ffs_inode.c`, but ext2 lacks FFS fragment-size handling and quota calls here.

Watch points:
- Triple indirect support is explicitly noted as untested.
- `allerror` is assigned after an earlier possible update error path, so error preservation depends on later flow.
- `ext2fs_setsize()` may mark `EXT2F_ROCOMPAT_LARGE_FILE` but still returns `EFBIG` when the requested size exceeds the computed max.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c

Implements ext2 directory reading, name lookup, directory entry mutation, emptiness checks, and rename path validation.

Key entry points:
- `ext2fs_readdir()` reads ext2 directory blocks and converts entries to BSD `struct dirent`.
- `ext2fs_lookup()` performs namecache lookup, linear directory scanning, create/delete/rename setup, and vnode locking rules.
- `ext2fs_search_dirblock()` scans one directory block, validates forward progress, finds matches, and records reusable slots.
- `ext2fs_direnter()` inserts a new entry, either by appending a fresh block or compacting free space.
- `ext2fs_dirremove()` removes an entry by zeroing the first entry in a block or merging with the previous record.
- `ext2fs_dirrewrite()` retargets an existing entry.
- `ext2fs_dirempty()` accepts only `.` and matching `..`.
- `ext2fs_checkpath()` prevents directory renames that would create cycles.

Important behavior:
- Directory record lengths are ext2 lengths, while exported `dirent` lengths are recomputed for BSD ABI.
- Lookup stores mutation state in the directory inode: `i_offset`, `i_count`, `i_reclen`, `i_ino`, and `i_endoff`.
- Creation searches for reusable slots and supports compaction when enough fragmented free space exists.
- Delete and rename paths enforce directory write permission, sticky-directory ownership rules, and read-only mount restrictions.
- `..` lookup unlocks the parent before fetching the target to avoid vnode lock deadlocks.

Dependencies:
- Uses `ext2fs_bufatoff()`, `ext2fs_truncate()`, `ext2fs_setsize()`, `VFS_VGET()`, namecache APIs, and UFS `ufs_dirbad()` diagnostics.
- Directory file type fields are filled only when ext2 revision/features support `EXT2F_INCOMPAT_FTYPE`.

Watch points:
- Full directory entry validation is gated by `dirchk`; malformed entries normally only require nonzero record length for progress.
- `ext2fs_dirbadentry()` prints and panics when enabled, so it is diagnostic rather than recoverable validation.
- `ext2fs_readdir()` converts one entry at a time and has an explicit TODO to batch conversions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c

Implements ext2 vnode read/write operations, with separate read paths for classic indirect blocks and ext4 extents.

Key entry points:
- `ext2fs_read()` dispatches to extent or indirect read based on `EXT4_EXTENTS`.
- `ext2_ind_read()` reads regular files, directories, and non-fast symlinks through vnode logical blocks.
- `ext4_ext_read()` resolves extent mappings and reads physical blocks from the device vnode.
- `ext2fs_write()` allocates buffers, copies user data, updates size, and writes buffers back.

Important behavior:
- Indirect reads use simple sequential read-ahead via `ci_lastr`.
- Extent reads use the extent cache, call `ext4_ext_find_extent()` on misses, and return success for cached gaps.
- Writes honor `IO_APPEND`, ext2 append-only files, vnode file-size limits, and filesystem overflow checks.
- Short or partial writes allocate with `B_CLRBUF` when needed.
- On `uiomove()` failure into a non-cleared buffer, the touched region is zeroed to avoid exposing stale page contents through mmap.
- `IO_UNIT` writes roll back file size and user I/O state via `ext2fs_truncate()`.

Dependencies:
- Uses `ext2fs_buf_alloc()`, `ext2fs_setsize()`, `ext2fs_update()`, `ext2fs_truncate()`, UVM vnode sizing, buffer cache, and extent helpers.

Watch points:
- Ext4 extent support here is read-oriented; writable ext4 extent semantics are not implemented in this file.
- `ext4_ext_read()` treats extent gaps as end of readable data for the current operation rather than synthesizing zero-filled holes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_subr.c

Provides ext2 helper routines for directory block access and vnode initialization.

Key entry points:
- `ext2fs_bufatoff()` returns a buffer for a directory offset and optionally a pointer inside the buffer.
- `ext2fs_vinit()` initializes vnode type/op vectors for an inode and handles special-device aliasing.

Important behavior:
- `ext2fs_bufatoff()` resolves ext4 extents directly when the inode has `EXT4_EXTENTS`; otherwise it falls back to vnode logical `bread()`.
- Special block/char vnodes are switched to `ext2fs_specvops` and passed through `checkalias()`.
- FIFO vnodes use `ext2fs_fifovops` when FIFO support is compiled in.
- The root inode gets `VROOT`.
- `i_modrev` is initialized from microtime.

Dependencies:
- Uses ext2 extent lookup, UFS inode/vnode wrappers, buffer cache, and spec/fifo vnode infrastructure.

Watch points:
- Extent lookup failure in `ext2fs_bufatoff()` silently falls back to normal block mapping.
- Device alias handling transfers `v_data` from the discarded vnode to the alias vnode.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c

Implements ext2 filesystem-level VFS operations: init, mount, reload, unmount, statfs, sync, vnode lookup, file handles, and metadata updates.

Key entry points:
- `ext2fs_init()` initializes inode/dinode pools and delegates common UFS init.
- `ext2fs_mountroot()`, `ext2fs_mount()`, and `ext2fs_mountfs()` attach ext2 filesystems.
- `ext2fs_reload()` reloads read-only mounted filesystem metadata after fsck.
- `ext2fs_unmount()` flushes, marks clean when possible, closes the device, and frees mount data.
- `ext2fs_statfs()` computes free blocks/files and overhead.
- `ext2fs_sync()` flushes dirty vnodes, device buffers, group descriptors, and superblock.
- `ext2fs_vget()` materializes vnodes/inodes from inode-table blocks.
- `ext2fs_fhtovp()` and `ext2fs_vptofh()` implement NFS file-handle conversion.
- `ext2fs_sbupdate()` and `ext2fs_cgupdate()` write superblock and group descriptors.
- `e2fs_sbcheck()` validates magic, block size, revision, feature compatibility, and journal recovery state.

Important behavior:
- Mounting read-write marks a clean filesystem dirty; unmount/sync can mark it clean again if no errors remain.
- Unsupported incompat features reject the mount; ext4 read-only incompat features force read-only operation.
- `e2fs_sbfill()` computes in-memory geometry and loads all group descriptors.
- Large-file limits are derived from logical indirect capacity and physical block counters, with special handling for huge-file and extent features.
- `ext2fs_vget()` reconstructs 32-bit uid/gid from split ext2 fields and resets deleted inodes to mode/size zero.
- Generation numbers are assigned on old filesystems when absent.

Dependencies:
- Shares UFS mount structure (`ufsmount`) and generic UFS operations.
- Uses ext2 endian load/save helpers, group descriptor helpers, pools, buffer cache, and vnode iteration APIs.

Watch points:
- `ext2fs_reload()` calls `e2fs_sbfill()` to allocate group descriptors after copying a new superblock; the old descriptor allocation is not freed in this function.
- `e2fs_sbcheck()` allows journal recovery-needed filesystems only for read-only mount attempts.
- `ext2fs_sync()` panics if it sees modified state on a read-only filesystem.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c

Defines ext2 vnode operations for create, metadata changes, links, rename, directories, symlinks, locking, fsync, reclaim, and vop tables.

Key entry points:
- `ext2fs_create()`, `ext2fs_mknod()`, and `ext2fs_makeinode()` allocate and install new inodes.
- `ext2fs_open()` enforces append-only open semantics.
- `ext2fs_access()`, `ext2fs_getattr()`, and `ext2fs_setattr()` implement permission and attribute operations.
- `ext2fs_chmod()` and `ext2fs_chown()` implement ownership/mode changes.
- `ext2fs_remove()`, `ext2fs_link()`, and `ext2fs_rename()` mutate directory links.
- `ext2fs_mkdir()` and `ext2fs_rmdir()` manage directory creation/removal and link counts.
- `ext2fs_symlink()` and `ext2fs_readlink()` support fast and block-backed symlinks.
- `ext2fs_pathconf()` reports timestamp resolution and delegates other values to UFS.
- `ext2fs_advlock()` uses inode lockf state.
- `ext2fs_fsync()` flushes buffers and inode metadata.
- `ext2fs_reclaim()` removes inode hash/cache state and returns pools.
- `ext2fsfifo_reclaim()` chains FIFO reclaim to inode reclaim.

Important behavior:
- Immutable and append-only flags affect access, open, setattr, remove, link, rename, mkdir/rmdir contexts.
- Non-root writes that change data clear setuid/setgid in the write path, while chown/chmod enforce BSD ownership rules.
- Rename follows the classic UFS algorithm: temporarily bumps source link count, creates/rewrites target, removes source, and patches `..` for moved directories.
- Directory creation writes `.` and `..` before entering the directory in the parent.
- Fast symlinks shorter than `EXT2_MAXSYMLINKLEN` are stored in the dinode shortlink area.

Dependencies:
- Uses ext2 allocation, directory, inode update/truncate helpers plus generic UFS lock, close, ioctl, kqueue, bmap/strategy, and cache routines.

Watch points:
- Rename has many panic assertions for impossible races or corrupted directory state.
- The FIFO vop table maps `.vop_access` to `ufsfifo_close`, which is an unusual table entry worth checking against surrounding OpenBSD conventions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ext2fs/ext2fs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_alloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_alloc.c

Implements FFS block, fragment, inode, cylinder-group, and cluster allocation/freeing policy.

Key entry points:
- `ffs_alloc()` allocates blocks/fragments with minfree and quota enforcement.
- `ffs_realloccg()` grows an existing fragment in place or relocates it.
- `ffs_inode_alloc()` selects and allocates a new inode.
- `ffs_dirpref()` chooses cylinder groups for new directories.
- `ffs1_blkpref()` and `ffs2_blkpref()` choose preferred block locations for UFS1/UFS2.
- `ffs_hashalloc()` tries preferred cylinder group, quadratic rehash, then brute-force scan.
- `ffs_cgread()` reads and validates cylinder group blocks.
- `ffs_fragextend()`, `ffs_alloccg()`, and `ffs_alloccgblk()` allocate fragments/full blocks inside a cylinder group.
- `ffs_nodealloccg()` allocates an inode bitmap slot and lazily initializes UFS2 inode blocks.
- `ffs_blkfree()`, `ffs_inode_free()`, and `ffs_freefile()` return blocks/fragments/inodes to free maps.
- `ffs_mapsearch()` finds a free fragment pattern using `fragtbl`.
- `ffs_clusteracct()` maintains contiguous-cluster summaries.

Important behavior:
- Allocation respects quotas before committing disk space and rolls quota back on failure.
- Non-root users cannot consume below `fs_minfree`.
- Fragment growth switches between `FS_OPTSPACE` and `FS_OPTTIME` based on fragmentation pressure.
- Directory placement spreads top-level directories and limits too many consecutive directories in one cylinder group.
- Indirect block preferences reserve early data areas in a cylinder group for metadata locality.
- Freeing validates against double-free of blocks/fragments/inodes and panics on corruption for writable filesystems.

Dependencies:
- Uses FFS fragment tables from `ffs_tables.c`, bitmap helpers from `ffs_subr.c`, UFS quota helpers, buffer cache, and filesystem geometry macros.

Watch points:
- Many corruption cases intentionally panic, reflecting kernel filesystem invariant enforcement rather than defensive recovery.
- `ffs_cgread()` returning NULL causes allocation/free routines to fail quietly in several paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_balloc.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_balloc.c

Allocates physical storage for logical file offsets, including direct blocks, fragments, and indirect trees.

Key entry points:
- `ffs_balloc()` dispatches to UFS2 or UFS1 implementation.
- `ffs1_balloc()` implements UFS1 allocation.
- `ffs2_balloc()` implements UFS2 allocation under `FFS2`.

Important behavior:
- Direct blocks may be full blocks or fragments depending on file size.
- When a write skips beyond a final fragment, the old fragment is extended to a full block first.
- For new indirect blocks, the code writes zeroed indirect blocks synchronously before linking parent pointers, avoiding pointers to garbage.
- Allocation failure after partial indirect allocation triggers an unwind path: fsync, clear parent pointer, free newly allocated blocks, restore quota, adjust block counts, and fsync again.
- `B_CLRBUF` controls whether returned buffers are cleared before use.

Dependencies:
- Uses `ufs_getlbns()` for indirect path decomposition.
- Uses `ffs_alloc()`, `ffs_realloccg()`, `ffs_blkfree()`, `ffs1_blkpref()`, `ffs2_blkpref()`, buffer cache, quota rollback, and UVM vnode size updates.

Watch points:
- Failure unwind is deliberately slow but protects against dangling softdep/block dependencies.
- UFS1 and UFS2 code are nearly parallel but differ in pointer width and some unwind details.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_balloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_extern.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_extern.h

Public internal header for FFS kernel routines, vop tables, sysctl IDs, and pools.

Contents:
- Defines FFS sysctl IDs, mostly legacy/softdep names plus active dirhash settings.
- Defines `FFS_NAMES` sysctl name table.
- Forward-declares kernel structs used by prototypes.
- Exports `ffs_vops`, `ffs_specvops`, and `ffs_fifovops`.
- Declares allocation, block allocation, inode update/truncate, helper, VFS, vnode, and softdep-related functions.
- Exports inode and dinode pools.

Important role:
- This is the API boundary between FFS implementation files and shared UFS code.
- FFS2-specific declarations are guarded by `#ifdef FFS2`.
- The prototypes expose the major layering: allocation, balloc, inode ops, subr helpers, vfsops, and vnops.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_inode.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_inode.c

Implements FFS inode metadata updates and truncation, including recursive indirect block freeing.

Key entry points:
- `ffs_update()` writes a UFS1/UFS2 inode to disk and updates timestamps.
- `ffs_truncate()` grows or shrinks files/directories/symlinks and frees blocks/fragments.
- `ffs_indirtrunc()` recursively clears and frees indirect block trees.

Important behavior:
- `ffs_update()` handles old UFS1 uid/gid compatibility fields and asserts effective link count matches disk link count.
- `ffs_truncate()` obtains inode quota state, enforces `fs_maxfilesize`, updates UVM size, and resets clustering state.
- Shrink writes the shortened inode and block pointers before freeing blocks.
- Unlike ext2, FFS handles fragment shrinkage of the final direct block and returns quota blocks through `ufs_quota_free_blocks()`.
- Direct block freeing uses `blksize()` so partial final fragments are accounted correctly.
- `ffs_indirtrunc()` supports UFS1 32-bit and UFS2 64-bit block pointer arrays through `BAP` macros.

Dependencies:
- Uses `UFS_BUF_ALLOC`, `UFS_UPDATE`, `ffs_blkfree()`, quota helpers, buffer cache, and UFS/FFS geometry macros.

Watch points:
- Triple indirect blocks are noted as untested.
- The code relies on writing pointer-cleared metadata before freeing storage to preserve fsck recoverability after crashes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_subr.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_subr.c

Provides shared FFS helper routines usable in kernel and some userland contexts.

Key entry points:
- `ffs_bufatoff()` reads a directory block for a byte offset and returns an optional pointer within it.
- `ffs_fragacct()` updates fragment summary counts for a block map.
- `ffs_isblock()`, `ffs_clrblock()`, `ffs_setblock()`, and `ffs_isfreeblock()` manipulate full-block availability in fragment bitmaps.
- `ffs_vinit()` initializes vnode type/op vectors and handles device aliases.

Important behavior:
- Bitmap helpers specialize for `fs_frag` values 1, 2, 4, and 8.
- `ffs_fragacct()` uses `fragtbl`, `around`, and `inside` patterns to count available fragment runs.
- `ffs_bufatoff()` adjusts buffer count to the actual logical block size from `blksize()`.
- `ffs_vinit()` assigns spec/fifo vop tables, marks root vnode, and initializes `i_modrev`.

Dependencies:
- Kernel part depends on UFS inode/vnode structures, buffer cache, and FFS vop tables.
- Non-kernel part exposes fragment and bitmap helpers plus `panic()` prototype for userland filesystem tools.

Watch points:
- The bitmap routines assume valid `fs_frag`; invalid fragment counts are rejected earlier by mount validation.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_tables.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_tables.c

Defines static fragment-allocation lookup tables used by FFS allocation and accounting.

Contents:
- `around[]` and `inside[]` bit masks support testing whether a fragment run of a given size is available.
- `fragtbl124[]` covers fragment configurations 1, 2, and 4.
- `fragtbl8[]` covers 8 fragments per block.
- `fragtbl[]` maps supported `fs_frag` values to the correct lookup table and leaves unsupported values NULL.

Important behavior:
- Allocation code uses these tables with bitmap scans to quickly locate suitable fragment runs.
- Mount validation rejects `fs_frag` values whose `fragtbl` entry is NULL.

Dependencies:
- Used by `ffs_mapsearch()` and `ffs_fragacct()` through declarations in FFS headers.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vfsops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vfsops.c

Implements FFS VFS operations: mount, reload, validation, sync, vnode lookup, file handles, superblock updates, initialization, and sysctl.

Key entry points:
- `ffs_vfsops` registers mount, unmount, statfs, sync, vget, fh conversion, init, sysctl, and export checks.
- `ffs_vtbl` binds UFS inode operation hooks to FFS implementations.
- `ffs_checkrange()` validates inode numbers and UFS2 lazy inode initialization for NFS file handles.
- `ffs_mountroot()`, `ffs_mount()`, and `ffs_mountfs()` attach filesystems.
- `ffs_reload()` refreshes read-only mounts after fsck.
- `ffs_validate()` checks superblock sanity.
- `ffs_oldfscompat()`, `ffs1_compat_read()`, and `ffs1_compat_write()` handle old UFS1 layout compatibility.
- `ffs_unmount()` flushes, marks clean, closes the device, and frees mount allocations.
- `ffs_flushfiles()` handles quota/system vnode flushing.
- `ffs_statfs()` reports block and inode availability.
- `ffs_sync()` flushes dirty vnodes, quotas, device buffers, and superblock state.
- `ffs_vget()` loads UFS1/UFS2 dinodes and initializes vnodes.
- `ffs_fhtovp()` and `ffs_vptofh()` convert NFS file handles.
- `ffs_sbupdate()` writes summary blocks then the superblock.
- `ffs_init()` initializes inode/dinode pools once.
- `ffs_sysctl()` exposes bounded dirhash sysctls when enabled.

Important behavior:
- Mount scans all known superblock locations and avoids interpreting an FFS1 superblock at the UFS2 location.
- Read-write mount is denied for unclean filesystems unless forced.
- Writable mounts allocate `fs_contigdirs`, set `fs_clean = 0`, and write the dirty superblock.
- `ffs_reload()` reuses existing pointer fields, reloads cylinder summaries, resets cluster knowledge, then reloads active vnodes.
- `ffs_sync()` can temporarily force clean/dirty superblock state during stall sync, then restores in-memory state.
- `ffs_sbupdate()` writes cylinder summaries first and avoids writing a clean superblock if summary writes failed.
- `ffs_vget()` sets generation numbers on old filesystems and supports UFS1 old uid/gid compatibility.

Dependencies:
- Uses generic UFS operations, quota code, dirhash sysctls, buffer cache, vnode iteration, FFS allocation/inode helpers, and `ffs_tables.c`.

Watch points:
- Clean/dirty handling is conservative and intentionally refuses normal read-write mount of unclean filesystems.
- `ffs_sync()` panics if modified filesystem state exists while mounted read-only.
- Many old-format compatibility paths are marked with `XXX`, but are still part of the mount/write path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vfsops.c -->