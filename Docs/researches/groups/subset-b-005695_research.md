# subset-b-005695 Research

Grouped source research for NFSv4 client state, session, superblock, sysctl, renewal, and trace support.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4renewd.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4renewd.c

## Purpose
`nfs4renewd.c` implements the NFSv4 client lease renewal worker. The worker is a delayed work item stored on `struct nfs_client` (`cl_renewd`) and runs in the system workqueue rather than as a persistent thread. Its job is to keep server-side NFSv4 state alive by scheduling protocol-specific renewal operations before the lease expires, and by expiring delegations when renewal credentials are unavailable or stale.

## Important APIs and Functions
- `nfs4_renew_state(struct work_struct *work)`: delayed-work callback that decides whether a lease renewal or delegation callback renewal is needed.
- `nfs4_schedule_state_renewal(struct nfs_client *clp)`: computes the next renewal deadline and requeues `cl_renewd` on `system_percpu_wq`.
- `nfs4_kill_renewd(struct nfs_client *clp)`: synchronously cancels the delayed worker during teardown.
- `nfs4_set_lease_period(struct nfs_client *clp, u32 period)`: stores the server lease period, caps it at one hour, and updates the RPC reconnect timeout to half the lease.

## Control Flow
`nfs4_renew_state()` obtains the minor-version maintenance operations from `clp->cl_mvops->state_renewal_ops`. It exits immediately if `NFS_CS_STOP_RENEW` is set. It compares `jiffies` against `cl_last_renewal + cl_lease_time / 3` and sets `NFS4_RENEW_TIMEOUT` when the client is sufficiently far into the lease. If delegations are present, it also sets `NFS4_RENEW_DELEGATION_CB`.

When a renewal is needed, it asks the ops table for a renewal credential. A missing credential is fatal for ordinary lease renewal and sets `NFS4CLNT_LEASE_EXPIRED`; for delegation-only renewal it expires all delegations instead. With a credential, it calls `sched_state_renewal()` asynchronously and tolerates `-EAGAIN` and `-ENOMEM` as retryable queueing failures. Successful or retryable paths reschedule the delayed work and expire unreferenced delegations.

## State and Persistence
The file mutates transient in-memory `nfs_client` state: `cl_lease_time`, `cl_last_renewal`, `cl_res_state`, and `cl_state` bits. There is no disk persistence. Correctness depends on `cl_lock` protecting lease period updates and delayed-work scheduling state. Lease timing is expressed in `jiffies`.

## Dependencies and Integration Points
This file integrates with minor-version state maintenance ops, SUNRPC delayed work and reconnect timeout APIs, and delegation helpers from `delegation.h`. It is called after clientid/session setup by `nfs4state.c`, and its expiration decisions feed the state manager via `NFS4CLNT_LEASE_EXPIRED`.

## Risks
Renewal timing is sensitive to stale `cl_last_renewal`, missing machine/user credentials, and work cancellation races at teardown. If a non-delegation renewal cannot obtain credentials, the client deliberately marks the lease expired, which pushes recovery to the state manager. If `sched_state_renewal()` returns an unexpected error, this worker does not reschedule immediately and relies on expiration handling.

## Test Signals
Useful signals are lease-renew tracepoints (`nfs4_renew`, `nfs4_renew_async`), `NFSDBG_STATE` debug output, observed delayed-work requeue intervals, delegation expiration behavior, and recovery triggered by `NFS4CLNT_LEASE_EXPIRED`. Tests should cover no-delegation/no-credential, delegation-only/no-credential, transient async allocation failures, lease cap behavior, and cancellation during client teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4renewd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4session.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4session.c

## Purpose
`nfs4session.c` implements NFSv4.1 session allocation, slot table management, slot sequencing, dynamic slot limit adjustment, and session initialization/destruction. It provides the runtime machinery used by SEQUENCE operations to serialize requests through session slots and by callback handling to wait for in-flight sequence IDs.

