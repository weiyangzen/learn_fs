# subset-b-005680 research

Grouped research for JFS directory, extent, inode-map, inode, incore, filsys, and locking files. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.c

Purpose: implements the JFS directory B+-tree manager. It stores directory names as variable-length slot chains, keeps a sorted slot table per page for binary search, starts directories in the inode-resident `dtroot_t`, grows into external dtree pages, and optionally maintains the persistent directory index table used for stable `readdir` cookies and NFS-style resume. It also contains late corruption validators for dtree roots and pages.

Important APIs and functions: exported entry points are `dtSearch`, `dtInsert`, `dtDelete`, `dtModify`, `dtInitRoot`, `jfs_readdir`, `check_dtroot`, and `check_dtpage`. The split/growth path is factored through `dtSplitUp`, `dtSplitPage`, `dtExtendPage`, and `dtSplitRoot`. Deletion compaction uses `dtDeleteUp` and `dtRelink`. Traversal helpers are `dtReadFirst` and `dtReadNext`. Name handling and slot mutation live in `dtCompare`, `ciCompare`, `ciGetLeafPrefixKey`, `dtGetKey`, `dtInsertEntry`, `dtMoveEntry`, `dtDeleteEntry`, `dtTruncateEntry`, and `dtLinelockFreelist`. Persistent directory indexes are handled by `read_index_page`, `get_index_page`, `find_index`, `lock_index`, `add_index`, `free_index`, `modify_index`, `read_index`, and `add_missing_indices`.

Control flow: `dtSearch` uppercases the search key only for OS/2 case-insensitive mode, descends from block zero using binary search on each page's sorted table, pushes parent frames on a `btstack`, and returns either a pinned leaf/index for create/remove/rename or an inode result for lookup. `dtInsert` computes the number of slots needed, inserts directly if `freecnt` is sufficient, or delegates to `dtSplitUp`. `dtSplitUp` handles root splits, first-leaf extension below page size, full page splits, and router-key propagation up the stack. `dtDelete` first searches for the target, updates or frees the persistent readdir index, then deletes the entry directly or calls `dtDeleteUp` to remove now-empty pages. `jfs_readdir` has two paths: indexed directories use stable directory table entries and repair invalid entry indexes through `add_missing_indices`; legacy directories use a packed `(pn,index)` offset and `dtReadNext`.

State and persistence behavior: directory tree state is stored in inode inline `i_dtroot` until split and then in metapage-backed dtree extents. Non-root pages carry `self`, sibling pointers, `freelist`, `freecnt`, `nextindex`, `maxslot`, and `stblindex`. Directory entries store UTF-16LE name segments and either inode numbers in leaf entries or child PXDs in internal entries. With `JFS_DIR_INDEX`, every leaf entry also has a persistent directory-table index; the table starts in `i_dirtable`, then migrates into an xtree under the directory inode. Mutations acquire transaction locks with dtree linelocks, mark metapages dirty, update quota on directory page allocation/free, and use map locks for freed dtree extents. `dtInitRoot` may truncate an external directory index xtree and marks `COMMIT_Stale` when more cleanup is expected after commit.

Dependencies and integration: depends on JFS btree macros, metapages, the transaction manager (`txLock`, `txMaplock`, `txCommit`, linelocks), block map allocation (`dbAlloc`, `dbReAlloc`, `dbFree`), quota accounting, Unicode/NLS helpers, `jfs_incore` fields, and `jfs_filsys` constants. It integrates with VFS through `jfs_readdir`, with inode read/write through `i_dtroot`, `i_dirtable`, `next_index`, and `COMMIT_Dirtable`, and with `jfs_imap.c` because `copy_from_dinode` validates loaded directory roots via `check_dtroot`.

Risks and edge cases: split and delete logic must keep sibling links, parent router keys, sorted tables, freelists, quota counts, and persistent directory indexes synchronized; a missed `modify_index` can break `readdir` resume. Case-insensitive mode stores leaf names case-preserving but compares folded names, so router key compression must retain enough uppercase prefix information. `jfs_readdir` defends against invalid indexes, stale cookies, infinite free-index loops, DBCS expansion into its temporary page, and malformed slot tables. `dtExtendPage` relocation must rewrite directory indexes to the new block. Corruption validators catch bad freelist/slot-table metadata but are intentionally structural, not a full semantic tree verifier.

