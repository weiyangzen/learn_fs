# Research: subset-b-008822 TiKV CDC Core Files

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/delegate.rs -->
# sources/storage-engines/tikv/components/cdc/src/delegate.rs

## Purpose

`delegate.rs` implements the per-region CDC delegate that turns observed raftstore apply commands and incremental-scan entries into `cdcpb` change events for one or more downstream subscriptions. It is also the region-local resolved-ts gate: it tracks in-flight locks, keeps per-downstream lock heaps for observed subranges, sends region errors, stops observation, and toggles transaction-layer old-value capture through the shared `TxnExtraOp`.

The file is the CDC boundary between raftstore observation (`CmdBatch`, `ObserveHandle`), client delivery (`Sink`, `CdcEvent`, `Conn`), transaction decoding (`txn_types::{Lock, WriteRef, TimeStamp}`), and resolved-ts advancement (`endpoint::Advance`).

## Important APIs, Types, And Functions

- `DownstreamId` is an atomically allocated unique identifier used to avoid ABA mistakes when deregistering a subscription.
- `DownstreamState` models subscription progress: `Uninitialized`, `Initializing`, `Normal`, and `Stopped`. `ready_for_change_events` allows scan and delta entries during initialization, while `ready_for_advancing_ts` only allows resolved-ts after the incremental scan has completed.
- `on_init_downstream` and `post_init_downstream` perform atomic state transitions used by `Endpoint::run(Task::InitDownstream)` and `Initializer` completion.
- `Downstream` holds request identity, connection identity, requested KV API (`TiDb`, `RawKv`, etc.), loop filtering, observed range, sink, state, scan cancellation flag, and per-downstream resolved-ts state (`lock_heap`, `advanced_to`). `sink_event` attaches the request ID and handles sink failures; `sink_error_event` marks scan truncation and force-sends protocol errors.
- `PendingLock`, `LockTracker`, and `MiniLock` are the resolver state. `LockTracker::Preparing` buffers lock deltas while the asynchronous snapshot lock scan is still building the initial resolver; `Prepared` stores the region plus a `BTreeMap<Key, MiniLock>`.
- `Delegate` owns `region_id`, the raftstore `ObserveHandle`, memory quota, lock tracker, downstream list, `txn_extra_op`, and failure/lag bookkeeping.
- `Delegate::subscribe`, `unsubscribe`, `stop`, `stop_observing`, `mark_failed`, and `txn_extra_op` manage downstream lifecycle and observation.
- `Delegate::init_lock_tracker`, `finish_scan_locks`, `push_lock`, `pop_lock`, and `finish_prepare_lock_tracker` manage lock resolver construction and live lock deltas.
- `Delegate::on_batch` processes raftstore `CmdBatch` values, routing normal write batches to `sink_data` and split/merge admin commands to protocol errors.
- `Delegate::on_min_ts` computes each downstream's resolved-ts based on current global/store min-ts and tracked locks, then fills `Advance` buckets according to connection feature gates.
- `Delegate::convert_to_grpc_events` converts incremental-scan `KvEntry` records into one or more `CdcEvent::Event` values capped by `CDC_EVENT_MAX_BYTES`.
- Decode helpers `decode_write`, `decode_lock`, `decode_rawkv`, and `decode_default` translate storage-layer write/lock/default/raw records into `cdcpb::EventRow`.
- `ObservedRange` keeps both encoded and raw key range forms and filters raw/encoded event rows for partial-region subscriptions.

## Control Flow

Registration creates a `Delegate` through `endpoint.rs`, subscribes a `Downstream`, and later initializes the lock tracker while `initializer.rs` performs snapshot capture and incremental scan. During initialization, raftstore apply events may arrive first; `sink_txn_put` buffers lock additions/removals into `LockTracker::Preparing`. When the snapshot lock scan finishes, `finish_prepare_lock_tracker` overlays buffered deltas onto the snapshot lock set, accounts memory, and moves to `Prepared`.

Delta changes enter through `Delegate::on_batch`. Stale observe IDs are ignored. Each raft command checks response headers, then normal put requests are grouped by user key with `RowsBuilder`. RawKV puts are decoded directly. TxnKV write CF records produce commit/rollback rows and remove locks unless one-phase commit makes the commit row self-contained. Lock CF records produce prewrite rows, add locks, and mark that old value needs to be read. Default CF records attach the large value payload.

