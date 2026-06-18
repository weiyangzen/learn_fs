# Research Group subset-b-005800

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.c

Purpose: Implements the main XFS quota manager for mount-time quota initialization, dquot cache lifecycle, quota inode creation/loading, quotacheck rebuilding, and inode-level quota attachment helpers. It is compiled behind quota support and sits between mount/VFS operations, transaction quota accounting, dquot buffers, inode walks, and metadata-directory quota files.

Important APIs and functions: `xfs_qm_mount_quotas` initializes `m_quotainfo`, loads or creates user/group/project quota inodes, runs quotacheck when `XFS_QM_NEED_QUOTACHECK` is true, and syncs superblock quota flags. `xfs_qm_unmount`, `xfs_qm_unmount_quotas`, and `xfs_qm_destroy_quotainfo` tear down cached dquots, quota inodes, LRU state, locks, and shrinkers. `xfs_qm_dqattach_locked`, `xfs_qm_dqattach`, and `xfs_qm_dqdetach` attach/release inode dquot references. `xfs_qm_vop_dqalloc`, `xfs_qm_vop_chown`, `xfs_qm_vop_rename_dqattach`, and `xfs_qm_vop_create_dqattach` are vnode-operation helpers used by create, rename, and ownership changes. `xfs_inode_near_dquot_enforcement` answers preallocation throttling decisions near quota limits.

Control flow: Mount quota startup validates realtime quota support, allocates `struct xfs_quotainfo`, initializes quota inodes via legacy superblock fields or metadata directory files, initializes default limits from id-zero dquots, registers the dquot shrinker, and optionally invokes quotacheck. Quotacheck resets all on-disk dquot counters by scanning quota inode extents, walks all filesystem inodes with `xfs_iwalk_threaded`, charges blocks/inodes/realtime blocks to uncached or cached dquots, flushes dirty dquot buffers through delayed write lists, then marks `m_qflags` as checked. Error paths purge partially cached dquots, flush inodegc before destroying `m_quotainfo`, reset superblock quota flags, and mark quota health sick.

State and persistence: Persistent state lives in quota inodes, dquot buffers, superblock quota inode/qflag fields, and optional metadir quota files. In-core state is `mp->m_quotainfo`, radix trees per dquot type, dquot LRU, default quota limits, expiry ranges, and inode `i_udquot/i_gdquot/i_pdquot` references. Dquot purge uses lockref death marking, AIL/pin checks, dirty flushes, radix tree deletion, and LRU removal. The shrinker reclaims clean unused dquots only under `__GFP_FS|__GFP_DIRECT_RECLAIM`.

Dependencies and integration: Depends on dquot core helpers, transaction reservations, inode walks, bmap extent reads, buffer verification, XFS health reporting, metadata directory helpers, realtime groups, inodegc, and quota macros from `xfs_quota.h`. It exposes services consumed by VFS operations, quota syscalls, transaction quota code, and realtime mount teardown. Online repair hooks are initialized in `qi_mod_ino_dqtrx_hooks` and `qi_apply_dqtrx_hooks`.

Risks and invariants: Quotacheck assumes mount-time single-threaded conditions for quota inode extent scanning and quotaoff exclusion. The V4 group/project shared quota inode conversion has corruption checks for impossible superblock combinations. Realtime quotas are disabled unless rtgroups are enabled and zoned mode is not active. Dquot purge/reclaim must not free dirty, pinned, referenced, dead, or AIL-resident dquots. Metadata directory quota inodes must not be charged to user-visible quotas.

Test signals: Exercise mount with quota flags requiring quotacheck, metadir and non-metadir quota inode creation, V4 gquota/pquota switch cases, forced dquot buffer corruption repair during quotacheck, quotaoff/unmount purge under dirty dquots, inode create/chown/rename quota accounting, realtime quota rejection without rtgroups, and shrinker reclaim of clean unused dquots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.h

Purpose: Defines the quota manager's in-core data structures, default limit containers, transaction dquot accounting layout, and function prototypes shared by quota manager implementation, syscall wrappers, and transaction code.

