# sources/distributed-fs/ceph-client/fs/nfsd/nfs4state.c

## Purpose

`nfs4state.c` is the Linux NFSD NFSv4 state engine. It owns client identity, sessions, duplicate-reply replay state, open owners, lock owners, open/lock/delegation stateids, lease/grace-period expiry, reclaim tracking, and state cleanup for per-network-namespace NFSv4 service instances. It is the implementation behind protocol operations such as `SETCLIENTID`, `EXCHANGE_ID`, `CREATE_SESSION`, `SEQUENCE`, `OPEN`, `CLOSE`, `LOCK`, `LOCKT`, `LOCKU`, `DELEGRETURN`, `TEST_STATEID`, `FREE_STATEID`, `RECLAIM_COMPLETE`, `DESTROY_SESSION`, and `DESTROY_CLIENTID`.

The file bridges wire protocol state to VFS state: it hashes NFS filehandles to `struct nfs4_file`, pins `struct nfsd_file` objects with share access and deny accounting, creates POSIX byte-range locks with NFSD lock-manager callbacks, creates kernel leases for delegations, and interacts with pNFS and server-to-server copy state.

## Important Types And State

- `struct nfs4_client`: per NFS client identity. It is keyed by generated clientid and opaque client owner name, has confirmed/unconfirmed placement, sessions, stateid idr, delegation lists, callback state, credential constraints, reclaim flags, active/courtesy/expirable state, and an nfsdfs debug directory.
- `struct nfsd4_session`, `struct nfsd4_slot`, `struct nfsd4_conn`: NFSv4.1+ session tracking. Sessions are hashed by sessionid, hold forechannel slot caches for SEQUENCE replay, have backchannel security/program data, and bind to one or more RPC transports.
- `struct nfs4_stid`: common stateid header embedded in open/lock/delegation/layout state. It carries refcount, type (`SC_TYPE_OPEN`, `SC_TYPE_LOCK`, `SC_TYPE_DELEG`, `SC_TYPE_LAYOUT`), status bits (`SC_STATUS_CLOSED`, `REVOKED`, `ADMIN_REVOKED`, `FREEABLE`, `FREED`), idr-backed wire stateid, owning client, associated file, and free callback.
- `struct nfs4_ol_stateid`: open or lock stateid. It links to file, owner, child lock stateids, per-client open/delegation state, share access and deny bitmaps, optional parent open stateid for locks, and a mutex for stateid-changing operations.
- `struct nfs4_stateowner`, `struct nfs4_openowner`, `struct nfs4_lockowner`: protocol owner strings with replay cache and seqid. Open owners are retained briefly on a close LRU for NFSv4.0 CLOSE replay. Lock owners hold blocked-lock callback records.
- `struct nfs4_file`: global per-filehandle file state, keyed by inode through an `rhltable` and then disambiguated by filehandle. It tracks open/lock stateids, delegations, share deny union, open `nfsd_file` descriptors for read/write/read-write, delegation file handles, aliasing, and pNFS layouts.
- `struct nfs4_delegation`: delegation stateid plus per-file/per-client linkage, recall LRU state, callback objects for `CB_RECALL` and `CB_GETATTR`, delegated timestamp state, write/read type, and retry flags.
- `struct nfsd_net`: per-netns owner of client hash tables, session hash table, client and close LRUs, delegation recall LRU, blocked-lock LRU, laundromat work, grace/lease timers, client tracking hooks, and COPY_NOTIFY stateid idr.

## Key APIs And Function Groups

