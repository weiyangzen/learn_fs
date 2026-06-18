# Research: subset-b-007663

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_actions.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_actions.c

## Purpose
This file owns persistent HSM coordinator action logging and the debugfs view over that log. The coordinator stores HSM actions as `HSM_AGENT_REC` records in the `LLOG_AGENT_ORIG_CTXT` catalog so requests survive coordinator restarts and can be replayed/scanned later. It also manages request cookie allocation by deriving the last cookie from the existing llog when needed.

## Important APIs, Types, And Functions
`dump_llog_agent_req_rec()` formats one `llog_agent_req_rec` for HSM debug logging. `cdt_llog_process()` is the shared wrapper around `llog_cat_process()` for action-log scans. `mdt_agent_record_add()` allocates and appends a new persistent action record with status `ARS_WAITING`, archive id, flags, timestamps, and a stable cookie. Internally, `hsm_last_cookie_cb()` and `cdt_update_last_cookie()` reverse-scan the llog to initialize `coordinator::cdt_last_cookie`. The `agent_action_iterator` plus `mdt_hsm_actions_debugfs_*()` sequence operations implement `mdt_hsm_actions_fops`.

## Control Flow
Callers submit an `hsm_action_item` through `mdt_agent_record_add()`. The function builds a variable-size `llog_agent_req_rec`, gets the agent-origin llog context, initializes `cdt_last_cookie` if it is zero, assigns a new cookie except for explicit cancel records, and appends the record with `llog_cat_add()`. Debugfs iteration opens a seq file, allocates an iterator and `lu_env`, gets the llog context on each start, then repeatedly calls `llog_cat_process()` from the saved catalog/index cursor until the seq buffer fills or EOF is reached.

## State And Persistence
The durable state is the HSM action llog. Each record persists request status, archive id, original request flags, create/change timestamps, cookie, FID/data FID, extent, gid, and inline HAI data. `cdt_last_cookie` is in-memory but recoverable by reverse llog scan. Debugfs iterator state tracks the last shown catalog and record index to avoid restarting from the beginning on every seq callback.

## Dependencies And Integration Points
This code depends on Lustre llog APIs, MDT device naming helpers, `struct coordinator`, HSM action definitions, and debugfs/seq_file. It is called by HSM client registration paths, last-unlink HSM remove policy, coordinator scan code, and agent dispatch/update code. `mdt_internal.h` exports its APIs to the broader MDT/HSM subsystem.

## Risks
Missing or invalid `LLOG_AGENT_ORIG_CTXT` returns `-ENOENT`, which prevents new durable HSM requests and hides actions from debugfs. Cookie correctness depends on the reverse scan skipping cancel records and finding the newest non-cancel record; corrupted or out-of-order logs can affect duplicate detection. Debugfs iteration relies on llog catalog/index cursor bookkeeping and can skip or repeat records if llog mutation races are mishandled. Allocation sizes depend on `hai_len`, so malformed HAI lengths would be dangerous if upstream validation regresses.

## Test Signals
Useful signals are HSM archive/restore/remove/cancel tests that verify llog replay across MDT or coordinator restart, cancel records retaining target cookies, debugfs `hsm/actions` showing expected statuses and cookies, and last-cookie monotonicity after restart. Fault-injection coverage should include missing llog context, allocation failures, and llog add/process failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_actions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_agent.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_agent.c

## Purpose
This file manages HSM copytool agents registered with the MDT coordinator and sends selected HSM action batches to them. It tracks agent archive capabilities and load, converts active request lists into userspace kernel-comm HSM action lists, updates persistent llog records after dispatch, and provides a debugfs listing of registered agents.

