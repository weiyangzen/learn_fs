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
