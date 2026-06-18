# Group Research: group_339_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_ufs_ffs_softdep_c_s_632baf24f1e1

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/bsd/dragonflybsd`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep.c

DragonFly UFS/FFS soft updates implementation. It tracks metadata dependencies so UFS can issue asynchronous writes while preserving crash-safe ordering for allocation bitmaps, inode blocks, indirect blocks, directory entries, truncation, and inode reuse.

Key responsibilities:
- Registers a `bio_ops` implementation for softdep-aware buffer lifecycle hooks: I/O initiation, write completion, dependency deallocation, vnode fsync, mount sync, dependency movement/counting, and read/write checks.
- Maintains dependency objects for pages/directories (`pagedep`), inodes (`inodedep`), newly allocated blocks (`newblk`), cylinder-group bitmap safety (`bmsafemap`), direct and indirect allocations (`allocdirect`, `allocindir`, `indirdep`), delayed fragment/block/file frees, mkdir dependencies, directory additions, and directory removals.
- Builds hash tables for pagedep, inodedep, and newblk lookups, with simple semaphores to serialize racing structure creation.
- Protects allocation bitmaps by attaching inode/block allocation dependencies to cylinder-group buffers and completing them only after bitmap buffers reach disk.
- Handles direct block allocation dependencies, including fragment replacement, old-fragment delayed free, ordered inode dependency lists, directory page dependency creation, and merge handling for repeated allocation to the same logical block.
- Handles indirect block allocation dependencies by maintaining a safe shadow copy of indirect blocks; pending unsafe pointers are rolled back before disk writes and restored afterward.
- Implements truncate-to-zero and file deletion dependency handling: zeroes inode pointers, drains dirty buffers, deallocates obsolete dependencies, then delays block and inode frees until the zeroed inode state is stable.
- Implements directory add/remove/change ordering: new directory entries wait for target inode updates, removals wait for directory blocks to commit, renames combine add and remove dependencies, and mkdir adds also wait for `.`/`..` body and parent link updates.
- Rolls metadata back during `softdep_disk_io_initiation()` and rolls it forward during `softdep_disk_write_complete()`, marking buffers dirty again when an unsafe write used a temporary safe image.
- Provides synchronous cleanup paths used by `fsync`, sync, unmount, and memory-pressure throttling: `softdep_fsync`, `softdep_sync_metadata`, `softdep_flushfiles`, `flush_inodedep_deps`, `flush_pagedep_deps`, `clear_remove`, and `clear_inodedeps`.
- Recomputes cylinder-group summaries on softdep mount if the filesystem was not clean, because soft updates guarantees bitmap ordering more directly than auxiliary summary counters.

Dependencies:
- Includes DragonFly kernel buffer, mount, vnode, lock, spinlock, sysctl, and bio infrastructure.
- Depends on local UFS headers: `dir.h`, `quota.h`, `inode.h`, `ufsmount.h`, `fs.h`, `softdep.h`, `ffs_extern.h`, and `ufs_extern.h`.
- Calls core UFS/FFS routines including `ffs_flushfiles`, `ffs_blkfree`, `ffs_freefile`, `ffs_truncate`, `ffs_update`, `VFS_VGET`, `VOP_FSYNC`, `bread`, `bwrite`, `bawrite`, and buffer cache helpers.

Notable risks:
- The file intentionally enables `DIAGNOSTIC` and `DEBUG` if absent, reflecting the fragility of dependency invariants and the value of runtime checks.
- There is a likely typo in `newblk_lookup()` race cleanup: it releases `pagedep_in_progress` instead of `newblk_in_progress`.
- Locking is complex: many paths drop and reacquire the global softdep lock around allocation, I/O, vnode lookup, or buffer locking; callers must respect buffer/vnode lock ordering to avoid races or deadlocks.
- Several fatal paths use `panic()` for invariant violations or unrecovered I/O errors, so corrupt dependency state is treated as kernel-fatal rather than recoverable.
- The implementation only handles the common softdep truncation case of reducing file length to zero; other truncation cases are left to synchronous write behavior.
- Memory-pressure mitigation is heuristic, driven by `max_softdeps`, worklist backlog, syncer requests, and timed sleeps.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep_stub.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep_stub.c

Compile-time stub implementation used when `SOFTUPDATES` is not configured. It preserves the softdep API surface while making accidental use of softdep-only mutation hooks fail loudly.

Key responsibilities:
- Provides no-op initialization, mount, mount-device fsync, and metadata-sync functions when soft updates are disabled.
- Defines all setup/change/free softdep hooks with `__dead2` panics, preventing code paths from silently relying on missing dependency tracking.
- Keeps the same exported function names as the real softdep implementation, allowing the rest of UFS/FFS to link in non-softdep kernels.

Dependencies:
- Includes `opt_ffs.h` and is compiled only under `#ifndef SOFTUPDATES`.
- Uses local UFS/FFS headers for matching prototypes and type visibility: `quota.h`, `inode.h`, `ffs_extern.h`, and `ufs_extern.h`.