## Important APIs and Functions
- Slot lifecycle: `nfs4_setup_slot_table()`, `nfs4_shutdown_slot_table()`, `nfs4_alloc_slot()`, `nfs4_lookup_slot()`, `nfs4_free_slot()`, `nfs4_try_to_lock_slot()`.
- Draining/wakeups: `nfs4_slot_tbl_drain_complete()`, `nfs41_wake_and_assign_slot()`, `nfs41_wake_slot_table()`, `nfs4_slot_wait_on_seqid()`.
- Dynamic sizing: `nfs41_set_target_slotid()`, `nfs41_update_target_slotid()`.
- Session lifecycle: `nfs4_alloc_session()`, `nfs4_setup_session_slot_tables()`, `nfs4_destroy_session()`, `nfs4_init_session()`, `nfs4_init_ds_session()`.

## Control Flow
Slot tables are linked lists of `struct nfs4_slot` plus a bitmap of used slot IDs. `nfs4_realloc_slot_table()` grows the list as needed, resets sequence numbers, and constrains `max_slotid` to the negotiated table size. Request dispatch code allocates a free slot under `slot_tbl_lock`; waiters sleep on an RPC priority wait queue and are woken by `nfs41_wake_slot_table()` when slots become available.

`nfs41_assign_slot()` attaches a reserved slot to the RPC task's `nfs4_sequence_args` and `nfs4_sequence_res`. During drain, non-privileged tasks are not assigned slots. `nfs4_free_slot()` clears the used bitmap and recomputes `highest_used_slotid`; when the last slot drains it completes the table's drain completion so session reset and recovery can proceed.

The slot-target update path consumes server SEQUENCE results. `nfs41_update_target_slotid()` clamps server values to `NFS4_MAX_SLOTID`, filters sharp target changes as outliers using first and second derivative checks, updates server and target slot bounds, and wakes waiters if capacity increases.

Session setup initializes forechannel slots and, for `SESSION4_BACK_CHAN`, backchannel slots. Destruction sends `DESTROY_SESSION`, tears down the transport backchannel, destroys both wait queues, frees slots, and releases the session. Data-server session initialization mirrors the metadata server lease time and verifies the client is actually a DS client.

## State and Persistence
All state is in memory under `struct nfs4_session` and `struct nfs4_slot_table`: session ID, flags, channel attributes, slot sequence counters, capacity fields, generation counters, drain state, wait queues, and completions. There is no durable persistence; the server-visible state is reconstructed by EXCHANGE_ID/CREATE_SESSION after reset.

## Dependencies and Integration Points
This code depends on SUNRPC task scheduling and wait queues, transport backchannel support, NFSv4 protocol types, callback handling, and client state recovery in `nfs4state.c`. State recovery drains these tables before lease reclaim, session destroy/create, migration, and bind-connection operations. Tracepoints in `nfs4trace.h` observe setup and completion of SEQUENCE operations.

## Risks
The main risks are slot leaks, incorrect highest-used-slot tracking, assigning slots while draining, dynamic-slot outlier filtering suppressing legitimate server changes, and sequence ID waits timing out on callback paths. Error handling is memory-allocation sensitive because slot lookup can allocate with `GFP_NOWAIT` or `GFP_NOFS` depending on path.

## Test Signals
Exercise concurrent slot allocation/free, max-slot shrink and grow, callback waits via `nfs4_slot_wait_on_seqid()`, drain completion during session reset, and server-provided highest/target slot changes. Tracepoints `nfs4_setup_sequence` and `nfs4_sequence_done` should show slot IDs, sequence IDs, and target slot evolution. Fault injection around allocation and session destroy/create is important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4session.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4session.h

## Purpose
`nfs4session.h` declares the NFSv4.1 session and slot-table data structures shared by the NFSv4 client. It is the contract between session management, state recovery, XDR/SEQUENCE call setup, and callback handling.

