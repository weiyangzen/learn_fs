# Group Research: group_1025_linux_stable_sources_os_linux_linux_stable_fs_nfs_nfs4state_c_sourc_b1c6e1ebf939

Scope: `Docs/research_subset_a.md` only. Files researched completely:
- `sources/os/linux/linux-stable/fs/nfs/nfs4state.c`
- `sources/os/linux/linux-stable/fs/nfs/nfs4super.c`
- `sources/os/linux/linux-stable/fs/nfs/nfs4sysctl.c`
- `sources/os/linux/linux-stable/fs/nfs/nfs4trace.c`
- `sources/os/linux/linux-stable/fs/nfs/nfs4trace.h`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4state.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4state.c

## Purpose

`nfs4state.c` implements the Linux NFSv4 client's state model and recovery engine. It owns clientid/session establishment, NFSv4 state owner caching, open state and lock state lifetime, stateid selection for I/O, NFSv4.0 seqid serialization, lease renewal, server reboot recovery, no-grace recovery, migration recovery, trunking discovery, session reset/binding, delegation/layout recall dispatch, and the asynchronous state-manager thread.

The file-level header still says "Client-side XDR", but the implementation is state management rather than XDR encoding/decoding.

## Key State Objects

- `nfs_client`: global client/server connection instance; its `cl_state` bitset is the central recovery work queue.
- `nfs_server`: mounted export/superblock state, linked from `clp->cl_superblocks`.
- `nfs4_state_owner`: per-credential open owner, stored in `server->state_owners` rb-tree and cached on `state_owners_lru`.
- `nfs4_state`: per-inode/per-owner open state, linked from both `NFS_I(inode)->open_states` and `owner->so_states`.
- `nfs4_lock_state`: per-lock-owner state under an open state.
- `nfs_seqid_counter` / `nfs_seqid`: serialize NFSv4.0 owner sequence IDs.
- `nfs4_state_recovery_ops` and `nfs4_state_maintenance_ops`: minor-version callbacks used for establish, reclaim, renewal, and lock/open recovery.

## Clientid, Session, and Credentials

The file defines special stateids: `zero_stateid`, `invalid_stateid`, and `current_stateid`.

For NFSv4.0, `nfs4_init_clientid()` performs `SETCLIENTID` and `SETCLIENTID_CONFIRM`, stores `cl_clientid`/`cl_confirm`, manages `NFS4CLNT_LEASE_CONFIRM`, and schedules state renewal.

For NFSv4.1+, `nfs41_init_clientid()` performs `EXCHANGE_ID` and `CREATE_SESSION`. If the server did not report an already-confirmed client, it starts reboot reclaim. `nfs41_finish_session_reset()` clears lease-confirm/session-reset/bind flags and schedules renewal.

Credential helpers prefer machine credentials:
- `nfs4_get_machine_cred()` returns `rpc_machine_cred()`.
- `nfs4_get_renew_cred()` uses machine credentials first, then scans mounted servers and state owners for an open-state credential.
- `nfs4_get_clid_cred()` uses machine credentials for clientid/session operations.
- `nfs4_root_machine_cred()` clears GSS principal data to force a root-machine fallback during trunking discovery.

## Session Draining

Recovery operations drain in-flight session traffic before mutating client/session state:
- `nfs4_drain_slot_tbl()` marks a slot table draining and waits for active slots.
- `nfs4_begin_drain_session()` drains the legacy slot table or both v4.1 forechannel/backchannel slot tables.
- `nfs4_end_drain_session()` clears draining and wakes slot waiters.

This protects lease re-establishment, session reset, migration transport replacement, and expired delegation handling from racing normal RPC traffic.

## State Owner and Open State Lifetime

State owners are keyed by credentials:
- `nfs4_get_state_owner()` finds or allocates an owner and invokes LRU garbage collection.
- `nfs4_put_state_owner()` moves refcount-zero owners to an LRU rather than freeing immediately.
- `nfs4_gc_state_owners()` expires unused owners older than a lease window.
- `nfs4_purge_state_owners()` detaches cached owners for unmount/reclaim boundaries.
- `nfs4_free_state_owners()` frees detached owners.

