# Group Research: group_1292_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_ffs_ffs_bswap_c_source_5e2afc783de4

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_bswap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_bswap.c

This file implements byte-order conversion for FFS/UFS on-disk structures. It is used by kernel and userland tooling when reading or writing filesystems whose byte order differs from the host.

Key responsibilities:
- Swap FFS superblocks, UFS1/UFS2 dinodes, cylinder group summaries, total summaries, and cylinder groups.
- Preserve opaque bitmap/block-pointer arrays that are either endian-neutral at this layer or handled elsewhere.
- Support both old UFS1 cylinder group layouts and newer layouts with offset-based summary tables.

Important functions:
- `ffs_sb_swap`: Converts the fixed superblock fields, quota fields, snapshot inode array, summary totals, size/time fields, masks, flags, and magic. It bulk-swaps the initial contiguous 32-bit field region up to `fs_fmod`.
- `ffs_dinode1_swap`: Converts UFS1 inode metadata fields while copying direct/indirect block arrays unchanged.
- `ffs_dinode2_swap`: Converts UFS2 inode metadata, including 64-bit timestamps, birthtime, block count, extattr size, and flags; copies extattr/data/indirect block arrays unchanged.
- `ffs_csum_swap`: Swaps an arbitrary cylinder-summary byte range as 32-bit words.
- `ffs_csumtotal_swap`: Converts 64-bit aggregate directory/free-block/free-inode/free-fragment counters.
- `ffs_cg_swap`: Converts cylinder group headers, fragment summaries, old rotational tables, cluster summaries, and UFS1 block totals/position tables. It may be called in-place.

Important interactions:
- Declared in `ffs_extern.h`; called during mount, reload, snapshot writeout, and summary update paths.
- Uses `ufs_rw*`/`UFS_FSNEEDSWAP` conventions indirectly through callers.
- Must stay aligned with on-disk `struct fs`, `struct cg`, `struct ufs1_dinode`, and `struct ufs2_dinode`.

Notable behavior and risks:
- Several superblock fields overlap historic postbl table locations; the code explicitly comments on those compatibility areas.
- Dinode block pointer arrays are copied, not swapped here; consumers must interpret them through UFS byte-order helpers.
- `ffs_cg_swap` chooses offsets based on the already-converted or original magic, which is subtle but necessary for in-place use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_bswap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extattr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extattr.c

This file implements native UFS2 extended attributes stored in the UFS2 dinode extension block area. UFS1 extended attributes are delegated to the older file-backed UFS extattr implementation when compiled in.

Key responsibilities:
- Read and write UFS2 extended attribute blocks using negative logical block numbers.
- Maintain a per-inode in-memory extended-attribute transaction buffer.
- Implement VOP open/close/get/set/list/delete extended attribute operations.
- Commit EA changes back to `di_extsize`/`di_extb` through `ffs_extwrite` and `ffs_truncate`.
- Route strategy calls for FIFO/native EA negative block numbers.

Important functions:
- `ffs_extread`: Reads the EA data stream from UFS2 extension blocks, using `bread`/`breadn`, EOF clamping, short-read protection, and `uiomove`.
- `ffs_extwrite`: Writes the EA stream, allocating extension blocks with `UFS_BALLOC` and `IO_EXT`, updating `di_extsize`, handling synchronous writes, WAPBL transactions, setuid/setgid clearing, and `IO_UNIT` rollback.
- `ffs_findextattr`: Walks packed `struct extattr` records and matches namespace/name, returning content size and optional record/content pointers.
- `ffs_rdextattr`: Allocates a temporary contiguous copy of the EA area and fills it with `ffs_extread`.
- `ffs_open_ea` / `ffs_close_ea`: Reference-count the in-memory EA area, commit or discard changes, truncate stale on-disk extension data when the new EA area shrinks, and free state on last close.
- `ffsext_strategy`: Sends UFS2 negative EA logical blocks to `ufs_strategy`; FIFO non-EA traffic bypasses to FIFO handling.
- `ffs_getextattr`: Checks credentials, opens the EA transaction, finds a named attribute, and either returns its size or copies content to the caller.
- `ffs_setextattr`: Builds or replaces an aligned `struct extattr` record, grows/shrinks the in-memory packed area, copies user data, and commits.
- `ffs_listextattr`: Emits namespace-filtered attribute names in extattr list format.
- `ffs_deleteextattr`: Removes a named record by compacting the packed EA area and committing.

