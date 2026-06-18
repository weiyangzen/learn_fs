# Research: sources/distributed-fs/ceph-client/fs/nfs/nfs4proc.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005693`: lines 1-9526, `Docs/researches/chunks/subset-b-005693_research.md`
- `subset-b-005694`: lines 9527-10750, `Docs/researches/chunks/subset-b-005694_research.md`

## Chunk Research

### subset-b-005693: lines 1-9526

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

### subset-b-005694: lines 9527-10750

# sources/distributed-fs/ceph-client/fs/nfs/nfs4proc.c lines 9527-10750

## Scope

This chunk covers the tail of the NFSv4 procedure implementation. It begins at the release side of `RECLAIM_COMPLETE`, then implements NFSv4.1 pNFS control operations (`LAYOUTGET`, `LAYOUTRETURN`, `GETDEVICEINFO`, and `LAYOUTCOMMIT`), `SECINFO_NO_NAME` root security discovery, `TEST_STATEID` and asynchronous `FREE_STATEID`, NFSv4.1 stateid comparison, minor-version operation tables for v4.1 and v4.2, xattr listing and handler tables, swap state-manager hooks, server cloning, and the final `nfs_v4_clientops` VFS/RPC dispatch table.

The range is an end-of-file integration point. Many callbacks assigned in the operation tables are implemented in earlier chunks of `nfs4proc.c`, while the pNFS and stateid helpers implemented here are called from `pnfs.c`, layout drivers, delegation/state recovery code, and generic NFS client setup.

## Purpose

The code in this range binds NFSv4.1+ session/state machinery to pNFS layout lifetime management and to the generic NFS client operation interfaces. It translates high-level pNFS layout requests into sequenced NFSv4 compound RPCs, classifies server and transport errors into retry, fallback, or recovery actions, and updates local layout/stateid state so data I/O can safely switch between pNFS data servers and ordinary metadata-server I/O.

It also selects the behavior profile for NFS minor versions. The v4.1 and v4.2 `nfs4_minor_version_ops` tables define capabilities, state recovery callbacks, session slot handling, lease renewal, migration recovery, and lock-state freeing. The final `nfs_v4_clientops` table exposes the NFSv4 implementation to common NFS/VFS code.

## Important APIs, Types, and Functions

`nfs41_proc_reclaim_complete()` issues global `RECLAIM_COMPLETE` using the client's state-management RPC client (`cl_rpcclient`). It allocates `struct nfs4_reclaim_complete_data`, sets `one_fs = 0`, initializes a privileged NFSv4.1 sequence, and runs the call through `nfs4_call_sync_custom()` with `nfs4_reclaim_complete_call_ops`.

`nfs4_layoutget_prepare()`, `nfs4_layoutget_done()`, `nfs4_layoutget_release()`, `nfs4_layoutget_call_ops`, and `nfs4_proc_layoutget()` implement pNFS `LAYOUTGET`. The public entry point runs an asynchronous RPC task but waits synchronously for completion, then either processes the returned layout through `pnfs_layout_process()`, retries on an empty layout body, or maps protocol errors through `nfs4_layoutget_handle_exception()`.

`nfs4_layoutget_handle_exception()` is the key pNFS error classifier. It maps `NFS4ERR_LAYOUTUNAVAILABLE` to `-ENODATA` so upper layers can retry ordinary in-band I/O, maps `NFS4ERR_BADLAYOUT` or `LAYOUTTRYLATER` with zero minimum length to `-EOVERFLOW`, maps layout/return recall conflicts to `-ERECALLCONFLICT`, and handles revoked/expired/bad stateids by either asking ordinary state recovery to repair the open stateid or invalidating the layout stateid and freeing affected layout segments.

`max_response_pages()` computes the number of pages needed to hold the session's maximum response size from `cl_session->fc_attrs.max_resp_sz`. It is exported through `pnfs.h` for pNFS callers that size reply buffers.

