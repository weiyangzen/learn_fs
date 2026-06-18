# Research: subset-b-008823

Grouped CDC research report for the subset B work item. Each section is bounded for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/observer.rs -->
# sources/storage-engines/tikv/components/cdc/src/observer.rs

## Purpose
`observer.rs` implements `CdcObserver`, the raftstore coprocessor bridge that turns apply, role, and region-change callbacks into CDC endpoint tasks. It is the handoff point between raftstore event ordering and the CDC endpoint scheduler, and it also supplies the old-value callback used later while handling committed MVCC changes.

## Important APIs, Types, and Functions
- `CdcObserver::new` wires a FIFO `Scheduler<Task>` and shared `MemoryQuota`.
- `register_to` installs command, role, and region-change observers into `CoprocessorHost` with priorities chosen so CDC command observation precedes resolved-ts observation.
- `subscribe_region`, `unsubscribe_region`, and `is_subscribed` maintain `region_id -> ObserveId` under `RwLock`; unsubscribe checks the `ObserveId` to avoid ABA removal of a newer subscription.
- `CmdObserver::on_flush_applied_cmd_batch` filters `ObserveLevel::All` batches, creates a defensive engine snapshot, allocates batch memory quota, and schedules `Task::MultiBatch`.
- `RoleObserver::on_role_change` and `RegionChangeObserver::on_region_changed` schedule `Task::Deregister` with request errors when leadership is lost, a region is destroyed, split, or committed-merged.

## Control Flow
Apply callbacks assert a non-empty input batch, pass through failpoint `before_cdc_flush_apply`, then drop work unless all requested observation reaches `ObserveLevel::All`. A fake region wrapper is used to create a `RegionSnapshot` over the current engine snapshot so old values cannot disappear due to GC before CDC handles the batch. Role and region-change callbacks first check `observe_regions`; only subscribed regions generate deregistration tasks.

## State and Persistence Behavior
The observer holds only in-memory subscription state and does not persist CDC registrations. The engine snapshot captured for old-value lookup is a temporary consistency guard. Memory quota is charged with `alloc_force` before scheduling multi-batch work; endpoint-side processing is responsible for eventual release.

## Dependencies and Integration Points
The file depends on raftstore coprocessor traits, raft role metadata, TiKV storage `Statistics`, `MemoryQuota`, the CDC `endpoint::Task` protocol, and `old_value::get_old_value`. It is registered by CDC service setup and feeds endpoint delegate logic.

## Risks and Edge Cases
The shared `RwLock<HashMap<...>>` is called out as a potential bottleneck. Scheduler failure only logs warnings/errors after quota allocation, so downstream release behavior matters. Correct FIFO scheduler behavior is required by the file-level comment because apply events are strongly ordered.

## Test Signals
Unit tests cover command scheduling, memory quota charging, ignored events after observation handles stop, role-change NotLeader errors with leader and transferee peers, ABA-safe unsubscribe, no events for unsubscribed regions, and dropping txn extra when quota is exceeded.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/observer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/old_value.rs -->
# sources/storage-engines/tikv/components/cdc/src/old_value.rs

## Purpose
`old_value.rs` provides CDC old-value retrieval for MVCC changes. It combines an LRU cache populated from observed transaction extras with direct MVCC scans over the write/default column families when the cache misses.

## Important APIs, Types, and Functions
- `OldValueCallback` is the callback signature passed from observer batches into endpoint handling.
- `OldValueCacheSizePolicy` accounts cache capacity using encoded key length, `OldValue::size`, and mutation-type metadata.
- `OldValueCache` wraps `LruCache<Key, (OldValue, Option<MutationType>)>` and tracks access, miss, miss-none, and update counters; `resize` and `flush_metrics` synchronize Prometheus gauges/counters.
- `get_old_value` is the main lookup path: consume cache entry if present, otherwise append `query_ts`, build a write cursor, and call `near_seek_old_value`.
- `near_seek_old_value` scans MVCC write records for the latest visible value at or before the requested timestamp and optionally loads large values from the default CF via snapshot get or reusable cursor.
- `OldValueCursors` bundles reusable write/default cursors for scan-heavy paths.

## Control Flow
Cache hits are removed from the LRU and interpreted by mutation type. Inserts guarantee no previous value; puts/deletes may carry no value, inline value bytes, or a `ValueTimeStamp` requiring a default-CF read. Cache misses truncate the timestamp from the encoded key, append the query timestamp, and seek write CF. `near_seek_old_value` skips rollback/lock writes, honors GC fence visibility for puts, returns `None` for deletes or invisible puts, and loads long values through `near_load_data_by_write` or `get_cf_opt`.