## Important APIs and Types
- Constants: `NFS4_DEF_SLOT_TABLE_SIZE`, `NFS4_DEF_CB_SLOT_TABLE_SIZE`, `NFS4_MAX_SLOT_TABLE`, `NFS4_MAX_SLOTID`, `NFS4_NO_SLOT`.
- `struct nfs4_slot`: per-slot sequence state, slot number, table pointer, generation, and flags for privilege and sequence completion.
- `struct nfs4_slot_table`: parent session, slot list, used bitmap, locking, RPC wait queue, completion wait state, slot bounds, generation, and dynamic resizing derivatives.
- `struct nfs4_session`: session ID, session flags/state, channel attributes, fore/back slot tables, and owning `nfs_client`.
- Inline helpers: `nfs4_slot_tbl_draining()`, `nfs4_test_locked_slot()`, `nfs4_get_session()`, `nfs4_has_session()`, `nfs4_has_persistent_session()`, `nfs4_copy_sessionid()`, `nfs_session_id_hash()`.

## Control Flow
The header does not implement protocol control flow, but it defines the fields consumed by `nfs4session.c` and `nfs4state.c`. Slot users take `slot_tbl_lock`, reserve a bitmap bit, attach a slot to SEQUENCE args, and later free it. Recovery code tests `NFS4_SLOT_TBL_DRAINING` and waits on `complete`. Session users test `NFS4_SESSION_INITING` and `NFS4_SESSION_ESTABLISHED` through `session_state`.

## State and Persistence
The structures are transient client memory. The most important mutable state is the slot sequence counters and session ID because they mirror server-side session state. `generation` is used to avoid applying stale target-slot updates after target changes.

## Dependencies and Integration Points
The header is compiled only when `CONFIG_NFS_V4` is enabled. It depends on kernel bitmap sizing, CRC32 hashing, NFSv4 protocol structures, and SUNRPC wait queue types through includers. The exported declarations are used by session setup, client state recovery, callback SEQUENCE handling, and pNFS data-server session setup.

## Risks
Because the header fixes maximum slot table size and bitmap layout, changing constants can affect memory use and concurrency limits globally. Callers must honor the locking annotations in the C file; the header exposes raw structures, so misuse can bypass invariants such as `highest_used_slotid` consistency or drain semantics.

## Test Signals
Compile coverage under `CONFIG_NFS_V4`, `CONFIG_NFS_V4_1`, and pNFS configurations is the first signal. Runtime tests should validate that session ID hashes in trace output remain stable, persistent-session detection follows `SESSION4_PERSIST`, and slot table size bounds prevent out-of-range slot IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4state.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4state.c

## Purpose
`nfs4state.c` implements the client-side NFSv4 state model: clientid/session establishment, lease renewal setup, open-owner and lock-owner tracking, stateid selection, sequence-id ordering, state recovery, server reboot handling, migration handling, session reset, and the asynchronous state manager kthread. It is the central coordinator for preserving and rebuilding server-side NFSv4 state.

## Important APIs, Types, and Functions
- Special stateids: `zero_stateid`, `invalid_stateid`, and `current_stateid`.
- Clientid setup: `nfs4_init_clientid()`, `nfs41_init_clientid()`, `nfs41_discover_server_trunking()`, `nfs4_discover_server_trunking()`.
- Credentials: `nfs4_get_machine_cred()`, `nfs4_get_renew_cred()`, `nfs4_get_clid_cred()`.
- Owner/state lifecycle: `nfs4_get_state_owner()`, `nfs4_put_state_owner()`, `nfs4_purge_state_owners()`, `nfs4_free_state_owners()`, `nfs4_get_open_state()`, `nfs4_put_open_state()`, `nfs4_close_state()`, `nfs4_close_sync()`.
- Lock state: `nfs4_set_lock_state()`, `nfs4_put_lock_state()`, `nfs4_select_rw_stateid()`.
- Seqids: `nfs_alloc_seqid()`, `nfs_wait_on_sequence()`, `nfs_increment_open_seqid()`, `nfs_increment_lock_seqid()`.
- Recovery scheduling: `nfs4_schedule_state_manager()`, `nfs4_schedule_lease_recovery()`, `nfs4_schedule_migration_recovery()`, `nfs4_schedule_lease_moved_recovery()`, `nfs4_schedule_stateid_recovery()`, `nfs4_schedule_session_recovery()`.
- Main recovery loop: `nfs4_state_manager()` and `nfs4_run_state_manager()`.

