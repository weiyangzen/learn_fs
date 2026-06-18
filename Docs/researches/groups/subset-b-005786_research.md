# subset-b-005786 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.c

Purpose: Implements the incore realtime group manager for XFS, including rtgroup geometry, lifecycle in the generic group radix tree, metadata inode locking/loading/creation, realtime superblock verification, and realtime superblock logging.

Important APIs, types, and functions: Exports `xfs_rtgroup_alloc`, `xfs_rtgroup_free`, `xfs_initialize_rtgroups`, `xfs_free_rtgroups`, `xfs_rtgroup_extents`, `xfs_rtgroup_calc_geometry`, `xfs_update_last_rtgroup_size`, `xfs_rtgroup_lock`, `xfs_rtgroup_unlock`, `xfs_rtgroup_trans_join`, `xfs_rtgroup_get_geometry`, rt metadata inode helpers `xfs_rtginode_*`, `xfs_update_rtsb`, `xfs_log_rtsb`, and verifier ops `xfs_rtsb_buf_ops`. Internal `xfs_rtginode_ops` maps bitmap, summary, rmap, and refcount metafiles to feature predicates, sickness bits, fork format masks, and create callbacks.

Control flow: Mount/grow code allocates `struct xfs_rtgroup`, precomputes extents, block count, and minimum usable group block, and inserts it as `XG_TYPE_RTG`. Metadata operations lock bitmap/summary inodes for non-zoned filesystems and optional rmap/refcount btree inodes for feature-enabled groups, then join those inodes to transactions so commit releases locks. Metadata inode loading uses legacy superblock inode numbers without rtgroups, or metadir paths like `<rgno>.<type>` with rtgroups. Creation starts a metadir update, creates a regular metafile, sets `i_projid` to the rtgroup number, invokes the feature-specific create hook, commits, and installs the inode pointer.

State and persistence: Incore state lives in `struct xfs_rtgroup` and referenced metadata inodes. Persistent state is the metadir hierarchy, legacy bitmap/summary inode pointers, realtime rmap/refcount btree roots, and optional realtime superblock. `xfs_update_rtsb` copies label and UUID data from the primary superblock, deriving `meta_uuid` when the feature is absent; `xfs_log_rtsb` orders the rt superblock buffer in the transaction.

Dependencies and integration points: Depends on generic group management, metadir/metafile helpers, realtime bitmap/summary creation, realtime rmap/refcount btree creation, buffer verifiers, health reporting, inode locking, transaction inode joins, and zoned feature predicates.

Risks and test signals: Key risks are wrong tail-group extent recomputation after growfs recovery, rt metadata inode path/type mismatches, stale `i_projid` validation, lock ordering across deferred rt operations, and failing to update/log the realtime superblock during primary superblock changes. Test mount and growfs with rtgroups, legacy realtime without rtgroups, zoned vs non-zoned locking, missing metadir, corrupted rt inode fork formats, rtsb CRC/UUID mismatches, and deferred operations touching multiple rtgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.h

Purpose: Defines the incore realtime group abstraction, realtime group metadata inode slots, lock flags, reference helpers, block/address conversion helpers, and public prototypes for rtgroup and realtime superblock operations.

Important APIs, types, and functions: Defines `enum xfs_rtg_inodes`, `struct xfs_rtgroup`, `XFS_RTG_FREE`, `XFS_RTGLOCK_*`, `to_rtg`, `rtg_group`, `rtg_mount`, `rtg_rgno`, `rtg_blocks`, `rtg_bitmap`, `rtg_summary`, `rtg_rmap`, `rtg_refcount`, passive/active ref helpers, rtgroup iterators, `xfs_verify_rgbno`, `xfs_verify_rgbext`, `xfs_rgbno_to_rtb`, `xfs_rtb_to_rgno`, `xfs_rtb_to_rgbno`, `xfs_rtb_to_daddr`, `xfs_daddr_to_rtb`, `xfs_rtginode_path`, `xfs_rtgs_to_rfsbs`, and `xfs_rtgroup_raw_size`.

Control flow: Callers use passive refs for cached access and active refs for objects that must remain live. Conversion helpers route through generic `xfs_group` math, but `xfs_rtb_to_daddr` and `xfs_daddr_to_rtb` handle the rtgroups case without device-address gaps by remapping sparse group block numbers to packed device offsets. `CONFIG_XFS_RT` gates real implementations; non-RT builds compile to no-op or unsupported stubs.

State and persistence: The structure stores metadata inode pointers, realtime extent count, a union for either bitmap summary cache or zoned open-zone state, and zoned GC reference count. It describes incore state only, but its conversion helpers encode assumptions about persisted realtime geometry in the superblock.

Dependencies and integration points: Included by realtime allocation, bitmap, rmap/refcount, scrub, growfs, mount, and zoned code. It depends on `xfs_group.h` for generic group lifetime and geometry primitives and on superblock-derived `m_groups[XG_TYPE_RTG]` geometry.

