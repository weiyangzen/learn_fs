# Group Research: group_1454_openzfs_sources_cow_pools_openzfs_module_zfs_zfs_quota_c_sources_co_b8c1bda52d5f

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_quota.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_quota.c

## Summary
Implements ZPL user, group, and project quota helpers. It translates znode/SA bonus data into DMU ownership accounting, enumerates quota ZAP objects, reads or writes per-id quotas, and checks whether block or object usage exceeds explicit or default quotas.

## Main Responsibilities
- Extract file accounting identity from old `DMU_OT_ZNODE` bonuses or modern `DMU_OT_SA` bonuses.
- Map `zfs_userquota_prop_t` values to the backing DMU/ZAP objects.
- Enumerate many user/group/project usage or quota records with serialized ZAP cursors.
- Look up one user/group/project usage or quota value.
- Set per-user, per-group, or per-project block and object quotas.
- Enforce block and object quotas for writes, clones, rewrites, and object creation paths.

## Key APIs
- `zpl_get_file_info()`.
- `zfs_userspace_many()`, `zfs_userspace_one()`.
- `zfs_set_userquota()`.
- `zfs_id_overblockquota()`, `zfs_id_overobjquota()`, `zfs_id_overquota()`.

## Important Behavior
`zpl_get_file_info()` is the low-level DMU accounting parser. For legacy znodes it reads uid, gid, and generation from `znode_phys_t`; for SA bonuses it validates SA magic/header size, handles byte-swapped headers, reads fixed SA offsets for uid/gid/generation/flags, and uses `ZFS_DEFAULT_PROJID` unless the `ZFS_PROJID` flag is present.

Quota enumeration requires the relevant feature to be present: userspace accounting, user object accounting, or project quota accounting. Object-usage properties use the `DMU_OBJACCT_PREFIX` namespace and skip entries from the opposite quota type.

`zfs_set_userquota()` creates the quota ZAP object lazily, records it in the master node, handles FUID dirty state, removes entries for zero quotas, and updates entries for nonzero quotas.

The over-quota checks use explicit quota objects first and fall back to dataset default quota fields. They skip enforcement during ZIL replay and trigger quota accounting upgrades when the objset is upgradable but not yet present.

## Dependencies
Depends on DMU objset quota feature probes and upgrades, ZAP lookup/update/cursor APIs, FUID string conversion, project-id validation, and `zfsvfs_t` cached quota object/default fields.

## Risks
The SA parsing path assumes current fixed offsets for ZPL SA attributes, so it depends on the SA layout contract staying compatible. Enforcement intentionally returns false while replaying, so replay callers must only apply already-authorized log records. Default quota fallback means missing ZAP entries do not necessarily mean unlimited usage.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_ratelimit.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_ratelimit.c

## Summary
Provides a small ZFS-owned rate limiter used instead of the Linux kernel `__ratelimit()` helper because the kernel helper emits unwanted suppression messages.

## Main Responsibilities
- Initialize and destroy `zfs_ratelimit_t`.
- Track event count within a fixed interval.
- Return whether the caller should proceed or suppress the event.

## Key APIs
- `zfs_ratelimit_init()`.
- `zfs_ratelimit_fini()`.
- `zfs_ratelimit()`.

## Important Behavior
The limiter stores a pointer to the live burst value rather than copying it, allowing module parameters or other callers to adjust the threshold after initialization. `zfs_ratelimit()` increments `count` under `rl->lock`, resets the interval when `NSEC2SEC(now - start) >= interval`, and returns `0` when the count reaches or exceeds `*burst` before the interval expires.

## Dependencies
Uses ZFS kernel compatibility primitives: `mutex_init()`, `mutex_enter()`, `gethrtime()`, and `NSEC2SEC()`.

## Risks
The first event after an interval reset sets `count` to zero after incrementing, effectively restarting the accounting window. A burst value of zero suppresses all events in an active interval after the initial reset behavior.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_ratelimit.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_replay.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_replay.c

## Summary
Implements ZIL replay for ZPL operations. It decodes log records, rebuilds vattr/xvattr/FUID/ACL context, claims logged object numbers and dnode sizes, and invokes the normal ZFS file operation paths to recreate logged filesystem mutations.

