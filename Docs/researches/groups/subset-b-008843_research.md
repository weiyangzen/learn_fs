# Research: subset-b-008843

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/dispatcher.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/dispatcher.rs

## Purpose
`dispatcher.rs` is the raftstore coprocessor dispatch layer. It owns the observer registry, boxed cloneable observer wrappers, registration ordering, and the public `CoprocessorHost` hook methods that raftstore calls while proposing, applying, executing, persisting, splitting, snapshotting, computing consistency hashes, handling messages, and observing write batches.

## Important APIs, Types, And Functions
`StoreHandle` is the scheduling interface observers use to send raftstore side effects back into the store: approximate size/key updates, split requests, bucket refreshes, consistency hash results, and compaction-declined byte updates. The `SyncSender<SchedTask>` implementation is intentionally best-effort via `try_send`.

`SchedTask` is the concrete message enum emitted by split checkers and other coprocessors. `Registry<E>` stores observer vectors by hook family, each as `Entry { priority, observer }`, plus singleton `write_batch_observer` and `snapshot_observer`. The `impl_box_observer!` and `impl_box_observer_g!` macros adapt cloneable concrete observers into trait-object boxes.

`CoprocessorHost<E>` is the main facade. `new` installs default split checkers in priority order: `HalfCheckObserver`, `SizeCheckObserver`, `KeysCheckObserver`, `TableCheckObserver`, plus `SplitObserver` for admin split validation.

## Control Flow
Registration calls `start()` and then sorts ascending by priority; lower priority value runs earlier. `loop_ob!` and `try_loop_ob!` create an `ObserverContext`, invoke each observer, and stop when `ctx.bypass` is set. Error-returning hooks short-circuit on `Result::Err`.

The host dispatches query versus admin paths in `pre_propose`, `pre_apply`, `post_apply`, `pre_exec`, and `post_exec`. Snapshot hooks fan out through `apply_snapshot_observers`. Split checks are created through `new_split_checker_host`, which gives observers a chance to add checkers. Consistency checks walk observers, consuming portions of request context as each observer computes a hash. Apply command batch flushing first emits `post_apply` for contained commands and then lets command observers inspect or mutate the batch vector.

## State And Persistence Behavior
The dispatcher itself persists no data. Persistence influence is indirect: `post_exec_*` can request special persistence, `pre_persist` can veto region/meta persistence, `pre_write_apply_state` can veto apply-state writes, and write-batch/snapshot observers can observe engine writes or snapshots. `StoreHandle` messages cross back into raftstore state machines asynchronously and can be dropped if the sync channel is full.

## Dependencies And Integration Points
This file integrates `engine_traits`, `kvproto`, `raft`, split-check modules, read/write observers, consistency checks, and raftstore store types (`BucketRange`, `SnapKey`, `Snapshot`). It is called by raftstore FSM/apply code and is extended by CDC, resolved-ts, PiTR, region-info access, split observers, and consistency observers.

## Risks
Priority ordering is contract-sensitive; a lower numeric priority runs first. `try_send` silently drops scheduling tasks on channel pressure, so callers must tolerate stale approximate stats or delayed split signals. Singleton write-batch and snapshot observers mean later registrations replace earlier ones. Several hooks run on performance-critical raftstore paths, so observer code must avoid blocking. `on_update_safe_ts` checks `query_observers.is_empty()` before iterating `update_safe_ts_observers`, which is surprising and could suppress safe-ts hooks if no query observer is registered.

## Test Signals
Unit tests verify correct hook routing, priority ordering, bypass behavior, error short-circuiting, apply snapshot hooks, persistence hooks, raft message hooks, and command-batch flushing through a synthetic `TestCoprocessor`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/dispatcher.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/error.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/error.rs

## Purpose
`error.rs` defines the small error surface used by raftstore coprocessor hooks and split-check helpers.

## Important APIs, Types, And Functions
`Error` has two variants: `RequireDelay { after, reason }`, for retry-after style coprocessor failures, and `Other(Box<dyn StdError + Sync + Send>)`, for boxed underlying errors. `Result<T>` aliases `StdResult<T, Error>`. `ErrorCodeExt` maps all variants to `error_code::raftstore::COPROCESSOR`.