Test signals: exercise create/lookup/delete/rename across inline roots, first external leaf extension, full 4 KiB leaf split, internal split propagation, root collapse on deletion, indexed and legacy `readdir`, NFS cookie resume after deletion, case-insensitive lookup collisions, quota failure during page allocation, and corrupted freelist/stbl inputs returning `-EIO` rather than walking out of bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.h

Purpose: declares the on-disk/in-memory directory dtree layout and the exported directory tree APIs used by JFS directory operations.

Important APIs and types: defines `ddata_t`, `struct dtslot`, `struct idtentry`, `struct ldtentry`, `struct dir_table_slot`, `dtroot_t`, and `dtpage_t`. It declares `dtInitRoot`, `dtSearch`, `dtInsert`, `dtDelete`, `dtModify`, `jfs_readdir`, `check_dtroot`, and `check_dtpage`. Important macros include `DO_INDEX`, `PARENT`, `dtEmpty`, `DT_GETSTBL`, `NDTINTERNAL`, `NDTLEAF`, `NDTLEAF_LEGACY`, `DTSaddress`, and `addressDTS`.

Control flow: callers use the declared APIs as the directory lifecycle: initialize root, search before insert/remove/rename, mutate entries, and enumerate through `jfs_readdir`. The layout macros drive slot counts, sorted-table addressing, parent lookup, and persistent directory index addressing.

State and persistence behavior: this header defines the serialized directory structures. `dtroot_t` resides inside the JFS inode and carries the parent inode number, sorted table, freelist, and DASD accounting. `dtpage_t` describes external dtree pages with sibling pointers and a self PXD. `ldtentry` has a legacy format without persistent index and an indexed format with the `index` field. `dir_table_slot` records whether a readdir index is valid or free and stores either a leaf page/slot pair or a next-free/deleted index.

Dependencies and integration: depends on `jfs_btree.h`, JFS PXD types, `struct inode`, and superblock mount flags through `JFS_SBI`. It is consumed by directory operations, inode incore layout (`jfs_incore.h` embeds `dtroot_t` and `dir_table_slot`), inode serialization, and VFS directory file operations.

Risks and edge cases: slot-size constants must match the packed structures exactly or tree mutation will corrupt on-disk directories. `DO_INDEX` changes both entry format and `i_size` semantics, so mixed legacy/indexed handling must choose `NDTLEAF_LEGACY` versus `NDTLEAF` correctly. `DIREND` uses `INT_MAX`, making persistent cookie bounds important.

Test signals: compile-time layout users, indexed versus legacy directory creation, large names requiring continuation slots, parent lookup through `PARENT`, and directory root/page corruption checks are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.c

Purpose: implements allocation, hinting, and record-state updates for regular-file extents in the JFS xtree.

Important APIs and functions: exported functions are `extAlloc`, `extHint`, and `extRecord`. Internal helpers are `extBalloc` and `extRoundDown`.

Control flow: `extAlloc` rejects read-only filesystems, starts an anonymous transaction, serializes with `commit_mutex`, clamps the request to `MAXXLEN`, computes file block offset from page number, optionally uses the previous extent as a contiguous allocation/extend hint, calls `extBalloc`, charges quota, and records the allocation through `xtExtend` or `xtInsert`. On any xtree failure it frees both blocks and quota. `extHint` looks up the previous page-sized extent and returns an XAD hint only when it maps exactly one page. `extRecord` converts an allocated-not-recorded extent to recorded by calling `xtUpdate` under the commit mutex.

State and persistence behavior: persistent state is xtree XAD entries plus block allocation map and quota accounting. `extAlloc` may insert XADs with `XAD_NOTRECORDED` for delayed record semantics. It marks the inode dirty and commits immediately if `COMMIT_Synclist` was set by anonymous page tlocks. `extBalloc` also updates the inode's active allocation group for regular files in the fileset, maintaining `bmap->db_active` counters to guide later inode allocation away from actively growing AGs.

Dependencies and integration: depends on `jfs_incore`, `jfs_inode`, `jfs_superblock`, `jfs_dmap`, `jfs_extent.h`, xtree operations (`xtLookup`, `xtInsert`, `xtExtend`, `xtUpdate`), quota APIs, anonymous transaction startup, and JFS block-map allocation (`dbAlloc`, `dbFree`). It integrates with writepage/get-block paths that need real disk extents.

