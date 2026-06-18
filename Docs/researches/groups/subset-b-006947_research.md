# Research: subset-b-006947

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PrimaryLogPG.h -->
# sources/distributed-fs/ceph/src/osd/PrimaryLogPG.h

## Purpose
`PrimaryLogPG.h` declares Ceph's primary replicated placement-group implementation. It is the OSD-side coordinator that turns client operations, recovery work, cache-tiering activity, watches/notifies, snap trimming, and backend replication callbacks into ordered PG log updates and object-store transactions. The class inherits from `PG`, `PGBackend::Listener`, and `ECListener`, so it is both a PG state owner and the callback surface used by `ReplicatedBackend` and erasure-coded backends.

## Important APIs, Types, And Functions
Key nested types are `OpContext`, `RepGather`, `CopyOp`, `FlushOp`, `ProxyReadOp`, `ProxyWriteOp`, `CLSGatherOp`, and `ManifestOp`. `OpContext` is the central per-client-operation state holder: it carries the request, old and new object/snapset state, log entries, stats deltas, transaction, lock manager, watch/notify side effects, async read completions, replies, and success/commit/final callbacks. `RepGather` tracks a replicated mutation after submission, including the object, version, rep tid, lock manager, completion callbacks, and commit state. The class exposes backend listener methods such as `log_operation()`, `on_local_recover()`, `on_peer_recover()`, `update_last_complete_ondisk()`, `schedule_recovery_work()`, and object lock helpers.

Major public entry points include `do_request()`, `do_op()`, `do_op_impl()`, `do_pg_op()`, `do_backfill()`, `snap_trimmer()`, `do_osd_ops()`, `start_cls_gather()`, and lifecycle hooks like `on_change()`, `on_activate_complete()`, `on_flushed()`, `on_removal()`, and `on_shutdown()`. Copy/cache-manifest APIs include `start_copy()`, `finish_copyfrom()`, `start_flush()`, proxy read/write handlers, dedup/chunk-manifest refcount helpers, and cache promotion/redirect helpers.

## Control Flow
Client operation flow is: request enters `do_request()`, object context and locks are acquired, `OpContext` accumulates effects through `do_osd_ops()`, `prepare_transaction()` builds a `PGTransaction`, and `finish_ctx()`/`execute_ctx()` submit through the backend. Backend commit callbacks eventually release locks, execute registered callbacks, and reply. Recovery/backfill flow starts through `start_recovery_ops()`, selects primary, replica, or backfill work, and delegates object push/pull/delete preparation to `PGBackend`.

Snap trimming is modeled as a Boost statechart with states such as `NotTrimming`, `WaitReservation`, `AwaitAsyncWork`, `WaitRepops`, `WaitTrimTimer`, `WaitRWLock`, and `WaitScrub`. This protects snap deletion against scrub, reservations, object locks, outstanding repops, and OSD map flags. Cache-tiering control flow uses `TierAgentState`, hit sets, promotion, flush, eviction, proxy operations, and redirect/requeue decisions.

## State And Persistence Behavior
Persistent state is mediated through PG logs, `PGTransaction`, object attrs, snapset mappings, hit-set objects, temp objects, and object-store collection operations. `log_operation()` updates hit-set history, snap mappings, projected rollback state, replica object context cleanup, and recovery-state log append. Temp objects are explicitly tracked through backend listener methods. In-memory state includes object-context LRU, snapset-context registry, recovery maps, backfill tracking, copy/flush/proxy/manifest maps, watcher state, and dynamic performance stats.

## Dependencies And Integration Points
This file integrates `PG`, `OSD`, `PGBackend`, `ReplicatedBackend`, `PGTransaction`, `Watch`, `TierAgentState`, `SnapMapper`, object-store transactions, messenger messages, monitor commands, scrub/recovery state, hit sets, and class methods. It is the main bridge between high-level PG semantics and backend-specific IO/replication.

## Risks And Test Signals
High-risk areas are lock ordering, async callback lifetime, PG interval changes, temp-object cleanup, duplicate request logging, snap trimming races, recovery/backfill accounting, and cache-manifest refcount updates. Useful tests are OSD unit/integration tests covering replicated writes, replay/dup detection, degraded recovery, backfill, snap trim under scrub, watch notify disconnects, cache promotion/flush/eviction, manifest dedup, and fault injection around object-store or replica commit errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/PrimaryLogPG.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ReplicatedBackend.cc -->
# sources/distributed-fs/ceph/src/osd/ReplicatedBackend.cc