Notable risks:
- Any runtime call to a setup hook in a kernel built without `SOFTUPDATES` panics, so all call sites must be correctly guarded by mount flags or build configuration.
- `softdep_mount()` and `softdep_sync_metadata()` return success without doing work, matching the expectation that no softdep dependencies exist in this build.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_softdep_stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_subr.c

Shared FFS helper routines for block access, fragment accounting, and free-block bitmap operations. The code is partly kernel-only and partly usable outside the kernel.

Key responsibilities:
- Implements `ffs_blkatoff()` to read the filesystem block containing a byte offset and optionally return a pointer to the in-buffer offset.
- Implements `ffs_blkatoff_ra()` with read-ahead or cluster-read behavior for sequential directory/file scans.
- Implements `ffs_fragacct()` to update cylinder-group fragment summary counts using the `fragtbl`, `around`, and `inside` lookup tables.
- Implements bitmap tests and mutations: `ffs_isblock()`, `ffs_isfreeblock()`, `ffs_clrblock()`, and `ffs_setblock()` for fragment configurations of 1, 2, 4, or 8 frags per block.

Dependencies:
- Kernel builds include vnode, buffer, credential, mount, quota, inode, filesystem, and FFS external interfaces.
- Non-kernel builds include `dinode.h` and `fs.h`, and provide a local `panic()` declaration.
- Uses tables defined in `ffs_tables.c` through `fs.h` externs.

Notable risks:
- Bitmap operations panic on unsupported `fs_frag` values, so superblock validation must ensure legal fragment geometry.
- `ffs_blkatoff_ra()` avoids readahead for the last block because it may be a fragment; callers depend on correct `i_size` and `blksize()` calculations.
- Fragment accounting is table-driven and sensitive to bit-pattern interpretation; mistakes corrupt free-space summaries.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_tables.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_tables.c

Static fragment-pattern lookup tables used by FFS free-space accounting and allocation logic.

Key responsibilities:
- Defines `around[]` and `inside[]` bit masks used to identify available fragments inside a block map.
- Defines `fragtbl124` for filesystems with 1, 2, or 4 fragments per block.
- Defines `fragtbl8` for filesystems with 8 fragments per block.
- Exposes `fragtbl[MAXFRAG + 1]`, mapping legal fragment counts to the appropriate table and unsupported counts to null.

Dependencies:
- Includes only `sys/param.h`.
- Consumed by `ffs_fragacct()` and any code using `fragtbl` through `fs.h`.

Notable risks:
- These constants encode on-disk bitmap semantics; changing values would alter allocator behavior and summary accounting.
- Unsupported fragment counts deliberately have null table entries, so callers must validate or restrict `fs_frag`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vfsops.c

DragonFly VFS operations for mounting, unmounting, syncing, statfs, vnode lookup, file handles, initialization, and superblock updates for UFS/FFS.

Key responsibilities:
- Registers the `ufs` VFS with mount, unmount, root, quota, statfs, sync, vget, file-handle conversion, export checking, and init handlers.
- Implements root mount, new mount, and update/remount handling in `ffs_mount()`, including user argument copyin, device lookup, permission checks, read-only/read-write transitions, export updates, clean-bit handling, and softdep activation.
- Implements `ffs_reload()` for read-only filesystem reload after fsck, invalidating device metadata, rereading the superblock and summary info, and refreshing active inode contents.
- Implements `ffs_mountfs()` common mount setup: validates the block device and superblock, opens the device, copies the superblock, reads summary blocks, allocates per-mount summary/cluster/contiguous-directory state, initializes `ufsmount`, sets vnode ops, initializes inode hash, handles old filesystem compatibility, caps max file size for VM object limits, and marks writable filesystems dirty.
- Implements `ffs_unmount()` with softdep-aware flushing, clean superblock update, device buffer invalidation, device close, inode hash teardown, and memory cleanup.
- Implements `ffs_flushfiles()` with quota shutdown support, vnode flushing, and device metadata fsync.
- Implements `ffs_statfs()` from in-memory superblock counters and `freespace()`.
- Implements `ffs_sync()` to scan dirty vnodes, fsync modified files, flush device metadata, sync quotas, and write the superblock.
- Implements `ffs_vget()` to find or instantiate in-core inodes, read dinodes from disk, apply softdep effective link counts, initialize vnode type/ops, handle aliases, set generation numbers, and preserve old inode-format uid/gid compatibility.
- Implements NFS file-handle conversion with inode range validation and generation numbers.
- Implements `ffs_sbupdate()` to write summary information and the superblock, including compatibility transforms for old FFS formats.

