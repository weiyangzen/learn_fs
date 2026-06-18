# subset-b-008861 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/mod.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/recorder/mod.rs

Purpose: owns the resource metering recorder worker. It drives a vector of `SubRecorder`s at a fixed 99 Hz timer, receives thread/collector/config registration tasks, and periodically emits `RawRecords` to registered collectors.

Important APIs/types/functions: `Recorder`, `RecorderBuilder`, `Task`, `ConfigChangeNotifier`, and `init_recorder`. The module also re-exports collector registration handles, local storage, `CpuRecorder`, `SummaryRecorder`, and the public summary counter functions. `Recorder::tick` runs each sub-recorder’s `tick`, then calls `collect` once the configured precision window elapses. `pause`, `resume`, and `cleanup` bracket active collection and remove dead-thread state.

Control flow: the worker handles `CollectorReg`, `ThreadReg`, and `ConfigChange` tasks through `Runnable::run`; timer ticks call `on_timeout`. If no non-observer collectors are present, the recorder pauses and observers alone do not keep sampling active. When resumed, records and timestamps reset before sub-recorders resume.

State/persistence: state is in-memory only: `RawRecords`, per-thread `LocalStorage`, collector maps, observer maps, and timing instants. Cleanup checks live OS thread ids, shrinks oversized record capacity, and delegates cleanup to sub-recorders. No durable persistence is performed.

Dependencies/integration: uses `tikv_util::worker`, thread ids/stats, `ResourceTagFactory`, resource metering config, and the global `ENABLE_NETWORK_IO_COLLECTION` flag. `init_recorder` is consumed by the server startup path and returns the handles needed by storage, reporter, and config management.

Risks: record delivery is best-effort through worker scheduling; dead thread cleanup depends on platform thread id discovery; observers are intentionally passive; CPU/summary precision depends on timer scheduling. A high `records.records` churn pattern can allocate until periodic shrink.

Test signals: inline tests cover pause/resume, thread registration, collector/observer semantics, record dispatch, and deregistration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/cpu.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/cpu.rs

Purpose: implements CPU usage sampling as a `SubRecorder`. It attributes per-thread CPU deltas to the currently attached resource tag.

Important APIs/types/functions: `CpuRecorder`, private `ThreadStat`, and `detect_thread_pool_type`. `thread_created` records the thread’s shared attached tag reference, initial stat, and detected pool type. `tick` reads current thread CPU stats, computes deltas from the previous sample, and calls `RawRecord::add_cpu_time` with the pool classification.

Control flow: each recorder tick iterates known thread stats, skips threads without an attached tag, reads current stats from `tikv_util::sys::thread`, increments `STAT_TASK_COUNT`, and updates the stored baseline. `resume` resets baselines to avoid charging paused time.

State/persistence: keeps an in-memory `HashMap<Pid, ThreadStat>`. `cleanup` retains only thread ids still present in recorder local-storage state and shrinks capacity above a threshold.

Dependencies/integration: depends on thread stat APIs, `THREAD_NAME_HASHMAP`, scheduler/unified read pool name matching, `RawRecords`, `ThreadPoolType`, and local storage shared tag state. Its output feeds reporter aggregation through raw record CPU fields.

Risks: CPU accounting is approximate and platform-specific; missing or stale thread names classify as `Unknown`; stat read failures skip samples; `u32` millisecond deltas can lose precision or saturate elsewhere depending on record merge behavior.

Test signals: platform-gated tests verify that CPU-heavy work under an attached tag creates records on Linux/macOS and that unsupported platforms leave records empty.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/cpu.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/mod.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/mod.rs

Purpose: defines the extension contract for resource-specific recorders driven by `Recorder`.

Important APIs/types/functions: the `SubRecorder: Send` trait with hooks `tick`, `collect`, `cleanup`, `pause`, `resume`, and `thread_created`. It exposes `cpu` and `summary` implementations as submodules.

Control flow: `Recorder` invokes these hooks from its timer and task handlers. Most methods default to no-op, letting implementations opt into sampling, batch collection, lifecycle switching, or thread registration.

State/persistence: the trait itself stores no state. It passes mutable access to shared in-memory `RawRecords` and the `HashMap<Pid, LocalStorage>` representing known threads.

Dependencies/integration: depends on `tikv_util::sys::thread::Pid`, `collections::HashMap`, `RawRecords`, and `LocalStorage`. Implementations are boxed in `RecorderBuilder` and run sequentially on the recorder worker thread.