Risks and test signals: Risks include off-by-one iteration in `xfs_rtgroup_next`, incorrect raw size when `ZONE_GAPS` is active, packed vs gapped device address conversion errors, and using RGB verifiers on non-rtgroup filesystems. Test conversion round trips, first-group rtsb exclusion, non-power-of-two realtime extent sizes, gapped zoned layouts, `CONFIG_XFS_RT=n`, and lock flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.c

Purpose: Adapts the generic XFS btree engine to realtime refcount btrees rooted in realtime metadata inodes, providing cursor operations, verifiers, record/key conversion, root resizing, reserve sizing, and inode fork format/flush support.

Important APIs, types, and functions: Defines `xfs_rtrefcountbt_ops`, `xfs_rtrefcountbt_buf_ops`, `xfs_rtrefcountbt_init_cursor`, `xfs_rtrefcountbt_commit_staged_btree`, `xfs_rtrefcountbt_maxrecs`, `xfs_rtrefcountbt_maxlevels_ondisk`, cursor cache init/destroy, `xfs_rtrefcountbt_compute_maxlevels`, `xfs_rtrefcountbt_calc_size`, `xfs_rtrefcountbt_calc_reserves`, `xfs_iformat_rtrefcount`, `xfs_rtrefcountbt_to_disk`, `xfs_iflush_rtrefcount`, and `xfs_rtrefcountbt_create`.

Control flow: Cursor creation requires the rt refcount inode to be locked, allocates a cursor from the kmem cache, binds it to the inode data fork and rtgroup, and derives height from the inode root. Btree ops encode refcount record starts with the shared/COW domain, compare ordered startblock keys, verify CRC v5 blocks, and resize the inode-root buffer while moving pointer arrays when internal roots grow or shrink. Inode read converts the compact on-disk root into a generic incore btree block; flush reverses that transformation. Staged btree commit replaces the real fork with a fake-root fork and logs core/root changes.

State and persistence: Persistent state is the rt refcount metafile inode with `XFS_DINODE_FMT_META_BTREE`, an on-disk `xfs_rtrefcount_root`, and child btree blocks with `XFS_RTREFC_CRC_MAGIC`. Incore state includes the fork btree root, cursor cache, mount max/min record geometry, and held rtgroup reference.

Dependencies and integration points: Integrates with refcount update code, realtime group inode management, generic btree staging, metadata block allocation/freeing, xfs health sickness masks, transaction logging, and mount-time geometry calculation.

Risks and test signals: Risks include root size calculation mismatches between disk and incore formats, accepting reflink-disabled metadata, pointer-array movement during resize, maxlevel underestimation, and corrupt domain-encoded startblocks. Test metadir growfs creation before rt volume attach, reflink and rtreflink feature combinations, root split/join, staged repair commit, CRC/magic/level corruption, and maximal rtgroup extent counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.h

Purpose: Declares the realtime refcount btree interface and provides layout helpers for incore and on-disk realtime refcount roots.

Important APIs, types, and functions: Defines `XFS_RTREFCOUNT_BLOCK_LEN`; declares cursor, staging, max-record, max-level, reserve, format, flush, conversion, and create functions. Inline helpers compute record/key/pointer addresses in incore `xfs_btree_block` roots and on-disk `xfs_rtrefcount_root` blocks, plus `xfs_rtrefcount_broot_space_calc`, `xfs_rtrefcount_broot_space`, `xfs_rtrefcount_droot_space_calc`, and `xfs_rtrefcount_droot_space`.

Control flow: Btree code and inode format/flush paths use these helpers to locate variable-length root contents. Leaf roots store `xfs_refcount_rec` records; internal roots store keys followed by long pointers. Disk-root helpers start after the compact `xfs_rtrefcount_root`, while incore helpers reserve the full CRC btree block header area.

State and persistence: The header defines no state itself, but its layout math is the contract between on-disk inode fork bytes and incore btree root buffers. Persistent correctness depends on exact sizes and endian-aware callers.

Dependencies and integration points: Used by realtime refcount btree implementation, inode fork formatting, userspace libxfs consumers, repair/staging code, and generic btree code.

Risks and test signals: Risks are ABI/layout drift, off-by-one one-based index handling, using a leaf layout for internal roots, and inconsistent incore-vs-disk root sizing. Test root address helpers with zero, one, and many records; max dinode fork sizes; internal roots with pointer movement; and userspace repair builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrefcount_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.c

Purpose: Implements the realtime reverse-mapping btree adapter for XFS, rooted in realtime metadata inodes and optionally available as an in-memory btree for repair/scrub workflows.

