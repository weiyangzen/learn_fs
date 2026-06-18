# sources/distributed-fs/lustre-release/lustre/mdt/mdt_open.c

## Purpose

`mdt_open.c` implements MDT open, create-on-open, by-FID open, cross-reference open, open-lock/lease handling, per-export open-handle tracking, replay reconstruction for open, close handling, HSM release, layout swap/merge/split/resync close intents, Size-on-MDS updates, dirty-flag updates, and operation counters. It is one of the central metadata request files for translating client open/close RPCs into MDD/LOD object operations and LDLM locks.

## Important APIs, Types, and Functions

- `struct mdt_file_data` lifecycle helpers: `mdt_mfd_new()`, `mdt_open_handle2mfd()`, `mdt_mfd_free()`, `mdt_mfd_set_mode()`, `mdt_mfd_close()`, and `mdt_close_internal()`.
- Write/execute exclusion helpers: `mdt_write_get()`, `mdt_write_put()`, `mdt_write_deny()`, `mdt_write_allow()`, and `mdt_write_read()`, operating on `mot_write_count`.
- Transaction/replay helper `mdt_empty_transno()` creates or assigns transaction numbers and updates in-memory `lsd_client_data` last-reply fields.
- Open helpers: `mdt_create_data()`, `mdt_prep_ma_buf_from_rep()`, `mdt_mfd_open()`, `mdt_finish_open()`, `mdt_open_by_fid()`, `mdt_open_by_fid_lock()`, `mdt_cross_open()`, `mdt_lock_root_xattr()`, `mdt_open_lock_mode()`, `mdt_pack_attr_acl()`, and public `mdt_reint_open()`.
- Lock helpers: `mdt_object_open_lock()` and `mdt_object_open_unlock()` handle normal open locks, leases, layout locks, DoM ibits, and readdir update locks.
- Recovery entry `mdt_reconstruct_open()` rebuilds replies from last-reply data and may rerun by-FID or regular open paths.
- HSM/layout close helpers: `mdt_hsm_release_allow()`, `mdt_orphan_open()`, `mdt_hsm_set_released()`, `mdt_get_lmm_gen()`, `mdt_hsm_release()`, `mdt_close_handle_layouts()`, and `mdt_close_resync_done()`.
- Public close entry `mdt_close()` unpacks close data, handles resends, closes the handle, fixes replies, and records counters.

## Control Flow

Open starts in `mdt_reint_open()`. The handler validates EA presence for flags that claim client-provided EA/objects, rejects write opens for read-only clients, blocks unauthorized `.lustre/fid` by-FID operation, then dispatches cross-ref, replay, or explicit by-FID opens before the normal name-based path.

The normal path validates the name, locks root xattr if remote root defaults may be needed, finds and version-checks the parent, enforces fscrypt/resource-id/encryption policy, chooses parent lock mode with `mdt_open_lock_mode()`, takes a parent lock, and performs lookup. Missing names require `MDS_OPEN_CREAT`, non-read-only export, and possibly a retry with a write parent lock to close unlink/create races. Creation allocates a new child object with the requested FID, saves VBR versions, sets create disposition, copies the configured job xattr name, calls `mdo_create()`, and then fetches child attributes. Existing children handle remote-object referral, early `O_DIRECTORY` checks, complex attr/HSM fetch, security/encryption context packing, optional open/layout/DoM lock acquisition, and `mdt_finish_open()`.

`mdt_finish_open()` packs inode attributes into `RMF_MDT_BODY`, rejects unsupported mirrored/overstriped layouts for older clients, optionally packs ACLs, suppresses open handles for symlinks and special nodes when requested, enforces `O_EXCL|O_CREAT`, checks directory/open flag mismatches, handles resent opens by finding an existing `mfd` with the same XID, then calls `mdt_mfd_open()`. `mdt_mfd_open()` may create missing LOV data, updates reply EA size flags, enforces write-vs-exec exclusion, calls `mo_open()`, allocates and links `mfd`, takes an MDT object reference, updates open/lease counts, handles replay orphan handles, returns the open cookie, and records an empty transaction number for reply reconstruction.

Close starts in `mdt_close()`. It unpacks close/SOM data, packs a minimal reply, checks resend reconstruction, initializes `ma` buffers, calls `mdt_close_internal()` to resolve and remove the open handle, and then `mdt_mfd_close()`. `mdt_mfd_close()` handles close intents first: HSM release, layout merge/split/swap, or resync done. It then updates LSOM, releases write/exec exclusion, writes close time updates, adds dirty flags, decrements open counts, handles last unlink cleanup, calls `mo_close()`, discards DoM data if needed, decrements lease count, frees the `mfd`, and drops the object reference. `mdt_close()` assigns an empty transno unless the handle was stale, fixes client compatibility in the reply, and records the close counter.