`nfs4_layoutreturn_prepare()`, `nfs4_layoutreturn_done()`, `nfs4_layoutreturn_release()`, `nfs4_layoutreturn_call_ops`, and `nfs4_proc_layoutreturn()` implement `LAYOUTRETURN`. The entry point applies state protection for pNFS cleanup, optionally makes the task asynchronous, grabs and activates the inode when needed, initializes a sequenced operation, and frees or defers local layout segments in the release callback depending on the final RPC status.

`_nfs4_proc_getdeviceinfo()` and `nfs4_proc_getdeviceinfo()` implement `GETDEVICEINFO`. The inner helper asks for device-change and device-delete notifications, marks `pnfs_device::nocache` if the server cannot provide the exact notification set, and emits a tracepoint. The outer helper wraps the call in `nfs4_handle_exception()` retry logic.

`nfs4_layoutcommit_prepare()`, `nfs4_layoutcommit_done()`, `nfs4_layoutcommit_release()`, `nfs4_layoutcommit_ops`, and `nfs4_proc_layoutcommit()` implement `LAYOUTCOMMIT`. The call may be synchronous or asynchronous. It updates server-side layout commit state for writes and, during release, calls `pnfs_cleanup_layoutcommit()` and forces weak-cache-consistency attribute update via `nfs_post_op_update_inode_force_wcc()`.

`_nfs41_proc_secinfo_no_name()`, `nfs41_proc_secinfo_no_name()`, and `nfs41_find_root_sec()` implement NFSv4.1 root security flavor discovery. The code first tries `SECINFO_NO_NAME` with integrity protection and machine credentials when available, falls back to the filesystem RPC client/user credential on `WRONGSEC`, and ultimately falls back to older "guess and check" root security discovery if the operation is unsupported.

`_nfs41_test_stateid()`, `nfs4_handle_delay_or_session_error()`, and `nfs41_test_stateid()` implement `TEST_STATEID` with retry behavior for delay, replay-cache, and session-slot/session-death errors. `nfs4_state_protect()` may switch the RPC client or credential according to state-protection policy before the RPC is sent.

`struct nfs_free_stateid_data`, `nfs41_free_stateid_prepare()`, `nfs41_free_stateid_done()`, `nfs41_free_stateid_release()`, `nfs41_free_stateid_ops`, and `nfs41_free_stateid()` implement asynchronous `FREE_STATEID`. The function pins the `nfs_client`, copies the stateid into callback data, starts an async/moveable sequenced RPC, and immediately marks the caller's stateid as `NFS4_FREED_STATEID_TYPE` after successful task launch.

`nfs41_free_lock_state()` uses `FREE_STATEID` for a lock stateid, then releases local lock state through `nfs4_free_lock_state()`.

`nfs41_match_stateid()` provides the NFSv4.1 stateid comparison callback. It requires matching type and `other` bytes, treats equal sequence IDs as a match, and also treats sequence ID zero as a wildcard. `nfs4_match_stateid()` is a generic wrapper around `nfs4_stateid_match()` with tracing.

`nfs41_sequence_slot_ops`, `nfs41_reboot_recovery_ops`, `nfs41_nograce_recovery_ops`, `nfs41_state_renewal_ops`, and `nfs41_mig_recovery_ops` bind the v4.1 session, recovery, lease-renewal, and migration helper functions into `struct nfs4_minor_version_ops`.

`nfs_v4_1_minor_ops` and `nfs_v4_2_minor_ops` define capabilities and callback families for NFSv4.1 and NFSv4.2. v4.2 extends v4.1 with features such as allocate/deallocate, copy/offload, seek, layoutstats/layouterror, clone, read-plus, and offload status. `nfs_v4_minor_ops[]` publishes the compiled minor-version table.

`nfs4_listxattr()` composes xattr names from generic xattrs, LSM security xattrs, and NFSv4 user xattrs, returning `-ERANGE` when a supplied buffer is too small.

`nfs4_enable_swap()` and `nfs4_disable_swap()` keep or wake the NFSv4 state manager when an NFS inode is used for swap, so lease/state management remains available even under memory pressure.

