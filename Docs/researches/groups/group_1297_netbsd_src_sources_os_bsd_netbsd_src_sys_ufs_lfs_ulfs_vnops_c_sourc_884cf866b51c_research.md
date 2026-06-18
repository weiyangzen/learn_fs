# Group Research: group_1297_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_lfs_ulfs_vnops_c_sourc_884cf866b51c

Scope confirmed against `Docs/research_subset_a.md`: NetBSD source tree under subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vnops.c

This is the LFS/ULFS vnode operation implementation, derived from UFS vnode code but routed through LFS-specific inode state, directory accessors, allocation, truncation, and update paths.

Key responsibilities:
- Implements vnode operations for open, access, setattr, remove, link, whiteout, rmdir, readdir, readlink, print, pathconf, advisory locks, special-device wrappers, FIFO wrappers, vnode initialization, GOP allocation/update helpers, and buffer I/O.
- Enforces append-only, immutable, snapshot, read-only mount, ownership, chmod/chown, timestamp, and kauth authorization rules.
- Uses LFS-specific paths such as `lfs_update`, `lfs_truncate`, `lfs_balloc`, `lfs_bufrd`, and `lfs_bufwr` rather than generic FFS/UFS writeback paths.
- Converts on-disk `LFS_DIRHEADER` directory records into userspace `struct dirent` entries in `ulfs_readdir`, including optional directory cookies.
- Handles short symlink reads directly from inode block-pointer storage, preserving the historical off-by-one compatibility behavior around `um_maxsymlinklen`.
- Integrates optional LFS quota accounting during access checks and ownership changes.

Important implementation notes:
- Directory mutation state is still stashed in inode lookup scratch fields (`i_crap`) between lookup and operation calls.
- `ulfs_chown` removes quota usage from the old owner, applies uid/gid changes, then rolls back if quota recharging fails.
- `ulfs_link`, `ulfs_remove`, `ulfs_rmdir`, and `ulfs_whiteout` update link counts and directory entries through ULFS directory helpers.
- `ulfs_gop_alloc` updates EOF incrementally because `lfs_balloc` requires the current file size before each allocation.
- `ulfs_vinit` installs special-device or FIFO vnode ops based on inode mode and initializes device aliases with byte-swapped `rdev` handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfsmount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfsmount.h

This header defines the ULFS-specific mount-private structure used by LFS’s UFS-derived layer.

Key contents:
- Defines `struct ulfsmount`, storing the backing `struct mount`, filesystem type, `struct lfs *`, extended-attribute state, and quota state.
- Supports quota1 and quota2 through a union of per-mount quota timers/flags or quota2 block-size metadata.
- Defines ULFS mount flags such as `ULFS_NEEDSWAP`, `ULFS_QUOTA`, and `ULFS_QUOTA2`.
- Defines filesystem type constants `ULFS1` and `ULFS2`.
- Provides `VFSTOULFS(mp)` and block-mapping helper macros `MNINDIR` and `blkptrtodb`.

Role:
- Central mount bridge for ULFS vnode, quota, byte-swap, bmap, and extended-attribute code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/lfs/ulfsmount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/Makefile

This kernel include makefile installs public MFS headers.

Key contents:
- Sets `INCSDIR` to `/usr/include/ufs/mfs`.
- Installs `mfs_extern.h` and `mfsnode.h`.
- Includes `bsd.kinc.mk`.

Role:
- Build-system glue only; no runtime filesystem logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_extern.h

This header declares the external MFS VFS and vnode operation interface.

Key contents:
- Declares `VFS_PROTOS(mfs)`.
- Declares `mfs_initminiroot`.
- Declares vnode operations including `mfs_open`, `mfs_strategy`, `mfs_bmap`, `mfs_close`, `mfs_inactive`, `mfs_reclaim`, `mfs_print`, and `mfs_fsync`.
- Declares `mfs_doio`, the core buffer-to-memory transfer helper.
- Under `_KERNEL`, exposes global `mfs_lock`, `mfs_rootbase`, and `mfs_rootsize`.

Role:
- Public kernel header connecting MFS mount code, vnode operation code, and miniroot setup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_miniroot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_miniroot.c

This file initializes an in-kernel MFS miniroot early in boot.