Important APIs, types, and functions: Defines `xfs_rtrmapbt_ops`, optional `xfs_rtrmapbt_mem_ops`, `xfs_rtrmapbt_buf_ops`, `xfs_rtrmapbt_init_cursor`, `xfs_rtrmapbt_mem_cursor`, `xfs_rtrmapbt_mem_init`, `xfs_rtrmapbt_commit_staged_btree`, `xfs_rtrmapbt_maxrecs`, `xfs_rtrmapbt_maxlevels_ondisk`, cursor cache init/destroy, `xfs_rtrmapbt_compute_maxlevels`, `xfs_rtrmapbt_calc_size`, `xfs_rtrmapbt_calc_reserves`, `xfs_iformat_rtrmap`, `xfs_rtrmapbt_to_disk`, `xfs_iflush_rtrmap`, `xfs_rtrmapbt_create`, `xfs_rtrmapbt_init_rtsb`, and `xfs_rtrmap_highest_rgbno`.

Control flow: Btree ops order records by physical rtgroup block, owner, and offset key flags while masking unwritten status for key comparisons. The overlapping btree stores low/high keys, uses metadata inode block allocation, verifies CRC/magic/feature/maxlevel constraints, and resizes inode roots by moving pointer arrays. Disk format load and flush convert between compact `xfs_rtrmap_root` and incore generic btree blocks. The rtsb initializer maps the first realtime extent to `XFS_RMAP_OWN_FS` in rtgroup zero, and `xfs_rtrmap_highest_rgbno` reads the root high key.

State and persistence: Persistent state is the rtrmap metafile inode, its on-disk root, and child blocks with `XFS_RTRMAP_CRC_MAGIC`. Incore state includes cursor cache, mount btree geometry, optional `xfbtree` memory tree, and rtgroup references.

Dependencies and integration points: Integrates with rmap update/deferred-item code, metadir rtgroup inode management, btree staging, scrub/repair in-memory btrees, realtime superblock ownership, health masks, and transaction logging.

Risks and test signals: Risks include incorrect offset flag masking, high-key generation for inode vs non-inode owners, maxlevel calculation under extreme reflink sharing, mem-btree verifier divergence, root conversion errors, and stale rtsb ownership maps. Test rmap insert/delete/update on realtime extents, unwritten extent transitions, non-inode owners, staged repair commit, in-memory scrub btrees, rtsb initialization, and corrupted magic/CRC/level blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.h

Purpose: Declares realtime rmap btree entry points and defines address/size helpers for overlapping realtime rmap root layouts.

Important APIs, types, and functions: Defines `XFS_RTRMAP_BLOCK_LEN`; declares cursor, staging, reserve, maxlevel, format/flush, create, rtsb initialization, in-memory btree, and highest-rgbno helpers. Inline helpers include `xfs_rtrmap_rec_addr`, `xfs_rtrmap_key_addr`, `xfs_rtrmap_high_key_addr`, `xfs_rtrmap_ptr_addr`, on-disk root address helpers, and root space calculators for incore and disk formats.

Control flow: Realtime rmap roots are leaf roots with records or internal roots with paired low/high keys and long pointers. One-based index helpers compute offsets into compact root storage and generic incore blocks. Callers use these helpers during cursor operations, inode fork conversion, and userspace repair validation.

State and persistence: The header encodes persistent root layout assumptions for `struct xfs_rtrmap_root`. Because rmap btrees are overlapping, internal roots must allocate twice as many key bytes per record slot as ordinary btrees.

Dependencies and integration points: Used by `xfs_rtrmap_btree.c`, generic btree code, inode format/flush, repair staging, and rtgroup/rtsb setup.

Risks and test signals: Risks are low/high key layout mistakes, pointer offset drift after root resize, incorrect userspace assumptions, and root space calculations that exceed dinode fork size. Test leaf/internal root helpers, staged root replacement, maximum records for several block sizes, and in-memory btree builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_rtrmap_btree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.c

Purpose: Provides shared superblock validation, feature decoding, disk/incore conversion, verifier ops, mount geometry initialization, superblock logging/sync, secondary superblock update/read helpers, filesystem geometry export, and stripe/realtime geometry checks.

Important APIs, types, and functions: Exports `xfs_sb_good_version`, `xfs_sb_version_to_features`, `xfs_validate_rt_geometry`, `xfs_compute_rgblklog`, `xfs_sb_quota_from_disk`, `xfs_sb_from_disk`, `xfs_sb_to_disk`, `xfs_sb_buf_ops`, `xfs_sb_quiet_buf_ops`, `xfs_sb_mount_rextsize`, `xfs_mount_sb_set_rextsize`, `xfs_sb_mount_common`, `xfs_log_sb`, `xfs_sync_sb`, `xfs_update_secondary_sbs`, `xfs_sync_sb_buf`, `xfs_fs_geometry`, `xfs_sb_read_secondary`, `xfs_sb_get_secondary`, `xfs_validate_stripe_geometry`, and `xfs_compute_rextslog`.