Important interactions:
- Uses UFS2 `di_extsize` and `di_extb[]`; rejects native EA operations on UFS1 unless `UFS_EXTATTR` fallback exists.
- Uses `extattr_check_cred` for namespace permission checks.
- Uses `genfs_node_wrlock` to serialize EA buffer state.
- Uses WAPBL around EA writes and truncation.

Notable behavior and risks:
- EA records are manually packed and 8-byte padded; malformed lengths can stop scans early.
- Commit truncates the entire EA stream to zero before rewriting when shrinking, noted by an in-code XXX.
- `ffs_setextattr` rejects NULL `uio` deletion; deletion is handled by `ffs_deleteextattr`.
- Device nodes are rejected for some native EA paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extern.h

This header is the main external interface for NetBSD FFS implementation files. It declares sysctl IDs, kernel pools, vnode/VFS entry points, allocation and block I/O helpers, snapshot hooks, WAPBL hooks, Apple UFS helpers, byte-swap helpers, and common FFS subroutines.

Key responsibilities:
- Define FFS sysctl identifiers.
- Publish kernel-only FFS APIs across allocation, block allocation, inode update/truncate, VFS operations, vnode operations, extattrs, snapshots, and WAPBL.
- Publish non-kernel-safe helpers for Apple UFS metadata and byte swapping.
- Define `FFS_NOBLK` and `FFS_ITIMES`.

Important declarations:
- Allocation: `ffs_alloc`, `ffs_realloccg`, `ffs_valloc`, `ffs_blkalloc`, `ffs_blkfree`, `ffs_vfree`, discard helpers, snapshot-aware free helpers.
- Block allocation: `ffs_balloc`.
- Inode lifecycle: `ffs_update`, `ffs_truncate`, `ffs_itimes`.
- VFS: `VFS_PROTOS(ffs)`, `ffs_reload`, `ffs_mountfs`, `ffs_flushfiles`, `ffs_sbupdate`, `ffs_cgupdate`.
- Vnode ops: `ffs_read`, `ffs_write`, `ffs_bufio`, `ffs_bufrd`, `ffs_bufwr`, `ffs_fsync`, `ffs_spec_fsync`, `ffs_reclaim`, `ffs_full_fsync`, page/lock helpers.
- Extended attributes: `ffs_openextattr`, `ffs_closeextattr`, `ffs_getextattr`, `ffs_setextattr`, `ffs_listextattr`, `ffs_deleteextattr`, `ffsext_strategy`.
- Snapshots: init/fini/create/mount/unmount/read/remove/block-free hooks.
- WAPBL: replay/start/stop/sync/abort hooks.
- Byte swapping: `ffs_sb_swap`, dinode swaps, csum swaps, cylinder-group swap.
- Support routines: `ffs_load_inode`, `ffs_getblk`, fragment/block/cluster accounting.

Important interactions:
- Centralizes ABI between `ffs_*.c`, shared UFS code, and kernel VFS registration.
- Exposes `ffs_vnodeop_p`, `ffs_specop_p`, and `ffs_fifoop_p` operation vectors used by vnode initialization.

Notable behavior and risks:
- Many declarations are gated on `_KERNEL`; userland tools still get byte-swap and some subroutine declarations.
- `FFS_ITIMES` loops while inode time flags remain set, so callers rely on `ffs_itimes` clearing the pending flags.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_inode.c

This file implements FFS inode update, truncation, indirect block reclamation, and timestamp materialization. It is the core code for persisting inode changes and freeing storage safely.