Key behavior:
- Defines global `mfs_rootbase` and `mfs_rootsize`.
- `mfs_initminiroot(void *base)` validates a UFS1 superblock at `base + SBLOCK_UFS1`.
- Rejects invalid magic, invalid block size, or too-small superblock.
- Sets `rootfstype = MOUNT_MFS`, records root memory base/size, and sets synthetic `rootdev = makedev(255, 0)`.
- Panics if called more than once.

Role:
- Boot-time bridge from a memory-resident filesystem image to an MFS root device mount.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_miniroot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vfsops.c

This file implements the MFS VFS layer. MFS presents a memory range as a synthetic block device, then mounts FFS over it.

Key responsibilities:
- Registers `mfs_vfsops` as a VFS module depending on FFS.
- Initializes, reinitializes, and tears down global MFS state and FFS support.
- Implements `mfs_mountroot` for miniroot boot mounting.
- Implements `mfs_mount` for normal MFS mounts from user-provided base/size arguments.
- Implements `mfs_start`, the service loop that processes queued buffer I/O for the memory-backed block vnode.
- Implements `mfs_statvfs` by delegating to FFS and overriding filesystem type name.

Important behavior:
- Normal mounts allocate synthetic block device minor numbers under major 255.
- MFS disables async and forces synchronous mounting to avoid memory-pressure deadlocks where cleaning pages requires allocating pages.
- `mfs_start` holds an extra `mfsnode` reference, drains its buffer queue, handles signals by attempting unmount, and exits on `mfs_shutdown`.
- Root MFS uses `mfs_proc == NULL` to indicate kernel-space miniroot memory rather than userspace-backed memory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vnops.c

This file implements vnode operations for the MFS synthetic block vnode.

Key responsibilities:
- Defines the `mfs_vnodeop_entries` table.
- Implements `mfs_open`, validating block vnode use.
- Implements `mfs_strategy`, routing buffers either directly to kernel miniroot memory, to the current MFS server process, to shutdown bitbucket behavior, or into the queued buffer list.
- Implements `mfs_doio`, copying between buffer data and the MFS backing address using `copyin`/`copyout`.
- Implements identity `mfs_bmap`.
- Implements `mfs_close`, draining pending I/O, invalidating buffers, and signaling shutdown.
- Implements inactive, reclaim, and print helpers.

Important behavior:
- If `mfs_proc == curproc`, I/O is handled directly to avoid deadlock through the queue.
- During shutdown, writes are discarded and reads warn.
- Lifetime is protected by `mfs_refcnt`; final reclaim/start-loop exit frees the queue, condition variable, and node.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfsnode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfsnode.h

This header defines MFS per-device state.

Key contents:
- `struct mfsnode` stores associated vnode, backing memory base, memory size, servicing process, shutdown flag, condition variable, reference count, and buffer queue.
- Defines `VTOMFS(vp)` and `MFSTOV(mfsp)` conversion macros under `_KERNEL`.

Role:
- Control object binding a synthetic block vnode to a memory range and service loop.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/mfs/mfsnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/Makefile

This kernel include makefile installs public UFS headers.

Key contents:
- Sets `INCSDIR` to `/usr/include/ufs/ufs`.
- Installs disk-format, directory, extattr, inode, quota, byte-swap, extern, WAPBL, and mount headers.
- Includes `bsd.kinc.mk`.

Role:
- Build-system glue for exporting UFS kernel headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/acl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/acl.h

This header declares UFS ACL support.

Key contents:
- Declares internal NFSv4 ACL get/set helpers.
- Declares POSIX.1e ACL set helper.
- Declares ACL/mode synchronization helpers between inode mode bits and ACL entries.
- Under `UFS_ACL`, maps vnode ACL operations to real functions.
- Without `UFS_ACL`, maps ACL operations to `genfs_eopnotsupp`.

Role:
- Compile-time switch and function surface for UFS POSIX.1e and NFSv4 ACL integration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dinode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dinode.h

This header defines UFS on-disk inode formats and file mode constants.

Key contents:
- Defines `UFS_ROOTINO` as inode 2 and `UFS_WINO` as whiteout inode 1.
- Defines direct/indirect pointer counts: `UFS_NDADDR`, `UFS_NIADDR`, and UFS2 external attribute pointer count `UFS_NXADDR`.
- Defines `struct ufs1_dinode` and `struct ufs2_dinode`.
- Defines short symlink capacities for UFS1 and UFS2.
- Defines permission and file type mode constants.
- Defines on-disk inode sizes.

