# sources/distributed-fs/ceph-client/fs/nfs/nfs4proc.c lines 1-9526

## Scope

This chunk covers the start of the Linux NFSv4 client procedure implementation through the beginning of the NFSv4.1 `RECLAIM_COMPLETE` cleanup callback. It is a large, central control-plane and data-path slice for NFSv4.0, NFSv4.1 sessions, and optional NFSv4.2 extended xattrs. The chunk includes:

- Shared NFSv4 error translation, retry, delay, migration, and recovery handling.
- Attribute bitmask definitions and helpers for GETATTR, OPEN, FSINFO, STATFS, PATHCONF, referrals, ACLs, security labels, and close-to-open consistency.
- NFSv4.1 session slot acquisition, SEQUENCE completion handling, synchronous compound wrappers, lease renewal, session creation/destruction, and transport trunking probes.
- OPEN, OPEN_CONFIRM, OPEN reclaim/expired recovery, delegation processing, open-stateid update/serialization, and CLOSE/OPEN_DOWNGRADE.
- GETATTR, SETATTR, LOOKUP, LOOKUPP, ACCESS, READLINK, CREATE, REMOVE, RENAME, LINK, SYMLINK, MKDIR, READDIR, MKNOD, STATFS, FSINFO, PATHCONF, READ, WRITE, and COMMIT procedure setup/completion.
- ACL, labeled-NFS, and user extended-attribute handlers.
- SETCLIENTID/SETCLIENTID_CONFIRM for v4.0 and EXCHANGE_ID/CREATE_SESSION/BIND_CONN_TO_SESSION/DESTROY_* paths for v4.1+.
- Delegation return, POSIX lock and lock reclaim/expiration handling, lease emulation from delegations, FS_LOCATIONS/migration discovery, FSID_PRESENT, SECINFO, and state-protection negotiation.

The chunk ends at line 9526 inside the declaration/body start of `nfs4_free_reclaim_complete_data()`. The remainder of `RECLAIM_COMPLETE`, pNFS layout operations, TEST_STATEID/FREE_STATEID, later NFSv4.2 procedures, and the final procedure operation tables are outside this chunk and must be reconciled by adjacent chunk reports.

## Purpose

`nfs4proc.c` is the NFSv4 client procedure layer. It translates VFS/NFS client operations into NFSv4 COMPOUND RPC calls, selects the correct NFSv4.0/v4.1/v4.2 protocol behavior, manages stateful protocol objects, and updates local inode/open/lock/delegation/session caches from server replies.

The code in this chunk sits between generic NFS client code and lower-level SUNRPC/XDR machinery. It builds operation arguments and responses, initializes sequence arguments for session-capable minor versions, chooses credentials and machine credentials, retries or schedules recovery on NFSv4 protocol errors, and preserves Linux VFS semantics around open, close, truncate, locking, ACLs, xattrs, referrals, migration, and delegation recall.

## Important APIs, Types, and Data

Important exported or cross-module entry points in this chunk include:

- `nfs4_handle_exception()` and `nfs4_async_handle_error()` convert NFSv4 protocol failures into retry, delay, recovery, or Linux errno outcomes.
- `nfs4_init_sequence()`, `nfs4_setup_sequence()`, `nfs4_sequence_done()`, `nfs41_sequence_done()`, `nfs4_call_sync()`, and `nfs4_call_sync_sequence()` wrap session-aware RPC execution.
- `nfs4_do_open()`, `nfs4_open_reclaim()`, `nfs4_open_expired()`, `nfs4_open_delegation_recall()`, `update_open_stateid()`, `nfs4_do_close()`, and `nfs4_close_context()` manage OPEN/CLOSE and associated stateids.
- Procedure implementations such as `nfs4_proc_getattr()`, `nfs4_proc_setattr()`, `nfs4_proc_lookup()`, `nfs4_proc_access()`, `nfs4_proc_readlink()`, `nfs4_proc_remove()`, `nfs4_proc_rmdir()`, `nfs4_proc_link()`, `nfs4_proc_symlink()`, `nfs4_proc_mkdir()`, `nfs4_proc_readdir()`, `nfs4_proc_mknod()`, `nfs4_proc_statfs()`, `nfs4_proc_fsinfo()`, `nfs4_proc_pathconf()`, and `nfs4_proc_commit()`.
- I/O hooks `nfs4_proc_read_setup()`, `nfs4_read_done()`, `nfs4_proc_pgio_rpc_prepare()`, `nfs4_proc_write_setup()`, `nfs4_write_done()`, `nfs4_proc_commit_setup()`, and `nfs4_commit_done()`.
- ACL and xattr entry points `nfs4_proc_get_acl()`, `nfs4_proc_set_acl()`, the `system.nfs4_acl`, DACL, SACL, labeled security handlers, and optional NFSv4.2 `user.*` xattr handlers.
- Client/session lifecycle entry points `nfs4_proc_setclientid()`, `nfs4_proc_setclientid_confirm()`, `nfs4_proc_exchange_id()`, `nfs4_proc_create_session()`, `nfs4_proc_destroy_session()`, `nfs4_destroy_clientid()`, `nfs4_proc_bind_conn_to_session()`, `nfs4_test_session_trunk()`, `nfs4_proc_sequence()`, and `nfs41_proc_async_sequence()`.
- Delegation and lock entry points `nfs4_proc_delegreturn()`, `nfs4_proc_getlk()`, `nfs4_proc_unlck()`, `nfs4_proc_setlk()`, `nfs4_proc_lock()`, `nfs4_lock_reclaim()`, `nfs4_lock_expired()`, `nfs4_proc_setlease()`, and `nfs4_lock_delegation_recall()`.
- Namespace/migration/security entry points `nfs4_proc_get_rootfh()`, `nfs4_find_root_sec()`, `nfs4_proc_fs_locations()`, `nfs4_proc_get_locations()`, `nfs4_proc_fsid_present()`, and `nfs4_proc_secinfo()`.

Key local data structures are RPC call-state containers:

- `struct nfs4_opendata` carries OPEN/OPEN_CONFIRM arguments, results, dentry/dir/state owner references, create attributes, labels, pNFS layout-open state, and sequence data.
- `struct nfs4_closedata` carries CLOSE/OPEN_DOWNGRADE arguments, optional return-on-close pNFS layoutreturn state, close-to-open fattr state, retransmission counts, and the open state reference.
- `struct nfs4_createdata` packages CREATE-like operations with a temporary file handle and fattr.
- `struct nfs4_delegreturndata`, `struct nfs4_unlockdata`, and `struct nfs4_lockdata` hold asynchronous DELEGRETURN, LOCKU, and LOCK call state.
- `struct nfs4_cached_acl` caches ACL length and optionally inline ACL payload on `struct nfs_inode`.
- `struct nfs41_exchange_id_data`, `struct nfs4_get_lease_time_data`, `struct nfs4_sequence_data`, and `struct nfs4_reclaim_complete_data` hold NFSv4.1 client/session maintenance call state.

Important constant data includes the NFSv4 attribute bitmaps (`nfs4_fattr_bitmap`, `nfs4_pnfs_open_bitmap`, `nfs4_open_noattr_bitmap`, `nfs4_statfs_bitmap`, `nfs4_pathconf_bitmap`, `nfs4_fsinfo_bitmap`, `nfs4_fs_locations_bitmap`) and the `nfs4_sp4_mach_cred_request` state-protection request map.

## Control Flow

Most public procedure wrappers follow a common pattern: build an argument/result pair, initialize sequence arguments with `nfs4_init_sequence()`, issue a synchronous or asynchronous SUNRPC task, process `SEQUENCE` state if needed, update local caches on success, and loop through `nfs4_handle_exception()` on recoverable NFSv4 errors.

Error flow is centralized. `nfs4_do_handle_exception()` classifies protocol errors into immediate Linux errno mapping, retry, exponential delay, stateid/open/lock/delegation recovery, session recovery, migration recovery, lease recovery, or transport release. `nfs4_handle_exception()` performs sleeping waits for synchronous callers, while `nfs4_async_handle_exception()` uses RPC task delay/sleep queues and restarts. Retry pacing uses `NFS4_POLL_RETRY_MIN` through `NFS4_POLL_RETRY_MAX`, with soft-error mount handling through `nfs4_exception_should_retrans()`.

