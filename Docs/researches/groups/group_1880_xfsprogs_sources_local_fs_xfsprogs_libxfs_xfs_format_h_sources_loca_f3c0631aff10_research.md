# Group Research: group_1880_xfsprogs_sources_local_fs_xfsprogs_libxfs_xfs_format_h_sources_loca_f3c0631aff10

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_format.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_format.h

## Purpose
Defines the core XFS on-disk format shared by kernel-style libxfs code and userspace xfsprogs tooling. This is the authoritative layout contract for superblocks, AG headers, dinodes, quota records, symlink blocks, allocation/inode/rmap/refcount/bmap btree records, generic btree block headers, and ACL records.

## Main Contents
- Superblock format:
  - Defines historical superblock versions 1-5 and legacy `sb_versionnum` feature bits.
  - Defines v5 feature masks: compat, ro-compat, incompat, and log-incompat.
  - Supports modern flags including finobt, rmapbt, reflink, inobt block counts, sparse inodes, bigtime, large extent counts, exchange range, parent pointers, metadata directories, zoned realtime, and realtime LBA gaps.
  - Provides incore `struct xfs_sb` and ondisk `struct xfs_dsb`; changes here have repair-tool implications noted by comments.
- Address conversion macros:
  - Converts between fsblocks, AG numbers, AG blocks, disk addresses, bytes, and basic blocks.
  - Defines AG header block positions for superblock, AGF, AGI, and AGFL.
- AG metadata:
  - `struct xfs_agf` for free-space/rmap/refcount roots and counters.
  - `struct xfs_agi` for inode btree roots, free inode btree roots, inode counters, unlinked buckets, CRC/LSN, and inobt block counters.
  - `struct xfs_agfl` for AG freelist header.
- Realtime metadata:
  - Defines realtime bitmap/summary raw word storage, realtime group limits, realtime superblock `struct xfs_rtsb`, and realtime metadata btree root records.
- Time encoding:
  - Defines legacy timestamp bounds and bigtime timestamp conversion helpers.
  - Bigtime shifts XFS timestamp epoch to the legacy minimum timestamp range.
- Dinode format:
  - Defines `struct xfs_dinode`, fork access macros, inode flags, large extent count support, metadata inode constraints, device-number helpers, inode number bit slicing, and maximum inode numbers.
  - Data/attr fork sizes are derived from inode version, inode size, and `di_forkoff`.
- Quota format:
  - Defines dquot record types, bigtime quota expiry encoding, grace-period bounds, `struct xfs_disk_dquot`, and `struct xfs_dqblk`.
- Btree formats:
  - Allocation btree records and keys.
  - Inode allocation btree records, sparse inode holemask format, free masks, and inobt/finobt magic values.
  - Reverse mapping btree owners, records, key format, and offset flag packing.
  - Refcount btree records, CoW staging flag, and realtime refcount variants.
  - Bmap btree records, delayed allocation startblock encoding, max extent length, and generic short/long btree block headers.
- ACL/xattr format:
  - On-disk ACL structures and maximum entry calculations.
  - Well-known XFS ACL xattr names.

## Dependencies and Integration
- Consumed by most libxfs modules because it defines persistent metadata structures.
- Used directly by inode allocation code for `xfs_agi`, `xfs_inobt_rec`, inobt masks, inode number conversion, and btree magic values.
- Used by mount/feature logic through inline feature helpers such as `xfs_sb_is_v5`, `xfs_sb_has_*_feature`, and log-incompat helpers.
- Must remain synchronized with repair code and log-format code because layout changes affect recovery and xfs_repair validation.

## Invariants and Constraints
- Ondisk structures use explicit endian types; callers must convert via `cpu_to_be*` / `be*_to_cpu`.
- Superblock counter fields are intentionally contiguous for transaction delta application.
- AGI logging regions are split around the unlinked bucket array to avoid excessive log ranges.
- Metadata inode flags are deliberately restrictive to reduce userspace exposure risk.
- Inobt sparse records use a 16-bit holemask where nonzero bits mean physically missing inode subranges; free masks must be interpreted together with holemasks.
- Btree header sizes must be computed with macros, not `sizeof(struct xfs_btree_block)`.