Important APIs and types: `struct xfs_quotainfo` is the central per-mount quota state, containing user/group/project dquot radix trees, quota inode pointers, optional quota directory inode, dquot LRU, quotaoff mutex, dquot chunk geometry, default quota limits, shrinker, expiry range, and live hook lists. `struct xfs_quota_limits` and `struct xfs_def_quota` model default hard/soft/time values for block, inode, and realtime block resources. `struct xfs_dquot_acct` stores transaction dquot deltas across user/group/project classes and up to `XFS_QM_TRANS_MAXDQS` entries each. Inline helpers `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` route by `xfs_dqtype_t`.

Control flow and integration: This header is included by quota manager, quota syscall, quotactl, and transaction accounting paths. The exported syscall prototypes (`xfs_qm_scall_*`) are implemented in `xfs_qm_syscalls.c` and surfaced through `xfs_quotaops.c`. The transaction prototypes connect to dquot log item handling and commit-time quota delta application. `xfs_qm_qino_load` gives other quota front ends a safe quota inode loader.

State and persistence: The header itself stores no state, but describes state whose persistent backing is quota inodes, dquot buffers, and superblock quota fields. `qi_dqchunklen` and `qi_dqperchunk` encode on-disk dquot clustering assumptions used during dquot iteration and quotacheck. Expiry bounds differ for bigtime versus legacy filesystems.

Dependencies and integration points: Depends on dquot and dquot log-item definitions. Consumers must hold the right locks around radix tree, dquot, inode, and quotaoff operations; the header's inline selectors do not synchronize. Live hook fields are used by online repair or hook users to observe quota transaction changes.

Risks and invariants: `xfs_dquot_tree`, `xfs_quota_inode`, and `xfs_get_defquota` assert on invalid quota types and return `NULL` only as an impossible fallback. `XFS_DQITER_MAP_SIZE` intentionally limits quotacheck bmap memory. `XFS_IS_DQUOT_UNINITIALIZED` defines when quota reporting treats a dquot as nonexistent, so changes to dquot resource fields can alter user-visible `ENOENT` behavior.

Test signals: Build coverage with and without quota/live-hook configuration, mount quota initialization checking `qi_dqperchunk`, quota report behavior for zeroed dquots, and transaction tests with more than one dquot of each class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_bhv.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_bhv.c

Purpose: Provides quota-related mount behavior helpers outside the core quota manager: quota-aware `statvfs`, mount-time quota state validation, early quota mounting/deferment, and metadir quota state resume.

Important APIs and functions: `xfs_qm_statvfs` reports project-quota-limited filesystem statistics for project quota directory trees. `xfs_qm_newmount` reconciles mount options and on-disk quota accounting/enforcement flags, decides whether quotas must be mounted immediately or deferred until after log recovery, and rejects forbidden read-only/norecovery state changes. `xfs_qm_resume_quotaon` restores metadir quota accounting/enforcement state from the superblock when no quota mount options were supplied. Internal `xfs_fill_statvfs_from_dquot` clamps block and inode totals/free counts to quota limits.

Control flow: During mount, `xfs_qm_newmount` reads on-disk quota flags, checks whether requested in-core state would change quota accounting/enforcement on read-only or norecovery mounts, then either calls `xfs_qm_mount_quotas` immediately when no quotacheck is needed or clears `m_qflags` while returning the saved flags through `needquotamount/quotaflags`. For `statvfs`, the helper gets the project dquot, locks it, and uses soft limits preferentially over hard limits to clamp `kstatfs`.

State and persistence: Reads persistent superblock `sb_qflags` and quota inode state. Mutates only in-core mount quota flags during mount deferment/resume; persistent changes are handled by the main quota manager. `statvfs` uses reserved counts, not merely committed counts, so delayed allocations affect reported free space.

Dependencies and integration: Integrates with the VFS statfs path, mount path, dquot lookup, quota default limit structures, readonly/norecovery checks, metadir feature flags, and `xfs_qm_mount_quotas`.

Risks and invariants: Read-only or norecovery mounts must not trigger quota state transactions; the function returns `-EPERM` if mount options would require a quota state change. Metadir filesystems prefer mount-without-quota-options behavior to restore persisted quota state. `xfs_qm_statvfs` silently falls back to global statfs if the project dquot cannot be obtained.

Test signals: Mount read-only/norecovery filesystems with matching and mismatching quota flags, metadir quota resume without mount options, deferred quotacheck mount path, and project-quota `df` output under block/inode soft and hard limits including realtime inherited trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_bhv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_syscalls.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_syscalls.c