- Lifecycle and slabs: `nfsd4_create_laundry_wq`, `nfsd4_destroy_laundry_wq`, `nfsd4_init_slabs`, `nfsd4_free_slabs`, `nfs4_state_start`, `nfs4_state_shutdown`, `nfs4_state_start_net`, `nfs4_state_shutdown_net`.
- Client/session protocol: `nfsd4_setclientid`, `nfsd4_setclientid_confirm`, `nfsd4_exchange_id`, `nfsd4_create_session`, `nfsd4_sequence`, `nfsd4_sequence_done`, `nfsd4_bind_conn_to_session`, `nfsd4_backchannel_ctl`, `nfsd4_destroy_session`, `nfsd4_destroy_clientid`, `nfsd4_reclaim_complete`, `nfsd4_renew`.
- Open path: `nfsd4_process_open1` validates/open-owner setup; `nfsd4_process_open2` hashes the file, finds or initializes an open stateid, checks delegation claims, acquires VFS files, applies truncate/share state, returns stateid, and optionally grants a delegation.
- Close/downgrade/confirm: `nfsd4_open_confirm`, `nfsd4_open_downgrade`, `nfsd4_close`, `move_to_close_lru`, and `nfsd4_cleanup_open_state`.
- Stateid validation and current-stateid handling: `nfsd4_lookup_stateid`, `nfs4_preprocess_stateid_op`, `nfs4_preprocess_seqid_op`, `nfsd4_test_stateid`, `nfsd4_free_stateid`, plus the `nfsd4_set_*stateid` and `nfsd4_get_*stateid` helpers.
- Locking: `nfsd4_lock`, `nfsd4_lockt`, `nfsd4_locku`, `nfsd4_release_lockowner`, `check_for_locks`, `nfsd_posix_mng_ops`, and blocked-lock `CB_NOTIFY_LOCK` helpers.
- Delegation and lease handling: `nfs4_set_delegation`, `nfs4_open_delegation`, `nfsd_break_deleg_cb`, `nfsd_break_one_deleg`, `nfsd4_delegreturn`, `nfsd4_deleg_getattr_conflict`, `nfsd_get_dir_deleg`, `nfsd_update_cmtime_attr`.
- Cleanup and expiry: `nfs4_laundromat`, `laundromat_main`, `courtesy_client_reaper`, `deleg_reaper`, `nfsd4_state_shrinker_worker`, `nfsd4_revoke_states`, `expire_client`, `destroy_client`.
- Reclaim and persistence integration: `nfs4_client_to_reclaim`, `nfsd4_find_reclaim_client`, `nfs4_has_reclaimed_state`, `nfs4_check_open_reclaim`, `nfs4_release_reclaim`, and calls to `nfsd4_client_record_*`/`nfsd4_record_grace_done`.

## Control Flow

Client establishment has two versions. NFSv4.0 creates an unconfirmed client in `nfsd4_setclientid`, then confirms or replaces it in `nfsd4_setclientid_confirm`; callback address setup is parsed from SETCLIENTID. NFSv4.1+ uses `nfsd4_exchange_id` to compare client owner name, verifier, credentials, update flags, machine credentials, and existing state, then `nfsd4_create_session` to validate channel attributes, allocate slots, cache CREATE_SESSION replay data, confirm the client, initialize the session, and bind the transport.

Every v4.1+ compound begins with `nfsd4_sequence`. It looks up and references the session, validates slot seqid, request size, op count, and bound connection, reconstructs a replay response when appropriate, otherwise marks a slot in use and restricts the XDR response buffer to the negotiated cached or uncached size. `nfsd4_sequence_done` stores the reply in the slot cache and drops the session reference.

OPEN is split. `nfsd4_process_open1` resolves or allocates the open owner, performs seqid/replay checks for v4.0, handles delegation claim inputs, and allocates provisional file/open state. `nfsd4_process_open2` inserts or finds the `nfs4_file`, checks existing delegation state for `CLAIM_DELEGATE_CUR`, finds or initializes the open stateid, acquires VFS access with share deny enforcement, applies truncate, updates stateid generation, and attempts delegation issuance. Existing opens become upgrades; new opens can be suppressed when the client requested open-xor-delegation and a delegation was granted.

