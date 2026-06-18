# Group Research: group_1414_openbsd_src_sources_os_bsd_openbsd_src_sys_ufs_ffs_ffs_vnops_c_sour_7e3cf2d362ff

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/openbsd-src` source tree. All 22 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vnops.c

Read completely: 545 lines.

Defines FFS vnode operation vectors and implements FFS-specific regular-file I/O, fsync, and inode reclaim.

Core behavior:
- `ffs_vops`, `ffs_specvops`, and optional `ffs_fifovops` bind generic UFS directory/metadata operations to FFS read/write/fsync/reclaim behavior, plus special-device and FIFO wrappers.
- `ffs_read()` validates offsets/types, reads logical file blocks with `bread()` or clustered read-ahead, clamps transfers to file size and residual I/O, and marks access time unless `MNT_NOATIME` suppresses it.
- `ffs_write()` enforces append-only and max-file-size/rlimit checks, allocates blocks through `UFS_BUF_ALLOC()`, extends vnode size, clears exposed buffer contents on failed partial `uiomove()`, chooses sync/async/delayed writes, clears setuid/setgid for unprivileged successful writes, and rolls back `IO_UNIT` writes by truncating to the original size.
- `ffs_fsync()` scans dirty vnode buffers under `splbio()`, skips metadata on the first synchronous pass, writes dirty buffers, waits for vnode I/O, retries dirty buffers for non-block devices, and finally calls `UFS_UPDATE()`.
- `ffs_reclaim()` delegates generic UFS cleanup, returns UFS1/UFS2 dinodes and inode objects to pools, and clears `v_data`; `ffsfifo_reclaim()` chains FIFO cleanup first.

Integration and risks:
- Depends on `inode.h` `DIP()` and vnode vtable indirection to support UFS1/UFS2.
- Buffer state flags and `splbio()` ordering are critical in `ffs_fsync()`.
- Write error cleanup is subtle because newly instantiated pages must not expose stale data through mmap.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/ffs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/fs.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ffs/fs.h

Read completely: 591 lines.

Defines the on-disk and in-memory FFS superblock/cylinder-group layout plus address, size, fragment, and geometry macros used by FFS and UFS code.

Core definitions:
- Declares boot/superblock locations and search offsets, block/fragment limits, mount and volume name sizes, default free-space and allocation tuning constants, snapshot reservation count, and clean/flag magic values.
- `struct fs` is the FFS superblock, containing geometry, block/fragment sizing, cylinder group layout, summary counters, mount metadata, compatibility fields, UFS1/UFS2 extended state, flags, max file size, and embedded variable layout data.
- `struct cg` and legacy `struct ocg` describe cylinder-group headers, free maps, inode maps, rotational summaries, cluster summaries, and compatibility layout.
- Provides macros for summary access, cylinder-group address calculation, inode-to-block mapping, block/fragments conversions, offsets/rounding, available-space calculation, block size at logical block, sectors per block/fragment, indirect count, and kernel max file size.

Integration and risks:
- This is a filesystem ABI header; structure field order and exact widths are part of on-disk compatibility.
- Many macros assume power-of-two block/fragment sizes and valid superblock-derived masks/shifts.
- `blksize()`, `dblksize()`, and `sblksize()` are relied on by read/write/truncate paths to avoid over-reading partial final fragments.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ffs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_extern.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_extern.h

Read completely: 64 lines.

Declares the public MFS interfaces used across the memory filesystem implementation.

Core definitions:
- Forward-declares kernel structures used by MFS VFS and vnode operations.
- Exposes `mfs_vops`.
- Declares VFS hooks: `mfs_mount()`, `mfs_start()`, `mfs_init()`, and `mfs_checkexp()`.
- Declares vnode/device hooks: `mfs_open()`, `mfs_ioctl()`, `mfs_strategy()`, `mfs_doio()`, `mfs_close()`, `mfs_inactive()`, `mfs_reclaim()`, and `mfs_print()`.

Integration and risks:
- MFS is implemented as an FFS filesystem backed by a synthetic block vnode, so these prototypes connect VFS mount setup to block-device strategy handling.
- `mfs_doio()` is the central data mover and must match `mfsnode` layout.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vfsops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vfsops.c

Read completely: 222 lines.

Implements MFS VFS operations by mounting an FFS instance over a kernel vnode whose backing store is a user-process memory region.

Core behavior:
- `mfs_vfsops` reuses many FFS/UFS operations: unmount, root, quota, statfs, sync, vget, file-handle conversion, sysctl, and generic UFS root/export helpers where appropriate.
- `mfs_mount()` handles update mounts, read-only transitions, optional export update, creates a `VT_MFS` block vnode, assigns a synthetic device number, allocates `struct mfsnode`, records memory base/size and servicing thread id, initializes the buffer queue, then calls `ffs_mountfs()`.
- After mount, it fills `fs_fsmnt`, `mnt_stat.f_mntonname`, `f_mntfromname`, `f_mntfromspec`, and stored MFS args.
- `mfs_start()` keeps the mounting process in-kernel as an I/O server: drains queued buffers through `mfs_doio()`, sleeps on the device vnode, and on signals tries to unmount, forcing only for `SIGKILL`.
- `mfs_checkexp()` rejects exports with `EOPNOTSUPP`; `mfs_init()` delegates to `ffs_init()`.

Integration and risks:
- The filesystem lives only while the server process and memory mapping are valid.
- Signal/unmount handling is delicate; failed unmounts clear the pending signal to avoid spinning.
- Duplicate synthetic device aliases panic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vnops.c

Read completely: 263 lines.

Implements vnode operations for the synthetic MFS block device used as backing storage for an FFS filesystem.

Core behavior:
- `mfs_vops` rejects normal filesystem operations with generic badops and provides open, close, ioctl, strategy, inactive, reclaim, print, and generic bmap/bwrite behavior.
- `mfs_strategy()` validates a block vnode, then either services I/O directly if called by the MFS server thread or queues the buffer and wakes the server.
- `mfs_doio()` clamps I/O to the memory filesystem size, translates block number to memory offset, copies data with `copyin()` for reads and `copyout()` for writes, sets `B_ERROR`/`b_resid`, and completes the buffer with `biodone()` under `splbio()`.
- `mfs_close()` drains queued buffers, invalidates in-core buffers with `vinvalbuf()`, marks shutdown, and wakes the server.
- `mfs_inactive()` unlocks the vnode; `mfs_reclaim()` destroys the buffer queue, frees the mfsnode, and clears vnode data.

Integration and risks:
- The apparent block device is backed by user address space, so copy direction and bounds are central.
- Direct self-I/O avoids deadlock when the server thread issues I/O against its own device.
- Shutdown requires queue draining before invalidation and reclaim.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfsnode.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfsnode.h

Read completely: 53 lines.

Defines the in-core state for an MFS backing device.

Core definitions:
- `struct mfsnode` stores the associated vnode, FIFO buffer queue, base user address, filesystem size, servicing thread id, an unused/legacy buffer-list pointer, and shutdown flag.
- `VTOMFS()` and `MFSTOV()` convert between vnode and mfsnode pointers.

Integration and risks:
- `mfs_baseoff`, `mfs_size`, and `mfs_tid` are consumed directly by strategy and I/O paths.
- Queue lifetime is owned by vnode reclaim, so close/reclaim ordering must keep pending buffers from referencing freed state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/mfs/mfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dinode.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dinode.h

Read completely: 156 lines.

Defines UFS inode-number types, root inode constants, UFS1/UFS2 on-disk inode formats, short-link/device overlays, and file mode/type constants.

Core definitions:
- `ufsino_t` is a 32-bit inode number; `ROOTINO` is inode 2.
- `NXADDR`, `NDADDR`, and `NIADDR` define external, direct, and indirect address counts.
- `struct ufs1_dinode` stores mode, link count, old id/inumber union, size, 32-bit timestamps, 32-bit direct/indirect block addresses, flags, block count, generation, uid/gid, and spare fields.
- `struct ufs2_dinode` stores wider uid/gid, block size, size, block count, 64-bit timestamps, birth time, generation, kernel/user flags, external attribute blocks, 64-bit direct/indirect block addresses, and spare fields.
- Defines overlays for device numbers and short symlinks, per-format max symlink lengths, permission bits, and file type bits.

Integration and risks:
- Exact field widths and positions are on-disk ABI.
- `MAXSYMLINKLEN()` depends on mount filesystem type.
- `di_rdev` and short symlink overlays reuse block address fields, so type-specific interpretation is required.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dir.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dir.h

Read completely: 134 lines.

Defines UFS directory entry format and helper macros.

Core definitions:
- `doff_t` is a 32-bit directory offset, with `MAXDIRSIZE` capped near 2 GB.
- `DIRBLKSIZ` is `DEV_BSIZE`; entries are variable-length records inside fixed directory blocks.
- `struct direct` contains inode number, record length, type, name length, and a null-terminated name buffer up to `MAXNAMLEN`.
- Defines directory file type constants and conversion macros `IFTODT()` and `DTTOIF()`.
- `DIRECTSIZ()` and `DIRSIZ()` compute record sizes rounded to 4-byte boundaries.
- `struct dirtemplate` provides the packed `"."` and `".."` layout used for new directories and parent checks.

Integration and risks:
- Deletion and insertion rely on `d_reclen` absorbing free space.
- Directory readers must validate record lengths to avoid infinite loops and malformed entry exposure.
- The kernel tolerates some noncanonical free entries created by fsck.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dirhash.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/dirhash.h

Read completely: 132 lines.

Declares the optional UFS directory hash accelerator used for large directories.

Core definitions:
- Uses open addressing with `DIRHASH_EMPTY` and `DIRHASH_DEL` sentinels and a two-level hash array of directory offsets.
- Tracks per-directory-block free space in `dh_blkfree` and first-free indexes by free-space size to speed creation.
- `struct dirhash` contains its rwlock, hash arrays, slot counts, free-space summaries, sequential lookup optimization state, recycling score, list membership, and global LRU/LFU list linkage.
- Exposes tunables `ufs_mindirhashsize`, `ufs_dirhashmaxmem`, and `ufs_dirhashmem`.
- Declares build, lookup, insert, remove, move, new-block, truncate, free, and consistency-check routines.

Integration and risks:
- Hash memory can be recycled independently from the inode pointer, requiring callers to detect `dh_hash == NULL` and rebuild/fallback.
- Lock ordering is global dirhash list lock before per-dirhash lock.
- Directory mutation paths must keep free-space summaries and offset hashes synchronized.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/dirhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/inode.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/inode.h

Read completely: 344 lines.

Defines the in-core UFS inode, filesystem-specific vtable hooks, dinode access macros, inode flags, indirect-block path structure, vnode conversions, and file-handle layout.

Core definitions:
- `struct inode` stores hash linkage, vnode, mount, flags, device/inode identity, effective link count, FFS/ext2 filesystem pointer, cluster info, quota pointers, NFS revision, lock state, inode rwlock, directory lookup side-effect fields, extension union for ext2 or dirhash, dinode pointer union, and operation vtable.
- `struct inode_vtbl` abstracts filesystem-specific truncate, update, inode allocation/free, buffer allocation, and buffer-at-offset operations.
- `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_INODE_ALLOC`, `UFS_INODE_FREE`, `UFS_BUF_ALLOC`, and `UFS_BUFATOFF` dispatch through that vtable.
- Defines UFS1/UFS2/ext2 field aliases and `DIP()`/`DIP_ASSIGN()`/`DIP_ADD()`/`DIP_AND()`/`DIP_OR()` for UFS1/UFS2 field selection.
- Defines inode flags for pending timestamp updates, modification, rename, locks, lazy modification, and hash membership.
- `struct indir` carries logical indirect-block paths for bmap/truncate; `struct ufid` overlays file handles.

Integration and risks:
- `DIP()` does not cover ext2, so callers must special-case ext2 where needed.
- Directory lookup writes state into the inode (`i_offset`, `i_count`, etc.), so callers must preserve locking assumptions.
- `i_effnlink` intentionally differs from on-disk link count during pending directory operations.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/quota.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/quota.h

Read completely: 149 lines.

Defines UFS quota constants, quotactl commands, on-disk quota record format, flags, and kernel quota APIs.

Core definitions:
- Supports two quota types: user and group, with default one-week soft-limit grace times.
- Defines quota command encoding with `QCMD()`, including quota on/off, get, set, set-use, and sync.
- `struct dqblk` is the quota-file record: hard/soft block limits, current blocks, hard/soft inode limits, current inodes, and block/inode grace-expiration times.
- Kernel flags let callers skip uid/gid accounting or force changes without limit checks.
- Declares quota accounting, quota deletion, quota file control, sync, and initialization functions; when quota is disabled, matching stubs are provided elsewhere.

Integration and risks:
- The `dqblk` timestamps are 32-bit and explicitly carry a 2038 concern.
- `MAXQUOTAS` is baked into inode and mount arrays.
- Accounting callers depend on matching allocation/free semantics during ownership changes and rollback.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_bmap.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_bmap.c

Read completely: 308 lines.

Implements logical-to-physical block mapping and indirect-block path generation for UFS/FFS files.

Core behavior:
- `ufs_bmap()` returns the underlying device vnode when requested and maps a logical block through `ufs_bmaparray()`.
- `ufs_bmaparray()` handles direct blocks from dinode direct pointers, indirect blocks through negative logical block numbers, cached or on-disk indirect block reads, UFS1/UFS2 pointer width selection, and optional sequential run-length detection for clustered I/O.
- Missing data or indirect mappings are reported as `-1`.
- `ufs_getlbns()` computes the chain of indirect blocks and offsets needed for a data block or metadata block, supporting single, double, and triple indirection, and rejects too-large logical blocks with `EFBIG`.

Integration and risks:
- Indirect metadata logical block numbering is negative and must match truncate/allocation code.
- Cached dirty indirect blocks can satisfy mapping before disk writeback.
- UFS1 and UFS2 pointer sizes are selected at runtime through mount type.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_dirhash.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_dirhash.c

Read completely: 1064 lines.

Implements the optional hash-based lookup and free-space index for large UFS directories.

Core behavior:
- `ufsdirhash_build()` decides whether a directory should be hashed, enforces global memory limits, allocates hash/free-space structures, scans directory entries with `UFS_BUFATOFF()`, inserts live entries, and accounts free record space.
- `ufsdirhash_lookup()` looks up a name by SipHash slot, supports sequential-access optimization, validates offsets and directory records, returns the containing buffer and optional previous-entry offset, and falls back to linear lookup on corrupt or recycled state.
- `ufsdirhash_findfree()` uses free-space summaries to locate a block/range suitable for a new entry; `ufsdirhash_enduseful()` identifies trailing empty directory blocks.
- Mutation helpers `ufsdirhash_add()`, `remove()`, `move()`, `newblk()`, and `dirtrunc()` keep hash slots and free-space statistics in sync with directory changes.
- `ufsdirhash_checkblock()` optionally verifies hash state against an on-disk directory block.
- Recycling uses a score-based global list: `ufsdirhash_recycle()` detaches and frees backing arrays from low-score dirhashes while leaving stubs for later rebuild.
- Initialization sets pool state, locks, random SipHash key, default max memory, and minimum directory size.

Integration and risks:
- Locking order is global `ufsdirhash_mtx` before per-dirhash `dh_mtx`.
- Callers must tolerate `dh_hash == NULL` after recycling.
- Incorrect free-space accounting can corrupt create/compact paths.
- Directory corruption causes fallback where possible, but some internal mismatches panic.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_extern.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_extern.h

Read completely: 132 lines.

Declares exported UFS vnode, VFS, inode-cache, inode-lifecycle, lookup, bmap, quota-adjacent, special-device, FIFO, and helper functions.

Core definitions:
- Lists vnode operation entry points for access, create, mknod, open/close, attributes, directory operations, symlink/readlink, strategy, locking, pathconf, advisory locks, kqueue filter, and special/FIFO wrappers.
- Declares block mapping helpers `ufs_bmaparray()` and `ufs_getlbns()`.
- Declares inode hash lifecycle: initialization, lookup, insert, and remove.
- Declares generic inactive/reclaim and directory manipulation helpers.
- Declares generic VFS hooks such as start, root, quotactl, file-handle conversion, and export checks.
- Declares `ufs_itimes()` and `ufs_makeinode()` used by filesystem-specific vnode implementations.

Integration and risks:
- This header is the cross-module contract tying FFS, MFS, ext2-adjacent code, and generic UFS routines together.
- Signature drift here would break vnode/VFS operation vectors.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_ihash.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_ihash.c

Read completely: 194 lines.

Implements the global in-core inode hash table keyed by device and inode number.

Core behavior:
- `ufs_ihashinit()` allocates the hash table sized from `initialvnodes` and seeds a SipHash key.
- `ufs_ihash()` hashes `(dev, ino)` using SipHash24.
- `ufs_ihashget()` searches for a matching inode, locks/references its vnode via `vget()`, retries on vnode recycle races, and rejects inodes being reclaimed or invalidated, including an ext2-specific nlink check.
- `ufs_ihashins()` locks the vnode, detects duplicate device/inode pairs, sets `IN_HASHED`, and inserts the inode.
- `ufs_ihashrem()` removes hashed inodes and clears diagnostics pointers.

Integration and risks:
- Comments flag missing/unfinished hash-list locking; correctness depends on broader vnode serialization assumptions.
- `ufs_ihashget()` contains an explicit workaround for grabbing a vnode while inactive/reclaim is in progress.
- Duplicate insert returns `EEXIST` after unlocking the new vnode.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_ihash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_inode.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_inode.c

Read completely: 152 lines.

Implements generic UFS inode inactive and reclaim processing.

Core behavior:
- `ufs_inactive()` handles last-reference processing: ignores stale/zero-mode inodes, frees quota/inode resources and truncates data for unlinked writable inodes, clears mode/rdev, frees the on-disk inode through vtable dispatch, updates pending timestamps, unlocks the vnode, and recycles immediately when the inode is invalid.
- `ufs_reclaim()` stops lazy timestamp deferral, removes the inode from the global hash, purges namecache entries, releases the device vnode, frees optional dirhash state, and releases quota references.

Integration and risks:
- Deletion relies on `i_effnlink`/on-disk nlink state and mount read-only status.
- Reclaim intentionally does not free the dinode/inode pools; filesystem-specific reclaim such as FFS does that after generic cleanup.
- Lazy-modified special devices must be updated before reclaim loses state.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_lookup.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_lookup.c

Read completely: 1073 lines.

Implements UFS pathname component lookup and directory entry mutation helpers.

Core behavior:
- `ufs_lookup()` validates directory access, handles read-only mutation rejection, consults the namecache, optionally builds/uses dirhash for large directories, falls back to linear scanning, records found entry metadata, tracks reusable free slots for CREATE/RENAME, and handles `LOOKUP`, `CREATE`, `DELETE`, and `RENAME` namei contracts.
- Lookup carefully handles `.` and `..`, parent locking, sticky directories, negative namecache entries, and the two-pass `i_diroff` optimization.
- `ufs_dirbad()` reports/panics on bad directories for writable filesystems; `ufs_dirbadentry()` validates record size, alignment, name length, and null termination.
- `ufs_makedirentry()` fills `struct direct` for a target inode and component name.
- `ufs_direnter()` writes new directory entries, either extending the directory with a fresh block or compacting existing free space, updates dirhash state, writes buffers synchronously, updates timestamps, and truncates trailing unused directory blocks when possible.
- `ufs_dirremove()` removes entries by zeroing first-in-block entries or merging record length into the previous entry; it decrements target link counts.
- `ufs_dirrewrite()` rewrites an existing entry to a new inode/type and decrements the old inode link count.
- `ufs_dirempty()` verifies only `.` and `..` remain; `ufs_checkpath()` walks `..` links to prevent moving a directory into its own subtree.

Integration and risks:
- Directory mutation depends on lookup-populated inode side effects (`i_offset`, `i_count`, `i_reclen`, `i_endoff`).
- Parent/child vnode lock ordering is central to avoiding deadlocks and rename races.
- Dirhash updates must mirror every entry move/remove/add.
- Corrupt directory records can panic on writable filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota.c

Read completely: 1100 lines.

Implements UFS disk quota accounting, quotactl operations, and the in-core dquot cache.

Core behavior:
- `struct dquot` caches quota-file records with hash linkage, free-list linkage, flags, type/id, reference count, quota vnode/credentials, and `dqblk` contents.
- `getinoquota()` attaches user and group dquots to an inode based on uid/gid when quotas are enabled.
- Block/inode allocation functions check hard and soft limits for non-root callers, start grace timers, emit user warnings, update usage, and mark dquots modified; free functions decrement usage and clear warning flags.
- `quotaon()` opens a quota file, records vnode/credentials, marks quota state opening, sets default grace times from id 0, attaches dquots to active writable vnodes, and rolls back on error.
- `quotaoff()` marks closing, detaches dquots from mounted vnodes, closes the quota vnode, releases credentials, and clears `MNT_QUOTA` when no quotas remain.
- `getquota()`, `setquota()`, and `setuse()` implement userland quota record fetch/update and ktrace reporting.
- `qsync()` walks vnodes and writes modified dquots.
- `dqget()` hashes by quota vnode and id, reuses free dquots or allocates new ones, reads quota records from the quota file, initializes fake/no-limit and grace-time state, and handles read errors.
- `dqrele()` syncs modified last references and moves unused dquots to the free list; `dqsync()` writes quota records under a dquot lock.
- `ufs_quotactl()` performs privilege checks, mount busy protection, command dispatch, and unbusy cleanup.

Integration and risks:
- Quota state uses ad hoc `DQ_LOCK`/`DQ_WANT` sleep locking; lost wakeups or missed flag clearing would stall accounting.
- Ownership changes in `ufs_chown()` rely on quota free/delete/reallocate rollback semantics.
- Quota file vnodes are marked system files and are accessed through normal vnode read/write paths, so recursion/locking around `dqvp` matters.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota_stub.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota_stub.c

Read completely: 71 lines.

Provides no-op quota symbols for kernels built without `QUOTA`.

Core behavior:
- `getinoquota()`, block/inode allocation/free accounting, `quotaoff()`, `qsync()`, quota initialization, and inode quota deletion all return success or do nothing.
- `ufs_quotactl()` returns `EOPNOTSUPP`.

Integration and risks:
- Keeps call sites unconditional while removing runtime quota behavior.
- Must stay signature-compatible with `quota.h` and `ufs_quota.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_quota_stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vfsops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vfsops.c