## Control Flow
Most coprocessor modules return this `Result` and use `box_try!` or `box_err!` to convert lower-level failures into `Error::Other`. Dispatcher hooks that return `Result` short-circuit when this error is produced.

## State And Persistence Behavior
No state is stored or persisted. The only operational behavior is classification of errors for observability and error-code propagation.

## Dependencies And Integration Points
Depends on `thiserror`, `error_code`, and standard error traits. It is re-exported from `coprocessor/mod.rs` and used across dispatcher, split-check, and region-info provider methods.

## Risks
`RequireDelay` is defined here but not handled specially in the files in this subset; upstream callers need to preserve the retry semantics. The broad boxed `Other` type keeps conversion easy but can hide structured failure details unless logs include source errors and codes.

## Test Signals
No direct tests in this file. Coverage is indirect through modules that return `coprocessor::Result`, especially split-check approximate-stat tests and dispatcher error short-circuit tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/metrics.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/metrics.rs

## Purpose
`metrics.rs` declares Prometheus metrics for region-size/key observations and region-info collection counts.

## Important APIs, Types, And Functions
`REGION_SIZE_HISTOGRAM` records approximate region sizes with exponential buckets from 1 MiB up to roughly 512 GiB. `REGION_KEYS_HISTOGRAM` records approximate key counts with exponential buckets from 1 to about 2^29. `REGION_COUNT_GAUGE_VEC` exposes a `type` label and is used for `"region"`, `"leader"`, and `"buckets"` counts.

## Control Flow
Metrics are lazy-static globals registered at first use. Size/key split observers call histogram `observe`; `RegionCollector::on_timeout` refreshes the gauge values every 10 seconds.

## State And Persistence Behavior
Metrics are in-process Prometheus collectors only. They are not persisted to raftstore state, but scraping systems may retain time series externally.

## Dependencies And Integration Points
Uses `prometheus` registration macros and is consumed by `split_check/size.rs`, `split_check/keys.rs`, and `region_info_accessor.rs`.

## Risks
Registration uses `unwrap()`, so duplicate metric names or registry failures would panic during initialization. Gauge label cardinality is intentionally tiny; adding dynamic labels would be dangerous. Histogram ranges need to stay aligned with supported region sizes.

## Test Signals
No direct tests. Indirect runtime signal comes from split-check tests invoking histogram observations and region collector timer logic setting gauges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/mod.rs

## Purpose
`mod.rs` is the public interface for raftstore coprocessors. It declares the hook traits, command observation data structures, region-change and role-change event types, and re-exports the concrete dispatcher, split-check, consistency-check, read/write, and region-info APIs.

## Important APIs, Types, And Functions
`Coprocessor` provides `start`/`stop`. `ObserverContext` wraps the current region and the `bypass` flag used by dispatcher loops. Hook traits include `AdminObserver`, `QueryObserver`, `ApplySnapshotObserver`, `SplitCheckObserver`, `PdTaskObserver`, `RoleObserver`, `RegionChangeObserver`, `RegionHeartbeatObserver`, `RaftMessageObserver`, `CmdObserver`, `ReadIndexObserver`, `UpdateSafeTsObserver`, `DestroyPeerObserver`, and `TransferLeaderObserver`.

`RegionState` and `ApplyCtxInfo` describe apply-time state visible to exec observers. `Cmd` carries raft index, term, request, and response. `ObserveId`, `ObserveHandle`, and `CmdObserveInfo` track whether CDC, resolved-ts, and PiTR observation streams are active. `ObserveLevel` summarizes observation scope as `None`, `LockRelated`, or `All`. `CmdBatch` groups applied commands with observe IDs and region id and can estimate memory size.

## Control Flow
The dispatcher invokes default no-op trait methods unless registered observers override them. `CmdObserveInfo::observe_level` chooses the maximum active observation level: CDC and PiTR require all data, resolved-ts requires lock-related data, and inactive handles contribute `None`. `CmdBatch::push`, `extend`, and `into_iter` assert that region and observe IDs match, preventing accidental cross-region or stale-observer mixing.