Key responsibilities:
- Write in-core inode state back to on-disk dinode blocks.
- Truncate normal file data and UFS2 extension data.
- Grow files by allocating the last byte/range needed.
- Free direct and indirect blocks, including partial final fragments.
- Coordinate quota updates and WAPBL deallocation registration.
- Update atime, mtime, ctime, and modrev from pending inode flags.

Important functions:
- `ffs_update`: Applies pending times with `FFS_ITIMES`, reads the containing inode block, updates WAPBL unlinked-inode registration state, writes UFS1/UFS2 dinode bytes with optional endian swapping, and writes or delays the buffer based on update flags.
- `ffs_truncate`: Handles special vnode no-ops, negative length rejection, `IO_EXT` truncation of UFS2 EA blocks, short symlink clearing, file growth allocation, EOF zeroing before shrink, inode pointer clearing, indirect/direct block freeing, WAPBL deallocation registration, quota updates, and VM size consistency.
- `ffs_indirtrunc`: Recursively frees blocks referenced by single/double/triple indirect blocks. It writes cleared pointers before freeing for non-WAPBL safety, handles endian-aware pointer arrays, and unwinds WAPBL deallocation cookies on error.
- `ffs_itimes`: Converts `IN_ACCESS`, `IN_CHANGE`, `IN_UPDATE`, and `IN_MODIFY` into dinode timestamp updates, avoids mtime updates for snapshots, increments `i_modrev`, marks `IN_ACCESSED`/`IN_MODIFIED`, and clears transient flags.

Important interactions:
- Uses `ffs_balloc`, `ffs_blkfree`, `ffs_snapremove`, `ffs_update`, `ffs_getblk`, WAPBL macros, quota hooks, UVM page invalidation/zeroing, and UFS byte-order helpers.
- `ffs_truncate` is used by normal vnode truncation, EA truncation, failed snapshot setup cleanup, and reclaim/inactive flows.

Notable behavior and risks:
- Partial EA truncation is intentionally unsupported and panics if requested with nonzero length.
- For WAPBL, regular file data block frees may differ from metadata/non-regular deallocation handling.
- On `EAGAIN` during deallocation, truncation restores logical size but may have created holes.
- Triple indirect support is present but noted as untested.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_quota2.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_quota2.c

This small file mounts inode-based QUOTA2 files recorded in the FFS superblock.

Key responsibilities:
- Detect whether the filesystem requests QUOTA2.
- Validate quota magic and required user/group quota inode numbers.
- VGET quota inodes and attach them to `ufsmount`.
- Mark the mount as quota-enabled.

Important function:
- `ffs_quota2_mount`: If `FS_DOQUOTA2` is set, it enables `UFS_QUOTA2`, initializes quota block size/mask from the filesystem, validates `fs_quota_magic`, loads user/group quota vnodes according to `fs_quota_flags`, stores credentials, increments write counts, marks the group quota vnode as `VV_SYSTEM`, unlocks quota vnodes, and sets `MNT_QUOTA`.

Important interactions:
- Called from `ffs_mount` and `ffs_mountfs` for writable mounts when `QUOTA2` is compiled in.
- Uses quota inode numbers from `fs->fs_quotafile[]`.
- Cleanup is handled by quota2 unmount code in shared quota paths.

Notable behavior and risks:
- If group quota setup fails after user quota setup, it closes the user quota vnode before returning.
- User quota vnode write count is incremented but only group quota vnode is marked `VV_SYSTEM` in this code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_quota2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_snapshot.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_snapshot.c

This file implements FFS filesystem snapshots and snapshot copy-on-write. It tracks active snapshot inodes, creates persistent snapshot files, excludes unwanted live state from snapshot images, intercepts block writes/frees, and reattaches snapshots at mount.

Key responsibilities:
- Maintain per-mount snapshot state and active snapshot lists.
- Create a snapshot file with preallocated metadata coverage.
- Copy cylinder groups, superblock, and summary data into the snapshot.
- Expunge unlinked files and older snapshots from the snapshot view.
- Provide block-level copy-on-write before live filesystem writes overwrite data needed by snapshots.
- Claim or copy blocks that are being freed while snapshots still need their old contents.
- Reattach snapshot inodes on mount and detach them on unmount.
- Provide snapshot reads over filesystem-size logical space.