After rows are built, RawKV downstreams receive range-filtered raw rows. TiDB downstreams receive rows only if their state accepts change events, the key is inside their observed range, loop/import/DDL-source filtering permits the row, and old value is materialized if needed. If a downstream already has a resolved-ts lock heap, lock modifications are applied immediately so resolved-ts does not remain stuck on locks already committed or removed.

Resolved-ts advancement enters through `on_min_ts`. Delegates that are not `Prepared` increment `blocked_on_scan` and periodically warn. For each normal downstream, the first advance builds a per-downstream `lock_heap` from the shared region lock map filtered by `ObservedRange`. The downstream advances to `min(min_lock_ts, min_ts)`, never backwards. Depending on the connection feature gates, the result goes into multiplexed, exclusive batch, or compatibility resolved-ts output.

Administrative split and merge commands deliberately become epoch errors through `sink_admin`, which causes endpoint-level deregistration and client resubscription to the new region layout.

## State And Persistence Behavior

The delegate is in-memory only. Its durable source of truth is TiKV storage and raftstore apply order; this file does not write persistent CDC state. Important in-memory state includes:

- Shared per-region lock tracker, with memory quota accounting for key heap sizes and `CDC_PENDING_BYTES_GAUGE`.
- Per-downstream atomic state and scan cancellation flag.
- Per-downstream resolved-ts lock heap and `advanced_to`.
- `txn_extra_op`, a shared atomic flag read by the transaction layer. It is set to `ReadOldValue` when at least one downstream is attached and reset to `Noop` when observing stops.
- `ObserveHandle`, which can stop raftstore observation.

`Drop` returns memory held by pending/prepared lock tracking but intentionally does not update `txn_extra_op`; explicit lifecycle paths call `stop_observing` for that.

## Dependencies And Integration Points

- `raftstore::coprocessor::{CmdBatch, Cmd, ObserveHandle}` supplies observed apply events and observer handles.
- `endpoint::Advance` receives resolved-ts results; `Endpoint` owns scheduling and connection maps.
- `initializer::KvEntry` supplies incremental-scan entries for conversion into CDC events.
- `old_value::{OldValueCache, OldValueCallback}` is invoked for old values on delta prewrite/commit paths.
- `channel::{Sink, CdcEvent, SendError, CDC_EVENT_MAX_BYTES}` provides sink delivery and size splitting.
- `service::{Conn, FeatureGate, RequestId}` determines resolved-ts protocol shape.
- `txn_source::TxnSource` filters loopback CDC writes, Lightning physical imports, and lossy DDL reorg writes.
- `api_version::ApiV2` handles RawKV key/value timestamp encoding.
- `MemoryQuota` and CDC metrics provide backpressure and observability.

## Risks And Edge Cases

- Lock tracker memory accounting is subtle: preparing-state deltas allocate memory for buffered operations, then must be freed before prepared locks are charged. Incorrect accounting can either leak quota or allow unbounded pending locks.
- The shared region lock map is filtered into per-downstream heaps only once, then maintained by live lock deltas. Missing a `LockModifiedCount` update can permanently block resolved-ts.
- `decode_write` treats apply-time GC-fence rewrites specially by emitting an overlapped rollback. Any future write rewrite case must preserve CDC semantics here.
- Range filtering mixes encoded keys for TxnKV and raw keys for event rows. Wrong range form would leak or drop rows for observed subranges.
- Event size splitting uses row payload sizes, not full protobuf serialization size, so `CDC_EVENT_MAX_BYTES` is approximate.
- Some decoding paths use `unwrap`/`assert` on invariants supplied by TiKV storage encoding. Corrupt or unexpected records would panic rather than surface a CDC error.
- `sink_error_event` sets `scan_truncated` before force-sending the error; callers rely on this to stop concurrent incremental-scan delivery.
- `DownstreamState::Initializing` accepts change events but rejects resolved-ts. Reordering barriers in endpoint/initializer would break the guarantee that resolved-ts follows the complete incremental scan.

## Test Signals

The file has targeted unit coverage for protocol error mapping, delegate subscribe/unsubscribe behavior, observed range coverage and filtering, CDC loop/import/DDL source filtering, RawKV decoding including delete and expire timestamp, and lock tracker quota/delta behavior. Tests also cover admin split/batch-split/merge error conversion. These tests are strong for local delegate invariants but do not replace integration tests for raftstore apply ordering, sink backpressure under load, or multi-region resolved-ts behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/delegate.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/endpoint.rs -->
# sources/storage-engines/tikv/components/cdc/src/endpoint.rs

## Purpose