## Purpose
`ReplicatedBackend.cc` implements the `PGBackend` for replicated pools. It handles replicated client mutations, replica sub-ops and replies, recovery push/pull traffic, local object reads, deep scrub reads, and progress updates for `pg_committed_to`. Unlike erasure-coded backends, reads are direct object-store reads and EC hooks abort if called.

## Important APIs, Types, And Functions
The implementation defines context helpers for sending messages after transactions and scheduling recovery work. `generate_transaction()` lowers a `PGTransaction` into an `ObjectStore::Transaction`, preserving object initialization, deletion, rename, clone, truncate, attrs, omap, alloc hints, and buffer updates while collecting temp objects. Client write replication centers on `submit_transaction()`, `issue_op()`, `generate_subop()`, `do_repop()`, `repop_commit()`, `do_repop_reply()`, and `op_commit()`.

Recovery centers on `recover_object()`, `prepare_pull()`, `start_pushes()`, `prep_push_to_replica()`, `prep_push()`, `build_push_op()`, `handle_pull()`, `handle_pull_response()`, `handle_push()`, `handle_push_reply()`, `submit_push_data()`, and `submit_push_complete()`. Deep scrub uses `be_deep_scrub_read_data()` and `be_deep_scrub()` to compute data and omap digests while respecting configured stride/key limits. `send_pct_update()`, `maybe_kick_pct_update()`, and `cancel_pct_update()` manage delayed committed-to updates.

## Control Flow
For a primary write, `submit_transaction()` applies stat deltas, converts the PG transaction, registers an `InProgressOp`, sends `MOSDRepOp` messages to all acting recovery/backfill peers, logs the operation locally, queues the local transaction, and marks the operation applied. Replicas receive `MOSDRepOp` in `do_repop()`, decode shipped transactions/logs, update temp tracking and local PG log state, queue local transactions, and send an on-disk `MOSDRepOpReply` from `repop_commit()`. The primary removes peers from `waiting_for_commit` in `do_repop_reply()` and runs the final commit context when all commits arrive.

Recovery either pulls missing local objects from a peer or pushes local objects to missing peers. Pulls select an available source from missing-location state, compute copy/clone subsets, and send `MOSDPGPull`. Pushes are chunked by configured max cost/object limits and may use existing clone overlap on the receiver to reduce data transfer. Completion calls back to the parent PG with local, peer, or global recover notifications.

## State And Persistence Behavior
In-memory state includes `in_progress_ops`, `pushing`, `pulling`, `pull_from_peer`, and a scheduled PCT timer callback. Persistent writes are object-store transactions and PG log entries. Recovery writes may target temporary recovery objects until a complete object is atomically renamed into place. Omap and attrs are copied alongside data; zero extents are reconstructed from fiemap/copy subset state.

## Dependencies And Integration Points
The backend depends on `PGBackend::Listener` for PG locks, log updates, stats, recovery notifications, message sends, timers, temp-object tracking, and object-context locks. It uses Ceph message types `MOSDRepOp`, `MOSDRepOpReply`, `MOSDPGPush`, `MOSDPGPull`, `MOSDPGPushReply`, and `MOSDPGPCT`, plus `ObjectStore`, `PGTransaction`, scrub types, missing maps, and OSD feature flags.

## Risks And Test Signals
Risk is concentrated in commit quorum accounting, interval-change cleanup, mixed-version transaction encoding, clone-overlap calculations, temp-object rename/removal, recovery progress monotonicity, deep scrub digest compatibility, and failure paths that call `on_failed_pull()`. Test signals include replicated write/commit latency counters, recovery push/pull tests with snaps and sparse objects, deep scrub digest tests, PCT feature tests, object-store EIO injection, degraded/backfill repair tests, and interval reset tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ReplicatedBackend.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ReplicatedBackend.h -->
# sources/distributed-fs/ceph/src/osd/ReplicatedBackend.h

