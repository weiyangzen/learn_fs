# Research: sources/distributed-fs/ceph/src/mds/Server.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006918`: lines 1-7833, `Docs/researches/chunks/subset-b-006918_research.md`
- `subset-b-006919`: lines 7834-12486, `Docs/researches/chunks/subset-b-006919_research.md`

## Chunk Research

### subset-b-006918: lines 1-7833

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

### subset-b-006919: lines 7834-12486

# sources/distributed-fs/ceph/src/mds/Server.cc lines 7834-12486

## Scope and Purpose

This chunk is the tail of CephFS MDS `Server.cc`. It implements metadata mutations and snapshot-diff style read operations after the earlier path-resolution and create/open logic: hard link completion, unlink/rmdir, rename, peer prepare/commit/rollback protocols, snapshot listing and mutation, block diff, readdir snapdiff, and reconnect status helpers.

The code is centered on making client-visible POSIX namespace changes durable through MDS journal entries (`EUpdate`, `EPeerUpdate`) while preserving consistency across multiple authoritative MDS ranks. Most client operations follow the same pattern: validate and lock dentries/inodes, prepare projected dentry/inode/snaprealm state, journal the prepared state, apply projections in a log callback, notify peers/clients/cache subsystems, and respond to the client. Distributed mutations add a peer prepare/ack/commit or rollback protocol with explicit rollback blobs.

## Important APIs, Types, and Functions

- Link paths:
  - `_link_local()` and `_link_local_finish()` create a new remote dentry for a hard link to an auth inode, increment `nlink`, update `ctime`, `rstat.rctime`, `change_attr`, handle global snaprealm splitting, journal parent/inode dirties, then apply and notify dentry link watchers.
  - `_link_remote()` and `_link_remote_finish()` handle hard-link increment and remote unlink decrement when the target inode is authoritative on another MDS. They send `MMDSPeerRequest::OP_LINKPREP` or `OP_UNLINKPREP`, record `witnessed` peers, journal local dentry changes with `had_peers`, and commit after peer acks.
  - `handle_peer_link_prep()`, `_logged_peer_link()`, `_commit_peer_link()`, `_committed_peer()`, `do_link_rollback()`, and `_link_rollback_finish()` implement the peer side and rollback for remote link/unlink nlink changes.

- Unlink and rmdir:
  - `handle_client_unlink()` branches between unlink and rmdir, validates directory/non-directory semantics, checks permissions, prepares stray dentries for primary-link removal, locks link/snap/file/stray state, prepares snaprealm handoff blobs, gathers rmdir witnesses for subtree-root directories, and dispatches to `_link_remote(..., false, ...)` or `_unlink_local()`.
  - `_unlink_local()` projects the dentry to null, decrements inode `nlink`, records `stray_prior_path`, marks zero-link inodes orphaned, moves primary links to stray dentries when needed, journals cow/null dentries, and projects subtree renames for directories.
  - `_unlink_local_finish()` pops projected linkages, applies inode/fnode changes, sends unlink notifications, adjusts subtree and snaprealm state, responds, removes unlinked dentries, and notifies stray purge logic.
  - `_rmdir_prepare_witness()`, `handle_peer_rmdir_prep()`, `_logged_peer_rmdir()`, `handle_peer_rmdir_prep_ack()`, `_commit_peer_rmdir()`, `do_rmdir_rollback()`, and `_rmdir_rollback_finish()` provide distributed rmdir witness, journal, commit, and rollback behavior for auth subtree dirfrags.
  - `_dir_is_nonempty_unlocked()`, `_dir_has_snaps()`, and `_dir_is_nonempty()` are validation helpers for rmdir and rename-over-directory checks.