## State And Persistence Behavior
This module defines state passed between raftstore and observers but does not persist data itself. `ObserveHandle` state is shared via an `Arc<AtomicBool>`, allowing observers to stop observation without mutating batches already carrying IDs. `CmdBatch::size` estimates only successful non-admin put/delete command payloads.

## Dependencies And Integration Points
The module binds `engine_traits`, `kvproto`, `pd_client`, `raft`, raftstore snapshot/store types, split-check modules, read/write wrappers, and region-info accessor exports. It is the main API consumed by raftstore, CDC, backup-log/PiTR, resolved-ts, split, region-info, and consistency subsystems.

## Risks
Most default hooks are no-ops, so missing registration can fail silently. `CmdBatch` uses assertions for invariants, which is correct for internal misuse but can panic if callers combine wrong observe handles. `CmdBatch::size` is approximate and ignores some command types and error responses. Observer hook contracts are broad and run in sensitive raftstore paths, so implementors must avoid blocking and must honor region/epoch semantics.

## Test Signals
The local test covers `CmdObserveInfo::observe_level` combinations for CDC, resolved-ts, and PiTR active/inactive handles. Dispatcher tests cover most trait hook invocation paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/mod.rs

## Purpose
This module is the namespace for read/write observation support added under raftstore coprocessors.

## Important APIs, Types, And Functions
It declares `snapshot` and `write_batch` submodules and re-exports their public contents: `ObservedSnapshot`, `SnapshotObserver`, `ObservableWriteBatch`, `WriteBatchObserver`, and `WriteBatchWrapper`.

## Control Flow
There is no runtime logic here. Consumers import through `coprocessor::read_write` or through `coprocessor/mod.rs` re-exports.

## State And Persistence Behavior
No state or persistence is implemented in this file. The submodules define the actual snapshot/write-batch observation behavior.

## Dependencies And Integration Points
The module is used by `dispatcher.rs` for boxed observer registration and by `coprocessor/mod.rs` for public re-exports.

## Risks
Because this is a thin module, the main risk is API visibility drift: adding a new read/write observer type requires updating re-exports if external callers should use it.

## Test Signals
No direct tests; coverage is through `write_batch.rs`, `snapshot.rs`, and dispatcher integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/snapshot.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/snapshot.rs

## Purpose
`snapshot.rs` defines the hook for observing raftstore region snapshot creation.

## Important APIs, Types, And Functions
`ObservedSnapshot` is a marker trait requiring `Any + Send + Sync`, allowing concrete snapshot observation payloads to be downcast later. `SnapshotObserver` has `on_snapshot(region, read_ts, sequence_number) -> Box<dyn ObservedSnapshot>`, called when raftstore takes a `RegionSnapshot`.

## Control Flow
`CoprocessorHost::on_snapshot` calls the singleton registered snapshot observer, if present, and returns its boxed observed payload. If no observer is registered, the host returns `None`.

## State And Persistence Behavior
The file stores no state. Implementations may capture snapshot metadata or side data, but this trait only returns an in-memory object. It does not persist snapshot observations by itself.

## Dependencies And Integration Points
Depends on `kvproto::metapb::Region` and `std::any::Any`. It integrates with dispatcher snapshot registration and any subsystem that needs to bind metadata to region snapshots.

## Risks
Only one snapshot observer is supported by the registry, so registrations replace previous observers. Downcasting through `Any` is flexible but shifts type-safety to callers. Implementations run during snapshot creation and must avoid heavy blocking.

## Test Signals
No local tests in this file. Dispatcher behavior for optional singleton snapshot observer should be covered by integration or downstream observer tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/write_batch.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/write_batch.rs

## Purpose
`write_batch.rs` wraps an engine `WriteBatch` so raftstore can mirror write operations into an optional observable write batch for external observers while still writing through the real engine batch.

## Important APIs, Types, And Functions
`WriteBatchObserver` creates a boxed `ObservableWriteBatch`. `ObservableWriteBatch` extends `WriteBatch + Send` and adds `prepare_for_region`, `write_opt_seq`, and `post_write`. `WriteBatchWrapper<WB>` holds the real batch plus optional observable batch and implements both `WriteBatch` and `Mutable`.

