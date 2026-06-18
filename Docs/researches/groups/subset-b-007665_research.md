# subset-b-007665 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_reint.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_reint.c

## Purpose

`mdt_reint.c` is the Lustre Metadata Target reintegration dispatcher and implementation for metadata-changing RPCs. It handles replay-aware create, setattr, unlink, link, rename, directory migrate/restripe, FLR resync, and setxattr delegation through the `mdt_reinters[]` table. The file sits on the boundary between ptlrpc request decoding already stored in `struct mdt_thread_info`, MDT object lookup/locking, MDD/OSD mutation calls, and reply-body packing.

The central theme is preserving namespace correctness under replay, distributed namespace (DNE) placement, striped directories, remote MDT objects, leases, HSM/SOM state, and intent locks. Most operations save or check VBR object versions, acquire LDLM locks in carefully chosen orders, call an `mdo_*`, `mo_*`, or layout helper to persist the change, and then update counters/reply attributes.

## Important APIs, Types, and Functions

- `mdt_version_get_save()`, `mdt_version_get_check()`, `mdt_version_get_check_save()`, `mdt_lookup_version_check()`, and `mdt_enoent_version_save()` implement VBR replay slots and `ENOENT_VERSION` handling.
- `mdt_object_stripes_lock()` and `mdt_object_stripes_unlock()` lock a local object and, for striped directories, slave stripes through `mo_object_lock()` / `mo_object_unlock()`.
- `mdt_create()` and `mdt_reint_create()` implement create/mkdir/mknod/symlink creation, DNE/LMV validation, remote/striped directory checks, inherited defaults, intent-lock reply handling, and optional manual restripe when an existing directory is found.
- `mdt_reint_setattr()` and `mdt_attr_set()` apply attribute changes, truncate/open lease handling, LSOM updates, FLR/overstriping compatibility checks, and HSM dirty marking through `mdt_add_dirty_flag()`.
- `mdt_reint_unlink()` handles ordinary unlink/rmdir, remote unlink redirection, `REINT_RMENTRY`, last-link handling, DoM discard, and lookup-by-FID hash-name cases.
- `mdt_reint_link()` validates source and target parent, locks parent/source, checks target-name VBR state, and calls `mdo_link()`.
- `mdt_reint_rename()` is the largest path: it finds parents and children, optionally takes the global rename/BFL lock, orders parent and child locks, redirects remote target-child cases, handles replacement victims, calls `mdo_rename()`, tallies parallel-rename counters, and discards DoM data after unlock when needed.
- `mdt_reint_migrate()` performs directory/file migration and namespace-only restripe migration by locking source/target stripes, extra link parents, source object/open state, and target object before `mdo_migrate()`.
- `mdt_reint_resync()` validates an FLR resync lease, grabs `mot_open_sem`, runs `mdt_layout_change(MD_LAYOUT_RESYNC)`, and returns refreshed attributes.
- `mdt_reint_rec()` dispatches by `rr_opcode` and increments PTLRPC operation counters.

## Control Flow

All reint handlers start from `info->mti_rr`, `info->mti_attr`, and the current request in `mdt_info_req(info)`. DLM cancellation via `ldlm_request_cancel()` appears early in mutating paths when the client piggybacks cancels. Most handlers then resolve one or more `struct mdt_object` instances from FIDs, validate existence/type/resource IDs/encryption/RBAC, take LDLM locks, perform VBR checks, call the lower metadata method, and unwind locks/refs through `GOTO()` labels.

Create first performs a lockless lookup to avoid mass lock recalls on existing names. If the name exists and the request is not replay or restripe, it returns `-EEXIST`; if restripe is allowed, it calls `mdt_restripe()`. Otherwise it saves/checks the name as `ENOENT_VERSION`, locks the parent, repeats lookup under the parent PDO lock, creates a new child object for `rr_fid2`, sets creation flags and directory features, calls `mdo_create()`, fetches attributes/layout EAs, packs the reply body, and optionally grants an intent/open lookup lock.