Purpose: Implements XFS-internal quota syscall operations used by quotactl wrappers: turn enforcement on/off, truncate inactive quota files, set quota limits/timers, and fetch one or next quota record.

Important APIs and functions: `xfs_qm_scall_quotaoff` disables enforcement flags but intentionally no longer disables quota accounting. `xfs_qm_scall_quotaon` enables enforcement after verifying accounting is present. `xfs_qm_scall_trunc_qfiles` truncates selected quota inodes when quota is fully off. `xfs_qm_scall_setqlim` updates hard/soft limits and grace timers for a dquot, with id zero updating default limits. `xfs_qm_scall_getquota` and `xfs_qm_scall_getquota_next` report quota usage/limits.

Control flow: Quotaoff validates existing flags, strips accounting bits from the request, serializes through `qi_quotaofflock`, updates `m_qflags` and `sb_qflags`, and syncs the superblock. Quotaon accepts enforcement bits only, verifies matching accounting in `sb_qflags`, updates `sb_qflags`, syncs the superblock, and then updates in-core `m_qflags` if quota accounting is also live. Setqlim obtains or allocates the target dquot, starts a quota-limit transaction, joins and locks the dquot, validates hard >= soft per resource, writes limits/timers/defaults, adjusts timers for nonzero ids, marks dirty, logs the dquot, and commits. Getquota pushes inodegc at scan start, gets a dquot without allocation, optionally returns configured defaults for missing nonzero dquots, and suppresses timers when enforcement is off.

State and persistence: Persists enforcement flags in the superblock, limit/timer updates in dquot buffers via transactions, and quota file truncation through inode extent truncation. Default limits are cached in `xfs_quotainfo` and backed by id-zero dquots. Reporting converts internal fsblock counts to byte counts and uses reserved usage.

Dependencies and integration: Called by `xfs_quotaops.c`, depends on dquot get/next, quota inode loading, transaction reservations, inode truncation, dquot logging, superblock sync, inodegc, and quota conversion macros. It enforces XFS behavior expected by quota utilities, including `-EEXIST` for no-op quotaoff/quotaon.

Risks and invariants: Accounting cannot be switched on/off here; mount-time is authoritative. Hard limits lower than soft limits are rejected per resource without rolling back unrelated accepted fields in the same call, so callers should inspect field masks carefully. Missing dquots can report defaults as zero-usage limits, which affects unprivileged visibility. Root filesystem accounting can exist on disk before `m_qflags` knows about it.

Test signals: quotactl enable/disable enforcement with and without accounting, setqlim for block/inode/realtime resources and id-zero defaults, invalid hard/soft pairs, getquota missing dquot with/without defaults, get_nextdqblk id advancement, truncation of user/group/project quota files only when quota is off, and superblock sync failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_qm_syscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_quota.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_quota.h

Purpose: Declares kernel-only quota macros, transaction quota delta structures, quota operation prototypes, and no-op stubs for builds without `CONFIG_XFS_QUOTA`.

Important APIs and types: `XFS_NOT_DQATTACHED` determines whether an inode lacks any active quota dquot references. `XFS_QM_NEED_QUOTACHECK` derives mount-time quotacheck need from active quota types and checked superblock flags. `struct xfs_dqtrx` accumulates per-transaction reservations and deltas for data blocks, realtime blocks, delayed blocks, and inode counts. `struct xfs_apply_dqtrx_params` and `struct xfs_mod_ino_dqtrx_params` describe live-hook notification payloads. The header exposes transaction reservation/application functions and vnode quota helpers.

Control flow and integration: Transaction code reserves quota through `xfs_trans_reserve_quota_*`, accumulates changes with `xfs_trans_mod_dquot_byino` or live-hook-aware `xfs_trans_mod_ino_dquot`, and applies or unreserves changes during commit/cancel. Inode operations call dqalloc, create attach, rename attach, chown, attach/detach, and enforcement-near checks via this interface. Mount code uses newmount/resume/mount/unmount prototypes.

State and persistence: The header defines in-memory transaction accumulation; persistence occurs when dquot log items are joined/logged elsewhere. Deltas distinguish reserved versus used quota so delayed allocation and realtime reservations can be accounted correctly.

Dependencies and integration points: Integrates with `xfs_dquot`, `xfs_trans`, inode code, VFS quota operations, live hooks, and build configuration. Without quota support, most functions compile to no-ops or successful stubs while `xfs_rtmount_init`-style callers still get predictable behavior.

