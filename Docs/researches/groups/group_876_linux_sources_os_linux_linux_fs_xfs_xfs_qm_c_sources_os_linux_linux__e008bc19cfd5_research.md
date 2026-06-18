# Group Research: group_876_linux_sources_os_linux_linux_fs_xfs_xfs_qm_c_sources_os_linux_linux__e008bc19cfd5

Scope: `Docs/research_subset_a.md`, source tree `sources/os/linux/linux`.

This group covers XFS quota management, VFS quota operations, reflink copy-on-write mechanics, deferred refcount/rmap log intent items, and realtime allocation/grow/mount support.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_qm.c

## Role

Core XFS quota manager implementation. It owns per-mount quota initialization and teardown, dquot cache walking/reclaim, quotacheck rebuilding, quota inode creation/loading, inode dquot attachment, and vnode-operation helpers for create/chown/rename paths.

## Main Responsibilities

- Maintains dquot radix trees and LRU reclaim through `xfs_qm_dquot_walk`, `xfs_qm_dqpurge`, `xfs_qm_shrink_scan`, and `xfs_qm_dqfree_one`.
- Initializes `struct xfs_quotainfo` in `xfs_qm_init_quotainfo`, including quota inodes, radix trees, quota defaults, expiry ranges, shrinker, and live hooks.
- Supports both classic quota inode fields and metadata-directory quota inode layout via `xfs_qm_init_quotainos` and `xfs_qm_init_metadir_qinos`.
- Runs mount-time quotacheck in `xfs_qm_quotacheck`, resetting on-disk dquot counters, walking all inodes, adjusting dquot usage, flushing dirty dquot buffers, and marking quota health.
- Attaches and detaches user/group/project dquots to regular inodes with `xfs_qm_dqattach_locked`, `xfs_qm_dqattach`, and `xfs_qm_dqdetach`.
- Handles create/chown/rename quota transitions through `xfs_qm_vop_dqalloc`, `xfs_qm_vop_create_dqattach`, `xfs_qm_vop_chown`, and `xfs_qm_vop_rename_dqattach`.

## Important Flows

- Mount:
  `xfs_qm_mount_quotas` rejects unsupported realtime quota combinations, initializes quotainfo, runs quotacheck if needed, clears stale checked flags for disabled quota types, and writes superblock quota flags.
- Quotacheck:
  quota file counters are zeroed with `xfs_qm_reset_dqcounts_buf`; all non-quota, non-metadir inodes are visited by `xfs_iwalk_threaded`; dquot counters are rebuilt by `xfs_qm_quotacheck_dqadjust`; dirty dquots are flushed by `xfs_qm_flush_one`.
- Dquot reclaim:
  reclaim skips referenced, dead, dirty, pinned, or flush-locked dquots; removable dquots are marked dead, isolated from LRU, removed from radix trees, and destroyed.
- Quota inode creation:
  `xfs_qm_qino_alloc` handles legacy group/project quota inode sharing, optional superblock quota-version enablement, metadata inode tagging, and superblock qino updates.

## Locking and Consistency

- `qi_tree_lock` protects dquot radix tree iteration and deletion.
- `qi_quotaofflock` serializes quota-off/enforcement changes.
- Dquot purge coordinates `q_lockref`, `q_qlock`, pin waits, flush locks, AIL state, buffer attachment, and LRU deletion.
- Quotacheck is mount-time only and relies on single-threaded mount context for some otherwise racy-looking operations.
- Metadata directory inodes are excluded from user-visible quota accounting.

## Dependencies

Uses XFS inode walking, bmap, transaction, dquot, buffer, log, health, realtime group, and metadata inode APIs. Public declarations are split across `xfs_qm.h` and `xfs_quota.h`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_qm.h

## Role

Internal quota manager header. Defines quota defaults, per-mount quota manager state, transaction quota accounting containers, and syscall-level quota manager entry points.

## Main Contents