Setattr resolves the object, rejects remote objects, handles lease revocation for size-changing truncates, validates FLR/overstriping client compatibility, updates lazy SOM on truncation, and then either calls `mdt_attr_set()` for inode attributes or sets directory default LOV/LMV xattrs under xattr/update locks. After data-modified operations it marks HSM state dirty and returns fresh inode attributes.

Unlink locks the parent name first, does parent VBR, handles admin-only `sp_rm_entry`, resolves the child either from request FID or lookup/version check, redirects remote children with `-EREMOTE` plus `mbo_fid1`, locks local child lookup/update plus stripes, saves child version, serializes with `mot_lov_mutex`, calls `mdo_unlink()`, refreshes attributes or discards DoM data if dying, and handles last unlink state.

Migrate and rename are the most lock-sensitive flows. Migration optionally takes BFL for non-replay requests, finds the parent and source/target stripes through LMV hash logic, locks source/target parents in stripe-index order, locks all hardlink parents for non-directory inode migration using try-lock/revoke/retry logic, locks source lookup/xattr/open, optionally closes a lease-backed file, allocates/fetches target, and calls `mdo_migrate()`. Rename finds both parents, decides whether BFL is needed based on remote/parallel-rename policy, orders parent locks by subdir relation, stripe index, PDO hash, or FID, resolves old and optional new entries with version checking, locks children in deadlock-avoiding order, tries BFL after child preemption when enabled, drops/retries if contended, then calls `mdo_rename()`.

## State and Persistence Behavior

Persistent metadata changes are delegated to the MDD/MD object layer: `mdo_create()`, `mdo_unlink()`, `mdo_link()`, `mdo_rename()`, `mdo_migrate()`, `mo_attr_set()`, `mo_xattr_set()`, `mo_layout_change()`, and `mdt_layout_change()`. This file controls the in-memory state that makes those changes replayable and coherent: reply/request version slots, target VBR object marks via `tgt_vbr_obj_set()`, LDLM lock handles in `info->mti_lh[]`, `mot_restriping`, `mot_lov_mutex`, `mot_som_mutex` indirectly through SOM helpers, `mot_open_sem`, lease counts, and reply-body valid bits.

The replay contract is explicit. Normal requests save pre-operation versions into the reply; replay requests compare request versions and mark `exp_vbr_failed` on mismatch. Missing names and objects are represented with `ENOENT_VERSION`. Some distributed cases intentionally tolerate partially completed operations, such as remote mkdir replay where a name entry exists but the local target object does not, or remote unlink resend where the remote name was already removed.

## Dependencies and Integration Points

The file depends on `mdt_internal.h`, LMV and fscrypt helpers, LDLM lock APIs, ptlrpc request/reply capsules, MDD methods, DT versioning, HSM, LSOM, DoM, FLR layout changes, resource-ID and encryption checks, nodal DNE capability flags, RBAC fields in `struct lu_ucred`, LFSCK/fail injection macros, and lprocfs counters. It integrates with `mdt_restripe.c` through `mdt_restripe_internal()` and with `mdt_xattr.c` through `mdt_reint_setxattr()` / `mdt_dir_layout_update()`.

## Risks and Edge Cases

- Lock ordering is highly coupled to DNE, striped directories, hardlinks, and replay. Any new lock path must preserve parent/child/PDO/FID/BFL ordering or it can deadlock.
- VBR slot indexes have operation-specific meaning; changing request layouts or adding lookups without updating version save/check behavior can break replay correctness.
- Remote-object paths return `-EREMOTE` or `-EXDEV` with reply FID hints; clients and retry code depend on these exact semantics.
- `mot_restriping` is modified under restriper locks in some places but cleared on error paths outside the original spinlock in others; future changes need to keep queue/list state consistent.
- Rename two-phase BFL acquisition drops and reacquires many refs/locks. Missing a reset during the `goto lock_bfl` path would produce stale object pointers or leaked locks.
- LSOM/HSM/DoM side effects are easy to skip on new truncate, unlink, rename-replace, or data-modified paths.

## Test Signals

