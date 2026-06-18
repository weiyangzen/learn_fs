# Research: subset-b-005777

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xattr.c -->
# sources/distributed-fs/ceph-client/fs/xattr.c

## Purpose
This file implements Linux VFS extended attribute handling: namespace dispatch to filesystem xattr handlers, permission and LSM checks, syscall entry points for set/get/list/remove xattrs, POSIX ACL special routing, and the in-memory `simple_xattr` helper store used by simple filesystems. It is a policy and plumbing layer, not an on-disk xattr format implementation.

## Important APIs, Types, and Functions
- `xattr_resolve_name` walks `inode->i_sb->s_xattr` handler arrays, strips the matched prefix, validates exact-name handlers, and returns `-EOPNOTSUPP`, `-EINVAL`, or `-EIO` for unsupported, malformed, or bad-inode cases.
- `may_write_xattr` rejects immutable, append-only, or unmapped-id inodes before writes.
- `xattr_permission` centralizes VFS namespace policy: `security.*` and `system.*` defer to filesystem/LSM, `trusted.*` requires `CAP_SYS_ADMIN`, and `user.*` is limited by inode type plus sticky-directory ownership rules before falling through to `inode_permission`.
- VFS entry points include `vfs_setxattr`, `vfs_getxattr`, `vfs_listxattr`, `vfs_removexattr`, and lower-level locked/noperm variants such as `__vfs_setxattr_locked`, `__vfs_setxattr_noperm`, `__vfs_getxattr`, and `__vfs_removexattr_locked`.
- Syscall helpers include `path_setxattrat`, `path_getxattrat`, `path_listxattrat`, `path_removexattrat`, plus `setxattrat/getxattrat/listxattrat/removexattrat` and legacy `l*`/`f*` variants.
- `import_xattr_name`, `setxattr_copy`, and `kernel_xattr_ctx` move user names/values into kernel memory with `XATTR_SIZE_MAX` and flag validation.
- `generic_listxattr`, `xattr_list_one`, and `xattr_full_name` support filesystem handler implementations.
- The `simple_xattr*` family stores ephemeral xattrs in an `rhashtable`: allocation/free, get, set, limited set with atomic per-inode counters, list, lazy allocation, and teardown.

## Control Flow
Set operations import the user name/value, resolve either an fd or path with `AT_EMPTY_PATH` and symlink flags, acquire write access to the mount, route POSIX ACL names to ACL helpers, and otherwise call `vfs_setxattr`. `vfs_setxattr` converts file capabilities with `cap_convert_nscap`, locks the inode, performs namespace permission, LSM set checks, delegation breaking, and finally calls `__vfs_setxattr_noperm`; the noperm layer invokes filesystem handlers or `security_inode_setsecurity` fallback for `security.*`.

Get operations import the name, allocate a bounded buffer if the caller supplied a size, route ACLs separately, check permissions and LSM access, prefer active LSM `security.*` values via `security_inode_getsecurity`, and fall back to filesystem handler `get`. List operations call the inode `listxattr` op when present, otherwise list LSM security attributes; syscall wrappers cap `XATTR_LIST_MAX` and copy results back to userspace. Remove operations mirror set: write mount access, ACL special handling, VFS permission/LSM/delegation, handler `set(..., NULL, 0, XATTR_REPLACE)`, fsnotify, and LSM post-remove.

The `simple_xattr` helpers use RCU lookups for readers, externally serialized writers for set/replace/remove, and rhashtable walks for list. Set returns the replaced/removed object to be freed by the caller, with RCU delayed free when concurrent readers may still observe it.

## State and Persistence Behavior
The main VFS xattr paths mutate filesystem state only through filesystem xattr handlers, ACL helpers, and LSM security hooks. They also emit fsnotify notifications and update transaction-like mount write access around write syscalls. The simple xattr store is in-memory state: `struct simple_xattrs` owns an rhashtable of `struct simple_xattr` objects and can be lazily allocated/published with release semantics. It is not persistent unless a filesystem persists it separately.

## Dependencies and Integration Points
This file integrates with inode operation flags (`IOP_XATTR`), superblock `s_xattr` handler tables, idmapped mounts, VFS path lookup, file delegation breaking, POSIX ACL helpers, LSM hooks, audit, fsnotify, mount write accounting, RCU, rhashtable, and capability namespace conversion for `security.capability`.

