# Group Research: group_1298_netbsd_src_sources_os_bsd_netbsd_src_sys_ufs_ufs_ufs_lookup_c_sourc_ef3d7ec778cf

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_lookup.c

This file implements core UFS directory lookup and directory-entry mutation helpers. It is shared by UFS-family vnode operations for create, delete, link, mkdir, rename, whiteout, directory compaction, and empty-directory checks.

Key responsibilities:
- Resolve pathname components in UFS directories through namecache, optional `UFS_DIRHASH`, and linear scans.
- Record mutation metadata in `inode.i_crap` as `struct ufs_lookup_results`.
- Find reusable directory slots, compact directory blocks, grow directories, and optionally truncate trailing unused directory space.
- Insert, remove, and rewrite `struct direct` directory entries with byte-order and old/new directory format handling.
- Validate directory entries and report bad directory structure.
- Provide `ufs_blkatoff` for reading the buffer that contains a directory offset.

Important functions:
- `ufs_lookup`: Main VOP lookup path. It enforces execute permission, readonly restrictions for delete/rename, namecache lookup, exclusive-lock retry (`ENOLCK`), dirhash/linear search, whiteout handling, slot accounting, DELETE/RENAME/CREATE semantics, and namecache insertion.
- `slot_*` helpers: Track free space and determine whether insertion needs a fresh directory block or compaction.
- `ufs_can_delete`: Enforces write/delete-child access and sticky-directory rules.
- `ufs_dirbad` / `ufs_dirbadentry`: Report and validate bad entries, including record length, block containment, advertised name length, and NUL termination.
- `ufs_makedirentry`: Builds a new `struct direct` for a component name and inode.
- `ufs_direnter`: Dispatches insertion to `ufs_dirgrow` or `ufs_dircompact`.
- `ufs_dirremove`: Removes or whiteouts an entry and decrements the target inode link count.
- `ufs_dirrewrite`: Repoints an existing entry and decrements the old inode link count.
- `ufs_dirempty`: Accepts only empty slots, whiteouts, `.`, and `..` with the expected parent.
- `ufs_blkatoff`: Reads the filesystem block containing an offset, with optional modify marking and simple readahead.

Important interactions:
- Used directly by `ufs_vnops.c` and `ufs_rename.c`.
- Uses `UFS_BALLOC`, `UFS_TRUNCATE`, `UFS_UPDATE`, `UFS_WAPBL_UPDATE`, `ufsdirhash_*`, `cache_lookup`, `cache_enter`, and `vcache_get`.
- The lookup-result fields are validated by callers via `UFS_CHECK_CRAPCOUNTER`.

Notable behavior and risks:
- Namecache misses under a non-exclusive directory lock return `ENOLCK` so callers can retry with stronger locking.
- Directory mutation helpers have asymmetric link-count behavior: `ufs_direnter` does not increment target links, while `ufs_dirremove` and `ufs_dirrewrite` decrement old/removed inode links.
- Several comments document old API baggage: unused parameters, fragile `i_crap` storage, and limited recovery if buffer writes fail after link counts change.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.c

This file is the shared quota front end for UFS quota v1 and quota v2. It routes accounting and `quotactl` operations to the active quota implementation and manages the in-core `dquot` cache.

Key responsibilities:
- Initialize/free per-inode quota pointers.
- Dispatch block and inode quota accounting to v1 or v2 implementations.
- Implement generic `quotactl` command handling and authorization.
- Manage the global dquot hash table, pool cache, mutex, and condition variable.
- Create, find, reference, release, sync, and destroy in-core dquot objects.