## Main Responsibilities
- Convert logged create, mkdir, symlink, xattr-dir, remove, rmdir, link, rename, write, truncate, setattr, ACL, SA-xattr, whiteout, exchange rename, and clone-range records into ZPL operations.
- Decode extended attributes, creation times, scanstamp/project-id shared fields, and FUID domain tables from variable-length log payloads.
- Handle byte-swapped log records.
- Preserve logged object identity by using `dnode_try_claim()` before replaying creates and whiteouts.
- Maintain replay progress through `zil_replaying()` where needed.

## Key APIs
- `zfs_replay_vector`.
- `zfs_replay_create()`, `zfs_replay_create_acl()`.
- `zfs_replay_remove()`, `zfs_replay_link()`, `zfs_replay_rename()`.
- `zfs_replay_write()`, `zfs_replay_write2()`, `zfs_replay_truncate()`.
- `zfs_replay_setattr()`, `zfs_replay_setsaxattr()`.
- `zfs_replay_acl_v0()`, `zfs_replay_acl()`.
- `zfs_replay_clone_range()`.

## Important Behavior
Create replay smuggles logged creation time, generation, and dnode slot size through otherwise unused `vattr_t` fields because the generic create path does not expose those parameters directly. It then dispatches to `zfs_create()`, `zfs_mkdir()`, `zfs_make_xattrdir()`, or `zfs_symlink()`.

Write replay distinguishes immediate write payloads from `dmu_sync()` block records. Whole-block replay may temporarily write beyond current EOF and pass the intended EOF through `zfsvfs->z_replay_eof`; `TX_WRITE2` only extends the file size when earlier synced block data is already present.

SA xattr replay loads or creates the cached nvlist, applies add/update/remove from the log record, limits value and total SA sizes, calls `zfs_sa_set_xattr()`, and drops the inconsistent cache if persistence fails.

ACL replay handles both old fixed ACE records and modern FUID-aware ACE records. For modern records it reconstructs `z_fuid_replay` so ephemeral IDs embedded in ACEs can be remapped during `zfs_setsecattr()`.

Linux-only rename variants replay `RENAME_EXCHANGE` and `RENAME_WHITEOUT`; other platforms return `ENOTSUP` for those transaction types.

## Dependencies
This file bridges ZIL record definitions, ZPL vnode operations, FUID handling, ACL encoding, SA xattrs, DMU object claiming, block cloning replay, and platform-specific Linux/FreeBSD vnode/idmap contracts.

## Risks
Variable-length payload parsing is offset-sensitive: xvattr data, ACL bytes, FUID arrays, domain strings, names, symlink targets, and xattr values are packed back-to-back. Several replay paths intentionally tolerate missing files because ZIL writes and clones may be logged out of order relative to removal.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_replay.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_rlock.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_rlock.c

## Summary
Implements byte-range locking for ZFS file operations. It serializes readers, writers, append writes, truncation, hole punching, indirect ZIL data capture, and block-size growth using an AVL tree of locked ranges.

## Main Responsibilities
- Initialize and destroy per-znode range lock state.
- Acquire blocking or nonblocking reader, writer, and append locks.
- Split overlapping reader ranges into proxy locks with reference counts.
- Wake waiting readers and writers fairly enough to avoid continuous-reader starvation of writers.
- Reduce an over-wide writer lock after block-size growth has been completed.

## Key APIs
- `zfs_rangelock_init()`, `zfs_rangelock_fini()`.
- `zfs_rangelock_enter()`, `zfs_rangelock_tryenter()`.
- `zfs_rangelock_exit()`.
- `zfs_rangelock_reduce()`.

## Important Behavior
Writer acquisition checks for any overlapping AVL node. Append and block-size-growth handling is delegated to the caller-supplied callback, which must convert `RL_APPEND` into `RL_WRITER` and may expand the lock to the whole file.

Reader acquisition allows overlap with other readers but waits behind active writers or ranges with a writer waiting. Overlapping reader locks are represented by proxy nodes. Existing ranges may be proxified and split so each AVL node describes a non-overlapping segment with a reference count.

Unlocking a reader either removes the original node directly or walks the proxy segments representing the original range, decrements counts, removes zero-count proxies, broadcasts waiters, and defers condition-variable destruction/freeing until after the range-lock mutex is dropped.

`zfs_rangelock_reduce()` asserts that the caller holds the whole-file writer lock, rewrites its offset/length to the final range, and wakes waiters.

## Dependencies
Uses AVL trees, ZFS mutex/condition-variable wrappers, kernel memory allocation, and the `zfs_rangelock_cb_t` callback used by ZPL and zvol callers.

