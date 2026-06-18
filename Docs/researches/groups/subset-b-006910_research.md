# subset-b-006910 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Locker.cc -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Locker.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Locker.h -->
# sources/distributed-fs/ceph/src/mds/Locker.h

## Purpose

`Locker.h` declares the CephFS MDS `Locker` class and its public contract for metadata lock coordination, client capability management, lock caching, scatter/file lock evaluation, local locks, file max-size sharing, and client leases. It is the interface used by request execution, MDCache, migration/recovery code, and message dispatch to coordinate distributed metadata consistency.

## Important APIs, Types, and Functions

The header forward declares major collaborators (`MDSRank`, `MDCache`, `CInode`, `CDentry`, `CDir`, `SimpleLock`, `ScatterLock`, `LocalLockC`, `Capability`, sessions, cap and lease messages) and defines mempool-aware aliases for inode and xattr data. `Locker(MDSRank*, MDCache*)` binds the locker to one MDS rank and its cache.

Public APIs group into message dispatch (`dispatch`, `handle_lock`, `tick`), acquisition/drop (`acquire_locks`, `try_rdlock_snap_layout`, `cancel_locking`, `drop_locks`, `drop_non_rdlocks`, `handle_locks_for_early_reply`, `drop_lock`), remote cleanup (`request_drop_remote_locks`, `request_drop_non_rdlocks`, `request_drop_locks`), lock cache (`create_lock_cache`, `find_and_attach_lock_cache`, invalidate/eval/put helpers), evaluation (`eval_gather`, `eval`, `eval_any`, `try_eval`, `eval_cap_gather`, `eval_scatter_gathers`), lock primitives, cap handling, local locks, file lock handling, file IO caps/max-size, and lease handling.

Protected APIs declare the implementation-only state-machine handlers: sending `MLock`, `_drop_locks`, simple/scatter/file handlers, client-cap internals, local lock finishers, `file_update_finish`, xattr decoding, and quiesce failure handling. Private friend classes are completion contexts used by asynchronous journal, waiter, and retry callbacks.

## Control Flow and Data Flow

Callers build lock operation vectors and pass them to `acquire_locks`; on success, the mutation owns lock references and auth pins until a drop helper releases them. Callers that receive messages invoke `dispatch`, which routes to the protected message-specific handlers implemented in `Locker.cc`. Periodic MDS ticks invoke `tick`, allowing scatter and cap queues to make progress.

Capability data flows through `issue_new_caps`, `issue_caps`, cap release/update handlers, stale-cap helpers, and max-size helpers. Lock state data flows through `eval_any` and the primitive lock functions, with `eval_any` choosing gather evaluation for unstable locks and normal evaluation for stable auth locks.

## State and Persistence Behavior

The header exposes state containers owned by `Locker`: `updated_scatterlocks`, `updated_filelocks`, global and per-client `revoking_caps` lists, and `need_snapflush_inodes`. These are in-memory queues that drive later lock writeback, cap revocation warnings, and snapflush retries. Durable changes are performed by methods declared here but implemented through journal events in `Locker.cc`.

The class stores raw pointers to `MDSRank` and `MDCache`; the `Locker` lifetime is tied to the MDS rank. Friend context classes use these pointers to resume operations after waiters or log commits.

## Dependencies and Integration Points

`Locker.h` depends on Ceph common types, mempool allocation, `mdstypes`, `Mutation`, and `SimpleLock`. It integrates with the MDS message layer, request retry contexts, MDCache object waiters, lock state machines, journal callbacks, session/capability state, and client reply lease encoding.

The interface is intentionally broad because the locker sits at the convergence of metadata mutation, distributed lock state, client cap protocol, and journal persistence. MDCache can call `scatter_nudge`, cap paths can call lock evaluation, and request paths can use lock-cache helpers to elide repeated lock acquisition.

## Risks and Edge Cases

Because the header exposes many methods that mutate lock/cap state, callers must understand which functions require auth, stable locks, held auth pins, or active MDS state. `acquire_locks` can mutate the provided lock vector by adding quiesce/version locks. The local lock APIs only apply to `LocalLockC` lock types such as version and quiesce locks. `eval_any` silently does nothing for stable non-auth locks, so callers expecting replica-side state changes must send/request through the message path.

The public state lists are intrusive lists; objects must remove their list items before destruction. Misuse of `drop_non_rdlocks` versus `drop_locks` can preserve rdlocks that intentionally gate later snap/layout operations.

## Test Signals