`nfs4_clone_server()` clones an `nfs_server`, applies NFSv4.1 session limits to read/write and xattr sizes, and allocates the delegation hash before returning the clone.

`nfs_v4_clientops` is the public `struct nfs_rpc_ops` implementation for protocol version 4. It wires VFS-style operations, page I/O setup/completion, lock/open/delegation operations, server lifecycle, trunking discovery, and swap hooks to NFSv4 implementations.

The xattr handler constants (`nfs4_xattr_nfs4_acl_handler`, `nfs4_xattr_nfs4_dacl_handler`, `nfs4_xattr_nfs4_sacl_handler`, optional security-label handler, and optional v4.2 user handler) populate `nfs4_xattr_handlers[]` for VFS xattr dispatch.

## Control Flow

`RECLAIM_COMPLETE` follows the standard sequenced synchronous RPC pattern. The caller allocates callback data, initializes sequence arguments with privileged state-management behavior, points the RPC message at the argument/result structs, and lets `nfs4_call_sync_custom()` drive prepare/done/release callbacks. The done path in the preceding context wakes lock waiters on success, tolerates `COMPLETE_ALREADY` and `WRONG_CRED`, retries selected transient errors, and schedules lease recovery for unexpected failures.

`LAYOUTGET` initializes a sequence on the metadata server's client, starts an async/moveable RPC task with `RPC_TASK_CRED_NOREF`, waits for the task, and then examines both transport/task completion and NFS status. Negative `task->tk_status` is routed into `nfs4_layoutget_handle_exception()`. A successful RPC with a zero-length layout body is treated as retryable `-EAGAIN` with backoff. A non-empty layout is handed to `pnfs_layout_process()`, which validates and installs the returned layout segment.

`nfs4_layoutget_handle_exception()` frees the sequence slot before handling protocol errors because the higher-level exception path may sleep or restart. For bad layout stateids it takes `inode->i_lock` and compares the requested stateid against the layout header stateid. If the open stateid is implicated, it sets `exception->state` and `exception->stateid` so normal NFSv4 state recovery can repair it. If the layout stateid is implicated, it marks the layout stateid invalid, commits dirty inode data, frees invalidated layout segments, and returns `-EAGAIN`.

`LAYOUTRETURN` starts by checking sequence setup and whether the local layout is still valid. If the layout has already become invalid, prepare exits the RPC with success. In the done callback, RPC transport failures are converted into either success-like cleanup or `-EAGAIN` retry-later state. Protocol `OLD_STATEID` can refresh the layout stateid and restart the call. Bad/dead sessions schedule session recovery and cause local retry-later handling. `DELAY` uses the async exception helper and can restart the call after freeing the sequence slot.

The `LAYOUTRETURN` release path decides local persistence of layout segments. If the RPC completed acceptably or there is no active inode reference, it calls `pnfs_layoutreturn_free_lsegs()` and optionally applies a server-returned stateid. If retry is needed, it calls `pnfs_layoutreturn_retry_later()` so the layout return can be attempted again. It then frees sequence slot state, layout-driver private data, layout header reference, inode active reference, credential, and the request object.

`GETDEVICEINFO` is a simpler synchronous RPC wrapped in exception retry. After the call returns, the code compares returned notification bits to requested bits. Unsupported extras are only logged, while missing requested notifications mark the pNFS device as non-cacheable because the client cannot rely on later server notification to invalidate cached device information.

`LAYOUTCOMMIT` can run synchronously or asynchronously. For async operation it grabs and activates the inode, otherwise a disappearing inode causes release cleanup and `-EAGAIN`. The done callback ignores several pNFS semantic failures that mean the layout is no longer useful for commit (`DELEG_REVOKED`, `BADIOMODE`, `BADLAYOUT`, `GRACE`), but retries general transient errors through `nfs4_async_handle_error()`. Release always performs pNFS cleanup and WCC inode attribute update.