## State and Persistence Behavior
The cache is in-memory and bounded by byte size. Metrics expose configured quota, current bytes, length, access/miss counts, and miss-none counts. Persistent state remains in MVCC RocksDB column families; this module only reads snapshots/cursors and never mutates engine data.

## Dependencies and Integration Points
The module depends on TiKV storage cursors, engine traits (`CF_WRITE`, `CF_DEFAULT`, `ReadOptions`), txn-types MVCC key/write encodings, TiKV LRU utilities, and CDC metrics. It is invoked through observer-created callbacks during endpoint event conversion.

## Risks and Edge Cases
Timestamp encoding assumptions are pervasive (`split_on_ts_for`, `decode_ts_from`, `truncate_ts` unwraps). Cache entries for `Unspecified` and `SeekWrite` are unreachable by contract. Correct GC fence handling is critical or CDC could emit stale old values. Cursor range bounds intentionally avoid accidental region-bound misuse.

## Test Signals
Tests validate cache resizing and eviction, old-value behavior across prewrite/commit/delete/rollback/pessimistic locks, GC fence visibility, cursor reuse statistics, prefix seek block-read reduction, and capacity enforcement when oversized values are inserted.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/old_value.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/service.rs -->
# sources/storage-engines/tikv/components/cdc/src/service.rs

## Purpose
`service.rs` is the gRPC front end for the CDC `ChangeData` service. It accepts client event-feed streams, creates CDC connection state, parses version/features, converts register/deregister requests into endpoint tasks, and forwards endpoint events back to the gRPC sink.

## Important APIs, Types, and Functions
- `validate_kv_api` permits TiDB API and RawKV only when TiKV runs API V2.
- `RequestId` identifies logical subscriptions within a connection.
- `FeatureGate` models version-default and explicitly requested features: batch resolved-ts, cluster-id validation, and stream multiplexing.
- `Conn` tracks `ConnId`, sink, peer, negotiated version/features, and `(request_id, region_id) -> DownstreamValue`.
- `EventFeedHeaders` parses `features` request metadata for `event_feed_v2`.
- `Service::handle_event_feed` is the central stream lifecycle function.
- `handle_register` creates `ObservedRange` and `Downstream`; `handle_deregister` maps region/request scope to endpoint deregistration variants.

## Control Flow
`event_feed` and `event_feed_v2` call `handle_event_feed`; v2 first validates feature headers and fails the RPC with `UNIMPLEMENTED` for unknown features. A fresh `ConnId`, bounded CDC channel, and `Conn` are created, then `Task::OpenConn` is scheduled. The receive future reads the first request to parse TiCDC version, schedules `SetConnVersion`, handles that request, and then handles the rest. A watchdog is spawned. Separate receive and send tasks race normal stream completion against watchdog abort signals; receive-side closure deregisters the connection, while send-side failure fails the gRPC sink.

## State and Persistence Behavior
Connection and downstream maps are in-memory endpoint state. `ConnId` is process-local. No persistent state is written; registration durability is provided by clients re-registering streams. The service shares the CDC `MemoryQuota` with channel/backpressure and watchdog decisions.

## Dependencies and Integration Points
The file integrates grpcio generated `ChangeData`, CDC channel `Sink`, endpoint `Task`, delegate `Downstream`, watchdog, memory quota, and kvproto change-data request/response messages. It is the external API boundary for TiCDC and RawKV CDC clients.

## Risks and Edge Cases
`Conn::features` unwraps, so the endpoint must set version before feature checks. Duplicate `(request_id, region_id)` subscriptions return the previous downstream instead of replacing it. Header parsing rejects unknown explicit features. Send and receive tasks both can deregister on abort/failure, so endpoint deregistration must be idempotent.

## Test Signals
Unit tests cover gRPC flow control and watchdog idle timeout behavior. Failpoint integration tests elsewhere exercise stream multiplexing, register/deregister races, RawKV resolved-ts behavior, and connection failure paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/txn_source.rs -->
# sources/storage-engines/tikv/components/cdc/src/txn_source.rs

## Purpose
`txn_source.rs` defines bit allocation helpers for `kv.TxnSource`, allowing CDC to detect writes originating from TiCDC, lossy DDL reorg backfill, and Lightning physical import mode.