## Control Flow
For NFSv4.0, `nfs4_init_clientid()` performs SETCLIENTID and SETCLIENTID_CONFIRM, then calls lease renewal setup. For NFSv4.1+, `nfs41_init_clientid()` performs EXCHANGE_ID and CREATE_SESSION, may mark reboot reclaim if the server did not return confirmed state, finishes session reset, and marks the client ready.

Open state is organized by credential-based `nfs4_state_owner` objects in a server rb-tree, plus per-owner open-state lists and per-inode open-state lists. Open states track read/write mode counts, stateids, flags, locks, and RCU lifetime. Close decrements mode counts, determines whether a protocol CLOSE is necessary, and either drops local state or calls `nfs4_do_close()`.

Lock state hangs off open state and is attached to Linux `file_lock` objects through custom `file_lock_operations`. Read/write stateid selection prefers a valid lock stateid, then delegation stateid, then open stateid, and clears the seqid for NFSv4.1 stateid-capable servers.

The recovery scheduler sets bits in `clp->cl_state` and ensures a single state-manager kthread runs. The manager loops while `NFS4CLNT_RUN_MANAGER` is set. In priority order it purges state, reclaims expired leases, resets sessions, binds connections to sessions, checks leases, handles migration and lease-moved events, performs reboot reclaim, reaps expired delegations, and performs no-grace reclaim. It drains slot tables before operations that must quiesce in-flight session traffic and restores them when done.

Reclaim walks all superblocks for the client, purges cached state owners, reopens marked states using minor-version recovery ops, reclaims locks, handles pNFS layout reboot recovery, completes NFSv4.2 copy state where applicable, and marks unrecoverable open contexts bad. Error handlers translate protocol failures into state bits such as `LEASE_EXPIRED`, `SESSION_RESET`, `BIND_CONN_TO_SESSION`, `RECLAIM_REBOOT`, and `RECLAIM_NOGRACE`.

## State and Persistence
State is in memory but represents server-side persistent lease state. Important mutable fields live in `struct nfs_client` (`cl_state`, `cl_res_state`, `cl_cons_state`, `cl_clientid`, `cl_confirm`, `cl_session`, lease timing, migration generation), `struct nfs_server` (owner rb-tree, owner LRU, migration status), `struct nfs4_state_owner`, `struct nfs4_state`, and `struct nfs4_lock_state`. RCU, spinlocks, seqlocks, refcounts, atomic counters, and wait queues protect different ownership layers. There is no local durable persistence; recovery reconstructs state from open files, locks, delegations, layouts, and protocol negotiation.

## Dependencies and Integration Points
This file coordinates with the NFS protocol operation tables (`cl_mvops`), XDR/proc implementations (`nfs4_proc_*`), SUNRPC clients and credentials, delegation code, pNFS layout code, idmapping, net namespace callback configuration, local I/O probing, and tracepoints in `nfs4trace.h`. It also consumes session-slot APIs from `nfs4session.c` and renewal APIs from `nfs4renewd.c`.

## Risks
This file has high concurrency risk: state manager reentry is controlled by bits, open and lock state use layered locks, and recovery can race with open, close, lock, delegation return, migration, and session reset. Lease recovery must distinguish recoverable protocol errors from fatal mount/client initialization failures. Lost locks are deliberately marked and reported, which can surface as application I/O errors. Session drain failures or missed wakeups can deadlock recovery. Migration requires persistent file handles and can permanently mark a server migration failed.

