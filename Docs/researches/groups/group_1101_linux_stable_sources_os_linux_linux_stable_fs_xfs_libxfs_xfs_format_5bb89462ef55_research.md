# Group Research: group_1101_linux_stable_sources_os_linux_linux_stable_fs_xfs_libxfs_xfs_format_5bb89462ef55

Scope: `Docs/research_subset_a.md`; source tree `sources/os/linux/linux-stable` is included in subset A.

Files researched:
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_format.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_fs.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_health.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.h`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.c`
- `sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_format.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_format.h

## Role in the repository

`xfs_format.h` is the central XFS on-disk format header for general metadata objects. It defines the binary layout, magic values, feature bits, sizing constants, and address conversion macros for the superblock, allocation group headers, realtime metadata, dinodes, quotas, symlinks, and the common btree record formats used by libxfs and kernel XFS code.

Directory/attribute formats and log formats are intentionally kept in other headers, so this file is the shared format contract for most non-directory on-disk structures.

## Superblock and feature model

The file defines both the incore `struct xfs_sb` and on-disk `struct xfs_dsb`. The on-disk form uses fixed-endian fields and includes legacy fields plus v5 additions such as CRC, feature masks, metadata UUID, metadata directory root, realtime group geometry, internal realtime start, and zoned realtime reservations.

Feature handling is split across:
- legacy `sb_versionnum` bits;
- older `sb_features2` bits;
- v5 compat, read-only compat, incompat, and log-incompat masks.

The v5 feature masks cover modern features including FINOBT, RMAPBT, reflink, INOBT block counts, ftype, sparse inodes, metadata UUID, bigtime, needsrepair, 64-bit extent counters, exchange range, parent pointers, metadata directories, zoned realtime, and realtime-group LBA gaps. Inline helpers test or mutate these feature fields.

## Addressing and allocation group formats

The header defines filesystem block, basic block, byte, allocation group, and disk address conversion macros. These are used throughout XFS to translate between global filesystem blocks, AG-relative blocks, disk addresses, and inode-derived positions.

Allocation group metadata formats include:
- `struct xfs_agf`, tracking free-space btree roots, levels, free counts, longest extent, rmap/refcount roots, btree block usage, UUID, LSN, and CRC.
- `struct xfs_agi`, tracking inode btree roots, levels, inode counts, free inode counts, unlinked inode buckets, FINOBT roots, and INOBT/FINOBT block counters.
- `struct xfs_agfl`, the AG freelist header.

The file also defines AGF and AGI logging bitmasks used by transaction code to log precise field ranges.

## Realtime metadata

Realtime definitions include old and realtime-group raw word formats for bitmap and summary words, realtime group limits, the realtime superblock `struct xfs_rtsb`, and constants for realtime bitmap/summary buffer headers. Realtime groups introduce per-group metadata and big-endian on-disk words for newer formats.

## Timestamp and metadata inode formats

The timestamp section documents legacy signed 32-bit second timestamps and bigtime unsigned 64-bit nanosecond-era timestamps. Helpers convert between Unix seconds and bigtime seconds. Quota bigtime conversion helpers similarly trade precision for wider expiration ranges.

`enum xfs_metafile_type` defines on-disk metadata inode types such as metadata directories, quota files, realtime bitmap/summary, realtime rmap, and realtime refcount files.

## Dinode format

`struct xfs_dinode` defines the on-disk inode core, including mode, format, ownership, project id, extent counters, timestamps, size, block count, flags, unlinked list pointer, v3 CRC fields, changecount, LSN, flags2, CoW/RT metadata fields, creation time, inode number, and UUID.

Important related definitions include:
- inode core size helpers for v2 versus v3 inodes;
- data/attribute fork size and pointer macros;
- device-number accessors for special files;
- legacy `di_flags` and newer `di_flags2`;
- metadata inode constraints and metadata flag definitions;
- inode number decomposition and composition macros.

The file also defines maximum extent count constants for old and large extent counter formats.

## Btree record formats

The header defines on-disk records, keys, pointers, and magic values for:
- allocation btrees by block number and by length;
- inode allocation btree and free inode btree;
- reverse mapping btree;
- realtime reverse mapping btree;
- refcount btree and realtime refcount btree;
- bmap btree records and inode-rooted bmap roots;
- generic short and long btree block headers.

The inode allocation record has full and sparse encodings. Sparse inode records use a holemask, inode count, free count, and free bitmap to represent partially allocated inode chunks.

## Other on-disk objects

The file defines dquot records and blocks, quota timer limits, remote symlink headers and limits, ACL records, ACL sizing rules, and on-disk ACL xattr names.

## Important invariants

- On-disk structures are fixed ABI; field order, endian annotations, padding, and size comments matter.
- V5 CRC fields must be accessed only when the filesystem supports CRC metadata.
- Superblock summary counter fields must remain contiguous for transaction delta application.
- Sparse inode records use zero holemask bits for physically allocated inode regions.
- Inode and block conversion macros assume mount geometry fields have already been validated.
- `sizeof(struct xfs_btree_block)` must not be used as an actual disk header size; short/long and CRC/non-CRC macros determine the real header length.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_format.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_fs.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_fs.h

## Role in the repository

`xfs_fs.h` is the XFS userspace ABI header. It defines ioctl structures, ioctl numbers, geometry reports, bulk inode reporting, scrub and repair controls, file range exchange/commit operations, parent pointer iteration, health monitoring, media verification, and legacy compatibility interfaces. It is LGPL-licensed and written to remain C++ compilable.

## Mapping and extent reporting ABI

The file defines:
- `struct dioattr` for direct I/O alignment limits.
- `struct getbmap` and `struct getbmapx` for block mapping queries.
- `BMV_IF_*` input flags for data, attr, CoW, prealloc, delalloc, and hole filtering.
- `BMV_OF_*` output flags for preallocation, delayed allocation, last extent, and shared extents.
- `XFS_FMR_OWN_*` owner values for `FS_IOC_GETFSMAP`.

These structures provide userspace with file and filesystem extent layout information.

## Filesystem geometry and AG geometry

The header defines multiple geometry ABI versions:
- `xfs_fsop_geom_v1`
- `xfs_fsop_geom_v4`
- `xfs_fsop_geom`

The current geometry structure reports filesystem size, realtime size, log placement, UUID, stripe geometry, feature flags, health masks, realtime group count/size, internal realtime start, and zoned realtime reservations.

Feature flag exports include attr, nlink, quota, alignment, dirv2, logv2, sector size, attr2, projid32, lazy superblock counters, v5 superblock, ftype, FINOBT, sparse inodes, RMAPBT, reflink, bigtime, INOBT counters, 64-bit extent counters, exchange range, parent pointers, metadata directories, and zoned realtime.

`struct xfs_ag_geometry` reports per-AG length, free blocks, inode counts, health masks, and flags. `struct xfs_rtgroup_geometry` performs the same role for realtime groups and includes zoned write pointer reporting.

## Bulk inode and inode number ABI

Legacy `struct xfs_bstat` and newer `struct xfs_bulkstat` report inode attributes, timestamps, extent counts, project id, fork offset, CoW/extent hints, health state, and large data fork extent counts.

`struct xfs_inogrp` and `struct xfs_inumbers` report allocated inode chunks. `struct xfs_bulk_ireq` is the shared request header for modern bulkstat and inumbers ioctls, with flags for AG-limited scans, special inode requests, 64-bit extent count reporting, and metadata directory visibility.

## Handles and attribute-by-handle ABI

The file defines handle request structures for path-to-handle, fd-to-handle, open-by-handle, readlink-by-handle, attr-list-by-handle, and attr-multi-by-handle. Attribute list structures mirror libattr ABI layouts, including the opaque attrlist cursor and variable-length name entries.

## Scrub and repair ABI

`struct xfs_scrub_metadata` describes one scrub target. `XFS_SCRUB_TYPE_*` enumerates scrub targets for superblocks, AG headers, btrees, inode forks, directories, xattrs, symlinks, parent pointers, realtime metadata, quotas, fs counters, link counts, directory tree structure, metadata paths, realtime group superblocks, realtime rmap, and realtime refcount.

Scrub flags distinguish requested repair or forced rebuild from output states such as corrupt, preen, cross-reference failure, cross-reference corruption, incomplete, warning, and no repair needed. The vectored scrub ABI uses `struct xfs_scrub_vec` and `struct xfs_scrub_vec_head`, with a barrier vector type for dependency-sensitive batches.

## File exchange, commit range, and parent pointers

`struct xfs_exchange_range` describes an atomic range exchange between file1 and file2. `struct xfs_commit_range` extends this with file2 freshness fields so a prepared file can be committed only if the target has not changed.

Exchange flags support exchange-to-EOF, dsync, dry run, and file1-written-only behavior.

Parent pointer iteration uses `struct xfs_getparents`, `struct xfs_getparents_rec`, and by-handle variants. Inline helpers advance through variable-length parent records safely within the supplied buffer.

## Health monitor and media verification ABI

The health monitor section defines event domains for mount, fs, AG, inode, realtime group, devices, and file ranges. Event types include monitor status, unmount, sick/corrupt/healthy metadata, shutdown, media errors, pagecache I/O errors, direct I/O errors, and data loss.

`struct xfs_health_monitor_event` carries a timestamp and a domain-specific payload. `struct xfs_health_monitor` starts monitoring, and `struct xfs_health_file_on_monitored_fs` validates that an fd belongs to the monitored filesystem.

`struct xfs_verify_media` defines device media verification ranges and pacing, with optional reporting.

## Ioctl command surface

The bottom of the file assigns the XFS ioctl numbers for direct I/O info, extent maps, reserve/unreserve/zero range, EOF block trimming, scrub, AG geometry, parent pointers, vectored scrub, realtime group geometry, health monitor, media verify, geometry, bulkstat, inumbers, handles, growfs, counts, reserved blocks, error injection, freeze/thaw, going down, exchange range, and commit range.

## Important invariants

- This header is userspace ABI; structure sizes, field offsets, reserved zero fields, and ioctl numbers are compatibility-sensitive.
- Legacy and modern structures coexist because old tools and kernels still consume old ABI layouts.
- Health masks in this file are exported encodings derived from internal health flags, not the internal flags themselves.
- Variable-length ABI buffers carry explicit sizes and record lengths; callers must not infer layout beyond the documented fields.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_fs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.c

## Role in the repository

`xfs_group.c` implements generic XFS group lifetime management. A group is the common abstraction behind allocation groups and realtime groups. The file manages lookup, passive references, active references, iteration, xarray insertion/removal, and group teardown.

## Reference model

Groups have two separate reference types:
- Passive references keep a group object alive for cached objects and long-lived holders. They are manipulated by `xfs_group_get`, `xfs_group_hold`, and `xfs_group_put`.
- Active references represent short-term online access to a group for walking trees or touching mutable state. They are manipulated by `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, and `xfs_group_rele`.