Control flow: Read verification optionally checks CRC, converts the disk superblock without quota normalization, validates common geometry and feature masks, then enforces read-only/incompat feature policy. Write verification reconverts from disk, repeats common checks, validates summary counters and log LSN, stamps the buffer LSN, and updates CRC. Mount initialization caches block/sector/AG/RTG/btree geometry into `struct xfs_mount`. Logging recomputes lazy counters, writes incore state to the primary superblock buffer, and logs the full disk superblock.

State and persistence: Persistent state is the primary/secondary `xfs_dsb`, including v4/v5 feature masks, quota inode fields, metadir/rtgroup fields, zoned fields, summary counters, UUIDs, and CRC/LSN. Incore state normalizes old quota fields, derives `sb_meta_uuid`, zeros legacy rt bitmap inode numbers for metadir filesystems, and initializes rtgroup geometry and btree max records.

Dependencies and integration points: Central to mount, log recovery, growfs, quota, rtgroups, zoned realtime, metadir, xfsrepair-compatible secondary superblocks, transaction logging, buffer cache verification, and userspace geometry ioctls.

Risks and test signals: Risks include accepting unsupported feature combinations, writing bad summary counters, v4/v5 quota conversion regressions, metadir rtgroup geometry mismatches, zoned alignment mistakes, stale secondary superblocks, and CRC/LSN validation ordering. Test v4 and v5 mounts, unknown compat/ro-compat/incompat bits, metadir+rtgroups+zoned combinations, external/internal log mismatch, stripe mount-option repair, growfs secondary updates, quota inode normalization, and geometry ioctl versions 1-5.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.h

Purpose: Declares the superblock manipulation API shared by kernel and libxfs userspace code.

Important APIs, types, and functions: Declares logging/sync helpers `xfs_log_sb`, `xfs_sync_sb`, `xfs_sync_sb_buf`; mount geometry helpers `xfs_sb_mount_common`, `xfs_sb_mount_rextsize`, `xfs_mount_sb_set_rextsize`; disk conversion helpers `xfs_sb_from_disk`, `xfs_sb_to_disk`, `xfs_sb_quota_from_disk`; feature helpers `xfs_sb_good_version`, `xfs_sb_version_to_features`; secondary superblock helpers; geometry export via `xfs_fs_geometry`; validation helpers `xfs_validate_stripe_geometry`, `xfs_validate_rt_geometry`; and realtime log calculators `xfs_compute_rextslog`, `xfs_compute_rgblklog`.

Control flow: Consumers include mount, growfs, repair, log recovery, sync, and ioctl paths. `XFS_FS_GEOM_MAX_STRUCT_VER` caps geometry ABI versioning for `xfs_fs_geometry`.

State and persistence: The header itself has no state, but every function operates on persistent superblock fields or mount caches derived from them.

Dependencies and integration points: Depends on forward declarations for mount, superblock, disk superblock, transaction, geometry, and per-AG types; it is included broadly across XFS metadata code.

Risks and test signals: Risks are ABI drift in exported prototypes and mismatched userspace/kernel expectations. Test libxfs builds, all geometry ioctl versions, mount/growfs callers, and feature combinations that exercise both validation helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_shared.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_shared.h

Purpose: Collects XFS definitions shared between kernel and userspace libxfs that do not fit in more specific shared headers, especially verifier/btree op exports, transaction flags, superblock modification flags, buffer reference priorities, and inode geometry.

Important APIs, types, and functions: Declares many `xfs_buf_ops` verifier objects, btree op objects, btree type predicates such as `xfs_btree_is_rtrmap` and `xfs_btree_is_rtrefcount`, log reservation helpers, transaction flags `XFS_TRANS_*`, superblock modification masks `XFS_TRANS_SB_*`, buffer reference constants, and `struct xfs_ino_geometry`.

Control flow: Metadata modules publish verifier and btree operation tables here so generic btree, buffer, scrub, repair, and trace code can compare operation identities and route behavior. Transaction flags communicate logging, sync, reserve-pool, lowspace, writecount, freed-block, intent-done, and rtbitmap lock state through the transaction subsystem.

State and persistence: No runtime state is allocated here. The constants affect buffer cache retention, transaction semantics, and superblock field logging. `struct xfs_ino_geometry` is a mount-time cache of inode allocation and validation geometry derived from the superblock and feature bits.

Dependencies and integration points: Included throughout libxfs, kernel XFS, and userspace tools. It connects buffer verifiers, btree implementations, transaction accounting, and inode allocation geometry.

Risks and test signals: Risks are shared ABI/semantic drift, stale btree identity predicates when new ops are added, transaction flag bit collisions, and buffer reference changes that alter cache pressure. Test kernel and userspace builds, metadata verifier dispatch, trace string mappings, transaction flag propagation, and inode allocation on sparse/finobt configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_shared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.c

