# Group Research: group_1012_linux_stable_sources_os_linux_linux_stable_fs_jfs_jfs_dtree_c_sourc_9cd089969fff

Scope: `Docs/research_subset_a.md` only. All 11 listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.c

This file implements the JFS directory B+-tree manager: lookup, insertion, deletion, rename-target modification, directory traversal, persistent directory cookies, root/page validation, page splitting, page extension, and transaction logging support for directory pages.

Key responsibilities:
- Implements directory lookup in `dtSearch()`, descending the dtree from the inline root through internal pages to a leaf while maintaining a `btstack` for later insert/delete propagation.
- Supports JFS OS/2 case-insensitive behavior by uppercasing search keys and comparing folded leaf names while preserving original names in leaf entries.
- Maintains the persistent directory index table used for stable `readdir()` cookies when `JFS_DIR_INDEX` is enabled. The table starts inline in `i_dirtable`, then migrates to an xtree-backed external table as it grows.
- Adds, frees, reads, and updates directory index entries through `add_index()`, `free_index()`, `read_index()`, and `modify_index()`.
- Inserts directory leaf entries in `dtInsert()`, allocating slot chains for variable-length Unicode names and updating the sorted entry table.
- Handles full-page insertions through `dtSplitUp()`, `dtSplitPage()`, `dtSplitRoot()`, and `dtExtendPage()`, including child extent allocation, quota accounting, sibling links, router-key generation, and directory index table repair after entries move.
- Deletes leaf entries in `dtDelete()` and propagates empty-page removal upward through `dtDeleteUp()`, including extent free logging, quota release, sibling relinking, and root reinitialization.
- Updates the inode number in an existing directory entry through `dtModify()`, used by rename-style operations.
- Implements `jfs_readdir()`, including modern persistent-index traversal, legacy OS/2 offset traversal, dot/dotdot emission, NLS conversion from JFS Unicode names, page-buffer batching before `dir_emit()`, and opportunistic repair of missing directory indices.
- Provides low-level entry manipulation helpers: `dtInsertEntry()`, `dtMoveEntry()`, `dtDeleteEntry()`, `dtTruncateEntry()`, `dtLinelockFreelist()`, `dtCompare()`, `ciCompare()`, `dtGetKey()`, and `ciGetLeafPrefixKey()`.
- Validates inline roots and regular directory pages with `check_dtroot()` and `check_dtpage()` before trusting freelists, sorted-entry tables, and slot indices.

Important interactions:
- Uses B+-tree/metapage helpers from `jfs_btree.h` and `jfs_metapage.h`; directory page 0 is the inline root stored in the inode.
- Uses the block allocator and xtree code when directory pages, directory-index pages, or relocated/extending pages need new physical storage.
- Uses the transaction manager heavily through `txLock()`, `txMaplock()`, `txLinelock()`, line locks, map locks, and `BT_MARK_DIRTY()` so dtree changes are journaled at slot granularity.
- Uses quota helpers for directory page allocation/free and directory extent extension.
- Uses Unicode helpers for little-endian UCS name storage, case folding, and codepage conversion during lookup and readdir.
- Cooperates with `diWrite()` through inode-private dtree and dirtable commit flags; inline directory roots and inline directory tables are copied back into dinodes during inode commit.

Notable invariants and risks:
- Directory entries are stored as linked chains of 32-byte slots; `freelist`, `freecnt`, `stblindex`, `nextindex`, and every slot `next` pointer must stay mutually consistent.
- Internal/router entries store child extents and possibly suffix-compressed keys; the leftmost internal key is intentionally treated as a minimum sentinel.
- Leaf entry layout differs for legacy directories versus indexed directories because indexed entries reserve space for a persistent directory-table index.
- Split and extension paths must update directory-table slots whenever leaf entries move to a different page or sorted-entry-table index.
- `jfs_readdir()` has two independent offset schemes: persistent index cookies for indexed directories and `(page-number,index)` legacy offsets for old directories.
- The code has many paired metapage pins/releases and transaction locks; error paths in split/extend/delete flows are especially sensitive to leaked pins, double frees, stale quota accounting, and partially updated sibling links.
- The page validation helpers reduce corruption exposure by rejecting invalid freelists, duplicate slot references, bad sorted-table entries, and impossible free counts before page use.