## Notable Risks
- This file is ABI/persistent-format sensitive. Any field insertion, enum renumbering, or macro semantic change can break existing filesystems or userspace tooling.
- The macro `XFS_RMAP_IS_UNWRITTEN(len)` references `off` in its body; that depends on caller context or is a latent typo-style hazard.
- Feature-bit additions require coordinated updates in mkfs, mount validation, repair, scrub, geometry reporting, and compatibility checks.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_format.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_fs.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_fs.h

## Purpose
Defines the userspace-facing XFS filesystem ABI: ioctl numbers, ioctl payload structures, geometry records, bulkstat/inumbers records, scrub interfaces, health monitor events, media verification, parent-pointer iteration, exchange/commit range interfaces, and legacy compatibility structures.

## Main Contents
- Mapping and direct I/O:
  - `struct dioattr` for direct I/O alignment.
  - `struct getbmap` and `struct getbmapx` plus `BMV_IF_*` and `BMV_OF_*` flags for extent mapping queries.
  - FS map owner constants for XFS metadata classes.
- Filesystem geometry:
  - Versioned geometry structs `xfs_fsop_geom_v1`, `xfs_fsop_geom_v4`, and current `xfs_fsop_geom`.
  - Current geometry includes health bitmaps, realtime group count/size, internal realtime start, and zoned RT reservations.
  - Geometry feature flags mirror superblock features and are exported through `XFS_IOC_FSGEOMETRY`.
- AG and RT group geometry:
  - `struct xfs_ag_geometry` reports AG free blocks, inode counts, and health status.
  - `struct xfs_rtgroup_geometry` reports realtime group length and health status.
- Bulk inode reporting:
  - Legacy `xfs_bstat` and modern `xfs_bulkstat`.
  - `xfs_inogrp` and modern `xfs_inumbers`.
  - `xfs_bulk_ireq` controls bulkstat/inumbers requests with flags for AG restriction, special inode targets, 64-bit extent counts, and metadata directory visibility.
- Handles and attributes:
  - File handle structs and handle-based path/open/readlink/attribute ioctl payloads.
  - Attribute list cursor and multi-operation records matching libattr layouts.
- Scrub and repair:
  - `struct xfs_scrub_metadata` and scrub type constants for all major metadata classes.
  - Vectored scrub via `xfs_scrub_vec` and `xfs_scrub_vec_head`.
  - Scrub flags distinguish requested repair/rebuild from output conditions such as corrupt, preen, xfail, xcorrupt, incomplete, warning, and no-repair-needed.
  - Metadata path scrub selectors cover quota and realtime metadata directory entries.
- Exchange/commit range:
  - `struct xfs_exchange_range` and `struct xfs_commit_range` support crash-restartable file range exchange/commit workflows.
  - Flags cover to-EOF exchange, dsync, dry run, and file1-written-only exchanges.
- Parent pointers:
  - `xfs_getparents`, `xfs_getparents_rec`, by-handle variant, cursor helpers, and flags for root/done reporting.
- Health monitor and media verification:
  - Defines health monitor domains, event types, event payload union, monitor control struct, and same-filesystem fd check.
  - Defines shutdown reason bits, media error payloads, file range I/O event payloads, and `xfs_verify_media`.
- Ioctl numbers:
  - Maps all XFS ioctl commands, including legacy IRIX-derived commands and current Linux commands, under the `'X'` ioctl namespace.
  - Keeps basic block macros available when not supplied by the build environment.

## Dependencies and Integration
- Included by userspace tools and libxfs code that must share ioctl ABI with Linux XFS.
- Depends on kernel-style integer and ioctl types, `FS_IOC_*`, `FMR_OWNER`, user pointer annotations, and basic XFS typedefs supplied elsewhere.
- Health flags correspond to sickness masks defined in `xfs_health.h`.
- Geometry flags correspond to superblock feature bits in `xfs_format.h`.