Important functions:
- `ffs_snapshot_init` / `ffs_snapshot_fini`: Allocate and destroy `snap_info`, locks, active snapshot list, generation counter, and block hint list.
- `ffs_snapshot`: Main creation flow. It checks for an existing snapshot and free `fs_snapinum` slot, prepares the vnode, copies cylinder groups, marks the snapshot valid, fsyncs, suspends the filesystem, recopies changed cylinder groups, copies superblock/summary data, expunges unlinked files, registers the snapshot, establishes COW for the first snapshot, expunges snapshot blocks, writes snapshot metadata, flushes pages, and handles cleanup on error.
- `snapshot_setup`: Verifies mount/permissions/writecount, truncates the file, marks it `SF_SNAPSHOT|SF_SNAPINVAL`, writes a block-hint-list size placeholder, and preallocates indirect blocks, superblock, summary blocks, and cylinder group blocks.
- `snapshot_copyfs`: Creates an in-memory copy of the superblock and cylinder summaries, initializes maxcluster data, and clears `FS_DOWAPBL` in the snapshot copy.
- `snapshot_expunge`: Finds unlinked active vnodes and the in-filesystem WAPBL log, removes their blocks from the snapshot view, frees their copied inode state, and creates a preliminary list of preallocated snapshot blocks.
- `snapshot_expunge_snap`: Accounts older snapshots into the new one, removes invalid/unlinked snapshot inodes from the copied view, builds `i_snapblklist`, and writes that list to the end of the snapshot.
- `snapshot_writefs`: Writes copied summaries and superblock into the snapshot and ensures direct blocks needed by COW/snapblkfree are copied.
- `cgaccount` / `cgaccount1`: Copy cylinder group maps into the snapshot and mark free blocks as `BLK_NOCOPY`.
- `expunge` / `indiracct`: Rewrite the copied inode image for an expunged inode and walk direct/indirect block maps for accounting callbacks.
- `snapacct`, `mapacct`, `fullacct`: Mark snapshot-owned blocks and remove blocks from copied allocation maps.
- `ffs_snapgone`: Removes a deleted snapshot inode from `fs_snapinum` and drops the extra active reference.
- `ffs_snapremove`: Removes a snapshot from active COW tracking, clears COW if it was last, releases its hint list, clears `BLK_NOCOPY`/`BLK_SNAP` markers, and converts it back to a normal inode.
- `ffs_snapblkfree`: Handles block-free notifications. It lets snapshots claim full blocks directly or copies fragment/full-block data before allowing the free.
- `ffs_snapshot_mount`: Reads `fs_snapinum[]`, validates snapshot inodes, reads their block hint lists, links them onto the active list, and establishes COW.
- `ffs_snapshot_unmount`: Removes active snapshots, frees hint lists, drops references, and disestablishes COW.
- `ffs_copyonwrite`: COW callback for writes. It skips blocks outside the filesystem, in the journal, or in the precomputed no-copy list; otherwise it copies old block contents into snapshots that still map the block.
- `ffs_snapshot_read`: Reads snapshot logical data, optionally over the snapshot file size with `IO_ALTSEMANTICS`.
- `snapblkaddr`, `rwfsblk`, `syncsnap`, `wrsnapblk`: Lookup and raw read/write helpers for snapshot block handling.
- `db_get`, `db_assign`, `ib_get`, `idb_get`, `idb_assign`: UFS1/UFS2 and endian-aware block pointer helpers.

Important interactions:
- Uses `fscow_establish`/`fscow_disestablish` for copy-on-write integration.
- Works closely with `ffs_balloc`, `ffs_blkfree_snap`, `ffs_freefile_snap`, `ffs_truncate`, WAPBL, UVM, buffer cache, and quota hooks.
- Persistent snapshot state is recorded in `fs_snapinum[]` and per-snapshot block hint lists stored at the end of the snapshot file.

