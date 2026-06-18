# Group Research: group_859_linux_sources_os_linux_linux_fs_xfs_libxfs_xfs_format_h_sources_os_l_b6d377cf61f5

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_format.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_format.h

## Purpose

`xfs_format.h` is the central XFS on-disk format contract. It defines the packed/be-endian structures, magic numbers, feature bits, size limits, conversion helpers, and btree record layouts that all XFS kernel and userspace libxfs code must interpret consistently.

## Main Content

- Defines superblock formats:
  - In-core `struct xfs_sb`.
  - On-disk `struct xfs_dsb`.
  - V1-V5 version fields and older `sb_versionnum` feature bits.
  - V5 feature masks for compat, read-only compat, incompat, and log-incompat features.
  - Recent incompat features include parent pointers, metadata directory tree, zoned realtime allocator, and realtime group LBA gaps.
- Defines geometry and address conversion macros:
  - FSB/basic-block/byte conversions.
  - AG block/address conversions.
  - Inode number decomposition and composition macros.
- Defines allocation group headers:
  - `struct xfs_agf` for free-space metadata.
  - `struct xfs_agi` for inode allocation metadata.
  - `struct xfs_agfl` for AG freelist blocks.
  - Logging bitmasks for AGF and AGI fields.
- Defines realtime metadata:
  - Realtime bitmap/summary word unions.
  - Realtime group limits and `struct xfs_rtsb`.
  - Realtime btree root formats for rmap and refcount metadata.
- Defines timestamp encoding:
  - Legacy signed 32-bit seconds + nanoseconds.
  - Bigtime unsigned 64-bit nanosecond encoding with epoch conversion helpers.
  - Quota bigtime conversion and bounds.
- Defines on-disk inode core:
  - `struct xfs_dinode`, inode fork pointer/size helpers, device encoding helpers.
  - Inode format enum values.
  - Legacy and V3 inode fields, CRC, creation time, UUID, large extent counts, metadata inode type.
  - `di_flags` and `di_flags2`, including realtime, reflink, DAX, bigtime, nrext64, and metadata inode bits.
- Defines btree record formats:
  - Free-space btrees: allocation by block and by count.
  - Inode allocation btrees: inobt and finobt records, sparse inode holemasks, free masks.
  - Reverse mapping btree records and owner constants.
  - Refcount btree records and CoW staging flag.
  - Bmap btree records and delayed allocation startblock helpers.
  - Generic btree block short/long headers and CRC offsets.
- Defines quota, remote symlink, ACL, and xattr constants.

## Key Interfaces and Invariants

- V5 filesystems use expanded feature fields and CRC-protected metadata. Many helpers test feature bits by reading `struct xfs_sb`.
- AGI fields are split into logging regions because the unlinked inode hash table sits in the middle of the structure.
- Inode allocation records represent 64 inodes per chunk. Sparse inode chunks use a 16-bit holemask, with each bit covering multiple inodes.
- The format intentionally preserves old layout quirks such as `sb_bad_features2`.
- Structures are endian-annotated and generally must remain padded/aligned as on disk.
- `xfs_ialloc.c` and `xfs_ialloc_btree.c` depend directly on the inobt/finobt constants, AGI layout, and logging bit definitions from this file.

## Dependencies

This header assumes fundamental XFS scalar types and feature predicates are available from surrounding libxfs/kernel headers. It is included by most libxfs implementation files and is foundational for both kernel and xfsprogs-compatible code.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_fs.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_fs.h

## Purpose

`xfs_fs.h` defines the XFS userspace ABI: ioctl numbers, ioctl argument structures, geometry reports, bulk inode/stat interfaces, scrub/repair interfaces, parent pointer iteration, file range exchange operations, health monitoring, and media verification. It is LGPL-licensed and explicitly intended to compile under C++.

## Main Content