## Purpose
`ReplicatedBackend.h` declares the replicated-pool implementation of `PGBackend`. It defines the public backend contract used by `PrimaryLogPG` plus the private state machines for replicated write commit tracking and recovery push/pull progress.

## Important APIs, Types, And Functions
`ReplicatedBackend` overrides recovery handle creation/execution, `recover_object()`, message dispatch, recovery-source validation, lifecycle cleanup, omap accessors, synchronous/local reads, EC capability stubs, deep scrub hooks, on-disk size calculation, and `submit_transaction()`. `RPGHandle` batches outgoing `PushOp` and `PullOp` vectors per target shard. `push_info_t` and `pull_info_t` track `ObjectRecoveryInfo`, `ObjectRecoveryProgress`, object contexts, stats, lock managers, source peers, and cache hints. `InProgressOp` tracks a replicated client mutation by tid, waiting shards, commit callback, original op, and version.

Private helpers declared here cover message-specific handlers, recovery chunk building, pushed-data trimming, temp recovery writes, clone subset calculations, `MOSDRepOp` generation, commit processing, and PCT timer behavior. `pct_callback_t` adapts the PG lock/ref protocol to `common::intrusive_timer`.

## Control Flow
The public `_handle_message()` override dispatches OSD PG messages into private handlers. `submit_transaction()` starts the replicated write path and `op_commit()`/`do_repop_reply()` close it after local and peer commits. `recover_object()` chooses pull or push based on local missing state, then `run_recovery_op()` emits accumulated network messages. The header also documents that replicated reads are synchronous/local and that `call_write_ordered()` can invoke callbacks inline because replicated submission is ordered in `submit_transaction()`.

## State And Persistence Behavior
The header’s state declarations show which data survives only in memory: `pushing`, `pulling`, `pull_from_peer`, `in_progress_ops`, and `pct_callback`. Durable state is not stored directly by the backend object; it is written through `ObjectStore::Transaction` and parent PG log operations implemented in the `.cc` file. Recovery locks in `push_info_t`/`pull_info_t` must be released on completion or reset.

## Dependencies And Integration Points
The class integrates with `PGBackend`, `ObjectStore`, `ObjectContext`, missing/recovery types, scrub types, `MapCacher`-independent omap calls, Ceph messenger messages, and parent listener callbacks. It assumes replicated-pool semantics: availability for recovery requires any copy, readability requires the local shard, and EC encode/decode APIs are invalid.

## Risks And Test Signals
Header-level risks are ownership and lifecycle contracts: every map entry needs cleanup on `on_change()`/`clear_recovery_state()`, callbacks need PG locking, and EC stubs must never be reached for replicated pools. Tests should exercise message dispatch, recovery cancellation, state dump output, commit callback release, and compile-time/interface conformance against `PGBackend`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/ReplicatedBackend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Session.cc -->
# sources/distributed-fs/ceph/src/osd/Session.cc

## Purpose
`Session.cc` implements OSD client-session backoff cleanup and acknowledgement handling. Backoffs represent ranges or objects that a PG has asked a client to pause, and sessions maintain the client-side collection of those backoffs for request filtering and teardown.

## Important APIs, Types, And Functions
`Backoff::Backoff()` initializes a refcounted backoff with PG id, owning PG ref, session ref, sequence id, and begin/end object range. `Session::clear_backoffs()` detaches all backoffs from the session, unlinks still-active ones from their PGs, and clears session pointers for deleting backoffs. `Session::ack_backoff()` moves a sent backoff from `STATE_NEW` to `STATE_ACKED`, or removes it when the client acknowledges a deleting backoff. `Session::check_backoff()` tests an incoming message’s object against active backoffs and returns whether the request should be ignored/requeued.

## Control Flow
Session teardown swaps the backoff map out under `Session::backoff_lock`, sets `backoff_count` to zero, then iterates the saved entries while taking each `Backoff::lock`. If the backoff still has a PG, the PG is asked to remove its link before both PG and session refs are reset. If only the session remains, the state must be deleting and only the session ref is cleared. Ack handling locates by PG, begin key, and id, then either marks acked or erases deleting entries.

## State And Persistence Behavior
All state here is in memory and connection/session scoped. There is no durable persistence; correctness depends on lock ordering and consistent bidirectional links between PG backoff maps and session backoff maps. `backoff_count` mirrors whether `backoffs` is empty and is asserted after mutations.

