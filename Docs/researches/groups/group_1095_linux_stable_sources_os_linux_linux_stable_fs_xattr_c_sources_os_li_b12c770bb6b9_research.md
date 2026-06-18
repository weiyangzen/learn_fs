# Group Research: group_1095_linux_stable_sources_os_linux_linux_stable_fs_xattr_c_sources_os_li_b12c770bb6b9

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/xattr.c

## Purpose

Implements Linux VFS extended attribute handling. This file bridges the user ABI, VFS namespace policy, LSM hooks, filesystem xattr handlers, POSIX ACL special cases, delegation breaking, fsnotify, and generic in-memory xattr storage.

## Main Responsibilities

- Resolves xattr names to filesystem `struct xattr_handler` entries through `inode->i_sb->s_xattr`.
- Enforces VFS-level access policy for `security.*`, `system.*`, `trusted.*`, and `user.*`.
- Implements exported VFS helpers for set/get/list/remove xattrs:
  - `__vfs_setxattr`, `__vfs_setxattr_noperm`, `__vfs_setxattr_locked`, `vfs_setxattr`
  - `vfs_getxattr_alloc`, `__vfs_getxattr`, `vfs_getxattr`
  - `vfs_listxattr`
  - `__vfs_removexattr`, `__vfs_removexattr_locked`, `vfs_removexattr`
- Implements syscall paths for `setxattr`, `getxattr`, `listxattr`, `removexattr`, `l*`, `f*`, and `*xattrat` variants.
- Routes POSIX ACL xattr names to ACL helpers instead of regular xattr handlers.
- Provides `generic_listxattr` and the `simple_xattr` rhashtable-backed facility used by pseudo/simple filesystems.

## Key Control Flow

- `xattr_resolve_name` rejects bad/non-xattr-capable inodes, then matches namespace prefixes and passes only the suffix to handler callbacks.
- `xattr_permission` applies write rejection for immutable, append-only, and unmapped-id inodes; leaves `security.*` and `system.*` to filesystem/security code; restricts `trusted.*` to `CAP_SYS_ADMIN`; and restricts `user.*` by inode type and sticky-directory ownership.
- Set operations import the name and value, reject invalid flags, acquire write access to the mount, audit the target, and call either ACL setters or `vfs_setxattr`.
- `vfs_setxattr` converts file capabilities with `cap_convert_nscap`, locks the inode, calls security hooks, breaks delegations, invokes the filesystem or LSM security setter, and posts fsnotify/security notifications.
- Get operations cap user buffers at `XATTR_SIZE_MAX`, consult LSM security labels first for `security.*`, fall back to filesystem xattr handlers, copy results to userspace, and translate impossible oversize `-ERANGE` into `-E2BIG`.
- List operations cap buffers at `XATTR_LIST_MAX`, call `vfs_listxattr`, and copy NUL-separated names to userspace.
- Remove operations route ACL names to `vfs_remove_acl`, otherwise enforce write/security/delegation rules and invoke `handler->set(..., NULL, 0, XATTR_REPLACE)`.

## Simple Xattr Facility

- `simple_xattr_alloc`, `simple_xattr_free`, and `simple_xattr_free_rcu` manage variable-sized xattr objects.
- `simple_xattrs_init`, `simple_xattrs_alloc`, `simple_xattrs_lazy_alloc`, and `simple_xattrs_free` manage the backing rhashtable.
- `simple_xattr_get` performs RCU-protected lookup and length-or-copy retrieval.
- `simple_xattr_set` implements create, replace, remove, and upsert semantics. `value == NULL` means remove, unlike the VFS set path where size-zero is an empty value.
- `simple_xattr_set_limited` enforces per-inode count and total-size limits with speculative atomic accounting.
- `simple_xattr_list` combines POSIX ACL names, LSM security names, and stored simple xattrs while hiding `trusted.*` from unprivileged callers and suppressing MAC labels already supplied by LSM.

## Important Invariants and Edge Cases

- Empty values are valid xattr values in `__vfs_setxattr`; removal is represented by `NULL` value in remove paths.
- `import_xattr_name` rejects empty names and names that fill the fixed kernel buffer without termination as `-ERANGE`.
- `AT_EMPTY_PATH` support lets fd-based variants pass `pathname == NULL`.
- Delegation breaking uses retry loops around inode locking.
- Simple xattr writes require external serialization; the lookup/replace/remove sequence is not atomic by rhashtable locking alone.
- Lazy simple-xattr allocation publishes with store-release semantics and treats remove-without-storage as `-ENODATA` for replace or successful no-op otherwise.
- `generic_listxattr` intentionally excludes POSIX ACL entries; `vfs_listxattr` retains legacy ACL listing behavior through filesystem/listsecurity paths.