Notable behavior and risks:
- Snapshot creation briefly suspends the filesystem after most allocation is done to minimize suspension time.
- `si_gen` protects against snapshot list changes while locks are dropped.
- COW avoids the in-filesystem journal range to prevent WAPBL deadlocks/recursion.
- If copying a fragment during free fails, `ffs_snapblkfree` can deny the free to preserve snapshot consistency at the cost of leaked space.
- Snapshot support can be compiled out with `FFS_NO_SNAPSHOT`, leaving `ffs_snapshot` as `EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_snapshot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_subr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_subr.c

This file contains shared FFS support routines used by kernel code and filesystem tools: inode loading, buffer acquisition with COW, fragment accounting, block bitmap operations, and cluster summary accounting.

Key responsibilities:
- Load on-disk UFS1/UFS2 dinodes into in-core inode fields.
- Acquire buffers for filesystem blocks while integrating with filesystem COW.
- Maintain fragment summary counts.
- Test, clear, and set full-block availability bits in cylinder group bitmaps.
- Maintain contiguous cluster summary state.

Important functions:
- `ffs_load_inode`: Reads the correct dinode from an inode block, byte-swaps if needed, copies into `ip->i_din`, and mirrors common fields into generic inode members.
- `ffs_getblk`: Wraps `getblk`, optionally sets physical block number, clears the buffer, and runs `fscow_run` for mapped buffers.
- `ffs_fragacct`: Updates fragment-size summary counters using `fragtbl`, `around`, and `inside` tables, with optional endian-aware counter updates.
- `ffs_isblock`: Tests whether all fragments in a full filesystem block are free for the configured `fs_fragshift`.
- `ffs_isfreeblock`: Tests whether all fragments in a full filesystem block are allocated.
- `ffs_clrblock`: Marks a full block allocated in a bitmap.
- `ffs_setblock`: Marks a full block free in a bitmap.
- `ffs_clusteracct`: Updates cluster free bitmap and cluster length summary counters when allocating or freeing a full block, then updates `fs_maxcluster`.

Important interactions:
- `ffs_load_inode` is used by mount reload and vnode initialization.
- `ffs_getblk` is used by truncation, summary updates, superblock writes, and indirect block handling.
- Fragment and block bitmap helpers are used by allocation, free, WAPBL log placement, and snapshot accounting.
- Depends on lookup tables defined in `ffs_tables.c`.

Notable behavior and risks:
- Bitmap operations panic on unknown `fs_fragshift`; callers rely on validated superblocks.
- `ffs_clusteracct` assumes caller serialization around filesystem/cylinder group state.
- Userland builds define `FFS_EI` to include byte-swapped filesystem support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_tables.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_tables.c

This file defines static lookup tables for FFS fragment allocation accounting.

Key responsibilities:
- Provide bit masks used to identify available fragment runs inside a block bitmap byte.
- Provide fragment availability tables for filesystems with 1, 2, 4, or 8 fragments per block.
- Export the `fragtbl` pointer array indexed by `fs_frag`.

Important data:
- `around[9]`: Masks used when scanning fragment bit patterns.
- `inside[9]`: Expected interior bit patterns for available fragments.
- `fragtbl124[256]`: Availability table shared by fragment counts 1, 2, and 4.
- `fragtbl8[256]`: Availability table for 8 fragments per block.
- `fragtbl[MAXFRAG + 1]`: Selects the appropriate table for `fs_frag`.

Important interactions:
- Used by `ffs_fragacct` and allocation scanning code via external declarations.
- Encodes historic FFS fragment rules, including VAX `scanc`-oriented table use described in comments.

Notable behavior and risks:
- Entries for unsupported fragment counts are null; callers must use validated `fs_frag` values.
- This file has no executable functions; correctness depends on table constants matching FFS bitmap semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_tables.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vfsops.c

This file implements NetBSD FFS VFS operations: module registration, mount/update/reload/unmount, superblock validation, WAPBL replay/start integration, snapshot attachment, statvfs/sync, vnode initialization, NFS file handle conversion, pool lifecycle, and superblock/summary writeback.

Key responsibilities:
- Register FFS as a VFS module and define its `vfsops`.
- Mount root and regular FFS filesystems.
- Validate and load UFS1/UFS2/UFS2EA superblocks, including byte-swapped filesystems.
- Load summary information and initialize `ufsmount`.
- Handle read-only/read-write mount transitions, reloads, ACL flags, WAPBL, QUOTA2, snapshots, and discard.
- Flush, sync, and unmount filesystems.
- Allocate/load/reclaim inodes through vnode cache hooks.
- Write superblock and cylinder summary state.
- Convert between NFS file handles and vnodes.

Important functions:
- `ffs_checkrange`: Validates inode numbers for file handles, including UFS2 lazy-initialized inode range checks via cylinder group `cg_initediblk`.
- `ffs_snapshot_cb`: Kauth listener allowing snapshot creation by the file owner.
- `ffs_modcmd`: Attaches/detaches the FFS VFS and snapshot authorization listener.
- `ffs_mountroot`: Allocates and mounts the root FFS filesystem from `rootvp`.
- `ffs_acls`: Applies POSIX.1e/NFSv4 ACL mount/superblock flags, checks UFS2 EA support, and adjusts namecache/shared-lookup mount flags.
- `ffs_mount`: Main mount/update entry point. It validates device arguments and permissions, opens new mount devices, calls `ffs_mountfs`, handles r/w to r/o and r/o to r/w transitions, runs WAPBL replay/write/start/stop, reloads, starts QUOTA2, initializes discard, updates mount names, and writes dirty superblock state.
- `ffs_reload`: For read-only mounts after fsck, invalidates metadata, rereads the superblock and summaries, preserves in-memory pointer fields, reloads active inodes, and invalidates cached vnode data.
- `ffs_superblock_validate`: Sanitizes superblock size, block/fragment sizes, shift/mask consistency, inode-per-block counts, nonzero structural fields, frag count, and cylinder group size.
- `ffs_is_appleufs`: Detects Apple UFS through disk wedge type and optionally an Apple UFS label.
- `ffs_mountfs`: Common mount logic. It flushes device buffers, allocates `ufsmount`, initializes snapshots, searches superblock locations, handles UFS2EA magic and endian swapping, starts/replays WAPBL, loads summaries, initializes mount fields, attaches snapshots, starts WAPBL, mounts QUOTA2, and initializes discard.
- `ffs_oldfscompat_read` / `ffs_oldfscompat_write`: Translate old UFS1 superblock fields into modern in-memory fields and restore old layout fields before writeback.
- `ffs_unmount`: Flushes files, marks clean if appropriate, stops WAPBL/replay, closes the device, frees summaries/superblock/old compat state/snapshot state, and releases `ufsmount`.
- `ffs_flushfiles`: Stops quota/extattr state, flushes non-system vnodes, unmounts snapshots, flushes remaining vnodes and device metadata, and flushes WAPBL.
- `ffs_statvfs`: Fills block/inode counts, free/reserved/available counts, and statvfs metadata from FFS summaries.
- `ffs_sync`: Iterates dirty vnodes, updates inodes or fsyncs vnodes, syncs the device vnode, syncs quotas, writes modified superblock/summaries, and flushes WAPBL.
- `ffs_init_vnode` / `ffs_deinit_vnode`: Allocate/free in-core inode and dinode storage, load dinode data, initialize genfs node state, and attach/detach vnode data.
- `ffs_loadvnode`: Load an existing inode for vnode cache, reject unallocated inodes, set vnode ops, attach device vnode, set UVM size, and enter identity cache.
- `ffs_newvnode`: Allocate a new inode, initialize vnode/inode state, set uid/gid/mode/rdev/generation/birthtime, perform quota accounting, and publish vnode cache key.
- `ffs_fhtovp` / `ffs_vptofh`: Convert NFS `ufid` handles to/from vnodes with stale inode protection.
- `ffs_init`, `ffs_reinit`, `ffs_done`: Manage FFS inode/dinode pool caches and shared UFS init lifecycle.
- `ffs_sbupdate`: Writes the superblock, hiding internal flags, restoring old layout fields, converting UFS2EA magic, and byte-swapping if needed.
- `ffs_cgupdate`: Writes superblock plus cylinder summary blocks.
- `ffs_extattrctl`: Delegates UFS1 file-backed EA control to UFS extattr when available; otherwise uses standard extattr control.
- `ffs_vfs_fsync`: Fsyncs the mounted block device vnode, integrating WAPBL log flush and cache sync.

Important interactions:
- Integrates with `ffs_wapbl.c`, `ffs_snapshot.c`, `ffs_quota2.c`, `ffs_inode.c`, `ffs_subr.c`, shared UFS vnode/name/quota code, genfs, specfs, kauth, and NetBSD VFS.
- `ffs_mountfs` sets `mp->mnt_data`, `spec_node_setmountedfs`, `um_devvp`, `um_fs`, `um_ops`, and mount stat fields that most other FFS code relies on.
- Superblock/summary write paths use `ffs_getblk` and byte-swap helpers.

Notable behavior and risks:
- Dirty filesystem rejection logic is present but disabled with `#if 0`, matching comments about mount(8) behavior.
- WAPBL replay may force a superblock reread by jumping back to superblock search.
- UFS2EA on disk is normalized to UFS2 magic in memory with `UFS_EA` flag.
- Mount error cleanup must free several partially initialized structures; this path is careful but broad.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vnops.c