Important distinction:
- UFS1 stores 32-bit block pointers and legacy uid/gid compatibility fields.
- UFS2 stores 64-bit block pointers, birthtime, external attribute block metadata, and larger block accounting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dinode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dir.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dir.h

This header defines UFS directory entry layout and directory-format compatibility macros.

Key contents:
- Defines `struct direct` with inode number, record length, type, name length, and name.
- Defines directory block size, max name length, Apple UFS directory block size, and directory file type values.
- Defines `IFTODT` and `DTTOIF` conversions.
- Defines record sizing and padding macros.
- Defines old/new directory format constants `UFS_OLDDIRFMT` and `UFS_NEWDIRFMT`.
- Defines `struct dirtemplate` and `struct odirtemplate` for `.`/`..` directory creation.

Important compatibility note:
- Old-format directories lack `d_type`; the macro logic compensates for byte order and the old-format namelen/type overlap.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dir.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dirhash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/dirhash.h

This header defines the in-memory UFS directory hash accelerator.

Key contents:
- Defines empty/deleted slot markers for open-addressed hash tables.
- Defines hash scoring constants used for recycling.
- Defines two-level hash array layout constants.
- Defines `struct dirhash`, containing hash slots, per-directory-block free-space summaries, sequential lookup optimization state, score, and global list linkage.
- Declares build, lookup, add/remove/move, truncation, checking, init, and teardown functions.

Role:
- Speeds up large-directory lookup and free-space discovery while allowing memory-pressure recycling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/dirhash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/extattr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/extattr.h

This header defines UFS extended attribute constants, formats, and kernel state.

Key contents:
- Defines backing file magic/version and `.attribute/system` / `.attribute/user` directory names.
- Defines per-attribute file header and per-inode attribute header.
- Defines generic packed `struct extattr` and traversal/content macros.
- Defines `struct ufs_extattr_list_entry` for each enabled attribute backing file.
- Defines `struct ufs_extattr_per_mount` for per-mount state, recursive lock count, credentials, and enabled-attribute list.
- Declares extattr start/autostart/stop/control and vnode get/set/delete/list functions.

Role:
- Provides UFS1-style extended attributes by mapping attribute names to backing files rather than changing the main inode format.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/inode.h

This header defines the in-core UFS inode and supporting metadata.