## Risks and Edge Cases
Important risks are namespace policy regressions, missing delegation retry handling, incorrect LSM fallback for `security.*`, mishandling zero-length xattrs versus removal, user buffer truncation (`-ERANGE`/`-E2BIG`), `trusted.*` disclosure, bad inode behavior, and writer serialization requirements for simple xattrs. Lazy allocation uses `smp_store_release` but does not handle competing allocations beyond publishing one pointer, so callers must match expected serialization/lifetime rules.

## Test Signals
Relevant tests exercise all syscall variants including `*at` and `AT_EMPTY_PATH`, symlink-follow behavior, file descriptor paths, xattr namespace permissions, sticky directory `user.*` write denial, immutable/append-only denial, file capabilities under idmapped mounts, LSM `security.*` get/set/list behavior, POSIX ACL routing, delegation retry, list/get size probing, and simple_xattr create/replace/remove/list limits and RCU-safe teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/xfs/Kconfig

## Purpose
This Kconfig file exposes XFS kernel configuration switches. It defines the main `XFS_FS` tristate and feature/debug gates for deprecated formats, quotas, POSIX ACLs, realtime subvolumes, online scrub/repair, statistics, hooks, in-memory btrees, warnings, and debug behavior.

## Important Symbols
- `XFS_FS` depends on `BLOCK` and selects `EXPORTFS`, `CRC32`, and `FS_IOMAP`.
- `XFS_SUPPORT_V4` and `XFS_SUPPORT_ASCII_CI` are deprecated-format compatibility toggles, defaulting to `n`, with documented removal timelines.
- `XFS_QUOTA`, `XFS_POSIX_ACL`, and `XFS_RT` enable quota, ACL, and realtime subvolume code.
- Internal booleans `XFS_DRAIN_INTENTS`, `XFS_LIVE_HOOKS`, `XFS_MEMORY_BUFS`, and `XFS_BTREE_IN_MEM` are selected by scrub/repair.
- `XFS_ONLINE_SCRUB`, `XFS_ONLINE_SCRUB_STATS`, and `XFS_ONLINE_REPAIR` gate mounted metadata checking, debugfs usage stats, and mounted repair.
- `XFS_WARN`, `XFS_DEBUG`, `XFS_DEBUG_EXPENSIVE`, and `XFS_ASSERT_FATAL` tune runtime diagnostics and assertion behavior.

## Control Flow and Build Effects
Kconfig dependency resolution controls which objects from `fs/xfs/Makefile` are built. Enabling online scrub selects live hooks, drain intents, and memory-backed buffers; enabling repair selects in-memory btrees. `XFS_RT` defaults to `BLK_DEV_ZONED`, making realtime support mandatory for zoned block devices in the described configuration.

## State and Persistence Behavior
Kconfig itself stores no runtime filesystem state, but it determines whether kernels can mount or operate on certain on-disk features. Disabling V4 or ASCII-CI compatibility can deliberately reject older/case-insensitive filesystems. Enabling online repair changes mounted repair capabilities but does not by itself persist metadata.

## Dependencies and Integration Points
The symbols integrate with the kernel build system, XFS Makefile object lists, generic quota and ACL subsystems, debugfs, tmpfs/shmem for online scrub support, jump labels, iomap, exportfs, and zoned block device support.

## Risks and Edge Cases
Risk centers on distribution defaults: turning off deprecated compatibility can make legacy filesystems unmountable, while turning it on preserves attack surface. Online repair depends on newer on-disk metadata such as reverse mappings and parent pointers, so configuration support is not sufficient for all filesystems. Debug options can drastically alter performance and failure mode.

## Test Signals
Useful signals are allmodconfig/allyesconfig build coverage, feature-matrix builds for quota/ACL/RT/scrub/repair, boot/mount tests for V4 and ASCII-CI images with symbols on and off, xfstests scrub/repair groups, debugfs scrub stats checks, and build checks that selected internal symbols pull the expected object files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/Makefile -->
# sources/distributed-fs/ceph-client/fs/xfs/Makefile

## Purpose
This Makefile defines how the XFS kernel module or built-in object is assembled. It sets include paths for trace events and libxfs, orders trace compilation first, builds common libxfs components, high-level VFS integration, transaction/log recovery code, optional quota/realtime/ACL/compat/exportfs objects, and online scrub/repair objects under their Kconfig gates.

