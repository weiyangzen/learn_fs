# subset-b-009708 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_clientid.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_clientid.c

Purpose: Manages NFSv4 client identity records, confirmed and unconfirmed clientid caches, owner-name records, clientid/verifier generation, reference lifetimes, delayed expired-client cleanup, and administrative/client callback traversal for NFSv4.1 clients.

Important APIs, types, and functions: Global caches include `ht_confirmed_client_id`, `ht_unconfirmed_client_id`, and `ht_client_record`; `client_id_pool` allocates `nfs_client_id_t`. Public entry points include `create_client_id`, `nfs_client_id_insert`, `nfs_client_id_confirm`, `remove_confirmed_client_id`, `remove_unconfirmed_client_id`, `nfs_client_id_get_confirmed`, `nfs_client_id_get_unconfirmed`, `nfs_client_id_expire`, `reap_expired_client_list`, `get_client_record`, `nfs41_foreach_client_callback`, `destroy_all_client_connections`, `nfs_Init_client_id`, and `get_total_count_of_open_states`. Display/hash helpers cover clientids and client records, while `inc_client_id_ref`, `dec_client_id_ref`, `inc_client_record_ref`, and `dec_client_record_ref` own lifetime transitions.

Control flow: A clientid is allocated with an initialized embedded `STATE_CLIENTID_OWNER_NFSV4` owner, callback/session structures, owner lists, credential copy, and a reference to its `nfs_client_record_t` and `gsh_client`. It is inserted into the unconfirmed hash, then confirmation moves the same hash value from `ht_unconfirmed_client_id` into `ht_confirmed_client_id`, increments confirmed-client metrics, links the record's confirmed pointer, and calls `nfs4_add_clid` for recovery persistence. Lookups reject mismatched unique server epochs before hitting the hash table, then take a ref through `hashtable_getref`. Expiry detaches the client from its record, optionally marks it stale for IP release, unhashes true expirations, drains lock owners, open owners, layouts, delegations, callback channels, sessions, and recovery tags, then releases the hash-table ref. Delayed expiry first places low-state clients on `expired_client_ids_list`; the reaper later validates leases again, locks the client record, and forces full expiry.

State and persistence behavior: In-memory state is stored in three hashtables plus `expired_client_ids_list`; confirmed-client count and expired-client count are atomic counters. Client records are keyed by owner opaque value, pNFS flags, server address, and optionally client address. Persistent/restart state is delegated to recovery hooks via `nfs4_add_clid` and `nfs4_rm_clid`; the client itself stores `cid_recov_tag`. The code holds GSS credential refs, `gsh_client` refs, state-owner refs, client-record refs, and callback/session resources until final `free_client_id`.

Dependencies and integration points: Depends on Ganesha hash tables/latches, `glist`, atomic helpers, client manager, recovery (`nfs4_add_clid`/`nfs4_rm_clid`), lease code (`valid_lease`), state cleanup (`release_openstate`, `state_nfs4_owner_unlock_all`, `revoke_owner_layouts`, `revoke_owner_delegs`), sessions/callback RPC cleanup, metrics, LTTng tracepoints, and `nfs_param.nfsv4_param` configuration.

Risks: Lock ordering is critical: `expired_client_ids_list_lock` must not be taken under `cid_mutex`; expiry also coordinates with `cr_mutex`, owner mutexes, hash locks, and state locks. Reference underflow or a missed hash-table ref can free active clients. Delayed cleanup intentionally keeps expired clients reachable, so stale lease decisions or failure to unmark active clients can preserve or destroy state incorrectly. `compare_client_record` contains subtle address/owner matching semantics, including optional IP-based owner separation. Expiry loops depend on owners eventually releasing extra refs and can spin/yield heavily when refcount bugs exist.

Test signals: Useful tests should cover SETCLIENTID/CONFIRM insertion and migration, stale epoch rejection, confirmed/unconfirmed lookup refcounts, forced and delayed lease expiry, active lease un-expiry from the delayed list, NFSv4.1 session destruction, recovery tag add/remove, IP-release stale marking, max-client/max-open-state limits, and concurrent expiry versus lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_clientid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_lease.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_lease.c