Risks: implementations share mutable `RawRecords`; a slow sub-recorder delays all sampling. Default no-op hooks make missing lifecycle handling easy if a new resource recorder needs enable/disable propagation.

Test signals: behavior is indirectly tested by recorder tests with a mock `SubRecorder`, CPU recorder tests, and summary integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/summary.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/summary.rs

Purpose: records explicit per-request summary counters such as read/write keys, network bytes, and logical IO bytes from thread-local resource metering context.

Important APIs/types/functions: public functions `record_read_keys`, `record_write_keys`, `record_network_in_bytes`, `record_network_out_bytes`, `record_logical_read_bytes`, and `record_logical_write_bytes`; `SummaryRecorder` implements `SubRecorder`. Network/logical byte functions are gated by `ENABLE_NETWORK_IO_COLLECTION`.

Control flow: public record functions update atomics in `STORAGE` for the current thread. On `collect`, the recorder drains each thread’s completed `summary_records`, merges them into `RawRecords`, separately snapshots the currently attached tag’s live `summary_cur_record`, and propagates the enabled switch to local storage.

State/persistence: all counters are in thread-local/in-memory local storage. `pause` clears per-thread `summary_enable`; `resume` sets it; `thread_created` initializes new thread state from the recorder’s current enabled flag.

Dependencies/integration: integrated with local storage, global network collection config, and raw record summary merge methods. The reporter later aggregates these summary fields by resource tag or region.

Risks: byte counters are silently dropped when network IO collection is disabled; current-record collection requires non-empty `extra_attachment`; lock contention is possible around per-thread summary maps; enable state only reaches threads during collect/thread creation.

Test signals: summary integration tests verify no data before a data sink activates collection, correct read/write key reporting while active, and no data after the sink unregisters.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/recorder/sub_recorder/summary.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/collector_impl.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/collector_impl.rs

Purpose: adapts the recorder-side `Collector` trait into reporter worker tasks.

Important APIs/types/functions: `CollectorImpl::new` and `impl Collector for CollectorImpl`. `collect` wraps incoming `Arc<RawRecords>` in `Task::Records` and schedules it on the reporter scheduler.

Control flow: recorder invokes `collect`; scheduler success hands the batch to `Reporter::handle_records`; scheduler failure increments `IGNORED_DATA_COUNTER` with label `collect` and logs a warning.

State/persistence: stores only a scheduler clone. No durable persistence; dropped batches are not retried.

Dependencies/integration: depends on `tikv_util::worker::Scheduler`, reporter `Task`, `RawRecords`, the resource metering `Collector` trait, and metrics.

Risks: scheduling failure loses an entire raw-record batch. Backpressure is represented only by metric increments and warning logs.

Test signals: reporter tests indirectly exercise this adapter through reporter registration; recorder tests use mock collectors rather than this concrete type.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/collector_impl.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink.rs

Purpose: defines the output abstraction for sending aggregated resource usage records to a remote or local consumer.

Important APIs/types/functions: `DataSink: Send` with `try_send(&mut self, Arc<Vec<ResourceUsageRecord>>) -> Result<()>`.

Control flow: reporter upload methods call `try_send` for each registered sink. Implementations decide whether to enqueue, stream, or fail the batch.

State/persistence: trait has no state; implementations hold queues, schedulers, grpc clients, or streams. Calls are best-effort and errors are handled by callers with logging/metrics.

Dependencies/integration: depends on `kvproto::resource_usage_agent::ResourceUsageRecord` and crate error `Result`. Implemented by pubsub and single-target sinks.

Risks: the interface has no async completion or retry contract; `try_send` failure means caller-side drop. Mutable access serializes per-sink sends inside the reporter worker.

Test signals: summary and reporter tests define mock `DataSink` implementations to validate reporting behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink_reg.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink_reg.rs

Purpose: provides RAII registration for reporter `DataSink`s.

Important APIs/types/functions: `DataSinkRegHandle`, `DataSinkId`, `DataSinkReg`, and `DataSinkGuard`. `register` allocates a monotonically increasing id, schedules `Task::DataSinkReg(Register)`, and returns a guard that deregisters on drop.

Control flow: caller registers a boxed sink through the reporter scheduler. If scheduling succeeds, the guard retains the scheduler; if it fails, it logs and returns a guard that does not deregister.

State/persistence: only an atomic process-local id counter and guard-held scheduler. Reporter owns the actual sink map.