## Important Build Groups
- `obj-$(CONFIG_XFS_FS) += xfs.o` ties all `xfs-y` fragments into the XFS object.
- `xfs_trace.o` is first because trace macro expansion can be fragile.
- `libxfs/` objects include allocation group, allocator, btrees, metadata formats, directory, inode, rmap, refcount, realtime group, and transaction reservation code shared conceptually with userspace libxfs.
- High-level objects include VFS I/O, buffers, inode cache, ioctl, iomap, reflink, mount/super, sysfs, xattrs, and health monitoring.
- Transaction/log objects include log, CIL, item formats, recovery, AIL, and transaction buffer handling.
- Conditional groups cover quota, realtime, POSIX ACL, sysctl, compat ioctls, pNFS block export, DAX memory failure notification, hooks/drain/memory buffer/in-memory btree, scrub, scrub stats, and repair.

## Control Flow and Integration
The file has no runtime control flow, but the object ordering shapes link-time availability. The early libxfs group makes core metadata code available to higher layers; optional scrub/repair objects are only compiled under nested `ifeq` gates. It mirrors `Kconfig` symbols and therefore is the concrete build integration point for feature selection.

## State and Persistence Behavior
No runtime state is stored here. Build selections determine which runtime subsystems exist and therefore whether certain persistent on-disk features can be serviced.

## Dependencies and Integration Points
The Makefile integrates with Kbuild, Kconfig symbols, XFS trace headers, `libxfs` include paths, memory failure/DAX support, realtime code, quota, ACL, online scrub/repair, and exportfs block operations.

## Risks and Edge Cases
Object omission or ordering mistakes can break link dependencies, trace generation, or optional feature builds. Conditional blocks must remain consistent with Kconfig selects: for example repair depends on scrub and adds in-memory btree code; realtime scrub/repair objects require `CONFIG_XFS_RT`; quota scrub/repair requires `CONFIG_XFS_QUOTA`.

## Test Signals
Build all Kconfig combinations that toggle `XFS_QUOTA`, `XFS_RT`, `XFS_POSIX_ACL`, `CONFIG_COMPAT`, `CONFIG_SYSCTL`, `CONFIG_XFS_ONLINE_SCRUB`, and `CONFIG_XFS_ONLINE_REPAIR`. Link failures, missing symbols, modpost warnings, trace build failures, and xfstests feature skips are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.c

## Purpose
This file manages XFS allocation group lifecycle and geometry: per-AG allocation/free, initialization of in-core counters from AG headers, AG header construction for growfs, tail-AG shrink/extend operations, grow delta calculation, and reporting AG geometry.

## Important APIs and Functions
- `xfs_initialize_perag_data` reads every AGF/AGI, totals free blocks, freelist blocks, btree blocks, inode counts, validates counters, updates the in-core superblock, and reinitializes percpu counters.
- `xfs_initialize_perag`, `xfs_free_perag_range`, and `xfs_perag_alloc` create or free `struct xfs_perag` instances via generic `xfs_group` infrastructure.
- `xfs_ag_block_count`, `xfs_agino_range`, and `xfs_update_last_ag_size` compute AG block and inode ranges, especially for a short last AG after recovery/growfs.
- `xfs_ag_init_headers` initializes secondary superblocks, AGF/AGFL/AGI headers, and btree roots for new AGs.
- `xfs_ag_shrink_space` removes free space from the end of the last AG, updates AGF/AGI length, reinitializes reservations, and adjusts perag geometry.
- `xfs_growfs_compute_deltas` computes new AG count and data-block delta under minimum/maximum AG constraints.
- `xfs_ag_extend_space` extends the last AG, frees the new space into rmap/free-space metadata, and updates perag geometry.
- `xfs_ag_get_geometry` fills `xfs_ag_geometry` from AGF/AGI and in-core health/free-space accounting.

## Control Flow
Mount initialization allocates perag structures, then `xfs_initialize_perag_data` forces AGF/AGI reads so lazy superblock counters can be reconstructed from authoritative per-AG metadata. Growfs creates perag structures and writes new headers using uncached buffers, with initializer callbacks for each header/root type gated by rmap, finobt, and reflink features. Shrink first validates AGF/AGI consistency and inode-cluster safety, temporarily frees per-AG reservations, allocates the terminal range exactly to remove it from free-space btrees, rechecks reservations, and only then commits AG length reductions.

## State and Persistence Behavior
Persistent state includes AGF, AGFL, AGI, secondary superblocks, and btree root blocks written during grow/shrink/extend. In-core state includes `xfs_perag` counters, geometry, blockgc work, inode cache roots, opstate bits, and superblock/percpu counters. New secondary superblocks are marked `sb_inprogress` until growfs activation completes, giving recovery/repair a signal for incomplete growth.

