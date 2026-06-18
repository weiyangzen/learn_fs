# Chunk Research: sources/os/linux/linux/fs/nfs/nfs4proc.c lines 1-9520

## Scope

This chunk covers the beginning through the NFSv4.1 `RECLAIM_COMPLETE` path in `fs/nfs/nfs4proc.c`. It includes most core client-side NFSv4 procedure wrappers: error/recovery handling, sequence-slot management, OPEN/CLOSE stateid handling, metadata operations, directory operations, read/write/commit setup, ACL/security-label xattrs, delegation return, locking, referrals/migration helpers, `SETCLIENTID`, `EXCHANGE_ID`, session creation/destruction, lease renewal, and reclaim-complete. The next chunk begins in the pNFS layout operation area immediately after this range.

## Primary APIs and Entry Points

- Error and retry APIs: `nfs4_map_errors`, `nfs4_handle_exception`, `nfs4_async_handle_exception`, and `nfs4_async_handle_error` normalize negative NFSv4 protocol statuses into Linux errno values or schedule recovery/retry/delay behavior.
- Session/sequence APIs: `nfs4_init_sequence`, `nfs4_setup_sequence`, `nfs41_sequence_done`, `nfs4_sequence_done`, `nfs4_call_sync`, and `nfs4_call_sync_sequence` attach NFSv4.1 sequence slots to RPC tasks and drive synchronous compounds through the minor-version operation table.
- OPEN/CLOSE APIs: `nfs4_do_open`, `nfs4_atomic_open`, `nfs4_close_context`, `nfs4_do_close`, `nfs4_open_reclaim`, `nfs4_open_expired`, and `nfs4_open_delegation_recall` allocate `nfs4_opendata`, run `OPEN`/`OPEN_CONFIRM`, update stateids, and recover opens after reboot, expiration, or delegation recall.
- Metadata and namespace APIs: `nfs4_server_capabilities`, `nfs4_proc_get_rootfh`, `nfs4_proc_getattr`, `nfs4_proc_setattr`, lookup/lookupp/access/readlink/create/remove/rmdir/link/symlink/mkdir/readdir/mknod/statfs/fsinfo/pathconf wrappers expose NFSv4 compounds to the VFS-facing NFS client ops.
- I/O setup APIs: `nfs4_proc_read_setup`, `nfs4_proc_pgio_rpc_prepare`, `nfs4_read_done`, `nfs4_proc_write_setup`, `nfs4_write_done`, `nfs4_proc_commit_setup`, and `nfs4_proc_commit` prepare stateids, sequence args, bitmasks, callbacks, and state-protection credentials for page I/O and COMMIT.
- ACL/xattr APIs: `nfs4_proc_get_acl`, `nfs4_proc_set_acl`, NFSv4 ACL xattr handlers, optional security-label handlers, and NFSv4.2 user-xattr helpers bridge Linux xattr APIs to NFSv4 `GETACL`, `SETACL`, and NFSv4.2 xattr operations.
- Client/session lifecycle APIs: `nfs4_proc_setclientid`, `nfs4_proc_setclientid_confirm`, `nfs4_proc_exchange_id`, `nfs4_proc_create_session`, `nfs4_proc_destroy_session`, `nfs4_destroy_clientid`, `nfs4_proc_get_lease_time`, `nfs41_proc_async_sequence`, `nfs4_proc_sequence`, and `nfs41_proc_reclaim_complete`.
- Locking and lease APIs: `nfs4_proc_lock`, `nfs4_proc_setlease`, `nfs4_lock_reclaim`, `nfs4_lock_expired`, and `nfs4_lock_delegation_recall` manage POSIX/flock-style locks, lock stateids, lock retries, delegation-cached locks, and callback wakeups.

## Control Flow

