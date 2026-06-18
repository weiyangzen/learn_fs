# subset-b-008860 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/resource_group.rs -->
# sources/storage-engines/tikv/components/resource_control/src/resource_group.rs

## Purpose
This file is the central in-memory resource-control model for TiKV resource groups. It owns resource group metadata, read/write scheduling controllers, background/foreground limiters, virtual-time fairness, two-phase scheduling state, and admission-control delay accounting. It bridges PD-supplied `ResourceGroup` protobuf settings with TiKV scheduler priority metadata and runtime limiter state.

## Important APIs, Types, And Functions
`ResourceGroupManager` is the top-level registry. It stores `DashMap<String, ResourceGroup>`, a fast `group_count`, registered `ResourceController`s, shared priority limiters, a single shared background limiter, foreground RU trackers, and config via `VersionTrack<Config>`. `new` installs a default RU-mode group with medium priority and max RU quota. `add_resource_group`, `remove_resource_group`, and `retain` synchronize the manager registry and all derived controllers. `derive_controller` creates a read or write `ResourceController` and backfills existing groups.

`RuTracker` tracks per-group RU consumption in 30-second ring-buffer buckets. `record`, `advance`, `current_rate`, `historical_rate`, and `refresh_cached_historical_rate` support foreground admission control and two-phase scheduling. `ResourceLimiter` instances in `ru_trackers` are per foreground group and are created lazily by `record_ru_consumption` or `get_foreground_group_limiter`.

`AdmissionDecision` and `DelaySlotGuard` implement pre-pool admission control. `admission_decision` combines token-bucket debt with delayed-request caps and emits admission metrics; `delay_slot_guard` ensures delayed slots are released on cancellation.

`ResourceController` implements `yatp::queue::priority::TaskPriorityProvider`. It maps `TaskMetadata` and `CommandPri` to encoded priorities based on group priority, virtual time, command level, override priority, and optional two-phase baseline state. `GroupPriorityTracker` holds per-group RU quota, weight, virtual time, and `is_over_baseline`.

## Control Flow
PD/service code calls manager CRUD methods when resource-group config changes. Read/write pools call `derive_controller` and then use `priority_of`/`get_priority` for YATP scheduling. Work completion calls `consume_penalty` to advance virtual time. Foreground CPU measurement calls `record_ru_consumption`, while `online_adjust_resource_quota` periodically refreshes trackers, decides whether groups are above historical baseline, tightens or ramps CPU limits, emits metrics, and evicts idle trackers.

`advance_min_virtual_time` first updates two-phase group flags when fair scheduling is enabled, then asks each controller to rebalance virtual times. `update_min_virtual_time` raises lagging groups toward the max VT or subtracts `RESET_VT_THRESHOLD` near overflow.

Background control is selected through `get_background_resource_limiter_with_priority`: explicit background settings on a group win, otherwise non-default groups without background settings can fall back to the default group's configured background task types.

## State And Persistence Behavior
All state is process-local and rebuilt from PD/service config. Group names are lowercased in the manager. Background limiters are intentionally shared globally; removing the last background group resets shared limiter rates to infinity to avoid stale throttling. Foreground RU trackers are lazy and garbage-collected when idle. Virtual time is atomic per group but its global rebalance is approximate and intentionally not fully atomic because overflow/reset paths are rare.

## Dependencies And Integration Points
The file depends on `kvproto` resource-manager and RPC context types, `tikv_util::resource_control::{TaskMetadata, TaskPriority}`, YATP priority queues, `dashmap`, `parking_lot`, `VersionTrack<Config>`, and this crate's metrics and `ResourceLimiter`. It is driven by `service.rs` for PD config, `worker.rs` for periodic quota adjustment, and read/write execution paths that attach resource control metadata.

## Risks
Admission slots must be released exactly once; `DelaySlotGuard` mitigates this but callers using manual release remain sensitive. Two-phase scheduling depends on periodic worker ticks; stale `ru_trackers` or missed `online_adjust_resource_quota` calls leave phase state inaccurate. `historical_rate` intentionally dilutes missing buckets, so recently created groups can be throttled aggressively after spikes. The `Shared` background limiter design means all background groups affect each other. Several operations hold locks while iterating groups/controllers, so very large group counts could increase update latency.