## Dependencies

VFS inode/path/file helpers, mount write accounting, audit, fsnotify, delegation breaking, LSM hooks, POSIX ACL helpers, rhashtable, RCU, atomics, `kvmalloc`/`kvfree`, and userspace copy helpers.

## Research Notes

This is the central Linux xattr policy and dispatch file. The highest-risk areas are namespace permission ordering, LSM fallback behavior for `security.*`, delegation retry handling, POSIX ACL special casing, userspace size bounds, and write serialization for `simple_xattr` mutation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/xfs/Kconfig

## Purpose

Declares Linux kernel configuration options for building XFS and optional XFS features.

## Main Configuration Items

- `XFS_FS`: tristate XFS support, depends on `BLOCK`, selects `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- `XFS_SUPPORT_V4`: opt-in support for deprecated non-CRC V4 filesystems, default `n`.
- `XFS_SUPPORT_ASCII_CI`: opt-in support for deprecated ASCII case-insensitive filesystems, default `n`.
- `XFS_QUOTA`: quota support, selects `QUOTACTL`.
- `XFS_POSIX_ACL`: ACL support, selects `FS_POSIX_ACL`.
- `XFS_RT`: realtime subvolume support, defaults to `BLK_DEV_ZONED`.
- Internal switches: `XFS_DRAIN_INTENTS`, `XFS_LIVE_HOOKS`, `XFS_MEMORY_BUFS`, and `XFS_BTREE_IN_MEM`.
- Online maintenance:
  - `XFS_ONLINE_SCRUB` depends on `TMPFS && SHMEM` and selects live hooks, drain intents, and memory buffers.
  - `XFS_ONLINE_SCRUB_STATS` depends on scrub and debugfs.
  - `XFS_ONLINE_REPAIR` depends on scrub and selects in-memory btrees.
- Debug controls: `XFS_WARN`, `XFS_DEBUG`, `XFS_DEBUG_EXPENSIVE`, and `XFS_ASSERT_FATAL`.

## Important Semantics

- V4 and ASCII case-insensitive formats are documented as deprecated, default-off as of September 2025, and planned for removal in September 2030.
- ASCII case-insensitive support is explicitly described as unsafe for UTF-8 names and mixed case-sensitivity attacks.
- Realtime support is mandatory for zoned block devices.
- Online repair requires secondary metadata such as reverse mappings and parent pointers.
- `XFS_WARN` enables lighter checks than full debug; `XFS_DEBUG` enables assertions and additional sanity checks; `XFS_ASSERT_FATAL` controls fatal behavior for debug assertions.

## Research Notes

This file defines the build-time feature surface for the XFS files in this group. It explains why allocator and AG code contains conditional support for quota, ACLs, realtime/zoned behavior, online scrub/repair, live hooks, memory buffers, in-memory btrees, and debug-only checks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/xfs/Makefile

## Purpose

Builds the XFS kernel module/object from libxfs code, high-level filesystem code, transaction/log code, optional feature code, and online scrub/repair components.

## Main Structure

- Adds include paths for trace events and `libxfs`.
- Builds `xfs.o` when `CONFIG_XFS_FS` is enabled.
- Compiles `xfs_trace.o` first because trace macros can expand heavily.
- Builds core `libxfs` objects first, including this group’s `xfs_ag.o`, `xfs_ag_resv.o`, `xfs_alloc.o`, and `xfs_alloc_btree.o`.
- Adds realtime libxfs objects when `CONFIG_XFS_RT` is enabled.
- Adds high-level XFS modules for file I/O, attrs, buffers, discard, health, ioctl, iomap, inode cache, mount, stats, sysfs, xattrs, and related runtime behavior.
- Adds transaction and log recovery modules.
- Adds optional modules for quota, realtime, ACLs, sysctl, compat ioctls, pNFS, DAX memory failure notification, drain hooks, live hooks, memory buffers, and in-memory btrees.
- Adds online scrub and repair object lists under `CONFIG_XFS_ONLINE_SCRUB` and `CONFIG_XFS_ONLINE_REPAIR`.

## Relationship to This Group

- Directly compiles:
  - `libxfs/xfs_ag.o`
  - `libxfs/xfs_ag_resv.o`
  - `libxfs/xfs_alloc.o`
  - `libxfs/xfs_alloc_btree.o`
- Pulls in high-level `xfs_xattr.o`, while generic VFS xattr handling lives outside XFS in `fs/xattr.c`.

## Research Notes

The Makefile is a dependency map for XFS. It shows the allocator and AG code live in `libxfs`, below high-level runtime code, and explains why allocator/AG structures have hooks for realtime, rmap/refcount, scrub, repair, debug, and quota-related builds.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.c

## Purpose

Manages XFS allocation group lifecycle, per-AG initialization, AG geometry, growfs/shrink operations, new AG header construction, and AG geometry reporting.

## Main Responsibilities

- Initializes per-AG runtime data and rebuilds in-core filesystem summary counters.
- Allocates and frees in-core `xfs_perag` objects.
- Computes AG block counts and valid per-AG inode ranges.
- Initializes new AG headers and root btree blocks for growfs.
- Extends or shrinks the final AG.
- Reports AG geometry and health.

## Key Functions

- `xfs_initialize_perag_data` reads each AGF and AGI to populate per-AG state and recompute free block, free inode, allocated inode, AGFL, and btree block counters. It rejects obviously corrupt aggregate counts.
- `xfs_initialize_perag` allocates new per-AG structures and updates inode allocation limits and preallocated AG metadata block count.
- `xfs_free_perag_range` frees per-AG group objects and cancels delayed blockgc work in kernel builds.
- `xfs_ag_block_count`, `xfs_agino_range`, and `xfs_update_last_ag_size` maintain geometry for normal AGs and shortened final AGs.
- `xfs_ag_init_headers` creates uncached buffers for new AG metadata and initializes SB, AGF, AGFL, AGI, BNOBT, CNTBT, INOBT, optional FINOBT, RMAPBT, and REFCBT roots.
- `xfs_ag_shrink_space` shrinks the final AG by allocating the tail extent exactly, updating AGI/AGF lengths, reinitializing reservations, and updating per-AG geometry.
- `xfs_growfs_compute_deltas` computes grow deltas and new AG counts while respecting minimum AG size and maximum AG number.
- `xfs_ag_extend_space` extends the final AG, updates AGI/AGF lengths, records rmap behavior with skip-update owner info, and frees the new space into allocation btrees.
- `xfs_ag_get_geometry` reads AGI/AGF, reports inode/free counters, subtracts needed per-AG reservations, and annotates health.

## Header Initialization Details

- Free-space btree roots start with records covering space after static AG metadata.
- If the internal log is inside the AG, free-space records are split/trimmed around it.
- RMAP root initialization records static metadata, free-space btree roots, inode btree roots, optional refcount root, rmap root, and internal log ownership.
- AGF initialization sets roots, levels, AGFL indexes/counts, free block counters, longest extent, optional rmap/refcount fields, and UUID.
- AGFL initialization sets v5 headers where applicable and fills entries with `NULLAGBLOCK`.
- AGI initialization sets inode btree roots, optional finobt roots, unlink buckets, inode counters, and UUID.

## Important Invariants and Edge Cases

- Grow and shrink operations apply to the last AG only.
- Shrink temporarily frees per-AG reservations so the exact tail allocation is not blocked by reservation accounting.
- Shrink preserves AGI/AGF lock ordering across transaction rolls.
- If reservation reinitialization fails after shrink changes, the code either rolls back/free-defers the tail space or forces shutdown for in-core corruption.
- Grow uses uncached buffers because new AG headers can be beyond the current filesystem address space.
- Valid inode ranges exclude static metadata and are aligned to inode cluster geometry.
- `xfs_initialize_perag_data` marks filesystem counters sick on corrupt summary data but marks them healthy on the normal exit path.

## Dependencies

Allocation/free-space btrees, inode allocation, rmap/refcount, per-AG reservations, transaction/defer handling, buffer operations, health reporting, mount geometry, and group infrastructure.

## Research Notes

This is the AG lifecycle and geometry authority for XFS. Resize code is the most sensitive part because it mixes AGF/AGI updates, exact allocation/freeing, per-AG reservation reinitialization, rmap behavior, transaction rolling, and in-core geometry updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.h

## Purpose

Defines in-core XFS per-allocation-group state, per-AG reservation structures, AG operational state helpers, per-AG reference helpers, geometry validation helpers, iteration macros, and grow/shrink/reporting declarations.

## Key Types

- `struct xfs_ag_resv`
  - `ar_orig_reserved`: number of blocks originally hidden/reserved.
  - `ar_reserved`: remaining reserved blocks.
  - `ar_asked`: requested reservation size.
- `struct xfs_perag`
  - Embeds `struct xfs_group`.
  - Caches AGF-derived free-space btree levels, AGFL count, free blocks, longest free extent, and btree block count.
  - Caches AGI-derived inode counts.
  - Stores inode allocation search hints.
  - Holds metadata and rmapbt reservation state.
  - Stores valid AG inode range bounds.
  - Kernel-only fields include inode cache locking/radix tree, filestream count, reclaim cursor, blockgc work, and online-repair alternate btree heights.

## Operational State

Defines atomic bit positions and generated inline helpers for:

- AGF initialized.
- AGI initialized.
- AG prefers metadata.
- AG allows inodes.
- AGFL needs reset.

## Reference Helpers

- Passive references: `xfs_perag_get`, `xfs_perag_hold`, `xfs_perag_put`.
- Active references: `xfs_perag_grab`, `xfs_perag_rele`.
- Iteration helpers: `xfs_perag_next_range`, `xfs_perag_next_from`, `xfs_perag_next`, `xfs_perag_next_wrap`.
- Iteration macros wrap AG scans from a starting AG through a wrap point and restart range.

## Geometry Helpers

- `xfs_ag_block_count` and `xfs_agino_range` expose AG sizing and inode bounds.
- `xfs_verify_agbno` and `xfs_verify_agbext` delegate to generic group block validation.
- `xfs_verify_agino` and `xfs_verify_agino_or_null` validate AG inode numbers against precomputed non-metadata bounds.
- `xfs_ag_contains_log` detects whether an internal log starts in a given AG.
- `xfs_agbno_to_fsb`, `xfs_agbno_to_daddr`, and `xfs_agino_to_ino` convert per-AG addresses to filesystem/global forms.

## Grow/Shrink Interfaces

Declares per-AG lifecycle and resize functions implemented in `xfs_ag.c`, plus `struct aghdr_init_data` used for initializing new AG headers during growfs.

## Important Invariants

- `pag_group(pag)` is the embedded group object backing group infrastructure.
- Per-AG active iteration releases the current active reference before moving to the next.
- AG inode validation uses precomputed `agino_min`/`agino_max`, not raw AG size.
- Wrap iteration must respect AG lock ordering and transaction constraints used by allocation code.

## Research Notes

This header is the structural contract for allocation and AG lifecycle code. The allocator depends on cached free-space fields, reservation fields, opstate bits, geometry validators, and wrap iteration macros defined here.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.c

## Purpose

Implements XFS per-allocation-group block reservations for metadata structures that must be able to grow even when an AG is nearly full.

## Main Responsibilities

- Determines whether a per-AG reservation is critically low.
- Computes blocks that must remain unavailable to ordinary allocation.
- Initializes metadata and rmapbt reservations.
- Frees reservation state at teardown or during resize handling.
- Accounts allocations from and frees back to per-AG reservations.

## Key Functions

- `xfs_ag_resv_critical` reports critical low-space state when available reserve is below 10 percent of requested space, below max btree height, or an error tag forces it.
- `xfs_ag_resv_needed` returns blocks reserved for other consumers that the current allocation type must not consume.
- `xfs_ag_resv_free` frees both rmapbt and metadata reservations.
- `__xfs_ag_resv_init` hides reservation space from fdblocks, updates `m_ag_max_usable` for AG 0, and records asked/original/reserved counts.
- `xfs_ag_resv_init` calculates metadata reserves from refcountbt and finobt needs, falls back to refcount-only if finobt reservation cannot be made, then calculates rmapbt reserves.
- `xfs_ag_resv_alloc_extent` consumes reserve blocks and updates transaction superblock counters based on reservation type.
- `xfs_ag_resv_free_extent` replenishes reserve blocks and credits fdblocks or reserved fdblocks as appropriate.

## Reservation Model

- Metadata reservations hide only the not-yet-used portion because metadata btree blocks already in use are accounted as used on disk.
- RMAPBT reservations hide the full ask because rmapbt blocks live in free space and are not subtracted from fdblocks otherwise.
- AG 0 adjusts `m_ag_max_usable`, assuming no other AG requires a larger per-AG reservation.
- `XFS_AG_RESV_AGFL` and `XFS_AG_RESV_METAFILE` do not consume these reservation counters in the alloc/free hooks.
- `XFS_AG_RESV_NONE` updates ordinary fdblocks or delayed-allocation reserved fdblocks directly.

## Important Invariants and Edge Cases

- If `used > ask`, initialization raises `ask` to `used`.
- Finobt reservation failure sets `m_finobt_nores` and retries with refcountbt reservation only.
- If active reservations exceed current `pagf_freeblks + pagf_flcount`, initialization can return `-ENOSPC` after ensuring AGF state is initialized.
- RMAPBT reserve freeing uses `ar_orig_reserved`, while metadata uses remaining `ar_reserved`.
- Error tags can force reservation failure or critical-low behavior for testing.

## Dependencies

Refcountbt, finobt, rmapbt reserve calculators, free-space counters, transaction superblock accounting, error tags, tracepoints, and per-AG structures from `xfs_ag.h`.

## Research Notes

This file is allocator accounting infrastructure. It creates virtual in-core allocations so that AG-local metadata growth can succeed without requiring crash-time cleanup. Correctness depends on fdblocks accounting matching the reservation type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.h

## Purpose

Declares the per-AG reservation API and maps reservation types to fields in `struct xfs_perag`.

## API

- `xfs_ag_resv_free`
- `xfs_ag_resv_init`
- `xfs_ag_resv_critical`
- `xfs_ag_resv_needed`
- `xfs_ag_resv_alloc_extent`
- `xfs_ag_resv_free_extent`
- `xfs_perag_resv`

## Reservation Mapping

`xfs_perag_resv` maps:

- `XFS_AG_RESV_METADATA` to `pag->pag_meta_resv`.
- `XFS_AG_RESV_RMAPBT` to `pag->pag_rmapbt_resv`.
- Other reservation types to `NULL`.

## Research Notes

This header is small but central to allocator accounting. Callers must pass only reservation types that are meaningful for the helper being used; the inline mapper deliberately returns `NULL` for non-perag reservation classes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ag_resv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.c

## Purpose

Implements XFS free-space allocation, free-space freeing, AGFL balancing, AGF/AGFL verification, free-space btree manipulation, deferred extent free scheduling, allocation query helpers, and allocation/free intent cache lifecycle.

## Main Responsibilities

- Computes AGFL size, static AG preallocation blocks, maximum usable AG space, and set-aside blocks.
- Maintains BNOBT and CNTBT free-space records in sync.
- Selects allocation candidates for exact, near, this-AG, start-AG, first-AG, and size-based allocation modes.
- Trims busy extents and flushes busy extents when necessary.
- Balances the AGFL before allocation or free operations.
- Updates AGF and per-AG cached counters.
- Verifies AGF and AGFL metadata.
- Frees extents by merging with neighboring free records.
- Integrates rmap updates and per-AG reservation accounting.
- Schedules deferred frees and automatic reap/cancel/commit behavior for unwritten allocations.
- Provides free-space query and AGFL walk helpers.

## Geometry and Reservation Sizing

- `xfs_agfl_size` accounts for v5 AGFL headers by reducing usable entry slots on CRC filesystems.
- `xfs_refc_block` and `xfs_prealloc_blocks` compute fixed metadata block layout based on reflink, rmapbt, and finobt features.
- `xfs_alloc_set_aside` reserves space per AG for AGFL refill and file bmap btree split needs.
- `xfs_alloc_ag_max_usable` subtracts static AG metadata, AGFL reserve, and optional btree root blocks from AG size.
- `xfs_alloc_longest_free_extent` subtracts needed AGFL refill blocks and other reservations from the longest free extent.
- `xfs_alloc_min_freelist` computes worst-case AGFL blocks needed for bno/cnt btree splits and optional rmapbt splits.

## Btree Record Operations

- `xfs_alloc_lookup_eq/ge/le` wrap btree lookups and maintain an active-cursor flag.
- `xfs_alloc_update` writes a free-space record.
- `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, and `xfs_alloc_get_rec` convert and validate records.
- `xfs_alloc_fixup_trees` removes an allocated subextent from a free record and updates both btrees, handling full consumption, left trim, right trim, and split cases.
- `xfs_free_ag_extent` merges a freed extent with left and/or right neighbors and inserts the resulting record into both btrees.