## Control Flow
`prepare_for_region` delegates to the observable batch only. Mutations (`put`, `put_cf`, `delete`, `delete_cf`, `delete_range`, `delete_range_cf`) first mirror the operation into the observable batch, then apply it to the real batch. `write`, `write_opt`, and `write_callback_opt` delegate to the real batch; inside the real write callback the wrapper calls observable `write_opt_seq` once with the engine sequence number and options, then calls the caller callback. After write completion, `post_write` is invoked on the observable batch whether the real write succeeded or failed according to the returned result path.

Save points, rollback, pop, and clear are mirrored into both batches. `merge` is intentionally unsupported and panics if called.

## State And Persistence Behavior
The wrapper does not own persistence but sits directly on the write path. The real `WB` controls engine persistence; the observable batch records a parallel stream for consumers. The `AtomicBool` in `write_callback_opt` guards against multiple callback invocations causing multiple sequence notifications.

## Dependencies And Integration Points
Uses `engine_traits::{WriteBatch, Mutable, WriteOptions, CF_DEFAULT}` and `kvproto::metapb::Region`. `CoprocessorHost::on_create_apply_write_batch` constructs this wrapper from the registry singleton write-batch observer.

## Risks
Observable mutation happens before the real mutation, so if the real operation fails, the observable batch must tolerate rollback or post-write cleanup. `merge` is not supported; callers needing merge semantics must avoid wrapping or implement explicit merging. The overridden `put_msg`/`put_msg_cf` intentionally route through `put`/`put_cf` to avoid missed observations, but this assumes no underlying implementor relies on specialized message encoding behavior beyond protobuf bytes.

## Test Signals
No direct tests in this file. Expected coverage is through downstream write-batch observer implementations and raftstore apply-write paths that use `on_create_apply_write_batch`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/read_write/write_batch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/region_info_accessor.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/region_info_accessor.rs

## Purpose
`region_info_accessor.rs` maintains a worker-backed, in-memory index of region metadata, roles, bucket counts, leader ids, and recent heartbeat activity. It lets other components query region coverage and high-activity regions without directly walking raftstore internals.

## Important APIs, Types, And Functions
`RaftStoreEvent` models create, update, destroy, role-change, bucket-update, and activity-update events. `RegionInfo` stores `Region`, `StateRole`, and bucket count. `RangeKey` normalizes finite keys and empty end-key infinity so region ranges can be ordered in a `BTreeMap`.

`RegionInfoQuery` is the worker task enum for raftstore events and queries. `RegionEventListener` implements `RegionChangeObserver`, `RoleObserver`, and `RegionHeartbeatObserver`, forwarding events to the worker scheduler. `RegionCollector` owns the maps: `regions`, `region_ranges`, `region_activity`, and shared `region_leaders`. `RegionInfoAccessor` owns the worker and implements `RegionInfoProvider`.

Key methods include `check_region_range`, `handle_raftstore_event`, `handle_seek_region`, `handle_get_regions_in_range`, `handle_get_top_regions`, and provider methods such as `find_region_by_key`, `get_top_regions`, and `get_regions_stat`.

## Control Flow
`RegionInfoAccessor::new` starts a dedicated timed worker and registers `RegionEventListener` at priority 1. Raftstore observer hooks enqueue `RegionInfoQuery::RaftStoreEvent`. The collector first rejects invalid epoch-version-zero events and uninitialized role changes, then checks whether the incoming region is stale compared with same-id or overlapping regions. Non-stale events update the hash map and end-key index, possibly clearing older overlapping entries.

Queries are also scheduler messages. Async callbacks are used for seek and find-by-id; synchronous provider methods build an mpsc channel, schedule a query, and block waiting for the callback response. Timer ticks refresh region, leader, and bucket-count gauges every 10 seconds.

## State And Persistence Behavior
All collected state is in memory and intentionally approximate. It can lag raftstore and may temporarily omit regions during split/merge. `region_leaders` is shared through `Arc<RwLock<HashSet<u64>>>` for direct consumers. Destroy removes region metadata, end-key mapping, activity, and leader membership. No durable persistence is performed; restart reconstructs state from future raftstore events.