Open state is created by `nfs4_get_open_state()` and freed by `nfs4_put_open_state()`. Each state is linked under the inode and the owner. `nfs4_state_set_mode_locked()` updates read/write mode and reorders owner state lists so write-capable state is reclaimed before read-only state. That ordering reduces avoidable delegation churn during recovery.

`__nfs4_close()` updates read/write/RDWR open counters, computes the remaining mode, clears delegation state when fully closed, and either drops local state or sends `CLOSE` through `nfs4_do_close()`.

## Lock State and Stateid Selection

Lock state is tracked under `state->lock_states`. `nfs4_set_lock_state()` attaches NFSv4 lock-private data to Linux `file_lock` objects and uses `nfs4_fl_lock_ops` copy/release hooks to keep lock state refcounts correct.

`__nfs4_find_lock_state()` can match POSIX and flock/OFD owners and deliberately prefers the POSIX owner when both match.

`nfs4_select_rw_stateid()` chooses the stateid for read/write:
1. reject invalid open state with `-EIO`;
2. try an initialized matching lock stateid;
3. if a lost lock is detected, return `-EIO`;
4. prefer a valid delegation stateid;
5. use the lock stateid if available;
6. otherwise fall back to the open stateid.

For NFSv4.1 stateid semantics, selected stateids get sequence id zeroed.

## Seqid Serialization

NFSv4.0 open/close/lock operations require ordered owner sequence IDs:
- `nfs_alloc_seqid()` allocates a queued seqid object.
- `nfs_wait_on_sequence()` sleeps tasks that are not first in the owner sequence queue.
- `nfs_release_seqid()` wakes the next queued task.
- `nfs_increment_seqid()` increments for success and seqid-mutating errors only.
- `nfs_increment_open_seqid()` resets owner create time after `BAD_SEQID` and skips increment logic for session-based clients.
- `nfs_increment_lock_seqid()` applies lock seqid rules.

## Recovery Scheduling

External scheduling entry points set client/server bits and start the state manager:
- `nfs4_schedule_state_manager()`
- `nfs4_schedule_lease_recovery()`
- `nfs4_schedule_migration_recovery()`
- `nfs4_schedule_lease_moved_recovery()`
- `nfs4_schedule_stateid_recovery()`
- `nfs4_schedule_session_recovery()`

`nfs4_wait_clnt_recover()` waits for the manager to finish. `nfs4_client_recover_expired_lease()` loops recovery until lease-check/expired bits clear or retry budget is exhausted.

The manager is a kthread named from the server address. It pins the module and client while running. For swap-backed clients, it can remain available and sleep waiting for future state-manager work.

## Reclaim Marking and Execution

Reclaim markers exist at client, owner, open-state, lock-state, delegation, and layout levels:
- `nfs4_state_mark_reclaim_reboot()` marks valid open state for grace-period reboot reclaim.
- `nfs4_state_mark_reclaim_nograce()` marks state for no-grace recovery.
- `nfs4_state_start_reclaim_reboot()` marks delegations and all open states after server reboot.
- `nfs4_state_start_reclaim_nograce()` marks expired delegations and all open states for no-grace recovery.
- `nfs_inode_find_state_and_recover()` finds open/lock/delegation state matching a bad stateid and schedules no-grace recovery.
- `nfs4_state_mark_open_context_bad()` and `nfs4_state_mark_recovery_failed()` flag user contexts after unrecoverable failures.

`nfs4_reclaim_open_state()` walks an owner's open states with the requested reclaim bit. It skips invalid/closed state, rejects server-side copy state under `CONFIG_NFS_V4_2`, calls minor-version `recover_open`, reclaims locks via `nfs4_reclaim_locks()`, and converts many stateid/grace/session errors into no-grace reclaim or manager retry.

`nfs4_reclaim_locks()` walks POSIX then flock lock lists under inode locking, calls `ops->recover_lock()`, marks locks lost for denial/conflict/resource-style failures, and propagates severe server/session/timeout errors.