`endpoint.rs` implements the central CDC worker endpoint. It owns all active CDC connections, per-region delegates, observer subscriptions, incremental scan runtimes, resolved-ts scheduling, configuration hot updates, old-value cache ingestion, and periodic metrics. It is the event-loop side of the CDC subsystem: service/observer code schedules `Task` values, and `Endpoint` serializes state transitions for registrations, deregistrations, raft batches, scan completion, resolved-ts ticks, and validation callbacks.

## Important APIs, Types, And Functions

- `Deregister` describes all teardown scopes: whole connection, request, region subscription, downstream identity, or whole delegate/observe ID. It carries enough IDs to avoid stale deregistration.
- `Validate` exposes test/diagnostic callbacks over a region delegate, old-value cache, or unresolved region count.
- `Task` is the endpoint message protocol. Key variants are `Register`, `Deregister`, `OpenConn`, `SetConnVersion`, `MultiBatch`, `MinTs`, `FinishScanLocks`, `RegisterMinTsEvent`, `InitDownstream`, `TxnExtra`, `Validate`, and `ChangeConfig`.
- `ResolvedRegion` and `ResolvedRegionHeap` implement a min-heap using `BinaryHeap<Reverse<_>>`; `pop(count)` returns the lowest resolved-ts among popped outlier regions plus their IDs.
- `Advance` accumulates resolved-ts emissions in three protocol shapes: multiplexing by `(ConnId, RequestId)`, exclusive batching by `ConnId`, and legacy compatibility by `(ConnId, region_id)`. `emit_resolved_ts` sends `CdcEvent::ResolvedTs` or legacy `Event_oneof_event::ResolvedTs`.
- `Endpoint<T,E,S>` contains cluster identity, `capture_regions`, `connections`, scheduler, raft CDC handle, local tablets, observer, PD client, timers/runtimes, store meta, concurrency manager, config, scan limiters, sink memory quota, old-value cache, causal-ts provider, and metrics state.
- `Endpoint::new` constructs worker runtimes, speed limiters, old-value cache, leader resolver, initial metrics, and immediately registers the first min-ts event.
- `on_change_cfg` validates and applies online CDC config changes, resizing cache/quota/semaphore and updating scan/fetch speed limiters.
- `on_register` validates a client request, creates/subscribes delegates, installs raftstore observers, builds an `Initializer`, and spawns asynchronous incremental scan.
- `on_deregister`, `deregister_downstream`, and `deregister_observe` own all cleanup.
- `on_multi_batch` routes observed raftstore batches to delegates and schedules delegate teardown on error.
- `finish_scan_locks` reconciles initializer lock-scan output with the current delegate and deregisters failed downstreams.
- `on_min_ts` asks delegates to advance resolved-ts and emits the batched results.
- `register_min_ts_event` schedules asynchronous TSO/causal-ts acquisition and leadership resolution, then reschedules itself.
- `Runnable::run` is the worker dispatch loop; `RunnableWithTimer` flushes metrics every second.
- `CdcTxnExtraScheduler` accepts transaction-extra old-value payloads from the transaction layer, charges memory quota, and schedules `Task::TxnExtra`.

## Control Flow

Connections are opened with `Task::OpenConn`, then version/features are set with `Task::SetConnVersion`. A `Register` request first checks that the connection still exists. If the connection advertises cluster-ID validation, the request header must match `cluster_id`. The requested CDC KV API must be compatible with the store API version. The endpoint also enforces `incremental_scan_concurrency_limit`, returning `server_is_busy` before creating more pending scans.

After validation, `on_register` looks up the local region reader to obtain `txn_extra_op`, records the downstream in the connection, rejects duplicate `(request_id, region_id)` subscriptions, creates or reuses a `Delegate`, and subscribes the raftstore observer for new delegates. It then constructs an `Initializer` with snapshot/scan options and spawns it on the CDC worker runtime. The initializer later schedules `Task::InitDownstream` to synchronize capture-change response, send a barrier, and move the downstream into `Initializing`.

Raftstore observations arrive as `Task::MultiBatch`. The endpoint frees sink-memory quota already charged by the observer, then calls each region delegate. A delegate error marks it failed and becomes `Deregister::Delegate`, which broadcasts error events and removes connection subscriptions.

Resolved-ts is periodic. `register_min_ts_event` waits until the configured interval, obtains TSO from PD or causal-ts provider for API v2 RawKV, updates the concurrency manager, possibly lowers min-ts to `global_min_lock_ts`, resolves leader regions by either store RPC (`LeadershipResolver`) or raft command, schedules `Task::MinTs`, and re-registers the next event. `on_min_ts` delegates per-region advancement and emits grouped messages according to feature gates.