Risks and invariants: `XFS_NOT_DQATTACHED` is intentionally used without inode locks in some contexts and relies on inode references plus atomic ownership updates to be harmless. Stub behavior in nonquota builds must preserve call-site assumptions by nulling dquot outputs and returning success. The transaction dquot arrays assume no transaction affects more than `XFS_QM_TRANS_MAXDQS` dquots per type.

Test signals: Compile both quota and nonquota configurations, run delayed allocation quota reservation/rollback tests, verify quotacheck flag detection per quota type, exercise live hook enable/disable if configured, and check callers tolerate no-op stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_quotaops.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_quotaops.c

Purpose: Bridges Linux VFS `quotactl_ops` to XFS quota syscall helpers and maps generic quota ids, flags, state, limits, and timers into XFS quota types and flags.

Important APIs and functions: Exports `const struct quotactl_ops xfs_quotactl_operations`. `xfs_fs_get_quota_state` fills `qc_state`, per-type flags, quota inode numbers, quota file sizes/extents, default timers, and in-core dquot counts. `xfs_fs_set_info` updates default timers through id-zero setqlim. `xfs_quota_enable` and `xfs_quota_disable` translate generic FS quota flags to XFS flags. `xfs_fs_rm_xquota` truncates inactive quota files. `xfs_fs_get_dqblk`, `xfs_fs_get_nextdqblk`, and `xfs_fs_set_dqblk` wrap dquot report/update operations.

Control flow: VFS quotactl calls enter this table. Each mutating operation rejects read-only superblocks and requires active quota state where appropriate. Type conversion maps `USRQUOTA`, `GRPQUOTA`, and default/project to `XFS_DQTYPE_*`. State queries call `xfs_qm_fill_state` for all three types; absent quota inodes are reported as `NULLFSINO`, while errors other than `-ENOENT` propagate.

State and persistence: This file does not directly persist data; it reports state from `m_quotainfo`, quota inodes, and `m_qflags`, and delegates persistence to `xfs_qm_scall_*`. It converts ids through kernel quota namespace helpers and converts returned ids from get-next back into the current user namespace.

Dependencies and integration: Depends on VFS quota infrastructure, user namespace id conversion, quota manager syscall helpers, quota inode loading, and read-only checks. It is the user-visible quotactl integration point for XFS.

Risks and invariants: `xfs_quota_type` maps any non-user/non-group type to project quota, so callers must validate generic types before reaching unexpected values. `rm_xquota` requires quota to be off, while enable/disable require quota to be on. State reporting loads quota inodes each time and can surface metadata errors.

Test signals: Run generic quota ioctl/quotactl tests for state, set_info timer changes, enable/disable enforcement, get/set dqblk, get-next id conversion, read-only rejection, and rm_xquota behavior when quotas are active versus inactive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_quotaops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.c

Purpose: Implements refcount btree deferred update log items: CUI intent items and CUD done items for data-device and realtime refcount operations. These items make refcount updates recoverable across rolled transactions and crashes.

Important APIs and functions: `xfs_refcount_defer_add` attaches a `struct xfs_refcount_intent` to the deferred operation system and selects data versus realtime defer types. `xfs_cui_log_space` and `xfs_cud_log_space` expose reservation sizing. Internal CUI/CUD item ops format, unpin, release, match, and identify intent-done relationships. `xfs_refcount_update_defer_type` and `xfs_rtrefcount_update_defer_type` provide create intent, create done, finish item, cleanup, cancel, recover, and relog callbacks.

Control flow: Deferred refcount callers allocate intents and call `xfs_refcount_defer_add`, which pins the target AG or RT group and queues the correct defer type. Intent creation optionally sorts by group, allocates a CUI with a fast cache or dynamic allocation, and encodes each operation into `xfs_phys_extent` flags. Finish callbacks call `xfs_refcount_finish_one` or `xfs_rtrefcount_finish_one`; if reservation is exhausted and blockcount remains, they return `-EAGAIN` to requeue. Done item creation creates a CUD referencing the CUI id, and release drops the CUI reference.

State and persistence: Persistent redo state is the logged CUI format containing startblock, length, and operation type; logged CUD records completion by CUI id. In-core CUI reference counts handle log and done-item lifetimes and AIL removal. Recovery reconstructs CUIs from log records, validates feature flags and extent ranges, rebuilds deferred intents, allocates a recovery transaction, finishes the intent, and captures remaining deferred work.