Important functions:
- `ufsquota_init` / `ufsquota_free`: Initialize or release all quota references attached to an inode.
- `chkdq` / `chkiq`: Skip snapshots, then dispatch block or inode usage updates to `chkdq1`/`chkdq2` and `chkiq1`/`chkiq2`.
- `quota_handle_cmd`: Switches over `QUOTACTL_*` operations and calls typed handlers.
- `quota_handle_cmd_stat`, `idtypestat`, `objtypestat`: Report quota implementation metadata, ID types, and object types.
- `quota_handle_cmd_get` / `put` / `del`: Enforce authorization and delegate quota value lookup, update, and deletion.
- Cursor handlers: Expose quota2 iteration operations through `QUOTACTL_CURSOR*`; v1 generally returns `EOPNOTSUPP`.
- `dqinit`, `dqreinit`, `dqdone`: Manage global quota cache infrastructure.
- `getinoquota`: Attaches user/group dquots to an inode, refreshing them if UID/GID changed.
- `dqget`: Finds or allocates a cached dquot and loads implementation-specific backing state with `dq1get` or `dq2get`.
- `dqref` / `dqrele`: Maintain dquot references and sync modified dquots before final release.
- `qsync`: Dispatches quota sync to v1 or v2.

Important interactions:
- Called from vnode permission, ownership, allocation, and mount paths.
- Uses mount flags `UFS_QUOTA` and `UFS_QUOTA2` to select implementation.
- Coordinates with `ufs_quota1.c`, `ufs_quota2.c`, and `ufsmount.h` quota fields.

Notable behavior and risks:
- `dqget` handles races where another thread allocates the same dquot while the current thread temporarily drops `dqlock`.
- `dqrele` loops while the last referenced dquot is dirty, syncing before removing it from the hash.
- Quota file vnodes are skipped in `getinoquota` to avoid deadlocks from recursively quota-accounting quota files.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.h

This header defines the shared in-core quota structures and function prototypes used by UFS quota v1, quota v2, and common quota dispatch code.

Key responsibilities:
- Include on-disk quota v1 and v2 definitions.
- Define `struct dquot`, the common cached quota object.
- Define the quota2 disk-location descriptor embedded in dquots.
- Document dquot locking ownership and lock order.
- Provide shorthand macros for v1 quota fields and v2 entry locations.
- Declare shared quota globals and all v1/v2 helper functions.

Important structures and macros:
- `struct dq2_desc`: Logical block number and block offset of a quota2 entry.
- `struct dquot`: Hash linkage, flags, type, reference count, ID, mount pointer, interlock, and union of v1 `dqblk` or v2 disk-location descriptor.
- `DQ_MOD`: Dquot has modified state needing sync.
- `DQ_FAKE`: Dquot carries no real limits, only usage.
- `DQ_WARN(ltype)`: Warning-state bit for a block/file limit class.
- `NODQUOT`: Null quota pointer sentinel.
- `dq_bhardlimit`, `dq_curblocks`, `dq_itime`, etc.: v1 field aliases.
- `dq2_lblkno`, `dq2_blkoff`: v2 location aliases.

Important interactions:
- `ufs_quota.c` owns global dquot cache lifecycle and uses this structure for both implementations.
- `ufs_quota1.c` uses the `dq_un.dq1_dqb` part for flat-file quota records.
- `ufs_quota2.c` uses the `dq2_desc` part to locate quota2 entries in on-disk hash lists.

Notable behavior:
- Lock order is explicitly documented as `dq_interlock -> dqlock` and `dq_interlock -> dqvp`.
- The header is the ABI boundary between generic UFS quota dispatch and implementation-specific quota v1/v2 code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota1.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota1.c

This file implements legacy UFS quota v1. Quota data is stored as fixed-size `struct dqblk` records in per-type quota files, indexed directly by user or group ID.

Key responsibilities:
- Enforce block and inode limits for quota v1.
- Update v1 usage counters and warning flags.
- Turn quota v1 files on and off.
- Read and write v1 dquot records from quota files.
- Convert between legacy `dqblk` state and fs-independent `quotaval` commands.
- Sync dirty dquots during mount sync and final release.

