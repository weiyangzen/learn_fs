# Group Research: group_770_linux_sources_os_linux_linux_fs_jfs_jfs_dtree_c_sources_os_linux_lin_a1235ec56e7e

Scope: `Docs/research_subset_a.md` only. All 11 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dtree.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_dtree.c

## Role

Implements the JFS directory B+tree manager, including lookup, insertion, deletion, rename-target modification, directory traversal, persistent directory cookies, and structural validation of directory tree pages.

## Key Responsibilities

- Searches directory B+trees in `dtSearch()`, including case-insensitive OS/2 ordering, internal router keys, leaf-name comparison, stale-inode checks for remove/rename, and returning pinned leaf search results through a `btstack`.
- Inserts leaf entries in `dtInsert()` and handles overflow through `dtSplitUp()`, `dtSplitRoot()`, `dtSplitPage()`, and `dtExtendPage()`.
- Uses variable-length directory names stored across 32-byte slots, with page-local sorted-entry tables (`stbl`) for binary search and insertion ordering.
- Maintains persistent directory entry indices when `JFS_DIR_INDEX` is enabled: inline table first, then an xtree-backed directory table after `MAX_INLINE_DIRTABLE_ENTRY`.
- Deletes entries in `dtDelete()` and propagates empty-page removal upward through `dtDeleteUp()`, including sibling relinking and extent/quota release.
- Implements `jfs_readdir()` for both persistent-index directories and legacy OS/2/Linux JFS directory offsets.
- Validates in-inode dtree roots and external dtree pages with `check_dtroot()` and `check_dtpage()`.

## Important Interactions

- Uses generic JFS B+tree/metapage macros specialized through `DT_GETPAGE`, `DT_PAGE`, and `DT_GETSTBL`.
- Relies on transaction locks from `jfs_txnmgr` for physical-image logging of dtree slots, stbl regions, root updates, relinks, extent frees, and directory index table updates.
- Allocates and frees directory data extents through `dbAlloc()`, `dbReAlloc()`, `dbFree()`, `xtInsert()`, and `xtTruncate()`.
- Stores the inline root and inline directory table in `struct jfs_inode_info`; when the directory table grows, the same inode union area becomes an xtree root for external table pages.

## Invariants and Risks

- Directory pages are slot-managed: `freecnt`, `freelist`, `nextindex`, and `stbl` must remain mutually consistent.
- Root pages are inline in the dinode and are never freed; empty-root deletion resets the root through `dtInitRoot()`.
- Persistent directory indices must track leaf page block number and stbl position whenever entries are inserted, deleted, moved by split, or moved by stbl shifts.
- Case-insensitive ordering folds search keys and leaf names for comparison but stores leaf names in original case.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dtree.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_dtree.h

## Role

Defines the on-disk/in-memory directory tree layout and public directory B+tree API used by JFS directory operations.

## Key Responsibilities

- Defines directory slot formats: generic continuation `dtslot`, internal/router `idtentry`, and leaf `ldtentry`.
- Defines persistent directory index support through `struct dir_table_slot`, validity flags, and address packing/unpacking macros.
- Defines the inline directory root `dtroot_t` and external directory page `dtpage_t`.
- Provides constants for supported directory page sizes, table-slot counts, entry start offsets, and maximum directory offset sentinel.
- Declares public dtree entry points for root init, search, insert, delete, modify, readdir, and page validation.

## Important Interactions

- Included by `jfs_incore.h`, which embeds `dtroot_t` and inline directory table storage into `struct jfs_inode_info`.
- Depends on `jfs_btree.h` for common B+tree flags and transaction stack structures.
- `DO_INDEX()` depends on the superblock mount flag `JFS_DIR_INDEX`.

## Invariants and Risks

- Slot sizes and data-length constants must match the on-disk JFS directory format exactly.
- Legacy leaf entries use 13 UTF-16 characters in the head segment; indexed directories use 11 plus a 32-bit persistent index field.
- External page `stblindex` divides page slots into entry data and sorted-index table regions.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_dtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_extent.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_extent.c

## Role

Implements regular-file extent allocation, allocation hints, and conversion of not-recorded extents to recorded extents.

## Key Responsibilities