Research notes:
- This is the core JFS pathname-directory engine. The most important local design is the combination of a sorted slot table for B+-tree search, variable-length slot chains for names, and a separate persistent directory index table for stable VFS/NFS directory positions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.h

This header defines the on-disk/in-core layout and public interface for JFS directory B+-tree pages.

Key responsibilities:
- Defines `ddata_t`, the insert payload union for leaf entries (`tid`, inode pointer, inode number) or internal entries (`pxd_t` child extent).
- Defines 32-byte directory slots (`struct dtslot`) and type-specific head slots for internal entries (`struct idtentry`) and leaf entries (`struct ldtentry`).
- Defines slot-size constants and macros for computing the number of slots needed for internal, modern leaf, and legacy leaf entries.
- Defines the persistent directory-table slot format (`struct dir_table_slot`) and helpers to pack/unpack 40-bit page addresses or deleted-entry forward links.
- Defines the inline directory root (`dtroot_t`) stored in the inode and the external directory page (`dtpage_t`) used after the directory grows.
- Provides helper macros for parent inode lookup, empty-directory checks, sorted-entry table access, and directory-end offsets.
- Declares the dtree API: root initialization, search, insert, delete, modify, readdir, and page/root validators.

Important interactions:
- Included by `jfs_incore.h`, which embeds `dtroot_t` and the inline directory table in `struct jfs_inode_info`.
- Depends on generic JFS B+-tree and extent descriptor definitions from `jfs_btree.h`.
- Exposes `JFS_CREATE`, `JFS_LOOKUP`, `JFS_REMOVE`, and `JFS_RENAME` operation codes consumed by `dtSearch()`.

Notable invariants and risks:
- Inline roots have only 9 slots, while regular pages have 128 slots; code must select the correct sorted-table location with `DT_GETSTBL()`.
- Directory-table entries have two meanings for `addr2`: low address bits for valid entries, or next-index links for free/deleted entries.
- The `DO_INDEX()` macro changes leaf-entry capacity and traversal behavior; mixed handling of legacy and indexed directories is a recurring source of subtle offset and slot-count logic.

Research notes:
- This header is the compact schema for the dtree manager. It explains why `jfs_dtree.c` is dominated by slot accounting, sorted-table shifting, and format compatibility checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_dtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_extent.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_extent.c

This file implements regular-file extent allocation support for JFS. It chooses block ranges, inserts or extends xtree records, preserves not-recorded extent state, and provides allocation hints.

Key responsibilities:
- Allocates an extent for a file page range in `extAlloc()`, with read-only checks, anonymous transaction setup, commit mutex serialization, quota charging, block allocation, and xtree insertion/extension.
- Caps requested extents at `MAXXLEN` and converts page numbers to filesystem block offsets using the mounted block geometry.
- Uses a caller-provided `xad_t` as an allocation hint and extends the previous extent when the new allocation is contiguous and has matching recorded/not-recorded state.
- Falls back to smaller allocation sizes through `extBalloc()` when the requested contiguous extent is unavailable, rounding down toward power-of-two sizes while preserving at least one page of blocks.
- Produces previous-page allocation hints in `extHint()` by looking up the page before the requested offset and returning its extent descriptor when it exactly covers one page.
- Converts not-recorded extents to recorded state through `extRecord()`, delegating to `xtUpdate()`.
- Tracks the active allocation group for growing regular files so the block allocator can avoid fragmentation-sensitive placement conflicts.

Important interactions:
- Calls the JFS block allocator (`dbAlloc()`, `dbFree()`) and xtree operations (`xtInsert()`, `xtExtend()`, `xtLookup()`, `xtUpdate()`).
- Uses quota helpers to charge and roll back block allocation.
- Uses `JFS_IP(ip)->commit_mutex` to serialize extent-tree updates against inode commit.
- May force inode commit when `COMMIT_Synclist` is cleared after anonymous metadata updates.