Risks and edge cases: allocation degrades by powers of two down to one page, so callers must tolerate shorter-than-requested extents. Hint extension is valid only when extent offset, length, physical address, and not-recorded state line up. Quota failure and xtree failure must roll back block allocation. `extHint` treats a non-page-sized previous extent as corruption and returns `-EIO`.

Test signals: writes that allocate from no hint, contiguous extension of a previous extent, fallback to smaller extents under fragmentation, quota denial, `abnr` allocation followed by `extRecord`, active AG counter changes, and corrupt xtree hint detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.h

Purpose: exposes the file extent allocation interface and the inode-local allocation hint macro.

Important APIs and types: declares `extAlloc`, `extHint`, and `extRecord`. `INOHINT(ip)` computes a block hint from the inode's disk inode extent descriptor (`ixpxd`) by returning the last block of that extent.

Control flow: file allocation callers obtain a hint with `extHint` or `INOHINT`, then call `extAlloc`; delayed or not-recorded extents are finalized through `extRecord`.

State and persistence behavior: the header itself stores no state, but its APIs mutate xtree extent records, the block map, quota state, and inode dirty/commit state through `jfs_extent.c`.

Dependencies and integration: depends on `JFS_IP`, PXD helpers, `struct inode`, `s64`, `xad_t`, and the xtree/block-map layer. Used by JFS block mapping and file write code.

Risks and edge cases: `INOHINT` assumes `ixpxd` is valid and nonzero; callers must only use it for initialized inodes. `extAlloc` can return a shorter allocation than requested, so users must check the output XAD length.

Test signals: compilation of extent users, normal writes, fragmented allocation fallback, not-recorded extent conversion, and invalid inode extent detection in the caller path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_extent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_filsys.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_filsys.h

Purpose: centralizes JFS filesystem option bits, fixed layout constants, block/page conversion macros, reserved disk offsets, reserved inode numbers, and size limits.

Important APIs and constants: mount/superblock flags include `JFS_UNICODE`, `JFS_ERR_*`, quota flags, `JFS_NOINTEGRITY`, `JFS_DISCARD`, commit mode flags, inline log flags, `JFS_BAD_SAIT`, `JFS_SPARSE`, DASD flags, endian/platform flags, and `JFS_DIR_INDEX`. Layout constants include `PSIZE`, `PBSIZE`, `DISIZE`, `IDATASIZE`, `IXATTRSIZE`, `IAG_SIZE`, `INOSPERIAG`, `INOSPEREXT`, `INOSPERPAGE`, block size limits, `MAXFILESIZE`, `JFS_LINK_MAX`, `MINJFS`, fixed block/byte offsets, aggregate reserved inodes, fileset reserved inodes, and `JFS_NAME_MAX`.

Control flow: this header has no executable control flow; it controls branching in other files via mount flag tests and by defining conversion arithmetic used during inode, directory, block-map, and superblock operations.

State and persistence behavior: constants define persistent on-disk geometry. Changing them would alter interpretation of superblocks, inode maps, directory inline areas, inode extents, and reserved metadata locations. Macros like `LBLK2PBLK`, `PBLK2LBLK`, `SIZE2PN`, and `SIZE2BN` translate between logical units used in memory and persisted block/page addressing.

Dependencies and integration: included by JFS directory, inode-map, inode, mount, superblock, dmap, and transaction code. It is tightly coupled to `jfs_dinode.h`, `jfs_imap.h`, `jfs_dtree.h`, and `jfs_xtree.h` layouts.

Risks and edge cases: fixed 4 KiB page assumptions pervade dtree, xtree, imap, and dinode logic. Reserved offset macros assume historical JFS aggregate layout. Flags such as `JFS_DIR_INDEX`, `JFS_OS2`, and `JFS_BAD_SAIT` materially change runtime behavior, so compatibility testing must cover old OS/2/legacy filesystems as well as Linux-created filesystems.

Test signals: mount option parsing, superblock read/write, inode-map addressing, directory indexing enablement, old filesystem compatibility, block-size conversion tests, and fsck/recovery validation of reserved metadata locations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_filsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.c

Purpose: implements the JFS disk inode allocation map manager. It loads and persists the imap control page, reads and writes dinodes, allocates and frees disk inodes and inode extents, updates working versus persistent inode bitmaps, handles special aggregate inodes, and rebuilds inode allocation-group metadata after filesystem extension.

