# Chunk Research: sources/os/linux/linux-stable/fs/nfs/nfs4proc.c lines 1-9526

## Scope

This chunk covers the beginning of the Linux stable NFSv4 client procedure file through the start of `nfs4_free_reclaim_complete_data`. It contains the bulk of client-side NFSv4 procedure machinery: attribute bitmaps, error/recovery handling, NFSv4.1 sequence-slot handling, OPEN/CLOSE stateid management, metadata and namespace operations, page I/O setup, ACL/security-label xattrs, SETCLIENTID/EXCHANGE_ID/session setup, delegation return, locking, migration/referral helpers, lease renewal, and the beginning of `RECLAIM_COMPLETE`.

## Primary APIs and Entry Points

- Error/recovery: `nfs4_map_errors`, `nfs4_handle_exception`, `nfs4_async_handle_exception`, and `nfs4_async_handle_error` translate protocol errors, schedule state/session/lease/migration recovery, delay retryable operations, and preserve async retry state.
- Sequence/session wrappers: `nfs4_init_sequence`, `nfs4_setup_sequence`, `nfs41_sequence_done`, `nfs4_sequence_done`, `nfs4_call_sync_sequence`, `nfs4_call_sync`, and `nfs4_do_call_sync` attach SEQUENCE state to RPC tasks and run compounds through minor-version-specific callbacks.
- OPEN/CLOSE and stateid APIs: `nfs4_do_open`, `nfs4_atomic_open`, `nfs4_close_context`, `nfs4_do_close`, `nfs4_open_reclaim`, `nfs4_open_expired`, `nfs41_open_expired`, `nfs4_open_delegation_recall`, and `update_open_stateid` manage open owners, seqids, open/delegation stateids, cached opens, recoveries, and open-downgrade/close.
- VFS-facing metadata/namespace operations: `nfs4_server_capabilities`, `nfs4_proc_get_rootfh`, `nfs4_proc_getattr`, `nfs4_proc_setattr`, lookup/lookupp/access/readlink/create/remove/rmdir/link/symlink/mkdir/readdir/mknod/statfs/fsinfo/pathconf wrappers expose NFSv4 compounds to higher NFS/VFS layers.
- I/O setup/completion: `nfs4_proc_read_setup`, `nfs4_proc_pgio_rpc_prepare`, `nfs4_read_done`, `nfs4_proc_write_setup`, `nfs4_write_done`, `nfs4_proc_commit_setup`, and `nfs4_proc_commit` select current stateids, handle READ_PLUS fallback, request cache-consistency attributes, and restart RPCs on stale stateids.
- ACL/security/xattr APIs: `nfs4_proc_get_acl`, `nfs4_proc_set_acl`, NFSv4 ACL xattr handlers, optional security-label handlers, and NFSv4.2 user-xattr handlers bridge Linux xattr calls to NFSv4 ACL/security-label and NFSv4.2 xattr RPCs.
- Client/session lifecycle: `nfs4_proc_setclientid`, `nfs4_proc_setclientid_confirm`, `nfs4_proc_exchange_id`, `nfs4_test_session_trunk`, `nfs4_destroy_clientid`, `nfs4_proc_get_lease_time`, `nfs4_proc_create_session`, `nfs4_proc_destroy_session`, `nfs41_proc_async_sequence`, and `nfs4_proc_sequence`.
- Locking/leases: `nfs4_proc_lock`, `nfs4_proc_setlease`, `nfs4_lock_reclaim`, `nfs4_lock_expired`, `nfs41_lock_expired`, and `nfs4_lock_delegation_recall` implement GETLK/SETLK/UNLCK, lock stateid recovery, delegated lock caching, callback wakeups, and local file leases backed by delegations.

## Control Flow