## Dependencies And Integration Points
The file depends on `PG.h`, `Session.h`, Ceph debug logging, and PG methods such as `rm_backoff()`. It is used by OSD dispatch paths that need to suppress requests currently covered by PG-level backoff messages, and by connection reset paths that clean session state.

## Risks And Test Signals
The main risks are lock-order violations, stale PG/session references, underflow or mismatch in `backoff_count`, and races with messenger reset where `con` is cleared before backoffs are removed. Tests should cover client backoff ack/delete sequences, session reset while backoffs are new/acked/deleting, request filtering while disconnected, and debug crash behavior for ignored acked backoffs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Session.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Session.h -->
# sources/distributed-fs/ceph/src/osd/Session.h

## Purpose
`Session.h` declares the per-connection OSD `Session` object and its `Backoff` records. It centralizes client capabilities, connection state, watch state, map-wait queues, projected epoch tracking, heartbeat metadata, and per-client PG/object backoff tracking.

## Important APIs, Types, And Functions
`Backoff` is a refcounted object with states `STATE_NEW`, `STATE_ACKED`, and `STATE_DELETING`, PG/session references, an id, PG id, and `[begin,end)` object range. Its state helpers and `operator<<` support debug logging. `Session` stores `entity_name`, `OSDCap`, `ConnectionRef`, socket address, `WatchConState`, dispatch lock, `waiting_on_map`, `projected_epoch`, backoff maps, heartbeat peer/stamps, and helpers `ack_backoff()`, `have_backoff()`, `check_backoff()`, `add_backoff()`, `rm_backoff()`, and `clear_backoffs()`.

## Control Flow
Backoff lookup uses the PG id map and `lower_bound()` on range starts to find either an exact-object backoff or the preceding range that still covers the object. Request dispatch can call `check_backoff()` to suppress operations covered by active backoff state. PG code adds/removes backoffs, while session reset calls `clear_backoffs()` to sever session ownership. The comment block documents required lock ordering: `Backoff::lock`, then `PG::backoff_lock`, then `Session::backoff_lock`.

## State And Persistence Behavior
Session state is volatile and tied to messenger connection/session lifetime. Backoff ids are generated from `backoff_seq`. `backoff_count` is an atomic fast path for avoiding map locking when no backoffs exist. Watch state is held through `WatchConState` and reset with the session.

## Dependencies And Integration Points
The header integrates `OSDCap`, `OpRequest`, `Watch`, `OSDMap`, `PeeringState`, intrusive PG refs, messenger connections, and heartbeat stamps. PG code is a close collaborator for creating and releasing backoffs, while watch code uses `Session::wstate` to track connection-owned watches.

## Risks And Test Signals
Important risks are map/range lookup edge cases, lock ordering, inconsistent bidirectional ownership, and assumptions around `backoff_count` versus `backoffs.empty()`. Tests should include overlapping ranges, single-object backoffs, disconnect while requests are queued, backoff ack deletion, and session/watch reset interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapReaderI.h -->
# sources/distributed-fs/ceph/src/osd/SnapMapReaderI.h

## Purpose
`SnapMapReaderI.h` defines the scrub-facing read interface for snap-map data. It lets scrub code ask for the set of snaps associated with an object without depending on the full `SnapMapper` implementation or object-store transaction machinery.

## Important APIs, Types, And Functions
`Scrub::SnapMapReaderI` declares two pure virtual methods: `get_snaps()` and `get_snaps_check_consistency()`. Both return `tl::expected<std::set<snapid_t>, result_t>`. `result_t` distinguishes `success`, `backend_error`, `not_found`, and `inconsistent`, with `backend_error` carrying the raw errno. `snap_mapper_op_t` identifies fix operations as `add`, `update`, or `overwrite`. `snap_mapper_fix_t` packages a requested mapper repair with target object, desired snaps, and wrong snaps for logging.

## Control Flow
Scrub backends call `get_snaps()` when they only need the object-to-snaps entry and `get_snaps_check_consistency()` when they need to verify that object entries and snap mapping entries agree. If inconsistency is discovered, scrub can return or construct `snap_mapper_fix_t` records for the PG scrubber to apply through the real mapper and object-store transactions.