## Important APIs, Types, and Functions
- `TxnSource(u64)` wraps the source bitmap.
- `is_cdc_write_source_set` tests the low 8 bits.
- `is_lossy_ddl_reorg_source_set` tests bits shifted by `LOSSY_DDL_REORG_SOURCE_SHIFT`.
- `is_lightning_physical_import` checks bit 16.
- Test-only setters/getters create bitmap cases without exposing mutation APIs in production.
- `From<TxnSource> for u64` exports the raw value.

## Control Flow
There is no runtime control loop. Callers pass a raw transaction source into static predicates, and each predicate masks or shifts the bitmap to determine whether a class of source metadata is present.

## State and Persistence Behavior
The bitmap is carried in transaction metadata outside this file. The wrapper itself is copyable and has no heap or persistent state. Bit layout is part of an external contract with TiDB/TiCDC/Lightning writers.

## Dependencies and Integration Points
This module is intentionally dependency-light. It integrates with CDC filtering logic that needs to skip or classify writes by source, and with transaction metadata producers that set `kv.TxnSource`.

## Risks and Edge Cases
Bit allocation is compatibility-sensitive. `is_lossy_ddl_reorg_source_set` checks all bits above the lossy shift rather than masking only the lossy 8-bit field, so Lightning/import bits also make it return true; this appears deliberate from current code but should be validated when adding upper-bit meanings.

## Test Signals
Unit tests cover setting/getting CDC bits, lossy DDL reorg bits, and Lightning import detection, including default false cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/txn_source.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/types.rs -->
# sources/storage-engines/tikv/components/cdc/src/types.rs

## Purpose
`types.rs` currently defines the CDC connection identifier type used across service, watchdog, channel, and endpoint state.

## Important APIs, Types, and Functions
- `CONNECTION_ID_ALLOC: AtomicUsize` is the process-local monotonic allocator.
- `ConnId(usize)` is a copyable, hashable, debug-printable connection identifier.
- `ConnId::new` increments the allocator with `Ordering::SeqCst`.
- `Default` delegates to `new` so default construction still creates a unique ID.

## Control Flow
The only control flow is atomic fetch-add during connection creation. `Service::handle_event_feed` calls `ConnId::new` for every incoming event-feed stream, then passes that ID into channels, endpoint tasks, and watchdog logging.

## State and Persistence Behavior
The allocator is in-memory and resets on process restart. IDs are unique only within a single process lifetime and are not persisted or globally coordinated.

## Dependencies and Integration Points
The type is used by `service.rs`, `watchdog.rs`, endpoint task variants, downstream tracking, and CDC channel memory accounting/logging.

## Risks and Edge Cases
`usize` wraparound is theoretically possible in a very long-lived process, though practically remote. `SeqCst` is conservative and simple but stronger than strictly required for uniqueness.

## Test Signals
There are no local tests in this file. Coverage is indirect through service/watchdog tests that create and compare `ConnId`s, especially deregistration-on-watchdog-abort checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/types.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/watchdog.rs -->
# sources/storage-engines/tikv/components/cdc/src/watchdog.rs

## Purpose
`watchdog.rs` monitors a CDC EventFeed connection for stalled flushing under high memory pressure and explicitly aborts both receive and send tasks when the connection remains idle beyond configured thresholds.

## Important APIs, Types, and Functions
- `Config` holds check interval, idle deregister threshold, and memory-quota abort ratio; failpoints can override thresholds.
- `FlushActivity` shares the last successful flush `Instant` through `Arc<AtomicCell<Instant>>`.
- `WatchdogHandle` returns activity plus receive/send abort receivers and a `ForwardExitGuard`.
- `wait_for_abort` resolves only on explicit abort; dropped senders intentionally park forever.
- `Watchdog::spawn` and `spawn_with_activity` create abort channels, forward-exit signal, and spawn `run` on the worker pool.
- `check_and_maybe_abort` compares idle duration and memory quota usage, then aborts idempotently.

## Control Flow
The watchdog runs a timer interval via `GLOBAL_TIMER_HANDLE`. Each tick logs when the connection has been idle longer than one check interval, and aborts only if idle time exceeds `idle_deregister_threshold` and `MemoryQuota::used_ratio` is at or above the configured threshold. Dropping `ForwardExitGuard` wakes the watchdog and stops polling for normal send-task exit.