- Rename:
  - `handle_client_rename()` is the leader-side rename state machine. It validates dot/dotdot, alternate names, source/destination type compatibility, no self-descendant moves, stray migration constraints, common-ancestor traces, link-merge cases, cross-subvolume snaprealm rules, permissions, fragmentation limits, and directory emptiness. It prepares stray dentries, locks involved inodes and dentries, opens remote directory frags when necessary, builds snaprealm updates, computes witnesses, flushes projected dentries before peer prepares, sends `OP_RENAMEPREP` to peers, then journals `_rename_prepare()` and completes through `_rename_finish()`.
  - `_rename_prepare_witness()` encodes source/destination traces, alternate name, stray info, snaprealm blobs, source auth rank, witness set, and op stamp into peer prepare messages.
  - `_rename_prepare_import()` decodes imported inode/capability state from peer acks and stages force-open sessions and migrated cap state.
  - `_need_force_journal()` detects when rename must force-journal a destination or stray dentry because local auth subtree dirfrags need replayable subtree metadata.
  - `_rename_prepare()` is the shared projection and journal builder for leader and peer rename. It handles primary/remote link variants, link merge, silent stray reintegration, destination overwrite to stray, inode import/export projections, snaprealm projections, nlink/ctime/change_attr updates, parent fnode accounting, `EMetaBlob` dentry records, forced subtree journaling, corruption injection for dentry `first`, and `project_subtree_rename()`.
  - `_rename_apply()` applies the projected namespace changes after journaling: unlink old destination/source entries, pop projected linkages, link remote or primary destination, finish inode import/cap transfer, mark dirty versions, apply mutation projections, update subtree maps, issue snaprealm invalidation, and remove unlinked source dentries.
  - `handle_peer_rename_prep()`, `_logged_peer_rename()`, `_commit_peer_rename()`, `do_rename_rollback()`, `_rename_rollback_finish()`, `handle_peer_rename_prep_ack()`, `handle_peer_rename_notify_ack()`, and `_peer_rename_sessions_flushed()` implement peer-side prepare, ambiguity/freeze handling, session flushing, inode export/import, prepare ack expansion for insufficient witnesses, commit, abort rollback, and cleanup.
  - `_rollback_repair_dir()` repairs projected fnode accounting for rollback.

- Snapshot operations:
  - `handle_client_lssnap()` reads a directory's `SnapRealm`, encodes snapshot dentries with leases and inode stats, honors max entry/byte limits, and sets readdir completion flags.
  - `handle_client_mksnap()` validates snapshot feature enablement, UID bounds, directory/system-dir rules, subvolume restrictions, name and count limits, obtains a snap table transaction from `snapclient`, projects inode and snaprealm creation state, journals `TABLE_SNAP`, and finishes in `_mksnap_finish()`.
  - `handle_client_rmsnap()` validates name/existence/access, obtains snap destroy transaction state, projects snaprealm deletion and inode stat updates, journals `TABLE_SNAP`, and finishes in `_rmsnap_finish()` with stale snap-data purge.
  - `handle_client_renamesnap()` validates same parent directory, source/destination names, access, prepares snap update transaction state, changes `SnapInfo::name`, journals, and finishes in `_renamesnap_finish()`.

- Diff/read helpers:
  - `handle_client_file_blockdiff()` resolves two file paths, validates regular files, handles identical inodes as no-diff, and delegates object diff scanning to `mdcache->file_blockdiff()`. `handle_file_blockdiff_finish()` encodes `BlockDiff` into reply extra data.
  - `handle_client_readdir_snapdiff()` resolves and locks an auth directory, throttles on high cap acquisition, adjusts requested dirfrag/hash cursor, opens/fetches complete dirfrag data, validates snapshot ids, encodes directory stat, budgets reply bytes, and delegates to `_readdir_diff()`.
  - `_readdir_diff()` builds a bounded directory diff response between two snap ids, preserving hash-order flags and rollback points for same-name entries that do not fit in the response.
  - `build_snap_diff()` walks dentries, skips purging/out-of-range entries, opens remote dentries when needed, distinguishes deleted/new/unchanged/modified files and directories across snap ranges, and calls a result callback with existence state.
  - `get_snap_trace()` selects old or new snaprealm trace encoding based on client feature bits.
  - `waiting_for_reconnect()` and `dump_reconnect_status()` expose reconnect gather state.

## Control Flow and Distributed Protocols

Local mutations generally do:

1. Traverse/auth-pin dentries and inodes through earlier helpers.
2. Validate operation-specific semantic constraints and access.
3. Acquire `MutationImpl::LockOpVec` locks, often `linklock`, `snaplock`, `filelock`, `nestlock`, and dentry xlocks.
4. Project inode, dentry, fnode, and snaprealm changes in memory.
5. Build an `EUpdate` metablob with client request identity and dirty dentry/inode/parent records.
6. Submit to `mdlog` through `journal_and_reply()` or `submit_mdlog_entry()`.
7. In the log callback, pop/apply projections, mark dirties, update subtree/snaprealm/cache state, send dentry/snap notifications, then respond.