## State And Persistence Behavior
This header owns no state and performs no IO itself. It defines the error vocabulary for persistent snap mapper reads and repairs. The actual durable data lives in mapper omap keys managed by `SnapMapper`.

## Dependencies And Integration Points
Dependencies are intentionally small: scrub types, `tl::expected`, `hobject_t`, and `snapid_t` from Ceph headers. `SnapMapper` implements this interface, and scrub components consume it to decouple verification logic from PG internals.

## Risks And Test Signals
Risk is mostly semantic: callers must handle `inconsistent` differently from missing data or backend IO errors, and repair code must preserve enough wrong-snaps detail for diagnostics. Tests should mock or exercise implementations returning all result codes, especially consistency mismatches and backend errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapReaderI.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapper.cc -->
# sources/distributed-fs/ceph/src/osd/SnapMapper.cc

## Purpose
`SnapMapper.cc` implements Ceph OSD snap clone indexing. It maintains a bidirectional omap-backed mapping from object to snap set (`OBJ_...`) and from snap/object to object (`SNA_...`) so snap trim can enumerate objects by snap and scrub can verify mapper consistency.

## Important APIs, Types, And Functions
`OSDriver` adapts `ObjectStore` or Crimson store access to `MapCacher::StoreDriver`, providing `get_keys()`, `get_next()`, and `get_next_or_current()`. `SnapMapper` implements key formatting (`get_prefix()`, `to_raw_key()`, `to_object_key()`), encoding/decoding (`object_snaps`, `Mapping`, `from_raw()`), reads (`get_snaps_common()`, legacy and `tl::expected` `get_snaps()`), consistency checking (`get_snaps_check_consistency()`), writes (`set_snaps()`, `clear_snaps()`, `add_oid()`, `update_snaps()`, `remove_oid()`), trim enumeration (`get_next_objects_to_trim()`, `get_objects_by_prefixes()`), PG-log application (`update_snap_map()`), and purged snap tracking (`record_purged_snaps()` plus lookup/key helpers).

## Control Flow
Object updates enter through `update_snap_map()` from PG log handling. Deletes remove both `OBJ_` and all corresponding `SNA_` keys. Clone/promote entries call `add_oid()`, while modify/replace entries call `update_snaps()`. `update_snaps()` removes obsolete `SNA_` keys and tolerates a missing object entry by rebuilding from scratch to avoid creating one-sided state. Snap trim calls `get_next_objects_to_trim()` repeatedly for a snap; the mapper walks hash prefixes, returns up to `max` objects, preserves prefix iterator progress, and performs a second pass when it appears empty.

## State And Persistence Behavior
Durable state is stored as omap keys. `OBJ_` keys encode `object_snaps { oid, snaps }`; `SNA_` keys encode `Mapping { snap, hoid }` and sort by pool/snap/shard/object string. Purged snap intervals are stored under `PSN_` keys, with adjacent intervals merged. `MapCacher` buffers changes into caller-provided transactions; `flush_and_reset_backend()` persists pending state on interval changes. In-memory state includes `mask_bits`, `match`, pool/shard info, generated hash prefixes, `prefix_itr`, and `last_key_checked`.

## Dependencies And Integration Points
The mapper integrates `ObjectStore`, `MapCacher`, `hobject_t`, PG log entries, scrub reader interface, OSD map snap intervals, and optional Crimson store APIs. `PrimaryLogPG` updates it while logging operations, snap trim reads it to find clones, and scrub uses the reader interface for consistency checks and repair planning.

## Risks And Test Signals
Risks include key-format compatibility, shard-prefix parsing, one-sided `OBJ_`/`SNA_` corruption, iterator state across snap changes, split/merge `mask_bits` updates, purged interval merging, and backend iteration errors. Tests should cover encode/decode compatibility, add/update/remove idempotence, trim enumeration across prefixes, scrub consistency mismatch detection, recovery of missing mapper entries, purged snap interval joins, and Crimson/non-Crimson driver behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapper.h -->
# sources/distributed-fs/ceph/src/osd/SnapMapper.h

