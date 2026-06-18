# sources/distributed-fs/ceph/src/mds/Locker.cc

## Purpose

`Locker.cc` implements the CephFS MDS `Locker` service: the coordinator for metadata lock acquisition, lock state transitions, inter-MDS lock messages, client capability grant/revoke/update handling, client dentry leases, scatterlock writeback, and cap-driven inode persistence. It is one of the main bridges between request execution (`MutationImpl` and `MDRequest`), the metadata cache (`MDCache`, `CInode`, `CDentry`, `CDir`), the journal (`MDLog`, `EUpdate`, `EOpen`), and external protocol messages (`MLock`, `MClientCaps`, `MClientCapRelease`, `MClientLease`, `MInodeFileCaps`, `MMDSPeerRequest`).

## Important APIs, Types, and Functions

The public entry points are `dispatch`, `tick`, `acquire_locks`, `try_rdlock_snap_layout`, the lock drop/cancel helpers, lock-cache helpers, lock evaluators, rd/wr/xlock primitives, capability APIs, file-size range APIs, and lease APIs. `dispatch` demultiplexes inter-MDS lock messages, replica cap-wanted messages, client cap updates/releases, and client lease messages. `tick` drives `scatter_tick` and `caps_tick`.

`acquire_locks` is the central request-side lock acquisition path. It accepts a `MutationImpl::LockOpVec`, augments it with version locks and a shared quiesce lock when required, computes local and remote auth pins, requests remote `OP_AUTHPIN`/`OP_WRLOCK`/`OP_XLOCK` peer operations, starts lock state transitions, and returns false only after arranging a retry waiter or peer wait. `MarkEventOnDestruct` makes request wait reasons visible through `mdr->mark_event`.

The primitive lock APIs are `rdlock_start`/`rdlock_finish`, `wrlock_start`/`wrlock_finish`, `remote_wrlock_start`/`remote_wrlock_finish`, `xlock_start`/`xlock_finish`, `local_wrlock_start`/`local_xlock_start`, and force/grab variants. They manipulate `SimpleLock`, `ScatterLock`, and `LocalLockC` instances and record held locks in the mutation lock set. `eval`, `eval_any`, `eval_gather`, `simple_eval`, `scatter_eval`, and `file_eval` select state-machine transitions and issue caps when the allowed cap set changes.

The capability path is built around `issue_new_caps`, `get_allowed_caps`, `issue_caps`, `handle_client_caps`, `_do_cap_update`, `_do_snap_update`, `process_request_cap_release`, `_do_cap_release`, `remove_client_cap`, stale-cap helpers, and `caps_tick`. It consumes client cap messages, validates cap ids and migrate sequences, records dirty metadata, updates cap wanted/issued state, sends grants/revokes/acks, and maintains late-revocation tracking.

The persistence-heavy helpers are `file_update_finish`, `check_inode_max_size`, `_do_cap_update`, `_do_snap_update`, and `scatter_writebehind`. They create `MutationImpl` instances, project inodes, take journal-duration write locks, populate `EMetaBlob`, submit `EUpdate` or `EOpen` events, and apply/cleanup mutations after the log entry is safe.

## Control Flow and Data Flow

Request locking starts with the requested lock vector. `acquire_locks` first identifies additional locks and auth pins, then waits for single authority, unfreeze, active peer, or cluster recovery as needed. After pins are secure, it walks the sorted/merged lock operations: xlocks use `xlock_start`, wrlocks use local or scatter-aware `wrlock_start`, remote wrlocks send `MMDSPeerRequest::OP_WRLOCK`, and rdlocks use `rdlock_start`. Failure paths drop already-held locks, drop auth pins, and enqueue retry contexts.

Lock state transitions follow the `SimpleLock` and `ScatterLock` state machines. Auth MDS instances send `MLock` actions such as `LOCK_AC_SYNC`, `LOCK_AC_LOCK`, and `LOCK_AC_MIX` to replicas; replicas acknowledge with `LOCK_AC_LOCKACK`, `LOCK_AC_SYNCACK`, or `LOCK_AC_MIXACK`. `eval_gather` is the convergence point: it checks local rd/wr/xlocks, client leases, cap revocation needs, replica gather sets, flushing state, and file recovery state before moving to the next state and waking waiters.

Client cap data flows from `MClientCaps` into the inode's `Capability` and projected inode state. `handle_client_caps` validates MDS lifecycle state, session state, completed flush TIDs, inode existence, OSD epoch barriers, freeze policy, cap id, and migrate sequence. Dirty flushes create acks and call `_do_cap_update` or `_do_snap_update`; clean wanted/receipt updates call `adjust_cap_wanted`, `confirm_receipt`, `eval`, and `issue_caps`. Cap release messages follow the same frozen-inode deferral policy through `_do_cap_release` or `process_request_cap_release`.