Deregistration is careful about stale IDs. Downstream teardown checks `DownstreamId`; delegate teardown checks `ObserveId`; connection/request/region teardown removes connection mappings and unsubscribes delegates. Removing the last downstream from a delegate stops observation and resets `txn_extra_op`.

`Task::TxnExtra` inserts old values into `OldValueCache` and frees the associated memory quota. Periodic timeout updates endpoint, region, resolved-ts, old-value cache, and sink memory metrics.

## State And Persistence Behavior

The endpoint keeps volatile CDC state only. Persistent data remains in TiKV engines and raftstore; CDC subscriptions are expected to be recreated by clients after failures or topology changes. Important volatile state includes:

- `capture_regions: HashMap<u64, Delegate>`: all observed regions.
- `connections: HashMap<ConnId, Conn>`: stream sinks and subscription indexes.
- `CdcObserver`: observer registry keyed by region/observe ID.
- Incremental scan runtime and counters/semaphore/limiters.
- `OldValueCache`: cached transaction old values delivered via `TxnExtra`.
- `current_ts`, `min_resolved_ts`, region counts, and gauges/histograms for metrics.
- `sink_memory_quota`: shared quota for CDC sink and transaction-extra scheduling.

Configuration changes mutate in-memory config and live helpers; they are validated through the `OnlineConfig` path before taking effect.

## Dependencies And Integration Points

- Raftstore: `CdcHandle`, `CmdBatch`, `ObserveId`, `StoreRegionMeta`, `CdcObserver`, and local read delegates.
- PD/resolved-ts: `PdClient`, feature gate for resolved-ts store RPC, `LeadershipResolver`, `resolve_by_raft`, and `ResolvedTsConfig`.
- TiKV storage: `LocalTablets`, `ConcurrencyManager`, `TxnExtra`, `TxnExtraScheduler`, CDC config structs.
- Async runtimes: Tokio workers for incremental scan and TSO/leadership resolution, `SteadyTimer`, futures compatibility.
- Service/channel layer: `Conn`, `FeatureGate`, `RequestId`, `validate_kv_api`, `CdcEvent`, sink errors.
- `initializer.rs` for snapshot capture and incremental scan.
- `delegate.rs` for per-region event conversion and resolved-ts gating.
- `metrics.rs` for endpoint, scan, connection, old-value, resolved-ts, sink, and task metrics.

## Risks And Edge Cases

- Registration has several partially completed states: connection subscription, delegate insertion, observer registration, and async initializer spawn. Error paths must remove the right pieces without invalidating newer subscriptions.
- The scan task counter is incremented before several early returns and released by a defer guard. This is necessary to avoid over-admission but must remain paired with every return path.
- `InitDownstream` relies on a force-sent barrier before invoking the raft callback; this ordering protects incremental scan from racing earlier delta changes.
- `register_min_ts_event` must never lose the leader resolver or fail to reschedule, otherwise resolved-ts advancement can stop. The code panics on schedule errors other than shutdown to surface this.
- `Advance::emit_resolved_ts` batches regions by increasing outlier counts. Incorrect heap ordering would regress the minimum resolved-ts reported to metrics or clients.
- Feature gates split protocol behavior between stream multiplexing, batch resolved-ts, and legacy per-region events; mixed-version clients remain a compatibility risk.
- Runtime and semaphore replacement on config updates can leave already-running scans above the new limit temporarily by design.
- `connections.get(...).unwrap()` in resolved-ts emission assumes delegates only contain downstreams for live connections; deregistration invariants must preserve this.
- Memory quota for `CdcTxnExtraScheduler` drops tasks on allocation failure and increments a metric, so old-value completeness relies on the cache/memory sizing path.

## Test Signals

Endpoint tests cover API-version compatibility, config hot updates, raftstore busy handling, registration duplicate/nonexistent-region/capture-change failures, too many scan tasks, RawKV causal min-ts, feature gates and legacy resolved-ts formats, deregistration stale-ID protection, batch resolved-ts across multiple connections, disconnect-before-delegate-ready behavior, resolved-region heap ordering, large resolved-ts batching, request/region multiplexing deregistration, and ignored registration after connection removal. These tests give strong state-machine coverage; remaining risk is mainly integration with real raftstore, PD/store-resolved-ts behavior, and production backpressure timing.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/endpoint.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/errors.rs -->
# sources/storage-engines/tikv/components/cdc/src/errors.rs