NFSv4.1 session flow begins with `nfs4_setup_sequence()`, which allocates a slot from the client or session slot table unless the table is draining. `nfs41_sequence_process()` interprets SEQUENCE status, renews leases on success, updates slot sequence numbers and target slot ids, schedules session recovery on bad sessions, probes ambiguous misordered slots, and restarts tasks when safe. Slot release through `nfs41_release_slot()` increments completed sequence numbers, wakes waiters, and notifies the server if `highest_used_slotid` needs adjustment.

OPEN flow starts with state owner acquisition and lease recovery in `_nfs4_do_open()`. `nfs4_opendata_alloc()` constructs the OPEN request, maps access/share claims, chooses the parent or existing file handle by claim type, includes create attributes and security labels when needed, and asks for ACCESS information for caching. `nfs4_open_prepare()` may suppress the RPC when cached open state or a delegation is sufficient; otherwise it updates clientid, chooses OPEN vs OPEN_NOATTR, sets exclusive-create mode, and attaches a sequence. Completion validates file type, renews the lease, confirms seqids, and may run `_nfs4_proc_open_confirm()`. `_nfs4_open_and_get_state()` converts the result into a `struct nfs4_state`, attaches the open context, processes pNFS layout-open results, updates dentry aliases, and enforces execute/read access distinctions.

Open-stateid flow is explicitly serialized. `update_open_stateid()` uses state owner locking and the state seqlock to install open and delegation stateids. `nfs_set_open_stateid_locked()` waits for sequential stateid updates on session-capable mounts so local state transitions follow server ordering. Stale or superseded stateids may be tested/freed, and delegation state can replace the active `state->stateid` until the delegation is cleared.

CLOSE flow uses asynchronous `nfs4_closedata`. `nfs4_close_prepare()` computes whether to send CLOSE or OPEN_DOWNGRADE from the remaining read/write open counts, synchronizes the argument stateid with the latest open state, optionally waits for pNFS return-on-close layoutreturn, and requests close-to-open consistency attributes when no suitable read delegation is held. `nfs4_close_done()` handles layoutreturn completion, OLD_STATEID races with concurrent OPEN, revoked stateids, server ACCESS errors caused by requested attributes, recovery retries, local open-state flag updates, seqid release, and inode refresh.

Namespace operations follow the same wrapper pattern but also update directory change attributes and link counts. CREATE-like operations use `nfs4_createdata`; remove, rename, link, mkdir, symlink, mknod, and readdir update directory cache invalidation, nlink, atime, security labels, and referral attributes as appropriate. `nfs4_setup_readdir()` synthesizes `.` and `..` entries because NFSv4 servers do not return them.

I/O flow is split into setup, prepare, and completion hooks used by the generic NFS page I/O layer. Reads choose READ_PLUS when configured and supported, fall back to READ on `-ENOTSUPP`, refresh or restart when stateids changed, and invalidate atime. Writes select a read/write stateid, request post-write consistency attributes only when needed, renew the lease, update writeback inode state, and protect writes with machine credentials if SP4_MACH_CRED negotiated that mode. Commits similarly use sequence setup and optional machine credential protection.

ACL, security-label, and xattr flow is layered over GETACL/SETACL, GETATTR/SETATTR, and optional NFSv4.2 xattr procedures. ACL gets consult local cached ACL data/length before issuing RPCs; ACL sets invalidate attribute, access, and ACL caches. Security-label code is compiled under `CONFIG_NFS_V4_SECURITY_LABEL` and uses security LSM helpers to initialize and release labels during create/open and to get/set labels through NFSv4 attributes.

Client/session setup flow is split by minor version. NFSv4.0 uses `SETCLIENTID` and `SETCLIENTID_CONFIRM`, building client owner strings from nodename, peer address, optional namespace/client-id uniquifier, and callback netid/uaddr. NFSv4.1+ uses `EXCHANGE_ID`, checks exchange flags, negotiates SP4_MACH_CRED state protection when using krb5i/krb5p, detects server-scope mismatch, stores server owner/scope/implementation data, creates sessions with validated fore/back channel attributes, initializes slot tables, probes trunked transports, and binds connections to the session.