- Most public wrappers follow a two-layer pattern: an internal `_nfs4_*` routine builds a compound argument/result pair and calls `nfs4_call_sync` or launches an async `rpc_task`; an outer `nfs4_*` routine loops through `nfs4_handle_exception` until `exception.retry` is false.
- `nfs4_do_handle_exception` is the central control point for protocol errors. It schedules stateid recovery, lease recovery, session recovery, migration recovery, lease-moved recovery, or bounded delay depending on the status. It treats session sequence errors as already handled by `nfs41_sequence_process`.
- NFSv4.1 sequencing is integrated into RPC callbacks. Prepare callbacks call `nfs4_setup_sequence`; done callbacks call `nfs41_sequence_done` or `nfs4_sequence_done`; slots are released only after the sequence state machine records success, retries, sequence misordering, or session reset.
- `nfs41_sequence_process` handles `SEQUENCE`-level outcomes, including slot acking, target slot updates, `NFS4ERR_DELAY`, false retry, bad slot, sequence misordering, dead/bad sessions, and draining the slot table before scheduling session recovery.
- OPEN flow starts with state-owner acquisition and lease recovery, optionally uses cached open/delegation state, sends `OPEN`, optionally sends `OPEN_CONFIRM`, maps returned file handles/attrs to an inode/state, processes delegations, performs access checks, and attaches the open context.
- CLOSE flow allocates `nfs4_closedata`, selects `CLOSE` versus `OPEN_DOWNGRADE` based on remaining per-mode open counts, optionally folds pNFS return-on-close layoutreturn args into the compound, requests close-to-open consistency attributes when no delegation covers reads, then updates or clears the open stateid.
- Namespace operations update local cache state after successful server change-info responses. `nfs4_update_changeattr` invalidates directory data, nlink, access, ACL, size, xattr, and other inode fields depending on the operation and whether attributes are delegated.
- Read/write paths choose a current read/write stateid during RPC prepare. Done callbacks restart the task if the server reports an expired/old/openmode stateid and the locally selected current stateid has changed.
- Client setup differs by minor version: NFSv4.0 uses `SETCLIENTID`/`SETCLIENTID_CONFIRM`; NFSv4.1+ uses `EXCHANGE_ID`, state-protection negotiation, `CREATE_SESSION`, slot-table setup, connection binding, trunk discovery, and `SEQUENCE` lease renewal.

## State and Data Structures

- `nfs_client` state touched here includes clientid, exchange flags, session pointer, slot table, sequence id, state-protection flags, owner id string, acceptor string, last renewal timestamp, session-established bit, migration/recovery flags, server owner/scope/implementation IDs, and lock waitqueue.
- `nfs_server` state is updated with server capability flags, supported attribute bitmasks, security-label/no-label bitmasks, cache-consistency bitmasks, exclusive-create bitmasks, ACL support mask, file-handle expiry type, filesystem id, pNFS block size, and pNFS layout driver.
- `nfs4_state` tracks open and delegation stateids, open mode counters (`n_rdonly`, `n_wronly`, `n_rdwr`), open/delegated/lock flags, lock-state list, waitqueue, seqlock, and owner reference. This chunk carefully serializes stateid changes with owner locks, seqlocks, state locks, waitqueues, and RCU.
- `nfs4_opendata`, `nfs4_closedata`, `nfs4_lockdata`, `nfs4_unlockdata`, `nfs4_delegreturndata`, and `nfs4_reclaim_complete_data` are per-RPC callback payloads. They hold args, results, sequence state, inode/state references, credentials, timestamps, retrans counters, and pNFS layoutreturn sub-arguments where needed.
- Attribute bitmasks are not static request constants in practice. Helpers trim delegated attributes from `GETATTR` requests and add invalidated attributes back into close/write/delegreturn cache-consistency requests.
- ACL state is cached in `NFS_I(inode)->nfs4_acl`, with small ACL bodies copied into a kmalloc buffer and large/length-only ACLs represented as uncached length metadata.

## Dependencies and Integration Points

