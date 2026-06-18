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