The chunk ends during NFSv4.1 lease/state maintenance. It includes asynchronous SEQUENCE lease renewal and the setup, done, and start of free callbacks for `RECLAIM_COMPLETE`, but the final reclaim-complete operation wrapper is outside the requested line range.

## State and Persistence Behavior

Persistent client state is spread across `struct nfs_client`, `struct nfs_server`, `struct nfs_inode`, `struct nfs4_state_owner`, `struct nfs4_state`, `struct nfs4_lock_state`, delegations, and SUNRPC session/slot tables.

`struct nfs_client` state updated here includes `cl_last_renewal`, `cl_clientid`, `cl_seqid`, `cl_exchange_flags`, `cl_confirm`, `cl_sp4_flags`, session establishment state, server owner/scope/implementation identifiers, lease recovery bits, migration bits, and slot/session structures. Lease renewal happens after successful SEQUENCE, OPEN, CLOSE, READ/WRITE/COMMIT, SETCLIENTID, EXCHANGE_ID, DELEGRETURN, and lock operations.

`struct nfs_server` state includes capability flags, attribute bitmasks, cache-consistency bitmasks, exclusive-create bitmasks, ACL capability masks, file-handle expiry type, fattr validity masks, pNFS block size/layout driver state, filesystem id, and migration status. Capability bits can be downgraded at runtime when servers reject features, such as atomic open v1, POSIX locks, directory delegations, READ_PLUS, raw uid/gid handling, ACLs, labels, or xattrs.

`struct nfs_inode` state is updated through cache invalidation flags, change attributes/iversion, attr generation counters, attrtimeo state, read-cache timestamps, ACL cache pointers, open context attachment, delegation flags, and referral mountpoint fixups. Directory mutation helpers consistently invalidate data/change/ctime/nlink as needed and force lookup revalidation when change attributes move.

Open and lock stateids are persistent protocol state. Open modes are counted separately for read-only, write-only, and read-write opens. The state flags (`NFS_OPEN_STATE`, `NFS_O_RDONLY_STATE`, `NFS_O_WRONLY_STATE`, `NFS_O_RDWR_STATE`, `NFS_DELEGATED_STATE`, reclaim flags, lock flags) determine whether operations use open, lock, delegation, zero, or special stateids. Stateid seqids are advanced only when server ordering permits; wait queues coordinate races between concurrent OPEN/CLOSE/LOCK operations.

Delegations persist cached read/write authority and may provide stateids for open, setattr, reads, writes, leases, and local lock caching. The code returns incompatible delegations before conflicting opens/metadata updates, supports timestamp delegations on return, marks delegations returned, and falls back to recovery when delegation stateids are revoked or expired.

RPC task containers hold transient state but often own references that must be released in callback release functions. Correct release of seqids, open states, state owners, credentials, labels, inodes, pages, fattrs, pNFS layoutreturn state, and RPC tasks is central to the file's behavior.

## Dependencies and Integration Points

This code depends heavily on:

- SUNRPC task, credential, transport, slot, waitqueue, and XDR buffer infrastructure (`struct rpc_task`, `rpc_run_task`, `rpc_call_sync`, `rpc_restart_call_prepare`, `rpc_delay`, `rpc_sleep_on`, `rpc_clnt_*`, `rpcauth_*`).
- NFSv4 XDR procedure tables and argument/result structures from the NFS client implementation (`nfs4_procedures`, `nfs4_fs.h`, `nfs4session.h`, `nfs40.h`, `nfs42.h`).
- Generic NFS inode, page I/O, writeback, open-context, delegation, state manager, migration, FS cache, and pNFS helpers.
- Linux VFS dentry/inode/file-lock/xattr/security-label APIs.
- Kernel synchronization primitives including spinlocks, seqlocks, RCU, wait queues, mutexes, semaphores, refcounts, and task freezer-aware sleeps.
- Optional configuration gates: `CONFIG_NFS_V4_SECURITY_LABEL`, `CONFIG_NFS_V4_1_MIGRATION`, `CONFIG_NFS_V4_2`, and `CONFIG_NFS_V4_2_READ_PLUS`.