- `XFS_DQITER_MAP_SIZE`: limits bmap entries fetched while iterating quota file extents during quotacheck.
- `XFS_IS_DQUOT_UNINITIALIZED`: detects dquots with no limits and no usage.
- `struct xfs_quota_limits`: hard/soft defaults plus grace timer.
- `struct xfs_def_quota`: default block, inode, and realtime block quota limits per quota type.
- `struct xfs_quotainfo`: per-mount quota state containing dquot radix trees, quota inodes, quota metadir inode, dquot LRU, dquot counts, quotaoff mutex, dquot chunk geometry, defaults, shrinker, expiry range, and live quota hooks.
- `xfs_dquot_tree` and `xfs_quota_inode`: select per-type radix tree or quota inode.
- `struct xfs_mod_ino_dqtrx_params`: hook payload for quota transaction modifications.
- `struct xfs_dquot_acct`: per-transaction arrays of dquot changes for user/group/project quota types.
- Default grace periods: one week for block, realtime block, and inode soft-limit timers.

## Exported Interfaces

Declares internal quota transaction functions (`xfs_trans_mod_dquot`, `xfs_trans_dqjoin`, `xfs_trans_log_dquot`), syscall helpers (`xfs_qm_scall_*`), quotainfo destruction, default-quota lookup, and quota inode loading.

## Dependencies

Includes dquot log item and dquot definitions. Consumed mainly by quota manager implementation, quota syscalls, quota ops, and transaction quota accounting code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm_bhv.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_qm_bhv.c

## Role

Mount/statvfs behavior helpers for quotas. It translates project quota limits into statfs-style results and validates/restores quota state during mount.

## Main Responsibilities

- `xfs_fill_statvfs_from_dquot` clamps `kstatfs` block and inode totals/free counts to the applicable dquot hard or soft limits.
- `xfs_qm_statvfs` reports project-quota constrained `statvfs` for directory trees using inherited project IDs.
- `xfs_qm_validate_state_change` rejects quota state changes on read-only or norecovery mounts.
- `xfs_qm_newmount` reconciles requested mount quota flags with on-disk quota accounting flags, optionally mounts quotas immediately if no quotacheck is required, or defers quota mounting by clearing `m_qflags`.
- `xfs_qm_resume_quotaon` restores accounting/enforcement state from the superblock for metadata-directory filesystems when no quota mount options were supplied.

## Important Behavior

Project quota-backed directory trees are presented as filesystem-like accounting domains to `df`/`statfs`. Mounts that would require quota state mutations are rejected when transactions cannot safely be written.

## Dependencies

Uses mount flags, quota flags, dquot lookup, inode/project IDs, transactions indirectly through `xfs_qm_mount_quotas`, and generic `kstatfs`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm_bhv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm_syscalls.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_qm_syscalls.c

## Role

Implements XFS quota manager operations backing generic quotactl wrappers: enabling/disabling enforcement, truncating quota files, setting limits, and reading quota records.

## Main Responsibilities

- `xfs_qm_scall_quotaoff` disables quota enforcement bits in-core and on-disk, but deliberately does not support disabling quota accounting.
- `xfs_qm_scall_quotaon` enables enforcement after verifying accounting is already enabled.
- `xfs_qm_scall_trunc_qfiles` truncates selected quota files when quotas are fully off.
- `xfs_qm_scall_setqlim` updates block, realtime block, and inode hard/soft limits plus timers for one dquot; ID 0 updates default quota state.
- `xfs_qm_scall_getquota` reads one quota record, returning configured default limits with zero usage for missing nonzero IDs when appropriate.
- `xfs_qm_scall_getquota_next` scans to the next initialized dquot.
- Fill helpers convert internal filesystem-block units to byte-based `qc_dqblk` fields.

## Important Rules

- Limit updates reject hard limits lower than soft limits.
- Timer handling distinguishes default grace period updates for ID 0 from per-dquot grace expiration updates.
- Reporting hides timers when enforcement is disabled, even though internal timers continue to exist.
- Quota scans push inodegc at ID 0 to improve accounting freshness.

## Dependencies

Relies on dquot lookup/allocation, quota transactions, dquot logging, quota defaults from `xfs_quotainfo`, inodegc, superblock syncing, and quota inode loading/truncation.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_qm_syscalls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_quota.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_quota.h

## Role