CLOSE and related operations use stateid lookup plus owner seqid replay protection. `nfsd4_close` marks the open stateid closed, unhashes it and child locks, and for NFSv4.0 moves the stateid into the close LRU so replays can be recognized for a lease period. NFSv4.1+ releases state immediately after unhashing. `nfsd4_open_downgrade` verifies requested access/deny are subsets of tracked bitmaps and decrements access accounting.

LOCK creates or finds a lock owner and lock stateid, validates the parent open stateid for new locks, checks grace/reclaim mode, chooses a readable or writable `nfsd_file`, builds a `struct file_lock`, and calls `vfs_lock_file`. Blocking lock requests under sessions may use `FL_SLEEP`; NFSD stores a `struct nfsd4_blocked_lock` on both the owner and a netns LRU so `lm_notify` can send `CB_NOTIFY_LOCK` and the laundromat can expire stale blocked entries. LOCKT uses a temporary open to call `vfs_test_lock`; LOCKU sends a POSIX unlock through `vfs_lock_file`.

Delegation flow starts from OPEN or directory delegation. NFSD chooses read/write delegation type, checks callback viability, grace period, existing conflicts, setuid write hazards, filehandle/dentry races, export lock support, and per-client duplicate delegations. It installs a kernel lease with `kernel_setlease`, hashes the delegation under `deleg_lock`, and returns its stateid. Lease breaks call `nfsd_break_deleg_cb`, mark conflict state, schedule `CB_RECALL`, and put recalled delegations on `del_recall_lru`. Failure to return before lease timeout leads to revocation by the laundromat.

## State And Persistence Behavior

State is mostly in-memory, indexed by per-netns hash tables, idrs, rbtree name tables, LRUs, and the global file `rhltable`. Persistent behavior is limited to client recovery records and grace completion via the `nfsd4_client_tracking_*` operations. On startup, reclaim records decide whether a client may reclaim previous state; during grace `locks_start_grace` blocks normal opens/locks, `RECLAIM_COMPLETE` and v4.0 first OPEN help decide when all reclaimers are done, and `nfsd4_end_grace` records grace completion before ending the lock manager grace.

Stateid generation is incremented by `nfs4_inc_and_copy_stateid`, avoiding generation zero. Special stateids are recognized: all-zero, all-one, current stateid, and close stateid. v4.1 current stateid is stored in compound state by setters and substituted by getters when an operation passes the protocol current-stateid token.

The laundromat enforces time-based persistence limits. It ends grace, expires COPY_NOTIFY state, async copies, inactive clients, courtesy clients, admin-revoked v4.0 state, recalled delegations, close replay stateids, and blocked-lock notifications. Courtesy clients preserve state after lease expiry until pressure or conflict makes them expirable, reducing disruption for temporarily disconnected clients.

Client debug state is exposed through nfsdfs client directories: `info`, `states`, and writable `ctl`. Writing `expire\n` to `ctl` forces client expiration and waits until in-flight RPC users are gone and state cleanup is visible.

## Dependencies And Integration Points

- VFS and file cache: `nfsd_file_acquire`, `nfsd_file_acquire_opened`, `nfsd_file_put`, `nfsd_permission`, `fh_verify`, `nfsd_setattr`, `notify_change`, `kernel_setlease`, `vfs_lock_file`, `vfs_test_lock`.
- Lock manager: `locks_start_grace`, `locks_end_grace`, `locks_in_grace`, lease and POSIX lock manager ops, blocked-lock notifications, and `exportfs_cannot_lock`.
- RPC/session layer: `svc_rqst`, `svc_xprt`, xprt users, GSS credential checks, backchannel callback execution, XDR buffer replay, and duplicate reply cache behavior.
- Callback subsystem: `nfsd4_init_cb`, `nfsd4_run_cb`, `nfsd4_try_run_cb`, `nfsd4_probe_callback`, callback op tables for `CB_RECALL`, `CB_RECALL_ANY`, `CB_NOTIFY_LOCK`, and `CB_GETATTR`.
- pNFS: layout state is included in state revocation and nfsdfs state dumps; open/delegation state keeps `nfs4_clnt_odstate` so layouts can be returned per client/file.
- Server-to-server copy: COPY and COPY_NOTIFY stateids use `nn->s2s_cp_stateids`; `find_cpntf_state` maps COPY_NOTIFY state back to the parent open/lock/delegation state.
- Observability: heavy use of tracepoints in `trace.h`, `dprintk`, nfsdfs seq files, callback stats, and ratelimited timestamp update warnings.