Important APIs and functions: exported functions are `diMount`, `diUnmount`, `diSync`, `diRead`, `diReadSpecial`, `diWriteSpecial`, `diFreeSpecial`, `diWrite`, `diFree`, `diAlloc`, `diUpdatePMap`, and `diExtendFS`. Internal allocation helpers include `diAllocAG`, `diAllocAny`, `diAllocIno`, `diAllocExt`, `diAllocBit`, `diNewExt`, `diNewIAG`, `diIAGRead`, and `diFindFree`. Serialization helpers/macros are `IAGFREE_LOCK`, `AG_LOCK`, and inode map `IREAD/IWRITE` locks. `duplicateIXtree`, `copy_from_dinode`, and `copy_to_dinode` bridge special inode tables and VFS/JFS inode structures.

Control flow: mount reads the imap control page into `struct inomap`, initializes locks, and attaches it to the imap inode. Unmount optionally calls `diSync`, truncates the imap page cache, and frees the in-core map. `diRead` maps an inode number to IAG, extent, page, and relative dinode slot, then copies the dinode into the VFS inode. `diWrite` locates the dinode page, takes a transaction lock on the imap inode's metapage, copies changed inline btree roots, inline symlink/EA data, directory index table, and base dinode fields. `diAlloc` chooses an allocation policy based on directory/file status, parent AG, active growing files, and free counts, then tries same-IAG, same-AG, and other-AG allocation. `diFree` clears an inode from the working map and may free its entire inode extent or IAG, using a careful multi-buffer update plan before committing block-map free records. `diUpdatePMap` is called during transaction commit to update the persistent allocation bitmap and log-sync metadata.

State and persistence behavior: persistent state includes the dinomap control page, IAG pages, working maps (`wmap`), persistent maps (`pmap`), inode extent PXDs, per-AG free inode and free extent lists, the global free-IAG list, dinode pages, aggregate inode tables, and secondary AIT state. In-memory mirrors live in `struct inomap` plus atomics for total backed/free inodes. Working map changes happen at allocation/free time; persistent map changes are tied to commit/recovery semantics via `diUpdatePMap`. `diNewIAG` extends the inode map xtree transactionally, initializes a new IAG page, commits the imap inode, mirrors the extension into the secondary AIT through `duplicateIXtree`, and calls `diSync` to keep the control page current.

Dependencies and integration: depends on VFS inode/page APIs, metapages, quota flags for special inodes, block-map allocation/free, xtree mutation, transaction manager and logsync lists, superblock state, dinode layout, dtree root validation, and JFS mount flags. It integrates with inode allocation (`ialloc`), inode cache reads (`jfs_iget` path), writeback/commit (`diWrite`, `diUpdatePMap`), special metadata inode setup during mount, and online extendfs.

Risks and edge cases: lock ordering is critical: AG lock before IAG access, imap read/write lock around IAG reads/global map changes, and no rereading a held IAG buffer. Freeing an inode extent touches multiple lists and pages; failures must release all metapages and preserve map consistency. `diFree` deliberately releases AG lock only after transaction setup because a freed inode extent can be reused with different backing blocks. `diNewIAG` has a narrow failure window after extending the imap and before the control page is synced. `copy_from_dinode` rejects unexpected fileset IDs and validates directory roots with `check_dtroot`. UID/GID/umask mount overrides mean `copy_to_dinode` must preserve saved on-disk ownership/mode bits correctly.

Test signals: mount/unmount/sync of imap, reading stale or zero-link inodes, writing inline dtree/xtree roots, allocating files near parent IAG, directory allocation in preferred AG, active-AG avoidance, allocation from existing free inode, new inode extent allocation, new IAG extension, persistent-map update during commit, inode free that does and does not free the backing extent, secondary AIT failure setting `JFS_BAD_SAIT`, and extendfs rebuild count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.h

Purpose: defines the JFS inode allocation map disk/in-core structures, geometry constants, conversion macros, and exported inode-map APIs.

Important APIs and types: defines `struct iag`, `struct iagctl_disk`, `struct iagctl`, `struct dinomap_disk`, `struct dinomap`, and `struct inomap`. Constants include `EXTSPERIAG`, `IMAPBLKNO`, `SMAPSZ`, `EXTSPERSUM`, `PGSPERIEXT`, `MAXIAGS`, `MAXAG`, `AMAPSIZE`, and `SMAPSIZE`. Macros include `INOTOIAG`, `IAGTOLBLK`, `INOPBLK`, and shorthand aliases for `struct inomap` fields. Exports allocation, free, mount, unmount, read/write, persistent-map, extendfs, and special-inode functions.