## Purpose
`SnapMapper.h` declares the snap mapper and its object-store driver. The mapper owns the durable index that relates cloned objects to the snapshots that reference them, enabling snap trim, scrub verification, and PG-log-driven maintenance.

## Important APIs, Types, And Functions
`OSDriver` implements `MapCacher::StoreDriver<std::string, bufferlist>` and exposes `OSTransaction`, which translates cached key set/remove operations into omap operations on a fixed collection/object. `SnapMapper::object_snaps` encodes object-to-snaps records. `SnapMapper::Mapping` encodes snap-to-object records. `SnapMapper::Scrubber` scans mapping and purged-snap objects to identify stray mappings. Public `SnapMapper` APIs include constructor, `update_bits()`, `flush_and_reset_backend()`, `update_snaps()`, `add_oid()`, `get_next_objects_to_trim()`, `remove_oid()`, legacy `get_snaps()`, `update_snap_map()`, and `SnapMapReaderI` implementations.

## Control Flow
Callers create a mapper with PG hash match bits, pool, and shard. On PG split/merge, `update_bits()` regenerates prefixes. PG log application calls `update_snap_map()` to add, modify, replace, promote, or remove clone mappings. Snap trim calls `get_next_objects_to_trim()` for a specific snap until it returns `nullopt`. Scrub calls the reader methods and may use `Scrubber` support to compare mappings against purged snap intervals.

## State And Persistence Behavior
The header documents two persistent key spaces: `OBJECT_PREFIX + object` for object-to-snap sets and `MAPPING_PREFIX + pool + snap + object` for snap enumeration. Sharded EC objects include a shard prefix; replicated objects omit it. The `backend` cache is mutable so const reads can still fill cache state, while writes are flushed into caller-owned transactions. The prefix iterator is in-memory state that optimizes repeated trim scans.

## Dependencies And Integration Points
Dependencies include `MapCacher`, `ObjectStore`, `hobject_t`, `OSDMap`, `SnapMapReaderI`, Ceph encoding, and optional Crimson store types. Integration points are `PrimaryLogPG`/PG log updates, snap trimmer, scrubber, and OSD map purged snap tracking.

## Risks And Test Signals
Interface risks include stale cached writes if `flush_and_reset_backend()` is missed, incorrect prefix generation after split/merge, and legacy callers interpreting inconsistent data as `-ENOENT`. Tests should compile both Crimson and classic variants where applicable, verify key strings for replicated and EC shards, and exercise all public mutation/read methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/SnapMapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/TierAgentState.h -->
# sources/distributed-fs/ceph/src/osd/TierAgentState.h

## Purpose
`TierAgentState.h` declares the state container used by `PrimaryLogPG` cache-tiering agent work. It tracks where the agent is scanning, what recent hit-set/temperature information it has, and which flush/evict modes are active.

## Important APIs, Types, And Functions
`TierAgentState` stores `position`, `started`, `start`, `delaying`, a power-of-two temperature histogram, histogram age, archived `HitSetRef` values keyed by time, recent clean objects, flush mode, evict mode, and `evict_effort`. It defines `flush_mode_t` values `FLUSH_MODE_IDLE`, `FLUSH_MODE_LOW`, and `FLUSH_MODE_HIGH`, plus `evict_mode_t` values `EVICT_MODE_IDLE`, `EVICT_MODE_SOME`, and `EVICT_MODE_FULL`. Helper methods stringify modes, test idleness, manage hit sets, and dump state.

## Control Flow
`PrimaryLogPG` agent logic mutates this structure as it chooses agent modes, loads hit sets, estimates object temperature, flushes dirty objects, and evicts clean or cold objects. `is_idle()` reports no agent work only when not delaying and both flush and evict modes are idle. Hit-set methods add archived sets, remove the oldest, or discard all on reset.

## State And Persistence Behavior
This type is in-memory state only. Persistent tiering inputs and effects are elsewhere: hit-set objects, object dirty/clean state, and flush/evict transactions. The dump method exposes current mode, effort, scan position, and histogram for diagnostics.

## Dependencies And Integration Points
The header depends on Ceph formatter, histogram, `hobject_t`, and `HitSet`. It is included by `PrimaryLogPG.h`, where `agent_state` is a scoped pointer and the agent methods consume its fields.