## Test Signals
The inline tests cover resource group CRUD, priority encoding, virtual-time reset and overflow failpoints, retain behavior, background limiter selection/fallback, RU tracker bucket math, two-phase RU-based scheduling, foreground limiter retrieval, and admission delay/reject behavior. Worker and service tests further exercise manager integration with quota adjustment and PD meta-storage updates.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/resource_group.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/resource_limiter.rs -->
# sources/storage-engines/tikv/components/resource_control/src/resource_limiter.rs

## Purpose
This file wraps TiKV token-bucket limiters into a reusable `ResourceLimiter` abstraction for CPU, aggregate IO, and write-only IO throttling. It records consumption/wait statistics and exposes rate-limit controls used by background, priority, and foreground admission-control paths.

## Important APIs, Types, And Functions
`ResourceType` enumerates `Cpu` and `Io` and provides label strings. `ResourceLimiter::new` constructs CPU and IO `QuotaLimiter`s, a dedicated `write_io_limiter`, a version, a background flag, and optional priority wait histogram. `consume` charges CPU micros, read/write bytes, and optionally write-only IO; it returns the maximum wait duration and records priority wait metrics. `admission_delay` probes accumulated token-bucket debt with zero consumption and includes write IO debt for writes. `async_consume` sleeps on `GLOBAL_TIMER_HANDLE`.

`QuotaLimiter` wraps `tikv_util::time::Limiter`. `set_rate_limit` treats near-zero rates as infinity. `consume` and `consume_io` update total wait, byte counters, and request count. `GroupStatistics` snapshots limiter counters and supports saturating subtraction and division by elapsed seconds.

## Control Flow
Quota adjustment workers mutate limiter rates through `get_limiter(...).set_rate_limit` and `get_write_io_limiter`. Runtime request paths call `consume` either to build debt without waiting, to wait inline, or to query debt before entering a pool via `admission_delay`. Metrics are updated at consumption time and later read by workers/services via `get_limit_statistics`.

## State And Persistence Behavior
Limiter state is in-memory token-bucket state plus atomic counters. It is not persisted. `version` is included in statistics so reporters can detect limiter replacement. The same `ResourceLimiter` can be shared by multiple resource groups, especially the global background limiter.

## Dependencies And Integration Points
The limiter depends on `file_system::IoBytes`, `tikv_util::time::Limiter`, Prometheus histograms, `GLOBAL_TIMER_HANDLE`, and `TaskPriority`. `resource_group.rs` owns manager-level limiter selection; `worker.rs` adjusts rates; `service.rs` reports background consumption; execution paths consume against the returned limiter.

## Risks
Zero and extremely small rates are normalized to infinity, so callers cannot express a complete stop with `0`. `admission_delay` increments request counters even on zero probes when rates are finite, which is useful for stats but can surprise metric consumers. Write IO pressure is separate from aggregate IO only when callers pass `skip_compaction_pressure = false`.

## Test Signals
This file has no local test module, but its behavior is heavily exercised by `resource_group.rs` admission tests, `worker.rs` background/priority limiter tests, and service background RU reporting tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/resource_limiter.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/service.rs -->
# sources/storage-engines/tikv/components/resource_control/src/service.rs

## Purpose
`service.rs` connects the in-memory `ResourceGroupManager` to PD metadata and reporting RPCs. It loads and watches resource-group definitions from meta storage, loads RU controller cost configuration, and periodically reports background RU consumption to PD.

## Important APIs, Types, And Functions
`ResourceManagerService` owns the manager, an `RpcClient`, a checked/sourced meta-storage client, and the latest watch revision. `new` wires meta storage to the resource-control source. `watch_resource_groups` performs initial reload, then starts a prefixed watch from the stored revision and applies put/delete events. `reload_all_resource_groups` performs a full prefixed get, parses protobuf groups, adds valid groups, retains only groups still present, and updates `revision`.

`load_controller_config` repeatedly reads `RESOURCE_CONTROL_CONTROLLER_CONFIG_PATH` and parses `ControllerConfig` JSON into `RequestUnitConfig`. `report_ru_metrics` samples the shared background limiter every five seconds, computes deltas from the last report, converts CPU and IO usage to RRU/WRU using controller config, and calls `pd_client.report_ru_metrics`.

