# Group Research: group_853_linux_sources_os_linux_linux_fs_xattr_c_sources_os_linux_linux_fs_xf_17538b43cd40

Scope confirmed against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xattr.c -->
# File Research: sources/os/linux/linux/fs/xattr.c

Implements Linux VFS extended attribute dispatch, syscall entry points, permission checks, security-module integration, POSIX ACL routing, and generic in-memory simple-xattr helpers.

Key behavior:
- Resolves xattr names to filesystem-provided `struct xattr_handler` entries via `inode->i_sb->s_xattr` and `IOP_XATTR`.
- Enforces namespace-specific access rules:
  - `security.*` and `system.*` are left mostly to filesystem/LSM logic.
  - `trusted.*` requires `CAP_SYS_ADMIN`.
  - `user.*` is limited by inode type and sticky-directory ownership rules.
  - writes reject immutable, append-only, and unmapped-id inodes.
- Provides VFS set/get/list/remove APIs:
  - `vfs_setxattr`, `__vfs_setxattr_locked`, `__vfs_setxattr_noperm`, `__vfs_setxattr`.
  - `vfs_getxattr`, `vfs_getxattr_alloc`, `__vfs_getxattr`.
  - `vfs_listxattr`.
  - `vfs_removexattr`, `__vfs_removexattr_locked`, `__vfs_removexattr`.
- Handles `security.*` specially:
  - set path clears `S_NOSEC` and can fall back to `security_inode_setsecurity`.
  - get path calls `security_inode_getsecurity` before falling back to filesystem xattrs.
  - list path can synthesize LSM security labels if the filesystem lacks `listxattr`.
- Routes POSIX ACL xattr names away from normal handlers into ACL helpers.
- Converts `security.capability` values through `cap_convert_nscap` for idmapped mounts.
- Breaks inode delegations before mutating xattrs and retries after waiting.
- Implements all legacy and `*xattrat` syscalls:
  - `setxattrat`, `getxattrat`, `listxattrat`, `removexattrat`.
  - pathname, symlink-no-follow, and fd/`AT_EMPTY_PATH` variants.
- Copies user xattr names and values with explicit `XATTR_SIZE_MAX` and `XATTR_LIST_MAX` handling.
- Emits audit and fsnotify events for file-based and successful mutation paths.
- Provides `generic_listxattr` and `xattr_full_name` helpers for filesystems with handler tables.
- Implements `simple_xattr` support:
  - lazy rhashtable allocation keyed by parent list and name.
  - RCU-safe lookup, replace, remove, list, and free paths.
  - optional per-inode limits for count and total value size.
  - listing filters privileged `trusted.*` and MAC labels supplied by LSMs.
  - cache cleanup asserts the hash table is empty before destruction.

Important interactions:
- Filesystems expose xattr namespaces by populating `super_block->s_xattr`.
- Security hooks wrap get/set/list/remove operations.
- Idmapped mounts affect ownership, capability xattr conversion, and write permission.
- `simple_xattr` is reusable infrastructure for pseudo and memory-backed filesystems needing xattrs without on-disk storage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/Kconfig -->
# File Research: sources/os/linux/linux/fs/xfs/Kconfig

Defines XFS filesystem configuration options.