## Dependencies and Integration Points
This file depends on allocation btrees, rmap/refcount/inode btrees, transactions, deferred ops, health marking, buffer operations, mount geometry, blockgc, and generic group reference management. It is used by mount, growfs, shrink, geometry ioctl paths, and recovery.

## Risks and Edge Cases
Counter reconstruction rejects obviously impossible `fdblocks` or inode totals to avoid mounting corrupt AGFs. Growfs must use uncached buffers because new AG headers are beyond current valid filesystem space. Shrink is risky: it must avoid inode clusters beyond the new end, handle ENOSPC when reservations cannot be reestablished, roll transactions while holding AGF/AGI to avoid allocation races, and force shutdown on reservation repair failure.

## Test Signals
Exercise mount counter rebuild after lazy counters, corrupted AGF/AGI lengths, growfs with rmap/finobt/reflink combinations, interrupted growfs recovery, shrink of a full or fragmented tail AG, shrink with inode clusters near the end, reservation reinit ENOSPC paths, geometry ioctls, and health/sick marking under verifier failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.h

## Purpose
This header defines XFS per-allocation-group in-core structures, reservation data, opstate helpers, perag reference/iteration helpers, AG geometry validation helpers, and prototypes for AG lifecycle/grow/shrink functions.

## Important Types and APIs
- `struct xfs_ag_resv` tracks original reserved, currently reserved, and requested blocks for a per-AG reservation.
- `struct xfs_perag` embeds `struct xfs_group` and caches AGF/AGI counters, btree levels, free/inode counts, metadata reservations, inode allocation search hints, inode cache state, and blockgc work.
- Opstate bits include `AGF_INIT`, `AGI_INIT`, `PREFERS_METADATA`, `ALLOWS_INODES`, and `AGFL_NEEDS_RESET`, with generated inline testers.
- Reference helpers distinguish passive refs (`xfs_perag_get/hold/put`) from active refs (`xfs_perag_grab/rele`) and wrap generic `xfs_group` operations.
- Iteration helpers include `xfs_perag_next_range`, `xfs_perag_next_from`, `xfs_perag_next`, and wrap-around macros for allocation scans.
- Geometry helpers verify AG block extents, AG inode numbers, log containment, and convert AG block/inode numbers to fsblock, disk address, or inode number.
- `struct aghdr_init_data` carries state for new AG header initialization.

## Control Flow and Usage
Most functions are inline wrappers used throughout XFS allocator, inode allocation, scrub, and growfs paths. Allocation scans use wrap iterators to grab each AG in an order that respects locality and deadlock constraints. Verifiers and allocation code use cached perag geometry to reject invalid block/inode numbers without rereading disk headers.

## State and Persistence Behavior
`xfs_perag` is in-core only, but mirrors persistent AGF/AGI values such as free blocks, freelist count, btree levels, and inode counts. Reservation fields affect global free-block accounting through allocator code, though the reservation itself is a virtual in-core accounting construct rather than an on-disk allocation.

## Dependencies and Integration Points
This header sits between generic group management (`xfs_group.h`), allocator code, inode allocation, rmap/refcount btrees, mount geometry, online repair, inode cache, and background block garbage collection. Kernel-only fields are guarded by `__KERNEL__`.

## Risks and Edge Cases
Incorrect reference type use can race unmount or AG teardown. Stale cached AGF/AGI counters can lead to allocator misbehavior, so initialization opstate bits matter. AG inode validation must account for static metadata and short last AGs. Wrap iteration must release the current AG before grabbing the next to avoid leaks and stale refs.

## Test Signals
Compile tests should cover kernel and userspace libxfs includes. Runtime signals include AG iteration under grow/shrink, inode allocation range checks, short-last-AG geometry, blockgc cancellation during perag free, online repair alternate btree heights, and lock/reference debugging for perag get/grab/put/rele paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.c

## Purpose
This file implements per-AG block reservations that keep space available for metadata btree growth, especially refcount and rmap btrees. It uses in-core reservation counters plus global free-block accounting adjustments to virtually withhold blocks rather than writing explicit reservation metadata to disk.