Peer-assisted mutations add a two-phase protocol:

- The leader sends an `MMDSPeerRequest` prepare message and inserts the peer in `waiting_on_peer`.
- The peer journals an `EPeerUpdate::OP_PREPARE` when local replay state is required, stores rollback data, applies projected state, and replies with `OP_*PREPACK`. Some peer paths may mark replies as not journaled when no metablob is needed.
- The leader resumes the client request after all peers are witnessed, records `had_peers` in its own journal entry, and later commits or aborts peers through the stored `peer_commit` context.
- Peers commit with `EPeerUpdate::OP_COMMIT` and notify the leader with `OP_COMMITTED`; on failure they call the operation-specific rollback routine and finish rollback before resolve can proceed.

Rename has the most complex control flow. The destination dentry auth MDS acts as leader so cached inodes stay connected. It may need all replicas of source/destination/stray dentries as witnesses; source dentry auth is prepared last to handle ambiguous auth and inode export. When source primary auth moves to destination auth, the peer exports inode/cap state in `inode_export`; the leader imports that state in `_rename_prepare_import()` and `_rename_apply()`. The peer may return an expanded witness list instead of a normal witnessed ack, causing the leader to retry with additional witnesses.

## State and Persistence Behavior

- Dentry linkage state is staged with `push_projected_linkage()` and made real with `pop_projected_linkage()`, `link_remote()`, `unlink_inode()`, `mark_dirty()`, and `touch_dentry_bottom()`.
- Inode state is staged through `project_inode()`, `pre_dirty()`, and projected `mempool_inode` fields. Mutations update `nlink`, `ctime`, recursive stat timestamps, `change_attr`, versions, `stray_prior_path`, orphan state, and backtraces.
- Directory fnode and recursive accounting are adjusted through `predirty_journal_parents()`, `project_fnode()`, `_rollback_repair_dir()`, and `mut->add_updated_lock()` for file/nest locks.
- Snaprealm state is projected through `project_snaprealm()`, `prepare_new_srnode()`, `record_snaprealm_parent_dentry()`, `record_snaprealm_past_parent()`, `mark_snaprealm_global()`, `clear_snaprealm_global()`, encoded into peer request snap blobs, and invalidated/notified with `send_snap_update()`, `do_realm_invalidate_and_update_notify()`, `send_snaps()`, or `prepare_realm_merge()`.
- Persistent journal records are `EUpdate` for leader/local client operations and `EPeerUpdate` for peer prepare/commit/rollback. They include client request ids, oldest client tids, table transaction ids, rollback blobs, renamed directory inode/frags, and metablobs describing dentry/inode/dir state needed for replay.
- Rollback blobs preserve enough old state to undo peer-side changes: link rollback stores old inode ctime, dir mtimes/rctimes, nlink direction, and optional snap blob; rmdir rollback stores source/destination dentry locations and optional snap blob; rename rollback stores source/destination/stray dentry records, old directory times, old ctimes, snap blobs, and dentry linkage identifiers.
- Snapshot create/remove/rename are coupled to the snap table through `snapclient->prepare_*()` and `snapclient->commit()`, with `TABLE_SNAP` transactions recorded in the metadata journal.

## Dependencies and Integration Points

- `MDRequestRef` carries client or peer request state, request ids, op stamps, paths, locks, projected value maps, rollback blobs, witness/peer sets, import/export buffers, snap ids, and reply buffers.
- `MDSRank` services are used for session lookup, mdsmap feature/epoch checks, sending peer messages, waiting for active peers/maps, timers, queueing waiters, and snapclient table operations.
- `MDCache` supplies inode/dentry/dirfrag lookup, path traversal, journal metablob helpers, subtree rename projection/application, peer uncommitted tracking, rollback tracking, stray handling, snap update notifications, remote dentry opening, lru touches, and blockdiff/snapdiff helpers.
- `Locker` is responsible for metadata locks, snap layout locks, cap/lease encoding, client lease issuance, lock cache creation, imported/exported xlock repair, and eval after cap imports.
- `Migrator` integrates with rename auth transfer by encoding/decoding inode export, finishing imported/exported caps, gathering export clients, and forcing sessions open.
- `MMDSPeerRequest` encodes cross-MDS prepare/ack/commit traffic for link/unlink, rmdir, and rename, including paths, snap blobs, alternate names, witness sets, stray blobs, inode export blobs, and status flags.
- `EMetaBlob`, `EUpdate`, and `EPeerUpdate` are the journal substrate that make namespace changes replayable.
- `SnapRealm`, `SnapInfo`, `SnapPayload`, `sr_t`, and `TABLE_SNAP` connect namespace mutations to snapshot isolation and client-visible snapshot directories.
- `Session` and client feature flags influence snap trace format, cap throttling, lease/stat encoding, and forced session flushing.