Purpose: Implements encoding, verification, reading, writing, conversion, and truncation for remote XFS symlink targets stored outside the inode data fork.

Important APIs, types, and functions: Exports `xfs_symlink_blocks`, `xfs_symlink_hdr_set`, `xfs_symlink_hdr_ok`, `xfs_symlink_buf_ops`, `xfs_symlink_local_to_remote`, `xfs_symlink_shortform_verify`, `xfs_symlink_remote_read`, `xfs_symlink_write_target`, and `xfs_symlink_remote_truncate`.

Control flow: `xfs_symlink_write_target` stores short targets inline when they fit in the inode data fork; otherwise it allocates metadata extents, writes one buffer per mapping, stamps CRC headers when enabled, copies target chunks, logs buffers, and updates inode size/core. Read maps symlink extents, reads each buffer with verifier ops, checks header offset/length/owner, copies payload chunks, and NUL-terminates the caller buffer. Truncate reads current mappings, invalidates their buffers in the transaction, then unmaps all remote blocks.

State and persistence: Persistent remote symlink buffers optionally start with `xfs_dsymlink_hdr` containing magic, offset, bytes, UUID, owner inode, block address, LSN, and CRC. Non-CRC filesystems store raw target bytes. Inline symlink state lives in the inode local fork.

Dependencies and integration points: Depends on bmap read/write/unmap, buffer verifiers, inode health marking, transaction buffer logging/binval, log LSN checks, and inode fork initialization.

Risks and test signals: Risks include header/payload length mismatches, stale owner or block address, missing NUL termination for shortform data, multi-extent chunk ordering bugs, and partial truncate corruption. Test CRC and non-CRC filesystems, inline-to-remote conversion, max-length targets, sparse/corrupt symlink mappings, bad header owner/offset/length, and create/unlink recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.h

Purpose: Declares the remote symlink helper API for XFS inode, bmap, and symlink creation/removal code.

Important APIs, types, and functions: Declares block calculation, header set/check, local-to-remote conversion callback, shortform verification, remote read, symlink target write, and remote truncation functions.

Control flow: Creation paths call the sizing and write helpers; fork conversion code uses `xfs_symlink_local_to_remote`; lookup/readlink uses `xfs_symlink_remote_read`; unlink/inactivation uses `xfs_symlink_remote_truncate`; inode verifiers use `xfs_symlink_shortform_verify`.

State and persistence: The header carries no state, but prototypes define the boundary for persistent remote symlink buffer headers and inline fork validation.

Dependencies and integration points: Integrates with inode fork management, bmap allocation, transactions, buffer cache, and symlink VFS operations.

Risks and test signals: Risks are prototype drift against callers and inconsistent use of owner/path length arguments. Test builds across kernel and userspace libxfs and exercise symlink create/read/remove paths for inline and remote targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_symlink_remote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_inode.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_inode.c

Purpose: Provides transaction helpers for joining, timestamping, logging, and rolling XFS inodes.

Important APIs, types, and functions: Exports `xfs_trans_ijoin`, `xfs_trans_ichgtime`, `xfs_trans_log_inode`, and `xfs_trans_roll_inode`.

Control flow: `xfs_trans_ijoin` requires an exclusive inode lock, initializes the inode log item if needed, records commit-time unlock flags, clears per-transaction dirty flags, and adds the item to the transaction. `xfs_trans_ichgtime` updates ctime and optionally mtime, atime, and creation time under the inode lock. `xfs_trans_log_inode` marks the transaction dirty, sets the log item dirty bit, bumps i_version on the first log in the transaction when configured, and ORs requested inode log flags. Rolling logs core changes, rolls the transaction, and rejoins the inode.

State and persistence: State is transient until commit: inode log item flags, dirty masks, lock-release flags, VFS timestamps, and i_version. Persistence occurs through transaction commit and inode log item precommit/flush paths.

Dependencies and integration points: Depends on inode log items, VFS timestamp/i_version helpers, transaction item lists, inode locking assertions, and stale inode guards.

Risks and test signals: Risks include joining unlocked/stale/already-associated inodes, missing i_version updates, dirty flag loss across rolls, and timestamp changes without core logging by callers. Test metadata operations that roll transactions, i_version-enabled mounts, concurrent inode modification assertions, fsync/recovery of timestamps, and stale inode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.c

Purpose: Computes XFS transaction log reservations and log operation counts for all major metadata operations, including data writes, truncates, namespace changes, attributes, quotas, growfs, realtime metadata, deferred intent completions, and atomic write ioend completion.

Important APIs, types, and functions: Exports `xfs_allocfree_block_count`, finish reservation helpers for EFI/RUI/CUI/BUI and realtime variants, minimum-log-size variants for write/truncate/quota allocation, `xfs_trans_resv_calc`, `xfs_calc_max_atomic_write_fsblocks`, `xfs_calc_atomic_write_log_geometry`, and `xfs_calc_atomic_write_reservation`. Internal helpers calculate buffer overhead, inode log size, inobt/finobt/inode chunk reservations, realtime allocation/refcount block counts, namespace parent-pointer overheads, and per-transaction reservation bodies.

