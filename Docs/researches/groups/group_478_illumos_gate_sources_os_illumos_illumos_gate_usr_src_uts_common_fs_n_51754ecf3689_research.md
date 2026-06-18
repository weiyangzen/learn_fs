# Group Research: group_478_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_n_51754ecf3689

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/illumos/illumos-gate`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_db.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_db.c

Purpose: Implements the generic NFSv4 server state database used by server-side state tables.

Key behavior:
- Creates/destroys NFSv4 state databases, tables, indexes, hash buckets, ID spaces, and per-table kmem caches.
- Manages database entry lifecycle: allocation, constructor/destructor callbacks, refcounts, invalidation, hide/unhide, locking, timed waits, and condition broadcasts.
- `rfs4_dbsearch` searches a hash index, optionally creates a new entry through a single createable index, assigns IDs, and links the entry into all table indexes.
- Provides table walking and search-with-callback helpers that lock entries while invoking callers.
- Starts one reaper thread per expiring table; reapers reclaim entries with only the table hash reference left and either expired by policy or during shutdown.
- Handles database shutdown by marking all table reapers for exit and waiting for each to report completion.

Dependencies:
- Uses illumos kernel synchronization, kmem caches, ID space allocator, zthreads, callb CPR support, DTrace probes, and NFSv4 server structures from `nfs4_db_impl.h`.

Notable details:
- Table reap interval dynamically tightens as ID usage crosses low/high watermarks.
- Entries are linked into multiple indexes but only receive one table/hash reference.
- Index link invalidation uses a low-bit pointer marker to catch misuse.
- Resume-from-suspend callback extends client last-access times by one lease period.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_db.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_deleg_ops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_deleg_ops.c

Purpose: Provides FEM vnode monitors for files to which the NFSv4 server has granted delegations.

Key behavior:
- `recall_all_delegations` recalls outstanding delegations, optionally returns `NFS4ERR_DELAY` for nonblocking callers, and otherwise waits up to the lease time while retrying recalls.
- Read-delegation monitors recall on conflicting write/truncate/open/write/setattr/space/security operations.
- Write-delegation monitors permit server-owned operations but recall for non-owner opens, reads, writes, locks, setattr, space, and security changes.
- Vnode event monitors recall delegations for remove and rename source/destination events and always block until the delegation is returned.
- After conflict handling, each monitor forwards the operation to the next vnode operation with `vnext_*`.

Dependencies:
- Uses FEM, vnode/caller context APIs, NFSv4 server delegation state, `rfs4_recall_deleg`, `rfs4_dbe_*` entry synchronization, and the server caller ID.

Notable details:
- `CC_DONTBLOCK` callers receive `EAGAIN` through `CC_WOULDBLOCK`; remove and rename events deliberately ignore nonblocking behavior.
- The NFSv4 server’s own VOP calls are recognized through `cc_caller_id` to avoid self-conflict.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_deleg_ops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_dispatch.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_dispatch.c

Purpose: Dispatches NFSv4 RPC requests and implements the NFSv4.0 duplicate request cache.

Key behavior:
- Initializes/finalizes the duplicate request cache with a global LRU list plus per-XID hash buckets.
- `rfs4_find_dr` keys duplicate entries by RPC XID and remote transport address, returning NEW, REPLAY, PENDING, or ERROR.
- Reuses free or replayable DRC entries once the configured maximum cache size is reached.
- `rfs40_dispatch` runs NFSv4.0 COMPOUND requests, caches replies for non-idempotent requests, replays cached replies for duplicates, and avoids caching when the thread would block.
- Sends minor-version mismatch replies when a COMPOUND requests a disabled minor version.
- `rfs4_dispatch` handles NULL procedure, minor-version routing, NFSv4.0 dispatch, and NFSv4.1+ handoff to `rfs4x_dispatch`.

Dependencies:
- Uses RPC/SVC/XDR infrastructure, NFSv4 compound execution/free helpers, NFSv4 idempotency detection, server global state, DTrace probes, and list primitives.

Notable details:
- DRC entries transition through NEW/INUSE/REPLAY/FREE states under the DRC mutex.
- Pending duplicates are dropped without reply so the client retransmits.
- Resource exhaustion replies synthesize a one-op COMPOUND result with `NFS4ERR_RESOURCE` or `NFS4ERR_OP_ILLEGAL`.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_idmap.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_idmap.c

Purpose: Maps NFSv4 owner/group UTF-8 strings to local uid/gid values and back, with per-zone caches and nfsmapid door upcalls.

Key behavior:
- Initializes module-wide idmap cache storage, per-zone `nfsidmap_globals`, daemon door handles, and four caches: uid-to-string, string-to-uid, gid-to-string, string-to-gid.
- `nfs_idmap_str_uid` and `nfs_idmap_str_gid` convert owner strings to local IDs using literal numeric fallback, cache lookup, or nfsmapid door upcall.
- `nfs_idmap_uid_str` and `nfs_idmap_gid_str` convert local IDs to UTF-8 owner/group strings, special-casing nobody and falling back to stringified IDs when the daemon is unavailable.
- `nfs_idmap_args` flushes caches, installs a new daemon door handle, purges DNLC, and invalidates NFSv4 rnode attributes when nfsmapid re-establishes itself.
- Cache lookup/insert routines maintain per-bucket LRU lists, evict timed-out entries, and throttle eviction while the daemon is down.
- Literal helpers parse numeric stringified IDs and format numeric IDs into UTF-8 strings.

Dependencies:
- Uses zones, door kernel upcalls, nfsmapid protocol structs, DNLC purge, NFSv4 rnode invalidation, UTF-8 conversion helpers, kmem caches, per-bucket mutexes, and `pkp_tab_hash`.

Notable details:
- Server-side SETATTR mapping failures must return errors instead of silently mapping named owners to nobody, avoiding accidental ownership changes.
- Client-side unmappable strings generally map to `UID_NOBODY`/`GID_NOBODY`; server-side invalid named strings return errors such as `EPERM` or `ECOMM`.
- The daemon’s own process avoids recursive upcalls and returns `ENOTSUP` for literal numeric mappings that should not be cached.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_idmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_recovery.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_recovery.c

Purpose: Implements NFSv4 client recovery for server failover, stale client IDs, lost state, bad stateids/seqids, volatile filehandles, grace/delay handling, and reopen/relock flows.

Key behavior:
- `nfs4_needs_recovery` classifies transport, errno, and NFS status failures that require client recovery.
- `nfs4_start_recovery` converts errors into recovery actions, records lost state or bad-seqid requests, and starts or updates a per-mount recovery thread.
- `nfs4_start_fop` and `nfs4_end_fop` bracket normal NFSv4 operations with waits for grace/delay, delegation recall, filesystem recovery, recovery-error checks, server recovery locks, and volatile filehandle rename locks.
- The recovery thread drives a state machine: fail over to a responsive server, recover clientid, refresh security info, process bad seqids, reopen files, reclaim locks, resend lost state, and complete/notify waiters.
- Failover probes candidate servers with NULL RPCs, updates root/server filehandles, purges DNLC, marks files for remap, and moves mount state to the selected server.
- Clientid recovery calls `nfs4setclientid`, then triggers reopen recovery across all mounts sharing the server.
- Filehandle and stale-handle recovery remap files, distinguish per-file stale from filesystem-wide stale, and either fail over or mark affected rnodes dead.
- Open-file recovery builds a snapshot of valid open streams, optionally remaps files, reopens with `CLAIM_PREVIOUS` or `CLAIM_NULL`, and reclaims active locks.
- Lost state recovery resends OPEN, OPEN_DOWNGRADE, CLOSE, LOCK/LOCKU, and DELEGRETURN requests and performs compensating CLOSE after successful resent OPEN.
- Bad seqid recovery resets open-owner sequencing, marks lock owners bad, flags dangling lock owners on rnodes, and sends `SIGLOST`.

Dependencies:
- Uses NFSv4 client mount/server/rnode/open/lock/delegation structures, failover infrastructure, recovery locks, RPC client creation, DNLC, file locking, signals, zones, zthreads, callb CPR, DTrace, idmap headers, and event/fact logging.

Notable details:
- Recovery is serialized per mount with `MI4_RECOV_ACTIV` but can coordinate across all mounts sharing a server after clientid recovery.
- CLOSE, LOCKU, and DELEGRETURN are allowed limited retries even after rnode recovery errors so the client can release state.
- GRACE waits are tracked per mount; DELAY backoff is tracked per rnode with exponential growth.
- For lock reclaim failures, the owning process receives `SIGLOST`, and remaining locks for that pid are unregistered/skipped.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_rnode.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_rnode.c

Purpose: Manages NFSv4 client rnodes/vnodes, including hash lookup, freelist reuse, reclamation, attribute setup, open-list snapshots, and trigger stub state.

Key behavior:
- Initializes a global rnode hash table and `rnode4_cache`; each hash bucket has a reader/writer lock.
- Creates or finds vnodes by filehandle through `makenfs4node` and `makenfs4node_by_fh`, activating shadow vnodes when parent/name information is available.
- `make_rnode4` reuses freelist rnodes when possible, otherwise allocates vnode/rnode pairs, initializes locks, open-stream lists, delegation state, readdir cache, shared filehandle refs, vnode ops, and hash links.
- Maintains a freelist whose entries keep a vnode reference count of at least one to avoid VM races.
- `rp4_addfree` decides whether to cache, recycle, or destroy an rnode based on reference counts, dirty pages, delegations, open streams, recovery errors, unmount state, and allocation pressure.
- Provides hash insertion/removal, rnode lookup by filehandle, active-rnode checks, per-VFS destruction, global/per-VFS flushing, and attribute invalidation.
- Reclaim paths free access/readdir/symlink/ACL/xattr caches from free and active rnodes, then reclaim whole rnodes from the freelist if needed.
- `r4mkopenlist` snapshots valid open streams for recovery and discards/requires recovery for delegations.
- Provides helpers for clientid lookup, lease-time lookup, fsid-based rnode search, open-list release, and root-filehandle validation.
- Sets rnodes as mirror-mount or referral trigger stubs by switching vnode ops to trigger vnode ops.

Dependencies:
- Uses vnode/VFS/page APIs, DNLC, VM page lists, NFSv4 attr/cache/access/readdir/delegation/open/lock helpers, shared filehandles, shadow vnode support, recovery structures, and kmem reclaim callbacks.

Notable details:
- The documented lock order is hash bucket lock, then vnode lock, then freelist lock/rnode state lock as applicable.
- Hashing is by shared filehandle object address, not filehandle bytes.
- Misbehaving servers returning a different root filehandle for `"."` are corrected to the mount root filehandle.
- Rnodes with recovery failure are ignored by lookup and often destroyed instead of cached.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_rnode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_shadow.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_shadow.c

Purpose: Implements NFSv4 client shadow vnodes for regular-file hard-link/name disambiguation.

Key behavior:
- `vtosv` maps a vnode back to its owning `svnode_t`, checking the master vnode first and then the rnode shadow list.
- `sv_activate` initializes the master shadow vnode for new rnodes or replaces an existing master vnode reference with a matching shadow vnode when needed.
- `sv_find` finds a shadow vnode matching parent directory filehandle and component name, or allocates a new shadow vnode sharing the master rnode.
- `sv_match` compares by `nfs4_fname_t` identity and parent shared filehandle.
- `sv_inactive` removes and destroys inactive shadow vnodes and releases the master vnode reference they hold.
- `sv_exchange` replaces a shadow vnode reference with the master vnode, used when operations need resources owned only by the master vnode.
- Initializes/finalizes the `svnode_cache`.

Dependencies:
- Uses NFSv4 rnodes, shared filehandles, filename reference helpers, vnode allocation/ops, rnode shadow-list lock, and the NFSv4 vnode ops table.

Notable details:
- Shadow vnodes have no pages; the master vnode owns cached file data and file resources.
- For non-regular files or root vnodes, shadowing is bypassed and the master shadow name can be refreshed after server-side renames.
- Creating a shadow vnode holds the master vnode until the shadow is inactivated.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_shadow.c -->