## Allocation Candidate Selection

- `xfs_alloc_compute_aligned` trims busy regions and applies min AG block and alignment constraints.
- `xfs_alloc_compute_diff` scores locality for near allocations.
- `xfs_alloc_fix_len` enforces product/modulus length constraints.
- `xfs_alloc_cur` tracks CNTBT and BNOBT cursors plus best candidate state.
- `xfs_alloc_ag_vextent_exact` allocates at an exact AG block if a free record contains the target and the non-busy part satisfies minimum length.
- `xfs_alloc_ag_vextent_near` combines CNTBT and BNOBT searches to balance locality and size.
- `xfs_alloc_ag_vextent_size` finds a best-fit extent anywhere in an AG.
- `xfs_alloc_ag_vextent_small` handles small remaining free spaces and can allocate a single block from the AGFL when allowed.
- Public entry points adapt these modes:
  - `xfs_alloc_vextent_this_ag`
  - `xfs_alloc_vextent_start_ag`
  - `xfs_alloc_vextent_first_ag`
  - `xfs_alloc_vextent_exact_bno`
  - `xfs_alloc_vextent_near_bno`

## AGFL Management

- `xfs_alloc_fix_freelist` ensures an AG is usable for the requested operation, checks metadata-preferred AG behavior, validates free space against reservations, resets corrupted AGFL state when needed, shrinks overfull AGFLs by deferring one-block frees, and refills underfull AGFLs from free space.
- `xfs_alloc_get_freelist` removes a block from the AGFL, validates it, updates AGF/per-AG counters, and optionally marks it as a btree block.
- `xfs_alloc_put_freelist` adds a block to the AGFL and updates AGF/per-AG counters.
- `xfs_agfl_needs_reset` detects inconsistent AGFL index/count state.
- `xfs_agfl_reset` resets corrupted AGFL metadata, leaks untrusted entries deliberately, and warns that repair is required.