Important functions:
- `chkdq1`: Applies block usage deltas. Negative deltas reduce usage and clear warnings; positive deltas check hard/soft limits unless `FORCE`.
- `chkdqchg`: Checks block hard limits and soft-limit grace expiration, emitting user warnings.
- `chkiq1`: Applies inode usage deltas with the same negative/positive split.
- `chkiqchg`: Checks inode hard limits and soft-limit grace expiration.
- `quota1_umount`: Flushes vnodes and turns off all active v1 quota files.
- `quota1_handle_cmd_quotaon`: Opens the quota file, rejects WAPBL logging, marks the vnode system, saves credentials, initializes grace defaults, and attaches dquots to active writable vnodes.
- `quota1_handle_cmd_quotaoff`: Marks closing state, detaches dquots from all active vnodes, closes the quota file, frees credentials, and clears mount quota flags when appropriate.
- `quota1_handle_cmd_get`: Returns block or file quota values, using ID 0 as default/grace source for `QUOTA_DEFAULTID`.
- `quota1_handle_cmd_put`: Updates limits and grace periods, preserving current usage and recalculating expiration when crossing soft limits.
- `q1sync`: Walks mount vnodes and syncs modified dquots.
- `dq1get`: Reads a `dqblk` from the quota file; a missing record becomes a zeroed quota.
- `dq1sync`: Writes a dirty `dqblk` back to the quota file and clears `DQ_MOD`.

Important interactions:
- Uses common `dqget`, `dqrele`, `getinoquota`, `dqlock`, and `dqcv`.
- Mutates `ufsmount` fields `um_quotas`, `um_cred`, `umq1_btime`, `umq1_itime`, and `umq1_qflags`.
- V1 cannot be used with `-o log`/WAPBL journaling in this implementation.

Notable behavior and risks:
- Limit encoding maps `QUOTA_NOLIMIT` and values beyond 32-bit range to zero, matching v1’s 32-bit restriction.
- Quota-off waits for open/close transitions and detaches quota references from every vnode before closing the quota file.
- A large disabled `#if 0` block preserves older whole-`dqblk` and usage-setting routines but they are not active.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota1.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota2.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota2.c

This file implements UFS quota v2. Quota entries live in quota files with a header, default entry, hash lists, and free lists. The implementation supports journaled allocation/update of quota entries and cursor-based iteration.

Key responsibilities:
- Enforce block and file quota2 limits with shared limit-checking logic.
- Locate, allocate, delete, and update quota2 entries in on-disk hash/free-list structures.
- Convert quota2 on-disk values to and from fs-independent `quotaval`.
- Implement `quotactl` get/put/delete and cursor iteration for quota2.
- Track quota2 entry locations in `struct dquot`.
- Provide mount unmount cleanup for quota2 files.

Important functions:
- `getq2h`: Reads and validates the quota2 header block.
- `getq2e`: Reads a quota2 entry by logical block and block offset.
- `quota2_walk_list`: Walks a quota2 linked list, optionally allowing callbacks to modify parent pointers.
- `quota2_q2ealloc`: Allocates a free quota entry, extending the quota file if needed, initializes it from the default entry, and inserts it into the hash list.
- `getinoquota2`: Gets all relevant dquots for an inode, locks them, optionally allocates missing on-disk entries, and returns buffers/entry pointers.
- `quota2_check`: Shared block/file accounting path used by `chkdq2` and `chkiq2`; handles negative deltas, limit checks, warnings, soft-limit crossing times, and usage updates.
- `quota2_handle_cmd_put`: Updates default limits or a specific ID’s quota entry inside a WAPBL transaction.
- `quota2_handle_cmd_del`: Resets one object type to defaults and frees the entry if it no longer carries usage or custom limits.
- `quota2_handle_cmd_get`: Reads default or ID-specific quota values.
- Cursor helpers: Validate cursor state, scan hash buckets, return block/file key-value pairs, skip ID types, test end state, and rewind.
- `dq2get`: Locates an existing quota2 entry and stores its disk location in the dquot.
- `q2sync` / `dq2sync`: No-op because quota2 writes are made directly when buffers are updated.

Important interactions:
- Uses `UFS_WAPBL_BEGIN/END`, `UFS_BALLOC`, `UFS_UPDATE`, `quota2_bwrite`, and byte-swap helpers.
- Shares `dqlock` with common dquot code to protect headers/lists and follows `dq_interlock -> dqlock` lock order.
- Uses `ufsmount` quota2 fields `umq2_bsize` and `umq2_bmask`.

