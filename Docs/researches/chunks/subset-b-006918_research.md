# sources/distributed-fs/ceph/src/mds/Server.cc lines 1-7833

## Chunk Scope

This chunk covers the first 7,833 lines of CephFS MDS `Server.cc`. It includes `Server` construction, perf counters, client session and reconnect handling, generic client/peer request dispatch, helper routines for path traversal, locking, inode allocation, reply construction, lookup/getattr/open/readdir handlers, inode metadata updates, file locks, layout and virtual xattr handling, normal xattr handling, node creation, and the beginning of hard-link validation. Hard-link commit, unlink/rmdir/rename, snapshot, and snapdiff completion code continues after this chunk.

## Purpose

`Server` is the MDS front door for client and peer metadata operations. In this chunk it translates wire messages (`MClientRequest`, `MClientSession`, `MClientReconnect`, `MClientReclaim`, `MMDSPeerRequest`) into `MDRequestImpl` state machines, coordinates `MDCache` path traversal and forwarding, acquires `Locker` locks/auth pins, journals durable metadata changes through `MDLog`, and sends safe or early client replies.

The code is intentionally stateful and retry-driven: most helpers return `nullptr`/`false` after installing a waiter, forwarding to another rank, or replying with an error. Callers must treat those returns as "request ownership already handled".

## Important Local Types And Contexts

- `ServerContext` adapts callbacks to `MDSContext` with access to `server->mds`.
- `ServerLogContext` adapts journal finish callbacks to `MDSLogContextBase` and marks request events as journal-committed.
- `Batch_Getattr_Lookup` batches compatible `LOOKUP`/`GETATTR` requests on a dentry or inode batch map. The head request owns dispatch; followers either receive the head trace/result or are forwarded with it.
- `C_MDS_session_finish`, `C_MDS_TerminatedSessions`, `C_MDS_TryOpenInode`, `C_MDS_TryFindInode`, `C_MDS_LookupIno2`, `C_MDS_openc_finish`, `C_MDS_inode_update_finish`, and `C_MDS_mknod_finish` are callback objects that resume requests after journal commit, retry lookup/open recovery, or apply projected metadata.
- `MDRequestRef` is the main per-operation state carrier. This code stores session, request id, path dentries/inodes, locks, auth pins, projected inode/dentry changes, allocated/preallocated inode ids, reply trace objects, extra reply buffers, peer wait state, and retry flags in it.

## Dispatch And Session Control

- `create_logger()` defines `mds_server` perf counters for message dispatch counts, cap recall/eviction throttles, and per-op latency buckets.
- The constructor snapshots MDS config into member fields: request forwarding, batched ops, cap recall/acquisition throttles, directory limits, fragment limits, client inode delegation, dispatch delay/killpoint injection, supported CephFS feature sets, and metric feature sets.
- `dispatch()` demultiplexes message types. During reconnect/clientreplay it queues replayable unsafe requests, retries requests waiting for active state, drops sessionless requests, and preserves preallocated inode replay state when needed.
- `handle_client_session()` implements open, renew caps, close, flush ack, and mdlog flush session operations. It rejects clients lacking FS auth caps, duplicate UUIDs, required features, valid `root` metadata, or acceptable blocklist state. Successful opens are journaled as `ESession` before `_session_logged()` sends `CEPH_SESSION_OPEN`.
- `reclaim_session()` and `finish_reclaim_session()` support session reset/reclaim by UUID, validating auth identity and evicting or killing the old target session before replying.
- `journal_close_session()`, `kill_session()`, `apply_blocklist()`, `terminate_sessions()`, and `_session_logged()` handle close/kill persistence, release/purge of preallocated or delegated inode ids, cap/lease cleanup, connection disposal, and sessionmap/metrics removal.
- `reconnect_clients()`, `handle_client_reconnect()`, `reconnect_gather_finish()`, `reconnect_tick()`, `waiting_for_reconnect()`, and `dump_reconnect_status()` manage MDS restart reconnect windows, client cap/snaprealm/filelock rehydration, deny-all reconnect behavior, timeout eviction, reclaim waits, and transition into clientreplay.

## Client Request Flow

1. `handle_client_request()` validates MDS cache openness, resolves the client session, handles replay/retry duplicate completed requests, trims completed request history, starts an `MDRequestRef` through `MDCache`, attaches it to the session, processes embedded cap releases, and calls `dispatch_client_request()`.
2. `dispatch_client_request()` enforces killed/aborted state, optional dispatch delay/killpoint, read-only filesystem errors, peer error propagation, metadata pool full handling, and operation-specific dispatch.
3. The switch routes lookup/getattr, xattr, readdir, file lock, create/open, mknod/link/unlink/rmdir/rename/mkdir/symlink, snapshot, and snapdiff operations to handler methods. Only handlers through the start of `handle_client_link()` are in this chunk.
4. `respond_to_request()` either replies to a client, routes a batch response through `BatchOp`, or completes an internal operation callback.
5. `reply_client_request()` records successful write requests in `Session::completed_requests`, applies inode allocations, drops non-rdlocks before reply, attaches trace/snap information, sends the reply, finishes the `MDCache` request, and re-evaluates remote-link dentries.