## Important APIs, Types, And Functions
`mdt_hsm_agent_register()`, `mdt_hsm_agent_register_mask()`, and `mdt_hsm_agent_unregister()` maintain `coordinator::cdt_agents`. `mdt_hsm_agent_update_statistics()` adjusts per-agent request/success/failure counters. `mdt_hsm_find_best_agent()` chooses the least-loaded compatible agent for an archive. `mdt_hsm_agent_send()` validates a scan request, builds the outbound HAL, registers active in-memory requests, sends the request over the agent export reverse import, and modifies action llog records. `mdt_hsm_agent_modify_record()` persists status changes. `hsr_hal_size()` and `hsr_hal_copy()` size and fill the outbound `hsm_action_list`.

## Control Flow
Registration first obtains a coordinator reference, allocates a `hsm_agent`, copies archive ids, rejects duplicate UUIDs under `cdt_agent_lock`, links the agent, wakes the coordinator, and drops the reference. Agent selection scans registered agents under read lock, accepting archive-count zero as "all archives", and picks the lowest `ha_requests` count. Dispatch starts by choosing an agent; if no all-archive agent exists for archive zero remove requests, it can broadcast remove actions to all registered archive ids by adding fresh persistent records and marking the original records succeeded. Otherwise it revalidates each non-cancel request against current HSM state, removes invalid restore locks, builds a HAL excluding failed records, optionally registers active requests with `mdt_hsm_add_hsr()`, sends the packed kernelcomm message with `do_set_info_async()`, and finally updates/removes records and request counters.

## State And Persistence
Agent membership and counters are in-memory under `cdt_agent_lock`; persistent request state remains in the action llog and is changed through `mdt_hsm_agent_modify_record()`. Active requests are also registered in the coordinator request table by `mdt_hsm_add_hsr()` before dispatch. The outbound HAL is transient kernelcomm memory allocated by `kuc_alloc()`.

## Dependencies And Integration Points
The file integrates with coordinator reference management, request records from `mdt_hsm_cdt_requests.c`, HSM compatibility helpers from `mdt_coordinator.c`, llog modification, `obd_uuid_lookup()`, export lifecycle, and `LDLM_SET_INFO` reverse imports to clients running copytools. Its debugfs functions expose the registered-agent list and counters to operators.

## Risks
Agent selection is simple least-loaded scheduling and does not account for backend health beyond archive capability and export lookup. Dispatch has several race windows: objects can disappear between scan and send; agents can disconnect after selection; restore locks must be released for invalid restores; and llog status must remain consistent with in-memory request registration. Archive-zero remove broadcasting can produce duplicates after partial success because successfully reached archive ids are not persistently tracked. The archive mask path uses bit positions as archive ids plus one; very large archive ids are outside this mask representation.