This file defines FFS vnode operation vectors and FFS-specific vnode operations for fsync, special-file fsync, reclaim, and getpages sizing. Most normal read/write behavior is included from shared `ufs_readwrite.c`.

Key responsibilities:
- Define operation tables for regular FFS vnodes, special device vnodes, and FIFO vnodes.
- Hook FFS-specific read/write/fsync/reclaim/extattr/ACL operations into NetBSD vnode dispatch.
- Provide WAPBL-aware fsync implementations.
- Free inode/dinode pool storage during reclaim.
- Tell genfs how far writes should extend for fragment/block allocation.

Important data:
- `ffs_vnodeop_entries`: Regular vnode ops, including UFS lookup/create/remove/rename/dir operations, FFS read/write/fsync/reclaim, UFS bmap/strategy, native extattrs, and ACL hooks.
- `ffs_specop_entries`: Special vnode ops with `ffs_spec_fsync`, UFS metadata/EA/ACL hooks, and specfs defaults.
- `ffs_fifoop_entries`: FIFO vnode ops with `ffsext_strategy` to support UFS2 native EA negative block strategy.

Important functions:
- `ffs_spec_fsync`: Calls `spec_fsync`, then updates inode metadata. Under WAPBL it avoids metadata work for data-only/lazy syncs and wraps inode update in a WAPBL transaction.
- `ffs_fsync`: Handles range fsyncs for regular files. It flushes pages, flushes relevant indirect buffers for non-WAPBL range sync, updates inode metadata, optionally flushes WAPBL, and optionally issues device cache sync.
- `ffs_full_fsync`: Full vnode fsync path. Under WAPBL it flushes pages, updates inode metadata, conditionally flushes the log, and waits for output if requested. Without WAPBL it uses `vflushbuf`, `ffs_update`, and optional `DIOCCACHESYNC`.
- `ffs_reclaim`: Frees an inode whose vnode is being reclaimed. It frees unlinked allocated inodes under WAPBL, calls `ufs_reclaim`, returns dinode storage to the correct pool, destroys genfs state, clears vnode data, and returns the inode to `ffs_inode_cache`.
- `ffs_gop_size`: Computes the end offset to write for genfs: fragment-rounded for direct-block growth and block-rounded otherwise.