## AGF and AGFL Verification

- `xfs_agfl_verify`, read verifier, and write verifier validate CRC AGFL magic, UUID, sequence number, entries, LSN, and checksum.
- `xfs_validate_ag_length` ensures AGF/AGI sequence and length are consistent with filesystem geometry, allowing only the last AG to be shorter.
- `xfs_agf_verify` validates AGF magic, version, UUID, LSN, AGFL indexes, free counters, btree levels, btree block counts, and optional rmap/refcount fields.
- `xfs_alloc_read_agf` initializes per-AG cached AGF fields, detects AGFL reset need, updates `m_allocbt_blks`, and in debug builds checks cached AGF state against reread disk state.

## Allocation and Free Finish Paths

- `xfs_alloc_vextent_check_args` normalizes alignment/maxlen, initializes minimum AG constraints from `t_highest_agno`, and rejects invalid targets or arguments.
- `xfs_alloc_vextent_prepare_ag` obtains a perag if needed and runs `xfs_alloc_fix_freelist`.
- `xfs_alloc_vextent_finish` updates `t_highest_agno` to avoid AGF lock-order deadlocks, converts AG block to fsblock, records rmap allocation, updates counters, consumes reservations, updates stats, and drops active perag references if requested.
- `__xfs_free_extent` fixes the freelist, validates the extent against the locked AGF, frees into btrees, and inserts a busy extent for discard/reuse tracking.