Notable behavior and risks:
- Cursor iteration is two-pass: first gather keys under list protection, then fetch values by key without holding conflicting locks.
- If the quota2 hash size changes during cursor iteration, `EDEADLK` forces callers to restart.
- Corrupt quota headers or impossible entry offsets panic rather than returning ordinary I/O errors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_quota2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_readwrite.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_readwrite.c

This file implements UFS read/write operations for FFS through macro aliases. Regular files use UBC/page-cache I/O; directories and long symlinks use buffer-cache I/O.

Key responsibilities:
- Read regular files via `ubc_uiomove`.
- Read directories and long symlinks through filesystem block reads.
- Write regular files through UBC with block allocation and WAPBL transaction coverage.
- Write directories and long symlinks through buffer-cache allocation and `uiomove`.
- Update access/change/modify times and clear setuid/setgid bits after writes.
- Roll back file size and `uio` state on write errors.

Important functions:
- `ffs_read` via `READ`: Validates read state, dispatches directories to `BUFRD`, handles snapshots, bounds reads by inode size, supports direct I/O hints, and updates atime.
- `ffs_bufrd` via `BUFRD`: Buffer-cache read path with block mapping, one-block readahead, residual protection, and `uiomove`.
- `ufs_post_read_update`: Marks `IN_ACCESS` unless `MNT_NOATIME`; performs synchronous metadata update for `IO_SYNC`.
- `ffs_write` via `WRITE`: Handles append mode, append-only enforcement, maximum size, WAPBL transaction scope, fragment expansion, block/page allocation, UBC writes, page flushing, and final metadata update.
- `ffs_bufwr` via `BUFWR`: Writes directory/symlink data through `UFS_BALLOC`, updates inode size, invalidates leaked buffers on failed partial writes, and chooses sync/async/delayed writeback.
- `ufs_post_write_update`: Marks ctime/mtime and relatime atime, clears privileged mode bits if credentials lack retention authority, truncates back on error, restores `uio` state, and syncs metadata for `IO_SYNC`.

Important interactions:
- Uses FFS block macros (`ffs_lblkno`, `ffs_blksize`, etc.) through local macro aliases.
- Regular-file allocation uses `ufs_balloc_range` and `GOP_ALLOC`; buffer paths use `UFS_BALLOC`.
- WAPBL transaction coverage is intentionally broad for regular-file writes that allocate blocks.

Notable behavior and risks:
- The write path explains why WAPBL currently forces large single transactions for writes that may allocate blocks.
- On failed writes, `UFS_TRUNCATE` restores the original file size and rewinds the caller’s `uio`.
- Directory writes require `IO_SYNC`, exclusive vnode locking, and an already-held journal lock.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_rename.c

This file adapts UFS rename to NetBSD’s `genfs_sane_rename` framework. It supplies UFS-specific checks, directory entry mutations, ancestry walking, and lookup-result management.

Key responsibilities:
- Wrap old VOP rename arguments with the saner genfs rename API.
- Enforce UFS immutable/append constraints and credential checks.
- Move entries between directories, replace targets, or remove duplicate links.
- Adjust link counts for files, directories, old parents, and new parents.
- Rewrite `..` when a directory is reparented.
- Recalculate source lookup results when target insertion compacts the same directory block.
- Detect invalid ancestry moves by walking parent links.