- Defines direct I/O and file extent mapping structures:
  - `struct dioattr`.
  - `struct getbmap`.
  - `struct getbmapx`.
  - BMAP input and output flags for attr fork, CoW fork, prealloc, delalloc, holes, shared extents.
- Defines fsmap owner constants for XFS metadata owners.
- Defines filesystem geometry structures:
  - Legacy V1 and V4 geometry.
  - Current `struct xfs_fsop_geom`, including health fields, realtime group fields, internal realtime start, and reserved blocks.
  - Geometry feature flags mirroring superblock feature state.
- Defines AG and realtime group geometry reporting:
  - `struct xfs_ag_geometry`.
  - `struct xfs_rtgroup_geometry`.
  - Sick/checked bit definitions for metadata health reporting.
- Defines bulk inode/stat and inode-number reporting:
  - Legacy `struct xfs_bstat`, `struct xfs_inogrp`, and `struct xfs_fsop_bulkreq`.
  - Current `struct xfs_bulkstat`, `struct xfs_inumbers`, request headers, and version constants.
  - Flags for AG-limited scans, special inode queries, 64-bit extent counts, and metadata directory visibility.
- Defines handle-based operations:
  - File handles, fsids, fids.
  - Path/fd/handle conversion request structures.
  - Attribute list/multiop by handle structures.
- Defines scrub and repair ABI:
  - `struct xfs_scrub_metadata`.
  - Scrub type IDs covering AG metadata, inode forks, directory/xattr/symlink, quotas, counters, parent pointers, metapaths, realtime group metadata.
  - Input/output scrub flags and vectored scrub structures.
- Defines atomic file data exchange ABI:
  - `struct xfs_exchange_range`.
  - `struct xfs_commit_range`.
  - Flags for to-EOF, dsync, dry-run, and file1-written-only exchange.
- Defines parent pointer iteration:
  - `struct xfs_getparents`.
  - `struct xfs_getparents_by_handle`.
  - Record iteration helpers over userspace buffers.
- Defines health monitor ABI:
  - Event domains for mount, fs, AG, inode, realtime group, devices, and file ranges.
  - Event types for monitor state, unmount, sick/corrupt/healthy, shutdown, media errors, buffered/direct I/O errors, and data loss.
  - Event payload structures and monitor configuration.
- Defines media verification ABI:
  - `struct xfs_verify_media`.
  - Device IDs for data/log/realtime devices.
- Defines XFS ioctl command numbers.

## Key Interfaces and Invariants

- This file is ABI-stable; structure padding, reserved fields, and explicit fixed-width types are part of compatibility.
- Many newer interfaces provide version fields and reserved space to allow extension without breaking userspace.
- Health fields in geometry and bulkstat mirror in-core sickness masks defined elsewhere, including `xfs_health.h`.
- Scrub type numbers and ioctl numbers are externally visible and must not be renumbered.
- Some legacy ioctls are preserved or aliased even when deprecated.

## Dependencies

This header references Linux UAPI concepts such as `FS_IOC_*`, `FMR_OWNER`, `__user`, fixed-width kernel integer types, and xattr list limits. It bridges XFS internal health/scrub concepts to userspace tools such as xfs_io, xfs_scrub, and administrative monitors.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.c

## Purpose

`xfs_group.c` implements generic XFS group lifetime and lookup support. A group is an abstraction for allocation groups and realtime groups, stored in mount-level xarrays and protected by passive and active reference counts.

## Main Content

- Implements passive reference helpers:
  - `xfs_group_get` looks up a group by index/type under RCU and increments `xg_ref`.
  - `xfs_group_hold` increments a passive ref on an existing group.
  - `xfs_group_put` decrements a passive ref.
- Implements active reference helpers:
  - `xfs_group_grab` looks up a group and increments `xg_active_ref` only if nonzero.
  - `xfs_group_rele` decrements the active ref.
  - Active refs are intended for short-lived operational access and fail if a group is being removed/offlined.
