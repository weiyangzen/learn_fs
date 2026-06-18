# subset-b-005783 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_format.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_format.h

Purpose: `xfs_format.h` is the central on-disk format contract for general XFS metadata. In this subset it is especially important because `xfs_ialloc.c` and `xfs_ialloc_btree.c` depend on the superblock, AGI, inode-number, and inode btree record layouts defined here. It deliberately separates incore and ondisk structures, with ondisk fields stored in fixed-endian types.

Important APIs, types, and constants: the file defines `struct xfs_sb` and `struct xfs_dsb`, v4/v5 superblock feature flags, conversion helpers such as `xfs_sb_is_v5`, `xfs_sb_has_*_feature`, block/address macros such as `XFS_AGB_TO_FSB`, `XFS_FSB_TO_AGNO`, `XFS_FSB_TO_AGBNO`, and allocation group headers `struct xfs_agf`, `struct xfs_agi`, and `struct xfs_agfl`. The inode allocation btree contract is defined by `XFS_IBT_MAGIC`, `XFS_FIBT_MAGIC`, `xfs_inofree_t`, `XFS_INODES_PER_CHUNK`, `XFS_INOBT_ALL_FREE`, `XFS_INOBT_MASK`, `XFS_INOBT_HOLEMASK_*`, `struct xfs_inobt_rec`, `struct xfs_inobt_rec_incore`, `struct xfs_inobt_key`, and `xfs_inobt_issparse`. Generic short-form btree block header layouts appear later in the file and are used by inode btrees.

Control flow and state behavior: this header has no runtime control flow beyond inline helpers and macros, but it encodes the rules that all runtime code must follow. Inode records are keyed by `ir_startino`; full-format records store a 32-bit freecount, while sparse-inode records replace the high bytes with a holemask and inode count. A zero holemask means a full chunk; a nonzero holemask means portions of the 64-inode chunk are not physically allocated. AGI logging masks split fields around the large `agi_unlinked` array so callers can log only changed ranges.

Persistence behavior: this file defines persistent metadata ABI. Superblock feature bits gate format interpretation: sparse inodes, finobt, inobt block counters, bigtime, and crc-enabled btree headers change how later code reads and writes structures. `struct xfs_agi` persists inode btree roots and levels, inode/free counts, `agi_newino`, unlinked inode buckets, CRC/LSN/UUID fields, and optional inobt/finobt block counts. Incorrect changes here corrupt mount, repair, scrub, and userspace tooling.

Dependencies and integration points: it is included throughout libxfs and kernel XFS code. The inode allocator consumes `XFS_AGI_*` bits for transaction logging and the inobt/finobt record layouts for btree updates. The btree implementation consumes `XFS_BTREE_SBLOCK*_LEN` and magic numbers for verification. Userspace tools rely on some address macros even when not referenced in kernel builds.

Risks: the main risks are ABI drift, endian mistakes, logging-mask mismatch with structure offsets, and inconsistent feature-bit gating. Sparse inode fields are compact and easy to misinterpret; `ir_free` means free inode state, while the holemask means physical allocation state. Another risk is over-trusting arithmetic macros when group size, inode geometry, or v5 feature support differs.

Test signals: good coverage comes from xfsprogs/kernel builds, xfstests exercising mkfs/mount/repair/scrub across v4/v5, finobt, sparse inode, bigtime, inobtcount, and realtime-group variants. Corruption tests should verify AGI/IBT/FIBT verifier failures, CRC/UUID/LSN checks, sparse inode chunk merge behavior, and round-trip compatibility with bulkstat/inumbers userspace tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_fs.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_fs.h

Purpose: `xfs_fs.h` defines the public Linux XFS userspace ABI: ioctl request structures, filesystem geometry records, bulk inode reporting, scrub/repair controls, exchange-range operations, parent pointer iteration, realtime group geometry, health monitor events, media verification, and ioctl command numbers. It must remain C++-compilable and stable for userspace.