Important functions:
- `ufs_sane_rename`: Calls `genfs_sane_rename` with UFS lookup-result storage.
- `ufs_rename`: VOP entry point through `genfs_insane_rename`.
- `ufs_gro_directory_empty_p`: Uses `ufs_dirempty`.
- `ufs_gro_rename_check_possible` / `ufs_gro_rename_check_permitted`: Delegate UFS-like flag and credential checks to genfs helpers.
- `ufs_gro_rename`: Performs the rename under WAPBL: temporary source link bump, target creation or rewrite, target cleanup, `..` rewrite for reparented directories, source lookup-result recalculation, and source removal.
- `ufs_rename_ulr_overlap_p`: Detects whether a target insertion slot overlaps the source lookup region.
- `ufs_rename_recalculate_fulr`: Rescans the affected directory block to recover the source offset and previous record length after compaction.
- `ufs_gro_remove`: Handles rename-over-self as a remove of one link.
- `ufs_gro_lookup`: Performs `relookup`, unlocks the found vnode, and copies `i_crap`.
- `ufs_gro_genealogy`: Walks `..` from target directory toward root to detect whether the source parent is an ancestor.
- `ufs_read_dotdot`: Reads and validates the `..` entry.
- `ufs_gro_lock_directory`: Locks a directory and fails if it appears already removed.

Important interactions:
- Uses `ufs_direnter`, `ufs_dirrewrite`, `ufs_dirremove`, `ufs_dirempty`, `ufs_blkatoff`, `ufs_bufio`, `vcache_get`, and WAPBL.
- The `genfs_rename_ops` table at the end wires all callbacks into the generic rename engine.

Notable behavior and risks:
- Comments explicitly call out fragile historical link-count asymmetries and incomplete rollback questions.
- Some error branches that might back out changes are disabled with `#if 0`.
- Removed directories are detected by zero size, with a comment questioning whether that is fully correct.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vfsops.c

This file contains the generic VFS-level helpers for UFS-family filesystems. It does not mount FFS itself; instead it provides shared operations used by concrete UFS consumers.

Key responsibilities:
- Start a UFS filesystem.
- Return root and arbitrary inode vnodes.
- Dispatch filesystem quota control operations.
- Convert validated file handles to vnodes.
- Initialize, reinitialize, and tear down shared UFS resources.
- Provide the UFS kernel module command entry point.

Important functions:
- `ufs_start`: Placeholder start operation; currently no work.
- `ufs_root`: Loads `UFS_ROOTINO` with requested lock type.
- `ufs_vget`: Uses `vcache_get` and then locks the vnode.
- `ufs_quotactl`: If quota support is compiled in, marks the mount busy, serializes through `mnt_updating`, and calls `quota_handle_cmd`.
- `ufs_fhtovp`: Generic file-handle-to-vnode helper after lower filesystem validation; rejects stale inodes by generation, zero mode, or removed directory size.
- `ufs_init`: One-time shared initialization for direct-entry pool cache, quotas, dirhash, and extended attributes.
- `ufs_reinit`: Rehashes quota state after vnode table sizing changes.
- `ufs_done`: One-time teardown for quotas, direct-entry cache, dirhash, and extattrs.
- `ufs_modcmd`: Kernel module init/fini entry point.

Important interactions:
- `ufs_direct_cache` is used heavily by directory creation/link/rename code.
- Quota support is conditional on `QUOTA` or `QUOTA2`.
- Dirhash and extended attributes are initialized only when compiled in.
- Module dependency includes `wapbl` when WAPBL is compiled.

Notable behavior:
- `ufs_initcount` makes shared initialization idempotent across multiple UFS-family modules.
- `ufs_quotactl` keeps quota operations under mount update serialization because they may alter mount quota state and call authorization logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vnops.c

This file implements the generic UFS vnode operations for metadata, namespace mutations, directories, symlinks, special/fifo wrappers, vnode initialization, allocation, and buffer-I/O helpers.

Key responsibilities:
- Create, mknod, remove, link, mkdir, rmdir, symlink, readlink, whiteout, and readdir operations.
- Implement access checks, getattr, setattr, chmod, and chown.
- Integrate quota accounting, ACL checks/inheritance, WAPBL updates, and namecache updates.
- Initialize special/fifo vnode operations and device aliases.
- Provide UBC allocation and buffer-I/O wrappers used by other UFS code.