- Allocates file extents in `extAlloc()`, validating read-write state, clamping length to `MAXXLEN`, deriving file offset from page number, and using previous extent hints when possible.
- Extends a previous adjacent extent through `xtExtend()` when the new allocation is physically contiguous and has the same recorded/not-recorded state.
- Inserts a new xtree extent through `xtInsert()` when extension is not possible.
- Uses `extBalloc()` to allocate contiguous block ranges, backing off request size by powers of two until at least one page worth of blocks can be allocated.
- Provides `extHint()` to return the extent covering the previous page.
- Provides `extRecord()` to update an extent from not-recorded to recorded through `xtUpdate()`.

## Important Interactions

- Uses `dbAlloc()`/`dbFree()` for block-map allocation and release.
- Uses xtree operations (`xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`) to record allocated extents in file metadata.
- Serializes extent updates with `txBeginAnon()` and `JFS_IP(ip)->commit_mutex`.
- Calls quota helpers for block charging and rollback.

## Invariants and Risks

- Extent allocation refuses read-only filesystems via `isReadOnly()`.
- `extHint()` treats missing previous-page mappings as "no hint" rather than an error.
- `extBalloc()` never returns less than `nbperpage` blocks; inability to allocate one page returns `-ENOSPC`.
- Rollback paths must free both allocated blocks and quota reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_extent.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_extent.h

## Role

Declares the JFS extent allocation interface and the inode-location allocation hint macro.

## Key Responsibilities

- Defines `INOHINT(ip)` as the last block of the disk inode extent, used as a placement hint for file data allocation.
- Declares `extAlloc()` for allocating and recording file extents.
- Declares `extHint()` for deriving a previous-page extent hint.
- Declares `extRecord()` for converting not-recorded extent metadata to recorded.

## Important Interactions

- Depends on `JFS_IP(ip)->ixpxd`, the disk inode extent descriptor maintained by inode-map code.
- Public functions are implemented in `jfs_extent.c` and used by file/block mapping code elsewhere in JFS.

## Invariants and Risks

- `INOHINT()` assumes `ixpxd` is valid and non-empty.
- Callers must pass an `xad_t` whose address field may contain an allocation hint on entry and receives the allocated extent on success.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_filsys.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_filsys.h

## Role

Defines JFS filesystem-wide constants, mount/superblock flags, fixed disk layout offsets, size limits, reserved inode numbers, and filesystem state values.

## Key Responsibilities

- Defines mount and aggregate flags for Unicode, error policy, quotas, no-integrity mode, discard, commit mode, inline log state, bad secondary AIT, sparse files, DASD limits, endian marker, directory index support, and OS/platform compatibility.
- Defines page, physical-block, dinode, inline-data, inode-extent, IAG, and filesystem block-size constants.
- Defines inode table geometry: 4096 inodes per IAG, 32 inodes per extent, 8 dinodes per 4 KiB page, and 512-byte on-disk dinodes.
- Provides block/byte conversion macros for physical/logical blocks and size-to-page/block calculations.
- Defines fixed physical block addresses and byte offsets for superblocks, aggregate inode map/table, secondary superblock, and block allocation map.
- Defines aggregate reserved inode numbers and per-fileset reserved inode numbers.

## Important Interactions

- Used by most JFS source files to interpret disk layout and feature flags.
- `JFS_DIR_INDEX` gates persistent directory cookie support in dtree code.
- Inode-map geometry constants are consumed by `jfs_imap.h` and `jfs_imap.c`.
- Fixed aggregate offsets are used by special inode read/write paths.

## Invariants and Risks

- Constants encode on-disk format and cannot be changed without format incompatibility.
- `PSIZE` is fixed at 4096 and acts as the JFS buffer/metapage page size.
- Reserved inode numbers distinguish aggregate metadata inodes from fileset object inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_filsys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_imap.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_imap.c

## Role

Implements the JFS inode allocation map manager: mounting/syncing the inode map, reading/writing dinodes, allocating and freeing disk inodes and inode extents, maintaining IAG/AG free lists, and updating persistent inode bitmaps during transaction commit.

## Key Responsibilities