`nfs4_do_reclaim()` drains sessions, purges cached owners, walks all mounted servers and state owners, invokes open reclaim, reports lost locks, triggers local probe, and routes recoverable failures through `nfs4_recovery_handle_error()`.

After successful reboot reclaim, `nfs4_state_end_reclaim_reboot()` clears reboot reclaim, destroys pNFS layouts, optionally sends `RECLAIM_COMPLETE`, and re-marks reboot reclaim if the connection still is not bound to the session.

## Lease, Migration, and Trunking

`nfs4_check_lease()` renews the lease through minor-version state maintenance ops. Timeout re-sets `CHECK_LEASE`; other statuses are normalized by `nfs4_recovery_handle_error()`.

`nfs4_reclaim_lease()` establishes a new clientid/session after expiration, sets reboot or no-grace reclaim as needed, and clears check/expired bits. `nfs4_purge_lease()` re-establishes the lease, clears purge state, marks the lease expired, and starts no-grace reclaim.

`nfs4_try_migration()` retrieves `fs_locations`, drains the session, replaces transport via `nfs4_replace_transport()`, and marks migration failed on error. `nfs4_handle_migration()` processes servers marked `NFS_MIG_IN_TRANSITION`. `nfs4_handle_lease_moved()` probes root FSIDs and migrates the server that returns `NFS4ERR_MOVED`.

`nfs4_discover_server_trunking()` serializes with `nfs_clid_init_mutex`, obtains clientid credentials, invokes minor-version trunking detection, retries transient/stale cases, falls back to root machine credentials on access failure, can switch to `RPC_AUTH_UNIX`, and maps hard protocol/security failures to local errors.

`nfs41_discover_server_trunking()` uses `EXCHANGE_ID` and the v4.1 client list walk to detect address trunking and sets purge or lease-confirm state depending on transparent state migration possibility.

## Sequence Flags, Session Reset, and State Manager Loop

`nfs41_handle_sequence_flag_errors()` reacts to v4.1 `SEQUENCE` status flags:
- restart reclaim needed: server reboot recovery;
- all state revoked: reset all state;
- some/admin state revoked: no-grace recovery;
- lease moved: migration handling;
- recallable state revoked: destroy layouts and test delegations;
- backchannel fault: session reset;
- callback path down: bind connection to session.

`nfs4_reset_session()` drains session traffic, destroys the session, tolerates already-dead/bad sessions, retries delayed backchannel-busy cases, zeroes session id, recreates the session, and finishes with `nfs41_finish_session_reset()`.

`nfs4_bind_conn_to_session()` drains traffic, sends `BIND_CONN_TO_SESSION`, clears or re-sets the bind bit, and routes errors through recovery handling.

`nfs4_state_manager()` is the central ordered recovery loop under `memalloc_nofs_save()` to avoid deadlocks with NFS writeback during reclaim. It processes bits in this priority order: purge state, lease expired, session reset, bind connection, check lease, migration, lease moved, reboot reclaim, expired delegations, no-grace reclaim, delegation returns, and layout-return-any recalls. Failures are traced, rate-limited, and may mark client initialization failed for hard network/protocol errors.

## Integration Points

This file is tightly coupled with:
- `nfs4proc.c`/minor-version ops for protocol RPCs;
- `delegation.c` for delegation reclaim/return/expiration;
- `pnfs.c` and layout drivers for layout state recovery and recall;
- Linux VFS file locking through `struct file_lock`;
- SUNRPC tasks, credentials, wait queues, and session slot tables;
- tracepoints from `nfs4trace.h`.

## Risk Notes

The high-risk areas are concurrency and recovery ordering: state-owner refcounts, RCU list walks, slot-table draining, seqid wakeups, owner/open-state list ordering, and conversion between reboot/no-grace/session-reset recovery states. Small changes can cause lost state, stuck state-manager loops, or I/O using stale stateids. Error handling must preserve NFSv4 protocol distinctions between seqid-mutating errors, lease expiration, server reboot, revoked state, and transport/session faults.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4state.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4super.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4super.c