Dependencies:
- Uses DragonFly VFS, vnode, buffer cache, device, nlookup, disk, VM, quota, and mount infrastructure.
- Depends on local headers `quota.h`, `ufsmount.h`, `inode.h`, `ufs_extern.h`, `fs.h`, and `ffs_extern.h`.
- Calls softdep entry points when `MNT_SOFTDEP` or `FS_DOSOFTDEP` is active.

Notable risks:
- Mount clean-bit policy rejects read-write mounts of unclean filesystems unless forced or read-only; forced dirty mounts only warn.
- Soft updates is explicitly incompatible with async mounts, so softdep mount/update clears `MNT_ASYNC`.
- Device vnode identity during update is handled carefully across devfs aliases; wrong matching can reject updates or reuse the existing device vnode.
- Error cleanup in `ffs_mountfs()` must release buffers, close the device, uninitialize inode hash state, and free mount allocations in the correct order.
- `ffs_reload()` assumes read-only state and a VMIO-capable device vnode; violations panic.
- Several compatibility sections preserve old 4.2/4.4 FFS layout behavior, increasing risk around superblock field ordering and max-file-size handling.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vnops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vnops.c

FFS vnode operation table and fsync wrapper, with read/write implementations included from shared UFS code.

Key responsibilities:
- Defines normal-file vnode operations for FFS, using UFS defaults plus FFS-specific fsync, block allocation, block reallocation, read, write, getpages, and putpages hooks.
- Defines special-device and FIFO vnode operation tables that use UFS default behavior and FFS fsync.
- Includes `ufs_readwrite.c`, which supplies the `ffs_read()` and `ffs_write()` implementations referenced by the vnode ops table.
- Implements `ffs_fsync()` to flush softdep metadata for mounted block devices, run `vfsync()` with dependency deferral and `softdep_sync_metadata`, then update the inode.
- Implements `ffs_checkdeferred()` to mark buffers with outstanding rollback-causing dependencies as deferred during sync traversal.

Dependencies:
- Uses VM, vnode, buffer, mount, process, and device infrastructure.
- Depends on local `quota.h`, `inode.h`, `ufsmount.h`, `ufs_extern.h`, `fs.h`, and `ffs_extern.h`.
- Calls `softdep_fsync_mountdev()`, `softdep_sync_metadata()`, `vfsync()`, `buf_countdeps()`, and `ffs_update()`.

Notable risks:
- `ffs_fsync()` relies on `vfsync()` callbacks to avoid writing metadata buffers before softdep dependencies are safe.
- Included source `ufs_readwrite.c` means apparent function definitions are split across files; build and review tooling must account for textual inclusion.
- Deferred buffer marking depends on `B_DEFERRED` and dependency counts to prevent premature writes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/ffs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/fs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/fs.h

Primary FFS on-disk layout and geometry header. It defines superblock and cylinder-group structures, filesystem constants, and macros for translating between offsets, blocks, fragments, cylinder groups, and inode locations.

Key responsibilities:
- Defines boot/superblock sizes and offsets, minimum block size, mount/volume name lengths, default free-space policy, default directory allocation tuning, and reserved snapshot inode count.
- Defines `struct csum` cylinder-group summary counters.
- Defines `struct fs`, the FFS superblock, including geometry, layout offsets, masks/shifts, summary counters, clean/readonly/flags state, mount name, volume name, in-core summary pointers, cluster and directory allocation helpers, compatibility fields, max file size, masks, state, rotational layout metadata, and magic number.
- Defines filesystem magic, clean-state checksum value, inode format versions, optimization modes, softdep/unclean flags, and rotational table formats.
- Provides macros to access rotational layout tables and cylinder-group array data for both current and old cylinder group formats.
- Defines `struct cg` current cylinder group and `struct ocg` compatibility layout.
- Provides block/offset conversion macros: filesystem block to disk block, disk block to byte offset, logical block to offset, byte offset to logical block, fragments to blocks, blocks to fragments, cylinder group location, inode-to-block mapping, block map extraction, and free-space calculation.
- Provides block-size macros for current in-core inode, disk dinode, and explicit size cases, including fragment-sized final blocks.
- Exposes `inside`, `around`, and `fragtbl` table symbols.