Read completely: 147 lines.

Implements generic UFS VFS helper operations shared by FFS/MFS-style filesystems.

Core behavior:
- `ufs_start()` is currently a no-op.
- `ufs_root()` fetches `ROOTINO` via `VFS_VGET()`.
- `ufs_check_export()` looks up network export credentials and returns export flags and anonymous credential.
- `ufs_init()` runs once, initializing inode hash, quota subsystem, and optional dirhash subsystem.
- `ufs_fhtovp()` converts UFS file handles to vnodes through `VFS_VGET()`, then validates mode and generation number before returning the vnode.

Integration and risks:
- `ufs_init()` is shared initialization and must be idempotent.
- File-handle validation depends on stable inode generation numbers to reject stale NFS handles.
- Export support is mount-specific through `ufsmount.um_export`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vnops.c -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vnops.c

Read completely: 1933 lines.

Implements generic UFS vnode operations for metadata, namespace mutation, directory reads, symlinks, locking, strategy I/O dispatch, special/FIFO wrappers, kqueue filters, and inode creation.

Core behavior:
- `ufs_itimes()` applies pending access/change/update timestamp flags, handles ext2 separately, marks lazy or modified state, updates nanosecond timestamps, and increments modification revision.
- Create/mknod/mkdir/symlink paths allocate inodes through vtable hooks, initialize uid/gid/mode/link counts, charge quotas, write inode state before directory entries, and update parent directories through `ufs_direnter()`.
- `ufs_open()`, `ufs_access()`, `ufs_getattr()`, and `ufs_setattr()` enforce append/immutable/read-only checks, expose inode metadata, perform truncation, timestamp updates, chmod/chown, and emit vnode notifications.
- `ufs_chown()` transfers quota usage from old uid/gid to new uid/gid with rollback on failure.
- `ufs_remove()`, `ufs_link()`, `ufs_rename()`, and `ufs_rmdir()` implement hard links and namespace removal/rename, including sticky directory checks, link-count staging, directory cycle prevention, `..` rewriting, target replacement, source relookup, cache purges, and error rollback.
- `ufs_readdir()` converts on-disk `struct direct` entries to userland `struct dirent`, avoids partial entries, validates record lengths and slash-free names, updates offsets/eof, and marks access time.
- `ufs_readlink()` serves short symlinks from inode block-pointer storage or delegates to `VOP_READ()` for long symlinks.
- `ufs_lock()`, `ufs_unlock()`, and `ufs_islocked()` wrap the inode `rrwlock`.
- `ufs_strategy()` maps logical buffers through `VOP_BMAP()`, clears holes, and sends real I/O to the device vnode.
- Special-device and FIFO wrappers mark inode timestamps before delegating to `spec_*` or `fifo_*`.
- `ufs_pathconf()` returns POSIX path limits and transfer alignment; `ufs_advlock()` delegates byte-range locks to `lf_advlock()`.
- `ufs_makeinode()` is the shared file/symlink inode creation helper.
- Kqueue support installs read/write/vnode filters and reports data availability, write readiness, vnode notes, and revoke EOF/oneshot state.