Root security discovery first allocates one page to receive `struct nfs4_secinfo_flavors`. `nfs41_proc_secinfo_no_name()` may issue two attempts per retry cycle: integrity-protected machine-credential SECINFO, then ordinary filesystem-client SECINFO when the first path is unavailable or returns `WRONGSEC`. `nfs41_find_root_sec()` iterates returned flavors, converts RPC auth flavors to pseudoflavors, filters them through mount `auth_info`, and probes root lookup with the first acceptable flavor that works. `-EACCES` is normalized to `-EPERM`.

`TEST_STATEID` performs a sequenced state-protected synchronous RPC. If the compound succeeds at the RPC layer, the NFS operation status in `res.status` is returned as a negative NFS4 error. The public wrapper retries only delay/replay-cache and session-slot/session lifecycle errors; ordinary invalid-stateid answers are returned to the caller.

`FREE_STATEID` is intentionally fire-and-forget. It increments `cl_count`, builds callback data, initializes a privileged or unprivileged sequence, starts an async task, drops the task reference, and marks the local stateid type as freed. The release callback drops the client reference. The done callback only handles `NFS4ERR_DELAY` retry; other protocol results do not block local lock-state teardown.

The final operation tables are passive control flow: common NFS, VFS, state-manager, and mount code index `nfs_v4_minor_ops[]` and dereference `nfs_v4_clientops` callbacks instead of calling most functions in this file directly.

## State and Persistence Behavior

The pNFS operations in this range mostly maintain runtime client state rather than persistent local storage. `LAYOUTGET` installs or refreshes in-memory `pnfs_layout_hdr` and `pnfs_layout_segment` state through `pnfs_layout_process()`. `LAYOUTRETURN` removes or defers local layout segments based on RPC outcome, updates local layout stateid when the server returns one, and releases layout-driver private return data. `LAYOUTCOMMIT` reports layout-backed writes to the metadata server and then cleans local layoutcommit bookkeeping.

Stateid handling is central. Layout stateids can be invalidated under `inode->i_lock`, lock stateids can be asynchronously freed on the server, and NFSv4.1 stateid comparison treats sequence ID zero as a wildcard. `nfs41_free_stateid()` mutates the caller's stateid type to `NFS4_FREED_STATEID_TYPE` as soon as the async free task has been launched, so later local code should not reuse it even though the server reply may still be pending.

Session state is maintained by `nfs4_init_sequence()`, `nfs4_setup_sequence()`, `nfs41_sequence_process()`, `nfs41_sequence_done()`, and explicit `nfs4_sequence_free_slot()` calls. Several retry paths free the slot before restarting the RPC to avoid slot leaks or sequence-table stalls.

Security-flavor discovery affects mount/server runtime state by selecting an auth flavor that can access the pseudo-root. The result is not persisted by this chunk, but it feeds server setup and root lookup behavior. `GETDEVICEINFO` can set `pnfs_device::nocache`, affecting later pNFS device cache policy.

`nfs4_clone_server()` persists only in-memory server clone configuration: it constrains transfer sizes based on session attributes and allocates delegation tracking state for the cloned server. Failure after cloning frees the server to avoid a partially initialized mount/submount server.

Swap hooks mutate client state-manager bits. Enabling swap schedules the state manager so it remains alive; disabling swap sets `NFS4CLNT_RUN_MANAGER`, clears `NFS4CLNT_MANAGER_AVAILABLE`, and wakes waiters on `cl_state`, allowing the manager to observe updated state and exit when appropriate.

The xattr and operation tables are static module state. They do not change at runtime but define how VFS and common NFS code route operations for every NFSv4 inode/server.

## Dependencies and Integration Points

This chunk depends on the Linux RPC task framework (`struct rpc_message`, `struct rpc_task_setup`, `rpc_run_task()`, `rpc_wait_for_completion_task()`, `rpc_restart_call_prepare()`, `rpc_put_task()`), NFSv4 sequence/session helpers, NFSv4 exception handling, state protection, credentials, and tracepoints.