Key contents:
- Defines `struct ufs_lookup_results`, used to carry lookup side effects into directory mutation operations.
- Defines per-filesystem inode extensions for FFS, ext2fs, and LFS.
- Defines `struct inode`, including genfs node, vnode, mount, device vnode, inode number, filesystem union, quotas, modrev, locks, directory lookup scratch state, dirhash, extended attribute transaction fields, cached inode metadata, and on-disk dinode pointers.
- Provides aliases for UFS1 and UFS2 dinode fields.
- Defines inode state flags such as `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, `IN_MODIFIED`, and `IN_SPACECOUNTED`.
- Provides `DIP`, `DIP_ASSIGN`, `DIP_ADD`, `SHORTLINK`, `VTOI`, and `ITOV`.
- Defines `struct indir` for indirect block traversal and `struct ufid` for file handles.

Role:
- Central in-memory representation shared by UFS, FFS, LFS-derived ULFS, and ext2fs-adjacent code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota.h

This header defines quota constants common to quota1 and quota2.

Key contents:
- Defines two quota slots: user and group.
- Defines quota name initializer strings.
- Provides conversion helpers between generic quota id types and UFS quota slots.
- Declares quota subsystem init/reinit/done functions under `_KERNEL`.

Role:
- Common quota vocabulary used by both legacy quota files and newer metadata-backed quotas.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1.h

This header defines the original deprecated UFS disk quota format.

Key contents:
- Defines default soft-limit grace periods for block and inode quotas.
- Defines legacy quota filename and group.
- Defines old `quotactl` command encoding and commands.
- Defines `struct dqblk`, the on-disk quota1 record indexed by uid/gid.
- Declares conversion helpers between `dqblk` and generic `quotaval` pairs.

Role:
- Compatibility support for legacy quota files with 32-bit counters and limits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1_subr.c

This file converts between legacy quota1 records and generic quota values.

Key behavior:
- Treats quota1 limit value `0` as unlimited and otherwise stores `limit + 1` style values.
- `dqblk_to_quotavals` converts block and file quotas from `struct dqblk` into `struct quotaval`.
- `quotavals_to_dqblk` converts generic block/file quota values back to quota1 records.
- Notes unresolved handling of `qv_grace`.

Role:
- Thin compatibility adapter for old quota format consumers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota1_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2.h

This header defines the newer UFS quota2 on-disk metadata format.

Key contents:
- Defines `struct quota2_val` for hard/soft limits, current usage, expiry, and grace time.
- Defines quota value classes `QL_BLOCK` and `QL_FILE`.
- Defines `struct quota2_entry`, storing block/file values plus linked-list and uid data.
- Defines `struct quota2_header`, including magic, quota type, hash table sizing, default entry, free list head, and variable hash heads.
- Defines superblock flags for enabled quota2 types.
- Defines offset/index conversion macros.
- Declares quota2 block creation, free-list setup, byte-swap helpers, and limit checking.

Role:
- Metadata-integrated quota implementation intended to be fsck- and journal-visible.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2_subr.c

This file provides quota2 format construction, byte swapping, and limit checking.

Key behavior:
- `quota2_addfreeq2e` adds all quota entries in a block to the free list.
- `quota2_create_blk0` initializes the quota2 header block, hash table, unlimited default limits, and seven-day grace defaults.
- `quota2_ufs_rwq2v` and `quota2_ufs_rwq2e` byte-swap quota values and entries.
- `quota_check_limit` returns allow/deny status for soft/hard limit enforcement and indicates soft-limit crossings.

Role:
- Shared helper code for kernel and tooling that understands quota2 layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/quota2_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_acl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_acl.c

This file implements UFS POSIX.1e and NFSv4 ACL support on top of extended attributes and inode mode bits.

Key responsibilities:
- Synchronizes POSIX ACL entries from inode mode and inode mode from ACL entries.
- Retrieves NFSv4 ACLs from extended attributes, falling back to mode-derived trivial ACLs when absent.
- Retrieves POSIX.1e ACLs from old ACL extended attributes, synthesizing access ACLs from inode mode when absent.
- Sets NFSv4 ACLs, removing trivial ACL attributes and updating inode mode from ACL semantics.
- Sets or deletes POSIX.1e ACLs, storing old ACL format in extended attributes and updating inode mode for access ACLs.
- Validates POSIX.1e and NFSv4 ACLs for vnode operations.

Important behavior:
- Corrupt or wrong-sized ACL extended attributes are treated as protection failures and return `EPERM`.
- NFSv4 ACL set checks reserve space for chmod-driven entry splitting and canonical entries.
- POSIX.1e access ACL updates are non-atomic with respect to extended attribute and inode mode changes.
- ACL updates use WAPBL transactions around inode mode updates.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_acl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bmap.c

This file maps UFS logical file blocks to physical disk blocks.

Key responsibilities:
- Implements `ufs_bmap`, returning the underlying device vnode and physical block number.
- Implements `ufs_bmaparray`, traversing direct, external-attribute, single-, double-, and triple-indirect block pointers.
- Implements run-length detection for sequential physical blocks.
- Handles holes by returning `-1`.
- Handles snapshots specially, returning zero-fill behavior for snapshot marker block ranges.
- Implements `ufs_getlbns`, computing the chain of logical metadata block numbers and offsets needed to reach a data block.

Important behavior:
- Uses `ufs_rw32`/`ufs_rw64` and mount byte-swap state for UFS1/UFS2 pointer reads.
- Reads indirect blocks as buffers attached to the file vnode using negative logical block numbers.
- Supports UFS2 external attribute blocks through negative block numbers in the `-1 .. -UFS_NXADDR` range.
- Stops traversal early if an indirect block has no disk address and is not cached.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bswap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bswap.h

This header provides UFS endian-conversion helpers.

Key contents:
- Defines mount/filesystem/inode byte-swap predicates when `FFS_EI` is enabled.
- Provides inline `ufs_rw16`, `ufs_rw32`, and `ufs_rw64`.
- In non-swapping builds, helpers return inputs unchanged.
- Defines add-and-reswap helpers `ufs_add16`, `ufs_add32`, and `ufs_add64`.

Role:
- Centralizes endian-independent access for UFS metadata and quota/extattr support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_dirhash.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_dirhash.c

This file implements the UFS large-directory hash cache.

Key responsibilities:
- Builds per-directory hash tables from directory contents.
- Performs hashed lookup with fallback to linear lookup via `EJUSTRETURN`.
- Finds free directory space quickly using per-block free-space summaries.
- Tracks useful directory end for truncating trailing unused blocks.
- Updates hash state on directory entry add, remove, move, new block, and truncation.
- Provides optional consistency checks against real directory block contents.
- Recycles dirhash memory under configurable global memory limits.
- Exposes sysctls for minimum blocks, max memory, used memory, and consistency checking.

Important behavior:
- Uses open addressing with `DIRHASH_EMPTY` and `DIRHASH_DEL`.
- Uses a score-based hybrid recency/frequency recycling algorithm.
- Avoids hashing old-format directories, removed directories, small directories, and configurations with no memory budget.
- If a hash is recycled, its structure may remain but `dh_hash` becomes `NULL`, causing callers to free/rebuild or fall back.
- Build allocation is non-blocking where possible so lookup can fall back rather than stall indefinitely.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_dirhash.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extattr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extattr.c

This file implements UFS extended attributes using per-attribute backing files.

Key responsibilities:
- Manages per-mount extended attribute state and recursive mount-level locking.
- Autostarts attributes from `.attribute/system` and `.attribute/user`.
- Enables/disables attributes by opening backing vnodes and validating file headers.
- Autocreates backing files for supported namespaces when setting an unknown attribute.
- Implements vnode get, set, delete, and list extended-attribute operations.
- Removes all enabled attributes for an inode during inactive cleanup.
- Handles byte-swapped backing-file headers.

Storage model:
- Each enabled attribute has one backing file.
- Each inode maps to a fixed-size record in that backing file:
  `file header + inode_number * (attribute header + max attribute size)`.
- Per-record headers store in-use flag, length, and inode generation.
- Generation mismatch makes an attribute appear undefined.

Important behavior:
- Attribute reads and writes require offset zero, enforcing replace-style semantics.
- Attribute data writes are not atomic with header writes.
- `ufs_extattr_sync` can force synchronous backing-file writes.
- Access checks go through `extattr_check_cred`.
- Autocreation temporarily releases the extattr mount lock and vnode lock to avoid lock-order deadlocks while creating the backing file.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extern.h

This header declares the shared UFS operation surface.

Key contents:
- Declares vnode operations for access, create, lookup, directory mutation, readlink, remove, rename, strategy, whiteout, special device wrappers, and FIFO wrappers.
- Declares bmap helpers `ufs_bmaparray` and `ufs_getlbns`.
- Declares inode lifecycle, allocation, and truncation helpers.
- Declares directory lookup/edit helpers.
- Declares rename helper routines used by LFS.
- Declares quota functions and quota command handling.
- Declares VFS-level UFS helpers.
- Declares vnode initialization, GOP allocation/update, and buffer I/O helpers.
- Exposes `ufs_direct_cache` and `ufs_hashlock`.

Role:
- Main internal contract between UFS, FFS, LFS-adjacent code, quota code, and vnode/VFS layers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_inode.c

This file implements shared UFS inode lifecycle and allocation/truncation support.

Key responsibilities:
- `ufs_inactive` handles last-reference cleanup, deletion of unlinked inodes, truncation of all data, quota inode decrement, mode clearing, update, and recycle decision.
- `ufs_reclaim` writes final updates, releases the device vnode, frees quota state, and frees dirhash state.
- `ufs_balloc_range` allocates blocks over a byte range while locking pages so stale disk contents cannot become visible to racing readers.
- `ufs_truncate_retry` wraps truncate in WAPBL transactions and retries `EAGAIN` until size reaches target.
- `ufs_truncate_all` truncates file data plus UFS2 external attribute area.

Important behavior:
- Uses WAPBL begin/end around metadata-changing operations.
- Calls extended-attribute inactive cleanup before deleting unlinked inodes when UFS extattrs are enabled.
- Panics if an unlinked inode reaches inactive with mode zero but nonzero size or blocks after cleanup.
- Page-cache handling marks pages dirty and clears `PG_RDONLY` only when allocation succeeds and pages are fully backed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_inode.c -->