Header-level validation is compile coverage across MDS modules that include `Locker.h`. Behavioral coverage should exercise all declared public families through request locking, cap issue/release, scatter writeback, stale cap handling, max-size updates, and lease issue/revoke. API regression tests should verify that quiesce/version locks and lock-cache helpers remain available to request code and that friend callback classes can reach private completion methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/Locker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogEvent.cc -->
# sources/distributed-fs/ceph/src/mds/LogEvent.cc

## Purpose

`LogEvent.cc` implements runtime decoding and type-name mapping for MDS journal events. It is the central factory that turns a serialized event type in an MDS journal buffer into the correct `LogEvent` subclass for replay, inspection, and tooling.

## Important APIs, Types, and Functions

`LogEvent::decode_event(bufferlist::const_iterator)` reads the leading event type and supports both classic encoding and the newer versioned wrapper marked by `EVENT_NEW_ENCODING`. For versioned events it decodes a wrapper version, then the real event type, then delegates to the typed factory.

`LogEvent::decode_event(bufferlist::const_iterator&, EventType)` is the typed factory. It creates concrete subclasses for subtree maps, exports/imports, fragments, reset journal, session events, metadata updates, peer updates, open events, committed/purged markers, table client/server events, no-op, segment boundaries, and log-id events. `EVENT_SESSIONS_OLD` creates an `ESessions` instance and marks old encoding.

`get_type_str` maps numeric event ids back to stable names for logging and printing. `types` and `str_to_type` map strings to event ids for command/tool paths that refer to event names.

## Control Flow and Data Flow

Decode starts by reading an `EventType` from the buffer. If the value is `EVENT_NEW_ENCODING`, the method enters a `DECODE_START` block, reads the actual type, builds and decodes that event, and exits with `DECODE_FINISH`. Otherwise it treats the first type as the legacy event type and decodes directly. The typed factory logs the remaining byte count, constructs the subclass, calls `le->decode(p)`, asserts the iterator is at the end, and returns the unique pointer.

Errors in wrapper or event-body decoding are caught as `buffer::error`; the code logs at level 0 and returns `nullptr`. Unknown event types also return `nullptr`.

## State and Persistence Behavior

This file does not persist state itself. Its correctness determines whether persisted MDS journal records can be decoded during replay. The string/type map and switch statements are part of the durable journal compatibility surface: event id changes or missing cases can break recovery of existing logs.

The factory preserves special compatibility behavior for old session-map event encoding and for `EVENT_SUBTREEMAP_TEST`, which reuses `ESubtreeMap` but overrides the event type.

## Dependencies and Integration Points

The file includes every known concrete event header used by the switch, `MDSRank` for replay interfaces, and Ceph buffer/debug/config headers. It is used by `MDLog` replay and by journal inspection paths that need a polymorphic `LogEvent`. It integrates with each subclass's `encode`, `decode`, `update_segment`, `replay`, `dump`, and optional `get_metablob` behavior.

## Risks and Edge Cases

Adding a new event type requires updating `LogEvent.h` constants, this factory switch, `get_type_str`, and the `types` map. `str_to_type` uses `std::map::at`, so unknown strings throw rather than returning the comment's historical `-1`; callers must be prepared for that behavior. The `ceph_assert(p.end())` requires event decoders to consume exactly the supplied payload, making partial or trailing data a hard failure in debug/asserting builds.

The wrapper decode catch logs "type maybe" because the real type may not have decoded correctly. Returning `nullptr` must be handled by replay callers as corrupt or unsupported journal data.

## Test Signals

Tests should round-trip every event subclass through `encode_with_header` and `decode_event`, including legacy/classic encoding where still supported. Recovery tests should include old `EVENT_SESSIONS_OLD` logs, unknown event ids, truncated buffers, buffers with trailing bytes, and string mapping for every named event. Segment-boundary events should be decoded in integration tests that start new log segments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogEvent.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogEvent.h -->
# sources/distributed-fs/ceph/src/mds/LogEvent.h

## Purpose

`LogEvent.h` defines the abstract base class and numeric type ids for CephFS MDS journal events. It establishes the serialization, replay, segment-update, printing, and metablob-inspection contract implemented by all concrete event classes under `src/mds/events`.

## Important APIs, Types, and Functions

The file defines stable event ids such as `EVENT_SUBTREEMAP`, `EVENT_EXPORT`, `EVENT_IMPORTSTART`, `EVENT_FRAGMENT`, `EVENT_SESSION`, `EVENT_UPDATE`, `EVENT_OPEN`, `EVENT_COMMITTED`, `EVENT_TABLECLIENT`, `EVENT_NOOP`, `EVENT_SEGMENT`, and `EVENT_LID`. `EVENT_NEW_ENCODING` marks the versioned wrapper used by `encode_with_header`.