## State and Persistence Behavior
All state is per-connection and in-memory: last flush timestamp, abort senders, forward-exit receiver, peer string, connection id, and memory-quota reference. No persistent state is written.

## Dependencies and Integration Points
`service.rs` holds the returned `ForwardExitGuard` in the send task, passes `FlushActivity` into channel forwarding, and races send/receive futures against `wait_for_abort`. The watchdog uses TiKV worker pools, global timers, failpoints, and `MemoryQuota`.

## Risks and Edge Cases
Abort requires both idle duration and memory pressure, preventing cancellation of quiet but healthy streams. `wait_for_abort` intentionally hangs on sender drop, so misuse could leak a pending future. `memory_quota_abort_threshold` currently uses the same failpoint name as `idle_deregister_threshold`, which may be surprising for test control.

## Test Signals
Unit tests verify watchdog cancellation of both send and receive under quota pressure, idempotent abort sender behavior, and `wait_for_abort` not completing when sender side is simply dropped.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/watchdog.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/mod.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/mod.rs

## Purpose
This module is the failpoint test harness root for CDC. It enables the custom failpoint test runner, declares the individual failpoint test modules, and re-exports the common CDC test suite helpers.

## Important APIs, Types, and Functions
- `#![feature(custom_test_frameworks)]` and `#![test_runner(test_util::run_failpoint_tests)]` configure failpoint-aware test execution.
- Modules: `test_endpoint`, `test_memory_quota`, `test_observe`, `test_register`, and `test_resolve`.
- `#[path = "../mod.rs"] mod testsuite; pub use testsuite::*;` exposes shared cluster/client helpers.

## Control Flow
The Rust test framework discovers tests in the declared modules and runs them through `run_failpoint_tests`, ensuring failpoint setup/cleanup behavior is suitable for injected failure cases.

## State and Persistence Behavior
This file stores no runtime state. It determines compilation/test topology only.

## Dependencies and Integration Points
It ties the CDC failpoint suites to the broader test utility framework and the integration test suite definitions in the parent `tests` module.

## Risks and Edge Cases
Because all failpoint modules share one harness root, leaked failpoints in one test can affect later tests. Individual tests mostly remove failpoints explicitly, but ignored/panic paths remain a standard failpoint-suite risk.

## Test Signals
The file itself has no tests; its signal is successful compilation/discovery and execution of the five declared failpoint suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_endpoint.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_endpoint.rs

## Purpose
`test_endpoint.rs` exercises CDC endpoint behavior under failpoint-controlled races: incremental scan cancellation/failure, ordering before snapshot initialization, old-value-cache updates, RawKV resolved-ts bounds, stream multiplexing readiness, pending-region errors, and unresolved-region accounting.

## Important APIs, Types, and Functions
The tests use `TestSuite`/`TestSuiteBuilder`, `new_event_feed`/`new_event_feed_v2`, raftstore split/merge helpers, PD TSO, raw KV clients, and `Task::Validate` probes. Failpoints include `cdc_incremental_scan_start`, `cdc_scan_batch_fail`, `cdc_before_handle_multi_batch`, `cdc_sleep_before_drain_change_event`, `before_post_incremental_scan`, `cdc_before_initialize`, `before_schedule_incremental_scan`, and `before_schedule_resolver_ready`.

## Control Flow
Most tests open one or more event feeds, pause a specific endpoint stage, mutate the cluster, then unpause and assert emitted CDC events. The double-scan tests verify one of two concurrent scans handles deregistration or scan I/O failure without corrupting the surviving downstream. Ordering tests pause multi-batch handling and sink draining so they can assert `Initialized` arrives after prior delta entries. Multiplexing subscribes the same region twice with different request IDs and verifies resolved-ts routing waits for each request to become ready.

## State and Persistence Behavior
The tests manipulate real in-memory raftstore clusters and MVCC state, but do not persist artifacts. They inspect endpoint state using validation tasks for old-value cache update counts and unresolved-region counts.

## Dependencies and Integration Points
Coverage crosses service streams, endpoint delegates, resolver readiness, incremental scanner, CDC sink/channel flow, RawKV API V2 causal timestamp provider, and raftstore split/merge notifications.

## Risks and Edge Cases
The suite targets races that can duplicate events, emit resolved-ts before initialization, lose region errors while pending, or leave unresolved-region counts stuck. Timing uses sleeps around failpoints, so reliability depends on failpoints being at stable boundaries.