## Dependencies And Integration Points
Depends on `engine_traits::KvEngine`, `kvproto::metapb::Region`, `pd_client::RegionStat`, raft roles, TiKV worker utilities, and coprocessor observer traits. It feeds in-memory engine/cache decisions through `get_top_regions`, raft KV through leader-id access, and Prometheus metrics via `REGION_COUNT_GAUGE_VEC`.

## Risks
Range correctness depends on `RangeKey` and epoch comparisons. Event reordering around split/merge is expected; stale filtering handles many cases but comments acknowledge rare role inaccuracies. Provider methods that block on mpsc receive can fail if the worker stops. `handle_get_regions_stat` unwraps `self.regions.get(&id)`, assuming activity cannot outlive region metadata. Top-region selection is `O(N log N)` over heartbeat activity and logs debug summaries, so large deployments must keep heartbeat volume bounded.

## Test Signals
Tests cover `RangeKey` ordering, invalid-version filtering, epoch staleness, clearing overlapped regions, basic create/update/destroy/role behavior, split and merge event order permutations, extreme split/merge races, mock provider range/seek behavior, and top-region filtering by leadership, flashback, iterated count, and MVCC amplification.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/region_info_accessor.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/half.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/half.rs

## Purpose
`half.rs` implements load/admin half-split behavior: while scanning it records bucket boundary keys and returns a middle key, and in approximate mode it asks the engine for one approximate middle split key.

## Important APIs, Types, And Functions
`Checker` stores scanned bucket starts, current bucket size, target bucket size, and policy. `HalfCheckObserver` installs the checker for non-size split reasons. `half_split_bucket_size` derives a bucket target from region max size with a 1024-bucket cap and a 512 MiB per-bucket ceiling. `get_region_approximate_middle` calls `KvEngine::get_range_approximate_split_keys(range, 1)`.

## Control Flow
`on_kv` pushes the first key and every key after the current bucket reaches `each_bucket_size`, then accumulates entry size. `split_keys` returns the middle bucket key converted from data key to origin key, or no key if fewer than two buckets were recorded. `approximate_split_keys` returns at most one key from engine range properties.

`HalfCheckObserver::add_checker` skips `SplitReason::Size` so size-based split checks rely on size/keys checkers. For load/admin reasons it adds the half checker with the requested policy.

## State And Persistence Behavior
State is per split-check run only. The checker keeps bucket keys in memory and does not update raftstore directly. Actual split requests are issued later by the split-check runner through the host and `StoreHandle`.

## Dependencies And Integration Points
Uses `engine_traits::{KvEngine, Range}`, `kvproto` split reason/policy, TiKV `ReadableSize`, and shared split-check host traits. It is registered by default in `CoprocessorHost::new` with priority 100.

## Risks
Approximate middle depends on range properties and can be unavailable or imprecise for small/unflushed data. Scan mode memory grows with the number of bucket boundaries, bounded by bucket sizing rather than a hard vector length. The returned key is a bucket start near the middle, not necessarily a byte-perfect median.

## Test Signals
Tests verify checker selection by split reason, load split midpoint behavior, scan and approximate midpoint output, split checks over explicit key ranges, bucket generation for normal/MVCC/deleted-data cases, and approximate middle across column families.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/half.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/keys.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/keys.rs

## Purpose
`keys.rs` implements key-count-based split checking. It updates approximate key counts, decides whether a region needs split checking, and produces split keys either by scan counting commit-version entries or by engine approximate range properties.

## Important APIs, Types, And Functions
`Checker` tracks `max_keys_count`, `split_threshold`, `current_count`, accumulated `split_keys`, `batch_split_limit`, and `policy`. `KeysCheckObserver<C>` owns a `StoreHandle` router. `get_region_approximate_keys` calls `KvEngine::get_range_approximate_keys` over encoded region bounds.

## Control Flow
`KeysCheckObserver::add_checker` first asks the engine for an approximate key count up to `region_max_keys * batch_split_limit`. On success it sends `UpdateApproximateKeys`, records `REGION_KEYS_HISTOGRAM`, and adds a scan checker only if the count is at least `region_max_keys`. On approximate-stat error it logs and adds a checker anyway.