Dependencies and integration: Integrates with xfs_defer, xfs_log_item, AIL, log recovery, refcount btree code, realtime groups, transaction reservations, group intent references, tracepoints, and corruption reporting. Realtime support is conditional; without `CONFIG_XFS_RT`, realtime CUI/CUD recovery reports corruption for those item types.

Risks and invariants: CUI extent counts must be fully populated before formatting. Recovered records are rejected if reflink is disabled, flags are invalid, operation type is unknown, or data/realtime extents fail verification. Data and realtime updates are deliberately separated to avoid mixing RT metadata file locks and AGF locks in one deferred finish transaction. Reference counting must tolerate CUD processing racing AIL insertion order.

Test signals: Crash-recovery tests for refcount increase/decrease and COW alloc/free across transaction rolls, malformed CUI/CUD log record size and flags, realtime CUI/CUD recovery with and without RT support, reservation exhaustion requeue, AIL release ordering, and group reference cleanup on cancel/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.h

Purpose: Declares the in-core CUI/CUD log item structures and public helpers for deferred refcount update logging.

Important APIs and types: `struct xfs_cui_log_item` wraps a generic log item, CUI reference count, next extent index, and variable-sized `xfs_cui_log_format`. `struct xfs_cud_log_item` wraps a done log item, pointer to the associated CUI, and `xfs_cud_log_format`. `XFS_CUI_MAX_FAST_EXTENTS` controls cache-backed versus dynamic allocation. `xfs_cui_log_item_sizeof` computes allocation size for variable extent counts. Public functions include `xfs_refcount_defer_add`, `xfs_cui_log_space`, and `xfs_cud_log_space`.

Control flow and integration: Refcount users allocate an `xfs_refcount_intent` and add it through `xfs_refcount_defer_add`; the implementation creates CUI/CUD log items as part of deferred transaction processing. Log reservation code calls the log-space helpers. The structures mirror on-disk log formats defined in log format headers.

State and persistence: CUI stores redo intent state until matching CUD completion releases it. The header defines only in-core wrappers; persistence is performed by item formatting in `xfs_refcount_item.c`.

Dependencies and integration points: Depends on `xfs_log_item`, `xfs_cui_log_format`, `xfs_cud_log_format`, dyanmic-sized log formats, and slab caches created elsewhere. It is used by reflink, COW, and refcount btree update paths.

Risks and invariants: The fast-extent threshold must stay compatible with the cache object size. CUI/CUD lifetime is tied to reference counts and log recovery, so structure changes require matching format, recovery, and reservation updates. The header comment states the core crash invariant: intent in the first rolled transaction, done item in the transaction that performs refcountbt updates.

Test signals: Build-time structure sizing, log reservation calculations for extent counts above and below the fast path, and crash tests proving CUI without CUD replays while CUD cancels the intent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_refcount_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.c

Purpose: Implements XFS reflink and copy-on-write behavior: detecting shared extents, staging writes in the COW fork, completing COW remaps, recovering orphan COW extents, cloning/remapping file ranges, clearing reflink flags, and unsharing.

Important APIs and functions: Shared extent queries are `xfs_reflink_trim_around_shared`, `xfs_bmap_trim_cow`, and `xfs_reflink_inode_has_shared_extents`. COW allocation/completion APIs include `xfs_reflink_allocate_cow`, `xfs_reflink_convert_cow`, `xfs_reflink_cancel_cow_blocks/range`, `xfs_reflink_end_cow`, `xfs_reflink_end_atomic_cow`, `xfs_reflink_max_atomic_cow`, and `xfs_reflink_recover_cow`. Clone/remap APIs include `xfs_reflink_remap_prep`, `xfs_reflink_remap_blocks`, and `xfs_reflink_update_dest`. Maintenance APIs include `xfs_reflink_clear_inode_flag`, `xfs_reflink_unshare`, and `xfs_reflink_supports_rextsize`.