## Purpose

`errors.rs` defines the CDC subsystem error type and maps internal TiKV/engine/sink/memory errors into CDC protobuf error events sent to clients. It centralizes region-error detection so initializer and endpoint code can decide whether to deregister an entire delegate or only one downstream.

## Important APIs, Types, And Functions

- `Error` enum wraps generic boxed errors, RocksDB string errors, IO errors, storage KV errors, transaction errors, MVCC errors, raftstore request errors, engine-traits errors, CDC sink errors, and memory quota failures.
- `impl_from!` adds conversions from `String` to `Error::Rocks` and `txn_types::Error` to `Error::Mvcc`.
- `Result<T>` is the CDC-local result alias.
- `Error::request` boxes an `errorpb::Error` as `Error::Request`.
- `Error::has_region_error` matches nested storage/transaction/MVCC request errors and direct `Error::Request`.
- `extract_region_error` unwraps nested request errors into `errorpb::Error`; non-region errors become a generic message-bearing `errorpb::Error`.
- `into_error_event` maps errors into `cdcpb::Error`: sink congestion and memory quota become `Congested`; `not_leader` and `epoch_not_match` pass through; all other cases currently map to `region_not_found`.

## Control Flow

Most CDC functions use `?` into this `Error` type. When a failure must be sent to a downstream, callers invoke `into_error_event(region_id)`. Congestion-like local failures are represented as protocol `Congested` so clients can treat them as backpressure. Real raftstore region errors preserve their specific `not_leader` or `epoch_not_match` fields. For errors not represented in the CDC protocol, the fallback is `region_not_found`, with a TODO noting that the protocol should support more CDC-specific errors.

`has_region_error` is used by initializer deregistration policy: region errors, or failures while building a shared resolver, tear down the whole delegate; other errors can remove only the failing downstream.

## State And Persistence Behavior

The file has no mutable state and no persistence. It defines conversions and pure classification/mapping behavior.

## Dependencies And Integration Points

- TiKV storage errors from `tikv::storage::{kv,mvcc,txn}`.
- `engine_traits::Error`, `txn_types::Error`, and `std::io::Error`.
- CDC channel `SendError` for disconnected/full/congested sink cases.
- `tikv_util::memory::MemoryQuotaExceeded`.
- Protobuf error types from `kvproto::{cdcpb,errorpb}`.
- `thiserror` for display/source implementations.

## Risks And Edge Cases

- The fallback from unknown errors to `region_not_found` can hide the real error class from clients. This is explicitly marked as incomplete protocol coverage.
- `has_region_error` relies on exact nested box-pattern matching. If TiKV storage error wrapping changes, region errors may be misclassified and cause downstream-only deregistration instead of delegate teardown.
- Congestion and memory-quota errors are collapsed into the same CDC `Congested` event, which is useful for retry/backpressure but loses detail.
- `extract_region_error` consumes `self`; callers must not expect to inspect the original error afterwards.

## Test Signals

There are no tests in this file, but delegate and endpoint tests exercise `into_error_event` indirectly for `not_leader`, `epoch_not_match`, congestion, generic errors mapping to `region_not_found`, and admin split/merge error conversion. Direct unit tests for nested storage error variants would make `has_region_error` safer against future error type changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/initializer.rs -->
# sources/storage-engines/tikv/components/cdc/src/initializer.rs

## Purpose

`initializer.rs` runs the asynchronous initialization for a newly registered downstream. Its responsibilities are to capture raftstore change observation, establish the ordering barrier between already-observed delta changes and snapshot scan output, optionally build the shared lock resolver, scan incremental changes since the checkpoint, stream scan events to the sink under rate limits, and schedule deregistration on failure.

This file is the bridge from a client registration to a normal CDC stream.

## Important APIs, Types, And Functions