## Peer Request Flow

- `handle_peer_request()` and `handle_peer_request_reply()` coordinate multi-MDS operations. They create or find peer-side `MDRequestRef` instances, filter stale attempts, decode replica stray dentries, wait for replay/active states, handle finish/drop-lock messages, and route replies for remote locks, auth pins, link/rmdir/rename prep acks, and rename notifications.
- `dispatch_peer_request()` executes remote lock/unlock, auth pin, link prep, rmdir prep, and rename prep operations. For remote xlocks/wrlocks it uses `Locker::acquire_locks()`, returns lock state in a `MMDSPeerRequest` ack, and resets peer request state.
- `handle_peer_auth_pin()` verifies requested objects exist and are auth, waits for unfreeze when needed, optionally freezes a rename source inode to avoid auth-pin/lock ABBA deadlocks, returns auth pin info, or reports read-only/would-block/blocking status.
- `handle_peer_auth_pin_ack()` mirrors remote auth pin state into the leader request, clears waiters, handles read-only/EAGAIN peer errors, drops locks when a peer says it is blocked, and redispatches once all peers answered.

## Path, Locking, And Inode Helpers

- `check_access()` centralizes session auth cap checks using caller uid/gid/groups, target inode, requested mask, and setattr uid/gid fields.
- `check_fragment_space()` and `check_dir_max_entries()` enforce configured directory fragment and entry limits for creation-like operations.
- `prepare_stray_dentry()` locates or creates a stray dentry for unlink-style moves, waits on frozen stray dirs, marks the dentry stray, and pins it in the request.
- `prepare_new_inode()` allocates or consumes a preallocated inode id, optionally refills session prealloc ranges, initializes layout/dir layout, uid/gid/mode/timestamps, fscrypt blobs, client-supplied xattrs, inline-data compatibility, and inserts the inode into `MDCache`.
- `journal_allocated_inos()` records allocated/used/preallocated inode ranges into an `EMetaBlob`; `apply_allocated_inos()` applies them to `InoTable` and session state after reply.
- `rdlock_path_pin_ref()` traverses a path, optionally wants auth, installs rdlocks/snap locks, handles `ESTALE` by finding/opening the inode on peers, auth-pins the terminal inode if required, and pins it in the request.
- `rdlock_path_xlock_dentry()` traverses to a target dentry for create/unlink-like mutations, validates snapshot and `.`/`..` cases, wants auth and xlocks the dentry, handles existing/null dentry rules, and seeds `dn->first` from the newest snap sequence for new dentries.
- `rdlock_two_paths_xlock_destdn()` locks source and destination paths in deterministic order for link/rename-like operations, including remote wrlocks for source dir locks when needed.
- `try_open_auth_dirfrag()` opens or forwards to the auth rank for a directory fragment, waiting if the inode is frozen.

## Journaling, Replies, And Persistence

- Durable metadata mutations are modeled as projected in-memory changes plus `EUpdate` or `ESession` journal entries. Finish callbacks pop projected linkages, mark inodes/dirs dirty, apply request projections, notify peers/clients, share max-size state, and then reply.
- `journal_and_reply()` captures reply trace objects, optionally sends an early unsafe reply, submits the log entry, advances replay queues, and either handles early-reply locks or flushes the mdlog.
- `early_reply()` is disabled for replay, allocated-inode operations, explicit no-early requests, and operations with journaled peers. It marks xlocks done, sends an unsafe `MClientReply` with trace/extra data, updates latency counters, and records that a final safe reply should not duplicate trace/cap work.
- `set_trace_dist()` encodes snap trace, parent dir stat, dentry name/lease, and inode stat into replies. It also issues client leases and omits dist specs when all requests are forwarded to auth.
- `trim_completed_request_list()` advances per-session replay dedupe state and warns when clients do not advance `oldest_client_tid`.

## Operation Handlers In This Chunk