- Mounts the inode map in `diMount()` by reading the dinomap control page into an in-core `struct inomap` and initializing global/free-list locks.
- Reads regular inodes in `diRead()` by locating the containing IAG, validating the inode extent descriptor, handling legacy unaligned inode extents, reading the dinode page, and copying dinode fields into the VFS inode.
- Reads/writes aggregate special inodes through `diReadSpecial()` and `diWriteSpecial()` from fixed AIT or secondary AIT locations.
- Writes regular dinodes in `diWrite()`, including inode base fields, inline symlink data, inline EA data, inline dtree root, regular-file xtree root, and directory-table xtree root.
- Frees disk inodes in `diFree()`, updating working maps, summary maps, per-IAG/per-AG/global counts, free lists, and freeing whole inode extents when above retention thresholds.
- Allocates disk inodes in `diAlloc()` using directory-vs-file policy.
- Allocates from AGs and IAGs through `diAllocAG()`, `diAllocAny()`, `diAllocIno()`, `diAllocExt()`, `diAllocBit()`, `diNewExt()`, and `diNewIAG()`.
- Updates persistent inode allocation maps in `diUpdatePMap()` during transaction processing.
- Rebuilds per-AG imap control lists after filesystem extension in `diExtendFS()`.

## Important Interactions

- Uses IAG pages and dinomap structures defined in `jfs_imap.h`; uses filesystem geometry and fixed AIT offsets from `jfs_filsys.h`.
- Coordinates with the block allocator through `dbAlloc()`, `dbFree()`, `BLKTOAG()`, `AGTOBLK()`, `dbNextAG()`, and active AG counters.
- Uses metapage I/O for dinomap, IAG, and dinode pages.
- Uses transaction manager locks/commits for dinode writes, inode extent frees, imap xtree extension, persistent-map updates, and secondary AIT updates.
- Calls `check_dtroot()` when loading directory inodes to reject corrupt inline directory roots.

## Invariants and Risks

- Working maps (`wmap`) reflect currently allocated inodes; persistent maps (`pmap`) are updated during commit and must match transaction state.
- IAG free-inode and free-extent lists are doubly linked and require careful pre-reading of neighbor IAG pages to avoid partial updates and deadlocks.
- `im_agctl[].numfree` must never exceed `numinos`; multiple paths treat this as filesystem corruption.
- Special aggregate inodes bypass the normal inode map because they are needed early in mount.
- Legacy OS/2 unaligned inode extents require careful page/relative-inode calculation in both read and write paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_imap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_imap.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_imap.h

## Role

Defines the inode allocation map on-disk structures, in-core control structures, geometry macros, and public imap API.

## Key Responsibilities

- Defines IAG geometry: 128 inode extents per IAG, 32 extents per summary word, 4 pages per inode extent, up to `MAXIAGS`, and up to 128 allocation groups.
- Provides inode-number conversion macros such as `INOTOIAG()`, `IAGTOLBLK()`, and `INOPBLK()`.
- Defines `struct iag`, including AG start, list links, summary maps, counts, padding, working/persistent allocation maps, and inode extent descriptors.
- Defines on-disk and in-core dinomap control pages.
- Defines `struct inomap`, which wraps the in-core dinomap, inode-map inode pointer, free-list locks, per-AG locks, debug map pointer, and atomic global counts.
- Declares public imap operations for allocation, free, sync, persistent-map update, filesystem extension, mount/unmount, regular/special inode read/write, and special inode release.

## Important Interactions

- Includes `jfs_txnmgr.h` because persistent-map updates receive transaction blocks.
- Depends on geometry constants from `jfs_filsys.h` for inode counts, dinode size, and extent size.
- Used by `jfs_imap.c`, inode allocation code, transaction commit code, and mount/umount paths.

## Invariants and Risks

- `struct iag` and `struct dinomap_disk` are 4096-byte disk-format pages.
- `wmap` uses 1 bits for allocated working inodes; comments indicate 0 means free.
- Summary-map polarity is subtle: an `inosmap` bit is 0 when a backed extent has at least one free inode, and 1 when no allocatable backed free inode exists.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_imap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_incore.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_incore.h

## Role

Defines JFS private in-core inode and superblock structures, lock helpers, commit flags, and core accessor functions.

## Key Responsibilities

- Defines `struct jfs_inode_info`, embedding Linux `struct inode` plus JFS fields for fileset, mode flags, saved uid/gid, inode extent descriptor, ACL/EA descriptors, creation time, directory index state, AG placement, transaction state, locks, and type-specific inline metadata.
- Provides inode union storage for regular-file xtree root plus imap pointer, directory inline table plus dtree root, and symlink/inline-EA data.
- Provides read/write lock macros for inode metadata serialization using `rdwrlock`.
- Defines commit flags for zero-link commit, inline EA commit, free-WMAP, dirty state, dirtable commit, stale extents, and sync-list metadata.
- Defines `struct jfs_sb_info`, storing mount flags, metadata inodes, log state, block-size geometry, aggregate IDs, descriptors, UUIDs, inode generation state, block map, NLS table, mount overrides, and discard settings.
- Provides `JFS_IP()`, `JFS_SBI()`, `jfs_dirtable_inline()`, and `isReadOnly()` helpers.