## Control Flow
Startup calls `watch_resource_groups`, which first reconciles all current groups and then watches for incremental changes. Watch compaction triggers a full reload. Transient errors sleep for `RETRY_INTERVAL` and restart the watch. Reporting waits until background groups exist, then reads limiter statistics, skips unchanged samples, builds a `TokenBucketsRequest` under the default resource group with `is_background = true`, and sends it to PD.

## State And Persistence Behavior
Persistent source of truth is PD meta storage. Local service state is only the last watch revision and previous background statistic snapshot. The report loop resets nothing in the limiter; it sends deltas by subtracting previous cumulative counters and resets its baseline when the limiter version changes.

## Dependencies And Integration Points
The file integrates with `pd_client` meta storage and RPC reporting, `kvproto` resource-manager messages, serde JSON controller config, `GLOBAL_TIMER_HANDLE` delays, and `ResourceGroupManager`. Background limiter statistics come from `resource_limiter::GroupStatistics`.

## Risks
The watch loop is intentionally infinite; bad data logs parse errors but leaves previous valid local state until a retain pass. `load_controller_config` blocks forever until valid config exists. Reporting all background consumption under `DEFAULT_RESOURCE_GROUP_NAME` matches the shared-limiter design but loses per-background-group attribution. Delta subtraction assumes monotonic counters and handles limiter replacement only through `version`.

## Test Signals
Tests use mock PD meta storage to validate CRUD reload, watch put/delete updates, watch-server reboot recovery, controller config loading, and background RU reporting with failpoint-shortened report intervals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/service.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/worker.rs -->
# sources/storage-engines/tikv/components/resource_control/src/worker.rs

## Purpose
`worker.rs` contains periodic adaptive quota workers for resource control. It samples process CPU and IO usage, adjusts the global background limiter, adjusts foreground per-group admission-control limits, applies compaction-pressure write IO throttling, and manages priority-class CPU limiters.

## Important APIs, Types, And Functions
`ResourceStatsProvider` abstracts system sampling. `SysQuotaGetter` implements it with process CPU stats, `SysQuota::cpu_cores_quota`, `fetch_io_bytes`, and configured IO bandwidth.

`GroupQuotaAdjustWorker` drives background and foreground control. `adjust_quota` enforces a minimum one-second interval, reads CPU once, calls `background_adjust_quota`, then feeds CPU utilization to `ResourceGroupManager::online_adjust_resource_quota`. Background adjustment caps configured utilization at `fg_cpu_throttle_threshold`, linearly scales from target to a floor between `bg_cpu_throttle_threshold` and foreground threshold, only tightens while under pressure, and recovers by 10 percent when idle. It also updates background metrics and the manager's `bg_cpu_at_floor` flag. `adjust_write_io_by_compaction_pressure` controls the write-only IO limiter between configured floor and ceiling.

`PriorityLimiterAdjustWorker` adjusts medium/low priority CPU limiters. It fast-paths single-group and low-CPU cases to infinity, derives per-priority CPU and wait stats, reserves high priority, and assigns remaining quota to lower priorities according to `priority_ctl_strategy`.

## Control Flow
External scheduling invokes workers periodically, nominally every `QUOTA_ADJUST_DURATION`. The background worker uses cumulative limiter stats to compute per-second background consumption and system utilization. Foreground throttling occurs only after background CPU is at its floor. Priority adjustment reads limiter and YATP wait histograms, then sets CPU rate limits on priority limiters.

## State And Persistence Behavior
Worker state is in-memory: last adjustment time, previous limiter statistics, previous background presence, histogram baselines, and last low/single-group flags. It does not persist across restart. When no background groups exist, background is considered at floor so foreground logic may proceed without waiting for background squeezing.

## Dependencies And Integration Points
The file depends on `file_system` IO counters, `tikv_util` process stats, system quota, thread names, YATP metrics, Prometheus metrics from this crate, `ResourceGroupManager`, and `ResourceLimiter`. It is the periodic companion to `resource_group.rs` and the source of dynamic rate-limit changes used by runtime request paths.