## Risks and Edge Cases

- Distributed operations rely on exact ordering of peer prepare, local journal, peer commit, and rollback. Missing a `waiting_on_peer` transition or incorrect `witnessed` bookkeeping can leave uncommitted peer updates or double-apply rollback.
- Rename is highly sensitive to auth ownership and witness completeness. Insufficient witness sets are dynamically expanded; failures in that path can leave ambiguous auth/frozen inode state that must be cleaned by `_commit_peer_rename()` or `_rename_rollback_finish()`.
- Snaprealm transitions are interleaved with link/unlink/rename. Incorrect projection or rollback of `sr_t` blobs can break snapshot visibility, global snaprealm parentage, or cap snap notifications.
- Rmdir and rename-over-directory use fast unlocked emptiness checks followed by locked checks. The fast path can only reject obvious non-empty directories; correctness depends on later `filelock` validation.
- Stray dentries are used for primary-link deletion and overwritten rename targets. Races are explicitly noted after `respond_to_request()` drops locks, so `notify_stray()` is conditional on the stray still being linked.
- Peer paths sometimes skip journaling when the local metablob is empty. Callers must honor `is_not_journaled()` so commit/rollback cleanup does not assume a journaled peer update exists.
- `do_rename_rollback()` intentionally avoids `is_auth()` during resolve and uses authority ranks directly. Resolve-mode behavior is fragile if required dirfrags/dentries were trimmed or not discoverable.
- Reply byte budgeting in `lssnap`, blockdiff, and snapdiff must avoid partial/inconsistent entries. `_readdir_diff()` has explicit rollback logic for same-name snapshot entries that would otherwise split across fragments.
- Remote dentry resolution during snapdiff may issue leases/caps before discovering missing remote inode state; the code either opens remote dentry asynchronously and returns a partial reply or drops locks and retries when no entries were emitted.
- Fault-injection assertions (`mds_kill_link_at`, `mds_kill_rename_at`, `inject_rename_corrupt_dentry_first`) indicate intentionally tested crash windows. Production changes around those points need replay/rollback coverage.

## Test Signals

- Hard link tests should cover local auth targets, remote auth targets, cross-subvolume rejection (`-EXDEV`), no-link target rejection, alternate name length, snaprealm global split, and replay through `link_local`/`link_remote` journal events.
- Unlink/rmdir tests should cover file unlink, directory unlink rejection (`-EISDIR`), rmdir non-dir rejection (`-ENOTDIR`), empty/non-empty directory checks, primary-link move to stray, remote unlink prepare, subtree-root rmdir witnesses, and rollback after peer failure.
- Rename tests should cover no-op same dentry, self-descendant rejection, type mismatch over existing destination, alternate-name mismatch, link merge from stray, overwrite to stray, remote source auth import/export, expanded witness retry, forced journal for nested auth subtrees, cross-subvolume rejection, and crash/replay at `mds_kill_rename_at` points.
- Snapshot tests should cover disabled snapshots, UID min/max enforcement, invalid names, duplicate names, per-directory snapshot limit, subvolume descendant rejection, create/remove/rename journal table commits, snap update notification, stale snap-data purge, and lssnap pagination/byte limits.
- Snapdiff and blockdiff tests should cover invalid snap ids, cap acquisition throttling, dirfrag cursor adjustment, incomplete/frozen dirfrag retry, remote dentry opening during diff, same-file no-op blockdiff, byte-limited responses, same-name rollback behavior, and feature-dependent snap trace encoding.
- Recovery tests should verify `EPeerUpdate` prepare/commit/rollback replay, `mdcache->add_uncommitted_*` cleanup, `finish_rollback()`, resolve-mode subtree trimming, snaprealm rollback, and ambiguous-auth cleanup after aborted peer rename.