Purpose: Provides NFSv4 lease validation, reservation, renewal, and expiry handoff for `nfs_client_id_t` records.

Important APIs, types, and functions: `_valid_lease` computes remaining lifetime, `valid_lease` exposes the mutex-protected boolean check, `reserve_lease` increments `cid_lease_reservations`, `reserve_lease_or_expire` atomically reserves or forces client expiry, and `update_lease` drops a reservation and renews `cid_last_renew` when the last reservation exits.

Control flow: Lease validation returns invalid for `EXPIRED_CLIENT_ID`, valid for any active reservation, otherwise compares `cid_last_renew + lease_lifetime` against `time(NULL)`. A delayed-cleanup client is treated as still valid for non-reaper checks so active traffic can remove it from the expired list. `reserve_lease_or_expire` locks `cid_mutex`, reserves valid leases, optionally updates them, then asks the caller to unexpire outside the client mutex. If invalid, it takes temporary client/client-record refs, drops state-owner refs passed by the caller so expiry can clean owners, locks `cr_mutex`, calls `nfs_client_id_expire`, and releases all temporary refs.

State and persistence behavior: State is only the client record's `cid_last_renew`, `cid_lease_reservations`, confirmation state, and delayed-cleanup marker. Persistence is indirect: invalid lease handling invokes client expiry, which removes recovery records and state through other SAL files.

Dependencies and integration points: Uses global `nfs_param.nfsv4_param.lease_lifetime`, clientid refcount APIs, client-record refs, state-owner refs, delayed-expired-client list removal, and LTTng clientid tracepoints. It is called from stateid validation, reaper code, and NFSv4 operation processing paths that need to reserve a lease while mutating state.

Risks: Callers must hold `cid_mutex` for `valid_lease`, `reserve_lease`, and `update_lease` semantics; missing the required lock can corrupt reservation counts. Every successful reserve requires a later update/release path. The `st_owner` drop inside `reserve_lease_or_expire` is intentional to avoid owner cleanup deadlock; callers must tolerate it being nulled. Delayed-cleanup behavior makes lease validity context-sensitive via `is_from_reaper`.

Test signals: Cover lease lifetime boundary, reservation preventing expiry, last-reservation renewal, delayed-client validity from normal callers versus reaper, forced expiry on invalid lease, state-owner ref release during expiry, and list removal when renewed clients become active again.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_lease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_owner.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_owner.c

Purpose: Implements the NFSv4 state-owner cache for open owners, lock owners, and the embedded clientid owner, plus NFSv4.0 seqid/replay tracking and lock-conflict response helpers.

Important APIs, types, and functions: The `ht_nfs4_owner` table stores `state_owner_t` entries keyed by owner type, clientid, and opaque owner value. Key functions are `Init_nfs4_owner`, `create_nfs4_owner`, `free_nfs4_owner`, `display_nfs4_owner`, `compare_nfs4_owner`, `Process_nfs4_conflict`, `Release_nfs4_denied`, `Copy_nfs4_denied`, `Copy_nfs4_state_req`, and `Check_nfs4_seqid_locked`.

Control flow: `create_nfs4_owner` builds a stack key with owner name, client record, owner type, related open owner, initial seqid, confirmation state, and cached response placeholders, then delegates allocation/deduplication to `get_state_owner`. `init_nfs4_owner` initializes the per-owner state list, refs the related owner and clientid, and links open or lock owners into the client's per-client list under `cid_mutex`. Existing lock owners can be re-associated with a new related open owner when they have no active POSIX locks, recovering zombie lock-owner reuse after client crash/expiry. `free_nfs4_owner` removes per-client linkage and releases cached response and references. Seqid handling compares a request to the next expected seqid, returns cached responses on replay, and flags bad seqids for out-of-order or wrong-op requests.