## Purpose

`nfs4super.c` wires NFSv4 client support into the Linux VFS/module layer. It defines NFSv4 superblock operations, module initialization/exit, mount/referral traversal, referral loop protection, inode writeback integration, and NFSv4-specific inode eviction cleanup.

## Superblock and Module Registration

`nfs4_sops` provides the NFSv4 `super_operations` table:
- inode allocation/free via common NFS helpers;
- `nfs4_write_inode()` for writeback plus pNFS layout commit;
- `nfs_drop_inode`, `nfs_statfs`, VFS show helpers, and `nfs_umount_begin`;
- `nfs4_evict_inode()` for NFSv4 cleanup.

`nfs_v4` is the `struct nfs_subversion` registered with the NFS core. It binds the module owner, `nfs4_fs_type`, NFSv4 RPC version, NFSv4 client ops, super ops, and NFSv4 xattr handlers.

`init_nfs_v4()` initializes DNS resolver support, idmapper support, optional NFSv4.2 xattr cache, sysctl registration, optional NFSv4.2 server-side-copy ops, and then registers the NFSv4 version. `exit_nfs_v4()` unregisters in reverse order and also unloads conditional pNFS v3 data-server connection handling.

## Writeback and Eviction

`nfs4_write_inode()` delegates normal writeback to `nfs_write_inode()`. If that succeeds, it performs `pnfs_layoutcommit_inode()`, using synchronous layout commit when the writeback control mode is `WB_SYNC_ALL`.

`nfs4_evict_inode()` performs NFSv4-specific teardown:
- final page-cache truncation;
- `clear_inode()`;
- return/free any held delegation;
- return pNFS layout state;
- destroy final pNFS layout metadata;
- run common NFS inode cleanup;
- zap the NFSv4 xattr cache.

This ordering ensures delegation and pNFS layout state are returned before common inode state is discarded.

## Mount and Referral Traversal

`do_nfs4_mount()` implements NFSv4's root-then-subtree mount behavior. It duplicates the caller's `fs_context`, installs the prepared `nfs_server`, clears/rebuilds the source as `hostname:/` or `[ipv6]:/`, mounts the server root with `fc_mount()`, then calls `mount_subtree()` for the requested export path. It propagates fscache uniqueness when configured.

`nfs4_try_get_tree()` creates a normal NFSv4 server via `nfs4_create_server()` and mounts the requested remote path through `do_nfs4_mount()`.

`nfs4_get_referral_tree()` creates a referral server via `nfs4_create_referral_server()` and uses the same mount path. This is used when traversal encounters NFSv4 referrals.

## Referral Loop Protection

The file maintains a task-keyed global `nfs_referral_count_list` protected by `nfs_referral_count_list_lock`. `nfs_referral_loop_protect()` increments the current task's referral nesting count and rejects traversal beyond `NFS_MAX_NESTED_REFERRALS` with `-ELOOP`. `nfs_referral_loop_unprotect()` decrements/removes the task entry.

This prevents recursive referral traversal from looping indefinitely while still allowing limited nested referrals.

## Integration Points

This file integrates:
- VFS `fs_context`, `fc_mount()`, and `mount_subtree()` APIs;
- common NFS client server creation and inode operations;
- DNS resolver and idmapper initialization;
- NFSv4 sysctl registration;
- pNFS layout commit/return/destruction;
- optional NFSv4.2 xattr and server-side-copy support.

## Risk Notes

Mount error paths must correctly release duplicated `fs_context`, root mounts, and server objects. Referral loop accounting is per current task, so every protect path must unprotect after `mount_subtree()`. Eviction ordering is important because delegation return can trigger pNFS return-on-close behavior before final layout destruction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4sysctl.c

## Purpose

`nfs4sysctl.c` exposes a small NFSv4 client sysctl interface under `fs/nfs`.

## Sysctls

The file registers two entries:
- `nfs_callback_tcpport`: read/write integer using `proc_dointvec_minmax`, backed by `nfs_callback_set_tcpport`, constrained to `0..65535`.
- `idmap_cache_timeout`: read/write integer using `proc_dointvec`, backed by `nfs_idmap_cache_timeout`.