Control flow: this header has no executable flow, but the structures define how `jfs_imap.c` walks from inode number to IAG page, to inode extent PXD, to dinode page and slot. The exported functions form the mount/read/allocate/free/write lifecycle for JFS inodes.

State and persistence behavior: `struct iag` is a 4 KiB persistent page containing AG list links, summary maps, counts, working and persistent bitmaps, and inode extent addresses for 4096 inodes. `dinomap_disk` is the persistent imap control page; `dinomap` and `inomap` are in-core mirrors with locks and atomics. The split between `wmap` and `pmap` is central to transaction recovery.

Dependencies and integration: includes `jfs_txnmgr.h` for transaction-related declarations and relies on JFS type/PXD helpers. Used by inode allocation, inode read/write, mount setup, dmap interaction, and transaction commit code.

Risks and edge cases: the on-disk structure sizes and endian fields must remain stable. Summary-map polarity is subtle: a set bit in `inosmap` means no free backed inodes are available for that extent, while `extsmap` tracks free extents. `MAXAG` and `MAXIAGS` bound online growth and allocation loops.

Test signals: structure-size/layout checks, inode number-to-IAG conversion, allocation/free count consistency, working versus persistent bitmap recovery, max AG/IAG boundary handling, and endian-safe mount/unmount of the control page.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_imap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_incore.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_incore.h

Purpose: defines the in-memory JFS inode and superblock private structures and their lock/flag helpers.

Important APIs and types: `struct jfs_inode_info` embeds VFS inode state plus JFS-specific fields: fileset/mode2, saved ownership, inode extent PXD, ACL/EA descriptors, creation time, directory index counter, imap pointer, commit flags, active AG, anonymous transaction list state, locks, and a union for file xtree root, directory table/dtree root, or symlink inline data. `struct jfs_sb_info` stores mount flags, metadata inodes, log, geometry, aggregate ID, log/fsck/ait PXDs, UUIDs, commit state, inode generation/stamp, block map, NLS table, and mount overrides. Helpers include `JFS_IP`, `JFS_SBI`, `jfs_dirtable_inline`, `isReadOnly`, lock macros, cflag bit helpers, and lock subclass enums.

Control flow: inline helpers provide object lookup and policy checks used throughout JFS. `jfs_dirtable_inline` controls whether directory indexes are stored in `i_dirtable` or external xtree pages; `isReadOnly` treats absence of a journal/log as read-only for metadata mutation paths.

State and persistence behavior: this header separates persistent mirrors (`i_xtroot`, `i_dtroot`, `i_dirtable`, `ixpxd`, ACL/EA descriptors) from runtime-only state (`commit_mutex`, `rdwrlock`, `xattr_sem`, cflags, active AG, anonymous tlock list fields). `jfs_sb_info` carries mount-session state and fields copied from or written back to disk metadata.

Dependencies and integration: depends on Linux mutex/rwsem/bitops/uuid APIs and JFS type, xtree, and dtree layouts. It is included by nearly every JFS implementation file and is the bridge between VFS `struct inode`/`super_block` and JFS internals.

Risks and edge cases: the union overlays very different persistent formats; code must select fields according to file type. Lock subclass usage matters for lockdep and for avoiding deadlocks between normal inodes, imap, and dmap. Commit flags such as `COMMIT_Dirtable`, `COMMIT_Stale`, and `COMMIT_Synclist` drive later writeback behavior and can cause persistence bugs if missed.

Test signals: inode allocation/read/write of regular files, directories, symlinks, inline EA updates, directory index migration, lockdep coverage for nested inode/map locks, lazy commit behavior, and read-only mount mutation rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_incore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.c -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.c

Purpose: implements JFS inode flag projection to VFS flags and allocation/initialization of new in-memory plus on-disk inodes.

Important APIs and functions: exported functions in this file are `jfs_set_inode_flags` and `ialloc`.

Control flow: `jfs_set_inode_flags` maps JFS private `mode2` bits such as immutable, append-only, noatime, dirsync, and sync to VFS inode flags. `ialloc` allocates a VFS inode with `new_inode`, asks `diAlloc` for a disk inode, inserts it locked into the inode cache, initializes ownership and quota, inherits selected JFS flags from the parent, sets directory versus non-directory mode bits, initializes timestamps, generation number, commit flags, ACL/EA descriptors, index counters, lock-related fields, and returns the new inode. Error paths drop quota, clear link count, discard or put the inode as appropriate.