Dependencies/integration: used by `SingleTargetDataSink` and `PubSubService`; consumed by `Reporter::handle_data_sink_reg` to start/stop recorder collection based on active sinks.

Risks: registration scheduling failure is non-fatal and produces an inert guard; id counter never reuses ids; deregistration is best-effort during drop and can fail during shutdown.

Test signals: reporter tests directly schedule data-sink registration/deregistration tasks; summary tests exercise guard drop behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/data_sink_reg.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/mod.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/mod.rs

Purpose: owns the reporter worker that aggregates raw recorder batches into protobuf `ResourceUsageRecord`s and uploads them to registered data sinks.

Important APIs/types/functions: `Reporter`, `Task`, `ConfigChangeNotifier`, and `init_reporter`. Key methods are `handle_records`, `handle_data_sink_reg`, `upload_grouptag_record`, `upload_region_record`, `upload`, and `reset`.

Control flow: `Task::Records` aggregates by extra tag; when network IO collection is enabled, it also aggregates by region. Timer ticks upload group-tag records and optional region records at `report_receiver_interval`. First registered data sink registers a recorder collector; removing the last data sink drops that collector and pauses recorder sampling.

State/persistence: keeps in-memory `Records`, `RegionRecords`, data sink map, config, and optional `CollectorGuard`. Upload uses `std::mem::take` to reset accumulated records whether sinks succeed or fail.

Dependencies/integration: depends on recorder collector registration, `CollectorImpl`, data sink registration, aggregation helpers, config, kvproto records, worker timers, and metrics/logging through sink implementations.

Risks: upload failures drop current aggregates after logging; a hard limit of 10 sinks rejects excess sinks; config changes replace config wholesale; worker name reuses recorder thread prefix, which can complicate thread-level attribution.

Test signals: inline tests cover interval config, basic upload, multiple sinks, deregistration, and network-enabled region reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/pubsub.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/pubsub.rs

Purpose: exposes resource metering records through the `ResourceMeteringPubSub` gRPC streaming API.

Important APIs/types/functions: `PubSubService::new`, `impl ResourceMeteringPubSub for PubSubService`, and private `DataSinkImpl`. `subscribe` registers a bounded channel-backed sink and spawns an async task to forward record batches to the streaming response.

Control flow: on subscription, a channel of capacity 1 is created. Reporter calls `DataSinkImpl::try_send`; the gRPC task receives batches, records metrics, sends each `ResourceUsageRecord`, and exits on channel close or send error. The registration guard lives inside the async task, deregistering when the stream ends.

State/persistence: per-subscriber in-memory bounded channel and guard. No replay or durable storage.

Dependencies/integration: integrates kvproto pubsub service, grpcio server streaming, futures mpsc, `DataSinkRegHandle`, `DataSink`, and report/ignored/duration metrics.

Risks: backpressure drops whole batches because the channel capacity is one; slow or broken subscribers terminate their stream; each record is cloned before send.

Test signals: no direct tests in this file; behavior is indirectly covered through reporter/data-sink abstractions.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/pubsub.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/single_target.rs -->
## sources/storage-engines/tikv/components/resource_metering/src/reporter/single_target.rs

Purpose: implements the default data sink that reports resource usage records to a single configured remote `ResourceUsageAgent` gRPC endpoint.

Important APIs/types/functions: `SingleTargetDataSink`, `Task`, `AddressChangeNotifier`, `Limiter`, `Guard`, and `init_single_target`. Private `DataSinkImpl` schedules incoming batches onto the single-target worker.

Control flow: `update_data_sink` registers or resets the reporter sink based on address. `handle_records` enforces one in-flight report with `Limiter`, lazily builds a grpc client, starts `report_opt` with a two-second timeout, and spawns async sends for each record followed by stream close and response wait.

State/persistence: keeps scheduler, registration guard, grpc environment/client, limiter state, and current address. Address changes clear the client; empty address resets registration.

Dependencies/integration: registered through `DataSinkRegHandle`, uses kvproto `ResourceUsageAgentClient`, grpcio channel/call options, futures `SinkExt`, worker scheduling, and reporting metrics.

Risks: batches are dropped if a previous report is still running, no address is configured, grpc call setup fails, or scheduler enqueue fails. The limiter is released only when the async task drops its guard, so stuck grpc work can block later reports.

Test signals: no direct tests here; reporter tests use mock sinks, while server startup wires this sink into resource metering config.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/src/reporter/single_target.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/tests/recorder_test.rs -->
## sources/storage-engines/tikv/components/resource_metering/tests/recorder_test.rs