## Invariants and Constraints
- The file explicitly states it must compile with C++ compilers.
- Struct layout, padding, reserved fields, and ioctl numbers are ABI-stable and must not be casually changed.
- Reserved fields are generally required to be zero, enabling future ABI expansion.
- Legacy and modern versions coexist because older tools and kernels still use older structure layouts.
- `XFS_BULK_IREQ_NREXT64` changes where extent count is returned and defines overflow behavior.

## Notable Risks
- ABI breakage is the main risk: changing type widths, field order, padding, or ioctl numbers can break userspace.
- Several features represented here are coupled to other files: adding a scrub type or health bit requires conversion code in health, scrub, geometry, and reporting paths.
- Health monitor unions are deliberately non-anonymous for bindgen compatibility; changing that could break Rust/Python client generation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_group.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_group.c

## Purpose
Implements the generic XFS group lifetime and lookup abstraction used for allocation groups and realtime groups. Groups are stored in mount-level xarrays and use separate passive and active reference counts.

## Main Functions
- `xfs_group_get`:
  - RCU-loads a group by index/type from `mp->m_groups[type].xa`.
  - Takes a passive reference if found.
- `xfs_group_hold`:
  - Takes another passive reference from an existing group pointer.
  - Requires either passive or active refs already exist.
- `xfs_group_put`:
  - Drops a passive reference.
- `xfs_group_grab`:
  - RCU-loads a group and attempts to take an active reference via `atomic_inc_not_zero`.
  - Fails if the group is being offlined/shrunk and active refs are zero.
- `xfs_group_next_range`:
  - Iterates through a numeric group range, releasing the previous active ref and grabbing the next group.
- `xfs_group_grab_next_mark`:
  - Iterates to the next xarray entry with a specified mark, taking an active reference.
- `xfs_group_rele`:
  - Drops an active reference.
- `xfs_group_insert`:
  - Initializes mount/index/type, kernel-only busy extent or hook state, defer-drain state, and sets the mount-owned active reference.
  - Inserts the group into the mount xarray.
- `xfs_group_free`:
  - Removes the group from the xarray, checks passive refs are gone, frees drain/busy state, runs optional uninit, drops mount active ref, verifies active refs are zero, and RCU-frees.
- `xfs_group_get_by_fsb`:
  - Converts a filesystem block to group number and takes a passive reference.

## Dependencies and Integration
- Uses xarray APIs, RCU read-side protection, atomics, tracing, defer-drain infrastructure, and kernel-only extent busy/rmap hook structures.
- `xfs_group.h` supplies the structure and conversion helpers.
- Mount geometry in `mp->m_groups[type]` defines group block/log/mask parameters.

## Invariants and Control Flow
- Passive refs protect longer-lived cached holders; the freeing path is responsible for cleaning those holders before `xfs_group_free`.
- Active refs represent online usability; a mount-owned active ref keeps the group online.
- Removing/offlining a group prevents new active refs because `atomic_inc_not_zero` fails once active refs reach zero.
- Iterators transfer active references by releasing the previous group before grabbing the next.

## Notable Risks
- `xfs_group_free` assumes `xa_erase` returns a valid group; callers must ensure the xarray entry exists.
- Consumers that break out of `xfs_group_next_range` or marked iteration early must release the active ref themselves.
- Passive ref misuse can leave cached objects pointing at groups past the intended cleanup point.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_group.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_group.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_group.h

## Purpose
Declares the generic `struct xfs_group` and helper APIs/macros for allocation-group or realtime-group lifetime, xarray marks, geometry conversion, and group-block verification.

## Main Contents
- `struct xfs_group`:
  - Common fields: mount pointer, group number, group type, passive refcount, active refcount.
  - Precomputed geometry: usable block count and minimum usable group block.
  - Kernel-only fields:
    - Busy extent tree or zoned RT reset list linkage.
    - Health state bitsets (`xg_checked`, `xg_sick`) protected by `xg_state_lock`.
    - Deferred intent drain used by scrub/repair to avoid transient inconsistencies.
    - Rmap update hooks for online repair.