Kernel-facing XFS quota interface header. Defines transaction quota accounting records, dquot attachment checks, quotacheck-needed checks, and CONFIG-dependent stubs.

## Main Contents

- `XFS_NOT_DQATTACHED`: tests whether an inode lacks any enabled quota dquot.
- `XFS_QM_NEED_QUOTACHECK`: checks superblock checked bits against enabled quota accounting.
- `xfs_quota_chkd_flag`: maps quota type to checked flag.
- `struct xfs_dqtrx`: per-dquot transaction deltas/reservations for data blocks, realtime blocks, delayed allocation, and inode counts.
- `enum xfs_apply_dqtrx_type` and `struct xfs_apply_dqtrx_params`: hook payloads for applying or unreserving transaction quota deltas.
- Public quota operation declarations when `CONFIG_XFS_QUOTA` is enabled.
- No-op stubs when quota support is disabled, allowing call sites to compile cleanly.
- `xfs_quota_unreserve_blkres`: small helper to return reserved quota blocks by applying a negative reservation.

## Live Hooks

When `CONFIG_XFS_LIVE_HOOKS` is enabled, declares hook setup/add/remove/enable/disable functions used by online repair to observe quota transaction deltas.

## Dependencies

Includes quota definitions and forward declarations for transactions and buffers. Used broadly across inode, transaction, bmap, reflink, and mount paths that need quota accounting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_quotaops.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_quotaops.c

## Role

Generic VFS `quotactl_ops` adapter for XFS. It maps Linux quota control operations and generic quota types/flags to XFS quota manager internals.

## Main Responsibilities

- `xfs_fs_get_quota_state` reports accounting/enforcement state, in-core dquot count, quota inode numbers, quota file blocks/extents, grace timers, and system-file flags.
- `xfs_fs_set_info` updates default quota timers through ID 0 `xfs_qm_scall_setqlim`.
- `xfs_quota_flags` maps `FS_QUOTA_*` flags to XFS `XFS_*QUOTA_*` flags.
- `xfs_quota_enable` and `xfs_quota_disable` wrap XFS enforcement transitions.
- `xfs_fs_rm_xquota` truncates quota files only when quotas are off.
- `xfs_fs_get_dqblk`, `xfs_fs_get_nextdqblk`, and `xfs_fs_set_dqblk` adapt generic `kqid` quota block calls to XFS dquot IDs and types.

## Important Behavior

The adapter performs read-only and quota-enabled checks before calling deeper quota manager functions. It uses `init_user_ns` for incoming quota IDs and converts returned scan IDs to the current user namespace.

## Exported Object

Defines `const struct quotactl_ops xfs_quotactl_operations`.

## Dependencies

Uses `xfs_qm.h`, `xfs_quota.h`, quota inode loading, dquot syscalls, and generic VFS quota structures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_quotaops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_refcount_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_refcount_item.c

## Role

Deferred log intent/done item implementation for refcount btree updates. It supports crash-recoverable refcount changes for reflink/CoW on data and realtime devices.

## Main Responsibilities

- Defines caches for CUI/CUD log items: `xfs_cui_cache`, `xfs_cud_cache`.
- Manages CUI lifecycle through allocation, formatting, unpin, release, AIL deletion, and variable-size freeing.
- Manages CUD lifecycle and links done items back to their CUI intent.
- Logs deferred refcount intents with `xfs_refcount_update_log_item`.
- Adds work to deferred operation queues through `xfs_refcount_defer_add`, splitting realtime and data-section work into separate defer types.
- Finishes deferred work using `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`.
- Recovers CUIs from log items, validates physical extents, rebuilds deferred work, allocates recovery transactions, and commits or captures remaining deferred work.
- Relogs intent items to advance the log tail.
- Provides recovery handlers for CUI/CUD and realtime CUI/CUD log item types.

## Important Types and Operations

- CUI: refcount update intent, containing one or more `xfs_phys_extent` entries.
- CUD: done item canceling a previous CUI by ID.
- Supported intent types include increase, decrease, alloc-COW, and free-COW.
- Realtime variants use `XFS_LI_CUI_RT` and `XFS_LI_CUD_RT`; if realtime support is not compiled in, recovered realtime items are treated as corruption.