## Test Signals
Assertions check region-not-found/epoch-not-match/congested errors, initialized event placement, resolved-ts request IDs and timestamp bounds, old-value cache update suppression when no captures remain, and unresolved-region count transitioning from all pending to zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_memory_quota.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_memory_quota.rs

## Purpose
`test_memory_quota.rs` validates CDC behavior when resolver lock tracking, pending lock handling, or initial lock scanning exceed the configured CDC memory quota.

## Important APIs, Types, and Functions
The tests build a single-node cluster with a small `memory_quota`, disable event-size quota effects via `cdc_event_size`, create large-key prewrites, and use `Task::Validate(Validate::Region)` to verify delegate cleanup. Failpoints include `cdc_finish_scan_locks_memory_quota_exceed` and `cdc_incremental_scan_start`.

## Control Flow
Each test opens an event feed, arranges lock memory usage to fit or exceed the quota, receives events, and expects a congested CDC error once quota is exceeded. After the error, a validation task confirms the delegate for the region has been removed.

## State and Persistence Behavior
The state under test is endpoint memory accounting for locks and delegates, not persistent storage. MVCC locks are created through normal prewrite calls; quota overflow results in deregistration/cleanup rather than persisted CDC state changes.

## Dependencies and Integration Points
The suite connects CDC endpoint memory quota enforcement with resolver lock tracking, pending downstream initialization, initial scan lock loading, grpc event feeds, and raftstore test-cluster writes.

## Risks and Edge Cases
Large keys are used to make memory pressure deterministic. The tests intentionally make `CdcEvent` size zero so failures isolate lock/resolver memory paths. A regression could either miss the congested error or keep a delegate alive after an unrecoverable quota failure.

## Test Signals
Four tests cover resolver tracking overflow after normal initialization, overflow when finishing scan locks, overflow while locks are pushed to pending during paused scans, and overflow while scanning preexisting locks. All expect `Error.has_congested()` and delegate absence.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_memory_quota.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_observe.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_observe.rs

## Purpose
`test_observe.rs` focuses on raftstore observation ordering and duplicate/stale command handling around CDC subscriptions, especially when apply flushing is paused while connections churn.

## Important APIs, Types, and Functions
The primary active test is `test_observe_duplicate_cmd`, parameterized over API V1/V2. It uses event feeds, PD TSO, prewrite/commit operations, and failpoint `before_cdc_flush_apply`. A second `test_delayed_change_cmd` is currently not a Rust test but documents a delayed change-command scenario involving read-index/heartbeat filters.

## Control Flow
The active test subscribes a region, receives initialization, prewrites a key, then pauses CDC apply flushing before committing. While the commit is blocked, it opens two new connections and drops the old ones. After unpausing, the surviving connection must receive exactly the committed entry followed by initialized, and then continue receiving advancing resolved-ts events.

## State and Persistence Behavior
The test uses real raftstore/MVCC state for the prewrite and commit. CDC state under observation includes observer command queues, downstream registration changes, and resolver progress after connection churn.

## Dependencies and Integration Points
This suite exercises `CdcObserver` apply flushing, endpoint multi-batch handling, downstream initialization, event-feed transport, PD timestamp allocation, and API-version key formatting.

## Risks and Edge Cases
The target risk is duplicated or misordered command delivery when an apply batch is delayed while downstreams are removed and re-added. The expected event order also guards against emitting `Initialized` before older observed changes.

## Test Signals
Assertions verify initialization, prewrite delivery, combined committed+initialized output on the final connection, absence of CDC errors, and multiple nonzero resolved-ts advancements after the churn.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_observe.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_register.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_register.rs

## Purpose
`test_register.rs` validates CDC registration and deregistration behavior across pending batches, role changes, stale region epochs, splits, merges, and pending downstream removal.

## Important APIs, Types, and Functions
Tests use `TestSuite`, `new_event_feed`, `ObserverContext`, `RoleObserver::on_role_change`, `RegionEpoch`, and raftstore merge/split helpers. Failpoints include `cdc_incremental_scan_start`, `before_handle_catch_up_logs_for_merge`, `destroy_peer`, `before_schedule_resolver_ready`, and `raft_on_capture_change`.

## Control Flow
The suite pauses incremental scans or resolver readiness, mutates region topology, and asserts registration outcomes. `test_failed_pending_batch` confirms an epoch-not-match pending batch does not prevent re-subscription. `test_region_ready_after_deregister` simulates role loss while initialization is paused and verifies no panic. `test_connections_register` covers stale epoch rejection, connection replacement, and split error delivery. `test_merge` walks source/target subscriptions through prepare/commit merge and retry. The pending-downstream test checks deregistration during resolver build.