During scanning, `Checker::on_kv` ignores entries that are not commit versions. After `current_count` exceeds `split_threshold`, it records the current origin key and resets the counter. Scanning can stop early once the batch split limit is reached and the remaining counted tail is large enough. `split_keys` drops the final key if the last region fragment would be under `max_keys_count`. Approximate mode estimates how many split keys are needed with `calc_split_keys_count` and retrieves that many approximate split keys through the size module helper.

## State And Persistence Behavior
Only per-run counters and split keys are stored. Persistent raftstore state is updated indirectly via `StoreHandle::update_approximate_keys` and later split scheduling. Approximate counts are observability/control-plane inputs, not durable state in this file.

## Dependencies And Integration Points
Uses `engine_traits::KvEngine`, `kvproto::CheckPolicy`, split-check host/config, shared metrics, `StoreHandle`, and `size::get_approximate_split_keys`. It runs after size checking in the default registry, and comments rely on size checker ordering for bucket-scan reuse.

## Risks
Correctness depends on `KeyEntry::is_commit_version`; non-MVCC or unusual entries can affect counts. Approximate key counts may undercount subregions depending on range properties. The final split-key pop logic protects against undersized trailing regions but makes boundary behavior sensitive to off-by-one changes in threshold comparison.

## Test Signals
Tests cover scan split generation at configured key thresholds and batch limits, approximate-key split mode, approximate key counting from write/default CF data, split-key count math, interaction with bucket-enabled size checks, sub-region approximate-key behavior, and safe behavior when the receiver is dropped.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/keys.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/mod.rs

## Purpose
`split_check/mod.rs` ties together the concrete split checkers and defines the split-check host used during raftstore split scans.

## Important APIs, Types, And Functions
The module re-exports `HalfCheckObserver`, `KeysCheckObserver`, `SizeCheckObserver`, `TableCheckObserver`, and approximate-stat helpers. `Host<'a, E>` owns a list of boxed `SplitChecker<E>`, the `SplitReason`, and a borrowed `Config`. `calc_split_keys_count` computes how many split keys are needed from region size/key count, split threshold, max per region, and batch limit.

## Control Flow
Observers add checkers through `Host::add_checker`. `policy` returns `Approximate` if any checker requests approximate mode; otherwise it returns `Scan`. `on_kv` feeds each scanned `KeyEntry` to each checker and aborts if any checker asks to stop. `split_keys` and `approximate_split_keys` return the first non-empty result from checkers in registration order. `approximate_bucket_keys` uses approximate size to decide whether buckets should be generated, then uses a size checker to produce bucket boundaries.

`calc_split_keys_count` returns zero below `max_count_per_region`; above that it chooses the larger of rounded split-threshold division minus one and max-count division, capped by `batch_split_limit`.

## State And Persistence Behavior
`Host` only stores in-memory checkers for one split-check task. It does not persist, but its results drive later `AskSplit` or `RefreshRegionBuckets` scheduling in raftstore.

## Dependencies And Integration Points
Depends on `kvproto` split policies/reasons, shared `Config`, `Bucket`, `KeyEntry`, and coprocessor `SplitChecker` traits. It is constructed by `CoprocessorHost::new_split_checker_host` after registered split observers inspect a region.

## Risks
Only the first checker with non-empty split keys wins, so observer priority and checker order determine split behavior when several policies could split. `policy` escalates to approximate if any checker wants it, which can affect bucket-only checks. `calc_split_keys_count` uses floating-point rounding; tests protect expected ranges, but boundary behavior should be treated carefully.

## Test Signals
Tests live in child modules. They cover checker selection, split-key count math, scan versus approximate policies, bucket generation, table-boundary splitting, and range-property helper behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/size.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/size.rs

## Purpose
`size.rs` implements size-based split checking and approximate region-size helpers. It updates raftstore with approximate sizes, decides whether size or bucket checks are needed, and produces split keys by scan byte accounting or engine range properties.

## Important APIs, Types, And Functions
`Checker` tracks `max_size`, `split_size`, `current_size`, `split_keys`, `batch_split_limit`, and `policy`. `SizeCheckObserver<C>` owns a `StoreHandle`. `get_region_approximate_size` wraps `KvEngine::get_range_approximate_size`; `get_approximate_split_keys` wraps `KvEngine::get_range_approximate_split_keys` over encoded region bounds.

