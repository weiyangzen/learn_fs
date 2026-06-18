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