## State and Persistence Behavior
The tests exercise in-memory endpoint delegate/downstream state over real raftstore topology changes. Region metadata and MVCC writes live in the test cluster; CDC registrations are expected to be removed or replaced cleanly.

## Dependencies and Integration Points
Coverage spans service event feeds, observer role-change callbacks, endpoint registration validation, incremental scanner, resolver-ready scheduling, raftstore split/merge paths, and error conversion to CDC protocol errors.

## Risks and Edge Cases
Races between registration, initialization, and topology changes can leave stale delegates or send wrong errors. Merge handling is especially sensitive because source regions may be destroyed while target regions need epoch-not-match signaling.

## Test Signals
Expected signals include `Initialized`, `epoch_not_match`, and `region_not_found` events, plus absence of panics when a region becomes ready after deregistration. Some function naming appears typoed (`est_connections_registertest_deregister_pending_downstream`) but still carries the `#[test]` attribute.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_register.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_resolve.rs -->
# sources/storage-engines/tikv/components/cdc/tests/failpoints/test_resolve.rs

## Purpose
`test_resolve.rs` validates resolved-ts behavior when resolvers become stale, regions merge, callbacks are dropped, or raft configuration changes make progress temporarily impossible.

## Important APIs, Types, and Functions
The suite uses `TestSuite`, `TestSuiteBuilder`, event feeds, PD TSO, prewrite/commit, merge/confchange helpers, and `ReadableDuration` CDC config tuning. Failpoints include `before_schedule_resolver_ready`, `cdc_incremental_scan_start`, `cdc_before_handle_multi_batch`, `cdc_before_handle_deregister`, and `change_peer_after_update_region`.

## Control Flow
`test_stale_resolver` pauses resolver readiness, opens replacement streams, commits while another scan is paused, and then verifies both streams receive the correct prewrite/commit/initialized combinations. `test_region_error` blocks multi-batch and deregister handling while merging regions, then confirms the target region still receives monotonically increasing resolved-ts. `test_joint_confchange` repeatedly receives resolved-ts across node stop/start and joint confchange, then pauses region update during another confchange and expects resolved-ts progress to stop within the timeout.

## State and Persistence Behavior
The state under test is resolver lifecycle and resolved-ts advancement, plus raftstore region/peer metadata in the test cluster. No research or product state is persisted by the tests.

## Dependencies and Integration Points
The tests connect endpoint resolver scheduling, CDC event emission, raftstore merge/confchange, PD client operations, and hibernate-region compatibility settings.

## Risks and Edge Cases
Stale resolvers can emit incorrect events after connection replacement. Region errors can drop callbacks needed for resolved-ts advancement. Joint consensus changes can make resolved-ts unsafe to advance if region metadata is blocked or peers are unavailable.

## Test Signals
Assertions require commit/prewrite/initialized event shapes without CDC errors, strictly increasing or nondecreasing resolved-ts in healthy phases, and no resolved-ts progress while a critical region update failpoint is paused.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/failpoints/test_resolve.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/mod.rs -->
# sources/storage-engines/tikv/components/cdc/tests/integrations/mod.rs

## Purpose
This module is the integration test harness root for non-failpoint CDC integration tests. It declares the integration suites and re-exports common test-suite helpers.

## Important APIs, Types, and Functions
- Modules: `test_cdc` and `test_flow_control`.
- `#[path = "../mod.rs"] mod testsuite; pub use testsuite::*;` shares cluster/event-feed helper APIs with the integration tests.

## Control Flow
Rust test discovery loads the declared integration modules through this root. Individual test functions live in the child modules; this file only establishes module topology.

## State and Persistence Behavior
No runtime or persistent state is managed here. It affects compilation and test organization only.

## Dependencies and Integration Points
The file links integration tests with the shared CDC test suite infrastructure used by failpoint tests, allowing common cluster builders, clients, and event-feed utilities.

## Risks and Edge Cases
The main risk is organizational: missing module declarations would silently omit integration coverage from this harness. Shared helper re-export means changes in parent `tests/mod.rs` propagate to both failpoint and integration suites.

## Test Signals
The signal from this file is successful compilation and discovery of `test_cdc` and `test_flow_control`; behavioral assertions are in those modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/tests/integrations/mod.rs -->