## Important APIs and Functions
- `xfs_ag_resv_critical` reports low-reservation conditions based on remaining availability below 10 percent, below max btree height, or injected error tags.
- `xfs_ag_resv_needed` computes how many reserved blocks must remain unavailable to a given allocation type.
- `xfs_ag_resv_free` and `__xfs_ag_resv_free` return hidden blocks to fdblocks and reset reservation counters.
- `__xfs_ag_resv_init` hides reservation space from fdblocks, adjusts `m_ag_max_usable` for AG 0, and initializes `ar_asked`, `ar_orig_reserved`, and `ar_reserved`.
- `xfs_ag_resv_init` calculates reservation needs for refcountbt, finobt, and rmapbt, falls back if finobt reservation cannot be made, and ensures AGF-derived counters are initialized.
- `xfs_ag_resv_alloc_extent` and `xfs_ag_resv_free_extent` debit or replenish reservation counters and update transaction superblock deltas correctly for reserved versus ordinary blocks.

## Control Flow
Mount/grow/shrink paths call `xfs_ag_resv_init` per AG. Metadata reservation is attempted first from refcountbt and finobt calculations; if the combined reservation fails, the code marks `m_finobt_nores` and retries only the refcountbt requirement. Rmapbt reservation is separate because rmapbt blocks live in free space/AGFL accounting. Allocation and free paths pass a reservation type so the reservation can be consumed or replenished instead of treating all blocks as ordinary fdblocks.

## State and Persistence Behavior
Reservation state is stored in `pag->pag_meta_resv` and `pag->pag_rmapbt_resv`; global free-block accounting is adjusted via `xfs_dec_fdblocks`, `xfs_add_fdblocks`, and `xfs_trans_mod_sb`. There is no on-disk reservation record. After a crash, free-space metadata and normal mount-time accounting rebuild the usable state.

## Dependencies and Integration Points
The file integrates with refcount, rmap, and inode allocation reserve calculators; AGF reads; transaction superblock accounting; error injection; tracepoints; and allocator reservation types (`XFS_AG_RESV_*`). `xfs_alloc.c` uses `xfs_ag_resv_needed`, `alloc_extent`, and `free_extent` to enforce the virtual reservations.

## Risks and Edge Cases
Incorrect hidden-space math can overstate free blocks or starve userspace. Rmapbt differs from other metadata because its used blocks remain counted as free-space-owned, so `ar_orig_reserved` handling matters at unmount. Reservation init can return `-ENOSPC` even after counters were partly initialized; callers must decide whether to continue or recover. Shrink paths must free and reinitialize reservations carefully.

## Test Signals
Relevant tests use reflink/rmapbt/finobt filesystems near ENOSPC, heavy CoW/refcount growth, rmap-heavy metadata updates, mount/unmount accounting comparisons, shrink/grow reservation reinit, error tag injection for reservation failure/critical paths, and xfstests that validate fdblocks stability after metadata btree expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.h

## Purpose
This header declares the per-AG reservation interface used by XFS allocation and metadata btree code. It exposes initialization, teardown, critical-space checks, needed-reservation calculation, allocation/free accounting, and a helper to select the reservation object inside `struct xfs_perag`.

## Important APIs
- `xfs_ag_resv_init` and `xfs_ag_resv_free` establish and tear down per-AG reservations.
- `xfs_ag_resv_critical` and `xfs_ag_resv_needed` provide reservation availability signals to allocation policy.
- `xfs_ag_resv_alloc_extent` and `xfs_ag_resv_free_extent` adjust reservation/global accounting as blocks are allocated or freed.
- `xfs_perag_resv` maps `XFS_AG_RESV_METADATA` and `XFS_AG_RESV_RMAPBT` to `pag_meta_resv` and `pag_rmapbt_resv`.

## Control Flow and Integration
Allocator paths include this header to query reservation pressure before allocation and to update accounting after extent allocation/free. Mount/grow/shrink paths include it to reset or reinitialize reservations around AG geometry changes.

## State and Persistence Behavior
The header exposes in-core reservation state only. The selected `struct xfs_ag_resv` fields are persisted only in memory and affect persistent superblock counters indirectly through transaction accounting.

## Dependencies and Risks
Callers must pass only supported reservation types to `xfs_perag_resv`; unsupported types return `NULL` and are guarded by assertions in the implementation. Misuse of reservation type can corrupt fdblocks accounting or allow metadata ENOSPC.

## Test Signals
Build coverage for all callers, assertion/error-path testing for invalid reservation types, and accounting tests for metadata and rmapbt reservations are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_ag_resv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.c

## Purpose
This file is the core XFS data-device free-space allocator. It manages AG free-space btrees, AGFL refill/drain, AGF/AGFL verification, extent allocation strategies, extent freeing and coalescing, reservation-aware accounting, busy extent avoidance, delayed frees, and allocator query helpers.