Important APIs and types: early sections define `struct dioattr`, `struct getbmap`, and `struct getbmapx` plus bmap flags. Geometry APIs include `struct xfs_fsop_geom_v1`, `xfs_fsop_geom_v4`, and current `struct xfs_fsop_geom`, with feature flags such as `XFS_FSOP_GEOM_FLAGS_FINOBT`, `SPINODES`, `INOBTCNT`, `BIGTIME`, `NREXT64`, `PARENT`, `METADIR`, and `ZONED`. AG and realtime group reporting use `struct xfs_ag_geometry` and `struct xfs_rtgroup_geometry` with sick/checked masks. Bulk inode APIs include legacy `struct xfs_bstat`, current `struct xfs_bulkstat`, `struct xfs_inogrp`, `struct xfs_inumbers`, and `struct xfs_bulk_ireq`. Scrub is exposed through `struct xfs_scrub_metadata`, `struct xfs_scrub_vec`, and `struct xfs_scrub_vec_head`. Health monitoring is exposed through `struct xfs_health_monitor_event` and related detail structures.

Control flow and state behavior: as a UAPI header, it does not implement filesystem control flow; it defines the serialized parameters and result states for ioctls. Kernel call sites interpret flags, fill versioned structs, return sick/checked masks, and use vector barriers to short-circuit later scrub items after earlier errors. Inline helpers provide small ABI operations such as project-id reconstruction and variable-length parent-record iteration.

Persistence behavior: most structures are not on-disk persistence, but they are persistent ABI. Field widths, reserved zero fields, ioctl numbers, and flag meanings cannot change without breaking compiled userspace. Some structures expose persisted filesystem state, including superblock geometry, inode generation, inode allocation masks, AG health, rtgroup write pointer, and health-monitor event payloads.

Dependencies and integration points: this file integrates kernel XFS with xfsprogs, xfs_io, xfs_scrub, backup/indexing tools, monitoring daemons, and generic Linux fs ioctls. It maps kernel health masks from `xfs_health.h` into UAPI masks and exposes inobt/finobt health to scrub and geometry callers. The ioctl numbers are consumed by VFS ioctl dispatch and userspace libraries.

Risks: ABI compatibility is the dominant risk. Adding fields requires reserved padding and version/flag gating. Ambiguous input flags can cause unintended repair or cross-object operations, particularly scrub and exchange-range ioctls. Health monitor events must remain bindgen-friendly, which explains explicit named structs instead of anonymous nested unions. Large extent count compatibility needs careful `XFS_BULK_IREQ_NREXT64` handling to avoid silent truncation.

Test signals: build tests must include userspace headers and C++ compilation. xfstests should exercise every ioctl family: geometry, AG/rtgroup geometry, bulkstat/inumbers, scrub and scrubv, parent iteration, exchange/commit range, health monitor, media verify, and legacy request sizes. ABI tests should verify reserved fields are zeroed, unsupported flags fail predictably, old structure versions still work, and sick/checked masks match health state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.c -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.c

Purpose: `xfs_group.c` implements generic group lifecycle and lookup helpers for allocation groups and realtime groups. It abstracts common reference management, xarray storage, mark iteration, and teardown so per-AG and rtgroup code can share online/offline behavior.

Important functions: passive-reference helpers are `xfs_group_get`, `xfs_group_hold`, and `xfs_group_put`; active-reference helpers are `xfs_group_grab`, `xfs_group_next_range`, `xfs_group_grab_next_mark`, and `xfs_group_rele`. Lifecycle helpers are `xfs_group_insert`, `xfs_group_free`, and `xfs_group_get_by_fsb`.

Control flow: lookups run under `rcu_read_lock` and load `mp->m_groups[type].xa`. Passive gets increment `xg_ref` if the group exists. Active grabs use `atomic_inc_not_zero` on `xg_active_ref`, so groups being offlined, shrunk, or freed are not returned for active operations. Iteration helpers release the previous active reference before moving to the next index or marked xarray entry. Insert initializes the common fields, optional kernel-only busy extent tracking, state lock, hooks, and defer drain, then sets an initial active reference owned by the mount and inserts into the xarray. Free erases the xarray entry, checks passive references, drains deferred intents, releases kernel-only state, calls an optional uninit callback, drops the mount active reference, checks active reference underflow/leftovers, and frees by RCU.

