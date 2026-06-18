# Group Research: group_1031_linux_stable_sources_os_linux_linux_stable_fs_nfsd_nfs4state_c_52da4d1741fe

Scope: learn_fs subset A, source tree `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4state.c -->
# File Research: sources/os/linux/linux-stable/fs/nfsd/nfs4state.c

## Purpose

Implements Linux NFSD's NFSv4 state manager. This file owns most server-side lifetime and protocol handling for NFSv4 clients, sessions, stateids, open owners, lock owners, share reservations, delegations, reclaim/grace handling, replay caches, courtesy clients, and state cleanup.

## Main Entry Points

- Service lifecycle: `nfsd4_create_laundry_wq()`, `nfsd4_destroy_laundry_wq()`, `nfsd4_init_slabs()`, `nfsd4_free_slabs()`, `nfs4_state_start()`, `nfs4_state_shutdown()`, `nfs4_state_start_net()`, `nfs4_state_shutdown_net()`.
- Client/session protocol: `nfsd4_setclientid()`, `nfsd4_setclientid_confirm()`, `nfsd4_exchange_id()`, `nfsd4_create_session()`, `nfsd4_sequence()`, `nfsd4_sequence_done()`, `nfsd4_bind_conn_to_session()`, `nfsd4_backchannel_ctl()`, `nfsd4_destroy_session()`, `nfsd4_destroy_clientid()`, `nfsd4_reclaim_complete()`, `nfsd4_renew()`.
- OPEN/CLOSE state: `nfsd4_process_open1()`, `nfsd4_process_open2()`, `nfsd4_cleanup_open_state()`, `nfsd4_open_confirm()`, `nfsd4_open_downgrade()`, `nfsd4_close()`.
- Delegations: `nfsd4_delegreturn()`, `nfsd_wait_for_delegreturn()`, `nfsd4_deleg_getattr_conflict()`, `nfsd_get_dir_deleg()`, `nfsd_update_cmtime_attr()`, `nfsd4_vet_deleg_time()`.
- Locks: `nfsd4_lock()`, `nfsd4_lockt()`, `nfsd4_locku()`, `nfsd4_release_lockowner()`.
- Stateid validation: `nfs4_preprocess_stateid_op()`, `nfsd4_lookup_stateid()`, `nfsd4_test_stateid()`, `nfsd4_free_stateid()`.
- Recovery and administrative cleanup: `nfsd4_revoke_states()`, `nfs4_client_to_reclaim()`, `nfs4_has_reclaimed_state()`, `nfs4_check_open_reclaim()`, `nfs4_release_reclaim()`, `nfsd4_force_end_grace()`.

## Core State Model

The file tracks confirmed and unconfirmed `nfs4_client` records per network namespace using clientid hash tables and name red-black trees. NFSv4.1+ sessions hang off clients and are indexed by sessionid. Per-client stateids are allocated from an IDR and typed as open, lock, delegation, layout, or copy-related state.

Open and lock state is represented by `nfs4_ol_stateid`. Open stateids attach to open owners and `nfs4_file` objects; lock stateids attach to lock owners and parent open stateids. `nfs4_file` objects are globally indexed by inode with an rhashtable and distinguish filehandles that alias the same inode. Share access and deny modes are tracked with bitmaps so OPEN upgrade, downgrade, close, and share-conflict checks can be enforced.

Delegations are stateids backed by kernel leases. They are linked per file and per client, recalled through callback work, revoked by the laundromat when not returned, and rate-limited by a memory-derived `max_delegations`. A small Bloom-filter pair temporarily blocks immediately regranting delegations on recently recalled filehandles.

## Control Flow

Client establishment follows two paths. NFSv4.0 uses `SETCLIENTID` and `SETCLIENTID_CONFIRM`, while NFSv4.1+ uses `EXCHANGE_ID` and `CREATE_SESSION`. Both paths allocate a client, copy credentials, assign verifier/clientid data, create nfsdfs client control files, and move records from unconfirmed to confirmed tables. Credential matching, verifier matching, machine credential enforcement, and client replacement follow RFC case logic.

Session processing centers on `SEQUENCE`. The server validates the session, request size, slot id, slot sequence number, replay cache state, and bound connection. It then marks a slot in use, restricts response size, and optionally caches the encoded reply after the compound completes. Session slots grow opportunistically when clients use the highest slot and shrink via a registered shrinker.

OPEN is split into preparation and completion. `nfsd4_process_open1()` validates the client and owner sequence state, finds or allocates an open owner, and preallocates state structures. `nfsd4_process_open2()` hashes or reuses the `nfs4_file`, validates delegate claims, creates or upgrades an open stateid, acquires an `nfsd_file`, applies truncate if requested, returns a new stateid, and attempts delegation grant as a non-fatal optimization.

Delegation grant is deliberately conservative. It checks callback viability, grace-period state, protocol minor version, existing conflicts, filehandle stability after lookup, setuid/setgid write hazards, non-NFS writers, NFSv4 writer conflicts, and races before hashing the delegation. Recall uses kernel lease callbacks and NFSD callback work. Write delegations can use CB_GETATTR to collect delegated size/change/timestamp data before GETATTR replies.

Lock operations bridge NFSv4 lock owners and stateids to Linux POSIX file locks. `LOCK` can create a lock owner/stateid from an open stateid or reuse an existing lock stateid; blocking locks are represented by `nfsd4_blocked_lock` objects and can trigger `CB_NOTIFY_LOCK`. `LOCKT` performs a temporary open for testing, and `LOCKU` unlocks via `vfs_lock_file()`.

The laundromat is the periodic state reaper. It ends the grace period, expires copy-notify state, reaps async copies, converts inactive clients to courtesy clients, expires clients when needed, removes old NFSv4.0 admin-revoked state, revokes recalled delegations, drops old close replay state, expires stale blocked-lock notifications, services server-to-server copy unmounts when enabled, and recalls delegations under memory pressure.

## Notable Helpers And Interfaces

- Special stateids: zero, one, current, and close stateids are recognized and translated according to operation context.
- Replay handling: NFSv4.0 stateowners have a replay cache protected by `rp_locked`; NFSv4.1+ uses session slots.
- nfsdfs observability: per-client `info`, `states`, and `ctl` files expose client status, callback state, session slots, open/lock/deleg/layout state, and an administrative `expire` command.
- Server-to-server copy: copy and copy-notify stateids are allocated from a per-net IDR and integrated into stateid preprocessing.
- Current stateid: NFSv4.1 current-stateid helpers set or consume stateids across compound operations.

## Dependencies

This file depends on Linux VFS file, inode, dentry, lease, lock, shrinker, IDR, xarray, rhashtable, seq_file, workqueue, and net namespace APIs. It is tightly coupled to NFSD internal modules for XDR structures, file cache acquisition, callback machinery, pNFS layouts, server-to-server copy, client tracking, tracepoints, nfsdfs, and exported filesystem permission helpers.

Key local headers include `xdr4.h`, `xdr4cb.h`, `vfs.h`, `current_stateid.h`, `netns.h`, `pnfs.h`, `filecache.h`, and `trace.h`.

## Risks And Invariants

Correctness relies on strict lock ordering among `client_lock`, per-client `cl_lock`, per-file `fi_lock`, `deleg_lock`, blocked-lock locks, and stateid mutexes. Many cleanup paths intentionally collect objects on reap lists so sleeping destructors run outside spinlocks.

Reference ownership is subtle: clients, stateowners, stateids, sessions, `nfs4_file`, `nfsd_file`, delegation leases, callback objects, and blocked-lock objects all have independent lifetimes. Bugs here can become stale stateids, leaked opens, unmount blockers, or use-after-free races.

Protocol behavior depends on exact NFSv4 replay, seqid, generation, grace-period, reclaim, and revoked-state rules. NFSv4.0 and NFSv4.1+ often intentionally diverge, especially for replay caching, CLOSE handling, admin-revoked state, current stateid, and sessions.

Delegation logic is race-sensitive because leases interact with ordinary VFS opens, non-NFSD leases, GETATTR, timestamp delegation, rename/unlink, setuid/setgid mode changes, and callback failure. The file compensates with repeated validation and fallback-to-no-delegation behavior.

Memory pressure paths can expire courtesy clients and recall delegations. Those paths are best-effort and asynchronous, so callers must tolerate `NFS4ERR_DELAY`, revoked state, and callback-state transitions.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nfsd/nfs4state.c -->