Scatterlock dirty data flows from `mark_updated_scatterlock` to the `updated_scatterlocks` list, then through `scatter_tick`/`scatter_nudge` into lock transitions or `scatter_writebehind`. `scatter_writebehind` forcefully takes a write lock, finishes scatter-gather accounting into the inode projection, journals the dirty inode, flushes the log, and completes in `scatter_writebehind_finish`.

## State and Persistence Behavior

Held request locks and lock-cache references live in `MutationImpl`. Local auth pins and remote peer state guard objects against migration and freezing while the mutation is in flight. `request_drop_remote_locks`, `_drop_locks`, and lock-specific finishers are responsible for symmetric cleanup, peer notification, waiter wakeup, and cap reissue.

Persistent inode state is not changed directly. File size, xattrs, auth fields, inline data, fscrypt fields, client write ranges, old inode snapshots, and scatter-derived stats are projected into a mutation and journaled through `EUpdate` or `EOpen`. Completion contexts call `mut->apply()`, send flush acks, drop locks, issue caps, and cleanup pins. Max-size growth may force an immediate `mdlog->flush()` so clients promptly learn larger writable ranges.

Lock state itself is distributed state. Auth lock transitions are propagated to replicas through `MLock` messages, and replicas can ask auth for rdlock/scatter/unscatter/nudge actions. Dirty scatterlocks persist by journaling the inode after assimilating dirfrag/accounting updates. Cap flush idempotence is persisted through session completed-flush tracking and `EMetaBlob::add_client_flush`.

The file maintains volatile but important queues: `updated_scatterlocks`, `updated_filelocks`, `revoking_caps`, `revoking_caps_by_client`, and `need_snapflush_inodes`. These queues drive periodic retries, warnings, and snapflush nudges; they are not themselves durable, but they cause journal or protocol actions that converge durable state.

## Dependencies and Integration Points

`Locker.cc` depends on MDS cache objects (`CInode`, `CDentry`, `CDir`, `MDCache`), lock classes (`SimpleLock`, `ScatterLock`, `LocalLockC`, `MDLockCache`), request/mutation machinery (`MutationImpl`, `MDRequestRef`, `MDSContext`), MDS lifecycle and topology (`MDSRank`, `MDSMap`, sessions), journal events (`EUpdate`, `EOpen`, `EMetaBlob`, `MDLog`), messaging (`MLock`, `MClientCaps`, `MClientCapRelease`, `MClientLease`, `MInodeFileCaps`, `MMDSPeerRequest`), and OSD map barriers through `Objecter`.

It integrates with migration/freezing through auth pins, freeze waiters, migrator waiter accounting, ambiguous auth waiters, and cluster degraded/rejoin gating. It integrates with the open file table by logging `EOpen` for wanted caps and by preserving snap inodes with pending flushes. It integrates with balancer popularity through `hit_inode`, with session health through completed flushes and stale cap revocation, and with client-visible consistency through cap and lease messages.

## Risks and Edge Cases

The highest-risk area is lock cleanup symmetry. Remote xlocks/wrlocks and remote auth pins must be released with peer requests before local state is discarded, otherwise peer MDSs can retain pins or locks. Quiesce lock failures intentionally drop all locks, not just non-rdlocks, to avoid deadlocks with snapshot/layout operations.

Frozen, freezing, ambiguous-auth, degraded-cluster, rejoin, and recovery states create many retry paths. Missing a waiter or using a less permissive frozen-cap deferral policy can deadlock request processing against cap release/writeback. The code explicitly requires `should_defer_client_cap_frozen` to be consistent across request cap releases and client cap handling.

Cap sequencing is subtle. The code filters old migrate sequences, cap id mismatches, duplicate flush TIDs, stale cap releases, and wanted updates with issue-seq mismatches. Reissuing, revoking, suppressing, and stale-cap handling must preserve client protocol order, especially around dirty cap flush acks and snapflush. Xattr updates intentionally ignore oversized xattr payloads while advancing the version, which is a data-consistency edge case called out in the code.

Scatterlock and filelock transitions can require log flushes to release unsafe locks or propagate dirty accounting. Early replies, dirty scatter data, cap revocations, file recovery, and lock caches can all delay state transitions. Replica requests during degraded states are gated by MDS map state to avoid sending messages to peers that cannot process them.

## Test Signals

Useful tests include multi-client metadata operations that require rd/wr/xlocks, cross-MDS rename/link/unlink paths that exercise remote auth pins and remote wr/xlocks, degraded/rejoin replay tests for snap/layout xlocks, and quiesce/subvolume snapshot races. Lock-cache tests should cover cached unlink/create style operations, cache invalidation on cap loss, and frozen dirfrag interaction.

Capability tests should cover grant/revoke ordering, dirty cap flush acks, duplicate flush TID replay, stale session revocation/resume, cap release during freezing, snapflush including null snapflush inference, OSD epoch barriers, xattr version and maximum-size enforcement, inline data update, and file max-size sharing. Scatter tests should force dirty dirfrag/nest/file accounting into `scatter_writebehind`, replica gather acks, and log-segment expiry nudges. Lease tests should cover issue, renew, revoke ack, release, and stale-session lease cleanup.