- Implements iteration:
  - `xfs_group_next_range` walks sequential group indices in a bounded range.
  - `xfs_group_grab_next_mark` finds the next group marked in the xarray.
- Implements insertion and removal:
  - `xfs_group_insert` initializes group identity, optional extent-busy tracking, kernel-only state locks/hooks, defer drains, and the mount-owned active reference before inserting into the mount xarray.
  - `xfs_group_free` erases the group from the xarray, validates passive refs are gone, drains deferred intents, releases kernel-only resources, calls optional uninit, drops the mount active ref, validates active refs, and frees via RCU.
- Provides `xfs_group_get_by_fsb`, mapping a filesystem block to group number before lookup.

## Key Interfaces and Invariants

- Passive refs protect long-lived objects that can be cleaned up during group teardown.
- Active refs represent online/access-safe group use. A zero active count means new active users cannot enter.
- The mount holds one active reference to indicate that the group is online.
- `xfs_group_free` expects no passive references and no active references after dropping the mount ref.
- The xarray under `mp->m_groups[type].xa` is the authoritative group index.

## Dependencies

Includes core XFS mount, error, trace, extent busy, and defer-drain infrastructure. Kernel-only portions allocate extent busy trees, initialize spinlocks/hooks, and free kernel resources.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.h

## Purpose

`xfs_group.h` declares the generic XFS group object and helper APIs used for allocation groups and realtime groups. It also provides group-local geometry conversion and extent validation helpers.

## Main Content

- Defines `struct xfs_group`:
  - Mount pointer, group number, group type.
  - Passive and active reference counts.
  - Precomputed usable block bounds: `xg_block_count` and `xg_min_gbno`.
  - Kernel-only busy extent or zoned reset list state.
  - Kernel-only health state, state lock, defer-intent drain, and rmap update hooks.
- Declares group reference and lifecycle functions implemented in `xfs_group.c`.
- Defines xarray mark helpers:
  - `xfs_group_set_mark`.
  - `xfs_group_clear_mark`.
  - `xfs_group_marked`.
- Defines geometry helpers:
  - `xfs_group_max_blocks`.
  - `xfs_groups_to_rfsbs`.
  - `xfs_group_start_fsb`.
  - `xfs_gbno_to_fsb`.
  - `xfs_gbno_to_daddr`.
  - `xfs_fsb_to_gno`.
  - `xfs_fsb_to_gbno`.
- Defines group block validation:
  - `xfs_verify_gbno`.
  - `xfs_verify_gbext`.

## Key Interfaces and Invariants

- `xfs_gbno_to_daddr` handles both dense group address spaces and groups with disk-address gaps.
- `xfs_verify_gbno` enforces both upper bound and minimum usable block bound.
- `xfs_verify_gbext` rejects zero-length extents and catches arithmetic overflow before validating the end block.
- Kernel-only health fields (`xg_checked`, `xg_sick`) are shared with the health tracking API in `xfs_health.h`.

## Dependencies

Requires XFS mount group geometry (`mp->m_groups[type]`), xarray marks, atomic counters, and kernel-only XFS infrastructure when compiled in kernel mode.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_health.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_health.h

## Purpose

`xfs_health.h` defines the in-core metadata health model for XFS. It declares sickness bitmasks, checked/sick semantics, health mutation/query APIs, and helpers for mapping internal health to geometry, bulkstat, and health monitor reports.

## Main Content

- Documents the health model:
  - `checked && sick`: metadata was checked and needs repair.
  - `checked && !sick`: metadata was checked and is healthy.
  - `!checked && sick`: runtime evidence of trouble without a full check.
  - `!checked && !sick`: not examined since mount.
- Defines filesystem-wide sickness bits:
  - Counters, quotas, quota counts, nlinks, metadata directory tree, metadata paths.
- Defines realtime group sickness bits:
  - Superblock, bitmap, summary, rmapbt, refcountbt.
- Defines allocation group sickness bits:
  - SB, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcountbt, bad inodes.