State and persistence behavior: Owner state is in-memory hash/cache state. It stores owner opaque bytes, clientid, seqid, confirmation flag, related owner, cached response, cached request op, last object pointer, state list, and optional open-owner cache expiry. There is no direct persistence; owners are rebuilt from clients and protocol operations, and recovery is managed through clientid/recovery files.

Dependencies and integration points: Integrates with generic state-owner cache routines in `sal_functions`, clientid refs, NFS protocol compound copy/free helpers, response-size accounting, `LOCK4denied` encoding, and `unknown_owner`. The owner lists are consumed by `nfs4_state.c` and client expiry logic.

Risks: Hashing is intentionally simple and marked for replacement, so collision behavior relies on compare correctness. Replay detection stores shallow object pointers for last entry and only selected arguments, which is sufficient for current semantics but fragile if reused for deeper operation matching. Related-owner repair must not mask genuine active-lock conflicts. `Process_nfs4_conflict` allocates denied owner buffers conditionally, so release/copy paths must preserve the `unknown_owner` sentinel.

Test signals: Exercise new and reused open/lock owners, per-client list linkage, related-owner mismatch with active versus no locks, seqid next/replay/bad cases, cached response copying, lock denied owner allocation/release/deep-copy, and owner cleanup on client expiry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_recovery.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_recovery.c

Purpose: Coordinates NFSv4 grace periods, client reclaim eligibility, recovery backend selection, persistent client/revoked-filehandle records, clustered takeover/release events, and NLM/NFSv4 state release during recovery events.

Important APIs, types, and functions: Core state includes `grace_mutex`, `current_grace`, `clid_list`, `clid_count`, `grace_status`, `reclaim_completes`, and the `nfs4_recovery_backend` vtable. Key functions include `nfs_start_grace`, `nfs_try_lift_grace`, `nfs_get_grace_status`, `nfs_put_grace_status`, `nfs_in_grace`, `nfs4_add_clid`, `nfs4_rm_clid`, `nfs4_chk_clid`, `nfs41_reclaim_complete_clid`, `nfs4_record_revoke`, `nfs4_check_deleg_reclaim`, `nfs4_recovery_init`, `nfs4_recovery_shutdown`, `load_recovery_param_from_conf`, and cluster helpers such as `nfs_release_nlm_state` and `nfs_release_v4_clients`.

Control flow: Initialization selects FS, FS_NG, NONE, or RADOS recovery backends and initializes mutex/condition cleanup. `nfs_start_grace` sets or extends the active grace bit, handles sticky-grace references via an atomic status word, logs enforcement, loads recovery client ids, and handles failover events by cancelling blocked NLM work, releasing NLM locks, releasing v4 clients on IP release, or loading takeover records. `nfs_try_lift_grace` compares reclaim completes, client count, NLM status, zero-client handling, grace timeout, backend lift permission, and sticky-grace refs before calling `nfs_end_grace`. Reclaim checks match a client's `cid_recov_tag` to loaded `clid_entry_t` and require prior RECLAIM_COMPLETE for NFSv4.1+. Delegation reclaim converts filehandles to base64url strings and rejects reclaims recorded as revoked.

State and persistence behavior: In-memory recovery state is the client-id list and revoked-filehandle list loaded from the backend, plus grace status flags and counters. Durable state is entirely backend-owned through hooks: `recovery_read_clids`, `add_clid`, `rm_clid`, `add_revoke_fh`, `reclaim_complete`, and `end_grace`. RADOS backends are loaded dynamically when compiled in.

Dependencies and integration points: Integrates with clientid lifecycle, NLM owner/state caches, blocked lock cancellation, FSAL module reclaim callbacks, cluster backends, base64 filehandle encoding, configuration parsing, cleanup registration, and `nfs_param.nfsv4_param` grace/recovery settings. It also uses condition variables to wait for cluster-wide enforcement and sticky-grace ref drain.