- `handle_client_getattr()` and lookup mode path: may batch compatible lookups/getattrs, traverses/auth-pins when needed, avoids rdlocking fields for which the client has EXCL caps, handles filelock stability optimization, checks read access, records `getattr_caps`, and replies with inode/dentry trace.
- `handle_client_lookup_ino()`, `_lookup_snap_ino()`, and `_lookup_ino_2()` resolve inode-number, parent, dentry-name, and snapped-inode lookups, reject private/purging inodes, open missing inodes, verify parent/dirfrag state, and return `ESTALE` for unrecoverable missing data.
- `handle_client_open()` validates open flags, read-only/write/snap restrictions, inline-data client compatibility, O_DIRECTORY/O_TRUNC semantics, caps/masks, optional truncate flow, open file table logging, cap issuance, max-size checks, balancer hits, and reply trace selection.
- `handle_client_openc()` implements create-open. It xlocks the destination dentry, validates charmap and alternate name, computes and validates inherited/client-requested layout, checks access/space/entry limits, optionally creates async dir-op lock cache, prepares a new file inode, issues caps, journals `openc`, adds opened ino and inode allocation metadata, and may fragment the directory.
- `_finalize_readdir()` and `handle_client_readdir()` validate directory state, throttle cap-heavy sessions, lock file/dirfrag tree, select fragments and offsets, fetch incomplete dirfrags, encode dir stat, snap trace budget, dentries, leases, inode stats, remote dentry openings, and return paginated readdir data.
- `handle_client_file_setlock()` and `handle_client_file_readlock()` manipulate in-memory POSIX/flock lock state under `flocklock`; setlock can wait, detect deadlock, remove waiting locks, wake waiters, and return `EINTR`/`EDEADLK`/`EAGAIN`.
- `handle_client_setattr()` xlocks fields based on mask, validates fscrypt client version and auth, handles chown/chgrp access, full-filesystem growth rejection, encrypted last-block truncate change_attr validation, projected uid/gid/mode/time/size/fscrypt changes, truncate-start journaling, client range recalculation, and immediate mdlog flush when waiters need file caps.
- `do_open_truncate()` handles `OPEN|O_TRUNC`: issues caps, projects truncate to zero, updates encrypted logical size if needed, records truncate-start/opened-ino in `EUpdate`, and flushes because truncation is not effective until journal commit.
- `handle_client_setlayout()` and `handle_client_setdirlayout()` validate file/dir layouts against MDSMap data pools and size/truncate state, require `MAY_SET_VXATTR` if the layout changes, xlock policy/file/snap locks as appropriate, journal dirty inode updates, and suppress early reply for directory layout.
- `handle_client_setvxattr()` handles Ceph virtual xattrs: dir/file layout, quota and snaprealm creation, quiesce block, subvolume flags and snapdir visibility, export pins, ephemeral random/distributed pins, and charmap/case/normalization/encoding. Several paths first do cheap rdlock checks, drop locks, then repeat under xlock to avoid needless writes.
- Normal `handle_client_setxattr()`/`handle_client_removexattr()` validate allowed xattr names, snap write prohibition, xattr size limit, handler-specific validation, projected xattr maps, xattr version/change_attr bumps, and journal dirty inode updates.
- `handle_client_getvxattr()` returns virtual layout, quiesce, charmap, pin, subvolume, and snapdir visibility values in an encoded extra buffer.
- `handle_client_mknod()`, `handle_client_mkdir()`, and `handle_client_symlink()` create new inode/dentry linkages, validate parent write access, directory space limits, charmap/alternate names, initialize rstat/backtrace/snap follows, issue initial caps for regular files/directories, journal `mknod`/`mkdir`/`symlink`, and maybe fragment the parent dir.
- `handle_client_link()` begins hard-link handling: disables lock cache, resolves target by ino or second path, locks destination/source paths, validates empty destination, charmap/alternate name, non-directory target, and xlocks target snap/link locks. The next lines after this chunk handle the remaining nlink/link journaling behavior.

## Xattr Handler Extension Point

The chunk defines `Server::XattrHandler` dispatch:

- Default handler validates `CREATE`, `REPLACE`, and remove semantics and directly sets/removes named xattrs.
- `ceph.mirror.info` is a special root-only logical xattr parsed as `cluster_id=<uuid> fs_id=<number>`. It persists as two concrete xattrs, `ceph.mirror.info.cluster_id` and `ceph.mirror.info.fs_id`, and validates both sides consistently.

## State And Persistence Behavior

- Session states transition through `SessionMap` projected versions and are persisted with `ESession`; prealloc inode release/purge state is journaled with the close event.
- Metadata mutations use projection (`project_inode()`, `push_projected_linkage()`, `pre_dirty()`), then journal an `EUpdate` metablob. Finish callbacks apply projections only after commit callbacks run.
- Inode allocation has three states in a request: freshly allocated ids, consumed client prealloc ids, and newly delegated/preallocated ranges. These are recorded in the metablob and applied to `InoTable`/`Session` after successful request completion.
- Replay safety depends on `Session::completed_requests`, request ids, `oldest_client_tid`, and created inode ids. Completed create/open retries may be converted into lookup/getattr-style operations to return a trace for the created inode.
- Snapshot-sensitive state uses `SnapRealm`, dentry `first`/`last`, snap locks, snap trace buffers, and snapnode updates for quota/subvolume/visibility operations.
- File size/truncation uses projected inode size, truncate sequence/state, `EUpdate::metablob.add_truncate_start()`, `Locker::issue_truncate()`, and `MDCache::truncate_inode()` after commit.