Control flow: Reservation formulas combine fixed item overhead, log op headers, buffer log format overhead rounded to historical 128-byte units, inode log sizes, btree height-derived split budgets, quota overhead, and feature-dependent deferred intent costs. `xfs_trans_resv_calc` fills `struct xfs_trans_resv` in dependency order, computing attribute reservations before namespace reservations because parent pointers may invoke xattr updates. Atomic write helpers derive per-intent and finish-step overhead, then calculate supported block counts or required log reservation and minimum log blocks.

State and persistence: The file persists nothing directly. It populates `mp->m_resv`, which controls runtime transaction ticket sizing and minimum log sizing. Bad values can cause transaction reservation overrun, unnecessary log size rejection, or excessive reserved log space.

Dependencies and integration points: Depends on mount geometry, btree maxlevels, quota constants, realtime bitmap sizing, deferred log item space calculators, parent pointer attr formats, and log minimum size calculations. It is consumed by transaction allocation and mount-time log validation.

Risks and test signals: Risks include under-reserving when feature combinations stack, preserving old reflink minimum-log behavior incorrectly, missing realtime rmap/refcount costs, parent-pointer relog overhead mistakes, and arithmetic overflow in atomic write sizing. Test fstests covering reflink, rmapbt, rtreflink, rtgroups, parent pointers, quota allocation, growfs rt/data, min-log-size mount rejection, atomic writes with varied block counts, and injected transaction reservation overruns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.h

Purpose: Defines transaction reservation data structures, reservation slots, log count constants, and prototypes for reservation calculators.

Important APIs, types, and functions: Defines `struct xfs_trans_res`, `struct xfs_trans_resv`, `M_RES`, directory operation reservation macros, default and operation-specific log counts, old reflink log counts retained for minimum log calculations, finish reservation prototypes, minimum-log-size calculators, and atomic write reservation helpers.

Control flow: Mount code calls `xfs_trans_resv_calc` to populate `M_RES(mp)`. Transaction allocation paths select a specific reservation slot such as `tr_write`, `tr_itruncate`, `tr_rename`, `tr_attrsetm`, `tr_growrtalloc`, or `tr_atomic_ioend`. Deferred operation completion code uses the finish helper prototypes for dynamic counts.

State and persistence: Reservation structures are in-memory mount state only. Their values indirectly constrain persistent metadata operations by ensuring enough journal space for complete atomic transactions.

Dependencies and integration points: Included by most XFS code that allocates transactions. It depends on transaction space macros from `xfs_trans_space.h` via consumers and on mount geometry.

Risks and test signals: Risks are missing reservation slots for new operations, changing historical log counts, and mismatched runtime vs minimum-log reservations. Test compile coverage, mount-time log sizing, every transaction type, and feature-specific logcount adjustments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_resv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.c

Purpose: Computes filesystem block reservations for namespace operations, factoring directory edits, inode allocation, symlink target blocks, and optional parent pointer attributes.

Important APIs, types, and functions: Exports `xfs_parent_calc_space_res`, `xfs_create_space_res`, `xfs_mkdir_space_res`, `xfs_link_space_res`, `xfs_symlink_space_res`, `xfs_remove_space_res`, and `xfs_rename_space_res`.

Control flow: Each helper sums lower-level reservation macros from `xfs_trans_space.h`. Create and mkdir include inode allocation plus directory entry insertion. Link includes directory entry insertion. Symlink includes inode allocation, directory insertion, and remote symlink blocks. Remove includes directory removal. Rename includes removal plus target insertion and conditionally extra parent pointer work for whiteouts, target replacement, and source/destination parent updates.

State and persistence: No state is stored. Returned block counts reserve data-device metadata space so transactions can allocate directory, bmap, attr, and inode metadata blocks safely.

Dependencies and integration points: Used by high-level create/link/symlink/remove/rename transaction setup. Depends on directory/attribute reservation macros, bmap split costs, inode allocation geometry, and `xfs_has_parent`.

Risks and test signals: Risks include underestimating parent-pointer attr space, rename target/whiteout combinations, and mismatches with log reservations. Test create/mkdir/link/symlink/remove/rename with parent pointers on/off, long names, whiteouts, target replacement, ENOSPC injection, and directory btree split cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.h

Purpose: Defines block reservation macros for XFS metadata operations and declares the runtime namespace space reservation helpers.

Important APIs, types, and functions: Defines macros for contiguous bmap/rmap/rtrmap capacities, rmap/rtrmap add space, next extent additions, swap rmap space, directory/attribute tree entry and removal space, inode allocation/free space, add-attr-fork, attr remove/set, direct I/O, growfs, growfs realtime, quota allocation, and qino creation reservations. Declares parent/create/mkdir/link/symlink/remove/rename space helpers.