pNFS integration is broad. `nfs4_proc_layoutget()`, `nfs4_proc_layoutreturn()`, `nfs4_proc_getdeviceinfo()`, `nfs4_proc_layoutcommit()`, and `max_response_pages()` are declared through `pnfs.h` for use by `pnfs.c` and layout drivers such as file layout, flexfiles, and block layout. The code calls back into pNFS core helpers including `pnfs_layout_process()`, `pnfs_layoutget_free()`, `pnfs_mark_layout_stateid_invalid()`, `pnfs_free_lseg_list()`, `pnfs_layoutreturn_free_lsegs()`, `pnfs_layoutreturn_retry_later()`, `pnfs_put_layout_hdr()`, and `pnfs_cleanup_layoutcommit()`.

State recovery integration flows through `struct nfs4_minor_version_ops`. The v4.1/v4.2 tables point reboot recovery at `nfs4_open_reclaim()`, `nfs4_lock_reclaim()`, `nfs41_init_clientid()`, `nfs41_proc_reclaim_complete()`, and trunking discovery. No-grace recovery points at expired-open and expired-lock recovery. Lease renewal points at async `SEQUENCE`, machine credentials, and synchronous `SEQUENCE`. Migration recovery points at location and fsid-presence helpers implemented earlier in the file.

Security discovery depends on RPC auth helpers (`rpcauth_get_pseudoflavor()`), mount auth filtering (`nfs_auth_info_match()`), root lookup probing (`nfs4_lookup_root_sec()`), legacy root-security fallback (`nfs4_find_root_sec()`), and integrity/machine-credential helpers (`_nfs4_is_integrity_protected()`, `nfs4_get_clid_cred()`).

VFS integration is via `nfs4_dir_inode_operations`, `nfs4_file_inode_operations`, `nfs_v4_clientops`, and `nfs4_xattr_handlers[]`. These tables wire the chunk to generic NFS helpers, NFSv4-specific operations implemented earlier in `nfs4proc.c`, ACL/xattr handlers, file/page I/O code in `read.c` and `write.c`, and mount/server lifecycle code in `client.c` and superblock paths.

Conditional compilation affects the exported behavior. `CONFIG_NFS_V4_2` adds the v4.2 minor ops table and user xattr handler. `CONFIG_NFS_V4_0` controls whether minor version zero appears in `nfs_v4_minor_ops[]`. `CONFIG_NFS_V4_SECURITY_LABEL` adds the security label xattr handler.

## Risks

- Sequence-slot lifetime is subtle. Several error paths free slots manually before exception handling or RPC restart. Missing or duplicate slot release can deadlock a session, corrupt sequence accounting, or trip use-after-free behavior in callbacks.
- `LAYOUTGET` error mapping controls whether callers fall back to in-band I/O, retry pNFS, or run state recovery. Regressions can cause needless pNFS disablement, retry storms, or stale layout-stateid reuse after a server revokes state.
- The bad-stateid path in `nfs4_layoutget_handle_exception()` depends on comparing the requested stateid to `lo->plh_stateid` under `inode->i_lock`. Incorrect locking or comparison semantics could invalidate the wrong layout or miss required open-state recovery.
- `LAYOUTRETURN` deliberately treats some transport failures as cleanup success. Changing those mappings can either leak layout segments locally or discard layouts that should be retried after transient network recovery.
- Async `LAYOUTRETURN` and `LAYOUTCOMMIT` rely on active inode references. Failure to grab/release active references correctly can race unmount, inode eviction, or layout cleanup.
- `nfs41_free_stateid()` increments `cl_count` before allocating callback data but returns `-ENOMEM` directly if allocation fails. In the inspected code path, that means the client reference is not dropped on allocation failure; callers and future changes should treat this path carefully.
- `FREE_STATEID` marks the local stateid as freed immediately after task launch. If later code assumes server-side completion rather than local fire-and-forget semantics, it can hide server errors or race diagnostic checks.
- `GETDEVICEINFO` cacheability depends on exact notification negotiation. Mishandling `pdev->nocache` can leave stale data-server device mappings in use after a server-side change.
- `SECINFO_NO_NAME` intentionally falls back after `WRONGSEC` despite the specification comment noting this should not happen. Removing that compatibility path can break deployed servers.
- The final operation tables are wide blast-radius wiring. A wrong callback assignment can affect all NFSv4 mounts for lookup, writeback, locking, delegation return, server cloning, or swap behavior.
- The xattr list path must account for generic, security, and NFSv4 user xattrs without overflowing the caller buffer. Incorrect length handling can return incomplete lists without `-ERANGE` or write past the buffer.
- Swap hooks are small but memory-pressure sensitive. If the state manager exits while an NFS swapfile is active, lease recovery and state maintenance can fail under precisely the conditions where forward progress is hardest.