Risks: Grace transitions are concurrency-sensitive because active/change/refcount bits share one atomic word. Sticky-grace callers must balance `nfs_get_grace_status` and `nfs_put_grace_status`. `nfs4_cleanup_clid_entries` frees client entries but not the nested revoked-filehandle string list in this file, so backend/list ownership assumptions matter. Cluster release walks live NLM/v4 client hash tables while dropping locks and restarting; missed restarts or ref mistakes can skip or race clients. Reclaim policy depends on correct recovery tags and RFC 8881 reclaim-complete semantics.

Test signals: Validate backend selection errors, grace start/lift with and without sticky grace refs, zero-client grace extension, reclaim-complete counting, v4.1 reclaim rejection without previous complete, revoked delegation reclaim denial, IP release stale-client expiry, RADOS load failure handling, NLM release on failover, and condition wakeups for enforcement/ref drain.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state.c

Purpose: Creates, indexes, links, deletes, and bulk-cleans NFSv4 state objects across file handles, owners, exports, delegations, layouts, locks, and shares.

Important APIs, types, and functions: Main entry points are `_state_add_impl`, `_state_add`, `_state_del_locked`, `state_del`, `get_state_obj_export_owner_refs`, `state_nfs4_state_wipe`, `release_lock_owner`, `release_openstate`, `revoke_owner_delegs`, `state_export_release_nfs4_state`, and `check_and_remove_conflicting_client`. The code manipulates `state_t`, `state_hdl`, `state_owner_t`, `gsh_export`, and FSAL `fsal_obj_handle` operations.

Control flow: `_state_add` validates owner type against state type and takes the file state lock. `_state_add_impl` validates export readiness, allocates FSAL state if needed, enforces per-client open-state limits, initializes the mutex and stateid `other`, inserts into stateid/object hash tables, then links the state into export, file, and owner lists while taking object/export/owner references. It also updates client open counters, gsh-client stats, and write-delegation flags. Deletion first removes the state from the stateid hash to win races, then under appropriate locks detaches owner, lock/share, delegation, export, and file list state, closes the FSAL state with `close2`, updates counters, and drops sentinel/object/export refs. Bulk cleanup iterates owners or export state lists, taking safe refs before dropping list locks and restarting scans after destructive operations.

State and persistence behavior: State is in-memory but has multiple indexes: `ht_state_id`, `ht_state_obj`, file `list_of_states`, owner state lists, export state lists, optional debug global list, share lock lists, and delegation flags on the file state handle. Persistence is indirect through recovery/clientid/delegation code; this file ensures FSAL state is closed before memory is freed.

Dependencies and integration points: Depends on `nfs4_state_id.c` for stateid hash operations, FSAL allocation/close/ref APIs, export manager refs, op context export switching, pNFS layout return, delegation revoke helpers, open-owner cache, clientid counters, and NFS parameter limits. It is called by open/lock/delegation/layout protocol operations and by expiry/recovery paths.

Risks: Correct lock order is central: file `STATELOCK`, state mutex, owner mutex, export lock, and op-context export refs must not deadlock. The delete path intentionally removes hash visibility before list teardown; any caller using stale `state_t` pointers must hold refs. Open-owner caching retains owner refs after last state and must be uncached correctly. Write delegation bookkeeping keeps a client ref in the file state handle. Bulk export cleanup drops and reacquires locks with restart logic and can fail fatally after repeated errors.

Test signals: Cover add/delete for SHARE, LOCK, DELEG, and LAYOUT; duplicate object-owner insertion failure; per-client open-state limits; owner-ref and object-ref balancing; lock-before-share wipe ordering; open-owner cache retention/uncache; write delegation flag/client ref clearing; export release ordering; and delayed-client conflict cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state_id.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state_id.c

Purpose: Owns NFSv4 stateid construction, display, hash indexing, lookup, deletion, validation, special-stateid handling, lease reservation during stateid checks, and stateid seqid updates.