## Test Signals
Look for HSM copytool registration/unregistration tests, duplicate UUID rejection, archive-mask registration, agent failover on disconnect or `-EPIPE`, request status transitions from waiting to started/succeeded/failed in debugfs, and remove-with-archive-zero behavior when only archive-specific agents are registered. Fault injection should cover reverse import failure, export eviction, incompatible HSM state, and `mdt_hsm_add_hsr()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_agent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_client.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_client.c

## Purpose
This file is the coordinator-facing implementation of client HSM action registration and action lookup. It validates `hsm_action_list` requests, detects redundant or cancel-target requests in the persistent llog, enforces user/group/other HSM permission masks, checks current file HSM state, records needed actions, and exposes an optimized restore-running query.

## Important APIs, Types, And Functions
`mdt_hsm_add_actions()` is the main entry for registering a HAL. `hsm_find_compatible()` and `hsm_find_compatible_cb()` scan existing llog records to fill cookies for duplicate or cancel requests. `hsm_action_is_needed()` suppresses no-op archive/restore/remove requests unless forced. `hal_is_sane()` validates basic HAL shape. `hsm_action_permission()` applies read-only and coordinator request-mask policy. `mdt_hsm_register_hal()` records each needed action, handles archive-id defaults, and takes restore handles. `mdt_hsm_restore_is_running()` checks the restore hash. `mdt_hsm_get_action()` reports the active action/status/extent for a FID and enriches started actions with in-memory progress totals.

## Control Flow
`mdt_hsm_add_actions()` rejects stopped/stopping coordinator state, validates the HAL, scans for compatible llog records where needed, and delegates per-item processing. `mdt_hsm_register_hal()` initializes data FID defaults, skips redundant non-cancel requests and cancel-without-target requests, fetches HSM metadata, applies permission checks, tests if the action is needed and compatible, derives archive id from the request, file HSM metadata, or coordinator default, takes an exclusive restore handle for whole-file restores, then appends an action llog record. If any restore was recorded and `CDT_NONBLOCKING_RESTORE` is set, it returns `-ENODATA` after recording to signal the nonblocking path while still waking the coordinator.

## State And Persistence
New requests are persisted only by `mdt_agent_record_add()`. Restore exclusion state is in `coordinator::cdt_restore_hash` through `cdt_restore_handle_add()` and is queried by `mdt_hsm_restore_is_running()`. Existing request compatibility is derived from the llog, while progress detail in `mdt_hsm_get_action()` is read from the active request table.

## Dependencies And Integration Points
The file depends on MDT object lookup and HSM xattr fetch via `mdt_hsm_get_md_hsm()`, action compatibility rules via `mdt_hsm_is_action_compat()`, llog scanning/addition from `mdt_hsm_cdt_actions.c`, active request lookup from `mdt_hsm_cdt_requests.c`, coordinator reference/event handling, capability checks, and `mdt_rdonly()` for non-restore write restrictions.

## Risks
This path must align permission masks with the `HSMA_*` enum values; mismatches can authorize or deny the wrong action. Restore requests only support whole-file extents here and reject nonzero offsets. Cancel-by-FID depends on llog search of waiting/started records and ignores explicit-cookie cancels. Admin exceptions allow remove/cancel even when the Lustre object is missing, so caller capability checks are security-sensitive. The function mutates HAL cookies/archive ids during compatibility processing, which callers must treat as in/out state.

## Test Signals
Useful tests include duplicate archive/restore suppression, cancel by FID and by cookie, forced actions, permission masks for owner/group/other users, read-only MDT behavior, restore lock exclusion including the LU-9266/LU-15132 race paths, nonblocking restore `-ENODATA`, and `mdt_hsm_get_action()` progress reporting for started requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_requests.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_requests.c

## Purpose
This file owns the in-memory active HSM request table used by the coordinator after actions have been assigned to agents. It indexes requests by cookie, maintains request reference counts and per-action counters, tracks byte-progress intervals, handles completion statistics, and provides debugfs output for active requests.

## Important APIs, Types, And Functions
`cdt_request_cookie_hash_ops` defines the `cfs_hash` cookie index over `cdt_agent_req::car_cookie_hash`. `mdt_cdt_alloc_request()` and `mdt_cdt_free_request()` manage request memory and embedded copied llog records. `mdt_cdt_add_request()`, `mdt_cdt_find_request()`, `mdt_cdt_update_request()`, and `mdt_cdt_remove_request()` are the public active-request lifecycle. `hsm_update_work()` merges progress extents in an interval tree. The `mdt_hsm_active_requests_proc_*()` seq operations back `mdt_hsm_active_requests_fops`.

## Control Flow
Allocation copies a persistent `llog_agent_req_rec` into an `hsm_mem_req_rec`, initializes the interval tree, and starts the kref. Adding requires a non-cancel action, inserts into the cookie hash under `cdt_request_lock`, links it on `cdt_request_list`, takes the list reference, updates agent stats, and increments total/archive/restore/remove counters. Lookup uses the hash and returns a referenced request. Progress update finds by cookie, refreshes the change timestamp, merges reported extents for non-remove successful progress, and updates agent success/failure counters on completed progress. Removal deletes from hash and list, decrements action counters and request count, drops cancel references, wakes the coordinator when the active count becomes zero, and releases the list reference.

## State And Persistence
The active table is in-memory state protected by `cdt_request_lock`; the persistent copy remains in the llog and is modified elsewhere. Each request holds a copied record pointer, agent UUID, reference count, optional paired cancel request, and interval-tree progress state. Progress intervals are coalesced under `cdt_req_progress::crp_lock` and represented as total bytes moved.

## Dependencies And Integration Points
This code integrates with `cfs_hash`, kernel rb interval-tree helpers, HSM progress RPC handling, coordinator scan/dispatch, agent statistics, debugfs, and llog-memory record structures. `mdt_hsm_get_action()` reads `car_progress.crp_total`, and agent dispatch/removal paths rely on request count and wakeup behavior.

## Risks
Reference ownership is nontrivial: hash lookup, list insertion, cancel pairing, and debug/scan users must balance `mdt_cdt_get_request()`/`put`. Progress interval merging treats adjacent intervals as one range and must guard overflow when computing `offset + length - 1`. Removing a request with `car_cancel` drops multiple references tied to `mdt_hsm_add_hsr()` behavior. If request counters get out of sync with hash/list operations, coordinator throttling and debug output become misleading.

## Test Signals
Test active request add/find/remove under duplicate-cookie conditions, progress interval merging with overlapping/adjacent/sparse ranges, overflow rejection, completion success/failure stats, cancel-paired request removal, coordinator wakeup when the active list drains, and debugfs `active_requests` output while requests are concurrently updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_hsm_cdt_requests.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_identity.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_identity.c

## Purpose
This file implements the MDT identity upcall cache operations. It invokes the configured userspace identity helper, parses downcall identity/group/permission data into kernel cache entries, manages delayed freeing for group_info references, and exposes helpers for getting/putting/flushing identity entries and selecting NID-specific permission masks.

## Important APIs, Types, And Functions
`mdt_identity_upcall_cache_ops` binds the cache callbacks: `mdt_identity_entry_init()`, `mdt_identity_entry_free()`, `mdt_identity_free_delay()`, `mdt_identity_do_upcall()`, and `mdt_identity_parse_downcall()`. Public helpers are `mdt_identity_get()`, `mdt_identity_put()`, `mdt_flush_identity()`, and `mdt_identity_get_perm()`.

## Control Flow
Cache entry initialization zeros `md_identity` and back-points it to its cache entry. On cache miss, `mdt_identity_do_upcall()` validates the upcall path is not `NONE` or empty under `uc_upcall_rwsem`, invokes the helper with cache name and UID key, and returns success after `UMH_WAIT_EXEC`. Downcall parsing bounds group count, allocates/sorts group_info, allocates permission entries, converts legacy NID format to `lnet_nid`, and stores UID/GID/groups/perms in the entry. Freeing releases permission arrays immediately, then either schedules asynchronous work to `put_group_info()` and free the entry or frees directly when no group_info is present.

## State And Persistence
Identity state is an in-memory `upcall_cache` entry keyed by UID. It stores primary UID/GID, optional `group_info`, and optional `md_perm` array. There is no direct on-disk persistence here; freshness and lifetime are controlled by the generic upcall cache. Permission lookup treats `perm[0]` as the default/NID-any permission when applicable.

## Dependencies And Integration Points
The file depends on generic Lustre upcall cache infrastructure, Linux group_info allocation/freeing, `call_usermodehelper()`, identity downcall formats, LNET NID conversion, and credential code in `mdt_lib.c`. MDT credential initialization uses this cache to validate setuid/setgid/setgroups permissions and Kerberos group trust.

## Risks
The upcall path can change concurrently, so `mdt_identity_do_upcall()` guards with the upcall rwsem but still treats `NONE`/empty as `-EREMCHG`. Downcall group counts must remain bounded by `NGROUPS_MAX`; permission allocation failures need to free any already allocated group_info. Delayed free exists because `put_group_info()` can sleep while cache locks may be held; bypassing that pattern would risk sleeping in atomic/locked context. Permission matching assumes any default entry is at index zero.

## Test Signals
Test identity cache miss/upcall invocation, `NONE` and empty upcall behavior, downcall parsing with zero and many groups, over-`NGROUPS_MAX` rejection, multiple permission entries with exact NID match before default, cache flush by UID and idle flush, and cleanup paths with and without `group_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_identity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_internal.h -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_internal.h