Control flow: Higher-level reservation functions combine these macros based on operation semantics and feature bits. Macros derive worst-case split and join space from mount btree geometry and directory geometry.

State and persistence: Header-only formulas store no state but depend on mount caches such as btree max/min records, inode allocation geometry, directory geometry, and feature flags.

Dependencies and integration points: Used by transaction reservation code, namespace operation setup, bmap, attr, quota, growfs, and realtime paths.

Risks and test signals: Risks include division-by-zero if geometry is uninitialized, stale formulas for new btree types, under-reserving rtrmap operations, and overflows for large requested extent counts. Test reservation calculations after mount geometry setup, realtime rmap feature paths, attr fork operations, growfs, quota allocation, and ENOSPC stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_trans_space.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.c

Purpose: Implements core verifier helpers for XFS block, extent, inode, realtime block, inode count, directory/attribute block, and file offset types.

Important APIs, types, and functions: Exports `xfs_verify_fsbno`, `xfs_verify_fsbext`, `xfs_verify_ino`, `xfs_is_sb_inum`, `xfs_verify_dir_ino`, `xfs_verify_rtbno`, `xfs_verify_rtbext`, `xfs_icount_range`, `xfs_verify_icount`, `xfs_verify_dablk`, `xfs_verify_fileoff`, and `xfs_verify_fileext`. Internal helpers validate AG block and AG inode ranges.

Control flow: Data block verifiers reject blocks outside AG count, outside the AG tail, or inside static AG metadata. Extent verifiers reject wraparound and cross-AG ranges. Inode verifiers reject impossible AG/AGINO conversions and values outside per-AG inode ranges; directory inode verification additionally rejects internal quota/realtime metadata inodes. Realtime verifiers handle rtgroups by checking group number, per-group extent count, rtsb exclusion, and cross-group extents; legacy realtime falls back to `sb_rblocks`.

State and persistence: No state is persisted. The functions validate persistent metadata pointers against mount geometry and per-AG inode range state.

Dependencies and integration points: Used throughout metadata verifiers, bmap/rmap/refcount code, directory checking, repair/scrub, and superblock write validation. Depends on per-AG iteration, rtgroup helpers, quota inode checks, and realtime bitmap conversions.

Risks and test signals: Risks include allowing static metadata references, wraparound misses, rtgroup tail extent mistakes, rtsb block allocation, and inode count range errors during grow/shrink/recovery. Test boundary blocks in first/last AG, AGFL/static metadata addresses, cross-AG and cross-RTG extents, rtgroup zero rtsb, internal inode directory entries, sparse inode ranges, and max file offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.h

Purpose: Defines fundamental XFS scalar types, null sentinel values, geometry limits, fork identifiers, extent/rmap/refcount records, group/free-counter enums, and verifier prototypes.

Important APIs, types, and functions: Provides typedefs for AG/RTG block and group numbers, inode numbers, extent lengths, filesystem/realtime block numbers, file offsets, log sequence numbers, quota ids, and failure addresses. Defines `NULL*` sentinels, block/sector size limits, fork ids, name length, lookup enum, `struct xfs_name`, bit constants, extent cursor and bmap record types, refcount domains/records, rmap flags/records, AG reservation types, btree record packing enum, group type enum, free counter enum, and verifier declarations.

Control flow: Headers across XFS use these types to maintain unit clarity. String mapping macros feed trace/debug output. Verifier prototypes route metadata checks to `xfs_types.c`.

State and persistence: Many typedefs and structs mirror persistent metadata fields or incore decoded forms of persistent records. Sentinel values are serialized or compared in metadata paths, so width stability matters.

Dependencies and integration points: Foundational include for libxfs, kernel XFS, userspace tools, tracepoints, btree/rmap/refcount/bmap code, scrub, quota, and transaction reservations.

Risks and test signals: Risks include changing type widths, sentinel collisions, trace enum drift, record flag mask mistakes, and misuse of filesystem vs realtime block units. Test kernel/userspace builds, sparse type checks where available, metadata boundary verifiers, trace enum consistency, and big filesystem/rtgroup configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.c

Purpose: Validates block-layer zone descriptors against XFS zoned realtime geometry and extracts write pointers for sequential zones.

Important APIs, types, and functions: Exports `xfs_validate_blk_zone`. Internal helpers `xfs_validate_blk_zone_seq` and `xfs_validate_blk_zone_conv` validate sequential-write-required and conventional zones respectively.

Control flow: Top-level validation checks that zone capacity equals expected realtime group capacity and zone length equals expected raw group size. Conventional zones are accepted only with `BLK_ZONE_COND_NOT_WP`. Sequential zones map empty to write pointer zero, open/closed/active states to `wp - start` after bounds checks, full zones to capacity, and reject not-write-pointer, offline, readonly, or unknown conditions.