## Consistency Checks

Recovery rejects CUIs if reflink is unavailable, flags are invalid, type bits are unknown, or extents fail data/realtime extent verification. On corruption, it reports with `XFS_CORRUPTION_ERROR`.

## Dependencies

Uses defer ops, transactions, log recovery, refcount btree helpers, AG/RT group abstractions, btree cursors, tracepoints, and realtime refcount support.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_refcount_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_refcount_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_refcount_item.h

## Role

Header for refcount update intent/done log items.

## Main Contents

- Documents CUI/CUD redo semantics for refcount btree updates across rolled transactions.
- `XFS_CUI_MAX_FAST_EXTENTS`: fast allocation threshold of 16 extents.
- `struct xfs_cui_log_item`: log item, reference count, next extent counter, and variable CUI format payload.
- `xfs_cui_log_item_sizeof`: computes dynamic CUI allocation size.
- `struct xfs_cud_log_item`: done log item linking to the original CUI plus CUD format.
- Extern declarations for CUI/CUD slab caches.
- Declaration for `xfs_refcount_defer_add`.
- Log space helpers `xfs_cui_log_space` and `xfs_cud_log_space`.

## Dependencies

Forward declares `xfs_mount`, `kmem_cache`, and `xfs_refcount_intent`. Implemented by `xfs_refcount_item.c` and consumed by refcount/reflink/defer/log code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_refcount_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_reflink.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_reflink.c

## Role

XFS reflink and copy-on-write implementation. It coordinates shared extent detection, CoW fork allocation/conversion/cancelation, IO completion remapping, range clone/remap, unshare, and reflink flag maintenance.

## Main Responsibilities

- Detects shared data or realtime extents via refcount btrees with `xfs_reflink_find_shared` and `xfs_reflink_find_rtshared`.
- Trims mappings around shared/unshared boundaries with `xfs_reflink_trim_around_shared` and `xfs_bmap_trim_cow`.
- Allocates or reuses CoW fork staging extents in `xfs_reflink_allocate_cow`, including delayed allocation conversion.
- Converts unwritten CoW fork extents to real extents before IO through `xfs_reflink_convert_cow_locked` and `xfs_reflink_convert_cow`.
- Cancels CoW reservations and frees orphan CoW extents with `xfs_reflink_cancel_cow_blocks` and `xfs_reflink_cancel_cow_range`.
- Completes CoW IO by remapping written CoW fork extents into the data fork using `xfs_reflink_end_cow` or one-transaction atomic mode `xfs_reflink_end_atomic_cow`.
- Computes maximum software atomic CoW size through `xfs_reflink_max_atomic_cow`.
- Recovers leftover CoW staging extents at mount with `xfs_reflink_recover_cow`.
- Implements file range remapping through `xfs_reflink_remap_prep`, `xfs_reflink_remap_blocks`, `xfs_reflink_remap_extent`, and `xfs_reflink_update_dest`.
- Maintains inode reflink flags and CoW fork state through `xfs_reflink_set_inode_flag`, `xfs_reflink_inode_has_shared_extents`, `xfs_reflink_clear_inode_flag`, and `xfs_reflink_unshare`.
- Validates realtime reflink support with `xfs_reflink_supports_rextsize`.

## Important Invariants

- Shared written blocks are never overwritten in place; writes allocate staging blocks in the CoW fork and remap after IO succeeds.
- CoW fork preallocation can be larger than the IO range due to `cowextsize`; remap completion only moves written real extents.
- Data and realtime file ranges cannot be reflinked to each other.
- DAX and non-DAX files cannot share data.
- Dedupe/clone handling rejects or trims partial EOF block cases that could expose stale data.
- Reflink on realtime requires rtgroups and realtime extent size of one filesystem block.
- Quota updates distinguish CoW delayed/reserved counts from real data or realtime block counts.

## Locking and Transactions

Range remap preparation takes IO and mmap locks on both files. CoW completion uses one transaction per remapped extent for normal IO and one larger transaction for atomic CoW. Destination remap transactions reserve bmbt and quota space conservatively, then refine after reading the existing destination mapping.