## Test and Validation Signals

Useful validation should include targeted NFSv4.1/v4.2 and pNFS tests:

- pNFS `LAYOUTGET` success with file, flexfile, and block layout drivers, including tracepoint validation for requested/returned ranges and installed layout stateids.
- `LAYOUTGET` negative cases for `LAYOUTUNAVAILABLE`, `BADLAYOUT`, `LAYOUTTRYLATER` with zero and nonzero minimum length, `RECALLCONFLICT`, `RETURNCONFLICT`, `BAD_STATEID`, `EXPIRED`, `DELEG_REVOKED`, and `ADMIN_REVOKED`, verifying fallback, retry, and state-recovery behavior.
- Layout stateid invalidation tests that dirty data, trigger a bad layout stateid, and verify commits occur before invalidated segments are freed.
- `LAYOUTRETURN` synchronous and asynchronous tests for successful returns, old stateid refresh/restart, server `DELAY`, bad/dead session recovery, network unreachable handling with and without fatal flags, and retry-later persistence.
- `LAYOUTCOMMIT` tests for sync and async writeback, ignored semantic failures (`DELEG_REVOKED`, `BADIOMODE`, `BADLAYOUT`, `GRACE`), transient retry, WCC attribute refresh, and inode eviction races.
- `GETDEVICEINFO` tests for full notification support, missing notifications causing `nocache`, unsupported extra notifications being logged but not fatal, and exception retry on session/delay errors.
- Root security discovery tests where `SECINFO_NO_NAME` works with integrity-protected machine credentials, falls back after `WRONGSEC`, is unsupported and falls back to legacy probing, or returns flavors filtered by mount auth policy.
- `TEST_STATEID` tests for valid, invalid, expired, delayed, replay-cache retry, bad-slot, and dead-session results.
- `FREE_STATEID` tests for asynchronous lock-state free, delayed retry, client-reference release, and local stateid type transition to `NFS4_FREED_STATEID_TYPE`.
- NFSv4.1 and v4.2 mount probes verifying advertised capabilities, state recovery callbacks, session trunking, migration recovery, and no seqid allocation for minor versions using sessions.
- xattr list tests covering generic xattrs, LSM security xattrs, NFSv4 ACL/DACL/SACL names, optional v4.2 user xattrs, NULL-size queries, and too-small buffers returning `-ERANGE`.
- Swap-over-NFS tests ensuring the state manager remains scheduled while swap is active and exits only after disable/wakeup.
- Fault injection around allocation failures in reclaim-complete data, layout-return/commit inode activation, `SECINFO_NO_NAME` page allocation, free-stateid callback allocation, and server clone delegation-hash allocation.

## Cross-Chunk Notes

The chunk begins after the earlier `RECLAIM_COMPLETE` prepare/done/error handling helpers. The merge lane should combine those helpers with `nfs41_proc_reclaim_complete()` here when documenting reboot recovery.

The pNFS helpers in this range are declared in `pnfs.h`, but most layout allocation, invalidation, return-list management, and layoutcommit setup lives in `pnfs.c` and layout-driver-specific files. A complete per-file report should connect these RPC procedures to those pNFS core and driver flows.

The final `nfs_v4_clientops`, inode-operation tables, and xattr handler array reference many functions implemented before line 9527. This chunk should be treated as the callback map for the whole file, not proof that all listed callback behavior is implemented in this range.