Control flow: Write preparation trims mappings around shared refcount records, initializes the COW fork, finds existing COW reservations, allocates unwritten COW extents for shared regions, and optionally converts them to written for direct I/O. IO completion walks written COW fork extents, unmaps overlapping data fork storage or delalloc reservations, decreases old refcounts, frees COW orphan records, maps the new blocks into the data fork, updates quota deltas, deletes COW fork mappings, and commits per extent or all-at-once for atomic COW. Clone/remap prep locks both inodes against IO/mmap, validates realtime/DAX compatibility, flushes and unmaps destination ranges, attaches destination dquots, zeros post-EOF gaps, sets reflink flags, then remaps source extents into the destination one extent at a time.

State and persistence: Persistent state includes data fork mappings, COW fork mappings, inode `XFS_DIFLAG2_REFLINK` and COW extent-size hint flags, refcount btree records, COW orphan records, file sizes, and quota counters. In-core COW fork state and cowblocks inode tags drive cleanup. Recovery scans all AGs and RT groups for leftover COW staging records and frees them after ensuring no live cached inodes can still own them.

Dependencies and integration: Depends on bmap, refcount btrees, realtime refcount btrees, transaction reservations, quota accounting, iomap/DAX unshare, generic remap preparation, inode lock ordering, AG/RT group reservation checks, metadata reservations, and health marking. It consumes refcount deferred updates and interacts with `xfs_rtalloc` through realtime extent-size constraints.

Risks and invariants: XFS does not share partial blocks; remap prep rejects stale-data exposure around partial EOF blocks. Data and realtime files cannot be reflinked together, and DAX/non-DAX cannot be mixed. COW fork cleanup is unsafe while dirty pages, writeback, or direct I/O are active. Remapping identical physical extents with different written/unwritten states is treated as corruption. Realtime reflink requires rtgroups and `rextsize == 1`.

Test signals: Buffered and direct COW writes to shared extents, overlapping AIO completions, COW cancellation for truncate/error paths, atomic write max and end-atomic behavior, clone/dedupe EOF partial block cases, quota deltas during remap and COW completion, COW orphan recovery after crash, reflink flag clearing after unshare, realtime reflink with valid/invalid extent size, and DAX remap prep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.h

Purpose: Declares reflink/COW public interfaces and the safety predicate for freeing COW fork blocks.

Important APIs and functions: `xfs_can_free_cowblocks` checks dirty page, writeback, and direct-I/O state before COW fork cleanup. The header exposes sharedness trimming, COW allocation/conversion/cancel/end/recovery, remap prep/blocks/update, reflink flag scans/clears, unshare, realtime extent-size support, and max software atomic COW sizing.

Control flow and integration: Write paths call trim/allocation/conversion APIs; IO completion calls end-COW APIs; remap ioctls call prep, blocks, and update-dest; truncate/inactivation/error paths call cancel; mount recovery calls recover; maintenance paths call shared extent scans and clear flag helpers. The prototypes coordinate callers from iomap, bmap, file remap, inode cleanup, and mount recovery code.

State and persistence: The header manages no state directly. `xfs_can_free_cowblocks` reads VFS inode dirty/writeback/direct-I/O state, because persistent COW fork cleanup must not race outstanding writes that may target COW staging blocks.

Dependencies and integration points: Depends on `struct xfs_inode`, `xfs_bmbt_irec`, `xfs_trans`, VFS `struct file`, page cache tags, and atomic direct-I/O counters. It is only correct when callers hold the locking documented by the implementation.

Risks and invariants: COW cleanup requires no dirty cache, no writeback, and no direct I/O. Function declarations expose both byte-range and fsblock-range variants; callers must supply correctly converted ranges and hold expected locks. Realtime reflink constraints are centralized in `xfs_reflink_supports_rextsize`.

Test signals: Compile/link coverage from writeback, direct I/O, remap, truncate, recovery, and realtime grow paths; unit-style checks for `xfs_can_free_cowblocks` under dirty/writeback/dio states; and API misuse tests around range conversion boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.c

Purpose: Implements reverse-mapping btree deferred update log items: RUI intent items and RUD done items for data-device and realtime rmap updates. It provides crash-recoverable redo for map, unmap, convert, alloc, and free operations.

Important APIs and functions: `xfs_rmap_defer_add` queues an `xfs_rmap_intent` to data or realtime defer types. `xfs_rui_log_space` and `xfs_rud_log_space` size log reservations. Internal item ops allocate, format, release, match, relog, and recover RUI/RUD items. `xfs_rmap_update_defer_type` and `xfs_rtrmap_update_defer_type` plug into the generic deferred operation system.