## Deferred Free and Autoreap

- `xfs_defer_extent_free` creates `xfs_extent_free_item` work items, validates data or realtime extents, copies owner flags, and queues deferred work.
- `xfs_free_extent_later` is the public deferred-free wrapper.
- `xfs_alloc_schedule_autoreap` attaches a paused EFI to a transaction so crash recovery will free uncommitted allocated space.
- `xfs_alloc_cancel_autoreap` marks paused EFI items cancelled and unpauses them so an EFD is logged without freeing the space.
- `xfs_alloc_commit_autoreap` unpauses the deferred item to commit to freeing the space.

## Query Helpers

- `xfs_alloc_query_range` and `xfs_alloc_query_all` query BNOBT free-space records after record validation.
- `xfs_alloc_has_records` reports record packing over a block range.
- `xfs_agfl_walk` iterates active AGFL entries from first to last with wraparound.
- `xfs_extfree_intent_init_cache` and `xfs_extfree_intent_destroy_cache` manage the slab cache for deferred extent free items.

## Important Invariants and Edge Cases

- BNOBT and CNTBT must always represent the same free-space state with different sort orders.
- `agf_longest` must be repaired when operations touch the rightmost CNTBT record block.
- Busy extents are trimmed before allocation; if all valid space is busy, allocation can flush and retry, with special handling to avoid deadlock.
- AGFL blocks are considered free in on-disk accounting but are constrained by in-core availability checks.
- RMAP updates are skipped only when owner info explicitly requests skip-update behavior.
- AGFL reset keeps the filesystem online at the cost of leaked blocks that require repair.
- `t_highest_agno` prevents later allocations in the same transaction from locking lower-number AGFs out of order.
- Public allocation functions often return success with `NULLFSBLOCK` to signal ENOSPC-style no-allocation results.
- Freeing an already-free or overlapping extent is treated as corruption.
- Realtime deferred frees are validated separately and must not use per-AG reservations.