Notable invariants and risks:
- Extent offsets are filesystem-block offsets derived from page numbers, not byte offsets.
- The allocation hint can only be extended when the old extent ends exactly at the requested offset and the `XAD_NOTRECORDED` state matches.
- Failed xtree insertion/extension must free both allocated blocks and quota charges.
- `extHint()` treats a previous-page extent with a length other than one page as xtree corruption.
- `extBalloc()` must never return an allocation smaller than the filesystem blocks per page.

Research notes:
- This file is a narrow bridge between file write/page allocation and the lower JFS block map plus xtree metadata. It does not perform buffered I/O itself; it updates file extent metadata for callers elsewhere in JFS.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_extent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_extent.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_extent.h

This header declares the JFS extent allocation API and the inode-based allocation hint macro.

Key responsibilities:
- Defines `INOHINT(ip)`, which uses the inode extent descriptor as a block allocation hint.
- Declares `extAlloc()` for allocating file extents.
- Declares `extHint()` for deriving allocation hints from nearby file offsets.
- Declares `extRecord()` for changing an extent from not-recorded to recorded.

Important interactions:
- Depends on `JFS_IP(ip)->ixpxd` and extent descriptor helpers such as `addressPXD()` and `lengthPXD()`.
- Used by file/block mapping code that needs to allocate or update regular-file xtree records.

Notable invariants and risks:
- `INOHINT()` assumes the inode extent descriptor has a valid address and length.
- The API exposes `xad_t` directly, so callers must preserve correct offset, length, address, and `XAD_NOTRECORDED` semantics.