- `ScanStat` records emitted bytes, optional disk-read bytes, and RocksDB perf delta for incremental scan observability.
- `KvEntry` wraps either transactional `TxnEntry` or RawKV `KvPair` so delegate conversion can handle both APIs.
- `Scanner<S>` is either a TxnKV `DeltaScanner<S>` or RawKV `RawMvccIterator`.
- `Initializer<E>` stores all registration identity, checkpoint and epoch, resolver-building flag, observed range, observe handle, downstream state/cancellation, optional tablet, scheduler, sink, scan semaphore/limiters, batch sizing, timestamp-filter ratio, requested KV API, and loop filtering.
- `initialize` acquires the scan concurrency permit, sends `capture_change` to raftstore, schedules `Task::InitDownstream` from the read callback, waits for a pre-scan barrier, and handles the capture-change snapshot response.
- `on_change_cmd_response` either starts `async_incremental_scan` with the snapshot and region or converts a response header error.
- `async_incremental_scan` computes the effective scan range, builds resolver locks when requested, constructs TxnKV or RawKV scanner, loops over `scan_batch`, streams events with `sink_scan_events`, and transitions downstream to `Normal`.
- `do_scan` is the synchronous scan core. It reads up to byte/count batch limits, resolves old values when the ts-filter path emits `OldValue::SeekWrite`, gathers IO/perf stats, and appends `None` as an end marker.
- `scan_batch` updates cumulative stats, flushes RocksDB perf metrics, and applies disk-read and emitted-byte rate limiters.
- `sink_scan_events` converts entries through `Delegate::convert_to_grpc_events`, sends them with cancellation awareness, and waits on a final barrier before allowing resolved-ts.
- `finish_scan_locks` schedules `Task::FinishScanLocks` with the scanned lock map.
- `deregister_downstream` chooses between whole-delegate and single-downstream deregistration based on resolver-building and region-error classification.
- `ts_filter_is_helpful` inspects write-CF table properties, especially max timestamp, to decide whether `DeltaScanner::hint_min_ts` will avoid enough old versions.

## Control Flow

`initialize` first checks whether the downstream was already stopped, then requests raftstore to capture changes for the region using `ChangeObserver::from_cdc`. The raftstore read callback schedules `Task::InitDownstream`, which is handled by endpoint on the serial CDC worker. That endpoint task initializes the delegate lock tracker if needed, sets `build_resolver`, force-sends an incremental-scan barrier to the sink, transitions downstream state from `Uninitialized` to `Initializing`, and finally invokes the paired callback so `initialize` can continue.

The initializer waits for the barrier to complete before reading the capture-change snapshot response. This guarantees delta changes observed before the snapshot are delivered before scan results. If the snapshot exists, `async_incremental_scan` runs.

`async_incremental_scan` first updates `ObservedRange` against the actual region and computes intersection bounds for backwards-compatible clients that did not supply a range. If this initializer is responsible for resolver construction, it scans all storage locks for the whole region, filters to Put/Delete locks, and schedules `FinishScanLocks`.

For TxnKV, the scanner is a `DeltaScanner` over `(checkpoint_ts, max]`, optionally using `hint_min_ts` and `OldValueCursors` when table-property analysis says the timestamp filter is helpful. For RawKV, it creates a RawMVCC iterator over the API v2 raw key prefix and emits versions newer than `checkpoint_ts`.

The loop cancels quickly if downstream state becomes `Stopped`, warns/metrics long scans after 60 seconds, scans a bounded batch, detects completion by a trailing `None`, converts and sends events, and repeats. On completion it atomically moves state from `Initializing` to `Normal`, records scan duration/sink duration, and returns stats.

Errors from initialization call `deregister_downstream`: if resolver construction failed or the error is region-scoped, the whole delegate is deregistered; otherwise only this downstream is removed.

## State And Persistence Behavior

The initializer is transient and owns no durable state. It holds snapshots/iterators while scanning and uses in-memory semaphores/rate limiters/backpressure. Its observable side effects are:

- Scheduling endpoint tasks (`InitDownstream`, `FinishScanLocks`, `Deregister`).
- Sending scan events and barriers into the CDC sink.
- Moving downstream state from `Uninitialized` to `Initializing` to `Normal`, or respecting `Stopped`.
- Setting `scan_truncated` indirectly through sink error paths and responding to it in `send_all`.
- Updating CDC scan, old-value, disk-read, and RocksDB perf metrics.

The scan uses TiKV snapshot contents as the persistent source of truth; no CDC initialization checkpoint is written.

## Dependencies And Integration Points

- `raftstore::router::CdcHandle` and `ChangeObserver` for capture-change read callbacks.
- `endpoint::Task` and `Deregister` for scheduling endpoint state transitions.
- `delegate::{Delegate, MiniLock, ObservedRange, post_init_downstream}` for event conversion, resolver locks, and state transition.
- TiKV MVCC scanners: `DeltaScanner`, `MvccReader`, `ScannerBuilder`, `TxnEntryScanner`, RawKV `RawMvccSnapshot`.
- Rocks engine/table properties and perf context for timestamp-filter decisions and metrics.
- `old_value::{OldValueCursors, near_seek_old_value}` for materializing old values when filter optimization skips old write records.
- `tokio::sync::Semaphore` and `tikv_util::time::Limiter` for concurrency and speed limiting.
- `ApiV2`, engine-traits CF/range APIs, region metadata, fail points, and CDC metrics.