Important functions:
- `ufs_create` / `ufs_mknod`: Use lookup results in `i_crap`, call `ufs_makeinode`, end the WAPBL transaction, and unlock new vnodes.
- `ufs_open` / `ufs_close`: Enforce append-only open semantics and update times on close.
- `ufs_accessx`: Combines readonly/snapshot/immutable/quota checks with POSIX.1e, NFSv4 ACL, or Unix permission checks.
- `ufs_getattr`: Flushes pending times and exports UFS1/UFS2 inode attributes, timestamps, flags, bytes, type, and filerev.
- `ufs_setattr`: Handles flags, ownership, size, timestamps, birthtime, and mode updates with WAPBL, authorization, truncation, and cache identity refresh.
- `ufs_chmod` / `ufs_chown`: Apply authorization, ACL synchronization, quota transfer, mode/owner updates, and cache identity updates.
- `ufs_remove`: Removes non-directory entries using lookup results and `ufs_dirremove`.
- `ufs_link`: Increments link count, writes inode, inserts new directory entry, and rolls back on insertion failure.
- `ufs_whiteout`: Creates or deletes directory whiteout entries for supported directory formats.
- ACL inheritance helpers: Apply POSIX.1e or NFSv4 inherited ACLs to new directories/files.
- `ufs_mkdir`: Allocates a directory inode, initializes `.` and `..`, updates parent link count, writes directory contents, and enters the parent entry.
- `ufs_rmdir`: Verifies emptiness, removes the parent entry, updates link counts, truncates the removed directory, and purges caches.
- `ufs_symlink` / `ufs_readlink`: Store/read short symlinks inline and long symlinks via buffer I/O, preserving historical off-by-one compatibility.
- `ufs_readdir`: Converts on-disk `struct direct` entries to user `struct dirent`, handles byte swapping, produces cookies, and advances offsets by physical directory positions.
- `ufs_strategy`: Maps logical to physical blocks, calls device strategy, and applies WAPBL replay reads when needed.
- `ufs_vinit`: Assigns vnode type, special/fifo ops, root flag, device numbers, and modrev.
- `ufs_makeinode`: Shared file creation helper that allocates an inode, writes it before the directory entry, applies ACL inheritance, inserts the directory entry, and enters namecache.
- `ufs_gop_alloc`, `ufs_gop_markupdate`, `ufs_bufio`: Page-cache allocation, update marking, and typed buffer read/write wrapper.

Important interactions:
- Depends on lookup results from `ufs_lookup.c`.
- Calls quota functions through `chkdq`/`chkiq`.
- Calls filesystem-specific operations through `UFS_*` macros from `ufsmount.h`.
- Uses WAPBL around metadata and directory operations.
- Integrates with specfs, fifofs, genfs, UBC/UVM, ACL helpers, and optional dirhash.

Notable behavior and risks:
- Many namespace operations rely on `i_crap` lookup results remaining valid while the directory remains locked.
- `ufs_readdir` intentionally reads whole directory blocks and may rescan entries on later calls because `dirent` records can be larger than on-disk directs.
- Short symlink comparison uses historical `< um_maxsymlinklen` behavior, intentionally preserving existing filesystem image compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_wapbl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_wapbl.h

This header defines UFS integration points for WAPBL journaling. It contains superblock journal constants and macros that compile to real journaling operations when WAPBL is enabled or no-ops otherwise.

Key responsibilities:
- Define journal metadata values stored in UFS superblocks.
- Describe supported journal allocation locations.
- Define journal creation/clear flags and journal size bounds.
- Wrap WAPBL begin/end/update/assert/register operations behind UFS macros.
- Provide no-op fallbacks when WAPBL support is not compiled in.

Important constants:
- `UFS_WAPBL_VERSION`: Journal metadata version.
- `UFS_WAPBL_JOURNALLOC_NONE`: No journal.
- `UFS_WAPBL_JOURNALLOC_END_PARTITION`: Journal at end of partition, with locator slots for address/count/block size.
- `UFS_WAPBL_JOURNALLOC_IN_FILESYSTEM`: Journal inside filesystem, with locator slots for address/count/block size/inode.
- `UFS_WAPBL_FLAGS_CREATE_LOG` and `UFS_WAPBL_FLAGS_CLEAR_LOG`: Superblock journal action flags.
- `UFS_WAPBL_JOURNAL_SCALE`, `MIN`, `MAX`: Default and bounded journal sizing.