- SUNRPC dependencies: `rpc_run_task`, `rpc_call_sync`, `rpc_wait_for_completion_task`, `rpc_restart_call_prepare`, `rpc_sleep_on`, `rpc_delay`, transport release, xprt iteration, trunk add/remove, auth flavor and credential APIs.
- NFS core dependencies: inode/fh/fattr helpers, open context helpers, access cache, attr invalidation, dentry verifier/splice behavior, revalidation, sillyrename/delegation-on-close hooks, state owner/seqid allocation, and state manager scheduling.
- NFSv4 support modules: `nfs4_fs.h`, `delegation.h`, `callback.h`, `nfs4session.h`, `nfs40.h`, `nfs42.h`, `pnfs.h`, `nfs4idmap.h`, `sysfs.h`, and `nfs4trace.h`.
- pNFS integration appears throughout but is not fully defined in this chunk: open layoutget preparation/parsing, return-on-close, layoutreturn waiting, write/commit data-server client handling, layout driver selection from `FSINFO`, and pNFS cleanup state protection.
- LSM/security dependencies include `security_dentry_init_security`, `security_release_secctx`, `security_ismaclabel`, optional `CONFIG_NFS_V4_SECURITY_LABEL`, and security-label fattr handling.
- VFS/locking dependencies include `struct inode`, `dentry`, `file_lock`, generic file leases, Linux lock manager APIs, inode semaphores, dcache alias pruning, and xattr handler callbacks.

## Risks and Subtle Behaviors

- Stateid ordering is race-prone. The code relies on server stateid seqids, local seqlocks, owner locks, and waitqueues to process concurrent OPEN/CLOSE/OPEN_DOWNGRADE/LOCK/LOCKU updates in server order.
- Error handling can intentionally hide protocol details from userspace. Unhandled NFSv4 protocol errors are mapped to generic errno values, often `-EIO`, after recovery attempts.
- Async cancellation paths must clean up successful-but-cancelled state by issuing close/unlock operations. Several release callbacks conditionally close state or unlock a lock if the RPC completed after local cancellation.
- Delegations alter both correctness and performance. Cached opens/locks avoid RPCs, but incompatible delegation returns, revoked delegation cleanup, and delegated timestamp return paths must be synchronized with state recovery and pNFS layout return.
- Attribute cache correctness depends on precise bitmask adjustment. Requesting too little risks stale metadata; requesting unsupported or delegated attributes can cause server errors or unnecessary RPC payload.
- Security fallback paths are deliberate. Root lookup and SECINFO retry across auth flavors, and the SP4_MACH_CRED fallback from `SP4_MACH_CRED` to `SP4_NONE`, are compatibility paths for real servers.
- NFSv4.1 session recovery is coupled to sequence-slot errors. Bad session/slot/misordered sequence handling can drain slot tables, trigger manager recovery, and cause task restarts with or without delay.
- Some loops use sleep/retry on server `DELAY`, `GRACE`, or busy states. Soft-error mounts are bounded by `nfs_delay_retrans`; other recovery paths can continue until the state manager resolves the condition or a fatal signal occurs.
- The delegation recall lock helper contains a visible typo-like comparison to `-NFSERR_GRACE` in a loop condition after checking `-NFS4ERR_GRACE`; this should be reviewed against available constants in adjacent headers before treating it as a bug.

## Cross-Chunk References

- The range ends just before the pNFS layoutget/layoutreturn/layoutcommit implementations. This chunk calls into pNFS helpers and starts the `nfs4_layoutget_prepare` / `nfs4_layoutget_done` area after line 9520, so later chunk(s) must complete the layout operation story.
- Minor-version operation tables and final `nfs_v4_clientops`, inode ops, xattr handler arrays, and clone-server wiring are outside this chunk but are referenced by many functions through `cl_mvops`, `nfs4_procedures`, and exported wrapper functions.
- NFSv4.1 `test_stateid` and `free_stateid` are forward-declared and called for expired/revoked state cleanup in this chunk; their implementations appear after this range.
- NFSv4.2 xattr and read-plus support is partially represented here through guards and calls to `nfs42_proc_*`; the procedure implementations live in NFSv4.2-specific files or later code.
- Folder-level and final per-file synthesis should merge this chunk with the trailing part of `nfs4proc.c` to cover pNFS layouts, stateid test/free, minor-version ops tables, client ops registration, and xattr handler arrays.