State and persistence behavior: `ialloc` creates persistent allocation state indirectly through `diAlloc`, but this file initializes the in-memory fields that will later be committed by `diWrite`. It preserves saved UID/GID for mount override behavior, sets `mode2` for JFS-specific flags, zeroes ACL/EA descriptors and transaction fields, and increments the superblock generation generator.

Dependencies and integration: depends on VFS inode/quota APIs, `jfs_incore`, `jfs_imap`, `jfs_dinode` mode flags, and debug logging. It integrates with create/mkdir/symlink paths and with later writeback/commit code through the fields it initializes.

Risks and edge cases: failure after disk inode allocation but before quota allocation must not leak a live VFS inode. Symlinks intentionally clear inherited immutable/append flags. Directories get `IDIRECTORY` but clear `JFS_DIRSYNC_FL` in `mode2` while VFS mode still controls behavior. New fields in `jfs_inode_info` require updates here to avoid uninitialized runtime state.

Test signals: create regular files, directories, symlinks under parents with inherited flags, quota allocation failure, inode-cache insert failure, UID/GID mount override behavior, generation increment, and VFS flag projection from private mode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.h

Purpose: declares the JFS inode, file, directory, symlink, export, ioctl, writeback, truncate, block-mapping, fsync, and file-attribute interfaces used across the filesystem.

Important APIs and types: declares `ialloc`, `jfs_fsync`, file attribute get/set, `jfs_ioctl`, `jfs_iget`, commit/writeback/evict/dirty/truncate helpers, zero-link cleanup, NFS export helpers, `jfs_set_inode_flags`, `jfs_get_block`, `jfs_setattr`, and the address-space, inode-operation, file-operation, dentry-operation tables for JFS files/directories/symlinks/case-insensitive dentries.

Control flow: this header has no executable flow; it supplies the function surface used by VFS operation tables and JFS internal modules.

State and persistence behavior: the declared functions cover all inode lifecycle persistence points: allocation, lookup, dirtying, commit, writeback, eviction, truncation, block mapping, and metadata/file attribute changes.

Dependencies and integration: depends on Linux VFS types (`struct inode`, `file`, `dentry`, `fid`, `iattr`, `address_space_operations`, operation tables) and links JFS implementation files into VFS registration.

Risks and edge cases: signatures must track kernel VFS API changes, especially idmapped mount parameters and file attribute APIs. A mismatch in declared operation tables can break mount-time registration or case-insensitive dentry behavior.

Test signals: kernel build, VFS create/open/read/write/fsync/truncate/setattr/ioctl paths, exportfs file handle decode, symlink operation selection, and case-insensitive lookup behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_lock.h -->
# sources/distributed-fs/ceph-client/fs/jfs/jfs_lock.h

Purpose: provides a JFS-specific conditional sleep macro for wait queues protected by caller-supplied spinlock operations.

Important APIs and types: defines `__SLEEP_COND(wq, cond, lock_cmd, unlock_cmd)`. It includes Linux spinlock, mutex, and scheduler headers.

Control flow: the macro adds the current task to a wait queue, repeatedly sets `TASK_UNINTERRUPTIBLE`, checks the condition while the caller's lock is held, releases the lock and calls `io_schedule` if the condition is false, then reacquires the lock and retries. On success it restores `TASK_RUNNING` and removes the wait entry.

State and persistence behavior: runtime-only synchronization helper; it has no persistent on-disk state. It affects task state, wait queue membership, and lock ownership during I/O-oriented waits.

Dependencies and integration: intended for JFS code that needs to sleep until a lock-protected condition changes without open-coding waitqueue boilerplate. It depends on callers passing correct lock/unlock expressions and a condition safe to test under that lock.

Risks and edge cases: the wait is uninterruptible, so callers must ensure the condition will eventually become true. Mispaired lock commands can deadlock or sleep while still holding a spinlock. Because the macro evaluates caller-provided expressions, side effects in `cond`, `lock_cmd`, or `unlock_cmd` can be dangerous.

Test signals: lockdep coverage, I/O wait paths that use this macro, stress under contention, and shutdown/error paths that must wake blocked tasks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/jfs_lock.h -->