State and persistence behavior: group objects are incore only. They mirror persistent AG or rtgroup geometry but do not write disk metadata. The mount's xarray is the authoritative incore index. `xg_ref` tracks passive users such as cached buffers, and `xg_active_ref` gates online access. Kernel-only fields track busy extents or zoned reset lists, health masks, intent drains, and repair hooks.

Dependencies and integration points: the file depends on xarrays, RCU, atomics, XFS tracepoints, busy extent support, deferred intent drains, and mount group arrays. `xfs_group_get_by_fsb` depends on `xfs_fsb_to_gno` from `xfs_group.h`. Higher layers use active grabs while walking AG or rtgroup btrees, while buffer/cache code can hold passive references.

Risks: reference symmetry is the primary risk. Missing `xfs_group_rele` on early exit leaks active refs and can block offlining; using passive refs for live state access can race shrink/offline; freeing with residual passive refs is treated as corruption. Mark iteration can skip a group that loses its active ref concurrently, so callers must tolerate NULL and retry/continue as appropriate. Insert failure cleanup must match kernel-only allocations.

Test signals: concurrency tests should exercise mount/unmount, grow/shrink/offline, scrub walks, xarray mark iteration, and busy extent cleanup under parallel metadata work. Debug builds should catch refcount underflow, lingering active refs, and passive refs at free. Tracepoints provide useful sequencing evidence for get/put/grab/rele leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.h

Purpose: `xfs_group.h` defines the generic incore `struct xfs_group` and inline geometry helpers shared by allocation groups and realtime groups. It provides the contract implemented by `xfs_group.c` and used by perag/rtgroup code.

Important types and APIs: `struct xfs_group` contains mount pointer, group number, group type, passive and active reference counters, precalculated usable block range, and kernel-only members for busy extents or zoned reset tracking, health state, state lock, deferred intent drain, and rmap update hooks. Function declarations cover get/hold/put, grab/rele, range iteration, marked iteration, insert/free, and lookup by fsblock. Mark macros wrap xarray mark operations. Inline conversion helpers include `xfs_group_max_blocks`, `xfs_groups_to_rfsbs`, `xfs_group_start_fsb`, `xfs_gbno_to_fsb`, `xfs_gbno_to_daddr`, `xfs_fsb_to_gno`, `xfs_fsb_to_gbno`, `xfs_verify_gbno`, and `xfs_verify_gbext`.

Control flow: most code is declarative or inline arithmetic. Address conversion maps between group-relative block numbers, filesystem block numbers, and disk addresses. `xfs_gbno_to_daddr` has a key branch for group layouts with physical address gaps: if `has_daddr_gaps` is set, it converts through group FSB numbering; otherwise it multiplies group number by uniform group block count. Verification helpers reject blocks below `xg_min_gbno`, at or beyond `xg_block_count`, zero-length extents, and overflowed end calculations.

State and persistence behavior: this header defines incore state, not on-disk layout. However, its geometry arithmetic must match persisted superblock group geometry and realtime group layout. The health fields are incore summaries that feed geometry ioctls and health monitoring. Intent drains synchronize transient deferred-operation state so online repair and scrub do not see intentional inconsistencies.

Dependencies and integration points: it depends on mount group geometry (`mp->m_groups[type]`) and XFS integer types from format headers. Per-AG wrappers such as `pag_group` and realtime wrappers such as `rtg_group` integrate typed group users with generic helpers. `xfs_health.h` uses `struct xfs_group` for group-level health functions.

Risks: address conversion errors can cause metadata I/O against the wrong group, particularly for realtime group layouts with gaps. Arithmetic overflow in extent verification is explicitly guarded; callers should use `xfs_verify_gbext` before trusting external or ondisk ranges. Reference fields must only be manipulated through the implementation helpers. Kernel-only union members require type discipline because the same storage means different things for zoned rtgroups and ordinary groups.