- Reference/lifetime declarations:
  - Passive: `xfs_group_get`, `xfs_group_get_by_fsb`, `xfs_group_hold`, `xfs_group_put`.
  - Active: `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, `xfs_group_rele`.
  - Lifecycle: `xfs_group_insert`, `xfs_group_free`.
- Xarray mark macros:
  - `xfs_group_set_mark`, `xfs_group_clear_mark`, `xfs_group_marked`.
- Geometry helpers:
  - `xfs_group_max_blocks`, `xfs_groups_to_rfsbs`, `xfs_group_start_fsb`, `xfs_gbno_to_fsb`, `xfs_gbno_to_daddr`.
  - `xfs_fsb_to_gno`, `xfs_fsb_to_gbno`.
  - `xfs_verify_gbno`, `xfs_verify_gbext`.

## Dependencies and Integration
- Used by per-AG wrappers, realtime group wrappers, btree cursors, inode allocation, health tracking, and block mapping code.
- Depends on mount-level `m_groups[type]` geometry fields: `blocks`, `blklog`, `blkmask`, `start_fsb`, and `has_daddr_gaps`.

## Invariants
- `xg_active_ref` being nonzero means the group is online for active operations.
- `xg_ref` tracks passive holders that must be drained before final free.
- `xfs_gbno_to_daddr` chooses either gap-aware fsblock conversion or direct group-block multiplication based on group geometry.
- `xfs_verify_gbext` rejects zero-length extents and detects overflow when checking extent end.

## Notable Risks
- Inline conversion helpers assume mount group geometry is initialized and consistent.
- `xfs_fsb_to_gno` returns zero when `blklog` is zero, so callers must understand singleton group types.
- Kernel-only members make the same header serve userspace and kernel contexts with conditional behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_group.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_health.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_health.h

## Purpose
Defines in-core XFS metadata health state masks and public health helper prototypes. It provides the common vocabulary for scrub, repair, runtime corruption detection, geometry reporting, bulkstat reporting, and health monitor conversion.

## Main Contents
- Health model:
  - Each domain has `checked` and `sick` bitsets.
  - `checked && sick` means checked and needs repair.
  - `checked && !sick` means checked healthy.
  - `!checked && sick` means runtime evidence exists but no thorough check.
  - `!checked && !sick` means not examined since mount.
- Filesystem health flags:
  - Counters, user/group/project quota, quota check, nlinks, metadata directory tree, metadata path.
- Realtime group health flags:
  - Superblock, bitmap, summary, rmapbt, refcountbt.
- AG health flags:
  - Superblock, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcntbt, bad inodes.
- Inode health flags:
  - Core, data/attr/cow bmaps, directory, xattrs, symlink, parent pointers, erased/zapped fork states, forget marker, directory tree.
- Mask groupings:
  - Primary, secondary, indirect, zapped, and all masks per domain.
- Mark/measure APIs:
  - Filesystem, group/AG/RTG, and inode mark sick/corrupt/healthy/measure functions.
  - Helpers for bmap, btree, dirattr, and da-args sickness marking.
- Query helpers:
  - `xfs_fs_has_sickness`, `xfs_group_has_sickness`, `xfs_inode_has_sickness`, and healthy checks.
- Reporting conversion:
  - Geometry and bulkstat health fill functions.
  - Health monitor mask conversion helpers.
- Error helper:
  - `xfs_metadata_is_sick(error)` recognizes `-EFSCORRUPTED` and `-EFSBADCRC`.

## Dependencies and Integration
- Consumed by inode allocation and btree verifier paths to mark AGI/inobt/finobt sickness on corruption.
- Exported masks map onto userspace ABI masks in `xfs_fs.h`.
- `struct xfs_group` stores group health fields under kernel builds.

## Invariants
- Runtime code should call `mark_sick` when observing corruption without implying full checking.
- Fsck/scrub tools should use `mark_corrupt` when a checked object is corrupt and `mark_healthy` after successful repair.
- Secondary evidence can be forgotten when primary problems are fixed.
- Indirect evidence indicates a problem elsewhere after resource/context release.

## Notable Risks
- Masks must remain coordinated with userspace reporting masks and health monitor conversion functions.
- Misclassifying primary vs secondary vs indirect evidence can either over-report repairs or hide root causes.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_health.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.c

## Purpose
Implements XFS inode allocation, inode freeing, inode mapping, AGI logging/verification, inode allocation geometry setup, inobt record validation/counting, sparse inode handling, and shrink safety checks.

## Main Functional Areas
- Inobt record operations:
  - `xfs_inobt_lookup` sets cursor search key and calls generic btree lookup.
  - `xfs_inobt_update` serializes incore records to ondisk format, respecting sparse inode feature support.
  - `xfs_inobt_btrec_to_irec` converts ondisk records into normalized incore form.
  - `xfs_inobt_rec_freecount` calculates real free inode count, masking out sparse holes.
  - `xfs_inobt_check_irec` validates start/end agino bounds, count limits, freecount bounds, and freecount consistency.
  - `xfs_inobt_get_rec` wraps generic record read plus validation and sickness marking.
  - `xfs_inobt_insert_rec` inserts the current cursor record.
- New inode chunk initialization:
  - `xfs_ialloc_inode_init` zeroes inode buffers, stamps magic/version/generation/unlinked state, sets v3 inode number and UUID, calculates CRCs, and logs or delayed-writes buffers depending on transaction context.
  - V3 inode creation logs a logical icreate item and treats buffers as ordered allocation buffers.
- Sparse inode record handling:
  - `xfs_align_sparse_ino` aligns sparse chunks to full inode chunk boundaries and shifts allocation masks.
  - `__xfs_inobt_can_merge` and `__xfs_inobt_rec_merge` validate and merge sparse records.
  - `xfs_inobt_insert_sprec` inserts or merges sparse inobt records.
  - `xfs_finobt_insert_sprec` inserts or replaces corresponding finobt records using merged inobt state.
- Allocating inode chunks:
  - `xfs_ialloc_ag_alloc` chooses an extent for a new inode chunk.
  - Tries exact allocation after the last chunk, then near-root allocation with stripe/cluster alignment, then sparse allocation if enabled.
  - Initializes inode buffers, inserts inobt/finobt records, updates AGI counts, perag counters, and superblock counters.
  - Enforces max inode count and leaves space for btree splits.
- Allocating individual inodes:
  - `xfs_dialloc_ag_inobt` searches the inobt when finobt is unavailable, preferring parent locality and cached left/right search positions.
  - `xfs_dialloc_ag_finobt_near` finds the closest free inode record to the parent using the finobt.
  - `xfs_dialloc_ag_finobt_newino` uses AGI `agi_newino` or first free finobt record.
  - `xfs_dialloc_ag_update_inobt` mirrors finobt allocation changes into inobt and verifies both records match.
  - `xfs_dialloc_ag` dispatches finobt or inobt algorithm, updates AGI/perag/superblock free counts, and avoids sick inode clusters when possible.
  - `xfs_dialloc` picks an AG, handles low-space retry policy, tries AGs with/without trylocks, and rejects obviously corrupt allocations such as reallocating the parent inode.
- Freeing inodes:
  - `xfs_difree_inode_chunk` frees whole or sparse physical inode chunk extents.
  - `xfs_difree_inobt` marks an inode free, deletes fully free chunks when allowed, updates counters, and returns chunk deletion details via `xfs_icluster`.
  - `xfs_difree_finobt` independently mirrors the free operation in finobt, inserting/updating/deleting finobt records as required.
  - `xfs_difree` validates inode-to-AG mapping, reads AGI, updates inobt, then finobt if enabled.
- Mapping inode numbers:
  - `xfs_imap_lookup` verifies an inode number against inobt for untrusted lookups or unaligned chunks.
  - `xfs_imap` maps inode number to disk address, buffer length, and byte offset, using arithmetic fast paths when safe and btree lookup otherwise.
- AGI logging and verification:
  - `xfs_ialloc_log_agi` logs only requested AGI fields and splits ranges around the unlinked bucket region.
  - `xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate magic, version, UUID, LSN, AG length, btree levels, and unlinked inode buckets.
  - `xfs_read_agi` reads and types AGI buffers, marking AGI sick on metadata corruption.
  - `xfs_ialloc_read_agi` initializes perag inode counters from AGI and debug-checks stale AGI/perag mismatch.