## Important APIs, Types, and Functions
- Geometry/accounting helpers: `xfs_agfl_size`, `xfs_refc_block`, `xfs_prealloc_blocks`, `xfs_alloc_set_aside`, `xfs_alloc_ag_max_usable`, `xfs_alloc_compute_maxlevels`, `xfs_alloc_longest_free_extent`, and `xfs_alloc_min_freelist`.
- Btree helpers: `xfs_alloc_lookup_{eq,ge,le}`, `xfs_alloc_update`, `xfs_alloc_btrec_to_irec`, `xfs_alloc_check_irec`, `xfs_alloc_get_rec`, `xfs_alloc_fixup_trees`, and longest-record maintenance.
- Allocation search structures/functions: `struct xfs_alloc_cur`, `xfs_alloc_cur_setup/check/finish/close`, `xfs_alloc_ag_vextent_exact`, `xfs_alloc_ag_vextent_near`, `xfs_alloc_ag_vextent_size`, and small/freelist fallback handling.
- Public allocation APIs: `xfs_alloc_vextent_this_ag`, `xfs_alloc_vextent_near_bno`, `xfs_alloc_vextent_exact_bno`, `xfs_alloc_vextent_start_ag`, and `xfs_alloc_vextent_first_ag`.
- Free path APIs: `xfs_free_ag_extent`, `__xfs_free_extent`, `xfs_free_extent_fix_freelist`, `xfs_free_extent_later`, and autoreap helpers.
- AGFL/AGF APIs: `xfs_alloc_fix_freelist`, `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`, `xfs_alloc_log_agf`, `xfs_read_agf`, `xfs_alloc_read_agf`, AGF/AGFL buffer ops and verifiers.
- Query helpers: `xfs_alloc_query_range`, `xfs_alloc_query_all`, `xfs_alloc_has_records`, and `xfs_agfl_walk`.

## Control Flow
Allocation begins by validating and normalizing `struct xfs_alloc_arg` in `xfs_alloc_vextent_check_args`, including transaction AG ordering constraints via `t_highest_agno`. The caller-specific wrapper prepares an AG with `xfs_alloc_vextent_prepare_ag`, which initializes/locks AGF state and calls `xfs_alloc_fix_freelist`. That function checks reservation-aware availability, resets corrupt AGFL indexes if needed, drains surplus AGFL blocks to deferred frees, and refills a short AGFL by allocating free-space extents and adding each block to the freelist.

Exact allocations search the bnobt for the containing free extent, trim busy ranges, and remove the requested range from both btrees. Near allocations run locality-aware parallel searches across cntbt and bnobt, retrying after busy-extent flushes when necessary. Anywhere allocations primarily search cntbt for the largest viable extent, scan for a better aligned candidate if needed, and fall back to small allocations or single AGFL blocks. Successful allocations update btrees, set `args->fsbno`, optionally add reverse mappings, decrement AGF/freeblock counters, debit reservations, and update stats.

Freeing fixes the freelist first, validates the extent against AGF length, optionally removes rmap ownership, finds left/right neighboring free extents in bnobt, coalesces with either or both neighbors, updates cntbt and bnobt, refreshes `agf_longest`, increments counters, replenishes reservations, and inserts a busy extent so recently freed blocks are not immediately reused unsafely.

## State and Persistence Behavior
Persistent state includes AGF fields, AGFL entries, bnobt/cntbt records, rmap records, transaction log items, deferred extent free intents, and buffer checksums/LSNs. In-core state includes perag cached freeblock/freelist/btree counters, btree levels, `m_allocbt_blks`, transaction highest-AG tracking, busy extent lists, allocator workqueue/cache state, and reservation counters. Deferred frees are persisted as EFI/EFD intent items so recovery can complete or cancel frees.

## Dependencies and Integration Points
The allocator integrates with XFS btree core, allocation btree ops, rmap updates, extent busy tracking, transactions and log item types, AG reservation code, AG/perag helpers, health/sick marking, buffer verifiers, error injection, tracepoints, deferred operation infrastructure, and slab caches for extent-free items. It is called by file block mapping, metadata allocation, grow/shrink, repair/scrub, and log recovery paths.

## Risks and Edge Cases
Primary risks are bnobt/cntbt divergence, stale `agf_longest`, AGFL count/index corruption, busy extent reuse races, transaction AG lock ordering deadlocks, incorrect reservation accounting, rmap update mismatches, and silent block-device write loss. The code has many corruption assertions and sick marking paths, but failure handling must preserve `NULLFSBLOCK` on allocation failure and release AGF/AGFL buffers correctly. AGFL reset intentionally leaks blocks to keep the filesystem online and requires repair.