## Risks
Quota behavior is sensitive to sampling interval and process-stat accuracy. IO utilization uses bytes since last sample and returns zero if sampled too frequently. Background recovery is intentionally gradual and only occurs under low utilization, so stale throttling can persist after load drops. Shared background limiter semantics mean all background groups are globally throttled. Priority logic assumes YATP histograms are registered for the named pools/priorities.

## Test Signals
Tests cover background limiter adjustment, infinite-RU foreground groups with background throttling, priority limiter adjustment, tiered load shedding, compaction-pressure write IO throttling, and the invariant that multiple background groups share one global budget rather than splitting it.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_control/src/worker.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/Cargo.toml -->
# sources/storage-engines/tikv/components/resource_metering/Cargo.toml

## Purpose
This manifest defines the `resource_metering` crate, a TiKV component for tagging request execution, collecting resource records, aggregating them, and reporting usage.

## Important APIs, Types, And Functions
The manifest sets package metadata (`name`, `version`, Rust 2021 edition, Apache-2.0) and declares dependencies needed by the public modules: `kvproto` for usage protobufs, `tikv_util` worker/sys/config helpers, `prometheus` metrics, `online_config`, `grpcio`, `futures`, `pin-project`, `pdqselect`, `collections`, `crossbeam`, serde, and logging crates. It also declares a `test-recorder` integration test at `tests/recorder_test.rs` and `rand` as a dev dependency.

## Control Flow
Cargo uses this file to compile the library and integration test. The dependency set supports the flows in `lib.rs`, `model.rs`, recorder, and reporter modules: async wrapping, thread-local registration, online config dispatch, top-K selection, metrics registration, and RPC/report data structures.

## State And Persistence Behavior
The manifest has no runtime state. Its dependency versions and workspace links determine build-time resolution and feature compatibility.

## Dependencies And Integration Points
Workspace dependencies keep the crate aligned with the surrounding TiKV tree. The explicit Prometheus `nightly` feature and `pin-project` match code usage in metrics and `InTags`. The integration test target signals recorder behavior is tested outside the unit-test modules covered here.

## Risks
The crate uses `#![feature(core_intrinsics)]` in `lib.rs`, so compiler/channel compatibility is coupled to TiKV's toolchain. Dependency drift in workspace crates can affect public re-exports and reporter/recorder internals even though this manifest is small.

## Test Signals
The manifest's direct test signal is `[[test]] name = "test-recorder"`, plus unit tests in the crate source files.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/collector.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/collector.rs

## Purpose
`collector.rs` defines the handoff trait between record-producing code and reporting/scheduling code in resource metering.

## Important APIs, Types, And Functions
`Collector` is a `Send` trait with one method, `collect(&self, records: Arc<RawRecords>)`. It deliberately accepts an `Arc<RawRecords>` so the recorder can pass aggregated data without transferring ownership through a concrete implementation type.

## Control Flow
Recorder-side code collects raw measurements and passes them to registered collectors. Implementations usually schedule reporter work, but the trait itself stays minimal and does not encode scheduling, batching, or upload policy.

## State And Persistence Behavior
The trait owns no state. State lives in implementors and in the `RawRecords` payload.

## Dependencies And Integration Points
It depends only on `Arc` and `crate::RawRecords`. `collector_reg.rs` registers `Box<dyn Collector>` instances with the recorder. Reporter modules implement or consume this trait to bridge to upload pipelines.

## Risks
Because `Collector` is only `Send`, not `Sync`, callers must respect the recorder's scheduling model rather than sharing trait objects arbitrarily. `collect` has no result, so implementations must handle/report failures internally.

## Test Signals
There are no local tests. Registration and recorder integration are exercised through recorder tests and `CollectorRegHandle` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/collector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/config.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/config.rs

## Purpose
`config.rs` defines public resource-metering configuration, validation rules, global network-IO collection state, and online config dispatch to recorder/reporter components.

## Important APIs, Types, And Functions
`Config` is `Serialize`, `Deserialize`, `PartialEq`, and derives `OnlineConfig`. Fields include `receiver_address`, `report_receiver_interval`, `max_resource_groups`, `precision`, and `enable_network_io_collection`. Defaults use no receiver, one-minute reporting, 100 max groups, one-second precision, and network/logical IO collection disabled.