## Dependencies

BNOBT/CNTBT operations, AGF/AGFL buffers, per-AG state, reservations, rmap, extent busy tracking, transactions/defer items, buffer logging, health marking, error tags, tracepoints, statistics, and slab cache infrastructure.

## Research Notes

This is the core XFS data-device free-space allocator. The highest-risk areas are dual btree synchronization, AGFL refill/shrink accounting, reservation-aware availability checks, busy extent retry behavior, rmap integration, transaction lock-order constraints, and corruption handling around AGF/AGFL state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.h

## Purpose

Declares the XFS allocation/free-space API, allocation argument structure, free-space flags, deferred free item structure, autoreap API, and AGF/AGFL helper interfaces.

## Key Types

- `struct xfs_alloc_arg`
  - Carries transaction, mount, AGF buffer, perag, target/result block numbers, length constraints, alignment/modulus constraints, minleft/total requirements, locality range, datatype flags, reservation type, and owner information.
- `xfs_alloc_query_range_fn`
  - Callback for free-space btree query helpers.
- `xfs_agfl_walk_fn`
  - Callback for AGFL iteration.
- `struct xfs_extent_free_item`
  - Deferred free work item containing owner, start block, length, group, flags, and reservation type.
- `struct xfs_alloc_autoreap`
  - Stores a paused deferred-free item used for crash-safe automatic rollback of unused allocations.