## Dependencies

Uses bmap, refcount, rmap-related reservations, quota, iomap, DAX, transactions, AG reservation, realtime groups/refcount btrees, metadir reservation, and inode/pagecache synchronization.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_reflink.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_reflink.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_reflink.h

## Role

Public internal header for XFS reflink/CoW helpers.

## Main Contents

- `xfs_can_free_cowblocks`: checks whether it is safe to discard CoW fork blocks by ensuring no dirty pages, writeback, or direct IO are active.
- Declarations for shared extent trimming, CoW allocation/conversion/cancelation, CoW completion, atomic CoW, CoW recovery, remap preparation/blocks/update, reflink flag clearing, unshare, realtime extent-size support, and maximum atomic CoW sizing.

## Important Contract

Callers must respect IO/pagecache safety before freeing CoW fork blocks. Many declarations assume inode locks or transaction joins are managed by the caller or described in the implementation comments.

## Dependencies

References XFS inodes, bmap records, transactions, files, offsets, and mount-level realtime/reflink capabilities.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_reflink.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rmap_item.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_rmap_item.c

## Role

Deferred log intent/done item implementation for reverse mapping btree updates. It makes rmap updates crash-recoverable across rolled transactions for both data and realtime metadata.

## Main Responsibilities

- Defines caches for RUI/RUD log items: `xfs_rui_cache`, `xfs_rud_cache`.
- Manages RUI lifecycle: allocation, formatting, unpin, release, AIL deletion, dynamic freeing.
- Manages RUD lifecycle and links done items back to original RUI intents.
- Encodes rmap operation details into `xfs_map_extent` fields in `xfs_rmap_update_log_item`.
- Adds deferred rmap work via `xfs_rmap_defer_add`, splitting realtime and data-section work into distinct defer types.
- Finishes deferred work through `xfs_rmap_finish_one`.
- Recovers RUIs by validating map records, rebuilding `xfs_rmap_intent` entries, allocating recovery transactions, and committing/capturing deferred work.
- Relogs old intent items to move the log tail.
- Provides recovery handlers for RUI/RUD and realtime RUI/RUD log records.

## Supported Rmap Intent Types

Map, map shared, unmap, unmap shared, convert, convert shared, alloc, and free. Flags also preserve unwritten state and attr-fork state.

## Consistency Checks

Recovery rejects RUIs if rmapbt is unavailable, flags are invalid, operation type is unknown, inode owners fail verification, file offsets are invalid, or data/realtime physical extents are invalid.

## Realtime Handling

Realtime rmap intents use `XFS_LI_RUI_RT` and `XFS_LI_RUD_RT`, and separate defer ops named `rtrmap`. If realtime support is disabled, recovered realtime intents are flagged as corruption.

## Dependencies

Uses defer ops, transaction/log recovery internals, rmap btree helpers, AG/RT group intent references, btree cursor cleanup, and tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rmap_item.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rmap_item.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_rmap_item.h

## Role

Header for reverse mapping update intent/done log items.

## Main Contents

- Documents RUI/RUD redo semantics for map, unmap, and convert rmapbt updates across rolled transactions.
- `XFS_RUI_MAX_FAST_EXTENTS`: fast allocation threshold of 16 extents.
- `struct xfs_rui_log_item`: log item, reference count, next extent counter, and variable RUI format payload.
- `xfs_rui_log_item_sizeof`: computes dynamic RUI allocation size.
- `struct xfs_rud_log_item`: done log item linking to original RUI plus RUD format.
- Extern declarations for RUI/RUD slab caches.
- Declaration for `xfs_rmap_defer_add`.
- Log space helpers `xfs_rui_log_space` and `xfs_rud_log_space`.

## Dependencies