`validate` checks optional receiver address syntax, precision between 100 ms and one hour, `max_resource_groups <= 5000`, and report interval between 500 ms and `precision * 500`. `ENABLE_NETWORK_IO_COLLECTION` is a global `AtomicBool` initialized from the default. `ConfigManager` holds current config and notifiers; `dispatch` applies an online change, validates it, notifies address changes, then notifies recorder and reporter.

## Control Flow
Online config changes arrive as `ConfigChange`. Dispatch clones current config, applies the change through generated `update`, validates the candidate, emits address notification if needed, sends the full new config to recorder and reporter notifiers, and commits it as current.

## State And Persistence Behavior
`ConfigManager` stores the current in-memory config. The global `ENABLE_NETWORK_IO_COLLECTION` is atomic process state consumed by collection paths elsewhere. Persistent storage is external to this file.

## Dependencies And Integration Points
The file integrates with `online_config`, serde, `tikv_util::config::ReadableDuration`, recorder and reporter config notifiers, and `AddressChangeNotifier` from reporter single-target code.

## Risks
Validation error messages say "between 0 and MAX" for max groups but only enforces an upper bound. Dispatch notifies recorder/reporter after address notification; downstream notifier failures are not represented in this API. Global atomic state can diverge from `ConfigManager.current_config` if other modules update it independently.

## Test Signals
`test_config_validate` covers default validation, valid address/config, too-large reporting interval, too-large group count, and invalid precision.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/config.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/error.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/error.rs

## Purpose
This file defines the crate-wide result alias for resource metering.

## Important APIs, Types, And Functions
`pub type Result<T> = std::result::Result<T, Box<dyn std::error::Error + Sync + Send>>;` standardizes fallible APIs on boxed thread-safe errors.

## Control Flow
There is no control flow beyond type aliasing. Callers can return any error implementing `Error + Send + Sync + 'static` through `?` conversions where available.

## State And Persistence Behavior
No runtime state or persistence.

## Dependencies And Integration Points
The alias depends only on the standard library and is intended for use across recorder/reporter/client modules that need heterogeneous errors.

## Risks
Boxed dynamic errors erase concrete error types, which simplifies APIs but can make matching/recovery harder.

## Test Signals
No local tests are needed for the alias.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/lib.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/lib.rs

## Purpose
`lib.rs` is the public surface of the `resource_metering` crate. It re-exports collector/config/model/recorder/reporter APIs and implements request tagging wrappers that attach resource metering context to futures and streams through thread-local storage.

## Important APIs, Types, And Functions
`ResourceMeteringTag` holds `Arc<TagInfos>` and a `ResourceTagFactory`. `attach` registers thread-local storage with the recorder if needed, rejects nested attachments in debug builds, stores the tag in `STORAGE`, resets the per-request summary record, and returns a `Guard`.

`Guard::drop` clears the attached tag, optionally merges summary metrics into `summary_records`, ignores disabled summaries and empty extra tags, drops zero-read/logical records, and caps retained summary maps at `MAX_SUMMARY_RECORDS_LEN`.

`ResourceTagFactory` creates tags from RPC context, optionally with key ranges, and registers thread-local `LocalStorageRef`s with the recorder scheduler. `FutureExt` and `StreamExt` wrap async work in `InTags<T>`, whose `poll`/`poll_next` attaches the tag for the duration of each poll. `TagInfos` extracts store, peer, region, key ranges, and resource group tag bytes from `kvproto::kvrpcpb::Context`.

## Control Flow
Callers create a tag from request context, then call `.in_resource_metering_tag(tag)` on a future or stream. Each poll attaches the tag to thread-local storage, allowing recorder sampling to attribute CPU and summary counters to the current request. When the poll returns, the guard drops and clears the tag while aggregating summary counters.

## State And Persistence Behavior
State is thread-local in recorder `STORAGE`, plus shared summary maps protected by `Mutex`. Registration retries are capped by `MAX_THREAD_REGISTER_RETRY`. The crate does not persist data directly; reporter/recorder modules handle downstream transport.