## Test Signals
High-value tests include fragmented free-space allocation, exact/near/anywhere allocation with alignment/mod/prod constraints, delayed allocation under ENOSPC, AGFL refill/drain at low space, busy extent flush and retry, concurrent frees and allocations, reverse-map enabled filesystems, reflink/refcount pressure, transaction roll/deadlock avoidance across AGs, forced verifier failures, dmflakey stale AGF reads, EFI/EFD log recovery, discard skip paths, and scrub queries over free-space btrees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.h

## Purpose
This header declares the public and shared interfaces for XFS free-space allocation, freeing, AGFL manipulation, AGF reading/logging, allocator queries, deferred extent frees, and allocator work/cache lifecycle.

## Important Types, Flags, and APIs
- `struct xfs_alloc_arg` is the central allocation request/result object containing transaction, mount, AG/perag, target block, min/max length, alignment, locality bounds, reservation type, owner info, datatype flags, and outputs.
- Freelist flags include `TRYLOCK`, `FREEING`, `NORMAP`, `NOSHRINK`, `CHECK`, and `TRYFLUSH`.
- Datatype flags describe user data, initial user data, and no-busy constraints.
- Allocation entry points are `xfs_alloc_vextent_this_ag`, `near_bno`, `exact_bno`, `start_ag`, and `first_ag`.
- Freeing entry points include `__xfs_free_extent`, inline `xfs_free_extent`, `xfs_free_extent_later`, and `xfs_free_extent_fix_freelist`.
- AGF/AGFL functions include `xfs_alloc_read_agf`, `xfs_read_agf`, `xfs_alloc_read_agfl`, `xfs_alloc_fix_freelist`, `xfs_alloc_get_freelist`, `xfs_alloc_put_freelist`, and `xfs_alloc_log_agf`.
- Query and validation functions include `xfs_alloc_get_rec`, `xfs_alloc_check_irec`, `xfs_alloc_query_range`, `xfs_alloc_query_all`, `xfs_alloc_has_records`, `xfs_agfl_walk`, and `xfs_validate_ag_length`.
- `struct xfs_extent_free_item` records deferred free intent state, owner, block range, group, flags, and reservation type.
- Autoreap helpers schedule, cancel, or commit crash-recovery-backed freeing for newly allocated unwritten space.

## Control Flow and Integration
Callers populate `xfs_alloc_arg` and choose an allocation mode; the implementation validates, prepares an AG, allocates, updates rmap/accounting, and returns `fsbno/len` or `NULLFSBLOCK`. Free callers pass a perag plus AG-relative extent to `xfs_free_extent`, or schedule a deferred free through `xfs_free_extent_later`. Scrub/repair code uses query helpers and AGFL walking to inspect free-space state.

## State and Persistence Behavior
The header exposes interfaces that mutate AGF/AGFL/free-space btrees, rmap btrees, superblock counters, deferred intent log items, and in-core perag counters. `struct xfs_extent_free_item` is transient memory but represents work that can be logged as persistent EFI/EFD recovery state.

## Dependencies and Integration Points
It depends on transactions, btree cursors, perag references, owner info, reservation types, deferred ops, realtime/free flags, and buffer handling. It is included broadly by XFS bmap, inode, grow/shrink, scrub, repair, and log recovery code.

## Risks and Edge Cases
`xfs_alloc_arg` has many fields with mode-specific meaning; uninitialized alignment, min/max, reservation, or owner data can cause ENOSPC, corruption assertions, or rmap/accounting errors. Deferred free flags must distinguish realtime, discard skipping, attr fork, bmbt, and cancelled items correctly. Free extents must be AG-valid and non-null.

## Test Signals
Compile API consumers, allocation mode tests, deferred free recovery tests, rmap owner validation, realtime free flag handling, AGFL walk/query tests, and debug assertions for malformed `xfs_alloc_arg` fields are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.c -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.c

## Purpose
This file implements the XFS free-space btree operations for the by-block-number tree (bnobt) and by-count tree (cntbt). It defines cursor behavior, root updates, block allocation/free via the AGFL, key/record comparisons, verifiers, btree operation tables, staged-btree commit support, max record/level calculations, and cursor cache lifecycle.