## Purpose
This is the central private MDT header. It defines the core MDT device, object, request-thread, HSM coordinator, HSM request, agent, restore-handle, lock, and directory restriper data structures, plus internal prototypes and inline helpers shared across MDT implementation files.

## Important APIs, Types, And Functions
Major types include `mdt_file_data`, `coordinator`, `mdt_device`, `mdt_object`, `mdt_lock_handle`, `mdt_reint_record`, `mdt_thread_info`, `cdt_req_progress`, `cdt_agent_req`, `hsm_agent`, `cdt_restore_handle`, `hsm_mem_req_rec`, and `hsm_scan_request`. Important inline helpers include `cdt_mdt_state2str()`, `mdt_th_info()`, `hsr_get_archive_id()`, object get/put/FID conversion helpers, layout interpretation helpers for DoM/FLR/overstriping, `agent_req_in_final_state()`, `mdt_rdonly()`, `mdt_check_resent()`, `is_identity_get_disabled()`, `mdt_fid_lock()/unlock()`, `mdt_hsm_cdt_event()`, `mdt_changelog_allow()`, `mdt_check_enc()`, and `mdt_dom_check_for_discard()`.

## Control Flow
The header does not implement request handlers directly, but it defines the call graph contracts: request handlers obtain `mdt_thread_info` from the `lu_env`, operate on `mdt_device` and `mdt_object`, use lock handles for LDLM/PDO/cross-MDT locks, unpack requests into `mdt_reint_record`, and call lower `md_object`/`dt_object` operations. HSM coordinator paths use `coordinator` state, agent lists, request lists, cookie hash, restore hash, and event signaling. IO paths use the exported DoM/BRW/fallocate/punch/glimpse prototypes.