## Dependencies And Integration Points
This file integrates with recorder registration, reporter data sinks/pubsub/single-target APIs, `kvproto` contexts, `tikv_util::worker::Scheduler`, `thread::thread_id`, `HeapSize`, `pin-project`, and `core_intrinsics::unlikely`.

## Risks
Nested attachment is only debug-asserted and returns a guard without replacing the tag, so nested async instrumentation can silently skip attribution in release builds. `SharedTagInfos::load_full` in local storage uses swap-based access, so guard drop spin-waits until the tag is available. Summary maps are capped to prevent unbounded growth if recorder cleanup fails, which means new tags can be dropped under high cardinality.

## Test Signals
`test_attach` creates a thread-local tag, verifies it is visible during attachment, and verifies the tag is cleared after guard drop.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/metrics.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/metrics.rs

## Purpose
`metrics.rs` declares Prometheus metrics for resource metering recorder/reporter activity.

## Important APIs, Types, And Functions
The file uses `lazy_static!` to register `STAT_TASK_COUNT`, `REPORT_DURATION_HISTOGRAM`, `REPORT_DATA_COUNTER` labeled by `type`, and `IGNORED_DATA_COUNTER` labeled by `type`.

## Control Flow
Metrics are registered at first use. Other modules increment stat task counts, observe reporting duration, count reported data, and count ignored data.

## State And Persistence Behavior
Metric state is global process state in Prometheus collectors. There is no local persistence.

## Dependencies And Integration Points
It depends on `lazy_static` and `prometheus`. Recorder and reporter modules consume these metrics to expose observability for collection and upload behavior.

## Risks
Registration uses `unwrap`, so duplicate metric names or registry failures panic during initialization. Metric names are global to the process and must stay unique.

## Test Signals
No local tests. Runtime metric registration and use are indirectly covered by recorder/reporter tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/model.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/model.rs

## Purpose
`model.rs` defines the core data model and aggregation algorithms for resource metering. It represents raw sampled usage, groups records by resource tag or region, selects top resource consumers, rolls the rest into "others", and converts internal structures into `kvproto` usage records.

## Important APIs, Types, And Functions
`RawRecord` stores CPU time, per-pool CPU time, read/write keys, logical IO, and network bytes. `add_cpu_time`, `merge`, and `merge_summary` update it. `RawRecords` is a time-windowed map from `Arc<TagInfos>` to `RawRecord` and can aggregate by extra tag or by extra tag plus region.

`find_kth_cpu_time`, `find_kth_values`, `get_iter_for_cpu_time`, and `get_iter_for_cpu_network_io` implement top-N selection using thread-local reusable buffers and `pdqselect`. `handle_records_impl` appends selected records and merges unselected records to "others", optionally considering network/logical IO as well as CPU.

`Record` stores per-timestamp vectors and validates aligned lengths before conversion. `Records` stores tag-keyed records plus timestamp-keyed others and converts into `ResourceUsageRecord` with `GroupTagRecord`. `RegionRecords` mirrors this for region IDs and `RegionRecord`. `SummaryRecord` provides atomic counters for request summaries, with clone, reset, merge, and take-and-reset operations. `RegionCpuRecord` accumulates total and per-pool CPU into region-level records.

## Control Flow
Recorder produces `RawRecords` for a sampling window. Reporter aggregates by tag and region, selects top groups up to configured limits, appends selected values by timestamp, merges unselected values into `others`, and finally converts accumulated records into protobuf messages for upload. Summary counters from thread-local request guards can be merged into raw records before final aggregation.

## State And Persistence Behavior
Aggregation state is in memory. `Records` and `RegionRecords` retain per-tag/per-region vectors until cleared. `SummaryRecord` fields are atomics so request paths can update counters cheaply and safely. Thread-local buffers reduce repeated allocation during top-K selection but require correct clear/set discipline.

## Dependencies And Integration Points
The model depends on `collections::HashMap`, `kvproto::resource_usage_agent` messages, `pdqselect`, `Arc<TagInfos>`, and `tikv_util::warn`. It is used by recorder, collector, and reporter modules and by public re-exports from `lib.rs`.