## Test Signals
Tracepoints `nfs4_state_mgr`, `nfs4_state_mgr_failed`, stateid/open/lock/delegation events, and SEQUENCE events are primary observability. Test scenarios should include server reboot, expired lease, bad/stale stateid, lock reclaim conflicts, lost lock reporting, session reset errors (`BADSESSION`, `BAD_HIGH_SLOT`, `CONN_NOT_BOUND_TO_SESSION`), callback path faults, migration with and without `fs_locations`, pNFS layout recovery, and NFSv4.2 copy state interruption. Lockdep, KCSAN, refcount debugging, and fault injection around allocation and RPC errors are especially relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4super.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4super.c

## Purpose
`nfs4super.c` wires NFSv4 into the Linux VFS/NFS subversion framework. It defines NFSv4 superblock operations, module initialization and teardown, NFSv4 mount/referral traversal through the server pseudo-root, referral loop protection, and inode eviction cleanup for NFSv4-specific state.

## Important APIs and Functions
- `nfs_v4`: `struct nfs_subversion` registration binding NFSv4 RPC version, client ops, super ops, filesystem type, and xattr handlers.
- `nfs4_write_inode()`: delegates normal NFS inode writeback, then commits pNFS layouts on synchronous writeback.
- `nfs4_evict_inode()`: final inode cleanup for delegations, pNFS layouts, generic NFS inode state, and NFSv4 xattr cache.
- `nfs4_try_get_tree()`: creates an NFSv4 server and mounts the requested export via the pseudo-root.
- `nfs4_get_referral_tree()`: creates a referral server and mounts the referred export.
- `init_nfs_v4()` / `exit_nfs_v4()`: module lifecycle for DNS resolver, idmapper, xattr cache, sysctl, server-side-copy ops, pNFS DS unload, and subversion registration.

## Control Flow
Mounting duplicates the caller's `fs_context`, installs the created `nfs_server` into the duplicate root context, copies fscache uniqueness when present, synthesizes a root source string (`host:/` or `[ipv6]:/`), mounts the server root with `fc_mount()`, then uses `mount_subtree()` to walk to the requested export path. Referral protection tracks nesting per current task in a global list and rejects traversal beyond `NFS_MAX_NESTED_REFERRALS`.

Inode eviction first truncates and clears inode pages, then returns delegations, returns and destroys pNFS layout state, runs generic NFS inode cleanup, and zaps the NFSv4 xattr cache. Module initialization is staged with unwind labels so partial failures destroy only initialized subsystems.

## State and Persistence
The file owns registration state for the NFSv4 subversion and sysctl/idmap/DNS/pNFS-xattr subsystems. Referral loop state is a transient global list protected by `nfs_referral_count_list_lock` and keyed by `current`. Superblock and inode state persist only as VFS/NFS in-memory objects.

## Dependencies and Integration Points
This code integrates VFS mount APIs, NFS fs_context parsing, NFSv4 server creation, DNS resolution, idmapping, NFSv4 sysctls, pNFS, NFSv4.2 xattrs and server-side copy, and the generic NFS superblock helpers. It exports the NFSv4 subversion to the generic NFS mount path via `register_nfs_version()`.

## Risks
Mount error paths must drop duplicated contexts, root mounts, and server references correctly. Referral loop accounting is per-task and must always be unwound after `mount_subtree()`. Eviction ordering is important: delegations and layouts must be returned before generic inode state is discarded. Initialization and exit ordering must remain symmetric, especially around optional `CONFIG_NFS_V4_2` features.

## Test Signals
Mount tests should cover IPv4 and IPv6 source formatting, normal exports, referral traversal, nested referral loop rejection, fscache options, and failure injection in server creation or root mount. Teardown tests should watch delegation return, layout return/destroy, xattr cache cleanup, and clean module unload with optional NFSv4.2 features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4sysctl.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4sysctl.c

## Purpose
`nfs4sysctl.c` registers NFSv4 tunables under `fs/nfs`. It exposes the callback TCP port and idmapper cache timeout to sysctl userspace.