`LogEvent` stores `_type`, `_start_off`, `stamp`, and a `LogSegmentRef`. The main virtual interface is `encode(bufferlist&, uint64_t features)`, `decode(bufferlist::const_iterator&)`, `dump(Formatter*)`, `print(std::ostream&)`, `update_segment()`, `replay(MDSRank*)`, and `get_metablob()`. `encode_with_header` writes the versioned wrapper plus the concrete event's payload. `decode_event` is the static factory implemented in `LogEvent.cc`.

The protected `get_segment()` gives subclasses access to the current log segment while `update_segment()` runs. `friend class MDLog` allows the log to set private segment/start metadata.

## Control Flow and Data Flow

During submit, `MDLog` assigns the current `LogSegmentRef` to the event, calls `update_segment`, stamps it, and serializes it with an event header. During replay or inspection, `decode_event` reads a buffer into a concrete subclass, after which callers can invoke `replay`, `dump`, `print`, or inspect a returned `EMetaBlob`.

Subclasses use `update_segment` to register dirty inodes, dentries, dirfrags, table versions, session touches, purges, or segment boundaries against the current log segment. That data later drives log trimming and expiry.

## State and Persistence Behavior

The event type ids and wire encoding are durable journal format. `_start_off` records where an event begins in the journal stream, `stamp` records event time, and `_segment` ties the in-memory event to the segment accounting object. The base `replay` aborts, so every replayable event must override it.

`encode_with_header` uses `ENCODE_START(1, 1)`, so future changes must preserve compatibility through Ceph's encoding versioning rules. `LogSegmentRef` is a shared pointer so event objects can safely refer to segment accounting while they are being submitted or processed.

## Dependencies and Integration Points

`LogEvent.h` depends on buffer forward declarations, `utime_t`, `LogSegmentRef`, and standard map/memory/ostream/string types. It integrates directly with `MDLog`, `LogSegment`, concrete `events/*` classes, `MDSRank` replay, journal dump tooling, and `EMetaBlob` metadata inspection.

## Risks and Edge Cases

Changing event ids, reusing ids, or failing to register a new event in the decode factory can make existing journals unreplayable. Subclasses that embed an `EMetaBlob` should override `get_metablob`; otherwise tooling and MDLog touched-inode tracking can miss metadata dependencies. Subclasses that need segment expiry accounting must override `update_segment`.

The base class is non-copyable and has a deleted default constructor, which prevents accidental type-less events but requires every subclass to explicitly pass an event id. `str_to_type` is declared as returning `EventType`, but the implementation throws for unknown strings.

## Test Signals

Compile tests should ensure every concrete event subclass implements encode/decode/dump and passes a valid event id. Journal replay tests should validate `replay` overrides for replayable event types. Encoding tests should inspect that `encode_with_header` emits `EVENT_NEW_ENCODING`, the wrapper version, and the concrete type. Segment-accounting tests should verify `update_segment` mutations are visible on the current `LogSegment`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogEvent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogSegment.h -->
# sources/distributed-fs/ceph/src/mds/LogSegment.h

## Purpose

`LogSegment.h` defines the in-memory accounting object for one MDS journal segment. It records which metadata objects, client/session state, table transactions, purges, truncates, open files, and distributed operations are tied to a segment so `MDLog` can decide when the segment is safe to expire.

## Important APIs, Types, and Functions

`LogSegment::seq_t` is the segment/event sequence type. The constructor initializes segment id, offset/end positions, event count, and multiple intrusive `elist` containers with the appropriate member offsets from `CDir`, `CInode`, and `CDentry`.

The declared behavior is `try_to_expire(MDSRank*, MDSGatherBuilder&, int op_prio)`, `purge_inodes_finish(interval_set<inodeno_t>&)`, `set_purged_cb`, and `wait_for_expiry`. The inline stream operator prints sequence, offset range, and event count.

The important state fields are dirty/new dirfrags, dirty inodes/dentries, open files, dirty parent inodes, dirty dirfrag scatter categories, truncating and purging inode sets, pending mdstable commits, uncommitted leader/peer/fragment sets, last client tids, touched sessions, inotable/sessionmap/table versions, and expiry waiters.

## Control Flow and Data Flow

`MDLog::_submit_entry` creates or selects the current segment, increments `num_events`, assigns the segment to each `LogEvent`, and lets `LogEvent::update_segment` populate these lists and sets. Later, `MDLog` calls `try_to_expire`; the implementation in `journal.cc` turns each recorded dependency into stores, commits, lock nudges, table saves, waits, or purge callbacks using an `MDSGatherBuilder`.