- The file uses a consistent two-layer operation pattern: an internal `_nfs4_*` helper builds protocol args/results and calls `nfs4_call_sync` or starts an async `rpc_task`; the public wrapper loops through `nfs4_handle_exception` while `exception.retry` remains set.
- `nfs4_do_handle_exception` is the central error switch. It converts stateid, lease, session, migration, delay, server-grace, idmapping, and moved errors into recovery scheduling, retry, delay, or final Linux errno mapping.
- NFSv4.1 `SEQUENCE` processing is task-callback driven. Prepare callbacks allocate/attach slots with `nfs4_setup_sequence`; done callbacks call `nfs41_sequence_done`/`nfs4_sequence_done`; slot release increments slot sequence numbers, wakes waiters, and may notify the server of lower highest-used slot IDs.
- OPEN flow acquires a state owner, performs client lease recovery, returns incompatible delegations, builds `nfs4_opendata`, optionally reuses cached open/delegation state, sends `OPEN`, optionally sends `OPEN_CONFIRM`, maps attrs/fh to inode/state, processes returned delegations, validates access, parses pNFS open layoutget results, and attaches the open context.
- CLOSE flow computes whether it can use `OPEN_DOWNGRADE` or must use `CLOSE`, synchronizes the outgoing open stateid, waits for return-on-close layoutreturn if needed, optionally requests close-to-open consistency attrs, and clears or updates open-state flags when the RPC completes.
- Read/write RPC prepare chooses a fresh read/write stateid and rejects bad contexts. Completion callbacks detect stateid-expired/old/openmode errors and restart if local current stateid differs from the one sent.
- NFSv4.0 client identity uses `SETCLIENTID` and `SETCLIENTID_CONFIRM`; NFSv4.1+ identity uses `EXCHANGE_ID`, optional SP4_MACH_CRED negotiation, `CREATE_SESSION`, slot table setup, connection binding/trunk probing, and periodic `SEQUENCE` lease renewal.

## State and Data Structures

- `nfs_client` state touched here includes clientid, exchange flags, seqid, owner id, acceptor string, last renewal time, session pointer/state, server owner/scope/implementation IDs, state-protection mode flags, recovery flags, transport/trunking state, and lock waitqueue.
- `nfs_server` state is populated with server caps, supported attr bitmasks, no-label bitmasks, cache-consistency bitmasks, exclusive-create bitmasks, ACL masks, fh expiry type, fsid, pNFS block size/layout driver, case-sensitivity flags, and delegation timestamp/open argument capabilities.
- `nfs4_state` carries open/delegation stateids, mode counters (`n_rdonly`, `n_wronly`, `n_rdwr`), open/lock/delegation flags, lock-state lists, waitqueues, owner references, seqlock, and state locks.
- Per-RPC callback payloads include `nfs4_opendata`, `nfs4_closedata`, `nfs4_createdata`, `nfs4_delegreturndata`, `nfs4_lockdata`, `nfs4_unlockdata`, `nfs4_sequence_data`, `nfs4_get_lease_time_data`, and `nfs4_reclaim_complete_data`.
- Attribute bitmasks are actively adjusted. `nfs4_bitmap_copy_adjust` suppresses delegated attributes from GETATTR-like requests; `nfs4_bitmask_set` adds invalidated attributes back for cache-consistency requests and masks them by server support.

## Dependencies and Risks

- Major dependencies are SUNRPC task/credential/transport APIs, NFS inode/fh/fattr/open-context/state-manager helpers, delegation and callback code, pNFS helpers, LSM security-label APIs, VFS locking/xattr APIs, and NFSv4.1 session code.
- Stateid ordering is fragile; the client relies on server stateid seqids plus local seqlock/waitqueue ordering to serialize concurrent OPEN, CLOSE, LOCK, and LOCKU state transitions.
- Async cancellation paths are correctness-sensitive because successful-but-cancelled opens or locks may need follow-up close/unlock cleanup.
- Delegations change behavior across opens, locks, getattr bitmasks, timestamp handling, and recovery paths.
- Session recovery is tightly coupled to SEQUENCE errors; bad/misordered sequence handling can restart calls, probe state, drain slots, release transports, and wake waiters.
- The `nfs4_lock_delegation_recall` loop compares one condition against `-NFSERR_GRACE` after checking `-NFS4ERR_GRACE`; this looks suspicious and should be verified against surrounding NFS error constants.
- This chunk ends mid-function at `nfs4_free_reclaim_complete_data`, so `RECLAIM_COMPLETE` cleanup/runner logic is incomplete here.

## Cross-Chunk References

- Lines 9527-10750 continue `nfs4_free_reclaim_complete_data`, finish `RECLAIM_COMPLETE`, and cover remaining pNFS layout, stateid test/free, minor-version operation tables, client ops, and xattr handler registration.
- Forward declarations for `nfs41_test_stateid` and `nfs41_free_stateid` are used in this chunk but implemented after this range.
- pNFS calls made here require the later chunk and `pnfs.*` files for full behavior.
- NFSv4.2 helpers referenced here, such as `nfs42_proc_getxattr`, `nfs42_proc_setxattr`, `nfs42_proc_listxattrs`, `nfs42_proc_removexattr`, and READ_PLUS support, are implemented in NFSv4.2-specific source files or later registration code.