Useful tests include replay VBR mismatch for each reint opcode, create resend after partial remote mkdir, create of remote/striped/foreign directories with old and new clients, unlink remote redirect and resent no-name cases, hash-name unlink with embedded FID, hardlink target-exists race, same-dir and cross-dir rename races with reverse PDO hashes, remote rename `-EXDEV`/BFL policy, migration of files with many hardlinks and open leases, directory split/merge migration interruption, HSM dirty updates after data modification, LSOM updates on truncate/close, FLR resync with valid/canceled leases, and fail-injection labels around write and rename lock points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_reint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_restripe.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_restripe.c

## Purpose

`mdt_restripe.c` implements MDT-side directory restriping and auto-splitting. It owns the background `mdt_restriper_*` kernel thread, queue management for directories needing split/migrate/layout-update work, and helper preparation for invoking the normal reintegration paths internally. It converts manual or automatic layout changes into LMV state transitions, migrates directory entries between old and new stripes, and finalizes the master layout after all stripes clear migration state.

## Important APIs, Types, and Functions

- `mdt_auto_split_add()`, `mdt_restripe_migrate_add()`, and `mdt_restripe_update_add()` enqueue MDT objects on `mdr_auto_splitting`, `mdr_migrating`, and `mdr_updating` while setting `mot_restriping` and taking object references.
- `mdt_restripe_internal()` performs the split/merge layout transition for a directory under caller-held locks.
- `mdt_auto_split()` consumes auto-split work, resolves a stripe back to its master when needed, allocates a target FID, locks parent/child/stripes, prepares `md_op_spec`, and calls `mdt_restripe_internal()`.
- `mdt_restripe_migrate()` reads one directory page from a migrating stripe, selects the next real dirent after `mot_restripe_offset`, allocates a target FID, prepares a synthetic migrate reint record, and calls `mdt_reint_migrate()`.
- `mdt_restripe_migrate_finish()` clears `LMV_HASH_FLAG_MIGRATION` on a stripe and drops it from the migration queue.
- `mdt_restripe_layout_update()` checks all stripes of a master for migration completion and then calls `mdt_dir_layout_update()` to clear layout-change state or shrink.
- `mdt_restriper_start()` and `mdt_restriper_stop()` initialize/tear down the queue state, folio, LU environment/session, root-like ucred, and background task.

## Control Flow

Producers enqueue objects by setting `mot_restriping`, resetting offsets where needed, taking a ref, appending to a list under `mdr_lock`, and waking the restriper thread. The thread loops in idle state, prioritizing auto-split, then delayed layout update, then migration. Each item is removed or left queued depending on whether more work remains.

Manual split/merge runs through `mdt_restripe_internal()`. It fetches the child LMV, rejects changing layouts, rejects unchanged stripe count/hash, and distinguishes split from merge by comparing requested and existing stripe counts. Split may create a new master object for a plain directory and calls `mo_layout_change(MD_LAYOUT_SPLIT)`. Merge marks the LMV with `LMV_HASH_FLAG_MERGE | LMV_HASH_FLAG_MIGRATION`, records merge count/hash, bumps layout version, and stores the xattr.

Auto-split consumes a child or stripe object. If the queued object is a stripe, it resolves the master from PFID and avoids doing the split on a remote master. It calculates the next count from `mdr_dir_split_delta` capped by connected MDT count, fetches the parent name/FID, allocates a target FID, locks parent and child stripes, prepares a synthetic LMV user MD, and invokes the same internal restripe helper as manual restripe.

Migration consumes one dirent at a time from the current stripe page. It validates stripe LMV and stripe index, skips new split stripes and some CRUSH merge target stripes by finishing them immediately, reads `mo_readpage()` from `mot_restripe_offset`, skips empty and dot entries, copies the name into `mti_filename`, allocates a target FID from the master, prepares `mti_rr`/`mti_spec`, and calls `mdt_reint_migrate()`. On success it advances `mot_restripe_offset` to the next dirent hash or page end. End-of-directory finishes the stripe by clearing migration state.