## Dependencies And Integration Points

- `MDSRank`: state machine gates, sessionmap, mdsmap, objecter, timers, internal request ids, replay queues, client/MDS messaging, clog, and global loggers.
- `MDCache`: request lifecycle, path traversal, inode/dirfrag open/fetch, forward-to-auth behavior, remote dentry open, journal helpers, stray dirs, cap reconnect, and cache LRU/popularity.
- `Locker`: capability issue/revoke, lock acquisition, lock dropping, auth pins, remote locks, cap recalls, stale cap handling, leases, max-size sharing, and truncate notifications.
- `MDLog`: journal submission, flushing, safe waiters, current log segment, and event persistence.
- `InoTable`: projected and applied inode id allocation/release.
- `Objecter`/`OSDMap`: blocklist checks, full metadata pool detection, OSD map epoch waits, data pool lookup and validation.
- `SnapRealm`/`SnapClient`: snap traces, snapnode projection, realm invalidation/update notifications.
- `MDBalancer`: inode/dir popularity hits and parent directory fragmentation checks.
- Message/event classes: `MClient*`, `MMDSPeerRequest`, `EUpdate`, `ESession`, `EOpen`, `EPeerUpdate`, `ECommitted`, and `EPurged`.

## Risks And Edge Cases

- Many functions return after scheduling retry/forward/reply; missing a `return` at callers would double-handle `MDRequestRef`.
- Lock ordering is critical. The two-path helper documents and implements deterministic ordering; auth-pin freeze logic exists specifically to avoid rename ABBA deadlocks.
- Early replies expose uncommitted metadata and are guarded by multiple checks. New mutation paths must set `no_early_reply` when clients must not observe unsafe state.
- Completed-request replay logic is subtle for create/open and for closed sessions during clientreplay; changing it can break failover idempotency.
- Full-filesystem handling permits some metadata operations and denies others. The code has special handling to avoid returning `ESTALE` for operations that should forward to auth.
- Layout and virtual xattr parsing depends on current or requested OSDMap epochs. Pool-name errors can defer on map updates before returning `EINVAL`.
- Fscrypt truncate validation compares client-provided `change_attr`; stale clients get `EAGAIN` after mdlog flush to obtain fresher metadata.
- Charmap changes require empty directories and no snapshots; create/mkdir/link paths also reject clients without charmap feature support when the parent has a charmap.
- Reconnect timeout behavior can evict or preserve clients depending on metadata timeout fields, blocklist config, deny-all reconnect config, and recent cap flush traffic.
- File locks are memory-resident and intentionally replay differently than journaled metadata writes; completed setfilelock requests are not deduped like other writes.

## Test Signals

- Session tests should cover open reject reasons, duplicate UUID, fs-name caps, root metadata validation, blocklisted clients, renew stale-to-open, close push sequence mismatch, reclaim reset, and close/kill inode prealloc cleanup.
- Failover/replay tests should cover unsafe request queuing during reconnect, completed create/open retry trace behavior, preallocated inode replay, denied reconnects, and timeout eviction/reclaim paths.
- Multi-MDS tests should cover peer auth pin waits, blocked auth pin lock dropping, remote xlock/wrlock acks, forwarding to auth dirfrag/inode ranks, and two-path lock ordering.
- Metadata op tests should cover lookup batching, `ESTALE` recovery through `find_ino_peers()`/`open_ino()`, O_TRUNC journal flushing, encrypted truncate change_attr `EAGAIN`, layout pool epoch waits, full metadata pool write denial, and old-client inline/fscrypt rejections.
- Directory tests should cover readdir pagination/offset hashes, incomplete dirfrag fetch, remote dentry opening, cap acquisition throttling, max entries/fragment size limits, charmap inheritance, alternate-name length, and parent fragmentation after create.
- Xattr tests should cover virtual xattr parse errors, quota realm creation, subvolume nesting rejection, snapdir visibility no-op/retry checks, pin bounds, charmap empty-dir/snapshot rejection, normal xattr size limits, and mirror-info root-only compound persistence.
- Creation tests should validate inode allocation/preallocation journaling, cap issuance, rstat/backtrace initialization, snap `first` assignment, and commit callback dirtying for mknod/mkdir/symlink/openc.