HSM release and layout close intents take write access to `mot_open_sem`, cancel the server-side lease, check whether the lease was already broken, acquire exclusive layout/xattr locks, and mutate layouts through `mo_swap_layouts()`, `mo_xattr_set()` with merge/split flags, or `mdt_layout_change()`. HSM release creates a volatile orphan object, marks layouts as released, sets HSM xattrs, swaps layouts, updates SOM, and reports intent execution in the reply.

## State and Persistence Behavior

The main live state is per-export open handles in `med_open_head` plus the global class handle hash. Each `mfd` owns a reference to the opened `mdt_object`, the open cookie, old replay cookie, XID, owner export, and open flags. Object-level state includes `mot_open_count`, `mot_lease_count`, `mot_write_count`, `mot_open_sem`, LOV-created flag, SOM mutex/state, cached root attr flag, and DoM discard decisions.

Persistent metadata changes are delegated to lower layers: `mdo_create()`, `mdo_create_data()`, `mdo_unlink()`, `mo_open()`, `mo_close()`, `mo_attr_set()`, `mo_xattr_set()`, `mo_swap_layouts()`, and `mdt_layout_change()`. Replay state is maintained through transaction numbers in replies and in-memory `lsd_client_data` fields (`lcd_last_transno`, `lcd_last_xid`, close variants, result, data, and pre-versions). `mdt_empty_transno()` is critical for operations that need reconstructable reply state even when no lower transaction was otherwise generated.

Close updates may persist atime/mtime/ctime, LSOM/SOM, HSM attributes, LOV layout changes, dirty flags, and last-unlink cleanup. Create failure after a child was created attempts to unlink the child unless it was volatile, where an orphan may remain until reboot.

## Dependencies and Integration Points

This file integrates with MDT internal request records, request capsules, LDLM inodebit locks, target VBR/replay helpers, nodemap/resource-id checks, encryption/fscrypt context packing, ACL packing, HSM state, LOD/MDD object operations, lprocfs counters from `mdt_lproc.c`, DoM helpers from other MDT files, and recovery reconstruction in `mdt_recovery.c`.

Client protocol compatibility is handled through connect flags: ACL, FLR, overstriping, read-only, open readdir, layout, DoM, NODEVOH, jobstats, DNE, and PCC-related flags. The file also uses many fault-injection points under `OBD_FAIL_MDS_*`, which are important integration hooks for Lustre recovery tests.

## Risks and Edge Cases

- Open replay and resend handling is subtle: handles can be found by current cookie, old replay cookie, or XID, and `mdt_empty_transno()` must keep last-reply data coherent without advancing committed state incorrectly.
- Lock return policy in `mdt_object_open_unlock()` depends on requested ibits, result code, remote-open sentinel, and whether useful open/layout/DoM bits were granted. Small changes can leak locks or fail to return needed client locks.
- Write/execute exclusion relies on signed `mot_write_count` where positive means writers and negative means exec deny; every failure path must balance get/put or deny/allow.
- HSM release and layout operations intentionally continue to close even after intent errors. Callers must inspect reply flags/status to distinguish close success from intent failure.
- `mdt_get_lmm_gen()` appears to call `le32_to_cpu(lmm->lmm_magic == LOV_MAGIC_COMP_V1)`, which compares before endian conversion; this is suspicious and should be reviewed because it can affect PCC/HSM layout version reporting.
- Volatile create/open failure can leave an orphan in PENDING until reboot, explicitly logged by the code.
- Parent lock mode starts with a lookup to decide PR vs PW for create; races force retry, so tests must cover create/unlink interleavings.

## Test Signals

High-value tests include open existing, create-on-open, `O_EXCL`, `O_DIRECTORY`, symlink/special NODEVOH, by-FID, cross-ref, remote-open referral, fscrypt/resource-id rejection, unsupported FLR/overstriping client rejection, ACL hint on `-EACCES`, replay after create, resent open same XID, old-cookie replay cleanup, write-vs-exec exclusion, lease acquisition conflicts, DoM/layout open lock return, parent lock retry on create race, close stale handle, close with time/SOM/dirty updates, last-unlink close, HSM release success/failure/already released, layout swap/merge/split/resync done, read-only export failures, and fault-injection cases for pack/net reply loss.