## Risks
Correctness depends on exact proxy splitting and reference-count invariants. Wait condition variables are lazily initialized per contested range and must be destroyed only after no waiters can observe them. `zfs_rangelock_reduce()` broadcasts outside the mutex after changing the range, which relies on the asserted whole-file exclusive state.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_rlock.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_sa.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_sa.c

## Summary
Defines the ZPL system-attribute registration table and kernel helpers for symlink storage, scanstamp attributes, SA-backed xattrs, and upgrading old bonus-buffer znodes into SA-format znodes.

## Main Responsibilities
- Register ZPL SA attributes such as times, mode, size, parent, uid/gid, ACLs, symlink, scanstamp, DXATTR, and project ID.
- Read and write symlink contents from bonus buffers or file data blocks.
- Get and set antivirus scanstamp xvattrs for both old and SA znode formats.
- Load and persist SA-backed extended attributes stored as packed nvlists.
- Convert old znode bonus layouts to SA layouts when possible.
- Provide transaction hold helpers for SA upgrades.

## Key APIs
- `zfs_attr_table`.
- `zfs_sa_readlink()`, `zfs_sa_symlink()`.
- `zfs_sa_get_scanstamp()`, `zfs_sa_set_scanstamp()`.
- `zfs_sa_get_xattr()`, `zfs_sa_set_xattr()`.
- `zfs_sa_upgrade()`, `zfs_sa_upgrade_txholds()`.

## Important Behavior
Small symlinks are stored after `ZFS_OLD_ZNODE_PHYS_SIZE` in the bonus buffer; larger symlinks use object data blocks after growing the block size.

`zfs_sa_set_xattr()` packs the cached xattr nvlist into XDR, enforces `SA_ATTR_MAX_LEN`, optionally logs `TX_SETSAXATTR` when the pool feature and module parameter allow it, updates ctime, and commits synchronously when dataset sync mode is `always`.

`zfs_sa_upgrade()` refuses to upgrade symlinks or znodes without cached ACLs. It carefully handles `z_lock`, bulk-reads old attributes, adds a default project ID when project quotas are enabled, builds a new SA template including ACLs and optional scanstamp, switches the bonus type to `DMU_OT_SA`, replaces all attributes, frees external ACL objects, and marks `z_is_sa`.

## Dependencies
Depends on the SA framework, DMU bonus buffers, ZFS ACL transformation and locators, nvlist packing, ZIL xattr logging, project quota feature state, and znode lock/ACL cache state.

## Risks
SA upgrade can only proceed when ACL state is already cached; otherwise the old format remains until a later opportunity. SA xattr persistence mutates both the cached nvlist and on-disk SA value, so replay and error paths must drop inconsistent caches when persistence fails.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_sa.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_vnops.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_vnops.c

## Summary
Implements common ZPL vnode operations for syncing, access checks, hole/data seeking, reads, writes, rewrites, ACL get/set, ZIL write-data capture, direct I/O alignment reporting, block cloning, and clone replay.

## Main Responsibilities
- Commit ZIL records for fsync and sync-required reads/writes.
- Enforce access checks through ZFS ACL helpers.
- Implement `SEEK_HOLE` / `SEEK_DATA`.
- Set up buffered, uncached, or direct I/O according to flags, dataset policy, alignment, mmap state, and tunables.
- Perform chunked reads and writes under range locks with quota checks, timestamp updates, page-cache synchronization, SA updates, and ZIL logging.
- Rewrite existing data blocks physically or logically for maintenance operations.
- Provide ACL get/set wrappers.
- Supply write data to the ZIL for immediate and indirect write records.
- Implement block cloning and clone-range replay.

## Key APIs
- `zfs_fsync()`, `zfs_access()`, `zfs_holey()`.
- `zfs_read()`, `zfs_write()`.
- `zfs_rewrite()`.
- `zfs_getsecattr()`, `zfs_setsecattr()`.
- `zfs_get_direct_alignment()`.
- `zfs_get_data()`.
- `zfs_clone_range()`, `zfs_clone_range_replay()`.

## Important Behavior
`zfs_setup_direct()` is the central direct-I/O gate. It may force `O_DIRECT` from the dataset property, fall back to uncached ARC I/O when direct I/O is disabled or the range is mmaped, reject misaligned explicit direct I/O when strict mode is set, skip direct I/O for short writes, and pin/map pages for true direct I/O.