Important interactions:
- The operation vectors are referenced by `ffs_vfsops.c` during VFS registration and vnode initialization.
- `ffs_read`, `ffs_write`, `ffs_bufrd`, and `ffs_bufwr` come from included shared UFS read/write code.
- Native UFS2 EA ops are supplied by `ffs_extattr.c`; UFS1 fallback depends on UFS extattr configuration.

Notable behavior and risks:
- Range fsync only takes the special range path for regular files with a nonzero range; otherwise it falls back to full fsync.
- WAPBL paths deliberately skip log flushing for syncer/data-only/lazy cases.
- Reclaim temporarily unlocks the vnode before WAPBL/free work, relying on vnode reclaim interlocks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_wapbl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_wapbl.c

This file integrates FFS with NetBSD WAPBL write-ahead physical block logging. It finds or creates journal storage, starts/stops logging, replays logs, cleans replayed inodes, and supplies WAPBL callbacks for metadata deallocation.

Key responsibilities:
- Determine whether the superblock layout supports WAPBL.
- Locate existing journals from superblock fields.
- Allocate a new journal either after the filesystem in the partition or inside the filesystem.
- Start, stop, and replay WAPBL logs.
- Record journal location in the superblock.
- Remove/clear old journal metadata.
- Complete logical cleanup after replay.
- Free or reallocate blocks during WAPBL sync/abort callbacks.