## Risks And Edge Cases

- Lock ordering is complex: `client_lock`, per-client `cl_lock`, `deleg_lock`, per-file `fi_lock`, stateid mutexes, inode locks, file lock context locks, and callback work can nest. Several paths intentionally drop locks and retry to avoid races with CLOSE, destruction, or lease callbacks.
- Reference lifetimes are delicate. `nfs4_stid`, stateowners, clients, sessions, delegations, files, blocked locks, and nfsd files have independent refcounts. Early idr insertion with `sc_type == 0`, close replay retention, callback-held refs, and revoked delegation refs are common failure points.
- Share reservations use separate bitmaps for READ/WRITE/BOTH history, not exact access/deny pairs. The source comments note this is intentionally incomplete for some downgrade validation cases.
- Delegation correctness depends on races with VFS opens, setuid/setgid changes, dentry rename/unlink, aliases for one inode with different filehandles, lease breaks, and callback responsiveness. The code often prefers not granting a delegation (`-EAGAIN`) over risking stale delegation state.
- NFSv4.0 and v4.1+ semantics diverge throughout: replay handling, callback channel setup, session replay, close retention, revoked state cleanup, current stateid, machine credentials, and client reclaim completion.
- Memory pressure behavior is active: session slots shrink through a global shrinker; client/delegation shrinkers schedule reapers. Bugs here can cause protocol-visible slot changes, excessive delegation recalls, or unexpected courtesy client expiry.
- `nfs4_transform_lock_offset` documents a protocol compliance limitation for byte-range locks beyond signed 64-bit VFS offsets.
- Administrative revocation and filesystem unmount cleanup must both notify clients later while also dropping kernel file/lock references promptly enough to permit unmount.

## Test Signals

- NFSv4.0 client lifecycle: SETCLIENTID/CONFIRM replay, credential mismatch, verifier mismatch, callback address invalidation, unconfirmed replacement, and CLOSE replay after close LRU retention.
- NFSv4.1+ sessions: EXCHANGE_ID cases, CREATE_SESSION replay slot, SEQUENCE replay cache hit/miss/false retry, bad slot/seqid paths, slot shrink/growth, BIND_CONN_TO_SESSION, DESTROY_SESSION with in-compound session reference.
- OPEN share semantics: read/write/both opens, deny conflicts, courtesy-client conflict resolution, truncate on open, open upgrade, open downgrade invalid subsets, open-xor-delegation, current-stateid propagation.
- Byte-range locks: new and existing lock owners, reclaim during grace, no-grace errors, blocking locks and `CB_NOTIFY_LOCK`, denial owner reporting, LOCKT without open, LOCKU stateid generation bump, lockowner release with held locks.
- Delegations: read/write delegation grants and refusal reasons, recall on conflicting VFS open, DELEGRETURN wakeups, revoked delegation FREE_STATEID, write delegation GETATTR conflict with `CB_GETATTR`, delegated timestamp clamping, directory delegation, delegation limit recall-any behavior.
- Expiry and recovery: grace end after reclaim completion, forced grace end, courtesy client transition and purge, client `ctl` forced expiration, admin revocation by superblock, nfsdfs `info`/`states` output, reclaim record acceptance/rejection after restart.
- Resource cleanup: netns start/shutdown, slab initialization failure unwinding, global rhltable and shrinker teardown, COPY_NOTIFY expiration, async copy reaper integration, pNFS layout return on client/file cleanup.