- Defines inode sickness bits:
  - Core, data/attr/CoW bmap forks, directory, xattrs, symlink, parent pointers, directory tree.
  - Zapped fork/directory/symlink bits.
  - `XFS_SICK_INO_FORGET` to avoid propagating some inactivation state.
- Groups sickness bits into primary, secondary, indirect, and all masks.
- Declares mutation and query APIs:
  - Mark sick/corrupt/healthy for fs, group, AG, realtime group, and inode scopes.
  - Measure sickness for fs, group, and inode.
  - Helpers to mark bmap, btree, dirattr, and da-args sickness.
- Provides health query helpers:
  - `xfs_fs_has_sickness`, `xfs_group_has_sickness`, `xfs_inode_has_sickness`.
  - Healthy checks for fs, AG, rtgroup, and inode.
- Declares export helpers:
  - `xfs_fsop_geom_health`.
  - `xfs_ag_geom_health`.
  - `xfs_rtgroup_geom_health`.
  - `xfs_bulkstat_health`.
- Defines `xfs_metadata_is_sick(error)` for corruption/CRC error classification.
- Declares health monitor mask conversion helpers.

## Key Interfaces and Invariants

- Runtime corruption detection calls `mark_sick`, which does not imply a complete scan.
- Scrub/repair tooling calls `mark_corrupt` or `mark_healthy` to update both sick and checked state.
- AG and realtime group health are stored in `struct xfs_group`.
- User-visible geometry and bulkstat health fields are derived from these internal masks.

## Dependencies

Forward declares core XFS structures and is consumed by scrub, repair, btree, inode, AG, realtime group, ioctl, and monitor code.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_health.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.c

## Purpose

`xfs_ialloc.c` implements XFS inode allocation, freeing, inode mapping, AGI verification/logging, inode record validation, sparse inode record handling, and inode allocation geometry setup.

## Main Content

- Inobt record operations:
  - `xfs_inobt_lookup` positions an inode btree cursor.
  - `xfs_inobt_update` writes an incore inode record to the current btree record.
  - `xfs_inobt_btrec_to_irec` converts on-disk btree records to incore records.
  - `xfs_inobt_rec_freecount` computes real free inode count, accounting for sparse holes.
  - `xfs_inobt_check_irec` validates alignment, count, freecount, and free mask consistency.
  - `xfs_inobt_get_rec` retrieves and validates the current record.
  - `xfs_inobt_insert_rec` inserts one record from cursor state.
- New inode initialization:
  - `xfs_ialloc_inode_init` stamps newly allocated inode buffers.
  - V3 inodes get inode numbers, metadata UUIDs, CRCs, and logical icreate logging.
  - Older inodes log inode cores physically.
- Sparse inode support:
  - `xfs_align_sparse_ino` aligns sparse chunk records to full chunk boundaries.
  - Merge helpers detect and combine compatible sparse records.
  - `xfs_inobt_insert_sprec` inserts or merges sparse records into the inobt.
  - `xfs_finobt_insert_sprec` inserts or replaces sparse records in the finobt.
- AG inode chunk allocation:
  - `xfs_ialloc_ag_alloc` allocates a new inode chunk in an AG.
  - Tries contiguous allocation after `agi_newino`, near btree roots, stripe/cluster alignment, then sparse allocation if supported.
  - Initializes new inode buffers, inserts inobt/finobt records, updates AGI and superblock inode counters.
- Inode allocation from existing free records:
  - `xfs_dialloc_ag_inobt` implements the inobt-only allocator.
  - `xfs_dialloc_ag_finobt_near` and `xfs_dialloc_ag_finobt_newino` implement finobt search policies.
  - `xfs_dialloc_ag_update_inobt` mirrors finobt allocation into the inobt.
  - `xfs_dialloc_ag` chooses finobt or inobt path.