## State And Persistence
`mdt_device` aggregates persistent-target attachments, namespace, bottom DT device, identity caches, root squash, quota connection, coordinator, and tunables. `mdt_object` contains per-object runtime state such as write/open/lease counts, locks, DoM semaphore, layout/SOM state, and restripe linkage. `coordinator` contains runtime HSM state, but its requests are mirrored in the HSM action llog through implementation files. `mdt_thread_info` is per-thread scratch state and must be initialized/reset carefully because parts are explicitly not initialized.

## Dependencies And Integration Points
The header ties MDT code to Lustre OBD, LU, MD, DT, LDLM, FLD, quota, nodemap, request capsule, HSM, lprocfs, and encryption subsystems. It is included by all files in this subset and exports their public internal symbols to the rest of MDT. Compatibility conditionals and connection-flag helpers make it a boundary between wire protocol features and server behavior.

## Risks
The lock order for HSM coordinator locks is documented here (`cdt_agent_lock`, `cdt_counter_lock`, `cdt_request_lock`) and violations can deadlock. `mdt_thread_info` has fields that are intentionally uninitialized, so handlers must only read initialized members for their phase. Inline helpers often assume non-null exports, devices, or request bodies and rely on upstream validation. Structure fields define concurrency boundaries; changing them requires auditing locking, replay, recovery, and on-wire compatibility.

## Test Signals
Compile-time coverage is important because this header is broad. Runtime signals include request replay/reconstruction, HSM coordinator state transitions, DoM IO, encryption-aware/unaware access, changelog RBAC checks, DNE/striped-directory feature negotiation, resource-id checks, and old-client compatibility paths. Static analysis should flag lock-order misuse and unchecked assumptions around `mti_pill`, `mti_exp`, and optional reply fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_io.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_io.c

## Purpose
This file implements MDT-side data operations for Data-on-MDT (DoM): high-priority BRW/punch request lock checks, prepare/commit of read/write buffers, fallocate, punch/truncate, fiemap, data-version lookup, DoM lock glimpse/LVB handling, read-on-open optimization, and discard of cached client data when objects are destroyed.