## Control Flow
`SizeCheckObserver::add_checker` reads approximate region size up to `region_max_size * batch_split_limit`. On failure it logs and adds a scan checker. On success it sends `UpdateApproximateSize`, observes the histogram, and adds a checker if the region exceeds max size or if region buckets are enabled and the region is at least two bucket sizes. Large regions switch policy to `Approximate` once above `region_size_threshold_for_approximate`; bucket-only checks can also prefer approximate.

During scans, `Checker::on_kv` adds `entry_size`, emits a split key when `current_size > split_size`, and preserves the current entry size when the previous total was exactly the split size. It can stop once batch limit is reached and enough size was scanned for the last part. `split_keys` removes the final key if the trailing part would be smaller than `max_size`. Approximate split mode computes split-key count via `calc_split_keys_count` and asks the engine for approximate keys.

## State And Persistence Behavior
State is per checker run. Persistent effects are indirect: approximate size updates and eventual split/bucket tasks sent through `StoreHandle`. The helper functions read engine properties but do not mutate engine state.

## Dependencies And Integration Points
Uses engine range properties across large column families, `StoreHandle`, split-check host/config, metrics, and raftstore split-check runner expectations. Size checking is registered by default before keys checking, which matters for scan reuse and policy escalation.

## Risks
Approximate range properties can be inaccurate for small, unflushed, compacting, or property-disabled data. Boundary handling around `current_size`, `split_size`, and final key popping is subtle and has regression tests. If approximate helpers error due to missing range properties, scan fallback protects split checking but may increase IO. `merge` of split results with bucket generation is order-sensitive because host returns the first non-empty checker result.

## Test Signals
Tests cover scan splits across CFs, approximate bucket generation for normal and MVCC keys, bucket policy selection, CF_LOCK without range properties, edge cases where max equals or doubles split size, approximate split-key errors and outputs, approximate size calculations, inaccurate subrange-size behavior, and a benchmark for approximate size.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/size.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/table.rs -->
# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/table.rs

## Purpose
`table.rs` implements table-boundary split checking. When enabled, it tries to split a region at TiDB table-prefix boundaries so a region spanning multiple tables can be separated.

## Important APIs, Types, And Functions
`Checker` stores the first table prefix, an optional split key, and policy. `TableCheckObserver` adds this checker when `Config::split_region_on_table` is enabled. Helpers include `last_key_of_region`, `to_encoded_table_prefix`, `is_table_key`, and `is_same_table`.

## Control Flow
`TableCheckObserver::add_checker` first skips if table splitting is disabled or the region start/end are in the same table. It reads the last key in `CF_WRITE` within the encoded region bounds. Based on how encoded start and last/end keys compare with TiDB's table prefix, it either skips non-table ranges, precomputes a split key, records the starting table prefix for scan-time detection, or adds a default scanner for short keys.

The scan `Checker::on_kv` converts the data key to origin key. If it has no first table prefix yet, the first table key can become a split key. If it has a prefix and sees a key from another table, it extracts that table prefix and stops. `split_keys` returns the precomputed or detected encoded table-prefix key once.

## State And Persistence Behavior
State is only per split-check run. It reads engine state through a write-CF iterator but does not mutate or persist data. Split execution is delegated to the surrounding split-check runner.

## Dependencies And Integration Points
Uses `engine_traits` iterators over `CF_WRITE`, TiDB table codec constants and prefix extraction, `txn_types::Key`, `KeyBuilder`, and split-check host traits. It is registered by default after size and keys observers, with table splitting gated by configuration.

## Risks
The logic assumes TiDB table key encoding and only inspects `CF_WRITE` for the last key. Non-table data, short keys, and ranges crossing table/non-table areas have special branches that can skip or force scans. Prefix comparison uses the first encoded table-prefix bytes, so any table key format change would require updates. Errors from iterator creation are logged and cause table splitting to be skipped.

## Test Signals
Tests verify `last_key_of_region` across open and bounded ranges and table-check behavior for ranges spanning table data, starting inside a table, ending before table data, crossing non-table prefixes, and skipping same-table ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/table.rs -->