Integration is broad: this file provides procedure callbacks consumed by the NFS superblock/client ops, generic read/write/commit paths, lock manager hooks, xattr handlers, mount/root discovery, migration recovery, state manager renewal/reclaim, pNFS layout code, delegation recall paths, and session trunking machinery.

## Risks

- Error handling is high risk. Misclassifying an NFSv4 error can produce infinite retries, premature user-visible EIO, missed lease/session recovery, unrecovered stateids, or unsafe migration behavior.
- Session slot sequencing is concurrency-sensitive. Incorrect slot release, sequence-number updates, or restart handling can corrupt exactly-once semantics, trigger server `SEQ_MISORDERED`, leak slots, or deadlock the state manager.
- Open-stateid serialization is subtle. The code relies on server stateid seqid ordering, seqlocks, state-owner locks, and wait queues. Reordering or skipping waits can make CLOSE/LOCK/WRITE use stale stateids.
- Delegation paths can race recall, local open/lock caching, pNFS layoutreturn, and inode teardown. Missing a delegation return or failing to clear delegated state may violate server share/lock semantics.
- Cache invalidation must match protocol change info. Under-invalidating attributes, ACLs, access cache, xattrs, directory data, or nlink can expose stale VFS state; over-invalidating hurts performance and delegation benefits.
- Runtime capability downgrades mutate shared `server->caps` and bitmasks. A wrong downgrade can permanently disable useful features for the mount, while a missed downgrade can repeatedly issue unsupported RPCs.
- Credential selection is security-sensitive. SP4_MACH_CRED, SECINFO integrity fallback, SETCLIENTID/EXCHANGE_ID credentials, delegation credentials, and user credentials must match protocol requirements.
- Memory ownership is complex in async callbacks. Many error paths depend on release callbacks to free seqids, fattrs, labels, credentials, pages, task data, open/lock state references, and pNFS return-on-close resources.
- The chunk boundary cuts through `nfs4_free_reclaim_complete_data()`, so any final per-file report must merge the next chunk to describe `RECLAIM_COMPLETE`, pNFS layout, TEST_STATEID/FREE_STATEID, and final operation table wiring accurately.

## Test and Validation Signals

Useful validation should combine protocol, recovery, and local VFS behavior:

- Build coverage for NFSv4.0, v4.1, v4.2, pNFS, security labels, and READ_PLUS configuration combinations.
- xfstests and NFS connectathon-style tests for open/create/exclusive create, unlink/rename/link/mkdir/symlink/mknod/readdir, getattr/setattr/truncate, close-to-open consistency, ACLs, xattrs, labels, and statfs/fsinfo/pathconf.
- NFSv4.1 session tests that exercise slot exhaustion, slot table draining, retry/replay errors, bad session recovery, trunked transports, BIND_CONN_TO_SESSION, EXCHANGE_ID, CREATE_SESSION, DESTROY_SESSION, and periodic SEQUENCE renewal.
- State recovery tests for server reboot, lease expiry, network partition, migration/referral, stale clientid, stale/old/bad stateid, revoked delegations, expired locks, and reclaim-complete handling.
- Delegation tests for cached open, incompatible delegation return, timestamp delegation return, local lease creation/removal, lock caching under delegation, and recall races with open/lock/close.
- I/O tests with reads, READ_PLUS fallback, writes, commits, direct I/O, pNFS data-server paths, lost lock stateids, and open-context bad-state handling.
- Security tests for SECINFO/WRONGSEC negotiation, krb5i/krb5p integrity-protected SECINFO, SP4_MACH_CRED negotiation, machine-credential cleanup/write/commit paths, raw uid/gid fallback, and LSM security labels.
- Fault injection or server-side scripted failures returning `NFS4ERR_DELAY`, `GRACE`, `OLD_STATEID`, `BAD_STATEID`, `STALE_CLIENTID`, `BADSESSION`, `MOVED`, `LEASE_MOVED`, `WRONGSEC`, `ACCESS`, `DENIED`, and unsupported-operation errors to confirm retry and recovery behavior.
- Runtime signals include `trace_nfs4_*` events, ratelimited warnings about bad sequence ids or server quirks, absence of leaked session slots/seqids, stable inode cache invalidation behavior, and no hung tasks on recovery wait queues.