## Important APIs, Types, And Functions
Public entry points include `mdt_hp_brw()`, `mdt_hp_punch()`, `mdt_obd_preprw()`, `mdt_obd_commitrw()`, `mdt_fallocate_hdl()`, `mdt_fiemap_get()`, `mdt_punch_hdl()`, `mdt_dom_object_size()`, `mdt_glimpse_enqueue()`, `mdt_brw_enqueue()`, `mdt_dom_client_has_lock()`, `mdt_data_version_get()`, `mdt_dom_read_on_open()`, `mdt_dom_discard_data()`, and `mdt_dom_obj_lvb_update()`. Internal helpers cover lock prolongation, BRW read/write prep, commit transactions, fallocate-zero fallback, FIEMAP sparse-region checks, glimpse AST work, and LVB reply packing.

## Control Flow
High-priority setup attaches `ptlrpc_hpreq_ops` when the request is covered by a client DoM lock and does not require server locking or replay processing. `mdt_obd_preprw()` validates one-object BRW requests, finds the MDT object, stores it in thread info, then maps remote buffers to local niobufs under `mot_dom_sem` for read or write. `mdt_obd_commitrw()` completes read cleanup or write commit; writes map nodemap IDs for reply, process grants/quota, update timestamps only for current FMD XIDs, run a DT transaction, retry for ENOSPC/restart cases, update counters, and refresh DoM LVBs. Fallocate and punch handlers optionally take server data locks, validate object type and resource ids, update attributes in transactions, and update LVB replies. Glimpse paths fill DoM size/block/time in either old MDT-body fields or the newer DLM LVB. Read-on-open grows the open reply with inline data only when a DoM+layout lock was returned and the configured optimization is enabled.

## State And Persistence
Persistent data changes are made through DT transactions against `mdt_bottom` objects. Runtime coordination uses `mdt_object::mot_dom_sem`, LDLM resources/LVBs, grant accounting, FMD XID tracking, lprocfs counters, and object flags such as `mot_discard_done`. Read-on-open copies data into the RPC reply without changing persistence. Discard uses a local PW DOM lock with `LDLM_FL_AST_DISCARD_DATA` to force clients to drop cached pages.

## Dependencies And Integration Points
This file sits between target RPC handling, LDLM, DT object IO, grants/quota, nodemap, request capsules, lprocfs counters, and MDT object lookup. It relies on prototypes and structures from `mdt_internal.h`, lower DT methods such as `dt_bufs_get()`, `dt_write_commit()`, `dt_falloc()`, `dt_fiemap_get()`, and target helpers such as `tgt_mdt_data_lock()` and `tgt_grant_*()`.

## Risks
DoM IO is lock-sensitive. Missing `mot_dom_sem` release, stale object handling, or incorrect high-priority lock matching can cause deadlocks, stale writes, or client eviction noise. Write grant handling must commit/deallocate grants on all error paths. Root-squash/nodemap remapping affects quota bypass flags and returned IDs. Fallocate zero fallback writes chunks using BRW-style commit and must avoid double-freeing buffers. Read-on-open must respect encryption-unit sizing and reply capacity; partial reads are intentionally ignored. Async discard stores object pointers in lock AST data and depends on callback cleanup for references.

## Test Signals
Relevant tests include DoM read/write under lock cancellation, BRW replay exclusion from high-priority handling, grants and overquota flags, root-squash writes, stale/missing object reads and writes during eviction/unlink, fallocate punch/zero/keep-size modes, FIEMAP with sparse DoM regions and server locks, old/new DoM LVB clients, read-on-open for encrypted and unencrypted files, and async discard behavior for old and new clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lib.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_lib.c