## Risks And Edge Cases

- Correctness depends on the capture-change callback, sink barrier, and snapshot scan ordering. If the barrier is skipped or not force-sent, clients can see scan rows before earlier delta changes.
- Resolver construction scans the whole region, not just the observed subrange, because it is shared across downstreams. This is intentional but increases memory and scan cost.
- `scan_locks_from_storage(None, None, ...)` relies on the region snapshot scope; if snapshot scoping changes, resolver lock coverage could become too broad.
- RawKV scanner iterates the whole RawKV prefix and filters by checkpoint timestamp, while range filtering happens later in event conversion/observed range handling. This can be expensive for small observed ranges.
- `ts_filter_is_helpful` depends on RocksDB table properties and `PROP_MAX_TS`; missing or inaccurate properties disable or misguide the optimization.
- Old-value resolution with `OldValue::SeekWrite` is correctness-sensitive. The missing-range cache test indicates prior risk around cursor movement and repeated misses.
- Long-running scans hold snapshots; scan concurrency and speed limiters mitigate but do not eliminate storage pressure.
- Many storage decoding paths still unwrap parser results from trusted on-disk encodings.

## Test Signals

Initializer tests cover lock scanning and resolver scheduling, observed-range scan filtering, cancellation and sink disconnect failures, transaction source filtering for CDC loop/import/lossy-DDL writes, old-value correctness with `hint_min_ts`, old-value missing-range cache behavior, deregistration policy, semaphore blocking in `initialize`, RawKV and TiDB initialize paths, Titan-backed scanner behavior, and table-property scan-range optimization. The tests are broad for scan correctness and cancellation; full production coverage still depends on endpoint/raftstore integration tests for ordering and leadership changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/initializer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/lib.rs -->
# sources/storage-engines/tikv/components/cdc/src/lib.rs

## Purpose

`lib.rs` is the crate root for TiKV's CDC component. It declares the internal CDC modules and re-exports the public API surface used by the rest of TiKV: event/channel primitives, configuration manager, delegate and endpoint types, error/result types, observer, old-value cache, and service entry points.

## Important APIs, Types, And Functions

- Enables `#![feature(box_patterns)]`, which is required by `errors.rs` nested error matching.
- Declares internal modules: `channel`, `config`, `delegate`, `endpoint`, `errors`, `initializer`, `observer`, `old_value`, `service`, `txn_source`, `types`, and `watchdog`.
- Exposes `metrics` as a public module.
- Re-exports:
  - `channel::{CdcEvent, recv_timeout}`
  - `config::CdcConfigManager`
  - `delegate::Delegate`
  - `endpoint::{CdcTxnExtraScheduler, Endpoint, Task, Validate}`
  - `errors::{Error, Result}`
  - `observer::CdcObserver`
  - `old_value::OldValueCache`
  - `service::{FeatureGate, Service}`

## Control Flow

There is no runtime control flow in this file. Its role is module wiring and public export selection. The larger CDC control flow starts from `Service` and `CdcObserver`, schedules `Task` values into `Endpoint`, uses `Initializer` for incremental scan, and delegates per-region event conversion to `Delegate`.

## State And Persistence Behavior

`lib.rs` has no state or persistence behavior. It controls crate visibility.

## Dependencies And Integration Points

The file integrates this crate with external TiKV components by exposing only selected types. `Endpoint`, `Task`, and `CdcTxnExtraScheduler` are required by worker/router wiring; `CdcObserver` integrates with raftstore coprocessor observation; `Service` is the gRPC-facing CDC service; `OldValueCache` and `metrics` support monitoring and old-value paths.

## Risks And Edge Cases

- Export changes can become crate API changes for other TiKV modules.
- The crate relies on nightly `box_patterns`; removing or stabilizing nested error matching would require coordinated updates in `errors.rs`.
- Making modules public accidentally would widen the maintenance surface; currently most internals remain private.

## Test Signals

There are no direct tests for `lib.rs`. Compile tests and downstream module tests validate that the module graph and re-exports are correct.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/metrics.rs -->
# sources/storage-engines/tikv/components/cdc/src/metrics.rs

## Purpose