## Risks And Test Signals
Risk is mostly policy drift: wrong idle semantics can stall or overrun tier-agent work, and stale hit sets can bias eviction decisions. Tests should cover mode transitions in `PrimaryLogPG`, dump output, hit-set trimming, delayed state, and cache-tiering integration under full/nearfull pool conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/TierAgentState.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Watch.cc -->
# sources/distributed-fs/ceph/src/osd/Watch.cc

## Purpose
`Watch.cc` implements OSD object watch and notify lifecycles. Watches bind clients to object contexts so clients can receive object notifications; notifies aggregate watcher acknowledgements, timeouts, and completion replies back to the notifier.

## Important APIs, Types, And Functions
`Notify` manages one notify operation: client connection/gid, payload, timeout, cookie, notify id, version, watcher set, reply collection, timer callback, and completion/discard flags. Important methods are `makeNotifyRef()`, `init()`, `start_watcher()`, `complete_watcher()`, `complete_watcher_remove()`, `discard()`, `register_cb()`, `unregister_cb()`, `do_timeout()`, and `maybe_complete_notify()`. `Watch` manages a watcher connection and object context with methods `connect()`, `disconnect()`, `got_ping()`, `remove()`, `discard()`, `start_notify()`, `cancel_notify()`, `notify_ack()`, and timeout callback creation. `WatchConState` tracks watches attached to a session.

## Control Flow
A notify is created, watchers are registered before `init()`, and `init()` arms a timeout then completes immediately if there are no watchers. Each watch stores the notify, sends `MWatchNotify` if connected, and later passes ack data to `Notify::complete_watcher()`. `Notify::maybe_complete_notify()` sends `CEPH_WATCH_EVENT_NOTIFY_COMPLETE` when all watchers respond or timeout fires, encoding replies and missed watcher ids. Watch timeout callbacks drop `watch_lock`, take the PG lock, and invoke `PrimaryLogPG::handle_watch_timeout()` if still valid. Session reset calls `WatchConState::reset()`, which disconnects affected watches under PG lock.

## State And Persistence Behavior
Watch and notify state is in-memory, associated with object contexts, sessions, messenger connections, and OSD watch timers. Persistent watch metadata is managed through object operations elsewhere; this file maintains runtime liveness, timeout, and notification state. `discard_state()` clears object context refs, session watch links, callbacks, and connection refs.

## Dependencies And Integration Points
The implementation depends on `PrimaryLogPG`, `OSDService`, `Session`, messenger `Connection`, `MWatchNotify`, OSD watch timer/lock, and PG locking. It integrates with `PrimaryLogPG` for timeout handling and with `Session::wstate` for connection reset cleanup.

## Risks And Test Signals
High-risk areas are callback lifetime, lock transitions between `watch_lock`, notify lock, and PG lock, duplicate disconnect/remove paths, ping timeout semantics, and notify completion after discard. Tests should cover connected and disconnected watches, pinging and non-pinging clients, notify ack aggregation, notify timeout with missed watchers, session reset, object removal with disconnect events, and peering discard.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Watch.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Watch.h -->
# sources/distributed-fs/ceph/src/osd/Watch.h

## Purpose
`Watch.h` declares runtime structures for RADOS object watch/notify behavior in the OSD. It separates `Notify` aggregation, individual `Watch` connection/object state, and `WatchConState` session-level watch tracking.

## Important APIs, Types, And Functions
`WatcherState` defines pending/notified markers used by watch metadata paths. `Notify` stores the notifying client, payload, timeout, cookie, notify id, object version, watcher refs, reply buffers, and timer callback. `Watch` stores weak self-ref, connection, callback, OSD service, PG ref, object context, in-progress notifies, timeout/cookie/address/entity fields, ping state, and discarded flag. Public APIs create refs, connect/disconnect, remove/discard, start/cancel notify, process notify ack, and access object/PG/cookie/entity data. `WatchConState` adds/removes watches and resets all watches for a connection.

## Control Flow
`Notify` is initialized after all watchers are added; it then waits for watcher completion or timeout. `Watch` connects to a session and registers with `Session::wstate`, resends in-progress notifies on reconnect, and uses timeout callbacks for missed pings or disconnected older clients. Removing or discarding a watch drains in-progress notifies and clears runtime state.