Research notes:
- This is a small public surface for the extent allocator implemented in `jfs_extent.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_filsys.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_filsys.h

This header defines implementation-wide JFS filesystem constants: mount flags, fixed sizes, reserved on-disk locations, reserved inode numbers, name limits, and filesystem state bits.

Key responsibilities:
- Defines mount/superblock flags for Unicode names, error handling policy, quotas, no-integrity mode, discard/TRIM, commit behavior, inline logs, sparse files, DASD limits, endian flags, directory indexing, and platform compatibility.
- Defines fixed JFS geometry constants such as page size, physical block size, disk inode size, inline inode data size, inline xattr size, inode allocation group size, inode extent size, and min/max filesystem block sizes.
- Defines conversion helpers for logical/physical block numbers and byte sizes to page/block numbers.
- Defines fixed physical block and byte offsets for the primary superblock, aggregate inode map, aggregate inode table, secondary superblock, and block allocation map.
- Defines reserved aggregate and fileset inode numbers, including aggregate metadata inodes, the fileset inode map, root inode, ACL inode, and first regular object inode.
- Defines directory/path length limits and superblock state values such as clean, mounted, dirty, logredo failure, and extendfs in progress.

Important interactions:
- Included throughout JFS to keep on-disk layout assumptions consistent across superblock, inode map, block map, dtree, and xtree code.
- Constants such as `INOSPERIAG`, `INOSPEREXT`, `DISIZE`, `IDATASIZE`, and `PSIZE` are directly used by inode map and directory code.
- Mount flags such as `JFS_DIR_INDEX`, `JFS_OS2`, and `JFS_BAD_SAIT` materially change behavior in dtree, imap, and mount/recovery paths.

Notable invariants and risks:
- Several offsets are fixed JFS on-disk ABI; changing them would break existing filesystems.
- JFS assumes a 4096-byte metadata page size while allowing filesystem logical block sizes from 512 to 4096 bytes.
- Reserved inode numbers are overloaded between aggregate-level and fileset-level namespaces and must be interpreted in the correct context.

Research notes:
- This file is the shared geometry and feature-flag contract for the rest of the JFS implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_filsys.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_imap.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_imap.c

This file implements the JFS inode allocation map manager. It mounts and syncs inode map metadata, reads and writes dinodes, allocates and frees inode numbers and inode extents, manages inode allocation group lists, updates persistent allocation maps during commit, handles filesystem extension, and maintains the secondary aggregate inode table.

Key responsibilities:
- Mounts the inode map in `diMount()` by reading the on-disk dinomap control page into an in-memory `struct inomap`, converting per-AG counters and initializing locks.
- Syncs and unmounts the inode map through `diSync()` and `diUnmount()`, writing control-page state and flushing dirty inode-map pages.
- Reads regular dinodes in `diRead()` by locating the target IAG, resolving the inode extent, handling OS/2-era unaligned inode extents, reading the containing page, and copying the dinode into the VFS inode.
- Reads and writes aggregate special inodes through `diReadSpecial()` and `diWriteSpecial()` using fixed aggregate inode table locations or the secondary AIT.
- Writes regular dinodes in `diWrite()`, copying base inode fields plus inline symlinks, inline EAs, inline directory roots, directory-index xtree roots, or regular-file xtree roots under transaction line locks.
- Frees inodes in `diFree()`, updating the working map, summary maps, per-IAG counters, per-AG free-inode/free-extent lists, global counters, quota-visible extent ownership, and logging freed inode extents when an entire inode extent is released.
- Allocates inodes in `diAlloc()`, preferring parent locality for files, allocation-group rotation for directories, and avoiding active AGs used by growing regular files.
- Allocates from a specific AG or any AG through `diAllocAG()`, `diAllocAny()`, and `diAllocIno()`.
- Allocates backed inode extents through `diAllocExt()` and initializes new inode extents through `diNewExt()`, including disk inode initialization, free-list maintenance, and block allocation.
- Allocates or extends IAG pages through `diNewIAG()`, including transactionally extending the inode-map xtree, synchronously initializing the new page, adding it to the free-IAG list, and duplicating the xtree into the secondary AIT when possible.
- Updates the persistent inode map in `diUpdatePMap()` during transaction commit and attaches the IAG metapage to log sync state.
- Rebuilds per-AG inode-map lists after filesystem growth in `diExtendFS()`.
- Converts between dinode and in-memory inode fields in `copy_from_dinode()` and `copy_to_dinode()`, including mount uid/gid/umask overrides, timestamps, device numbers, ACL/EA descriptors, directory dtree roots, and xtree roots.

Important interactions:
- Uses `struct inomap`, `struct iag`, and dinomap formats from `jfs_imap.h`.
- Coordinates with the block allocator for inode extent and IAG-page allocation/free.
- Coordinates with xtree code for inode-map addressability and with the transaction manager for inode, map, and freed-extent logging.
- Uses JFS private inode fields from `jfs_incore.h`, especially `ixpxd`, `agstart`, `ipimap`, inline roots, commit flags, and transaction lock IDs.
- Uses metapage I/O for inode map pages and raw/special aggregate inode table pages.
- Integrates with quota by marking metadata inodes `S_NOQUOTA`; actual user inode quota charging is handled around `ialloc()` and VFS inode lifecycle.

Notable invariants and risks:
- Lock ordering is explicit: AG list locks protect per-AG lists, IAG pages are locked by holding metapages, and the inode-map inode read/write lock protects global map state and IAG addressability.
- Working maps (`wmap`) track current allocation, while persistent maps (`pmap`) are updated through commit; the two must transition in the expected order.
- Summary maps use inverted availability semantics in places: set bits can mean no backed free inodes, while clear bits identify candidate free resources.
- Freeing an inode may free an entire inode extent only above low-water thresholds; otherwise the extent is retained to avoid churn.
- Careful update paths read all IAGs that will be linked/unlinked before mutating list pointers to avoid partially updated free lists.
- New IAG creation must keep the inode map, control page, and secondary AIT synchronized enough for recovery; failure paths mark `JFS_BAD_SAIT` when the secondary copy cannot be maintained.
- Dinode page addressing handles unaligned inode extents from OS/2-created filesystems, so page and relative-inode calculations are more complex than a simple division.
- `copy_from_dinode()` validates directory roots with `check_dtroot()` before exposing directory state to the rest of JFS.

Research notes:
- This is the allocator and serialization center for JFS inode metadata. The critical concepts are IAGs, backed inode extents, per-AG free lists, the split between working and persistent bitmaps, and transaction-time synchronization with log recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_imap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_imap.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_imap.h

This header defines the JFS inode allocation map data structures, conversion macros, and exported imap/dinode management API.

Key responsibilities:
- Defines inode allocation group geometry: extents per IAG, summary-map sizes, inodes per extent relationships, maximum IAG count, and maximum allocation groups.
- Provides conversion macros from inode number to IAG number, IAG number to logical block number, and inode extent descriptor plus inode number to containing page block.
- Defines `struct iag`, the 4096-byte inode allocation group page containing AG links, free-list links, summary maps, working and persistent allocation maps, and inode extent descriptors.
- Defines on-disk and in-core per-AG controls for free inode lists, free extent lists, backed inode counts, and free inode counts.
- Defines the on-disk dinomap control page (`struct dinomap_disk`) and in-core map state (`struct dinomap`, `struct inomap`) with locks and atomic global counters.
- Declares public imap functions for mount/unmount, sync, read/write, special inode handling, allocation/free, persistent map updates, and extendfs rebuilds.

Important interactions:
- Included by inode allocation, inode commit, mount, and transaction code.
- Depends on transaction manager declarations because persistent map updates receive a `struct tblock`.
- Encodes the on-disk ABI for IAG pages and the inode map control page.

Notable invariants and risks:
- `struct iag` is exactly one 4096-byte page and includes large fixed arrays; layout changes would affect disk compatibility.
- `wmap` and `pmap` are separate 1-bit-per-inode maps with different lifecycle meanings.
- `inosmap` and `extsmap` summarize 32 inode extents per word and must remain consistent with the full maps and extent descriptors.
- `IAGTOLBLK()` reserves logical block 0 for the dinomap control page and starts IAG pages at block group `iagno + 1`.

Research notes:
- This header is the schema behind `jfs_imap.c`; understanding the map/list fields here is necessary to follow inode allocation and recovery behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_imap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_incore.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_incore.h

This header defines the JFS in-memory inode and superblock private structures plus helper macros for locks, commit flags, and type-safe accessors.

Key responsibilities:
- Defines `JFS_SUPER_MAGIC`.
- Defines `struct jfs_inode_info`, embedding the VFS inode plus JFS-specific inode metadata: fileset, mode flags, saved uid/gid, inode extent descriptor, ACL/EA descriptors, creation time, directory index state, inode map pointer, commit flags, allocation group state, transaction lock IDs, synchronization primitives, quota pointers, device number, and type-specific inline storage.
- Overlays type-specific inode data through a union: regular files use an xtree root and inode-map pointer; directories use inline directory-table slots and a dtree root; symlinks/xattrs use inline data buffers.
- Defines lock helpers for the per-inode read/write semaphore and documents why it is redundant for directory mutation under VFS directory locking.
- Defines JFS commit flags such as dirty inode state, inline EA changes, directory-table changes, stale extents, and sync-list metadata.
- Defines lock subclass enums for commit mutex and read/write lock nesting.
- Defines `struct jfs_sb_info`, holding mount-wide state such as metadata inodes, log pointer, block size geometry, aggregate/log descriptors, UUIDs, commit state, inode generation/inostamp, block map, NLS table, recovery state, mount flags, uid/gid/umask overrides, and trim settings.
- Provides `JFS_IP()`, `JFS_SBI()`, `jfs_dirtable_inline()`, and `isReadOnly()` helpers.

Important interactions:
- Included by nearly every JFS implementation file.
- Pulls in xtree and dtree definitions because those roots are embedded directly in the inode-private union.
- Connects transaction code, inode-map code, directory code, extent code, quota, and VFS inode lifecycle through shared private state.

Notable invariants and risks:
- The unioned inline areas mirror on-disk dinode layout assumptions; wrong type interpretation can corrupt xtree roots, dtree roots, inline symlinks, or inline EAs.
- `commit_mutex` must be taken after starting a transaction, per the comment, because dirty inode commit can occur while another transaction waits.
- `jfs_dirtable_inline()` depends on `next_index` and the inline directory-table capacity; dtree code uses this to decide whether directory cookies live in the inode or in an xtree-backed table.
- `isReadOnly()` is tied to the presence of a log pointer, not directly to VFS mount flags.

Research notes:
- This is the main in-memory object model for JFS. Most cross-file behavior in this group passes through fields declared here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_incore.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_inode.c -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_inode.c

This file provides JFS inode flag translation and new inode allocation/initialization.

Key responsibilities:
- Translates JFS on-disk/private mode flags to VFS inode flags in `jfs_set_inode_flags()`, including immutable, append-only, no-atime, dirsync, and sync.
- Allocates a new VFS inode in `ialloc()`.
- Calls `diAlloc()` to allocate the corresponding JFS disk inode number and inode extent metadata.
- Inserts the inode into the inode cache with `insert_inode_locked()`.
- Initializes ownership, saved uid/gid, quotas, inherited JFS flags, directory/file/symlink-specific mode flags, timestamps, generation number, and JFS private fields.
- Handles allocation failure paths by dropping quotas, clearing link count, discarding new inodes, or releasing the inode.

Important interactions:
- Bridges VFS inode creation and the JFS inode map allocator in `jfs_imap.c`.
- Uses quota initialization/allocation after disk inode allocation and before returning the live inode.
- Relies on JFS mount-wide generation state (`gengen`) and parent `mode2` inheritance.
- Exports flag state used by VFS permission and write paths through `inode_set_flags()`.

Notable invariants and risks:
- Disk inode allocation occurs before quota allocation; later failures must unwind both VFS and quota state correctly.
- New directories set `IDIRECTORY` and clear inherited `JFS_DIRSYNC_FL`, while non-directories default to inline EA and sparse support.
- Symlinks explicitly drop immutable/append inheritance.
- `jfs_inode->mode2` combines private high-order flags with the VFS mode bits.

Research notes:
- This is the small but important handoff from VFS object creation into JFS-specific disk inode allocation and private inode initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_inode.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_inode.h

This header declares the JFS inode, file operation, export, ioctl, attribute, writeback, and block-mapping interfaces shared across the filesystem.

Key responsibilities:
- Declares `ialloc()` and `jfs_set_inode_flags()`.
- Declares file synchronization, ioctl, file attribute get/set, inode lookup, inode commit/writeback/eviction/dirty/truncation, zero-link cleanup, exportfs parent/fh lookup, block mapping, and setattr entry points.
- Exposes address-space operations, inode operations, file operations, symlink operations, and case-insensitive dentry operations.

Important interactions:
- Included by inode allocation, extent, imap, file, ioctl, export, and directory operation code.
- Provides the cross-file prototypes that connect JFS VFS operations to lower metadata code.

Notable invariants and risks:
- Many declarations here are VFS callbacks; prototype drift would break filesystem registration or operation-table initialization elsewhere.
- `jfs_get_block()` is the block-mapping bridge that ultimately depends on extent allocation/update behavior.

Research notes:
- This is the public internal header for JFS inode-facing code. The implementation is spread across multiple files outside this group.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_lock.h -->
# File Research: sources/os/linux/linux-stable/fs/jfs/jfs_lock.h

This header defines a small JFS locking/sleep helper for waiting on a condition protected by a spinlock.

Key responsibilities:
- Includes spinlock, mutex, and scheduler headers needed by JFS synchronization code.
- Defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`, which adds the current task to a wait queue, switches to `TASK_UNINTERRUPTIBLE`, drops the caller-provided lock while sleeping with `io_schedule()`, reacquires the lock, and exits when the condition becomes true.

Important interactions:
- Intended for JFS code paths where a wait condition is guarded by a spinlock and sleeping must temporarily release that lock.
- Uses caller-supplied lock/unlock command fragments rather than a typed lock object.

Notable invariants and risks:
- The macro sleeps uninterruptibly and requires the condition to become true or be woken by the relevant wait-queue protocol.
- Correctness depends on callers passing matching lock/unlock commands and holding the lock before entry.
- Because it is a macro with statement arguments, side effects in `cond`, `lock_cmd`, or `unlock_cmd` must be considered carefully.

Research notes:
- This is a low-level synchronization convenience header rather than a broad locking subsystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/jfs/jfs_lock.h -->