Integration and risks:
- Rename is the most complex path: it relies on staged extra link counts, `IN_RENAME`, `vfs_relookup()`, `ufs_checkpath()`, and careful vnode release/unlock behavior.
- Quota, link-count, and directory-entry updates must roll back coherently on write or allocation errors.
- `ufs_strategy()` depends on `ufs_bmap()` and buffer-cache hole semantics.
- Kqueue and timestamp side effects depend on every metadata mutation emitting the right `VN_KNOTE()` and inode flags.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufsmount.h -->
# File Research: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufsmount.h

Read completely: 94 lines.

Defines UFS-specific mount state and mount-level helper macros.

Core definitions:
- `struct ufsmount` stores the generic mount pointer, device id, device vnode, filesystem type, FFS/ext2 superblock pointer union, quota vnodes/credentials, indirect-pointer geometry, sequential block increment, quota grace times, quota flags, export data, saved max file size, and max short-symlink length.
- Defines mount filesystem type constants `UM_UFS1`, `UM_UFS2`, and `UM_EXT2FS`.
- Defines quota transition flags `QTF_OPENING` and `QTF_CLOSING`.
- `VFSTOUFS()` converts generic mount data to `struct ufsmount`.
- `MNINDIR()`, `blkptrtodb()`, and `is_sequential()` provide block mapping helpers used by bmap and clustered I/O.

Integration and risks:
- The superblock union and `um_fstype` drive UFS1/UFS2/ext2 field interpretation across the subsystem.
- Quota arrays must match `MAXQUOTAS`.
- Block pointer conversion macros assume mount geometry was initialized correctly at mount time.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sys/ufs/ufs/ufsmount.h -->