Active lookups use `atomic_inc_not_zero`, so a group that is being offlined or shrunk cannot be grabbed.

## Lookup and iteration

`xfs_group_get` and `xfs_group_grab` load groups from `mp->m_groups[type].xa` under RCU. `xfs_group_next_range` advances sequentially through a bounded index range, releasing the previous active reference as it moves. `xfs_group_grab_next_mark` finds the next group carrying an xarray mark, also releasing the previous active reference.

`xfs_group_get_by_fsb` maps a filesystem block to a group number for the requested group type and returns a passive reference.

## Insertion and removal

`xfs_group_insert` initializes the common group fields, optional kernel-only busy extent tracking, state lock, rmap update hooks, deferred intent drain, and the mount-owned active reference. It then inserts the group into the mount xarray.

`xfs_group_free` erases the group from the xarray, checks that passive references are gone, frees deferred drain and busy extent state, calls an optional type-specific uninit callback, drops the mount-owned active reference, checks active reference accounting, and finally frees the group via RCU-aware freeing.

## Important invariants

- The mount-owned active reference means a group is online.
- Active references must drop to zero before group memory can be freed.
- Passive references must already be cleaned up by the code responsible for cached objects.
- Iteration helpers transfer ownership by releasing the previous active reference before returning the next.
- Group xarray operations are indexed by both group number and group type.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.h