`nfs_set_port_min` is zero by default because it is a static const int without explicit initializer. `nfs_set_port_max` is `65535`.

## Lifecycle

`nfs4_register_sysctl()` calls `register_sysctl("fs/nfs", nfs4_cb_sysctls)` and returns `-ENOMEM` if registration fails.

`nfs4_unregister_sysctl()` unregisters the saved table header and clears the global pointer.

## Integration Points

This file depends on:
- Linux sysctl infrastructure;
- NFS callback port globals from callback support;
- NFSv4 idmapper timeout state;
- `nfs4super.c`, which calls registration during module init and unregisters during module exit.

## Risk Notes

The implementation is intentionally small. The important contract is lifecycle correctness: unregister only the table registered by this file and keep the pointer cleared after exit. The callback port accepts the full TCP/UDP port range, including zero for default/auto behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4trace.c -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4trace.c

## Purpose

`nfs4trace.c` instantiates the NFSv4 tracepoint definitions declared in `nfs4trace.h` and exports selected tracepoint symbols for use by NFS/pNFS layout modules.

## Tracepoint Instantiation

The file defines `CREATE_TRACE_POINTS` before including `nfs4trace.h`. That causes the Linux tracepoint macros in the header to emit tracepoint storage/definitions in this translation unit.

The includes provide required type visibility for NFS state, sessions, callbacks, block device persistent reservations, pNFS, and common internal helpers.

## Exported Tracepoints

The file exports tracepoints with `EXPORT_TRACEPOINT_SYMBOL_GPL()` for GPL modules. Exported groups include:
- pNFS read/write/commit data-server events: `nfs4_pnfs_read`, `nfs4_pnfs_write`, `nfs4_pnfs_commit_ds`;
- pNFS metadata-server fallback events for page init, mirror count, read/write done, and pagelist fallback;
- data-server connection event `pnfs_ds_connect`;
- flexfiles layout read/write/commit error events;
- block layout extent commit and persistent-reservation key registration/unregistration events;
- flexfiles `fl_getdevinfo`.

## Integration Points

This file is the single C compilation unit that materializes the header-defined trace events. NFS core and loadable pNFS layout modules can then reference selected tracepoints without owning their definitions.

## Risk Notes

Tracepoint symbol export must remain aligned with events actually declared in `nfs4trace.h`. Removing or renaming header events without updating this file breaks module linkage. Adding new trace events only requires export here when external modules need to call them.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4trace.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4trace.h -->
# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4trace.h

## Purpose

`nfs4trace.h` declares the NFSv4 tracepoint surface for the Linux client. It covers clientid/session operations, callback processing, XDR/status errors, open/close/lock state transitions, delegation and stateid checks, namespace operations, inode and attribute operations, pNFS layouts and devices, flexfiles/block layout diagnostics, and optional NFSv4.2 operations.

The header follows the Linux trace event pattern: guarded declarations, `TRACE_SYSTEM nfs4`, reusable `DECLARE_EVENT_CLASS` blocks, concrete `DEFINE_EVENT`/`TRACE_EVENT` definitions, and an unguarded final include of `<trace/define_trace.h>`.

## Formatting Helpers and Status Display

The file defines printer helpers for:
- NFS file attribute validity flags via `show_nfs_fattr_flags()`;
- client state-manager bit flags via `show_nfs4_clp_state()`;
- open-state and lock-state flags via `show_nfs4_state_flags()` and `show_nfs4_lock_flags()`;
- delegation flags via `show_delegation_flags()`;
- stateid types via `show_stateid_type()`;
- pNFS update-layout reasons via `show_pnfs_update_layout_reason()`;
- NFSv4.2 seek modes via `show_llseek_mode()`;
- persistent-reservation status via `show_pr_status()`.

It uses common trace helpers from `trace/misc/sunrpc.h`, `trace/misc/fs.h`, and `trace/misc/nfs.h` for status, file modes, open flags, lock commands, pNFS I/O modes, and SUNRPC task formatting.