## Important APIs and Functions
- `nfs4_cb_sysctls[]`: table containing `nfs_callback_tcpport` and `idmap_cache_timeout`.
- `nfs4_register_sysctl()`: calls `register_sysctl("fs/nfs", nfs4_cb_sysctls)` and stores the returned table header.
- `nfs4_unregister_sysctl()`: unregisters the table and clears the global header pointer.

## Control Flow
Module initialization in `nfs4super.c` calls `nfs4_register_sysctl()` after DNS/idmap/xattr setup. If registration fails, initialization unwinds. Module exit calls `nfs4_unregister_sysctl()`. The callback port entry uses `proc_dointvec_minmax` with bounds 0..65535, while the idmap timeout uses `proc_dointvec`.

## State and Persistence
The file stores only `nfs4_callback_sysctl_table`, a pointer to the registered sysctl header. The exposed data lives elsewhere: `nfs_callback_set_tcpport` from callback support and `nfs_idmap_cache_timeout` from idmapping. Sysctl values are runtime kernel state, not persisted by this code.

## Dependencies and Integration Points
It depends on Linux sysctl infrastructure, NFS callback state, and NFS idmapper state. Its lifecycle is tied directly to NFSv4 module registration in `nfs4super.c`.

## Risks
The main risks are registration failure during module init, invalid callback port configuration, and unregister ordering. The table is static, so adding new entries requires ensuring referenced backing variables outlive the sysctl registration.

## Test Signals
Check that `/proc/sys/fs/nfs/nfs_callback_tcpport` accepts 0..65535 and rejects out-of-range values, `idmap_cache_timeout` updates the idmapper timeout, registration failure unwinds module init, and module unload removes both entries cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.c -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.c

## Purpose
`nfs4trace.c` instantiates the NFSv4 tracepoint definitions declared in `nfs4trace.h` and exports selected pNFS/layout tracepoints to GPL modules. It is the single compilation unit that defines the tracepoint storage by setting `CREATE_TRACE_POINTS`.

## Important APIs and Functions
- `#define CREATE_TRACE_POINTS` before including `nfs4trace.h`: causes the Linux tracepoint macros to emit definitions rather than declarations.
- `EXPORT_TRACEPOINT_SYMBOL_GPL(...)`: exports selected tracepoints for pNFS read/write/commit, MDS fallback, data-server connect, flexfiles errors, block layout persistent reservation key events, and file-layout device info.

## Control Flow
There are no runtime functions in this file. Build-time macro expansion creates the tracepoint objects. At module load, those tracepoints become available through ftrace/perf/tracefs. Exported symbols allow other GPL NFS/pNFS layout modules to call the tracepoints without owning their definitions.

## State and Persistence
Tracepoint registration is kernel instrumentation state. Events are transient and emitted only when enabled by tracing infrastructure. There is no local persistent state.

## Dependencies and Integration Points
The file includes NFS core headers, `nfs4session.h`, callback support, and pNFS definitions so that all tracepoint prototypes in `nfs4trace.h` are fully typed. It bridges the header's trace definitions to external pNFS modules that need exported tracepoint symbols.

## Risks
Forgetting to keep exactly one `CREATE_TRACE_POINTS` compilation unit would cause missing or duplicate tracepoint definitions. Export lists must match tracepoints used outside this object; otherwise layout modules can fail to link or lose observability. Type changes in structs referenced by `nfs4trace.h` require this file's includes to remain sufficient.

## Test Signals
Build/link tests with pNFS layouts enabled are the main signal. Runtime checks should verify tracefs contains the NFSv4 events and that exported pNFS tracepoints can be called by flexfiles, block, and file-layout code when those modules are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.h -->
# sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.h