## Role in the repository

`xfs_group.h` defines the generic XFS group structure and helper APIs used by allocation groups and realtime groups. It centralizes group references, group geometry, state/health fields, deferred intent draining, rmap update hooks, xarray marks, and group-relative block conversions.

## Core structure

`struct xfs_group` contains:
- mount pointer, group number, and group type;
- passive and active reference counters;
- precomputed usable group block limits;
- kernel-only busy extent or zone-reset tracking;
- checked/sick health bitsets protected by `xg_state_lock`;
- deferred intent drain state;
- rmap update hooks for online repair.

This structure is embedded by more specific per-AG or realtime group wrappers.

## Public API

The header declares the reference and lifetime functions implemented by `xfs_group.c`:
- passive: `xfs_group_get`, `xfs_group_get_by_fsb`, `xfs_group_hold`, `xfs_group_put`;
- active: `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, `xfs_group_rele`;
- lifecycle: `xfs_group_insert`, `xfs_group_free`.

It also defines xarray mark helpers for setting, clearing, and testing group marks.

## Geometry helpers

Inline helpers convert between group-relative and filesystem-relative coordinates:
- `xfs_group_max_blocks`
- `xfs_groups_to_rfsbs`
- `xfs_group_start_fsb`
- `xfs_gbno_to_fsb`
- `xfs_gbno_to_daddr`
- `xfs_fsb_to_gno`
- `xfs_fsb_to_gbno`

`xfs_gbno_to_daddr` accounts for group types that have disk-address gaps, such as newer realtime configurations.

## Validation helpers

`xfs_verify_gbno` validates one group block number against the usable minimum and maximum. `xfs_verify_gbext` validates a nonzero extent, checks overflow, and verifies both endpoints.

## Important invariants

- Group geometry comes from `mp->m_groups[type]`; helpers are type-sensitive.
- `xg_min_gbno` and `xg_block_count` define the valid usable range, not merely the nominal group size.
- Kernel-only fields must not be assumed available in userspace libxfs builds.
- Group health bitsets require `xg_state_lock` for direct access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_group.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_health.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_health.h

## Role in the repository

`xfs_health.h` defines the internal XFS health-tracking interface. It names health bits for filesystem-wide metadata, realtime groups, allocation groups, and inodes; groups those bits into primary, secondary, indirect, and all masks; and declares the mark, clear, measure, geometry export, and health monitor mapping functions.

## Health model

Each health domain tracks two bitsets:
- `checked`, meaning the metadata item has been examined;
- `sick`, meaning the metadata item needs repair or had problems observed.

This supports four states: checked and sick, checked and healthy, unchecked but sick from runtime evidence, and unchecked with no observed issue.

The comments classify evidence as:
- primary evidence, directly indicating a problem in that metadata group;
- secondary evidence, side effects related to primary problems;
- indirect evidence, where another group is implicated but only indirect state remains.

## Health domains

Filesystem-wide sickness bits cover summary counters, quotas, quota counts, link counts, metadata directory tree, and metadata path health.

Realtime group bits cover group superblock, bitmap, summary, realtime rmap btree, and realtime refcount btree.

Allocation group bits cover AG superblock, AGF, AGFL, AGI, bnobt, cntbt, inobt, finobt, rmapbt, refcountbt, and bad inodes observed during inactivation.

Inode bits cover inode core, data/attr/CoW bmap btrees, directory, xattrs, symlink remote targets, parent pointers, zapped data/attr/dir/symlink state, inactivation propagation suppression, and directory tree structure.

## Public interface

The header declares functions to mark filesystem, group, and inode metadata sick, corrupt, or healthy, and to measure sickness:
- `xfs_fs_mark_*`
- `xfs_group_mark_*`
- `xfs_inode_mark_*`

It also declares targeted helpers such as `xfs_bmap_mark_sick`, `xfs_btree_mark_sick`, `xfs_dirattr_mark_sick`, and `xfs_da_mark_sick`.

Geometry and userspace export helpers include `xfs_fsop_geom_health`, `xfs_ag_geom_health`, `xfs_rtgroup_geom_health`, and `xfs_bulkstat_health`. Health monitor mask translation functions convert internal masks to exported event masks.

## Inline helpers

The header provides convenience predicates for testing health:
- `xfs_fs_has_sickness`
- `xfs_group_has_sickness`
- `xfs_ag_has_sickness`
- `xfs_rtgroup_has_sickness`
- `xfs_inode_has_sickness`
- `xfs_fs_is_healthy`
- `xfs_inode_is_healthy`

`xfs_metadata_is_sick` classifies `-EFSCORRUPTED` and `-EFSBADCRC` as metadata health errors.

## Important invariants

- Runtime corruption reports set sick bits without necessarily setting checked bits.
- Scrub/fsck-style confirmed corruption sets both sick and checked.
- Successful repair clears sick and sets checked.
- Some inode zapped bits are separate from primary sickness and must be preserved in `XFS_SICK_INO_ALL`.
- `XFS_SICK_INO_FORGET` is secondary state used to avoid AG health propagation during inactivation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_health.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.c

## Role in the repository

`xfs_ialloc.c` implements XFS inode allocation, inode freeing, inode record conversion and validation, inode chunk initialization, inode-to-buffer mapping, AGI logging and verification, inode count queries, inode allocation geometry setup, root inode prediction, and shrink safety checks.

It coordinates the AGI header, INOBT, optional FINOBT, free-space allocator, rmap ownership, superblock inode counters, per-AG cached counters, transactions, and health reporting.

## INOBT record access and validation

`xfs_inobt_lookup`, `xfs_inobt_update`, `xfs_inobt_btrec_to_irec`, `xfs_inobt_rec_freecount`, `xfs_inobt_check_irec`, `xfs_inobt_get_rec`, and `xfs_inobt_insert_rec` provide the core record access layer.

The code converts between on-disk full and sparse inode record formats. On filesystems without sparse inodes, records are treated as full chunks with a synthetic full count and zero holemask. On sparse filesystems, holemask and count fields are taken from disk.

Record validation checks AG inode range validity, count bounds, freecount bounds, and consistency between the free bitmap and freecount. Corrupt records mark the relevant btree sick and return `-EFSCORRUPTED`.

## Inode chunk initialization

`xfs_ialloc_inode_init` formats newly allocated inode clusters. For v3 inodes it writes inode numbers, metadata UUIDs, CRCs, and logs the initialization as an inode-create intent so recovery can replay logical initialization while inode buffers are tracked as ordered buffers. For v2 inodes it logs inode core ranges directly.

Without a transaction, such as during recovery-style paths, initialized inode buffers are queued for delayed write instead of being transaction-logged.

## Sparse inode record handling

Sparse inode helpers align sparse allocations to full chunk boundaries and merge records over time:
- `xfs_align_sparse_ino` aligns start inode and allocation mask.
- `__xfs_inobt_can_merge` validates compatible sparse records.
- `__xfs_inobt_rec_merge` merges holemask, count, freecount, and free mask.
- `xfs_inobt_insert_sprec` inserts or merges sparse records into INOBT.
- `xfs_finobt_insert_sprec` inserts or replaces the matching FINOBT record.

A failed sparse merge is treated as serious corruption because mount-time geometry should prevent overlapping incompatible sparse records.

## Allocating inode chunks

`xfs_ialloc_ag_alloc` allocates a new inode chunk in an AG when no free inodes are available. It first tries to extend from `agi_newino`, then tries aligned near-root allocation, then falls back to sparse allocation if supported and necessary.

After block allocation it initializes inode buffers, inserts INOBT and optional FINOBT records, updates AGI inode/free counts, updates per-AG counters, logs AGI fields, and adjusts superblock inode counters.

The allocator accounts for maximum inode count limits, stripe alignment, cluster alignment, sparse inode alignment, AG boundaries, and btree split reservation space.

## Allocating individual inodes

`xfs_dialloc` is the top-level disk inode allocator. It chooses a starting AG based on parent inode, directory rotor, and metadata-directory placement. It scans AGs, first with trylock behavior and, near low space, preferring existing free inodes before allocating new chunks.

`xfs_dialloc_try_ag` reads and locks the AGI, allocates a new inode chunk if needed, rolls the transaction while holding the AGI buffer, and allocates one inode from the selected AG.

`xfs_dialloc_ag` uses FINOBT when available, otherwise falls back to `xfs_dialloc_ag_inobt`. The FINOBT path finds a chunk near the parent or near `agi_newino`, removes or updates the FINOBT record, verifies and mirrors the change into INOBT, updates AGI/per-AG/superblock free counts, and checks counts. The INOBT-only path searches near the parent within a bounded distance, then falls back to the last allocated chunk and finally a full AG scan.

If an AG has sick inode state, candidate inodes are mapped and read before allocation to avoid reusing corrupt inode buffers.

## Freeing inodes

`xfs_difree` validates that the inode belongs to the supplied per-AG, reads the AGI, updates INOBT via `xfs_difree_inobt`, and updates FINOBT via `xfs_difree_finobt` when present.

`xfs_difree_inobt` marks the inode bit free. If the whole chunk becomes free and the block size does not contain multiple chunks, it deletes the INOBT record, updates inode/free counts, records chunk deletion details in `struct xfs_icluster`, and schedules the inode chunk blocks for freeing. Sparse chunks are freed extent-by-extent according to allocated holemask ranges.

`xfs_difree_finobt` independently updates or inserts the FINOBT record, checks consistency with the updated INOBT record, and deletes the FINOBT record when a fully free chunk is removed.

## Inode mapping

`xfs_imap` maps an inode number to disk address, buffer length, and byte offset. Trusted inode numbers can often be mapped arithmetically from inode geometry. Untrusted inode numbers, unaligned chunk layouts, and sparse layouts require `xfs_imap_lookup`, which consults INOBT and verifies that the record exists and that the inode is allocated when requested.

The final mapping is checked against filesystem block bounds before returning.

## AGI logging and verification

`xfs_ialloc_log_agi` logs AGI fields in two logical regions to avoid unnecessarily logging the large unlinked inode hash table when fields on both sides are modified.

`xfs_agi_verify`, read/write verifiers, and `xfs_agi_buf_ops` validate AGI magic, version, UUID, LSN, AG length, INOBT/FINOBT levels, and unlinked inode bucket values. Read failures from corruption or bad CRC mark AGI health sick.

`xfs_read_agi` reads an AGI buffer with verifier ops, sets buffer type and reference, and marks AGI sick on metadata errors. `xfs_ialloc_read_agi` initializes per-AG cached inode counters and optionally returns the locked buffer.

## Counting and geometry helpers

`xfs_ialloc_has_inodes_at_extent` classifies a block extent as empty, full, or sparse with respect to physically allocated inode records. `xfs_ialloc_count_inodes` walks all INOBT records to count total and free inodes.

`xfs_ialloc_setup_geometry` initializes inode geometry: new inode flags2, AG inode bit widths, INOBT fanout/minimums, inode chunk size, sparse minimum allocation size, max btree levels, maximum inode count, cluster buffer sizing, cluster alignment, stripe alignment, and minimum folio order.

`xfs_ialloc_calc_rootino` predicts the root inode location laid out by mkfs by accounting for AG headers, btree roots, AGFL, optional FINOBT/RMAPBT/refcount roots, internal log placement, and inode alignment.

`xfs_ialloc_check_shrink` prevents shrink operations from creating sparse inode records that extend beyond the new end of AG.

## Important invariants

- INOBT and FINOBT records must agree wherever both contain a chunk; FINOBT omits fully allocated chunks.
- AGI counts, per-AG counters, and superblock counters must be updated in the same transaction protocol as btree changes.
- Sparse inode records are aligned to full inode chunk ranges even if only part of the chunk is physically allocated.
- Freecount must match the actual free bits after masking out sparse holes.
- AGI logging must avoid overlogging the unlinked bucket table.
- Untrusted inode numbers require INOBT validation, not just arithmetic mapping.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.h

## Role in the repository

`xfs_ialloc.h` declares the public libxfs interface for inode allocation, inode freeing, inode mapping, AGI reading/logging, INOBT record lookup/access, inode chunk initialization, inode count queries, inode geometry setup, and shrink checks.

## Main definitions

`XFS_INODE_BIG_CLUSTER_SIZE` sets the preferred large inode cluster size to 8192 bytes.

`struct xfs_icluster` reports inode chunk deletion state to callers of `xfs_difree`. It records whether a chunk was deleted, the first inode number, and the physical allocation bitmap for sparse chunks.

`xfs_make_iptr` computes an on-disk dinode pointer within an inode buffer from a buffer pointer and inode index.

## Allocation and freeing API

`xfs_dialloc` allocates one on-disk inode and may roll the caller’s transaction. `xfs_difree` frees one on-disk inode and reports whether its containing inode chunk was removed.

`xfs_ialloc_inode_init` initializes newly allocated inode buffers for a chunk or sparse chunk.

## Mapping and AGI API

`xfs_imap` maps an inode to an `xfs_imap` location suitable for reading the inode buffer.

`xfs_ialloc_log_agi`, `xfs_read_agi`, and `xfs_ialloc_read_agi` expose AGI logging and verified AGI reads. `XFS_IALLOC_FLAG_TRYLOCK` requests trylock behavior for AGI buffer locking.

## INOBT helpers

The header declares:
- `xfs_inobt_lookup`
- `xfs_inobt_get_rec`
- `xfs_inobt_rec_freecount`
- `xfs_inobt_btrec_to_irec`
- `xfs_inobt_check_irec`
- `xfs_inobt_insert_rec`

It also exposes extent packing classification, inode counting, inode allocation geometry setup, root inode calculation, and shrink validation helpers.

## Important invariants

- Callers of `xfs_dialloc` must pass a transaction pointer by address because allocation can roll the transaction.
- `xfs_difree` requires the caller to supply the correct per-AG for the inode.
- `xfs_icluster.alloc` is a physical allocation bitmap for sparse chunks, not the logical free-inode mask.
- AGI reads use verifier-backed buffers and update per-AG cached state on first initialization.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.c

## Role in the repository

`xfs_ialloc_btree.c` implements the concrete generic-btree operations for the XFS inode allocation btree and free inode btree. It supplies cursor construction, root updates, block allocation/freeing, key and record initialization, ordering checks, verifiers, fanout calculations, staged btree commits, sparse allocation mask conversion, FINOBT reservation calculations, and cursor cache lifecycle.

## Cursor and root operations

`xfs_inobt_init_cursor` and `xfs_finobt_init_cursor` allocate generic btree cursors with INOBT or FINOBT ops, hold the per-AG group, attach the AGI buffer, and initialize cursor height from `agi_level` or `agi_free_level`.

Root callbacks update:
- `agi_root` and `agi_level` for INOBT;
- `agi_free_root` and `agi_free_level` for FINOBT.

Both root updates log the corresponding AGI fields.

## Block allocation, freeing, and counters

INOBT block allocation uses normal AG reservation, while FINOBT allocation uses metadata reservation unless the mount has `m_finobt_nores` set. New btree blocks are allocated near the requested start block and recorded as INOBT-owned rmap extents.

Freeing schedules one btree block for deferred freeing with the same owner and reservation policy.

`xfs_inobt_mod_blockcount` updates `agi_iblocks` or `agi_fblocks` when the INOBT block count feature is enabled, logging `XFS_AGI_IBLOCKS` because the AGI bit covers both counters.

## Btree operation callbacks

The INOBT and FINOBT ops share record/key logic:
- min/max records come from inode geometry fanout arrays;
- keys are initialized from `ir_startino`;
- high keys cover `ir_startino + XFS_INODES_PER_CHUNK - 1`;
- records are initialized from the cursor’s incore inode record, using sparse fields only when the filesystem supports sparse inodes;
- pointer initialization reads either `agi_root` or `agi_free_root`;
- key comparisons order by start inode;
- record ordering requires non-overlapping inode chunks.

The two operation tables differ primarily in name, stats offset, sick mask, root field, pointer root, buffer ops, and reservation behavior.

## Verification

`xfs_inobt_verify` checks magic, optional v5 AG btree header fields, level bounds against inode geometry, and generic AG btree block record counts. Read verification also checks CRC for CRC-enabled metadata and traces corrupt btree buffers on error. Write verification validates structure and recalculates AG btree CRCs.

`xfs_inobt_buf_ops` accepts INOBT magic values; `xfs_finobt_buf_ops` accepts FINOBT magic values. Both share verifier functions because their layout and rules are the same.

## Staged btree commit

`xfs_inobt_commit_staged_btree` installs a staged rebuilt INOBT or FINOBT root into the AGI. It copies fake-root block, level, and optional block count fields into AGI, logs the affected fields, and commits the staged root to the generic btree layer. This is used by rebuild/repair code.

## Geometry and sizing

`xfs_inobt_maxrecs` computes leaf or internal node fanout after subtracting the correct short-form btree header size. `xfs_iallocbt_maxlevels_ondisk` computes the maximum possible on-disk height across INOBT and FINOBT using minimum block sizes and worst-case inode record count.

`xfs_iallocbt_calc_size` wraps generic btree sizing for a given record count.

## Sparse inode helpers

`xfs_inobt_irec_to_allocmask` expands the sparse record holemask into a 64-bit physical inode allocation bitmap. Holemask zero bits mean physical inode regions exist, so the helper inverts the 16-bit holemask and expands each set holemask bit into multiple inode bits.

`xfs_inobt_rec_check_count`, enabled for debug or warning builds, verifies that the expanded allocation bitmap contains the same number of physically allocated inodes as `ir_count`.

## FINOBT reservation accounting

`xfs_finobt_calc_reserves` computes how many blocks to reserve for FINOBT growth and how many are currently used. If INOBT block counts are available it reads `agi_fblocks`; otherwise it counts blocks by traversing the FINOBT. The requested reservation is based on a maximum possible btree size for the AG.

## Cursor cache lifecycle

`xfs_inobt_init_cur_cache` creates the slab cache sized for the maximum INOBT cursor height. `xfs_inobt_destroy_cur_cache` destroys it during teardown.

## Important invariants

- INOBT and FINOBT are short-pointer AG btrees.
- FINOBT has the same record format as INOBT but tracks only records with free inodes.
- Btree block counters are updated only when the inobtcounts feature is enabled.
- Sparse record count and holemask consistency is checked independently of logical freecount.
- Growfs and log recovery can limit verifier assumptions about fully initialized per-AG state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.h

## Role in the repository

`xfs_ialloc_btree.h` declares the INOBT/FINOBT btree format helpers and public btree support API. It bridges on-disk inode allocation record layout from `xfs_format.h` with the generic btree engine.

## Layout macros

`XFS_INOBT_BLOCK_LEN` selects the correct short-form btree header length based on whether the filesystem has CRC metadata.

Address macros compute one-based record, key, and pointer locations inside an INOBT/FINOBT block:
- `XFS_INOBT_REC_ADDR`
- `XFS_INOBT_KEY_ADDR`
- `XFS_INOBT_PTR_ADDR`

The comments note that some macros are used by userspace even if they appear unused in kernel-only analysis.

## Public API

The header declares:
- cursor constructors for INOBT and FINOBT;
- fanout calculation via `xfs_inobt_maxrecs`;
- sparse record holemask-to-allocation-mask conversion;
- optional debug count validation;
- FINOBT reservation calculation;
- INOBT/FINOBT btree size calculation;
- staged btree commit;
- maximum on-disk height calculation;
- cursor cache init/destroy.

## Important invariants

- INOBT and FINOBT use the same record, key, and pointer block layout.
- Header length depends on CRC support and must be subtracted before fanout calculations.
- Address macros assume one-based btree indexes, matching the generic XFS btree engine.
- Staged btree commit is the repair/rebuild path for replacing AGI roots.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_ialloc_btree.h -->