Dirty dirfrag/dentry/inode lists flow into `CDir::commit` or inode stores. Dirty parent inodes flow into backtrace updates. Dirty dirfrag scatter lists flow into `Locker::scatter_nudge`. Open files may be re-journaled into a newer segment. Table and session versions flow into table save calls. Purging inodes install a callback that completes only after `purge_inodes_finish` subtracts all purged ids.

## State and Persistence Behavior

`LogSegment` is volatile accounting for durable journal content. It does not serialize itself as a standalone structure; rather, journal events update segment accounting as they are submitted or replayed. A segment cannot expire until every dependency represented here is durably stored or otherwise acknowledged. This makes the fields part of the crash-recovery safety mechanism even though they are in-memory.

`offset` and `end` track byte positions in the journal. `seq` is immutable. `purged_cb` and `expiry_waiters` are callback state for asynchronous expiry. Intrusive lists require that tracked cache objects own list hooks and remove/move them correctly.

## Dependencies and Integration Points

The header depends on Ceph intrusive lists, interval sets, context/gather types, fs and MDS types, and concrete cache object headers for member offsets. It integrates with `MDLog`, `LogEvent::update_segment`, `journal.cc` expiry logic, `MDCache`, `Locker`, table clients/servers, session map persistence, inode backtrace storage, purge/truncate machinery, and open file table commit tracking.

## Risks and Edge Cases

Expiry safety depends on complete segment accounting. If an event fails to register a dirty object or table/session version, the journal can trim before the corresponding state is safe. If an object remains on an intrusive list after destruction or migration, expiry can dereference invalid state. `set_purged_cb` asserts only one purge callback, so callers must not install multiple purge waits for the same segment.

Segments with open snap inodes, pending purges, uncommitted peer operations, or dirty scatterlocks can be delayed for reasons that are not obvious from byte offsets alone. Base inodes are stored directly while non-base dirty inodes commit through parent dirs, so tests must cover both paths.

## Test Signals

Integration tests should submit events that dirty each tracked object category and verify segment expiry waits for the expected commits, backtrace stores, table saves, session saves, scatter nudges, truncates, and purges. Replay tests should rebuild equivalent segment accounting from events. Purge tests should verify `purge_inodes_finish` completes `purged_cb` only when the interval set is empty. Log trimming tests should assert segments with pending open file table commits or uncommitted peer requests do not expire early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogSegment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogSegmentRef.h -->
# sources/distributed-fs/ceph/src/mds/LogSegmentRef.h

## Purpose

`LogSegmentRef.h` provides the shared ownership alias used throughout MDS journal code for `LogSegment` objects. It keeps headers lightweight by forward declaring `LogSegment` and exposing `using LogSegmentRef = std::shared_ptr<LogSegment>`.

## Important APIs, Types, and Functions

The file has no functions. Its only API is the `LogSegmentRef` alias. `LogEvent` embeds a `LogSegmentRef`; `MDLog` stores segments in maps of shared pointers; callers compare or pass segment references without including the full `LogSegment.h` definition.

## Control Flow and Data Flow

There is no runtime control flow in this file. Data flow is ownership-oriented: a `LogSegmentRef` can be copied into events, MDLog maps, and helpers so segment accounting remains alive while asynchronous log submission, expiry, replay, or callbacks may still refer to it.

## State and Persistence Behavior

The alias does not persist state. It influences lifetime of in-memory segment accounting for durable journal entries. Because it is a `std::shared_ptr`, destruction of a `LogSegment` is delayed until the last event/log owner releases its reference.

## Dependencies and Integration Points

It depends only on `<memory>`. It integrates with `LogEvent.h`, `LogSegment.h`, `MDLog.h`, segment boundary events, and any code that stores or returns segment references while avoiding a heavier include dependency.

## Risks and Edge Cases

The main risk is ownership ambiguity. Shared ownership prevents premature destruction, but cycles or excessive retention can keep old segment accounting alive. Code that only needs observation should prefer const references to existing `LogSegmentRef` values, as `LogEvent::get_segment` does, rather than unnecessary copies in hot paths.

## Test Signals

Compile coverage is the primary signal: headers that need segment references should be able to include `LogSegmentRef.h` without pulling in all cache-object definitions. Lifetime-sensitive tests should cover event submission and segment expiry with outstanding event references to ensure no dangling segment access occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/LogSegmentRef.h -->