Important macros/functions:
- `ufs_wapbl_begin` / `ufs_wapbl_end`: Inline wrappers around `wapbl_begin` and `wapbl_end` if the mount has a journal.
- `UFS_WAPBL_BEGIN` / `UFS_WAPBL_END`: Standard transaction wrappers used throughout UFS code.
- `UFS_WAPBL_UPDATE`: Calls `UFS_UPDATE` only when journaling is present.
- `UFS_WAPBL_JLOCK_ASSERT` / `JUNLOCK_ASSERT`: Diagnostic lock-state assertions.
- `UFS_WAPBL_REGISTER_INODE`, `UNREGISTER_INODE`, `REGISTER_DEALLOCATION`, `UNREGISTER_DEALLOCATION`: Journal registration hooks for inode and block deallocation tracking.

Important interactions:
- Included by lookup, rename, read/write, quota2, and vnode operations.
- Bridges generic UFS code and the kernel WAPBL subsystem without forcing all builds to include WAPBL behavior.

Notable behavior:
- Without WAPBL, transaction begin always returns 0 and update/register macros are no-ops or return 0.
- A comment questions whether the 64 MB journal maximum is too restrictive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufs_wapbl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufsmount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufsmount.h

This header defines mount arguments, the common in-kernel `struct ufsmount`, filesystem dispatch operations, and UFS mount flags used by UFS-family filesystems.

Key responsibilities:
- Define userspace mount argument structures for UFS and MFS.
- Define the kernel-private mount state shared by FFS, LFS, ext2fs, and related UFS code.
- Store common device, superblock, quota, extended attribute, block geometry, symlink, directory, snapshot, and discard state.
- Define the `struct ufs_ops` method table for filesystem-specific operations.
- Provide macros that dispatch common UFS code to filesystem-specific implementations.
- Define UFS-specific mount flags, filesystem type IDs, quota transition flags, and byte-swap/format helpers.

Important structures:
- `struct ufs_args`: Block device path for UFS mounts.
- `struct mfs_args`: MFS mount parameters, including exported name, base address, and size.
- `struct ufsmount`: Holds mount pointer, device identifiers/vnode, filesystem type, flags, superblock union, extattr state, quota vnodes/credentials, indirect block geometry, quota v1/v2 state union, oldfs compatibility, max symlink length, directory block size, max file size, snapshot data, operation table, and discard data.
- `struct ufs_ops`: Filesystem-specific callbacks for inode times, update, truncate, balloc, snapshot gone, buffer read, and buffer write.

Important macros:
- `VFSTOUFS`: Converts `struct mount` to `struct ufsmount`.
- `UFS_OPS`, `UFS_ITIMES`, `UFS_UPDATE`, `UFS_TRUNCATE`, `UFS_BALLOC`, `UFS_SNAPGONE`, `UFS_BUFRD`, `UFS_BUFWR`: Common dispatch layer used throughout UFS code.
- `UFS_NEEDSWAP`, `UFS_ISAPPLEUFS`, `UFS_QUOTA`, `UFS_QUOTA2`, `UFS_EA`: UFS-specific mount flags.
- `UFS1`, `UFS2`: Filesystem type identifiers.
- `QTF_OPENING`, `QTF_CLOSING`: Quota v1 transition state.
- `MNINDIR`, `blkptrtodb`: Block mapping helpers.
- `FSFMT`: Tests whether old directory format without `d_type` is in use.

Important interactions:
- All files in this group depend on `ufsmount.h` for mount state and `UFS_*` dispatch.
- Concrete filesystems populate `um_ops`; common UFS code remains mostly filesystem-neutral.

Notable behavior:
- Quota v1 and quota v2 share storage through a union because their mount-level state differs.
- The superblock pointer is also a union so the same mount wrapper can support FFS, LFS, ext2fs, and CHFS-style users.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/ufs/ufsmount.h -->