Dependencies:
- Relies on UFS scalar types from included upstream headers and `sys/param.h` consumers.
- Used broadly by FFS allocation, softdep, mount, vnode, and filesystem utility code.

Notable risks:
- This is on-disk ABI. Structure layout, constants, and compatibility transforms must remain stable for existing FFS filesystems.
- Many macros assume power-of-two block/fragment sizes and correct superblock masks/shifts; corrupt or unvalidated superblocks can cascade into wrong disk offsets.
- The file reserves FreeBSD snapshot/pending fields for compatibility while comments state DragonFly does not implement snapshots here.
- `fs_csp`, `fs_maxcluster`, and `fs_contigdirs` are in-core pointers embedded in the superblock copy, requiring careful preservation during reload and superblock writes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/inode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/inode.h

Kernel UFS inode wrapper header. It defines the in-core inode structure that pairs DragonFly vnode state with an on-disk UFS1 dinode and filesystem-specific transient fields.

Key responsibilities:
- Defines `ufs_lbn_t` as the logical block number type and `doff_t` for directory offsets.
- Defines `struct inode` under kernel/kernel-structure builds, including hash linkage, vnode/device references, flags, device and inode number identity, effective link count, filesystem pointer, quota pointers, NFS modification revision, byte-range lock state, directory lookup side-effect fields, directory hash pointer, and embedded `struct ufs1_dinode`.
- Provides field aliases from `i_din` to convenient inode names such as `i_size`, `i_mode`, `i_nlink`, direct/indirect block arrays, uid/gid, timestamps, generation, and block count.
- Defines inode flags for access/change/update/modified state, rename, shared/exclusive lock markers, hash membership, lazy modification, and special no-copy-write behavior.
- Defines `struct indir` for logical block path calculations used by truncate and bmap code.
- Defines `VTOI()` and `ITOV()` conversion macros.
- Defines `DOINGSOFTDEP()` and `DOINGASYNC()` mount-flag checks.
- Defines `struct ufid`, the UFS file-handle payload used for NFS/exported file handle conversion.

Dependencies:
- Includes `dinode.h` and queue definitions; kernel builds include lock and lockf headers.
- References `struct fs`, `struct vnode`, `cdev_t`, quota structures, and directory hash state.

Notable risks:
- `struct inode` is central in-core filesystem state; alias macros mean changes to `ufs1_dinode` fields directly affect most UFS code.
- `i_effnlink` is important for softdep delayed link-count semantics and must be kept consistent with `i_nlink` and `inodedep` state.
- Comments note `i_spare` is not truly spare for ext2fs, so shared ancestry with other filesystems constrains changes.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/quota.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/quota.h

UFS quota ABI and kernel dquot interface header. It defines user/group quota constants, quotactl command encoding, on-disk quota records, kernel quota cache records, and quota operation prototypes.

Key responsibilities:
- Defines default soft-limit grace periods for inode and disk-block quotas.
- Defines two quota slots, `USRQUOTA` and `GRPQUOTA`, and default quota file naming conventions.
- Defines `QCMD()` encoding and command values for quota on/off, get quota, set quota, set usage, and sync.
- Defines `struct ufs_dqblk`, the on-disk quota record containing hard/soft block limits, current blocks, hard/soft inode limits, current inodes, and block/inode grace expiry times.
- Under `_KERNEL`, defines `struct ufs_dquot` cache entries with hash/free-list links, flags, type, refcount, id, mount pointer, and embedded quota data.
- Defines dquot flags for locking/wakeup/modified/fake/warned states and shorthand field aliases.
- Defines `NODQUOT`, `FORCE`, `CHOWN`, and `DQREF()` behavior.
- Declares kernel quota functions for allocation checks, initialization, release, inode quota lookup, get/set/use, on/off, sync, and quotactl dispatch.
- Declares userland `quotactl()` when not compiling the kernel.

Dependencies:
- Includes `ufs_types.h`.
- Kernel portion uses queue types and forward declarations for inode, mount, process/thread, credentials, vnode, and ufsmount.

Notable risks:
- `struct ufs_dqblk` is on-disk quota-file format; field width/order changes would break existing quota files.
- Kernel and userland share command encoding, so ABI compatibility matters.
- Quota file vnode arrays in `ufsmount` and inode dquot arrays are sized by `MAXQUOTAS`; increasing quota types affects multiple structures and lookup semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/ufs/quota.h -->