Important APIs, types, and functions: Global tables are `ht_state_id` keyed by `stateid.other` and `ht_state_obj` keyed by object+owner for SHARE/LOCK states. Entry points include `nfs4_Init_state_id`, `nfs4_BuildStateId_Other`, `nfs4_State_Set`, `nfs4_State_Get_Pointer`, `nfs4_State_Get_Obj`, `nfs4_State_Del`, `nfs4_check_stateid_acquire_state_lock`, `nfs4_Check_Stateid`, `nfs_State_PrintAll`, and `update_stateid_locked`. Helper functions handle all-zero/all-one/current stateids and server-instance epoch validation.

Control flow: Stateid initialization fills all-zero/all-one sentinels and creates both hash tables. New stateids embed the 64-bit clientid plus a per-client stateid counter. `nfs4_State_Set` always indexes by `stateid.other`, and additionally indexes SHARE/LOCK states by object+owner, rolling back the first index if the second collides. Lookups take a state ref under hash latch. Deletion removes `ht_state_id` first, then conditionally removes the object-owner index only if it still points to the same state. Validation handles special stateids, rejects stale server epochs, looks up state and associated object/owner refs, distinguishes missing state from expired client versus stale entry, optionally acquires the file state lock, reserves the client lease, verifies file handle match and seqid ordering, detects replay cases, and updates compound `current_stateid`.

State and persistence behavior: Stateid data is transient in hash tables and `state_t`; no durable persistence is done here. The `other` field encodes clientid and state counter, while `seqid` is incremented by `update_stateid_locked` with wraparound avoidance. Lease reservation is recorded in `compound_data_t->preserved_clientid` so later compound processing can release/update the lease.

Dependencies and integration points: Uses clientid lookup/error mapping, lease reservation/expiry, revoked-delegation checks, FSAL object comparison and handle keys, owner comparison, CityHash, global unique server id, NFSv4 compound state, and trace/log infrastructure. It is central to every protocol operation that accepts a stateid.

Risks: Stateid validation is a high-risk concurrency boundary: a state may be found in the hash but have object/owner/export torn down concurrently. The optional `should_lock` path rechecks `state_owner` after waiting for `STATELOCK` to prevent CLOSE races. Special CLOSE replay handling preserves leases differently for v4.0 and v4.1. Seqid arithmetic must distinguish old, bad, current, and replay including wraparound from `0xffffffff` to 1. `ht_state_obj` uses object handle hash material and owner comparison, so any object/owner mutation after insertion would break lookup invariants.

Test signals: Exercise special all-zero/all-one/current stateids, stale epoch handling for v4.0 versus v4.1, missing state with valid/expired client, CLOSE replay paths, revoked delegation detection, file-handle mismatch, OLD_STATEID/BAD_STATEID/REPLAY seqid paths, lock-acquire race with concurrent close, duplicate object-owner insertion rollback, and seqid wraparound update.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nfs4_state_id.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nlm_owner.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nlm_owner.c

Purpose: Implements NSM client, NLM client, and NLM lock-owner caches used by Network Lock Manager state, including monitor integration, RPC callback client lifetime, and owner lookup/deduplication.

Important APIs, types, and functions: Global tables are `ht_nsm_client`, `ht_nlm_client`, and `ht_nlm_owner`. Key functions include `Init_nlm_hash`, `get_nsm_client`, `inc_nsm_client_ref`, `dec_nsm_client_ref`, `get_nlm_client`, `inc_nlm_client_ref`, `dec_nlm_client_ref`, `get_nlm_owner`, and the compare/hash/display helpers for `state_nsm_client_t`, `state_nlm_client_t`, and `state_owner_t` NLM owners.

Control flow: NSM lookup builds a caller-name key either from the protocol caller name or canonicalized caller address, then deduplicates through `ht_nsm_client`; `CARE_MONITOR` starts NSM monitoring before returning. NLM client lookup keys on NSM client, local server address from `getsockname`, transport type, and NLM caller name; it refs the NSM client and can also monitor. NLM owners key on NLM client, svid, and opaque owner handle, then delegate allocation to the generic `get_state_owner` cache with `init_nlm_owner`. Refcount zero paths remove the object from its hash table under a latch and tolerate already-removed or replaced entries.