Layout update waits until `mdr_update_time` has passed. It verifies every stripe no longer has restriping flags by fetching LMV directly and invalidating cache, then prepares a synthetic `REINT_SETXATTR` record and calls `mdt_dir_layout_update()`. If any stripe is still in progress it delays another five seconds; otherwise it clears `mot_restriping`, removes the master from the update list, and drops the ref.

## State and Persistence Behavior

Queue state lives in `struct mdt_dir_restriper`: three lists, one spinlock, an update timestamp, split thresholds, a folio used for `mo_readpage()`, reusable LMV buffers, and a thread LU environment/session. Per-object state is `mot_restriping`, `mot_restripe_linkage`, and `mot_restripe_offset`. Persistent layout state is in `trusted.lmv` xattrs: layout version, split/merge/migration flags, stripe FIDs, merge offset/hash, and cleared layout-change bits. Actual namespace movement is persisted by the regular `mdt_reint_migrate()` and MDD migration path.

## Dependencies and Integration Points

This file depends on Linux kthreads/folios, MDT object lifetime rules, LMV helpers, `mdt_reint_migrate()`, `mdt_dir_layout_update()`, `mdt_object_stripes_lock()`, MDD layout change and readpage methods, FID allocation through the child device, and capability/RBAC setup for an internal root-like thread. It is triggered by create/restripe paths in `mdt_reint.c` and finalizes through setxattr/layout code in `mdt_xattr.c`.

## Risks and Edge Cases

- Queue and `mot_restriping` invariants must match. Failing to clear the flag or delete linkage on every error can wedge future restripe attempts.
- `mdt_restripe_migrate()` reads one page and has a TODO to read one dirent; malformed or changing directory pages can return `-EBADF` and drop the queue item.
- The code parses stripe index from stripe name text after a rendered FID prefix, making name format changes risky.
- Internal synthetic requests have no ptlrpc request capsule in some paths, so called functions must tolerate `req == NULL` where expected.
- Auto-split is gated by connected MDT count; split attempts during no MDS-MDS connections fail and must be retried by higher-level triggers.
- Layout-update delay is time-based and may leave master objects queued while stripes are still migrating.

## Test Signals

Tests should cover enqueue idempotence, auto-split of plain and already-striped directories, remote-master skip, no-MDS-MDS connection behavior, split count capping, merge xattr flag/version updates, migration offset advancement across pages, skip of dot/dummy entries, end-of-directory finish, `-EBUSY` open-file handling, layout update while stripes are still in progress, layout update after all stripes finish, start/stop cleanup of non-empty queues, and fail injection through internal migrate/layout calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_restripe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_som.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_som.c

## Purpose

`mdt_som.c` implements MDT support for Lustre Size-on-MDS, especially lazy SOM revival (`LSOM`). It reads, writes, downgrades, and updates the `trusted.som` xattr that stores file size/block estimates on metadata targets so clients can sometimes avoid OST queries. It is deliberately conservative: strict SOM can be returned as inode size/blocks, lazy SOM is cached in `struct mdt_object`, and stale/strict transitions are guarded by `mot_som_mutex`.

## Important APIs, Types, and Functions

- `lustre_buf2som()` swabs on-disk `struct lustre_som_attrs` into in-memory `struct md_som`, treating zero-length or `-ENODATA` as no SOM.
- `mdt_get_som()` fetches `XATTR_NAME_SOM`, populates `ma->ma_som`, sets `MA_SOM`, returns strict size/blocks in `ma_attr`, and initializes lazy cached values in `mot_lsom_*`.
- `mdt_set_som()` writes a new SOM xattr with a supplied flag, size, and block count, and updates the in-memory lazy cache for `SOM_FL_LAZY`.
- `mdt_lsom_downgrade()` transitions strict SOM to stale while preserving the recorded size/blocks.
- `mdt_lsom_update()` decides whether close/truncate metadata should create or grow lazy SOM and writes `SOM_FL_LAZY` when appropriate.

## Control Flow

