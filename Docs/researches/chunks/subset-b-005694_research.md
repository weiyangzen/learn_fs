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