- Counting and shrink support:
  - `xfs_ialloc_has_inodes_at_extent` classifies an extent as empty/full/sparse of physical inode records.
  - `xfs_ialloc_count_inodes` sums count/freecount across all inobt records.
  - `xfs_ialloc_setup_geometry` computes inode btree record capacities, max levels, max inode count, cluster sizes, alignment, min folio order, and default new inode flags.
  - `xfs_ialloc_calc_rootino` predicts mkfs root inode placement from AG0 metadata layout.
  - `xfs_ialloc_check_shrink` prevents shrinking an AG past sparse inode records that would extend beyond the new end.

## Dependencies and Integration
- Depends heavily on:
  - `xfs_format.h` for AGI, inode, inobt, and conversion formats.
  - `xfs_ialloc_btree.c/h` for inobt/finobt cursors and allocation masks.
  - Free-space allocator APIs for inode chunk extent allocation/freeing.
  - Transaction APIs for buffer logging, rolling, superblock counter deltas, and ordered inode allocation buffers.
  - Health APIs to mark AGI/inobt/finobt/inodes sick.
  - Mount/perag geometry from `xfs_mount.h` and `xfs_ag.h`.

## Invariants
- Inobt is authoritative for all inode chunks; finobt only tracks records with at least one free inode.
- Inobt and finobt record contents must match whenever both contain a record.
- Sparse inode records require holemask-aware freecount and allocation mask handling.
- AGI `agi_count`, `agi_freecount`, perag counters, and superblock counters must be updated together.
- V3 inode initialization requires full inode CRC coverage and logical icreate logging.
- Untrusted inode lookups must validate against the inode btree before reading stale disk inodes.
- Fully free inode chunks can be removed only when block size does not pack multiple chunks into one filesystem block.