Important functions:
- `ffs_superblock_layout`: Distinguishes old UFS1 layout from UFS2-style superblock layout; WAPBL requires layout 2.
- `ffs_wapbl_replay_finish`: Processes replay cleanup records for unlinked inodes, vgets them, and frees mode-zero partially allocated inodes.
- `ffs_wapbl_sync_metadata`: WAPBL callback that applies delayed block frees, clears `fs_fmod`, updates `fs_time`, and writes summaries.
- `ffs_wapbl_abort_sync_metadata`: Reallocates blocks from aborted deallocation records.
- `wapbl_remove_log`: Clears journal locator fields and, for in-filesystem logs, zeroes the hidden log inode link count.
- `ffs_wapbl_start`: Enables logging when `MNT_LOG` is set, optionally clears old logs, finds/creates journal storage, flushes delayed buffers on update mounts, calls `wapbl_start`, sets `FS_DOWAPBL`, flushes the log, disables discard if needed, and completes replay cleanup.
- `ffs_wapbl_stop`: Flushes WAPBL, clears `FS_DOWAPBL` in a final transaction, stops the log, and handles forced stop.
- `ffs_wapbl_replay_start`: Locates the journal and initializes replay state with `wapbl_replay_start`.
- `wapbl_log_position`: Uses existing superblock journal locators if valid; otherwise chooses end-of-partition storage if sufficiently large, or creates an in-filesystem log, then writes journal locator metadata.
- `wapbl_create_infs_log`: Creates a hidden regular inode with `SF_LOG`, gives it one link, updates it, and allocates contiguous log storage.
- `wapbl_allocate_log_file`: Chooses a contiguous free extent, stores first data/indirect hints in the inode, allocates the file with `GOP_ALLOC`, and returns physical log start/count plus inode number.
- `wapbl_find_log_start`: Searches cylinder groups from the middle outward for a contiguous free extent large enough for the log plus needed indirect blocks.

Important interactions:
- Called by `ffs_mount`, `ffs_mountfs`, `ffs_unmount`, and `ffs_flushfiles`.
- Journal metadata is stored in `fs_journal_version`, `fs_journal_location`, `fs_journal_flags`, and `fs_journallocs[]`.
- Uses block bitmap helpers from `ffs_subr.c`, allocation via genfs/UFS paths, and WAPBL core APIs.
- Disables `MNT_DISCARD` when logging starts because discard conflicts with deallocation registration.

Notable behavior and risks:
- End-of-partition journal is preferred when the partition has enough space after the filesystem.
- In-filesystem journals require a contiguous free run and may fail with `ENOSPC` even when total free space is larger.
- Forced stop can leave `FS_DOWAPBL` state recovery to later handling.
- Several comments note duplicated journal-location logic across kernel and userland tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_wapbl.c -->