Key behavior:
- Declares `XFS_FS` as a block-device filesystem module/builtin option selecting `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- Defines deprecated-format support toggles:
  - `XFS_SUPPORT_V4` for old `crc=0` filesystems, default off, documented for removal in September 2030.
  - `XFS_SUPPORT_ASCII_CI` for deprecated ASCII case-insensitive filesystems, default off, also documented for removal in September 2030.
- Defines optional user-visible features:
  - `XFS_QUOTA`.
  - `XFS_POSIX_ACL`.
  - `XFS_RT`, defaulting to `BLK_DEV_ZONED`, for realtime subvolume and zoned device support.
- Defines internal feature gates:
  - `XFS_DRAIN_INTENTS`.
  - `XFS_LIVE_HOOKS`.
  - `XFS_MEMORY_BUFS`.
  - `XFS_BTREE_IN_MEM`.
- Defines online maintenance features:
  - `XFS_ONLINE_SCRUB`, requiring `TMPFS` and `SHMEM`, selecting live hooks, intent draining, and memory buffers.
  - `XFS_ONLINE_SCRUB_STATS`, requiring debugfs.
  - `XFS_ONLINE_REPAIR`, requiring online scrub and selecting in-memory btrees.
- Defines debug/warning controls:
  - `XFS_WARN`.
  - `XFS_DEBUG`.
  - `XFS_DEBUG_EXPENSIVE`.
  - `XFS_ASSERT_FATAL`.

Important interactions:
- `XFS_RT` is required for zoned block device support.
- Online repair depends on online scrub and enables additional btree infrastructure.
- V4 and ASCII-CI support are explicit compatibility/attack-surface choices.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/Makefile -->
# File Research: sources/os/linux/linux/fs/xfs/Makefile

Defines the kernel build composition for the XFS module/object.

Key behavior:
- Adds include paths for XFS trace events and `libxfs`.
- Builds `xfs.o` when `CONFIG_XFS_FS` is enabled.
- Compiles `xfs_trace.o` first because trace macros are sensitive to ordering.
- Includes core `libxfs` objects first, including AG, allocation, attribute, bmap, btree, directory, inode, rmap, refcount, superblock, transaction reservation, and type logic.
- Adds realtime shared `libxfs` objects when `CONFIG_XFS_RT` is enabled.
- Adds high-level filesystem objects for I/O, buffers, attributes, directories, discard, errors, export, extent busy tracking, file operations, fsmap, mount, reflink, stats, superblock, sysfs, transactions, verification, and xattrs.
- Adds low-level log and transaction item objects.
- Adds optional quota, ACL, sysctl, compat ioctl, pNFS, DAX memory-failure, live hook, drain, memory-buffer, and in-memory btree objects based on config.
- Adds online scrub object groups under `CONFIG_XFS_ONLINE_SCRUB`.
- Adds online repair object groups under `CONFIG_XFS_ONLINE_REPAIR`.
- Adds realtime scrub/repair and quota scrub/repair files when corresponding features are enabled.

Important interactions:
- `libxfs/xfs_ag.o`, `xfs_ag_resv.o`, `xfs_alloc.o`, and `xfs_alloc_btree.o` from this group are core `libxfs` build inputs.
- Scrub and repair expand the build substantially and depend on Kconfig feature gates.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.c

Implements XFS allocation-group lifecycle, geometry calculation, grow/shrink support, and new AG header initialization.

Key behavior:
- `xfs_initialize_perag_data` reads every AGF/AGI to rebuild incore superblock counters for allocated/free inodes and free blocks.
- Detects impossible summary counts, marks filesystem counters sick, and fails mount with `-EFSCORRUPTED`.
- Allocates, inserts, and frees per-AG structures through generic `xfs_group` helpers.
- Computes AG block counts, including shorter final AGs.
- Computes valid AG inode ranges after static AG metadata and inode-cluster alignment.
- Updates the previous tail AG geometry during growfs recovery.
- Initializes new per-AG structures with kernel-only inode-cache and blockgc state.
- Prepares uncached buffers for new AG headers during growfs.
- Initializes:
  - secondary superblocks with `sb_inprogress`.
  - AGF headers and free-space counters.
  - AGFL blocks and null entries.
  - AGI headers and unlinked-inode buckets.
  - free-space btree roots.
  - inode btree roots.
  - rmap/refcount roots when enabled.
- Builds initial free-space records while excluding AG headers and internal log space.
- Builds initial rmap records for static metadata, btree roots, refcount root, and internal log.
- Implements `xfs_ag_shrink_space`:
  - validates tail AG state.
  - checks inode allocation constraints.
  - disables/reinitializes per-AG reservations.
  - allocates the to-be-removed tail range exactly from free space.
  - updates AGI/AGF lengths and perag geometry.
  - handles reservation rollback and shutdown on unrecoverable reservation errors.
- Implements `xfs_growfs_compute_deltas` to normalize requested data-block count into AG count and delta.
- Implements `xfs_ag_extend_space`:
  - extends AGI/AGF length.
  - frees newly added space into rmap and free-space btrees.
  - updates perag geometry.
- Implements `xfs_ag_get_geometry` for reporting AG length, inode counts, free blocks, and health.

Important interactions:
- Depends on AGF/AGI readers from allocation and inode allocation code.
- Uses rmap and free-space allocation code to materialize grow/shrink changes.
- Per-AG reservations must be reestablished around shrink operations.
- New AG initialization coordinates superblock, AG headers, free-space btrees, inode btrees, rmapbt, and refcountbt.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.h

Declares XFS per-allocation-group structures, state flags, reference helpers, geometry helpers, and grow/shrink interfaces.

Key behavior:
- Defines `struct xfs_ag_resv` for per-AG metadata block reservations:
  - originally reserved.
  - currently reserved.
  - originally requested.
- Defines `struct xfs_perag`, the incore AG cache:
  - embedded `struct xfs_group`.
  - AGF-derived free-space btree levels, freelist count, free blocks, longest extent, btree blocks.
  - AGI-derived allocated/free inode counters.
  - inode allocation search hints.
  - refcount btree level.
  - metadata and rmapbt reservations.
  - precalculated min/max valid AG inode numbers.
  - kernel-only inode cache, reclaim, filestream, repair-height, and blockgc state.
- Provides `to_perag`, `pag_group`, `pag_mount`, and `pag_agno` conversion helpers.
- Defines atomic per-AG state bits:
  - AGF initialized.
  - AGI initialized.
  - prefers metadata.
  - allows inodes.
  - AGFL needs reset.
- Declares perag initialization, freeing, counter reconstruction, and last-AG-size update functions.
- Provides passive and active perag reference wrappers around `xfs_group`.
- Provides perag iteration helpers, including wrap-around iteration with explicit restart and stop bounds.
- Declares AG geometry verification:
  - AG block number/range checks.
  - AG inode number checks.
  - internal-log containment check.
- Defines `struct aghdr_init_data` used by growfs AG-header initialization.
- Declares AG header init, shrink, grow delta computation, extend, and geometry-reporting functions.
- Provides AG-relative conversion helpers to filesystem block, disk address, and inode number.

Important interactions:
- `xfs_alloc.c`, `xfs_ag.c`, inode allocation, scrub, repair, and growfs code rely on the cached perag counters and state bits.
- Perag reference helpers enforce lifecycle semantics for allocation scans and AG mutation paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.c

Implements per-AG block reservations for metadata structures that must be able to grow without hitting ENOSPC.

Key behavior:
- Explains the reservation model:
  - reserve blocks per AG for metadata btree growth.
  - hide reservation space from global free-block accounting.
  - track per-AG reserved counters in memory.
  - account rmapbt specially because it lives in free space/AGFL-owned space.
- `xfs_ag_resv_critical` reports low-reservation conditions for metadata and rmapbt reservations using 10% and max-btree-height thresholds, plus error injection.
- `xfs_ag_resv_needed` reports blocks reserved for other reservation classes that must not be allocated away.
- `xfs_ag_resv_free` releases rmapbt and metadata reservations back to `fdblocks`, restoring `m_ag_max_usable` for AG 0.
- `__xfs_ag_resv_init`:
  - normalizes `ask >= used`.
  - computes hidden space by reservation type.
  - decrements global free blocks.
  - adjusts `m_ag_max_usable` for AG 0.
  - records asked, original reserved, and currently reserved values.
- `xfs_ag_resv_init` creates:
  - metadata reservations for refcountbt and finobt needs.
  - rmapbt reservations.
  - fallback behavior if finobt reservation cannot be fully established on older filesystems.
  - AGF initialization when active reservations exist.
  - `-ENOSPC` if reservations exceed AG free space.
- `xfs_ag_resv_alloc_extent` consumes reservation counters and updates transaction superblock accounting according to reservation type.
- `xfs_ag_resv_free_extent` replenishes reservation counters when blocks are freed and accounts leftover blocks to normal free space.

Important interactions:
- Uses reserve calculators from refcountbt, finobt, and rmapbt code.
- Allocation paths call reservation helpers after allocating or freeing extents.
- AG shrink temporarily frees and then reinitializes reservations to validate the new geometry.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.h

Declares XFS per-AG reservation APIs.

Key behavior:
- Exposes reservation lifecycle:
  - `xfs_ag_resv_init`.
  - `xfs_ag_resv_free`.
- Exposes reservation state queries:
  - `xfs_ag_resv_critical`.
  - `xfs_ag_resv_needed`.
- Exposes accounting hooks for allocation and free paths:
  - `xfs_ag_resv_alloc_extent`.
  - `xfs_ag_resv_free_extent`.
- Provides `xfs_perag_resv` inline mapper:
  - `XFS_AG_RESV_METADATA` maps to `pag_meta_resv`.
  - `XFS_AG_RESV_RMAPBT` maps to `pag_rmapbt_resv`.
  - other reservation types return `NULL`.

Important interactions:
- Included by allocator, AG grow/shrink code, and metadata btree code that must account against per-AG reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ag_resv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.c

Implements XFS free-space allocation, freeing, AGFL management, AGF/AGFL verification, reservation accounting, deferred extent freeing, and free-space btree query helpers.

Key behavior:
- Defines global allocator resources:
  - extent-free intent slab cache.
  - allocation workqueue pointer.
- Computes AGFL size, preallocated AG metadata blocks, refcount root placement, AGFL set-aside, and maximum usable AG allocation length.
- Wraps free-space btree lookup/update for bnobt and cntbt records.
- Converts and validates free-space records, marking btrees sick on corruption.
- Implements allocation candidate logic:
  - trims busy extents.
  - applies min/max AG block ranges.
  - applies alignment.
  - computes locality distance for near allocations.
  - adjusts length by `prod`/`mod`.
- Maintains `agf_longest` from the by-count btree when records affecting the largest extent change.
- Updates both free-space btrees when allocating from the beginning, end, middle, or entirety of a free extent.
- Verifies AGFL buffers:
  - CRC filesystems validate magic, uuid, seqno, entries, LSN, and checksum.
  - non-CRC filesystems skip full AGFL verification due to historical uninitialized entries.
- Reads AGFL buffers and marks AGFL sick on metadata errors.
- Updates AGF free-block counters and logs AGF fields.
- Implements exact allocation:
  - finds containing bnobt record.
  - rejects busy or too-small regions.
  - updates bnobt/cntbt.
- Implements near allocation:
  - uses cntbt and two bnobt cursors in parallel for size and locality.
  - retries after busy-extent flush.
  - falls back to largest usable extent when locality fails.
- Implements size allocation:
  - searches cntbt for large enough records.
  - settles for smaller largest records when necessary.
  - handles busy extents and retries.
- Implements free-space insertion/merge:
  - checks left/right contiguous neighbors.
  - merges with neither, one, or both neighbors.
  - keeps bnobt and cntbt synchronized.
  - updates counters, reservations, stats, and rmap.
- Computes allocator max btree levels and longest free extent after AGFL/reservation constraints.
- Computes minimum AGFL length needed for worst-case btree splits across bnobt, cntbt, and optional rmapbt.
- Decides whether an AG has enough free space for an allocation before fixing the freelist.
- Detects inconsistent AGFL indices and marks perag for reset.
- Resets corrupted AGFL state, warning that blocks were leaked and repair is needed.
- Schedules deferred extent frees using EFI items, including realtime validation and owner flags.
- Provides autoreap support for crash-safe unwritten-space allocation:
  - schedule paused free intent.
  - cancel by marking EFI cancelled.
  - commit by unpausing.
- `xfs_alloc_fix_freelist`:
  - reads/initializes AGF.
  - respects metadata-preferred AGs for user data.
  - checks available space.
  - resets bad AGFL state.
  - shrinks overfull AGFL by deferred freeing.
  - refills underfull AGFL from free space.
  - updates rmap and counters for AGFL movement.
- `xfs_alloc_get_freelist` and `xfs_alloc_put_freelist` pop/push AGFL blocks, update AGF ring indices, btree block counts, and perag counters.
- Verifies AGF headers:
  - magic/version.
  - uuid/LSN for CRC filesystems.
  - seqno and length.
  - AGFL indices/count.
  - free/longest counters.
  - btree levels and block counts.
  - rmap/refcount fields when enabled.
- Reads AGF and initializes perag cached AGF fields, including allocbt block accounting.
- Checks allocation arguments and enforces transaction AG lock ordering through `t_highest_agno`.
- Provides public allocation entry points:
  - `xfs_alloc_vextent_this_ag`.
  - `xfs_alloc_vextent_start_ag`.
  - `xfs_alloc_vextent_first_ag`.
  - `xfs_alloc_vextent_exact_bno`.
  - `xfs_alloc_vextent_near_bno`.
- Frees extents through `__xfs_free_extent` after freelist preparation, bounds validation, free-space btree insertion, and busy-extent insertion.
- Provides free-space btree query helpers:
  - range query.
  - query all.
  - record-presence classification.
  - AGFL walking.
- Creates and destroys the extent-free intent cache.

Important interactions:
- Works tightly with bnobt/cntbt btree operations from `xfs_alloc_btree.c`.
- Calls rmap updates for allocated/freed extents unless owner info requests skipping.
- Calls per-AG reservation helpers for metadata/rmapbt accounting.
- Uses extent-busy tracking to avoid reusing blocks still unsafe after transaction activity.
- Coordinates AGF/AGFL logging with transaction buffer logging.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.h

Declares XFS allocation/free-space APIs, flags, argument structures, and deferred free item structures.

Key behavior:
- Declares allocator workqueue and AGFL sizing.
- Defines `xfs_alloc_fix_freelist` flags:
  - trylock.
  - freeing mode.
  - no rmap updates.
  - no AGFL shrink.
  - check-only.
  - try busy flush.
- Defines `struct xfs_alloc_arg`, the central allocation request/result object:
  - transaction, mount, AGF buffer, perag.
  - target/result block fields.
  - min/max length, alignment, prod/mod, minleft, total.
  - AG block range constraints.
  - data type flags.
  - delayed-allocation/freelist result flags.
  - owner info and reservation type.
- Defines allocation data-type flags:
  - user data.
  - initial user data.
  - no busy extents.
- Declares free-space accounting helpers:
  - set-aside.
  - max usable.
  - longest free extent.
  - minimum freelist.
- Declares AGFL get/put, free extent, maxlevel computation, AGF logging, and AGF/AGFL readers.
- Declares allocation entry points:
  - this AG.
  - near block.
  - exact block.
  - start AG scan.
  - first AG scan.
- Declares btree lookup/get/query helpers for free-space records.
- Declares AGFL walker and `xfs_buf_to_agfl_bno` layout helper.
- Declares deferred free scheduling via `xfs_free_extent_later`.
- Defines deferred free flags:
  - skip discard.
  - realtime.
- Defines `struct xfs_extent_free_item`, the sorted deferred free list item.
- Defines EFI item flags for discard skipping, attr fork, bmap btree block, cancellation, and realtime.
- Declares autoreap schedule/cancel/commit helpers.
- Declares extent-free intent cache lifecycle.
- Declares AG length validation helper.

Important interactions:
- This header is the allocator contract consumed by bmap, rmap, refcount, AG grow/shrink, repair, and transaction code.
- Reservation type in `xfs_alloc_arg` connects allocation/free operations to per-AG reservation accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.c

Implements XFS free-space btree operations for the by-block-number btree and by-block-count btree.

Key behavior:
- Maintains a cursor slab cache for allocation btree cursors.
- Provides cursor duplication for bnobt and cntbt.
- Updates AGF root pointers and level counters when btree roots change, synchronizing perag cached levels.
- Allocates new btree blocks from the AGFL, marks them busy-reused, and increments global allocbt block count.
- Frees btree blocks back to the AGFL, marks them busy with discard skipped, and decrements global allocbt block count.
- Provides min/max record counts from mount geometry.
- Initializes keys, high keys, records, and root pointers from records/cursors.
- Implements bnobt comparisons by start block.
- Implements cntbt comparisons by block count, then start block.
- Verifies alloc btree blocks:
  - magic and CRC headers.
  - perag-aware tree level limits when AGF is initialized.
  - repair-height allowances during online repair.
  - mount maximum levels when perag is unavailable or uninitialized.
  - generic AG btree block structure.
- Defines buffer ops for bnobt and cntbt.
- Enforces key/record ordering:
  - bnobt records must be non-overlapping and start-block ordered.
  - cntbt records are ordered by length then start block.
- Defines `xfs_btree_ops` for bnobt and cntbt, including sick masks, stat offsets, buffer ops, key comparisons, allocation/free block hooks, and ordering checks.
- Initializes bnobt/cntbt cursors with held AG group references and AGF-derived tree levels.
- Commits staged btree roots for online repair/rebuild flows.
- Computes alloc btree records per block, maximum on-disk levels, and btree size estimates.
- Initializes and destroys the allocation btree cursor cache.

Important interactions:
- `xfs_alloc.c` uses these btree ops to search, allocate, free, merge, and query free-space extents.
- AGF fields are the persistent roots and height counters for both free-space btrees.
- Online repair can stage replacement free-space btrees before committing new roots.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.h

Declares XFS free-space btree layout macros and cursor/utility APIs.

Key behavior:
- Defines `XFS_ALLOC_BLOCK_LEN(mp)`, selecting CRC or non-CRC short btree block header length.
- Defines record, key, and pointer address macros for allocation btree blocks:
  - `XFS_ALLOC_REC_ADDR`.
  - `XFS_ALLOC_KEY_ADDR`.
  - `XFS_ALLOC_PTR_ADDR`.
- Declares bnobt and cntbt cursor constructors.
- Declares max-record calculation for alloc btree blocks.
- Declares allocation btree size estimation.
- Declares staged btree root commit for rebuild/repair.
- Declares maximum on-disk alloc btree height calculation.
- Declares cursor cache lifecycle functions.

Important interactions:
- Used by allocator code, AG header initialization, userspace/libxfs consumers, and online repair staging code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_alloc_btree.h -->