## Flags

- `XFS_ALLOC_FLAG_TRYLOCK`: use trylock for buffer locking.
- `XFS_ALLOC_FLAG_FREEING`: caller is freeing extents.
- `XFS_ALLOC_FLAG_NORMAP`: do not modify rmapbt.
- `XFS_ALLOC_FLAG_NOSHRINK`: do not shrink the AGFL.
- `XFS_ALLOC_FLAG_CHECK`: test only, do not mutate allocation args.
- `XFS_ALLOC_FLAG_TRYFLUSH`: avoid waiting in busy-extent flush.
- Datatype flags:
  - `XFS_ALLOC_USERDATA`
  - `XFS_ALLOC_INITIAL_USER_DATA`
  - `XFS_ALLOC_NOBUSY`
- Free flags:
  - `XFS_FREE_EXTENT_SKIP_DISCARD`
  - `XFS_FREE_EXTENT_REALTIME`
- EFI flags:
  - `XFS_EFI_SKIP_DISCARD`
  - `XFS_EFI_ATTR_FORK`
  - `XFS_EFI_BMBT_BLOCK`
  - `XFS_EFI_CANCELLED`
  - `XFS_EFI_REALTIME`

## Declared API Areas

- AGFL sizing and access:
  - `xfs_agfl_size`
  - `xfs_alloc_get_freelist`
  - `xfs_alloc_put_freelist`
  - `xfs_alloc_read_agfl`
  - `xfs_buf_to_agfl_bno`
  - `xfs_agfl_walk`
- Free-space limits and counters:
  - `xfs_alloc_set_aside`
  - `xfs_alloc_ag_max_usable`
  - `xfs_alloc_longest_free_extent`
  - `xfs_alloc_min_freelist`
  - `xfs_prealloc_blocks`
- Allocation:
  - `xfs_alloc_vextent_this_ag`
  - `xfs_alloc_vextent_near_bno`
  - `xfs_alloc_vextent_exact_bno`
  - `xfs_alloc_vextent_start_ag`
  - `xfs_alloc_vextent_first_ag`
- Freeing:
  - `__xfs_free_extent`
  - `xfs_free_extent`
  - `xfs_free_extent_later`
  - `xfs_free_ag_extent`
  - `xfs_free_extent_fix_freelist`
- Btree lookup/query:
  - `xfs_alloc_lookup_le`
  - `xfs_alloc_lookup_ge`
  - `xfs_alloc_get_rec`
  - `xfs_alloc_btrec_to_irec`
  - `xfs_alloc_check_irec`
  - `xfs_alloc_query_range`
  - `xfs_alloc_query_all`
  - `xfs_alloc_has_records`
- AGF handling:
  - `xfs_read_agf`
  - `xfs_alloc_read_agf`
  - `xfs_alloc_log_agf`
  - `xfs_validate_ag_length`
- Autoreap and cache lifecycle:
  - `xfs_alloc_schedule_autoreap`
  - `xfs_alloc_cancel_autoreap`
  - `xfs_alloc_commit_autoreap`
  - `xfs_extfree_intent_init_cache`
  - `xfs_extfree_intent_destroy_cache`

## Important Invariants

- `xfs_alloc_arg` centralizes allocation state to avoid long argument lists and must be initialized carefully by callers or normalized by allocation helpers.
- `XFS_AG_RESV_AGFL` is not a valid reservation for normal allocation argument validation.
- `xfs_free_extent` is a non-discard-skipping wrapper over `__xfs_free_extent`.
- `xfs_buf_to_agfl_bno` accounts for CRC AGFL headers by skipping the header.
- Realtime deferred frees are identified with `XFS_EFI_REALTIME`.

## Research Notes

This header is the public contract for XFS data-device allocation. It exposes both low-level btree/AGFL primitives and higher-level allocation modes, so misuse of fields such as `resv`, `oinfo`, `datatype`, or length/alignment constraints can break allocator accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.c

## Purpose

Implements the XFS free-space btree operation tables, cursor allocation, verification, root updates, btree block allocation/free, staged btree commit, record capacity calculations, max-level computation, and cursor cache lifecycle for BNOBT and CNTBT.