## Notable Risks
- Counter synchronization is delicate; debug checks exist because stale AGI/AGF state can imply storage write loss or corruption.
- Allocation near ENOSPC intentionally has a two-pass policy, but comments note the AG free-space precheck is imperfect with per-AG reservations.
- Sparse inode merge failure is treated as serious corruption and can force shutdown.
- `xfs_dialloc_roll` deliberately moves quota accounting across transaction roll boundaries; mishandling this could charge the wrong transaction.
- `xfs_imap` must avoid arithmetic shortcuts for untrusted or unaligned cases to prevent stale inode exposure.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.h

## Purpose
Declares the inode allocation public interface for libxfs: inode allocation/freeing, inode number mapping, AGI reads/logging, inobt operations, inode chunk initialization, inobt record validation/counting, geometry setup, root inode calculation, and shrink checks.

## Main Contents
- Constants and helper types:
  - `XFS_INODE_BIG_CLUSTER_SIZE` defines the target inode cluster movement size.
  - `struct xfs_icluster` reports whether a freed inode caused chunk deletion, the first inode, and physical allocation bitmap for sparse chunks.
- Helper:
  - `xfs_make_iptr` maps a buffer plus inode index to an ondisk dinode pointer.
- Allocation/free APIs:
  - `xfs_dialloc` allocates an ondisk inode.
  - `xfs_difree` frees an ondisk inode and reports chunk-level deletion state.
- Mapping/read APIs:
  - `xfs_imap` converts inode number to buffer mapping information.
  - `xfs_read_agi` and `xfs_ialloc_read_agi` read AGI buffers; `XFS_IALLOC_FLAG_TRYLOCK` controls trylock behavior.