- AG selection and top-level allocation:
  - `xfs_dialloc_pick_ag` picks a starting AG based on metadata directory placement, directory rotor, or parent AG.
  - `xfs_dialloc_good_ag` checks AG eligibility, free inode availability, and whether enough free space exists to allocate a new inode chunk.
  - `xfs_dialloc_try_ag` reads AGI, allocates chunks if needed, rolls transactions, and allocates one inode.
  - `xfs_dialloc` scans AGs with a trylock pass and fallback pass, handles low-space behavior, enforces max inode count, and rejects obviously corrupt allocations.
- Inode freeing:
  - `xfs_difree_inode_chunk` frees full or sparse inode chunk backing extents.
  - `xfs_difree_inobt` marks an inode free, deletes a fully free chunk when eligible, updates AGI/superblock counters, and returns cluster deletion info.
  - `xfs_difree_finobt` updates, inserts, or removes the finobt record to stay consistent with the inobt.
  - `xfs_difree` validates inode-to-AG mapping, reads AGI, updates inobt, then finobt if enabled.
- Inode mapping:
  - `xfs_imap_lookup` performs btree lookup for untrusted or unaligned inode mapping.
  - `xfs_imap` maps an inode number to disk address, buffer length, and byte offset, with fast arithmetic paths for simple geometry.