Purpose: integration tests for CPU recorder attribution through real thread-local resource tags and the public `init_recorder` path.

Important APIs/types/functions: `Operation`, `Operations`, `DummyCollector`, and `merge`. Operations model context attach/detach, CPU-heavy work, and sleeping; `DummyCollector` merges collected records by resource group tag bytes.

Control flow: tests start a recorder, register a collector, spawn workload threads with attached resource tags from `ResourceTagFactory`, join them, then wait for collection and compare expected CPU time within drift.

State/persistence: test-only in-memory expected maps and collected maps behind `Arc<Mutex<_>>`. No filesystem or durable state.

Dependencies/integration: uses `resource_metering::{init_recorder, Collector, RawRecords}`, kvproto context resource group tags, and platform thread CPU stats. Tests are gated to Linux/macOS.

Risks: CPU-time tests are timing-sensitive; `MAX_DRIFT` of 200 ms and post-work sleep reduce flakiness but do not eliminate scheduler variance. Unsupported platforms skip the module.

Test signals: covers heavy CPU, sleeping, mixed work, single-thread and multi-thread attribution, context reset behavior, and merge behavior across tags.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/tests/recorder_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/tests/summary_test.rs -->
## sources/storage-engines/tikv/components/resource_metering/tests/summary_test.rs

Purpose: integration test for summary counter flow from thread-local recording through recorder, reporter, and a registered `DataSink`.

Important APIs/types/functions: `MockDataSink`, `test_summary`, constants `PRECISION_MS` and `REPORT_INTERVAL_MS`. The sink stores latest records by resource group tag.

Control flow: the test starts recorder and reporter, verifies counters are not emitted before a sink registers, registers the sink, records read/write keys under a tag and verifies sums after report interval, drops the guard, then verifies counters stop flowing.

State/persistence: in-memory `HashMap<Vec<u8>, ResourceUsageRecord>` protected by `Mutex`; worker state is stopped at the end.

Dependencies/integration: uses public `init_recorder`, `init_reporter`, `record_read_keys`, `record_write_keys`, kvproto context tags, and `ReadableDuration` config.

Risks: sleeps depend on configured precision/report intervals and can be slow/flaky under severe scheduling delay. It validates read/write keys but not network/logical byte gates.

Test signals: verifies the activation contract: reporter data-sink registration causes recorder collection to start, and dropping the sink stops reporting.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/resource_metering/tests/summary_test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/security/Cargo.toml -->
## sources/storage-engines/tikv/components/security/Cargo.toml

Purpose: package manifest for the `security` component crate.

Important APIs/types/functions: declares package name `security`, edition 2021, Apache-2.0 license, non-publishable. Dependencies include collections, encryption, grpcio, log wrappers, online config, serde/serde_derive, slog, slog-global, and tikv_util; dev dependency is tempfile.

Control flow: no runtime control flow; it controls crate compilation and feature availability.

State/persistence: no direct state. The dependency graph enables TLS certificate loading, online config handling, and encryption config embedding in `SecurityConfig`.

Dependencies/integration: consumed by server and PD/grpc clients. `grpcio` is central for channel/server credential builders and peer auth checks; `online_config` enables runtime redaction config changes.

Risks: because versions are mostly workspace-managed, security behavior tracks workspace dependency updates. No crate features are declared here, so optional behavior must come from dependencies or config.

Test signals: `tempfile` supports file-based certificate/config tests in `src/lib.rs`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/security/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/security/src/lib.rs -->
## sources/storage-engines/tikv/components/security/src/lib.rs

Purpose: implements TiKV security configuration, TLS credential loading, secure grpc channel/server setup, certificate reload, and common-name authorization.

Important APIs/types/functions: `SecurityConfig`, `SecurityConfigManager`, `SecurityManager`, `ClientSuite`, `Secret`, `match_peer_names`, and private helpers `check_key_file`, `load_key`, `CnChecker`, `Fetcher`, and `check_common_name`.

Control flow: `SecurityConfig::validate` enforces all-or-none CA/cert/key paths. `SecurityManager::connect` chooses insecure or TLS channel creation. `bind` chooses insecure bind or TLS bind with a credentials fetcher and optional CN checker. `Fetcher::fetch` reloads credentials only when the cert file modification time changes. Online config dispatch updates log redaction.

State/persistence: configuration is stored in an `Arc<SecurityConfig>`. Certificate contents are loaded from files on demand; server fetcher tracks last cert modification time behind a mutex. No secret content is printed because `Secret` redacts debug output.