## Purpose
This file provides shared MDT request helper logic. Its largest responsibilities are initializing and validating request credentials, integrating nodemap/root-squash/identity/RBAC/capability policy, checking resource IDs, shaping reply buffers, handling HSM remove-on-last-unlink policy, and unpacking all reintegration request variants into `mdt_thread_info`.

## Important APIs, Types, And Functions
Credential APIs include `mdt_init_ucred()`, `mdt_init_ucred_reint()`, `mdt_check_ucred()`, `mdt_exit_ucred()`, `allow_client_chgrp()`, and `mdt_enable_gid_deny()`. Request/reply helpers include `mdt_name_unpack()`, `mdt_close_unpack()`, `mdt_reint_unpack()`, `mdt_fix_lov_magic()`, `mdt_fix_reply()`, `mdt_pack_secctx_in_reply()`, `mdt_pack_encctx_in_reply()`, `mdt_layout_version_check()`, `mdt_fids_different_target()`, and `mdt_is_remote_object()`. Policy helpers include `mdt_check_resource_ids()` and `mdt_handle_last_unlink()`. Static unpackers cover setattr, create, link, unlink/rmentry, rename, migrate, open, setxattr, and FLR resync.

## Control Flow
Credential initialization first exits any previous credential state, chooses old or new initialization based on GSS/user descriptor availability, maps client IDs and supplementary groups through nodemap, sets original and effective IDs, fetches identity upcall data when enabled, enforces setuid/setgid/setgroups permissions, applies deny-unknown and root-squash policy, intersects or assigns capabilities based on nodemap/server configuration, handles Kerberos group trust, and records jobid/NID/audit/RBAC fields. Reintegration unpacking clears `mti_rr`, dispatches by opcode, copies wire records into attributes/op specs/FID/name fields, maps supplementary groups, validates optional security/encryption contexts and sepol, handles replay/no-create flags, and unpacks optional LDLM requests. Reply fixing shrinks unused optional buffers and grows/re-packs large LOV/LMV/ACL buffers when the initially allocated reply was too small.

## State And Persistence
Most state is per-request in `lu_ucred`, `mdt_thread_info::mti_attr`, `mti_rr`, and `mti_spec`. Identity references and group_info references are held until `mdt_exit_ucred()`. `mdt_handle_last_unlink()` can persist an HSM `HSMA_REMOVE` request into the action llog when RAoLU policy is active and the last open reference of an archived unlinked file closes. Reply buffer sizes are transient RPC capsule state, but `mdt_max_mdsize` may be updated when larger metadata is observed.

## Dependencies And Integration Points
This code depends on request capsules, ptlrpc authentication fields, nodemap, identity upcall cache, root-squash configuration, Linux capabilities, Lustre layout/LMV/LOV formats, security and encryption xattrs, FLD lookup, linkEA parsing, HSM coordinator action logging, and lower MD/DT xattr/attribute operations. It is a central dependency for MDT metadata handlers and close/open/reint paths.

## Risks
Credential code is security-critical and mutates wire/body fields after nodemap mapping; callers must not assume original client IDs remain in those structures. Error paths must drop identity and group_info references. Kerberos mode intentionally distrusts client supplementary groups and requires identity consistency. Request unpackers rely on exact wire record sizes and optional field presence; accepting malformed names, xattr sizes, encryption contexts, or layout EAs would affect filesystem integrity. `mdt_fix_reply()` must coordinate with all handlers that add optional reply fields, or clients may see missing/oversized metadata. RAoLU last-unlink logging intentionally returns success even if remove logging fails, so operational monitoring must catch CERRORs.

## Test Signals
High-value tests cover old and new credential paths, Kerberos setuid/setgid/setgroups rejection, deny-unknown nodemap behavior, root-squash/nosquash NIDs, capability masks, RBAC role propagation, resource-id denial, all reint unpackers with malformed and optional fields, encryption/security context packing, large LOV/LMV/ACL reply growth, remote-object detection through FLD/linkEA, layout-version mismatch, replay/no-create behavior, and RAoLU remove request creation on last unlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lib.c -->