## State And Persistence Behavior
The declarations define volatile runtime state. Watcher persistence in object metadata is handled by PG object operations and object contexts, not by this header. `Notify` keeps reply aggregation until completion; `Watch` keeps notify membership by notify id until ack, cancel, remove, or discard.

## Dependencies And Integration Points
The file depends on messenger connections, `Context`, `PrimaryLogPG`, `ObjectContext`, `OSDService`, and `MWatchNotify` forward declarations. It is consumed by `PrimaryLogPG` for watch operation effects and by `Session` for connection reset tracking.

## Risks And Test Signals
Risks include dangling weak/self references, missing callback cancellation, inconsistent connection/session state, and accidental use without PG lock where required. Tests should target object watch connect/unwatch, notify lifecycle, delayed timeout generation during scrub/recovery, reconnect resend behavior, and session reset interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/Watch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/error_code.cc -->
# sources/distributed-fs/ceph/src/osd/error_code.cc

## Purpose
`error_code.cc` implements the Boost/Ceph error category for OSD-specific error codes. It gives custom OSD conditions human-readable messages, default conditions, POSIX-style equivalence, and conversion from negative Ceph return codes.

## Important APIs, Types, And Functions
The private `osd_error_category` derives from `ceph::converting_category`. It overrides `name()`, two `message()` overloads, `default_error_condition()`, `equivalent()`, and `from_code()`. Recognized `osd_errc` values are `old_snapc`, `blocklisted`, and `cmpext_mismatch`; unknown codes fall back to `cpp_strerror()`. `osd_category()` returns a function-local static category instance.

## Control Flow
When Boost asks for a message, the category maps known enum values to OSD-specific strings and otherwise formats the errno. `default_error_condition()` keeps known OSD values in the OSD category and maps everything else to `generic_category()`. `equivalent()` maps `old_snapc` to `invalid_argument`, `blocklisted` to `operation_not_permitted`, and `cmpext_mismatch` to `operation_canceled`; other values compare through the default condition. `from_code()` converts a positive category value to the negative return convention.

## State And Persistence Behavior
There is no persistence and only one static category object. Behavior must remain stable because error categories are used across APIs and tests that compare categories/conditions.

## Dependencies And Integration Points
The file depends on `common/error_code.h`, `common/errno.h`, and local `error_code.h`. It integrates OSD-specific errors with Boost.System and Ceph’s negative errno conventions.

## Risks And Test Signals
Risks include changing numeric equivalence, returning unstable message buffers, or misclassifying an OSD-specific error as generic. Tests should check `make_error_code()`, category name, messages for known/unknown values, default conditions, equivalence to Boost errc values, and negative conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/error_code.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/error_code.h -->
# sources/distributed-fs/ceph/src/osd/error_code.h

## Purpose
`error_code.h` declares OSD-specific error codes and their Boost.System integration. It lets OSD code return typed errors while remaining compatible with Ceph’s mostly POSIX errno-based APIs.

## Important APIs, Types, And Functions
The header declares `osd_category()`, enum class `osd_errc`, Boost.System enum traits, and conversion helpers `make_error_code()` and `make_error_condition()`. `osd_errc` currently includes `old_snapc = 85`, `blocklisted = 108`, and `cmpext_mismatch = MAX_ERRNO`.

## Control Flow
Implicit conversion to `boost::system::error_code` is enabled by specializing `boost::system::is_error_code_enum`. `is_error_condition_enum` is false, so conditions are explicit through `make_error_condition()`. The inline conversion helpers attach the integer enum value to `osd_category()`.

## State And Persistence Behavior
There is no mutable state. The important persistence-like contract is numeric stability: these values may be visible in wire/API behavior and must remain compatible with existing error handling.

## Dependencies And Integration Points
The header depends on Boost.System, `include/rados.h`, and `include/err.h`. It is implemented by `error_code.cc` and consumed anywhere OSD-specific errors need typed Boost error codes.

## Risks And Test Signals
Risks include numeric collisions with POSIX/Ceph errno values, accidental condition conversion behavior, and changing values that external callers rely on. Tests should compile implicit `error_code` conversion, explicit condition conversion, and category/message/equivalence behavior through the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/osd/error_code.h -->