## Clientid, Session, and Callback Events

`nfs4_clientid_event` is reused for client/session maintenance operations:
- `nfs4_setclientid`
- `nfs4_setclientid_confirm`
- `nfs4_renew`
- `nfs4_renew_async`
- `nfs4_exchange_id`
- `nfs4_create_session`
- `nfs4_destroy_session`
- `nfs4_destroy_clientid`
- `nfs4_bind_conn_to_session`
- `nfs4_sequence`
- `nfs4_reclaim_complete`

These record destination address and normalized NFSv4 error/status.

Dedicated session/callback events include:
- `nfs4_trunked_exchange_id`: main and trunk addresses plus status.
- `nfs4_sequence_done`: session hash, slot id, sequence number, slot limits, status flags, and error.
- `nfs4_cb_sequence` and `nfs4_cb_seqid_err`: backchannel sequence arguments/results.
- `nfs4_cb_offload`: callback offload filehandle, stateid, count, stable-how, and error.
- callback error events `nfs_cb_no_clp` and `nfs_cb_badprinc`.

These events support diagnosing clientid establishment, trunking, session slot sequencing, backchannel faults, and callback authentication/lookup failures.

## State Manager and XDR Events

The header exports enum values for all `NFS4CLNT_*` state-manager bits and defines:
- `nfs4_state_mgr`: current client state bitset and hostname.
- `nfs4_state_mgr_failed`: client state, failed section, and error.

XDR diagnostics include:
- `nfs4_xdr_bad_operation`: actual versus expected operation with RPC task/client/xid.
- `nfs4_xdr_status`
- `nfs4_xdr_bad_filehandle`

These are used by decode/compound-processing paths to connect protocol errors to RPC identity and operation number.

## Open, Close, Lock, and Stateid Events

`nfs4_open_event` backs:
- `nfs4_open_reclaim`
- `nfs4_open_expired`
- `nfs4_open_file`

It records open context, file mode, open flags, fileid/fhandle, parent directory/name, and both general and open stateids.

Other open/close/state events:
- `nfs4_cached_open`: cached open state by fmode, fileid, fhandle, stateid.
- `nfs4_close`: close arguments/result and open stateid.
- `nfs4_open_stateid_update`, `nfs4_open_stateid_update_wait`, `nfs4_open_stateid_update_skip`, `nfs4_close_stateid_update_wait`.

Lock events include:
- `nfs4_get_lock`
- `nfs4_unlock`
- `nfs4_set_lock`
- `nfs4_state_lock_reclaim`

They record lock command/type, byte range, file identity, open stateid, and lock stateid where applicable.

Stateid test/match events include:
- `nfs4_test_delegation_stateid`
- `nfs4_test_open_stateid`
- `nfs4_test_lock_stateid`
- `nfs41_match_stateid`
- `nfs4_match_stateid`

These are core diagnostics for stateid recovery, old/bad stateid handling, and lock/open/delegation validation.

## Delegation and Callback-Inode Events

Delegation trace classes cover:
- `nfs4_set_delegation`
- `nfs4_reclaim_delegation`
- `nfs4_detach_delegation`
- `nfs_delegation_need_return`
- `nfs4_delegreturn_exit`

They report file identity, delegation mode, delegation flags, stateid, and return status.

Callback inode events include:
- `nfs4_cb_getattr`
- `nfs4_cb_recall`
- `nfs4_cb_layoutrecall_file`

These accept nullable client/inode data and record filehandle, optional inode identity, destination address, stateid, and status.

## Namespace, Inode, Attribute, and Idmap Events

Lookup-style events include:
- `nfs4_lookup`
- `nfs4_symlink`
- `nfs4_mkdir`
- `nfs4_mknod`
- `nfs4_remove`
- `nfs4_get_fs_locations`
- `nfs4_secinfo`
- `nfs4_lookupp`
- `nfs4_rename`

Inode events include:
- `nfs4_access`
- `nfs4_readlink`
- `nfs4_readdir`
- `nfs4_get_acl`
- `nfs4_set_acl`
- optional security label events under `CONFIG_NFS_V4_SECURITY_LABEL`.