- Btree record APIs:
  - `xfs_inobt_lookup`, `xfs_inobt_get_rec`, `xfs_inobt_rec_freecount`, `xfs_inobt_insert_rec`.
  - `xfs_inobt_btrec_to_irec` and `xfs_inobt_check_irec`.
- Higher-level helpers:
  - `xfs_ialloc_inode_init`.
  - `xfs_ialloc_has_inodes_at_extent`.
  - `xfs_ialloc_count_inodes`.
  - `xfs_ialloc_cluster_alignment`, `xfs_ialloc_setup_geometry`, `xfs_ialloc_calc_rootino`.
  - `xfs_ialloc_check_shrink`.

## Dependencies and Integration
- Implemented mainly by `xfs_ialloc.c`; cursor creation and masks come from `xfs_ialloc_btree.c/h`.
- Exposes functions used by inode creation/removal, scrub/repair, mkfs/recovery-style initialization, grow/shrink code, and inode lookup code.

## Invariants
- Callers freeing an inode must pass a perag matching the inode AG.
- `xfs_imap` accepts flags affecting trust and lookup behavior.
- Inobt record helpers return normalized incore records regardless of sparse inode feature encoding.
- `struct xfs_icluster.alloc` describes physical inode allocation, not logical free/allocated inode state.

## Notable Risks
- This header is a narrow public boundary for inode allocation internals; signature changes ripple across inode, scrub, repair, and mkfs code.
- The declaration `xfs_ialloc_cluster_alignment` is present here but not defined in the read file, so implementation is elsewhere in the source tree.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.c

## Purpose
Implements inode allocation btree and free inode btree cursor operations, block allocation/freeing, record/key callbacks, buffer verifiers, staged btree commit, record capacity calculations, sparse inode allocation mask conversion, finobt reserve calculation, and cursor cache lifecycle.

## Main Functional Areas
- Cursor operation callbacks:
  - Min/max records derive from mount inode geometry.
  - Duplicate cursor callbacks recreate inobt or finobt cursors for the same perag, transaction, and AGI buffer.
  - Root setters update AGI root/level fields for inobt or finobt and log AGI fields.
  - Key/record initializers and comparators operate on `ir_startino`.
  - Record ordering requires each inode chunk start to be at least `XFS_INODES_PER_CHUNK` after the prior record.
- Btree block accounting:
  - `xfs_inobt_mod_blockcount` updates AGI `agi_iblocks` or `agi_fblocks` when inobtcounts are enabled.
- Block allocation/freeing:
  - Inobt alloc/free uses normal AG reservation.
  - Finobt alloc/free uses metadata reservation unless `m_finobt_nores` is set.
  - Allocations request one block near the provided start block and tag reverse mapping owner as inobt.
  - Frees defer extent freeing through transaction infrastructure.
- Verification:
  - `xfs_inobt_verify` validates magic, v5 AG btree header, level bounds, and record capacity.
  - Read verifier checks CRC then structure; write verifier checks structure then updates CRC.
  - Shared read/write verifier logic supports both inobt and finobt through separate `xfs_buf_ops`.
- Btree ops tables:
  - `xfs_inobt_ops` and `xfs_finobt_ops` wire generic btree code to inode-specific callbacks, stats, buffer ops, and health masks (`XFS_SICK_AG_INOBT`, `XFS_SICK_AG_FINOBT`).
- Cursor initialization:
  - `xfs_inobt_init_cursor` and `xfs_finobt_init_cursor` allocate generic btree cursors, hold the perag group, attach AGI buffer, and set levels from AGI when available.
- Staged btree commit:
  - `xfs_inobt_commit_staged_btree` installs staged fake roots into AGI for inobt or finobt and logs root/level/block-count fields.
- Sizing:
  - `xfs_inobt_maxrecs` computes records per btree block after subtracting header length.
  - `xfs_iallocbt_maxlevels_ondisk` computes the maximum possible height of inobt/finobt for ondisk constraints.
  - `xfs_iallocbt_calc_size` estimates blocks needed for a given number of records.