## Risks
Top-N selection uses strict `>` comparisons against kth values, so ties at the threshold are rolled into "others"; this is intentional and covered by an issue regression test but can return fewer than N explicit records. Conversion skips invalid `Record` vector shapes after logging. Accumulators use integer addition without saturation in several paths, so extreme long-running accumulations could overflow if not periodically cleared. Thread-local reusable buffers make selection efficient but not reentrant within a thread.

## Test Signals
Tests cover `SummaryRecord` operations, tag aggregation, top-K CPU selection, tie handling for issue 12234, aggregation by repeated extra tags, aggregation by region, and top-K selection across CPU/network/logical IO.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/model.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/collector_reg.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/recorder/collector_reg.rs

## Purpose
`collector_reg.rs` implements registration and RAII deregistration of resource-metering collectors with the recorder worker.

## Important APIs, Types, And Functions
`CollectorRegHandle` wraps a `Scheduler<Task>`. `register` assigns a monotonically increasing `CollectorId`, schedules `Task::CollectorReg(CollectorReg::Register { ... })`, and returns a `CollectorGuard`. `new_for_test` builds a mock worker scheduler. `CollectorReg` is the recorder task payload for register/deregister operations. `CollectorGuard::drop` schedules deregistration if registration scheduling succeeded.

## Control Flow
Clients call `register(Box<dyn Collector>, as_observer)`. Non-observer collectors keep the recorder enabled, while observer collectors do not affect enabled state. When the guard is dropped, the recorder receives a deregister task for the same ID.

## State And Persistence Behavior
Collector IDs come from a static `AtomicU64` with sequential consistency. Guard state is just the ID and optional scheduler. Registration state itself lives in the recorder worker, not in this file.

## Dependencies And Integration Points
The file depends on `tikv_util::worker::{Scheduler, Worker}`, logging via `warn`, the `Collector` trait, and recorder `Task`. It is re-exported from `lib.rs` for external collector registration.

## Risks
If scheduling the register task fails, the returned guard has no scheduler and cannot deregister anything. Deregistration errors are logged only. ID allocation is process-local and monotonic; wraparound is theoretically possible but unrealistic.

## Test Signals
No local tests, but `new_for_test` supports recorder tests and integration tests around collector registration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/collector_reg.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/localstorage.rs -->
# sources/storage-engines/tikv/components/resource_metering/src/recorder/localstorage.rs

## Purpose
`localstorage.rs` defines the thread-local storage used by resource metering to associate currently polled work with a resource tag and per-thread summary counters.

## Important APIs, Types, And Functions
`STORAGE` is a thread-local `RefCell<LocalStorage>`. `LocalStorage` tracks registration status, failed register attempts, whether a tag is currently set, the shared attached tag, whether summaries are enabled, current summary record, and a shared map of summary records keyed by `Arc<TagInfos>`.

`LocalStorageRef` packages a thread `Pid` with a clone of its `LocalStorage` for recorder registration. `SharedTagInfos` wraps `Arc<AtomicCell<Option<Arc<TagInfos>>>>` and provides `new`, `swap`, and `load_full`. `load_full` temporarily swaps the tag out, clones it, then restores it.

## Control Flow
`ResourceMeteringTag::attach` mutates the thread-local `LocalStorage`, and the recorder registers `LocalStorageRef`s so background sampling can inspect per-thread tags and summaries. `Guard::drop` clears the tag and merges summaries through the same storage.

## State And Persistence Behavior
State is thread-local plus shared `Arc` fields cloned into recorder-visible references. Summary maps are protected by `Mutex`; tag access is lock-free through `AtomicCell<Option<Arc<TagInfos>>>`. Nothing is persisted.

## Dependencies And Integration Points
The file depends on `collections::HashMap`, `crossbeam::atomic::AtomicCell`, `tikv_util::sys::thread::Pid`, `TagInfos`, and `SummaryRecord`. It is a private recorder support module used by `lib.rs` and recorder internals.

## Risks
`SharedTagInfos::load_full` uses swap/restore and asserts that no other value appears during restoration. Misuse outside the expected recorder/guard coordination could panic or cause spinning in `Guard::drop`. Cloning `LocalStorage` shares the summary arcs, so ownership boundaries must be understood by recorder code.

## Test Signals
No local tests, but `lib.rs::test_attach` validates basic attached-tag visibility and cleanup through this storage.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/localstorage.rs -->