Forward declares mount, slab cache, and rmap intent types. Implemented by `xfs_rmap_item.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rmap_item.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rtalloc.c -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_rtalloc.c

## Role

Realtime device allocation, mount, unmount, free-space recount, and growfs implementation for XFS. It handles legacy single realtime sections, rtgroups, zoned realtime behavior, realtime metadata inodes, bitmap/summary maintenance, and realtime bmap allocation.

## Main Responsibilities

- Allocation search:
  `xfs_rtany_summary`, `xfs_rtallocate_extent_block`, `xfs_rtallocate_extent_exact`, `xfs_rtallocate_extent_near`, `xfs_rtalloc_sumlevel`, and `xfs_rtallocate_extent_size` search realtime bitmap/summary metadata for free extents that satisfy min/max/alignment constraints.
- Allocation update:
  `xfs_rtallocate_range` marks extents allocated, updates summaries for split free extents, updates bitmap state, and decrements free realtime counters.
- Busy extent handling:
  `xfs_rtalloc_check_busy` and `xfs_rtallocate_adjust_for_busy` trim or wait on busy realtime extents for rtgroup filesystems.
- Realtime bmap allocation:
  `xfs_bmap_rtalloc` aligns allocation requests to realtime extent size and extent-size hints, picks locality hints, calls rtgroup allocation, retries without hint alignment on ENOSPC, and accounts allocation.
- Mount/unmount:
  `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, `xfs_rtmount_rtg`, and `xfs_rtunmount_inodes` attach realtime superblocks, load realtime metadata inodes, preload their extent maps, and manage summary caches.
- Growfs:
  `xfs_growfs_rt` validates permissions, rt device presence, geometry, feature constraints, log sizing, rtgroup setup, and grows existing/new realtime groups.
- Grow internals:
  fake mount geometry calculation, bitmap/summary file block initialization, summary copying, realtime superblock initialization, superblock field updates, new extent freeing, secondary superblock updates, and metadata reservation reset.
- Free extent recount:
  `xfs_rtalloc_reinit_frextents` scans all rtgroups and resets `sb_frextents`.

## Important Rules

- Realtime shrink is unsupported.
- Realtime extent size can only change when adding the realtime volume.
- Without rtgroups, realtime cannot be combined with rmapbt, quotas, or reflink.
- With reflink, realtime extent size must satisfy `xfs_reflink_supports_rextsize`.
- Zoned realtime grow requires extent size 1 and new size aligned to RT group size.
- Summary size must not exceed log constraints because grow can log large summary updates.
- For initial user data on pre-rtgroup filesystems, `xfs_rtpick_extent` spaces allocations using a sequence stored in the bitmap inode atime.

## Locking and Transactions

Realtime allocation locks bitmap metadata, delays joining rtgroup inodes until committed to an allocation for rtgroup filesystems, and joins bitmap/summary inodes earlier for legacy behavior. Growfs is serialized by `m_growlock`; rtgroup locks protect bitmap/rmap updates.

## Dependencies

Uses realtime bitmap/summary APIs, realtime group/inode APIs, bmap allocation, transactions, quotas, health/error handling, rmap/refcount realtime btrees, reflink support checks, zoned allocation, secondary superblock update, and metadata reservations.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rtalloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rtalloc.h -->
# File Research: sources/os/linux/linux/fs/xfs/xfs_rtalloc.h

## Role

Header for realtime allocation and grow/mount interfaces.

## Main Contents

When `CONFIG_XFS_RT` is enabled, declares:

- `xfs_rtmount_readsb` and `xfs_rtmount_freesb`.
- `xfs_rtmount_init`.
- `xfs_rtmount_inodes` and `xfs_rtunmount_inodes`.
- `xfs_growfs_rt`.
- `xfs_rtalloc_reinit_frextents`.
- `xfs_growfs_check_rtgeom`.

When realtime support is disabled, provides stubs returning success for no-RT cases or `-ENOSYS`/warnings for unsupported realtime mounts.

Always declares `xfs_rtallocate_rtgs`, the rtgroup allocation entry point used by bmap allocation.

## Important Note

The disabled-RT stub section contains a macro typo-like reference in `xfs_rtmount_inodes(m)` using `mp` instead of `m`; this is source as read and may be covered by build configuration paths elsewhere.

## Dependencies

Forward declares mount and transaction types and exposes realtime allocation types used by bmap and growfs code.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/xfs/xfs_rtalloc.h -->