- Sparse inode helpers:
  - `xfs_inobt_irec_to_allocmask` expands sparse record holemask into a per-inode physical allocation bitmap.
  - `xfs_inobt_rec_check_count` debug-validates `ir_count` against the expanded allocation mask.
- Finobt reservations:
  - `xfs_finobt_calc_reserves` reads or counts finobt blocks and adds maximum theoretical reservation ask plus actual used blocks.
  - Uses `agi_fblocks` when inobtcounts are available, otherwise walks the btree.
- Cursor cache:
  - `xfs_inobt_init_cur_cache` creates a kmem cache sized for maximum inode btree levels.
  - `xfs_inobt_destroy_cur_cache` destroys it.

## Dependencies and Integration
- Uses generic btree framework, staged btree framework, allocation APIs, reverse mapping owner info, AGI logging from `xfs_ialloc.c`, perag/group wrappers, health masks, and inode geometry.
- Exports buffer ops used when reading inobt/finobt blocks.
- Provides cursor constructors consumed by inode allocation/freeing, scrub, repair, and btree rebuild code.

## Invariants
- Inobt and finobt share record format but use different roots, levels, stats, reservations, and health masks.
- Cursor `bc_group` holds a passive reference to the perag group.
- V5 btree blocks require CRC/header verification; level must be less than inode geometry maxlevels.
- Inobt block counters are updated only when feature support exists.
- Sparse holemask zero bits represent physically allocated inode subranges after inversion/expansion.

## Notable Risks
- Any mismatch between AGI roots/levels/block counters and actual btree structure can corrupt inode allocation.
- Finobt reservation behavior depends on `m_finobt_nores`; incorrect setting can affect metadata reservation accounting.
- Staged btree commits require callers to invalidate/free old blocks separately, as noted by comments.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.h

## Purpose
Declares inode allocation btree layout helpers, cursor constructors, record capacity helpers, sparse inode allocation mask conversion, finobt reserve calculation, staged commit, maximum-level calculation, and cursor cache lifecycle.

## Main Contents
- Header sizing:
  - `XFS_INOBT_BLOCK_LEN(mp)` chooses CRC or non-CRC short btree header length.
- Block layout access macros:
  - `XFS_INOBT_REC_ADDR`, `XFS_INOBT_KEY_ADDR`, and `XFS_INOBT_PTR_ADDR` compute record/key/pointer addresses within a btree block.
  - Comments note that some macros are used in userspace even if they appear unused.
- Cursor constructors:
  - `xfs_inobt_init_cursor` for inode allocation btree.
  - `xfs_finobt_init_cursor` for free inode btree.
- Capacity and sizing:
  - `xfs_inobt_maxrecs`.
  - `xfs_iallocbt_calc_size`.
  - `xfs_iallocbt_maxlevels_ondisk`.
- Sparse inode support:
  - `xfs_inobt_irec_to_allocmask`.
  - Debug/warn `xfs_inobt_rec_check_count`.
- Finobt and rebuild support:
  - `xfs_finobt_calc_reserves`.
  - `xfs_inobt_commit_staged_btree`.
- Cursor cache lifecycle:
  - `xfs_inobt_init_cur_cache`.
  - `xfs_inobt_destroy_cur_cache`.

## Dependencies and Integration
- Implemented by `xfs_ialloc_btree.c`.
- Used by inode allocation/freeing, scrub, repair, btree rebuild, and userspace tools that inspect btree block layouts.
- Depends on ondisk record/key/pointer types from `xfs_format.h`.

## Invariants
- Address macros use 1-based btree indexes consistent with XFS btree code.
- Header length must account for CRC feature state.
- Finobt and inobt use the same record shape but different roots and semantics.

## Notable Risks
- The address macros perform raw pointer arithmetic over ondisk buffers; wrong maxrecs/header inputs will misaddress records.
- Because userspace uses some macros directly, layout changes require broad compatibility review.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ialloc_btree.h -->