State and persistence: No persistent state is written. The returned `write_pointer` is derived incore state used by zoned realtime allocation/open-zone tracking. Validation enforces superblock rtgroup geometry against device-reported topology.

Dependencies and integration points: Depends on Linux `blk_zone`, XFS mount block conversions, warning logging, and zoned realtime mount/device scan code.

Risks and test signals: Risks include accepting non-uniform last-zone capacity, write pointer conversion errors, unsupported conventional zone states, and mismatch between gapped raw zone size and allocatable capacity. Test empty/open/closed/active/full sequential zones, offline/readonly rejection, conventional zones, capacity/length mismatch, and write pointers at start/end/out-of-range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.h

Purpose: Defines zoned realtime reservation constants and declares the zone validation helper.

Important APIs, types, and functions: Defines `XFS_GC_ZONES`, `XFS_RESERVED_ZONES`, `XFS_MIN_ZONES`, `XFS_OPEN_GC_ZONES`, `XFS_MIN_OPEN_ZONES`, `XFS_DEFAULT_MAX_OPEN_ZONES`, and declares `xfs_validate_blk_zone`.

Control flow: Zoned allocation and mount code use the constants to preserve forward progress for garbage collection and user writes. The validation function is called while scanning block device zones.

State and persistence: Constants influence incore allocator policy and superblock/device acceptance. They do not persist state directly, but reservation policy affects free-space availability and GC behavior.

Dependencies and integration points: Integrates with zoned realtime allocator, rtgroup open-zone tracking, garbage collection, and device topology validation.

Risks and test signals: Risks include too-small reserved zone counts causing GC deadlock, too-large defaults reducing usable capacity, and mismatched open-zone assumptions on devices without explicit limits. Test minimum-zone mounts, max-open-zone limits, sustained writes with GC, and near-full zoned realtime filesystems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_zones.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.c -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.c

Purpose: Provides scrub helpers to record allocation-group btree blocks into typed AG-block bitmaps.

Important APIs, types, and functions: Exports `xagb_bitmap_set_btblocks` and `xagb_bitmap_set_btcur_path`; internal visitor `xagb_bitmap_visit_btblock` converts a cursor block buffer address to AG block number and sets one bit in `struct xagb_bitmap`.

Control flow: `xagb_bitmap_set_btblocks` uses `xfs_btree_visit_blocks` with `XFS_BTREE_VISIT_ALL` to mark every block in a per-AG btree. `xagb_bitmap_set_btcur_path` is optimized for left-to-right record walks: it climbs cursor levels while each level pointer is at slot one, marking blocks newly encountered along the leaf-to-root path.

State and persistence: State is an incore `xbitmap32` wrapped by `struct xagb_bitmap`. The helpers do not modify filesystem metadata; they collect observed btree block addresses for scrub cross-checks.

Dependencies and integration points: Used by online scrub code for btree ownership/coverage checks. Depends on generic btree cursors, buffer addresses, block conversion macros, and the `xbitmap32` range bitmap implementation.

Risks and test signals: Risks include using the path optimization on non-left-to-right walks, converting non-AG btree blocks, missing root blocks when cursor pointers are not at one, and bitmap allocation failures. Test all per-AG btree scrubbers, empty/single-level/multi-level btrees, corrupted cursor buffers, and memory allocation failure in bitmap set operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.h

Purpose: Defines a type-checked AG-block bitmap wrapper around `xbitmap32` for online scrub code.

Important APIs, types, and functions: Defines `struct xagb_bitmap` and inline wrappers `xagb_bitmap_init`, `xagb_bitmap_destroy`, `xagb_bitmap_clear`, `xagb_bitmap_set`, `xagb_bitmap_test`, `xagb_bitmap_disunion`, `xagb_bitmap_hweight`, `xagb_bitmap_empty`, `xagb_bitmap_walk`, and `xagb_bitmap_count_set_regions`. Declares btree block marking helpers.

Control flow: Scrub callers initialize a bitmap, add or remove AG-block ranges, test/walk/count regions, optionally subtract another bitmap, and destroy it after checks. The C file extends this with btree cursor collection.

State and persistence: The wrapper stores only an incore `xbitmap32`; no filesystem metadata is changed. Type-specific function signatures reduce accidental use of filesystem block or realtime block units.

Dependencies and integration points: Integrates with scrub bitmap utilities, per-AG btree scans, and xbitmap32 range operations.

Risks and test signals: Risks include unit confusion despite the wrapper, forgotten destroy calls, large fragmented bitmaps under corrupt metadata, and propagation of xbitmap32 allocation errors. Test bitmap set/clear/disunion/walk behavior, large AGs, fragmented ranges, and btree scrub call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/agb_bitmap.h -->