## Main Responsibilities

- Defines BNOBT and CNTBT `xfs_btree_ops`.
- Creates and duplicates free-space btree cursors.
- Updates AGF root and level fields when btree roots change.
- Allocates btree blocks from the AGFL and frees btree blocks back to the AGFL.
- Verifies free-space btree blocks on read/write.
- Defines key/record ordering rules for BNOBT and CNTBT.
- Installs staged btree roots for online repair.
- Calculates max records, max levels, and btree size.
- Manages the allocation btree cursor slab cache.

## BNOBT Versus CNTBT Semantics

- BNOBT is ordered by start block.
  - Key comparison uses `ar_startblock`.
  - High key is end block (`startblock + blockcount - 1`).
  - Records are in order if the first record ends before or at the next start.
  - Supports key-contiguity checks.
- CNTBT is ordered by block count, then start block.
  - Key comparison uses `ar_blockcount`, then `ar_startblock`.
  - High key carries block count only.
  - Records are in order by size, then start block.
  - Does not need key-contiguity checks.

## Key Functions

- `xfs_bnobt_dup_cursor` and `xfs_cntbt_dup_cursor` duplicate cursors.
- `xfs_allocbt_set_root` updates AGF bno/cnt root and level fields and mirrored perag levels.
- `xfs_allocbt_alloc_block` obtains a new btree block from the AGFL, increments `m_allocbt_blks`, and marks busy extent reuse.
- `xfs_allocbt_free_block` returns a btree block to the AGFL, decrements `m_allocbt_blks`, and inserts a busy extent with discard skipped.
- `xfs_allocbt_verify` checks magic, v5 header, level bounds, repair-height allowance, and generic AG btree block structure.
- `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` allocate cursors and initialize levels from AGF when an AGF buffer is available.
- `xfs_allocbt_commit_staged_btree` installs a staged root into AGF and commits fake-root state.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_maxlevels_ondisk`, and `xfs_allocbt_calc_size` compute format geometry.
- `xfs_allocbt_init_cur_cache` and `xfs_allocbt_destroy_cur_cache` manage the cursor cache.

## Important Invariants and Edge Cases

- Free-space btree blocks are allocated from and returned to the AGFL, not directly from ordinary free-space records.
- Root updates must keep AGF fields and perag cached levels synchronized.
- Verifier level checks use perag tree levels when AGF state is initialized, but fall back to mount-wide maximum levels during grow or recovery.
- Online repair can temporarily validate against alternate repair btree heights.
- BNOBT records must not overlap; CNTBT records must be sorted by length and start.
- Cursor initialization supports staging cursors with `tp` and `agbp` set to `NULL`.

## Dependencies

Generic XFS btree framework, btree staging support, AGF/AGFL allocation helpers, extent busy tracking, perag state, health masks, tracepoints, and allocation geometry from the mount.

## Research Notes

This file supplies the generic btree framework callbacks that make the allocator’s dual-tree model work. The critical coupling is with AGFL management and AGF root/level fields; block allocation/free callbacks affect global allocbt block accounting and busy extent tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.h

## Purpose

Declares free-space btree layout macros and the public alloc-btree helper API for XFS BNOBT and CNTBT.

## Layout Macros

- `XFS_ALLOC_BLOCK_LEN(mp)` returns the btree block header length, selecting CRC or non-CRC short-format headers.
- `XFS_ALLOC_REC_ADDR(mp, block, index)` computes the address of a record in a btree block.
- `XFS_ALLOC_KEY_ADDR(mp, block, index)` computes the address of a key in an internal btree block.
- `XFS_ALLOC_PTR_ADDR(mp, block, index, maxrecs)` computes the address of a pointer after the key array.

## Declared API

- `xfs_bnobt_init_cursor`
- `xfs_cntbt_init_cursor`
- `xfs_allocbt_maxrecs`
- `xfs_allocbt_calc_size`
- `xfs_allocbt_commit_staged_btree`
- `xfs_allocbt_maxlevels_ondisk`
- `xfs_allocbt_init_cur_cache`
- `xfs_allocbt_destroy_cur_cache`

## Important Invariants

- Record, key, and pointer address macros use one-based indexes, matching XFS btree conventions.
- Header size depends on whether the filesystem uses CRC-enabled metadata.
- Some layout macros are retained for userspace use even if not all appear used by kernel code.
- Staged btree commit is part of online repair/rebuild workflows.

## Research Notes

This header is the low-level layout contract for XFS free-space btrees. Incorrect header-size or index calculations would corrupt btree block interpretation across both kernel and userspace tooling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_alloc_btree.h -->