## Purpose
`nfs4trace.h` defines the NFSv4 tracepoint surface. It provides typed trace events for clientid/session operations, callback sequence handling, state manager transitions, XDR errors, open/close/lock state, delegation and stateid validation, namespace operations, idmapping, read/write/commit I/O, pNFS layout/device/data-server activity, flexfiles errors, block layout reservation keys, NFSv4.2 sparse/copy/offload operations, and xattrs.

## Important APIs and Event Families
- Client/session: `nfs4_setclientid`, `nfs4_exchange_id`, `nfs4_create_session`, `nfs4_destroy_session`, `nfs4_bind_conn_to_session`, `nfs4_sequence`, `nfs4_setup_sequence`, `nfs4_sequence_done`, `nfs4_trunked_exchange_id`.
- Callback: `nfs4_cb_sequence`, `nfs4_cb_seqid_err`, `nfs4_cb_offload`, `nfs_cb_no_clp`, `nfs_cb_badprinc`, callback inode/stateid events.
- State manager: `nfs4_state_mgr`, `nfs4_state_mgr_failed`, with `TRACE_DEFINE_ENUM` and `show_nfs4_clp_state()` for `NFS4CLNT_*` bits.
- Open/lock/delegation: `nfs4_open_*`, `nfs4_cached_open`, `nfs4_close`, `nfs4_get_lock`, `nfs4_set_lock`, `nfs4_unlock`, `nfs4_state_lock_reclaim`, delegation set/reclaim/detach/return/test events.
- Filesystem operations: lookup, rename, access, readlink, readdir, ACL/security-label, getattr/fsinfo/root lookup, setattr, delegreturn, layout stateid updates.
- I/O and pNFS: `nfs4_read`, `nfs4_write`, `nfs4_commit`, pNFS read/write/commit DS, layoutget/layoutcommit/layoutreturn/layoutstats, `pnfs_update_layout`, MDS fallback, deviceid, `pnfs_ds_connect`, flexfiles and file-layout events.
- NFSv4.2: llseek, fallocate/deallocate, copy, clone, copy_notify, offload cancel/status, get/set/remove/list xattr.

## Control Flow
The header uses the standard Linux tracepoint pattern: include guards allow multi-read, event classes define common payload schemas, `DEFINE_EVENT` instantiates related events, and the final `#include <trace/define_trace.h>` emits code when included from `nfs4trace.c` with `CREATE_TRACE_POINTS`. Most event classes hash file handles, stateids, session IDs, and device IDs so traces are useful without dumping opaque binary structures.

## State and Persistence
The header itself stores no runtime state. It defines how runtime state is sampled into trace buffers. Trace payloads commonly include error numbers normalized for `show_nfs4_status()`, device/file IDs, file handle hashes, stateid sequence/hash pairs, layout stateid hashes, open flags, fmode, lock ranges, client hostnames, session slot IDs, and pNFS device IDs.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure, SUNRPC trace helpers, NFS trace helpers, delegation structures, pNFS structures, NFSv4.2 structures under `CONFIG_NFS_V4_2`, and helper printers such as `show_nfs4_status()`, `show_fs_fmode_flags()`, and `show_pnfs_layout_iomode()`. It is used throughout NFSv4 proc/XDR/state/session/delegation/layout code and instantiated by `nfs4trace.c`.

## Risks
Tracepoints dereference many protocol and VFS structures in `TP_fast_assign`; callers must pass valid objects matching each event's expectations. Because some events include strings from dentries, hostnames, or data-server remote strings, lifetime assumptions matter. Trace schema changes affect userspace tooling that parses tracefs output. Conditional NFSv4.2 sections must remain guarded so non-v4.2 builds do not reference unavailable types.

## Test Signals
Build coverage across NFSv4.0, v4.1 sessions, pNFS, security labels, and NFSv4.2 configurations is essential. Runtime signals include enabling representative tracepoints through tracefs, checking payload fields for stateid/session/file-handle hashes, inducing state-manager failures, callback faults, pNFS fallback, flexfiles errors, block PR key events, sparse/copy/offload operations, and xattr operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nfs/nfs4trace.h -->