State and persistence behavior: All owner/client state is in-memory. NSM monitoring is external process/protocol state managed through `nsm_monitor` and `nsm_unmonitor`. NLM clients may own libtirpc callback `CLIENT` handles; TCP callbacks are configured with `CLSET_FD_CLOSE` before `CLNT_DESTROY` to close sockets. There is no direct durable persistence.

Dependencies and integration points: Integrates with `op_ctx->client`, caller addresses, NSM monitor code, libtirpc transports, Ganesha client manager refs, generic state-owner cache, hash latches, and `nfs_param.core_param.nsm_use_caller_name`. NLM recovery release in `nfs4_recovery.c` walks `ht_nlm_client`.

Risks: The NSM key intentionally ignores `ssc_client` and compares only caller name/address, which is required for SM_NOTIFY but can merge clients if caller names are ambiguous. Hash functions are simple byte sums and rely on compare for correctness. `get_nlm_client` assumes `xprt->xp_fd` and `getsockname` are usable; missing local address reduces key quality. Monitor failure must unwind references and likely remove just-created hash entries. Refcount-zero deletion races are expected and handled, but missed refs can leak monitors or callback sockets.

Test signals: Cover caller-name versus address-based NSM keys, SM_NOTIFY-style lookup with no `op_ctx->client`, monitor success/failure unwinding, NLM client keys across transport/local address/caller name, callback client destruction, owner dedup by svid and netobj, and concurrent lookup versus final ref release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nlm_owner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nlm_state.c -->
# sources/user-network-fs/nfs-ganesha/src/SAL/nlm_state.c

Purpose: Manages the NLM state cache for lock and share state records, mapping an NLM owner/export/object/type tuple to a reusable FSAL `state_t`.

Important APIs, types, and functions: The global `ht_nlm_states` stores NLM `state_t` entries. Entry points are `Init_nlm_state_hash`, `get_nlm_state`, and `dec_nlm_state_ref`, with compare/hash/display helpers `compare_nlm_state`, `nlm_state_value_hash_func`, and `nlm_state_rbt_hash_func`.

Control flow: `get_nlm_state` builds a key from requested state type, owner, current export, NSM state sequence, and object. It latches the hash table, returns an existing state with an atomic ref if possible, or for `CARE_MONITOR` deletes an old state whose `state_seqid` no longer matches the monitor state before creating a replacement. `CARE_NOT` and `CARE_OWNER` do not create new state. Creation allocates FSAL state, initializes state mutex and lock list, takes an active object ref, inserts under the existing latch, takes an export ref, and returns the state. `dec_nlm_state_ref` removes the state from the hash at refcount zero, releases the export, closes FSAL state against the object if still live, destroys the mutex, frees state memory, and drops object refs.

State and persistence behavior: NLM state is in-memory only and keyed by owner/object/export/type. Lock state initializes `state_data.lock.state_locklist`; share state is distinguished in hashing by complementing the hash value. There is no direct recovery persistence in this file; NSM/NLM notification and recovery drive state removal elsewhere.

Dependencies and integration points: Depends on FSAL `alloc_state`, `close2`, and object refs, export refs, NLM owners from `nlm_owner.c`, CityHash, hash latches, LTTng state tracepoints, and `op_ctx` export/FSAL context. NLM lock/share operations call this to bind protocol owners to FSAL state.

Risks: Hashing depends on `state_owner` and `state_obj` being adjacent fields in `state_t`, as stated in comments; struct layout changes could silently break hashing. `CARE_MONITOR` intentionally discards stale monitor-state entries, which is necessary after client reboot but can race with active references. Refcount-zero deletion must close FSAL state before freeing; object reference handling uses both a temporary ref and an active ref. Display output is minimal, reducing diagnostic value during hash collisions or leaks.

Test signals: Cover creating versus finding existing lock/share state, `CARE_NOT`/`CARE_OWNER` no-create behavior, monitor-state mismatch replacement, refcount deletion races, FSAL close invocation, object/export ref balancing, and hash/compare distinction between NLM lock and share state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/SAL/nlm_state.c -->