Dependencies/integration: used by server startup, status server, PD clients, and grpc services. Depends on `grpcio`, encryption config, online config, log redaction, and filesystem metadata.

Risks: `connect` uses empty certs on load failure and defers errors to grpc connection time; CN matching is exact despite a comment mentioning wildcard support; reload watches only cert path modification, not CA/key paths independently.

Test signals: tests validate default insecure config, invalid/incomplete/valid certificate file combinations, certificate loading, and modification timestamp detection.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/security/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/Cargo.toml -->
## sources/storage-engines/tikv/components/server/Cargo.toml

Purpose: package manifest for the `server` component crate that assembles TiKV runtime services.

Important APIs/types/functions: declares package `server`, edition 2024, features forwarding allocator, failpoint, engine, backup stream, and test-engine options. Dependencies include core storage engines, raftstore, resource_metering, security, PD client, CDC, backup, grpcio, tikv, tokio, yatp, and many support crates.

Control flow: no runtime control flow; manifest features decide compile-time capabilities such as allocator selection, memory engine, failpoints, and raft/rocks test engines.

State/persistence: no direct state; dependency choices govern access to RocksDB, raft log engine, encryption, backup, and server modules that persist data.

Dependencies/integration: this crate is an integration hub. The manifest explicitly depends on both `resource_metering` and `security`, matching the server startup code that wires metering and TLS into grpc/storage.

Risks: broad dependency surface means feature mismatches can affect large runtime areas. Edition 2024 may require workspace/toolchain support.

Test signals: features expose test engine configurations and failpoints; individual source files contain targeted unit tests for disk usage, raft engine switching, and compaction pressure.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/common.rs -->
## sources/storage-engines/tikv/components/server/src/common.rs

Purpose: shared startup/runtime utilities for TiKV-like servers: config validation, filesystem locks, encryption/IO setup, PD connection, quota tuning, engine migration, metrics, compaction pressure, stop abstraction, hybrid engine construction, and disk usage checks.

Important APIs/types/functions: `TikvServerCore`, `EnginesResourceInfo`, `ConfiguredRaftEngine`, `EngineMetricsManager`, `DiskUsageChecker`, `Stop`, `build_hybrid_engine`, `check_system_config`, and lock helpers.

Control flow: startup calls `init_config`, `check_conflict_addr`, `init_fs`, `init_yatp`, `init_encryption`, `init_io_utility`, `init_flow_receiver`, and `connect_to_pd_cluster`. Background tasks tune quota from process CPU usage, flush engine/IO metrics, update compaction pressure, and classify disk status. `ConfiguredRaftEngine` specializations migrate raft logs between RocksDB raftdb and raft-log-engine when the persisted state machine says a switch is needed.

State/persistence: manages data-dir locks, conflict-address lock files, reserved disk placeholder files, encryption key manager, flow channels, worker stop list, raft data migration, metrics reset timers, and moving averages of compaction pressure.

Dependencies/integration: ties together tikv config/controller, encryption, Rocks/raft engines, file_system IO limiter, PD client, security, raftstore, in-memory engine, prometheus/yatp, and system quota/disk APIs.

Risks: many failures are fatal by design; disk reservation and migration code mutate on-disk layout; compaction tuning assumes CF ordering matches `DATA_CFS`; disk status depends on mount separation heuristics and configured thresholds.

Test signals: unit tests cover `DiskUsageChecker` states under failpointed disk stats and `EnginesResourceInfo::update` selecting latest tablets and clearing caches.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/common.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/lib.rs -->
## sources/storage-engines/tikv/components/server/src/lib.rs

Purpose: crate root for the server component.

Important APIs/types/functions: enables specialization with `#![feature(specialization)]`, imports `tikv_util` macros, and exposes modules `setup`, `common`, `memory`, `raft_engine_switch`, `server`, `server2`, and `signal_handler`; `utils` remains private.

Control flow: no direct runtime flow; module export structure determines which server helpers are externally available.

State/persistence: none directly.

Dependencies/integration: downstream code imports this crate to run or compose TiKV server startup. Public modules expose both legacy/common startup utilities and newer server variants.

Risks: specialization requires nightly/compatible toolchain support; public module exposure increases API surface and coupling.

Test signals: tests live in submodules rather than the crate root.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/memory.rs -->
## sources/storage-engines/tikv/components/server/src/memory.rs

Purpose: flushes hierarchical memory trace providers into TiKV memory trace prometheus gauges.