`metrics.rs` defines Prometheus metrics and helper functions for the CDC component. It covers endpoint task backlog, resolved-ts lag, incremental scan throughput/duration, connection counts, old-value cache and scan details, sink memory, region resolve status, RocksDB perf counters, RawKV outlier lag, event pending duration, and aborted connections.

## Important APIs, Types, And Functions

- `TAG_DELTA_CHANGE` and `TAG_INCREMENTAL_SCAN` label old-value scan metrics by source path: raft delta changes versus incremental scan.
- `make_auto_flush_static_metric!` defines `PerfMetric` labels and `PerfCounter` for RocksDB read perf counters.
- Lazy static metrics include gauges, counters, counter vecs, histogram vecs, and histograms such as:
  - `CDC_ENDPOINT_PENDING_TASKS`
  - `CDC_RESOLVED_TS_GAP_HISTOGRAM`
  - `CDC_SCAN_DURATION_HISTOGRAM`
  - `CDC_SCAN_SINK_DURATION_HISTOGRAM`
  - `CDC_SCAN_BYTES`
  - `CDC_CONNECTION_COUNT`
  - `CDC_DROP_TXN_EXTRA_TASKS_COUNT`
  - `CDC_SCAN_TASKS`
  - `CDC_SCAN_DISK_READ_BYTES`
  - `CDC_MIN_RESOLVED_TS_REGION`, `CDC_MIN_RESOLVED_TS_LAG`, `CDC_MIN_RESOLVED_TS`
  - `CDC_PENDING_BYTES_GAUGE`
  - `CDC_CAPTURED_REGION_COUNT`
  - `CDC_OLD_VALUE_*`
  - `CDC_REGION_RESOLVE_STATUS_GAUGE_VEC`
  - `CDC_RESOLVED_TS_ADVANCE_METHOD`
  - `CDC_GRPC_ACCUMULATE_MESSAGE_BYTES`
  - `CDC_ROCKSDB_PERF_COUNTER` and static wrapper
  - `CDC_RAW_OUTLIER_RESOLVED_TS_GAP`
  - `CDC_EVENTS_PENDING_DURATION`
  - `CDC_ABORTED_CONNECTIONS`
- `TLS_CDC_PERF_STATS` is a thread-local `ReadPerfContext` accumulator.
- `tls_flush_perf_stat!` increments one static RocksDB perf counter.
- `tls_flush_perf_stats` takes and resets the thread-local perf context, then emits every RocksDB perf field.
- `flush_oldvalue_stats` emits TiKV `Statistics` detail counters with CF, tag, and type labels.

## Control Flow

Other CDC files update these metrics inline. `initializer.rs` adds scan bytes, disk-read bytes, durations, scan task counts, old-value stats, and RocksDB perf deltas. `delegate.rs` updates pending lock bytes. `endpoint.rs` updates pending tasks, captured region count, resolve status, min resolved-ts lag, sink bytes/capacity, connection count, dropped transaction-extra tasks, and resolved-ts advancement method.

`TLS_CDC_PERF_STATS` lets scan code accumulate RocksDB perf deltas on the scanning thread, then `tls_flush_perf_stats` drains the local context to global Prometheus counters.

## State And Persistence Behavior

Metrics are process-local runtime state registered with Prometheus. They are not persisted by this file. Lazy registration occurs on first access, and thread-local perf stats are reset after flushing.

## Dependencies And Integration Points

- `prometheus` and `prometheus_static_metric` provide metric registration and static label wrappers.
- `engine_rocks::ReadPerfContext` supplies RocksDB internal read counters.
- `tikv::storage::Statistics` supplies old-value scan detail counters.
- The metric names and labels are part of TiKV observability contracts consumed by dashboards, alerts, and tests.

## Risks And Edge Cases

- Metric registration names are global; duplicate names or label shape changes can break startup or dashboards.
- Gauge/counter semantic mistakes are easy: several old-value cache access/miss values are gauges even though names sound cumulative.
- `tls_flush_perf_stats` must be called from the same thread whose thread-local context was updated; otherwise counters can be delayed or lost until a later flush on that thread.
- Adding RocksDB perf fields requires updating both the static metric enum and flush function in lockstep.
- `flush_oldvalue_stats` depends on stable CF/tag strings from `Statistics::details`.

## Test Signals

There are no direct tests in this file. The metrics are indirectly exercised by delegate, endpoint, and initializer tests that call the paths updating gauges/counters/histograms. Direct metric registration tests would be low value but could catch duplicate name or label cardinality changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/cdc/src/metrics.rs -->