Attribute events include:
- `nfs4_getattr`
- `nfs4_lookup_root`
- `nfs4_fsinfo`
- `nfs4_setattr`

Idmapper events include:
- `nfs4_map_name_to_uid`
- `nfs4_map_group_to_gid`
- `nfs4_map_uid_to_name`
- `nfs4_map_gid_to_group`

These events consistently record VFS device numbers, NFS fileids, hashed filehandles, names where relevant, and normalized NFSv4 errors.

## Read, Write, Commit, and pNFS Layout Events

I/O events include:
- `nfs4_read`
- `nfs4_pnfs_read`
- `nfs4_write`
- `nfs4_pnfs_write`
- `nfs4_commit`
- `nfs4_pnfs_commit_ds`

They record file identity, filehandle, offset, requested/result byte counts, open stateid, layout stateid, and error.

Layout protocol events include:
- `nfs4_layoutget`
- `nfs4_layoutcommit`
- `nfs4_layoutreturn`
- `nfs4_layoutreturn_on_close`
- `nfs4_layouterror`
- `nfs4_layoutstats`
- `pnfs_update_layout`

MDS fallback events share `pnfs_layout_event`:
- `pnfs_mds_fallback_pg_init_read`
- `pnfs_mds_fallback_pg_init_write`
- `pnfs_mds_fallback_pg_get_mirror_count`
- `pnfs_mds_fallback_read_done`
- `pnfs_mds_fallback_write_done`
- `pnfs_mds_fallback_read_pagelist`
- `pnfs_mds_fallback_write_pagelist`

Device and data-server events include:
- `nfs4_deviceid_free`
- `nfs4_getdeviceinfo`
- `nfs4_find_deviceid`
- `pnfs_ds_connect`
- `fl_getdevinfo`

These support pNFS layout selection, fallback diagnosis, data-server connectivity, and deviceid lifecycle tracing.

## Flexfiles and Block Layout Events

Flexfiles events include:
- `ff_layout_read_error`
- `ff_layout_write_error`
- `ff_layout_commit_error`

They record MDS file identity, DS destination address, filehandle, offset/count, stateid where relevant, local error, and NFS operation status.

Block layout events include:
- `bl_ext_tree_prepare_commit`
- `bl_pr_key_reg`
- `bl_pr_key_unreg`
- `bl_pr_key_reg_err`
- `bl_pr_key_unreg_err`

Persistent reservation key events record block device identity, key, and PR status.

## NFSv4.2 Conditional Events

Under `CONFIG_NFS_V4_2`, the header adds:
- `nfs4_llseek` for `SEEK_DATA`/`SEEK_HOLE`;
- `nfs4_fallocate` and `nfs4_deallocate`;
- `nfs4_copy`, `nfs4_clone`, `nfs4_copy_notify`;
- `nfs4_offload_cancel`, `nfs4_offload_status`;
- `nfs4_getxattr`, `nfs4_setxattr`, `nfs4_removexattr`, `nfs4_listxattr`.

These events capture filehandles, fileids, offsets, lengths, stateids, copy result stateids/counts, offload status identifiers, xattr names, and errors.

## Integration Points

This header is consumed by many NFSv4 client files through `trace_nfs4_*()` calls and is instantiated exactly once by `nfs4trace.c`. Some pNFS tracepoints are exported from `nfs4trace.c` so layout modules can emit them.

It depends on stable structure fields from NFS core, NFSv4 state, pNFS layout headers, SUNRPC request/task objects, Linux block devices, and NFSv4.2 argument/result structures.

## Risk Notes

Tracepoints are ABI-like diagnostics for kernel tracing users. Field changes can break scripts even if code still compiles. Many events dereference nested objects such as `ctx->state`, `hdr->args.context->state`, layout segments, block-device disks, and callback arguments, so caller-side object lifetime must be valid when tracing. Conditional events and exported tracepoints must stay synchronized with Kconfig and `nfs4trace.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfs/nfs4trace.h -->