Important APIs/types/functions: `MemoryTraceManager`, `flush`, and `register_provider`. Providers are `Arc<MemoryTrace>` roots.

Control flow: `flush` iterates registered providers, then each child and optional leaf. Leafless children emit `provider-child`; leaf children emit `provider-child-leaf`; provider totals emit `provider`.

State/persistence: holds an in-memory vector of providers. Metrics are updated each flush; no durable persistence.

Dependencies/integration: used by server metrics flusher with raftstore and coprocessor memory trace roots. Depends on `tikv_alloc::trace::MemoryTrace`, `tikv::server::MEM_TRACE_SUM_GAUGE`, and `tikv_util::time::Instant`.

Risks: labels are constructed dynamically and can grow with provider topology; `_now` is currently unused; only two child levels are represented.

Test signals: no direct tests; exercised through server metrics-flush integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/memory.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/raft_engine_switch.rs -->
## sources/storage-engines/tikv/components/server/src/raft_engine_switch.rs

Purpose: migrates raft log/state data between RocksDB raftdb and raft-log-engine formats.

Important APIs/types/functions: `dump_raftdb_to_raft_engine`, `dump_raft_engine_to_raftdb`, `run_dump_raftdb_worker`, `run_dump_raft_engine_worker`, and emptiness checks. `BATCH_THRESHOLD` limits log batch size.

Control flow: public dump functions assert the target is empty, spawn worker threads, scan source raft groups/region ids, send ids over a channel, wait for workers, then sync the target. RocksDB-to-raft-engine workers scan raft key ranges, decode log entries/state, append batches, and consume periodically. Reverse workers fetch raft state and entries in chunks and consume Rocks batches.

State/persistence: directly writes target engine data and syncs it. Counts total transferred bytes with an atomic counter. Source engines are read-only during migration.

Dependencies/integration: used by `ConfiguredRaftEngine` implementations in `common.rs` during raft engine switching. Depends on RocksEngine, RaftLogEngine, raft key encoding, protobuf merge, raft entries, and engine traits.

Risks: uses assertions/panics for non-empty targets and decode errors; assumes raftdb scan ordering sees entries before raft state; concurrent migration thread count must be nonzero for progress; migration is a critical on-disk operation.

Test signals: tests create temporary engines, write raft batches for regions 1/5/15, migrate both directions, and verify state/entries with and without separate raftdb WAL.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/raft_engine_switch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/server.rs -->
## sources/storage-engines/tikv/components/server/src/server.rs

Purpose: orchestrates full TiKV server startup, service registration, background tasks, pause/resume, graceful shutdown, and stop sequencing.

Important APIs/types/functions: public `run_tikv`; internal `run_impl`; `TikvServer`, `TikvEngines`, `Servers`, and methods `init`, `init_raw_engines`, `init_engines`, `init_servers`, `register_services`, `init_metrics_flusher`, `init_storage_stats_task`, `run_server`, `run_status_server`, `pause`, `resume`, `graceful_shutdown`, and `stop`.

Control flow: `run_tikv` logs quotas, performs pre-start checks, dispatches by API version and raft engine choice, initializes `TikvServer`, sets memory high-water handling, checks locks/filesystems, initializes engines, servers, services, metrics, cgroup/storage/max-ts tasks, starts grpc/status servers, and then handles service events until shutdown. `init_servers` constructs flow control, GC, CDC, resolved-ts, read pools, resource metering recorder/reporter/sinks, storage, raft server, coprocessor, backup, split, import, and debug infrastructure before starting raft and workers.

State/persistence: owns engine handles, store metadata, workers, config controller, PD client, security manager, snapshot manager, resource manager, quota limiter, raft system/router, memory/statistics state, lock files, and stop list. It opens and mutates persistent RocksDB/raft engines, snapshot/import directories, and runtime lock files.

Dependencies/integration: this is the integration point for almost every component in the manifest: PD, raftstore, storage, grpc services, security, resource metering, CDC, backup, import SST, diagnostics/debug, in-memory engine, quota/resource control, and signal handling.

Risks: startup is order-sensitive and many errors are fatal; background tasks assume initialized fields via `unwrap`; resource metering must be started before storage request tagging; graceful shutdown depends on PD scheduler and leader eviction completing before timeout; stop ordering must prevent engines/workers from outliving dependencies.

Test signals: inline test covers `EnginesResourceInfo` compaction-pending behavior. Most server behavior is integration-tested elsewhere; this file’s code relies heavily on subsystem tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/server/src/server.rs -->