`zfs_read()` rejects quarantined files and directories, handles EOF and `FRSYNC`, locks the read range, reads in bounded chunks, chooses mapped-read versus DMU read paths based on cached page state, and falls back from direct I/O to ARC reads after checksum verification failures or trailing unaligned EOF reads.

`zfs_write()` validates readonly/immutable/append-only state, handles append range locking, applies file-size limits, checks user/group/project block quotas for each chunk, grows block size under a whole-file range lock when required, writes via DMU or pre-borrowed ARC buffers, updates mapped pages after races with mmap, clears setid bits when policy requires, updates size and timestamps, logs `TX_WRITE`, and commits when sync flags or sync=always require it.

`zfs_get_data()` is the ZIL get-data callback. Immediate records read data under a reader range lock. Indirect records lock a full block, recheck block size, hold the dbuf, and either record an already-completed direct-I/O block pointer or call `dmu_sync()`. `EALREADY` converts the log record to `TX_WRITE2`.

`zfs_clone_range()` validates same-pool and block-cloning feature state, encryption compatibility, optional strict dataset property matching, quarantine/readonly/immutable state, non-overlap for same-file clones, block alignment, fsize limits, dirty-source behavior, and block-size compatibility. It locks source as reader and destination as writer in a predictable order, reads L0 block pointers, clones through BRT, updates mapped destination pages, timestamps, size, setid bits, and logs `TX_CLONE_RANGE` in chunks that fit ZIL records.

`zfs_clone_range_replay()` replays logged clone records without access to the source znode by using the logged block pointers directly, growing the destination block size when needed and marking replay progress with `zil_replaying()`.

## Dependencies
This file ties together range locks, DMU reads/writes/sync/clone APIs, ARC buffers, page-cache integration, ZIL logging, SA bulk updates, quota checks, BRT block references, dataset properties, encryption-key comparison, and platform idmap/vnode behavior.

## Risks
The read/write paths are sensitive to races among direct I/O, mmap/page-cache state, range locks, and block-size growth. Clone validation has many feature and property constraints; returning partial progress is intentional and callers must honor the updated offsets/length. ZIL get-data runs while syncing is constrained, so it uses asynchronous znode release and callback-driven cleanup.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_znode.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/zfs_znode.c

## Summary
Provides object-to-parent, object-to-path, object-to-stat, and ZPL property lookup helpers for ZFS objsets. Despite the filename, this file is focused on SA-backed lookup utilities and master-node property reads rather than full znode lifecycle management.

## Main Responsibilities
- Initialize SA attribute tables for an objset.
- Safely grab/release SA handles for object numbers.
- Resolve an object's parent and identify xattr directories.
- Build a path string by walking parent object pointers and reverse-searching directory ZAP entries.
- Return lightweight stat data plus path for an object.
- Read selected ZPL properties from objset caches, the master node, or defaults.

## Key APIs
- `zfs_obj_to_pobj()`.
- `zfs_obj_to_path()`.
- `zfs_obj_to_stats()`.
- `zfs_get_zplprop()`.

## Important Behavior
`zfs_obj_to_pobj()` bulk-reads parent, flags, and mode, then verifies that the parent object still exists and is a directory unless the child is an xattr directory. This filters stale parent pointers left behind after unlink operations.

`zfs_obj_to_path_impl()` first checks the delete queue and returns `ESTALE` for unlinked objects. It then walks upward from the object to the root by repeatedly resolving parent object numbers, finding the child's directory entry name with `zap_value_search()`, inserting `/<component>` from the end of the caller buffer backward, and using `<xattrdir>` for xattr directory components.

`zfs_obj_to_stats()` combines `zfs_obj_to_stats_impl()` for mode, generation, link count, and ctime with the path reconstruction helper.

`zfs_get_zplprop()` uses cached objset fields for version, normalization, UTF-8-only, and case sensitivity when initialized. Otherwise it looks up master-node properties, returns defaults for missing values, and caches successful reads back into the objset fields.

## Dependencies
Depends on SA handle APIs, DMU object info, ZAP lookups, master-node names such as `ZFS_SA_ATTRS` and `ZFS_UNLINKED_SET`, ZPL property constants, and zfs_stat output structures.

## Risks
Path reconstruction assumes the caller-provided buffer is large enough; the code asserts rather than returns a clean truncation error if it walks past the buffer start. Parent pointers can be stale after unlink, so callers must handle `ESTALE` and validation errors.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/zfs_znode.c -->