Test signals: unit or fstests coverage should include group-relative conversion for AGs, rtgroups, internal realtime sections, and zoned gap layouts. Boundary tests should cover minimum usable block, last valid block, zero length, overflow length, and absent `blklog` behavior. Concurrency tests should pair header helpers with the lifecycle functions in `xfs_group.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_group.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_health.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_health.h

Purpose: `xfs_health.h` defines incore metadata health state and helper APIs for XFS. It provides the flag taxonomy used by online scrub, online repair, geometry ioctls, health monitoring, and runtime corruption reporting.

Important APIs and masks: health flags are grouped by filesystem (`XFS_SICK_FS_*`), realtime group (`XFS_SICK_RG_*`), allocation group (`XFS_SICK_AG_*`), and inode (`XFS_SICK_INO_*`). Each group defines primary, secondary, indirect, and all masks. AG flags include AGI, inobt, finobt, rmapbt, refcountbt, and bad-inodes indicators. Inode flags include core, bmap forks, directory, xattr, symlink, parent, directory tree, zapped forks, and `XFS_SICK_INO_FORGET`. The implementation-facing API declares `xfs_*_mark_sick`, `xfs_*_mark_corrupt`, `xfs_*_mark_healthy`, and `xfs_*_measure_sickness` for fs, group, and inode domains. It also declares mapper helpers for bmap, btree, dir/attr, health unmount, ioctl health export, and health monitor mask conversion.

Control flow and semantics: the header documents the state machine for each health bit using separate `checked` and `sick` fields. `checked && sick` means repair is needed; `checked && !sick` means checked healthy; `!checked && sick` means runtime evidence of a problem without a full check; `!checked && !sick` means not examined since mount. Mark-sick sets sick without checked, mark-corrupt sets both, mark-healthy clears sick and sets checked, and measure returns both bitmaps. Inline helpers measure and test sickness for fs, group, rtgroup, and inode domains.

State and persistence behavior: health state is incore and generally not persisted as metadata state, but it is externally visible through geometry, bulkstat, health-monitor, and log notices at unmount. Runtime metadata verifier failures feed these flags so administrators and repair tooling can react without necessarily forcing immediate shutdown.

Dependencies and integration points: `xfs_ialloc.c` marks AGI and inobt/finobt problems through this interface. `xfs_ialloc_btree.c` sets `sick_mask` in btree ops so generic btree code can mark the appropriate AG metadata unhealthy. `xfs_fs.h` publishes related UAPI masks. Scrub/repair implementations are expected to set checked/sick state according to findings and fixes.

Risks: incorrect classification can hide real corruption or over-report harmless secondary evidence. Confusing primary, secondary, and indirect flags can cause scrub/repair to clear symptoms while leaving root problems. Callers must not treat `!sick` as checked unless the checked bit is also set. Mask translations to UAPI must stay synchronized with `xfs_fs.h` and health monitor event definitions.

Test signals: scrub and repair tests should verify all four checked/sick combinations, mark_sick vs mark_corrupt vs mark_healthy transitions, propagation from btree and buffer verifiers, unmount notices, geometry/bulkstat export masks, and health monitor event mask conversion. Fault injection should check that `-EFSCORRUPTED` and `-EFSBADCRC` paths map to sickness via `xfs_metadata_is_sick`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_health.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.c -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.c

Purpose: `xfs_ialloc.c` implements inode allocation, inode freeing, inode-to-buffer mapping, AGI logging and verification, inode geometry setup, inode-count queries, and shrink checks. It is the main policy layer over the inode allocation btrees.

Important APIs and functions: public entry points include `xfs_dialloc`, `xfs_difree`, `xfs_imap`, `xfs_ialloc_inode_init`, `xfs_ialloc_log_agi`, `xfs_read_agi`, `xfs_ialloc_read_agi`, `xfs_inobt_lookup`, `xfs_inobt_get_rec`, `xfs_inobt_insert_rec`, `xfs_inobt_btrec_to_irec`, `xfs_inobt_rec_freecount`, `xfs_inobt_check_irec`, `xfs_ialloc_has_inodes_at_extent`, `xfs_ialloc_count_inodes`, `xfs_ialloc_setup_geometry`, `xfs_ialloc_calc_rootino`, and `xfs_ialloc_check_shrink`. Internal helpers handle inobt record updates, full and sparse chunk insertion, finobt synchronization, AG selection, transaction rolling, AGI verifier operations, and free chunk extent release.

Control flow: allocation starts in `xfs_dialloc`, which picks a starting AG from the parent, metadata-directory, or directory rotor policy. It decides whether new inode chunks may be allocated based on inode limits and low free space, then scans AGs first with trylock flags and later blocking. `xfs_dialloc_try_ag` reads/locks AGI, allocates a new inode chunk if needed via `xfs_ialloc_ag_alloc`, rolls the transaction to preserve the newly allocated free inode, and then allocates one inode through `xfs_dialloc_ag`. With finobt enabled, allocation searches the free-inode btree near the parent or `agi_newino`, updates/deletes the finobt record, then independently updates the matching inobt record. Without finobt, it searches inobt records directly. Freeing starts in `xfs_difree`, validates inode-to-AG mapping, updates the inobt through `xfs_difree_inobt`, and mirrors the change in finobt when present.

State and persistence behavior: persistent mutations include inode buffers initialized by `xfs_ialloc_inode_init`, inobt/finobt records, AGI `agi_count`, `agi_freecount`, `agi_newino`, roots/levels through btree operations, and superblock inode counters. Sparse chunks persist physical allocation state in `ir_holemask` and free-inode state in `ir_free`. V3 inode initialization logs an `icreate` intent and ordered inode buffers; older inode formats log inode cores directly. AGI logging is split around `agi_unlinked` to avoid excessive log ranges.

Dependencies and integration points: this file depends on btree cursors, allocation (`xfs_alloc_vextent_*`, `xfs_free_extent_later`), transactions, inode buffer ops, icreate log items, rmap owner info, perag geometry, health marking, and superblock counter accounting. `xfs_imap` integrates untrusted inode validation for bulkstat/handle lookups with direct arithmetic for aligned trusted inodes.

Risks: inobt and finobt must remain equivalent except for finobt omission of full chunks. Errors in sparse record alignment/merge can create overlapping inode records. Counter ordering is delicate: AGI, perag, and superblock counters must change consistently. Transaction rolling must hold AGI so another allocation cannot steal newly created free inodes. `xfs_imap` must reject stale/untrusted inode numbers to avoid reading removed inode buffers. Near ENOSPC behavior is intentionally complex and can produce excess scanning.

Test signals: xfstests should cover full and sparse inode chunk allocation, finobt-enabled and disabled filesystems, low-space allocation, max inode limits, parent-near allocation, root inode calculation, inode freeing with whole-chunk removal, sparse chunk extent freeing, untrusted imap rejection, AGI verifier CRC/UUID/level/unlinked checks, debug freecount checks, shrink refusal for sparse records crossing new EOAG, and fault injection for AGI reads and btree corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.h

Purpose: `xfs_ialloc.h` declares the inode allocation public interface used by libxfs and kernel XFS code. It exposes the allocator, freer, mapper, AGI accessors, inode btree record helpers, geometry setup, and shrink validation implemented mostly by `xfs_ialloc.c`.

Important APIs and types: `XFS_INODE_BIG_CLUSTER_SIZE` sets the default desired inode cluster size. `struct xfs_icluster` reports whether freeing an inode deleted a whole inode chunk, the first inode in that chunk, and the physical allocation bitmap for sparse chunks. `xfs_make_iptr` maps a buffer and inode index to an ondisk `struct xfs_dinode`. Public functions include `xfs_dialloc`, `xfs_difree`, `xfs_imap`, `xfs_ialloc_log_agi`, `xfs_read_agi`, `xfs_ialloc_read_agi`, `xfs_inobt_lookup`, `xfs_inobt_get_rec`, `xfs_inobt_rec_freecount`, `xfs_ialloc_inode_init`, `xfs_inobt_btrec_to_irec`, `xfs_inobt_check_irec`, `xfs_ialloc_has_inodes_at_extent`, `xfs_ialloc_count_inodes`, `xfs_inobt_insert_rec`, `xfs_ialloc_cluster_alignment`, `xfs_ialloc_setup_geometry`, `xfs_ialloc_calc_rootino`, and `xfs_ialloc_check_shrink`.

Control flow: the header does not implement control flow beyond `xfs_make_iptr`, but its signatures define the required transaction and locking shape. Allocation takes `struct xfs_trans **` because it may roll the transaction while preserving caller context. Freeing requires a caller-provided `struct xfs_perag` and returns chunk deletion information through `struct xfs_icluster`. Mapping accepts flags such as untrusted lookup requirements so callers can force btree validation before reading inode buffers.

State and persistence behavior: the declared functions mutate persistent inode allocation metadata: inode chunks, inobt/finobt records, AGI counters and roots, and superblock inode counters. `struct xfs_icluster` is an incore report of persistent chunk state used by callers to handle cache invalidation and sparse physical allocation. AGI read helpers initialize perag cached counters from disk and return locked buffers when requested.

Dependencies and integration points: this header ties inode creation code, inode cache lookup, bulkstat, scrub, grow/shrink, btree repair, and transaction code to the allocator implementation. It forward-declares core XFS types to avoid heavy includes and relies on format definitions for inode record types and constants.

Risks: misuse of transaction pointer semantics can break allocation when `xfs_dialloc` rolls the transaction. Calling `xfs_imap` without `XFS_IGET_UNTRUSTED` for externally supplied inode numbers can map stale or freed disk state. Callers of `xfs_difree` must pass the correct perag for the inode. `xfs_make_iptr` assumes valid buffer sizing and inode geometry.

Test signals: compile coverage should catch signature drift across allocator, inode cache, and repair code. Behavioral tests should verify transaction rolling through `xfs_dialloc`, chunk deletion reporting from `xfs_difree`, untrusted imap validation, AGI trylock behavior, and geometry setup consumed by mkfs/mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.c -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.c

Purpose: `xfs_ialloc_btree.c` implements the generic btree operations for the inode allocation btree (`inobt`) and free inode btree (`finobt`). It supplies cursor creation, key/record conversion, root updates, block allocation/freeing, verifiers, ordering checks, sparse holemask conversion, finobt reservation accounting, staged-btree commit, and cursor cache lifecycle.

Important APIs and functions: exported entry points include `xfs_inobt_init_cursor`, `xfs_finobt_init_cursor`, `xfs_inobt_commit_staged_btree`, `xfs_inobt_maxrecs`, `xfs_iallocbt_maxlevels_ondisk`, `xfs_inobt_irec_to_allocmask`, debug `xfs_inobt_rec_check_count`, `xfs_finobt_calc_reserves`, `xfs_iallocbt_calc_size`, `xfs_inobt_init_cur_cache`, and `xfs_inobt_destroy_cur_cache`. It defines `xfs_inobt_buf_ops`, `xfs_finobt_buf_ops`, `xfs_inobt_ops`, and `xfs_finobt_ops`.

Control flow: cursor operations are callbacks consumed by generic `xfs_btree` code. Root setters write `agi_root`/`agi_level` or `agi_free_root`/`agi_free_level` and log AGI fields. Btree block allocation requests one block near the requested start with rmap owner `XFS_RMAP_OINFO_INOBT`; finobt uses metadata reservation unless `m_finobt_nores` is set. Freeing queues a one-block extent free with the same owner and reservation class. Verifiers check magic, v5 headers/CRC, level bounds against inode geometry, and record capacity. Cursor initialization holds the perag group and reads levels from AGI when a real AGI buffer is supplied. Staged commit installs fake-root data into AGI and commits the staged btree root.

State and persistence behavior: this file persists btree structural changes and AGI root/level/block-count fields. `xfs_inobt_mod_blockcount` updates `agi_iblocks` or `agi_fblocks` when the inobtcount feature is enabled. Buffer ops validate and update CRCs on inobt/finobt blocks. `xfs_inobt_irec_to_allocmask` converts sparse holemask state into an inode-granularity physical allocation bitmap, which is important for sparse chunks and repair.

Dependencies and integration points: it depends on generic btree infrastructure, btree staging, AGI logging from `xfs_ialloc.c`, allocation/free space code, rmap owner metadata, health masks from `xfs_health.h`, and group/perag references. The ops table uses `XFS_SICK_AG_INOBT` and `XFS_SICK_AG_FINOBT` so generic btree corruption reporting can mark the right AG health bit.

Risks: inobt and finobt share most callbacks but differ in root fields, reservation class, magic numbers, and health masks; mixing them corrupts AGI state. Block count updates must only happen with the inobtcount feature. Verifier bounds depend on correctly initialized inode geometry. Sparse holemask conversion is bit-sensitive: holemask zero bits mean physically allocated inode groups, while `ir_free` bits mean logically free inodes. Staged commit callers remain responsible for invalidating/freeing old btree blocks.

Test signals: tests should cover btree block verifier failures for bad magic, crc, v5 owner/uuid, invalid levels, and record counts; cursor creation for inobt and finobt; root split/shrink logging; finobt metadata reservation accounting with and without inobtcounts; sparse allocmask conversion; staged repair commits; and cursor cache init/destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.h -->
## sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.h

Purpose: `xfs_ialloc_btree.h` declares the inode btree interface and layout helpers for inobt and finobt blocks. It bridges the on-disk record definitions in `xfs_format.h` with the btree implementation in `xfs_ialloc_btree.c` and allocator policy in `xfs_ialloc.c`.

Important APIs and macros: `XFS_INOBT_BLOCK_LEN(mp)` selects the short-form btree header size based on CRC support. `XFS_INOBT_REC_ADDR`, `XFS_INOBT_KEY_ADDR`, and `XFS_INOBT_PTR_ADDR` compute record/key/pointer locations inside a btree block; comments note that these are used by userspace even if not always by kernel code. Public functions include `xfs_inobt_init_cursor`, `xfs_finobt_init_cursor`, `xfs_inobt_maxrecs`, `xfs_inobt_irec_to_allocmask`, debug `xfs_inobt_rec_check_count`, `xfs_finobt_calc_reserves`, `xfs_iallocbt_calc_size`, `xfs_inobt_commit_staged_btree`, `xfs_iallocbt_maxlevels_ondisk`, and cursor cache init/destroy.

Control flow and state behavior: the header itself contains only address arithmetic and declarations. The address macros assume one-based btree slot indexes, a valid block pointer, a caller-supplied `maxrecs` for pointer arrays, and the proper header length for the mounted format. Cursor constructors require perag, optional transaction, and optional AGI buffer; staging cursors pass NULL transaction and AGI buffer.

Persistence behavior: this header does not write metadata directly, but it defines how code locates persistent btree records within on-disk buffers. Header length selection is format-sensitive: CRC-enabled filesystems have larger btree headers with UUID/owner/LSN/CRC fields, and using the wrong size would shift every record. Reserve and size functions affect persistent metadata reservation accounting for finobt.

Dependencies and integration points: it depends on `xfs_format.h` types such as `xfs_inobt_rec_t`, `xfs_inobt_key_t`, pointer types, and btree header lengths. It is consumed by inode allocator code, repair/staging code, userspace tools, and generic btree code. The reserve API integrates finobt sizing into per-AG metadata reservation setup.

Risks: off-by-one indexing in address macros can corrupt or misread btree blocks. Consumers must pass the same `maxrecs` value used to lay out a node block. CRC feature gating must be consistent with mounted superblock state. Debug-only `xfs_inobt_rec_check_count` compiles away in production, so production code must not rely on it for essential validation.

Test signals: build tests should include kernel and xfsprogs users. Btree layout tests should validate record/key/pointer offsets for CRC and non-CRC filesystems, leaf and node blocks, minimum block sizes, and max record calculations. Repair tests should exercise staged btree commit and finobt reserve calculations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ialloc_btree.h -->