## Important APIs and Functions
- Cursor constructors `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` allocate btree cursors, hold the perag group, attach AGF buffers, and set levels from AGF roots.
- `xfs_allocbt_set_root` updates AGF root/level fields and perag cached btree levels for either tree.
- `xfs_allocbt_alloc_block` gets new btree blocks from the AGFL, increments `m_allocbt_blks`, and marks busy extents reusable.
- `xfs_allocbt_free_block` returns btree blocks to the AGFL, decrements `m_allocbt_blks`, and records busy extents with discard skipped.
- Comparison helpers implement bnobt ordering by startblock and cntbt ordering by blockcount then startblock.
- `xfs_allocbt_verify`, read/write verifiers, and `xfs_bnobt_buf_ops`/`xfs_cntbt_buf_ops` validate magic, CRC, AG block headers, levels, and record capacity.
- `xfs_bnobt_ops` and `xfs_cntbt_ops` provide the generic btree core callbacks.
- `xfs_allocbt_commit_staged_btree` installs a rebuilt staged root into AGF and commits the fake root.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_maxlevels_ondisk`, `xfs_allocbt_calc_size`, and cursor cache init/destroy support geometry and memory sizing.

## Control Flow
Allocator code creates bnobt/cntbt cursors and uses generic btree operations through the callback tables. When the btree core splits or joins blocks, allocation and free callbacks move blocks to/from AGFL and update global in-core allocbt block counters. Root changes update both persistent AGF fields and perag cached levels. Verifiers run on buffer read/write to reject corrupt btree blocks before use or persistence.

## State and Persistence Behavior
Persistent state includes free-space btree blocks, AGF root pointers and levels, and buffer checksums. In-core state includes btree cursors, held perag group references, cached btree levels, and the mount-wide `m_allocbt_blks` counter. Staged btrees support online repair/rebuild before atomically installing new roots.

## Dependencies and Integration Points
This file integrates with the generic XFS btree engine, AGFL allocator functions in `xfs_alloc.c`, busy extent tracking, health/sick masks, tracepoints, online repair staging, buffer verification, and perag/group references.

## Risks and Edge Cases
Verifier level checks must tolerate growfs/log-recovery contexts where perag state is unavailable, and online repair contexts where alternate repair heights may be valid. Misordered keys or wrong high-key construction breaks allocation searches. AGFL allocation failure must return `stat = 0` rather than corrupting the tree. Incorrect root updates desynchronize AGF from perag caches.

## Test Signals
Tests should cover bnobt/cntbt cursor operations, btree split/join with AGFL pressure, online repair staged root commit, corrupt magic/CRC/level/order records, growfs initialization contexts without attached perag, allocator behavior after btree block reuse, and slab cache lifecycle at module init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.h -->
# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.h

## Purpose
This header declares on-disk layout helpers and public operations for XFS free-space allocation btrees. It abstracts record/key/pointer addressing inside bnobt/cntbt blocks and exposes cursor, staged commit, size, level, and cache lifecycle functions.

## Important APIs and Macros
- `XFS_ALLOC_BLOCK_LEN(mp)` selects short btree header size depending on CRC support.
- `XFS_ALLOC_REC_ADDR`, `XFS_ALLOC_KEY_ADDR`, and `XFS_ALLOC_PTR_ADDR` compute typed addresses inside allocation btree blocks.
- `xfs_bnobt_init_cursor` and `xfs_cntbt_init_cursor` create cursors for the by-block and by-count trees.
- `xfs_allocbt_maxrecs`, `xfs_allocbt_calc_size`, and `xfs_allocbt_maxlevels_ondisk` provide sizing/height calculations.
- `xfs_allocbt_commit_staged_btree` installs a staged rebuilt btree root.
- `xfs_allocbt_init_cur_cache` and `xfs_allocbt_destroy_cur_cache` manage cursor slab cache state.

## Control Flow and Integration
Allocator and repair code include this header to navigate btree blocks and construct cursors. The address macros are used by both kernel and userspace libxfs-style code, which is why some macros may appear unused in this kernel subset.

## State and Persistence Behavior
The macros directly address persistent on-disk btree records, keys, and pointers in buffers. The function declarations expose operations that mutate AGF roots and btree blocks through transactions.

## Dependencies and Risks
Correct header-length selection is essential: CRC-enabled and non-CRC formats have different btree headers. Off-by-one index handling in address macros would corrupt btree records. Staged commit callers must invalidate/free old btree blocks separately as documented in the implementation.

## Test Signals
Signals include btree record/key/pointer layout tests for CRC and non-CRC filesystems, cursor construction tests, online repair staged btree commits, max-level sizing checks, and userspace libxfs build coverage for the address macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_alloc_btree.h -->