## Important Interactions

- Includes `jfs_xtree.h` and `jfs_dtree.h` because inline roots live directly in the private inode.
- Used by nearly every JFS implementation file as the bridge between Linux VFS objects and JFS metadata.
- `isReadOnly()` treats absence of a log pointer as read-only behavior for metadata update paths.

## Invariants and Risks

- The private inode union overlays file, directory, and symlink metadata; callers must use the branch matching inode mode.
- `commit_mutex` must be acquired after transaction begin, per comment, to avoid dirty-inode commit races.
- Mount uid/gid/umask overrides are stored in the superblock and interpreted during dinode copy in/out.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_incore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_inode.c -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_inode.c

## Role

Provides basic JFS inode flag translation and new inode allocation/initialization.

## Key Responsibilities

- Maps JFS-specific mode flags to Linux inode flags in `jfs_set_inode_flags()`: immutable, append-only, no-atime, dirsync, and sync.
- Allocates a new VFS inode in `ialloc()`.
- Allocates a disk inode through `diAlloc()`, passing whether the requested mode is a directory.
- Inserts the new inode into the inode hash with `insert_inode_locked()`.
- Initializes owner, saved uid/gid, quota state, inherited JFS flags, file/directory/symlink mode flags, timestamps, generation number, and private JFS inode fields.
- Handles allocation failures by dropping quotas, clearing links, discarding new inodes, or putting the inode as appropriate.

## Important Interactions

- Calls `diAlloc()` from `jfs_imap.c` for disk inode assignment and inode extent metadata.
- Calls quota initialization/allocation after VFS ownership setup.
- Reads inherited JFS flags from the parent inode's `mode2`.
- Uses `JFS_SBI(sb)->gengen` to assign inode generation numbers.

## Invariants and Risks

- New inode state must be initialized after successful disk inode allocation but before returning to directory creation/link code.
- Quota allocation happens after the inode is inserted/owned; failure paths must mark `S_NOQUOTA`, clear link count, and discard the inode.
- Symlinks deliberately do not inherit immutable or append-only flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_inode.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_inode.h

## Role

Declares JFS inode, file, directory, export, ioctl, block-mapping, writeback, truncate, xattr/attribute, and operation-table interfaces.

## Key Responsibilities

- Declares inode allocation and lookup helpers: `ialloc()` and `jfs_iget()`.
- Declares sync/writeback/dirty/evict/commit paths.
- Declares truncate and zero-link free helpers.
- Declares exportfs helpers for parent and file-handle resolution.
- Declares inode flag and block mapping helpers.
- Declares setattr and file-attribute get/set interfaces.
- Exposes operation tables for address-space operations, directory/file/symlink inode operations, directory/file file operations, fast symlink operations, and case-insensitive dentry operations.

## Important Interactions

- Implemented across multiple JFS source files, including `jfs_inode.c`, generic inode/file/dir/namei/ioctl code, and export helpers.
- Included by allocation, extent, and imap code when they need inode lifecycle or commit entry points.

## Invariants and Risks

- This header is a cross-module contract; prototype drift would break many JFS compilation units.
- `jfs_get_block()` is the bridge from VFS/buffer-head mapping to JFS extent logic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_lock.h -->
# File Research: sources/os/linux/linux/fs/jfs/jfs_lock.h

## Role

Provides a JFS wait helper for sleeping on a condition protected by an external spinlock.

## Key Responsibilities

- Includes Linux spinlock, mutex, and scheduler headers needed by lock/wait code.
- Defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`.
- Adds the current task to a wait queue, sets `TASK_UNINTERRUPTIBLE`, checks the condition while the caller's lock is held, drops the lock around `io_schedule()`, reacquires it, and removes the waiter after wakeup.

## Important Interactions

- The macro is parameterized with caller-provided lock and unlock commands so it can be used with different spinlock instances.
- Intended for code where the condition is protected by a spinlock but waiting must happen without holding that spinlock.

## Invariants and Risks

- Sleep is uninterruptible; callers must use it only where signal interruption is not required.
- The condition must be tested while the caller's lock is held.
- The wait queue entry is stack-allocated and must be removed before macro exit.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/jfs/jfs_lock.h -->