- AGI logging and verification:
  - `xfs_ialloc_log_agi` logs selected AGI fields in two regions to avoid logging the whole unlinked hash table unnecessarily.
  - `xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate AGI magic, version, UUID/LSN, AG length, btree levels, and unlinked inode buckets.
  - `xfs_read_agi` reads AGI buffers and marks AGI sick on metadata corruption.
  - `xfs_ialloc_read_agi` initializes per-AG inode counters from AGI.
- Inode accounting and extent occupancy:
  - `xfs_ialloc_has_inodes_at_extent` reports whether an extent is empty, full, or sparse with respect to inode records.
  - `xfs_ialloc_count_inodes` counts total and free inodes under an inobt.
- Geometry:
  - `xfs_ialloc_setup_geometry` derives inode btree sizes, max levels, max inode count, inode cluster size, sparse allocation minimums, alignment, and folio order.
  - `xfs_ialloc_calc_rootino` computes the mkfs-laid-out root inode location.
  - `xfs_ialloc_check_shrink` prevents shrink from cutting through sparse inode records.

## Key Interfaces and Invariants

- Inobt and finobt records must describe equivalent chunk contents, but finobt only contains chunks with at least one free inode.
- AGI free counts, per-AG cached counts, and superblock counters are updated together under transaction control.
- Fully free inode chunks can be removed only when the filesystem block geometry does not contain multiple inode chunks per block.
- Sparse inode records must be aligned to full inode chunk boundaries and must not overlap allocated ranges.
- Allocation protects against reusing the parent inode and invalid directory inode numbers before returning success.
- AGI verifiers mark metadata sick for corruption/CRC failures, integrating allocator validation with the health model.

## Dependencies

Depends heavily on:
- `xfs_format.h` for AGI layout, inode record layout, masks, and address conversions.
- `xfs_ialloc_btree.h` for cursor creation and record address geometry.
- Allocation, transaction, btree, icreate logging, buffer, rmap, per-AG, and health subsystems.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.h

## Purpose

`xfs_ialloc.h` is the public libxfs header for inode allocation. It declares allocator/freeing/mapping entry points, AGI helpers, inobt helpers, inode chunk initialization, geometry setup, and shrink checks.

## Main Content

- Defines `XFS_INODE_BIG_CLUSTER_SIZE` as the large inode cluster target size.
- Defines `struct xfs_icluster`:
  - Indicates whether a chunk was deleted.
  - Carries first inode number.
  - Carries physical allocation bitmap for sparse chunks.
- Defines `xfs_make_iptr`, converting a buffer and inode offset into an on-disk dinode pointer.
- Declares top-level inode allocation/freeing:
  - `xfs_dialloc`.
  - `xfs_difree`.
- Declares inode mapping:
  - `xfs_imap`.
- Declares AGI logging and reading:
  - `xfs_ialloc_log_agi`.
  - `xfs_read_agi`.
  - `xfs_ialloc_read_agi`.
  - `XFS_IALLOC_FLAG_TRYLOCK`.
- Declares inobt operations:
  - `xfs_inobt_lookup`.
  - `xfs_inobt_get_rec`.
  - `xfs_inobt_rec_freecount`.
  - `xfs_inobt_btrec_to_irec`.
  - `xfs_inobt_check_irec`.
  - `xfs_inobt_insert_rec`.
- Declares inode chunk initialization:
  - `xfs_ialloc_inode_init`.
- Declares analysis/counting helpers:
  - `xfs_ialloc_has_inodes_at_extent`.
  - `xfs_ialloc_count_inodes`.
- Declares geometry and mkfs-layout helpers:
  - `xfs_ialloc_cluster_alignment`.
  - `xfs_ialloc_setup_geometry`.
  - `xfs_ialloc_calc_rootino`.
  - `xfs_ialloc_check_shrink`.

## Key Interfaces and Invariants

- `xfs_dialloc` returns an on-disk inode number and can roll the transaction pointer.
- `xfs_difree` takes a per-AG object matching the inode’s AG and reports whether an inode cluster was deleted.
- `xfs_imap` supports trusted fast paths and untrusted btree-backed validation.
- Inode records are always exposed through `xfs_inobt_rec_incore_t`, hiding sparse/non-sparse on-disk format differences.

## Dependencies

Forward declares core XFS allocation, transaction, mount, inode buffer, btree, and per-AG structures. Implemented primarily by `xfs_ialloc.c`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.c -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.c

## Purpose

`xfs_ialloc_btree.c` implements btree operations for the inode allocation btree (`inobt`) and free inode btree (`finobt`). It supplies cursor constructors, btree operation tables, block allocation/freeing, verifiers, record/key helpers, staged root commit, capacity calculations, reserve accounting, and cursor cache lifecycle.

## Main Content

- Cursor/cache state:
  - Static `xfs_inobt_cur_cache`.
  - `xfs_inobt_init_cur_cache` and `xfs_inobt_destroy_cur_cache`.
- Btree min/max record helpers:
  - `xfs_inobt_get_minrecs`.
  - `xfs_inobt_get_maxrecs`.
  - `xfs_inobt_maxrecs`.
- Cursor duplication:
  - `xfs_inobt_dup_cursor`.
  - `xfs_finobt_dup_cursor`.
- Root updates:
  - `xfs_inobt_set_root` updates `agi_root` and `agi_level`.
  - `xfs_finobt_set_root` updates `agi_free_root` and `agi_free_level`.
- Btree block count tracking:
  - `xfs_inobt_mod_blockcount` updates `agi_iblocks` or `agi_fblocks` when the inobtcount feature is enabled.
- Block allocation/freeing:
  - `__xfs_inobt_alloc_block` allocates one AG block near the requested start with inode-btree rmap ownership.
  - `xfs_inobt_alloc_block` uses no AG reservation.
  - `xfs_finobt_alloc_block` uses metadata reservation unless disabled.
  - Matching free helpers queue blocks for deferred freeing and adjust block counts.
- Record/key/pointer initialization and comparison:
  - Key initialization from record and high key from record.
  - Record initialization from cursor, respecting sparse inode on-disk format.
  - Root pointer initialization from AGI root fields.
  - Key comparisons, key ordering, record ordering, and contiguity.
- Verification:
  - `xfs_inobt_verify` checks magic, V5 AG btree header, level bounds, and record limits.
  - Read/write verifiers validate CRC and structure, trace corruption, and update CRCs.
  - Buffer ops for inobt and finobt specify distinct magic values and names.
- Btree ops tables:
  - `xfs_inobt_ops`.
  - `xfs_finobt_ops`.
  - Both are AG btrees with short pointers and inode record/key sizes, but different roots, allocation reservation behavior, stats offsets, and sickness masks.
- Cursor constructors:
  - `xfs_inobt_init_cursor`.
  - `xfs_finobt_init_cursor`.
  - Both allocate cursors, hold the per-AG group, attach AGI buffer, and set current btree levels from AGI.
- Staged btree commit:
  - `xfs_inobt_commit_staged_btree` installs fake-root state into AGI root/level/blockcount fields and commits the staged btree root.
- Capacity/height calculations:
  - `xfs_inobt_block_maxrecs`.
  - On-disk max level calculations for inobt and finobt.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Sparse record helpers:
  - `xfs_inobt_irec_to_allocmask` expands a sparse record holemask into a per-inode physical allocation bitmap.
  - `xfs_inobt_rec_check_count` validates `ir_count` against the allocation bitmap in debug/warn builds.
- Reservation accounting:
  - `xfs_inobt_max_size` estimates worst-case inobt size per AG.
  - `xfs_finobt_count_blocks` counts blocks by walking the tree.
  - `xfs_finobt_read_blocks` reads `agi_fblocks` when available.
  - `xfs_finobt_calc_reserves` calculates finobt reservation ask/used.
  - `xfs_iallocbt_calc_size` wraps generic btree size calculation.

## Key Interfaces and Invariants

- Inobt and finobt share the same record format but have separate roots and magic numbers.
- Finobt uses metadata reservation unless `m_finobt_nores` disables it.
- Record ordering requires non-overlapping inode chunks: one record’s start plus `XFS_INODES_PER_CHUNK` must not exceed the next record’s start.
- V5 filesystems require AG btree header verification and CRC updates.
- Staged btree commit must update the correct AGI fields and optionally inobtcount block counters.

## Dependencies

Relies on btree core, staged btree infrastructure, AGI logging from `xfs_ialloc.c`, inode record formats from `xfs_format.h`, group references from `xfs_group`, allocation/freeing, rmap ownership constants, and health sickness masks.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.h -->
# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.h

## Purpose

`xfs_ialloc_btree.h` declares inode allocation btree cursor APIs, block layout macros, record access macros, sparse record helpers, reserve calculations, staged btree commit, max-level calculation, and cursor cache lifecycle.

## Main Content

- Defines `XFS_INOBT_BLOCK_LEN(mp)`:
  - Chooses CRC or non-CRC short btree block header size.
- Defines on-block address macros:
  - `XFS_INOBT_REC_ADDR`.
  - `XFS_INOBT_KEY_ADDR`.
  - `XFS_INOBT_PTR_ADDR`.
- Declares cursor constructors:
  - `xfs_inobt_init_cursor`.
  - `xfs_finobt_init_cursor`.
- Declares geometry helpers:
  - `xfs_inobt_maxrecs`.
  - `xfs_iallocbt_calc_size`.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Declares sparse inode conversion:
  - `xfs_inobt_irec_to_allocmask`.
  - `xfs_inobt_rec_check_count` in debug/warn builds, otherwise a zero-return macro.
- Declares finobt reservation calculation:
  - `xfs_finobt_calc_reserves`.
- Declares staged btree commit:
  - `xfs_inobt_commit_staged_btree`.
- Declares cursor cache lifecycle:
  - `xfs_inobt_init_cur_cache`.
  - `xfs_inobt_destroy_cur_cache`.

## Key Interfaces and Invariants

- Record/key/pointer address macros use one-based btree indices, matching XFS btree conventions.
- The same physical record format is used by inobt and finobt.
- Header length depends on the filesystem CRC feature and must be used instead of raw structure sizes.
- Some macros may appear unused in kernel code but are kept for userspace libxfs consumers.

## Dependencies

Depends on btree block constants from `xfs_format.h`, mount feature predicates, and inode record types. Implemented by `xfs_ialloc_btree.c`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/libxfs/xfs_ialloc_btree.h -->