Control flow: Rmap callers create intents with owner, fork, extent, state, and operation type. Defer-add grabs the AG or RT group intent reference and queues the proper defer type. Intent creation optionally sorts by group and encodes each operation into `xfs_map_extent` owner/startoff/startblock/length/flags. Finish calls `xfs_rmap_finish_one`, then cancels the item. Recovery validates logged RUI records, reconstructs `xfs_rmap_intent` objects, allocates a transaction with rmap btree reservation, finishes the intents, captures remaining deferred work, or reports corruption.

State and persistence: Persistent redo state is the logged RUI format; completion is a logged RUD referencing the RUI id. In-core RUI reference counts coordinate log and done lifetimes, including AIL deletion. Recovered map records restore owner, fork, unwritten state, physical range, and logical offset into deferred work.

Dependencies and integration: Integrates with xfs_defer, xfs_log_item, AIL, log recovery, rmap btrees, realtime groups, btree cursors, transaction reservations, group intent refs, and corruption reporting. It participates in allocator/bmap/refcount operations that must keep reverse mappings consistent.

Risks and invariants: Recovery rejects RUI records when rmapbt is disabled, flags are invalid, owner inode is invalid, file extent range is invalid, or physical data/realtime extent is invalid. Data and realtime rmap updates are separated to avoid incompatible lock mixing. Without RT support, realtime RUI/RUD records are corruption. RUD log record size must exactly match the format.

Test signals: Crash recovery of map/unmap/convert/alloc/free intents, shared and unwritten flag combinations, malformed log formats and invalid owners, RT rmap recovery with RT enabled/disabled, relogging of long-running intents, and group reference release on cancel/error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.h

Purpose: Declares in-core RUI/RUD log item structures and public helpers for deferred reverse-mapping updates.

Important APIs and types: `struct xfs_rui_log_item` contains the generic log item, RUI reference count, next extent index, and variable-sized `xfs_rui_log_format`. `struct xfs_rud_log_item` contains the done log item, pointer to the related RUI, and `xfs_rud_log_format`. `XFS_RUI_MAX_FAST_EXTENTS` controls the slab-cache fast path. `xfs_rui_log_item_sizeof` computes variable allocation size. Public functions are `xfs_rmap_defer_add`, `xfs_rui_log_space`, and `xfs_rud_log_space`.

Control flow and integration: Rmap update producers queue `xfs_rmap_intent` work through `xfs_rmap_defer_add`; deferred operation code creates RUI/RUD items, and log recovery can replay unresolved RUIs. The comment documents the transaction ordering: intent in the first transaction, done item in the transaction that performs rmapbt updates, with possible bnobt/cntbt updates later.

State and persistence: The structures wrap log-format records that persist redo and done state. In-core reference counts protect an RUI until both log and done processing release it.

Dependencies and integration points: Depends on log item infrastructure, rmap log format definitions, and kmem caches. Used by allocation, bmap, refcount, and recovery code that changes reverse mappings.

Risks and invariants: Structure sizing must match log format sizing for arbitrary extent counts. The fast extent threshold must match cache allocation expectations. Any semantic change to rmap extent flags or owner encoding requires coordinated recovery validation updates.

Test signals: Log-space reservation calculations, RUI/RUD size checks, crash replay of unresolved RUI, cancellation by RUD, and compile/link checks for data and realtime builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rmap_item.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.c -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.c

Purpose: Implements XFS realtime device allocation, realtime bitmap/summary maintenance, realtime group mount/unmount, growfs for realtime volumes, free-extent counter rebuild, and bmap allocation integration.