Reads use a fixed `mti_xattr_buf`, call `mo_xattr_get()`, swab the result, and interpret flags. Strict SOM marks `info->mti_som_strict` and overlays `LA_SIZE | LA_BLOCKS` into the inode attr. Lazy SOM initializes `mot_lsom_size`, `mot_lsom_blocks`, and `mot_lsom_inited` only if they are not already initialized and no one holds `mot_som_mutex`.

Writes build `struct lustre_som_attrs` in the thread xattr buffer, swab to disk order, and call `mo_xattr_set()`. Lazy writes also update the in-memory cache. Downgrade locks `mot_som_mutex`, reads current SOM into a scratch `md_attr`, and if strict, writes stale state with the same size/blocks.

Update first fast-exits when the caller's `la_valid` values do not increase cached size/blocks, the operation is not truncate, and the cache is initialized. Otherwise it fetches inode+SOM, ensures LOV EA is available, skips files without LOV, unlink files, and DoM-only files, and then computes a new lazy size/block pair. Non-truncate updates only grow cached values and skip strict SOM or stale SOM with no data modification. Truncate records the requested size and uses zero or a conservative block count of one when real blocks are unreliable. The final write is serialized by `mot_som_mutex` and rechecks cached values before updating.

## State and Persistence Behavior

Persistent state is the SOM xattr containing `lsa_valid`, `lsa_size`, and `lsa_blocks`. In-memory state on `struct mdt_object` mirrors lazy values through `mot_lsom_size`, `mot_lsom_blocks`, and `mot_lsom_inited`; `info->mti_som_strict` marks request-local strict SOM use. This file does not update OST data; it records metadata-side size/block hints based on attrs supplied by close/truncate paths and lower metadata reads.

## Dependencies and Integration Points

The code depends on `mo_xattr_get/set()`, `mdt_attr_get_complex()`, LOV xattr fetch helpers, `mdt_lmm_dom_only()`, thread-local buffers, `struct md_attr`, `struct lu_attr`, and `mot_som_mutex`. It is called from setattr/truncate and close-related paths in MDT code, including `mdt_reint_setattr()` before size changes and paths that need SOM downgrade on non-authoritative changes.

## Risks and Edge Cases

- Lazy SOM only grows on non-truncate updates; callers expecting shrink behavior must pass `truncate`.
- The first fast-exit relies on caller-provided `la_valid` and cached `mot_lsom_*`; missing valid bits can skip a needed update.
- `mti_big_lov_used` allows reusing existing LOV data, so callers must ensure it truly corresponds to the object.
- Truncate block count is intentionally approximate until a later close; consumers must not treat lazy blocks as strict truth.
- Strict-to-stale downgrade preserves size/blocks but clears strict validity; missing downgrade on data modification would expose stale strict sizes.

## Test Signals

Tests should cover no xattr, malformed/short xattr error propagation, strict SOM overriding inode size/blocks, lazy SOM cache initialization, set lazy updating cache, strict downgrade to stale, update skip when cached values are current, initial lazy creation with size+blocks valid, growth-only updates, stale-without-data-modified skip, truncate-to-zero, truncate-to-smaller-size block heuristic, DoM-only skip, unlink skip, and concurrent updates serialized by `mot_som_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_som.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_xattr.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_xattr.c

## Purpose

`mdt_xattr.c` handles MDT extended-attribute get, list, get-all, set, remove, ACL nodemap translation, and directory-layout finalization through setxattr-style reintegration. It validates client capabilities and xattr namespaces, sizes reply capsules, maps ACL IDs between client and filesystem domains, protects client xattr caches through LDLM locks, and special-cases LMV layout update requests used by directory migration/restripe.

## Important APIs, Types, and Functions

- `mdt_getxattr_pack_reply()` determines reply sizes for single xattr, listxattr, and all-xattrs requests and packs the server capsule.
- `mdt_nodemap_map_acl()` maps POSIX ACL xattr buffers through the export nodemap in either filesystem-to-client or client-to-filesystem direction.
- `mdt_getxattr_all()` returns name list, value blob, and value lengths in the `EADATA`, `EAVALS`, and `EAVALS_LENS` buffers.
- `mdt_getxattr()` is the public get/list/get-all request handler.
- `mdt_dir_layout_update()` finalizes LMV layout changes after migration, split, or merge, including shrink-to-plain-directory through `mo_layout_change(MD_LAYOUT_SHRINK)`.
- `mdt_reint_setxattr()` is the reintegration handler for xattr set/remove and the trusted LMV user-MD shortcut into `mdt_dir_layout_update()`.

## Control Flow

Getxattr first validates SEPolicy, resource IDs, and credentials. Reply packing checks which valid bit is set: `OBD_MD_FLXATTR` fetches the size of a named xattr and handles old-client user-xattr capability and `lustre.pin` name translation; `OBD_MD_FLXATTRLS` sizes the xattr list; `OBD_MD_FLXATTRALL` trusts a caller-provided bounded/aligned size because accurate sizing would be expensive. After packing, `mdt_getxattr()` fetches actual data when the requested `mbo_eadatasize` is nonzero, maps ACLs back to client IDs, shrinks all-xattr buffers to actual lengths, sets reply `OBD_MD_FLXATTR`, and increments stats.

Setxattr validates the namespace before taking locks. User xattrs require `OBD_CONNECT_XATTR`. Trusted xattrs require `CAP_SYS_ADMIN`, except `trusted.lmv` with an LMV user magic is intercepted for layout update. Several internal trusted xattrs are silently ignored or no-op protected, including LOV/LMA/LMV/LINK/FID/VERSION/SOM/HSM/LFSCK namespace and default LMV when disabled. ACLs are mapped from client to filesystem IDs and rejected if mapping changes the length. `lustre.lov.*` names are validated and take layout locks, while `lustre.pin` is translated to the trusted pin xattr after capability/gid checks.

Normal set/remove takes an object lock with update plus perm/xattr/layout bits in `LCK_EX`, sets the VBR target and saves/checks object version, fixes missing ctime from old/bad clients, then calls `mo_xattr_set()` or `mo_xattr_del()`. On success it updates ctime through `mo_attr_set()` with `MDS_PERM_BYPASS`.

Directory layout update resolves the object and its parent, optionally locks the parent update bit if shrink converts to one stripe, locks the directory and stripes, fetches LMV, validates that the layout is changing and that the requested count/hash matches the LMV migration/split/merge state, then either calls `mo_layout_change(MD_LAYOUT_SHRINK)` or clears layout-change flags and migration fields in the LMV xattr while bumping layout version.

## State and Persistence Behavior

Persistent state is xattrs on MDT objects, especially user/trusted namespaces, ACL xattrs, pin xattrs, default LMV, and LMV layout xattrs. The file also persists ctime updates after xattr changes. Request/reply state lives in capsule fields `RMF_EADATA`, `RMF_EAVALS`, `RMF_EAVALS_LENS`, `RMF_ACL`, and `RMF_MDT_BODY`. Layout update mutates LMV flags/version and can physically shrink directory layout through the lower layout-change method.

## Dependencies and Integration Points

The file depends on Linux xattr and Lustre ACL/nodemap APIs, ptlrpc capsules, `mdt_object_find_lock()`, VBR helpers from `mdt_reint.c`, LMV helpers, layout-change methods, RBAC/capability checks, client connection flags, and lprocfs counters. It integrates with the restriper, because `mdt_restripe_layout_update()` synthesizes a `REINT_SETXATTR` record that lands in `mdt_dir_layout_update()`.

## Risks and Edge Cases

- `OBD_MD_FLXATTRALL` relies on a bounded client size estimate; too small a buffer leads to lower get failures and shrunken zero output.
- Protected trusted xattrs often return success without changing state. That compatibility behavior can hide caller mistakes.
- ACL mapping can fail due to nodemap lookup, size limits, old-client ACL limits, or non-length-preserving ID mapping.
- Layout update compares little-endian LMV fields and user values; future changes must preserve endian handling.
- Shrink-to-one-stripe changes parent namespace/FID behavior and therefore takes extra parent locking; missing this lock would corrupt namespace consistency.
- `mdt_getxattr_pack_reply()` treats missing `trusted.lov` as zero-length success for old client compatibility, unlike most missing xattrs.

## Test Signals

Tests should cover single/list/all getxattr sizing, missing `trusted.lov`, old-client user-xattr rejection, `lustre.pin` translation, ACL map success/failure/size limits, all-xattr buffer shrink behavior, trusted protected no-op xattrs, set/remove ctime update, VBR replay mismatch, layout update for migration/split/merge, shrink to one stripe, hash/count mismatch errors, layout already complete `-EALREADY`, and cache invalidation/lock cancellation through xattr/perms/layout inode bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/Makefile -->
# sources/distributed-fs/lustre-release/lustre/osc/Makefile

## Purpose

This `Makefile` defines the Lustre OSC kernel module build composition. It adds `osc.o` to the module list and enumerates the object files linked into the Object Storage Client module. It also enables GCOV instrumentation for this subdirectory when `CONFIG_GCOV_PROFILE_LUSTRE` is set.

## Important APIs, Types, and Functions

There are no C APIs in this file. The important build variables are:

- `obj-m += osc.o`, which tells kbuild to build the OSC as a loadable module object.
- `osc-objs := ...`, which composes `osc.o` from request, lproc, device, object, page, lock, IO, quota, and cache implementation objects.
- `GCOV_PROFILE := y`, enabled conditionally for Lustre coverage builds.

## Control Flow

Kbuild reads the file while descending into `lustre/osc`. When building modules, it links `osc_request.o`, `lproc_osc.o`, `osc_dev.o`, `osc_object.o`, `osc_page.o`, `osc_lock.o`, `osc_io.o`, `osc_quota.o`, and `osc_cache.o` into `osc.o`. If the Lustre GCOV option is active, kbuild compiles this directory with coverage instrumentation.

## State and Persistence Behavior

The file has no runtime state. Its persistent effect is the module link contract: all listed objects become one OSC module. Adding, removing, or reordering object entries changes which OSC code is linked and can expose missing symbols or initialization-order assumptions at module load.

## Dependencies and Integration Points

It depends on Linux kernel kbuild semantics for `obj-m`, `<module>-objs`, and `GCOV_PROFILE`. It integrates with the rest of the Lustre build system and ensures `lproc_osc.c` is included in the OSC module along with the request, cache, IO, lock, and quota layers.

## Risks and Edge Cases

- A new OSC source file must be added here or it will compile nowhere in module builds.
- Removing `lproc_osc.o` would drop tunable/debugfs/sysfs registration code from the module.
- GCOV coverage depends on the conditional matching the top-level Lustre configuration; incorrect scoping can over-instrument or miss OSC files.

## Test Signals

Build tests should verify `osc.ko` links with all expected objects, `modpost` reports no missing OSC symbols, coverage builds produce GCOV data for OSC files when configured, and non-coverage builds leave `GCOV_PROFILE` unset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/lproc_osc.c -->
# sources/distributed-fs/lustre-release/lustre/osc/lproc_osc.c

## Purpose

`lproc_osc.c` registers and implements sysfs/debugfs/lprocfs controls for the Lustre Object Storage Client. It exposes runtime tunables for import activation, RPC concurrency, dirty/cache limits, grants, checksums, idle reconnect behavior, page-cache shrinking, and multiple statistics views. The code is administrative/control-plane logic for a live OSC instance rather than data I/O itself.

## Important APIs, Types, and Functions

- Sysfs-style show/store pairs exist for `active`, `max_rpcs_in_flight`, `max_dirty_mb`, `osc_unevict_cached_mb`, grant counters/shrink controls, checksum toggles, resend count, idle timeout/connect, and page-cache shrink.
- Debugfs seq files include `osc_cached_mb`, `unstable_stats`, `io_latency_stats`, `rpc_stats`, and `osc_stats`.
- `ldebugfs_osc_obd_vars[]` names debugfs entries and file operations.
- `osc_attrs[]` lists sysfs attributes installed in the OSC kobject default group.
- `osc_tunables_init()` attaches the lproc/debugfs/sysfs state to an `obd_device`, registers sptlrpc client lproc state, and registers PTLRPC stats.

## Control Flow

Simple show handlers derive `struct obd_device` from the kobject and read fields from `obd->u.cli` or the import under `with_imp_locked()`. Store handlers parse booleans, unsigned integers, or memory strings, validate ranges, take the appropriate spinlock/import lock, update fields, and trigger side effects such as `client_adjust_max_dirty()`, `osc_wake_cache_waiters()`, `osc_schedule_grant_work()`, `ptlrpc_set_import_active()`, or a forced pinger/statfs allocation.

Cache controls expose both read-only counters and active shrink operations. `osc_cached_mb_seq_write()` parses `used_mb:`, computes the number of pages to reclaim, obtains a client LU environment, and calls `osc_lru_shrink()`. `osc_unevict_cached_mb_store()` accepts only `clear`, shrinks the unevictable cache, and then scans the LRU to discard pages or move mlocked pages.

Grant controls report current grant, dirty grant, and lost grant. Writing `cur_grant_bytes` only shrinks grants when the target is below current available grant and the import is fully connected. `grant_shrink_interval` updates the interval and schedules work; `grant_shrink` toggles whether import grant shrink is disabled while respecting negotiated connect flags in the show path.

Statistics seq files format histograms under `cl_loi_list_lock`. `osc_rpc_stats_seq_show()` emits current in-flight and pending page counts plus histograms for pages per RPC, RPCs in flight, offsets, and latencies. Write handlers clear the corresponding histograms and reset initialization timestamps. `osc_io_latency_stats` delegates bucket formatting/clearing to common OBD helpers. `osc_stats` reports and clears lockless read/write byte counters.

Initialization sets `obd->obd_debugfs_vars`, assigns `osc_groups` to the OBD ktype, calls `lprocfs_obd_setup()`, attaches sptlrpc lproc entries, and registers ptlrpc stats. On sptlrpc attach failure it cleans up the lprocfs OBD setup.

## State and Persistence Behavior

This file mutates live in-memory OSC state: `client_obd` concurrency limits, dirty/cache page limits, grant accounting controls, checksum flags, resend counters, import idle timeout/debug flags, import activation state, and stats histograms. It does not persist settings across module unload or reboot. Some writes have immediate behavioral effects on worker pools, grant work, cache waiters, and import state.

## Dependencies and Integration Points

The code depends on Lustre OBD/lprocfs attribute macros, Linux kobject/sysfs and seq_file APIs, OSC internals (`osc_lru_shrink()`, `osc_shrink_grant_to_target()`, request pool population, cache shrink helpers), PTLRPC import/pinger/request APIs, checksum parameter helpers, and common OBD histogram/stat formatting. The `Makefile` links this file into the OSC module, making `osc_tunables_init()` part of OSC device setup.

## Risks and Edge Cases

- Store handlers are administrative attack surface; range checks on RPC counts, dirty MB, idle timeout, and grant targets are important to prevent resource exhaustion or nonsensical state.
- `max_rpcs_in_flight_store()` may over-allocate request pool entries by design under race; tests should verify it remains bounded by pool caps in practice.
- `cur_grant_bytes_store()` returns zero without changing state when target is above current grant, which can surprise scripts expecting `count`.
- Some debugfs write parsers accept a narrow format, such as `used_mb:` or literal `clear`.
- Histograms are formatted while holding `cl_loi_list_lock`; expensive seq output under the spinlock should remain bounded.
- Import access must stay under `with_imp_locked()` or import references must be taken, as done by `active_store()`.

## Test Signals

Tests should cover sysfs parsing and range rejection for all writable attrs, activation/deactivation idempotence, request-pool growth when increasing max RPCs, dirty limit adjustment and waiter wakeup, cache shrink and unevictable clear commands, grant shrink only while fully connected, checksum/resend toggles, idle timeout debug/nodebug/numeric modes, idle connect pinger forcing, histogram show output with empty and populated buckets, histogram clear writes, `osc_tunables_init()` cleanup on sptlrpc attach failure, and presence of every expected sysfs/debugfs entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/osc/lproc_osc.c -->