Important APIs and functions: Allocation internals include `xfs_rtany_summary`, `xfs_rtallocate_range`, `xfs_rtallocate_extent_block/exact/near/size`, `xfs_rtallocate_rtgs`, and `xfs_bmap_rtalloc`. Grow/mount APIs include `xfs_growfs_rt`, `xfs_growfs_check_rtgeom`, `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, `xfs_rtunmount_inodes`, and `xfs_rtalloc_reinit_frextents`. Helpers manage rsum caches, rtgroup metadata inodes, realtime superblock initialization, zoned grow, and busy extent trimming.

Control flow: Realtime allocation aligns requested file offsets/lengths to realtime extent size and extent-size hints, computes min/max rtextents and product alignment, picks a locality hint from adjacent bmap state or bitmap inode sequence for initial files, scans summaries for free extents near or by size, trims against busy extents for rtgroups, marks the chosen range allocated in bitmap and summary, updates free extent counters, and accounts the bmap allocation. If aligned allocation fails, `xfs_bmap_rtalloc` retries without extent-size-hint alignment before returning no-space as a zero-length allocation.

State and persistence: Persistent realtime state lives in the realtime bitmap and summary metadata inodes, optional realtime superblock, rtgroup metadata inodes, superblock realtime geometry (`sb_rblocks`, `sb_rextents`, `sb_rbmblocks`, `sb_rextslog`, `sb_rgcount`, `sb_frextents`), and realtime rmap/refcount metadata when enabled. In-core state includes per-rtgroup inodes, `rtg_rsum_cache`, mount rsum levels/blocks, btree maxlevels, and `m_rtgrotor`. The bitmap inode atime stores the pre-rtgroups allocation sequence for spreading initial file allocations.

Dependencies and integration: Depends on rtbitmap/summary helpers, bmap allocator, transaction reservations, quota reservation hooks, realtime groups, metadir rtgroup inodes, rmap/refcount btrees, reflink realtime constraints, zoned allocator, secondary superblock updates, metadata reservations, and buffer IO. `xfs_growfs_rt` integrates with capability checks and growlock serialization.

Risks and invariants: Realtime shrink is unsupported. Non-rtgroups realtime filesystems cannot combine realtime with rmapbt, quota, or reflink; reflink with rtgroups requires `rextsize == 1`. Summary copying during grow must avoid log overflow, hence `xfs_growfs_check_rtgeom`. Busy extent handling for rtgroups may flush the log and retry. Grow must keep bitmap/summary inode sizes, mount geometry, superblock counters, rtgroup geometry, rsum cache, and secondary superblocks consistent even on partial success. Zoned realtime has stricter alignment and separate availability accounting.

Test signals: Allocate near hints and by size across fragmented realtime bitmaps, alignment fallback for extent-size hints, busy extent trimming/flushing, rtgroup rotor allocation, grow from no realtime volume, grow last partial rtgroup and add new rtgroups, zoned grow alignment rejection, rsum cache invalidation, mount/unmount loading of rtgroup inodes, free extent counter rebuild, realtime superblock read/write, and feature rejection for quota/rmap/reflink without rtgroups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.h -->
## sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.h

Purpose: Declares realtime allocation, mount, grow, and geometry-check interfaces, with stubs for kernels built without `CONFIG_XFS_RT`.

Important APIs and functions: With realtime support, exports `xfs_rtmount_readsb`, `xfs_rtmount_freesb`, `xfs_rtmount_init`, `xfs_rtmount_inodes`, `xfs_rtunmount_inodes`, `xfs_growfs_rt`, `xfs_rtalloc_reinit_frextents`, `xfs_growfs_check_rtgeom`, and `xfs_rtallocate_rtgs`. Without realtime support, grow returns `-ENOSYS`, mount initialization returns `-ENOSYS` if the filesystem has realtime blocks, and most cleanup/count functions become no-ops.

Control flow and integration: Mount code calls read/init/inodes to attach realtime metadata. Grow ioctl paths call geometry check and grow. Bmap allocation can call `xfs_rtallocate_rtgs` for realtime block allocation. Unmount paths release metadata inodes and the realtime superblock through declared cleanup functions.

State and persistence: The header has no state, but the APIs manipulate realtime superblocks, rtgroup metadata inodes, bitmap/summary files, free extent counters, and superblock geometry. Stub behavior prevents accidentally mounting realtime filesystems without kernel support.

Dependencies and integration points: Depends on `struct xfs_mount`, `struct xfs_trans`, realtime growfs user input types, and transaction/bmap callers. The exported `xfs_rtallocate_rtgs` remains declared outside the `CONFIG_XFS_RT` block for allocator integration.

Risks and invariants: The non-RT stub macro for `xfs_rtmount_inodes` references `mp` rather than its parameter name `m`, which is notable for compile coverage depending on macro expansion context. Callers must handle `-ENOSYS` for unsupported realtime features and should not assume cleanup stubs perform work.

Test signals: Build with and without `CONFIG_XFS_RT`, mount a realtime filesystem on a non-RT build expecting rejection, growfs ioctl stubs, and compile coverage of the `xfs_rtmount_inodes` macro use sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/xfs_rtalloc.h -->
