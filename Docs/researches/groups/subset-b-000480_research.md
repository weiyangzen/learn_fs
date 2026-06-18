# subset-b-000480 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterClientServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterClientServiceHandler.java

Purpose: gRPC client-facing handler for the metrics master. It exposes clear, heartbeat, and get-metrics RPCs from `MetricsMasterClientServiceGrpc.MetricsMasterClientServiceImplBase` and delegates all behavior to the injected `MetricsMaster`.

Important APIs/types/functions: constructor validates `MetricsMaster`; `clearMetrics` calls `MetricsMaster.clearMetrics`; `metricsHeartbeat` converts nested protobuf client metrics to `alluxio.metrics.Metric` objects and calls `clientHeartbeat(source, metrics)` per source; `getMetrics` returns the master's metric map in `GetMetricsPResponse`.

Control flow: every RPC is wrapped by `RpcUtils.call`, which centralizes logging, exception translation, and stream observer completion. Heartbeat iterates `request.getOptions().getClientMetricsList()`, creates a fresh Java list for each source, converts each protobuf metric through `Metric.fromProto`, then reports the list to the metrics master.

State and persistence: this handler stores only the master reference and is annotated not thread-safe; persistent behavior is delegated to the master and `MetricsStore`. It does not cache or journal client metrics itself.

Dependencies/integration: integrates with generated gRPC request/response types, `RpcUtils`, Guava `Lists`, and the `MetricsMaster` implementation used by the master registry.

Risks: null request internals are not explicitly guarded beyond protobuf defaults. Large heartbeat batches allocate a list per client source. The not-thread-safe annotation is worth respecting because gRPC service implementations are often shared unless guarded upstream.

Test signals: useful tests should verify clear delegation, protobuf-to-`Metric` conversion for multiple client sources, empty heartbeat handling, exception propagation through `RpcUtils`, and `getMetrics` map preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterClientServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterFactory.java

Purpose: master factory responsible for constructing and registering the metrics master in core master startup.

Important APIs/types/functions: implements `MasterFactory<CoreMasterContext>`; `isEnabled()` always returns true; `getName()` returns `Constants.METRICS_MASTER_NAME`; `create` builds a `DefaultMetricsMaster`, registers it under `MetricsMaster.class`, and returns it.

Control flow: during master boot, the factory logs creation, constructs `DefaultMetricsMaster` with the shared `CoreMasterContext`, adds it to `MasterRegistry`, and exposes the typed master for later dependencies such as block master and throttle master.

State and persistence: the factory itself is stateless and thread-safe. Metrics persistence and in-memory state belong to `DefaultMetricsMaster`, `MetricsStore`, and the global metrics system.

Dependencies/integration: participates in Alluxio's `MasterFactory` discovery/registration path and provides `MetricsMaster` dependency resolution to other masters.

Risks: because `isEnabled` is unconditional, tests and deployments must account for metrics master creation even when metric collection features are disabled. Duplicate registration behavior depends on `MasterRegistry` semantics and is not guarded here.

Test signals: verify name, unconditional enablement, returned implementation type, and registry lookup after `create`. Existing block/backup tests instantiate it to satisfy block-master dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsStore.java

Purpose: thread-safe in-memory aggregation store for worker and client metrics reported to the metrics master. It maps selected instance metrics to cluster counters and supports clearing/resetting metric state.

Important APIs/types/functions: `putWorkerMetrics`, `putClientMetrics`, `initMetricKeys`, `clear`, `getLastClearTime`, `incrementUfsRelatedCounters`, and nested `ClusterCounterKey`. `ClusterCounterKey` combines `MetricsSystem.InstanceType` and metric name for the counter lookup map.

Control flow: worker/client heartbeats enter through `put*Metrics`; empty or null-source batches are ignored. `putReportedMetrics` walks reported metrics and only processes `MetricType.COUNTER`. Known counters are incremented by delta value; unknown client counters are ignored; worker UFS read/write counters are expanded into per-UFS and aggregate cluster counters. `initMetricKeys` pre-registers the counter mappings and cache-hit-rate gauge.

State and persistence: state is in `mClusterCounters` and `mLastClearTime`, protected by a read/write lock. Report ingestion uses the read lock while `clear` takes the write lock, decrements all cluster counters to zero, updates clear time from the injected `Clock`, and calls `MetricsSystem.resetAllMetrics`. There is no journal persistence.

Dependencies/integration: depends on Dropwizard `Counter`, Alluxio `MetricsSystem`, `MetricKey`, `MetricInfo` tags, and `LockResource`. It receives worker/client data via `DefaultMetricsMaster` and affects cluster metrics exported through sinks and RPCs.

Risks: UFS-specific metrics assume the aggregate all-UFS counter was initialized before ingest, otherwise `mClusterCounters.get(...).inc` can null-dereference. Counter values are cast from double to long. `clear` resets the global metrics system, so callers must coordinate it with updater/sink lifecycle as the class comment warns.

Test signals: `MetricsStoreTest` should cover initialization, counter deltas, client-vs-worker behavior, UFS per-tag aggregation, clear-time updates, and reset behavior. Additional useful cases include missing UFS tags, ingest before `initMetricKeys`, concurrent put/clear, and non-counter metric filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/MetricsStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/TimeSeriesStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/TimeSeriesStore.java

Purpose: lightweight in-memory store for metric time series samples keyed by metric name.

Important APIs/types/functions: constructor initializes a `ConcurrentHashMap`; `record(metric, value)` creates or updates a `TimeSeries`; `getTimeSeries()` returns an immutable copy of all stored series.

Control flow: record uses `ConcurrentHashMap.compute` so series creation and sample recording for a metric key occur atomically with respect to other updates to that key. Retrieval snapshots the current values into an immutable list without deep-copying individual `TimeSeries` objects.

State and persistence: all state is in memory under `mTimeSeries`; there is no checkpointing or journal entry. Retention and sample storage details are delegated to `alluxio.metrics.TimeSeries`.

Dependencies/integration: used by metrics master paths that collect and expose historical metrics. Depends only on `TimeSeries`, Guava `ImmutableList`, and JDK concurrent maps.

Risks: returned `TimeSeries` objects may still be mutable depending on that class's implementation, so `getTimeSeries` is only a collection snapshot. Unbounded unique metric names can grow the map indefinitely.

Test signals: `TimeSeriesStoreTest` should exercise first-record creation, repeated record for same key, multiple metric keys, immutable collection behavior, and concurrent recording semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/metrics/TimeSeriesStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/DefaultWorkerProvider.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/DefaultWorkerProvider.java

Purpose: production `WorkerProvider` for scheduler jobs, sourcing worker metadata from `FileSystemMaster` and block worker clients from `FileSystemContext`.

Important APIs/types/functions: constructor stores `FileSystemMaster` and `FileSystemContext`; `getWorkerInfos` delegates to `FileSystemMaster.getWorkerInfoList`; `getWorkerClient` calls `FileSystemContext.acquireBlockWorkerClient`.

Control flow: scheduler calls `getWorkerInfos` during worker refresh, then opens clients for newly observed worker addresses. Checked `UnavailableException` becomes `UnavailableRuntimeException`; `IOException` from acquiring a block worker client becomes an `AlluxioRuntimeException`.

State and persistence: no internal mutable state and no persistence. Worker liveness and client pooling are handled by the file-system master and filesystem context.

Dependencies/integration: bridges `alluxio.scheduler.job.WorkerProvider` to master-side worker registry and block worker RPC client acquisition.

Risks: TODO notes that the provider returns all workers, not explicitly healthy-only workers. Client acquisition failures are escalated to runtime exceptions and the scheduler chooses whether to skip workers.

Test signals: verify unavailable master handling, IO-to-runtime conversion, and that returned worker list/client resources are exactly delegated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/DefaultWorkerProvider.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/JournaledJobMetaStore.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/JournaledJobMetaStore.java

Purpose: journal-backed metadata store for scheduler jobs. It persists job state changes through the filesystem master's journal and reconstructs jobs from scheduler checkpoint/journal entries.

Important APIs/types/functions: implements `JobMetaStore` and `Journaled`; `getJournalEntryIterator`, `processJournalEntry`, `resetState`, `getCheckpointName`, `updateJob`, and `getJobs`.

Control flow: on journal replay, only entries with `loadJob` are accepted; the entry is passed to `JobFactoryProducer.create(entry, mFileSystemMaster).create()` and the resulting job is added to `mExistingJobs`. `updateJob` opens a `JournalContext` from `FileSystemMaster`, appends `job.toJournalEntry()`, then stores the job in the concurrent set.

State and persistence: live state is `ConcurrentHashSet<Job<?>> mExistingJobs`. Persistence is append-only through the file-system master's journal context and checkpoint name `SCHEDULER`. `resetState` clears only the in-memory set.

Dependencies/integration: integrates with scheduler `JobMetaStore`, Alluxio journal replay/checkpoint framework, `JobFactoryProducer`, and `FileSystemMaster` for journal context creation.

Risks: set identity/equality semantics depend on `Job` implementations. `getJobs` returns the live concurrent set, allowing callers to observe mutations. `updateJob` turns `UnavailableException` into a user-facing runtime message about backups, so backup/journal unavailability blocks scheduling persistence.

Test signals: replay accepted/rejected entries, checkpoint iterator content, update appending behavior, unavailable journal handling, reset behavior, and duplicate/equivalent job entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/JournaledJobMetaStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/Scheduler.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/Scheduler.java

Purpose: master-side scheduler for Alluxio jobs. It owns active job state, periodically refreshes workers, assigns tasks, handles task callbacks, persists job updates, and cleans old finished jobs.

Important APIs/types/functions: `start`, `stop`, `submitJob`, `stopJob`, `getJobProgress`, `updateWorkers`, `cleanupStaleJob`, `processJobs`, `processJob`, and `scheduleTask`. Core maps are `mExistingJobs`, `mRunningTasks`, and `mActiveWorkers`.

Control flow: `start` retrieves persisted jobs, creates a single-thread scheduled executor, refreshes workers at configured interval, processes jobs every 100 ms, and cleans stale jobs hourly. `submitJob` updates a matching non-done job or persists and starts a new one if capacity allows. `processJob` persists completed/stopped jobs, fails unhealthy jobs, schedules at most one task per worker per job description, and completes or starts verification when the current pass finishes. `scheduleTask` obtains the next task, executes it on the worker client, and adds a future listener on the scheduler executor to process responses and chain more work.

State and persistence: job metadata is persisted through `JobMetaStore.updateJob`. Running worker sets are per-job `HashSet`s stored in a concurrent map; worker clients are immutable-map snapshots and are closed on stop or worker loss. Finished jobs are retained in `mExistingJobs` until retention cleanup.

Dependencies/integration: depends on `WorkerProvider`, `BlockWorkerClient`, scheduler `Job`/`Task` APIs, `JobProgressReportFormat`, `Configuration`, and Alluxio runtime exception classes.

Risks: per-job running-worker sets are plain `HashSet`s mutated by scheduler callbacks; the design relies on the single scheduler executor, but worker refresh can replace `mActiveWorkers` concurrently. `submitJob` and processing can race around `mRunningTasks`. Exceptions are broadly caught to preserve the scheduler thread, which can hide systemic issues except for logs and job failure state.

Test signals: tests should cover job recovery, duplicate submit/update, capacity exhaustion, worker refresh add/drop/client-close, task chaining, retryable/nonretryable `getNextTask` errors, stop job persistence, verification transition, retention cleanup, and executor shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/scheduler/Scheduler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/NoopService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/NoopService.java

Purpose: null-object implementation of `SimpleService` for disabled optional master services.

Important APIs/types/functions: implements `start`, `promote`, `demote`, and `stop` as no-ops.

Control flow: factories return `NoopService` when a feature such as JVM monitoring is disabled, allowing master startup code to treat it like any other service without conditionals.

State and persistence: no state and no persistence.

Dependencies/integration: used by service factories such as `JvmMonitorService.Factory` to satisfy the lifecycle interface.

Risks: lifecycle misuse is intentionally ignored, so tests that expect state-transition validation should use concrete service implementations instead.

Test signals: useful only as a guard that disabled factories return a service whose lifecycle calls are safe and side-effect free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/NoopService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/SimpleService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/SimpleService.java

Purpose: common lifecycle contract for master-adjacent services such as RPC, web, metrics sinks, and JVM monitoring.

Important APIs/types/functions: `start`, `promote`, `demote`, and `stop`. The Javadoc defines intended state transitions between standby and primary behavior.

Control flow: master process starts services in standby state, calls `promote` on gaining primacy, calls `demote` on losing primacy, and calls `stop` during shutdown. Concrete services decide whether promotion changes runtime behavior.

State and persistence: interface carries no state; implementations are responsible for idempotency or precondition checks. No persistence contract is included.

Dependencies/integration: referenced by master service factories and `AlluxioMasterProcess` service registration.

Risks: lifecycle preconditions are documented but not enforced by the interface. Implementations differ: some tolerate repeated stop, while RPC standby service rejects double promotion/demotion.

Test signals: lifecycle tests should verify concrete implementations against the documented contract, especially start-before-promote, demote-only-after-promote, and stop idempotency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/SimpleService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/jvmmonitor/JvmMonitorService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/jvmmonitor/JvmMonitorService.java

Purpose: optional `SimpleService` that starts a JVM pause monitor for the master and registers gauges for pause statistics.

Important APIs/types/functions: synchronized `start`, `promote`, `demote`, `stop`, and nested `Factory.create`. The service owns nullable `JvmPauseMonitor mJvmPauseMonitor`.

Control flow: factory returns `NoopService` when `MASTER_JVM_MONITOR_ENABLED` is false. `start` checks the monitor is absent, constructs `JvmPauseMonitor` from sleep/warn/info threshold configuration, starts it, and registers total/info/warn pause gauges if absent. `promote` and `demote` are no-ops. `stop` stops and clears the monitor if present.

State and persistence: monitor reference is guarded by the service instance lock. Metrics are registered in the global metrics system; there is no journaled state.

Dependencies/integration: depends on `Configuration`, `PropertyKey`, `MetricKey`, `MetricsSystem`, and `JvmPauseMonitor`. `ServerIndicator` later reads the total pause metric when throttling is enabled.

Risks: `start` is intentionally single-use until `stop` clears the monitor. Registered gauges capture the monitor instance; after stop/start, `registerGaugeIfAbsent` may keep an older supplier depending on metrics registry behavior.

Test signals: `JvmMonitorServiceTest` should cover disabled factory, start/stop lifecycle, duplicate start rejection, metric registration, and no-op promotion/demotion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/jvmmonitor/JvmMonitorService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/AlwaysOnMetricsService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/AlwaysOnMetricsService.java

Purpose: metrics-sink lifecycle variant that starts metrics reporting immediately when the master service starts, including standby mode.

Important APIs/types/functions: overrides `start`, `promote`, `demote`, and `stop` from `MetricsService`.

Control flow: `start` logs and calls `startMetricsSystem`; `promote` and `demote` do nothing because sinks remain active across primary state changes; `stop` calls `stopMetricsSystem`.

State and persistence: no fields. Sink state lives in the global `MetricsSystem`.

Dependencies/integration: selected by `MetricsService.Factory` when `STANDBY_MASTER_METRICS_SINK_ENABLED` is true. Used by master process startup tests parameterized over standby metric behavior.

Risks: repeated start or stop behavior depends on `MetricsSystem` idempotency. Always-on standby reporting can duplicate cluster sink output if deployments expect only primary masters to emit metrics.

Test signals: verify sink start on service start, no sink changes on promote/demote, sink stop on stop, and factory selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/AlwaysOnMetricsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/MetricsService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/MetricsService.java

Purpose: abstract base for master metrics sink lifecycle services.

Important APIs/types/functions: protected `startMetricsSystem`, protected `stopMetricsSystem`, and nested `Factory.create`.

Control flow: subclasses decide when to call the helpers. The start helper reads `METRICS_CONF_FILE` and calls `MetricsSystem.startSinks`; the stop helper calls `MetricsSystem.stopSinks`. Factory selects always-on or primary-only mode from `STANDBY_MASTER_METRICS_SINK_ENABLED`.

State and persistence: no local state. Metrics sinks, reporters, and exported metrics are global `MetricsSystem` concerns and are not journaled here.

Dependencies/integration: implements `SimpleService`; integrated into `AlluxioMasterProcess` registered service list and tested through master start/stop readiness checks.

Risks: factory returns concrete package-private subclasses, so external tests usually observe via lifecycle effects. Misordered lifecycle calls can double-start or double-stop sinks unless `MetricsSystem` tolerates it.

Test signals: `MetricsServiceTest` should cover factory selection, config-file path forwarding, and primary/standby lifecycle behavior through the two subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/MetricsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/PrimaryOnlyMetricsService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/PrimaryOnlyMetricsService.java

Purpose: metrics-sink lifecycle variant that reports only while the master is primary.

Important APIs/types/functions: overrides `start`, `promote`, `demote`, and `stop`.

Control flow: `start` only logs, leaving sinks stopped in standby. `promote` starts sinks. `demote` stops sinks. `stop` also stops sinks to clean up if the service is currently primary or if shutdown follows an unusual state path.

State and persistence: stateless wrapper over global `MetricsSystem`.

Dependencies/integration: default selection by `MetricsService.Factory` when standby sink reporting is disabled. Master process tests assert metric sinks are not serving for standby masters under this configuration.

Risks: double `demote` or `stop` after `demote` relies on sink stop idempotency. If promotion fails after sinks start, cleanup must occur through master process error handling.

Test signals: verify no start-on-standby, start-on-promote, stop-on-demote, stop-on-shutdown, and behavior across promote/demote/promote cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/metrics/PrimaryOnlyMetricsService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerService.java

Purpose: primary-only master RPC service lifecycle manager. It binds a rejecting server while standby, starts the real gRPC server on promotion, and cleans up server/executor resources on demotion or stop.

Important APIs/types/functions: `start`, `promote`, `demote`, `stop`, `startGrpcServer`, `stopGrpcServer`, `stopRpcExecutor`, `startRejectingServer`, `stopRejectingServer`, `isServing`, `isServingLeader`, `isServingStandby`, static `waitFor`, and nested `Factory.create`.

Control flow: `start` launches a `RejectingServer` on the RPC bind address. `promote` stops the rejecting server, waits briefly for the port to become free, builds a gRPC server from `MasterProcess.createBaseRpcServer`, optionally installs the master RPC executor, registers all primary services from every master in `MasterRegistry`, starts the server, and notifies safe mode. `demote` shuts down gRPC and executor, waits for the port to free, then restarts the rejecting server. `stop` stops both possible server types and the executor.

State and persistence: guarded nullable fields hold `GrpcServer`, `AlluxioExecutorService`, and `RejectingServer`. No journal state. Runtime serving state is derived from server fields.

Dependencies/integration: integrates `MasterProcess`, `MasterRegistry`, `Master.getServices`, `SafeModeManager`, `GrpcServerBuilder`, `RejectingServer`, and master process service registration.

Risks: all lifecycle methods are synchronized but static socket polling can silently time out and proceed. `startGrpcServer` may partially create an executor before gRPC start fails; callers depend on later stop cleanup. Factory switches to `RpcServerStandbyGrpcService` when standby gRPC is enabled.

Test signals: `RpcServerServiceTest` and master process tests should cover rejecting-server binding, primary promotion service registration, safe-mode notification, executor shutdown, demote-to-rejecting behavior, stop idempotency, and port-free wait behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerStandbyGrpcService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerStandbyGrpcService.java

Purpose: always-bound RPC service variant for standby gRPC mode. It serves standby endpoints while standby and restarts the server with primary endpoints on promotion.

Important APIs/types/functions: overrides `isServingLeader`, `isServingStandby`, `start`, `stop`, `promote`, and `demote`; owns boolean `mIsPromoted`.

Control flow: `start` immediately starts a gRPC server using `Master::getStandbyServices` and no rejecting server. `promote` rejects double promotion, stops current server and executor, waits for the port to free, starts primary services with `Master::getServices`, then marks promoted. `demote` performs the inverse and restarts standby services. `stop` shuts down server/executor and clears the promoted flag.

State and persistence: serving mode is in `mIsPromoted` plus inherited `mGrpcServer`. No persistence.

Dependencies/integration: selected by `RpcServerService.Factory` when `STANDBY_MASTER_GRPC_ENABLED` is true. Uses the same `MasterProcess` and registry server construction as the base class.

Risks: every promotion/demotion restarts the server, so active standby RPCs are interrupted during state changes. Preconditions reject repeated state transitions rather than making them idempotent. Safe-mode notification occurs inside inherited `startGrpcServer` for both standby and primary starts.

Test signals: `RpcServerStandbyGrpcServiceTest` should cover standby serving after start, leader serving after promote, restart back to standby after demote, double transition failures, and stop cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerStandbyGrpcService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/AlwaysOnWebServerService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/AlwaysOnWebServerService.java

Purpose: web-server lifecycle variant that starts the master web server in standby and keeps it running across primary state changes.

Important APIs/types/functions: constructor forwards `MasterProcess`; overrides `start`, `promote`, `demote`, and `stop`.

Control flow: `start` calls inherited `startWebServer`; promotion and demotion are no-ops; `stop` calls inherited `stopWebServer`.

State and persistence: no local state; web server object is managed by `WebServerService`.

Dependencies/integration: selected by `WebServerService.Factory` for `AlluxioMasterProcess` when `STANDBY_MASTER_WEB_ENABLED` is true. Master process tests assert web readiness while standby under this mode.

Risks: web resources are available from standby masters, so REST handlers must enforce state-sensitive operations themselves. Repeated start is guarded by the base precondition.

Test signals: verify start creates a web server, promote/demote do not restart it, stop tears it down, and factory selection only applies to eligible master process type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/AlwaysOnWebServerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/PrimaryOnlyWebServerService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/PrimaryOnlyWebServerService.java

Purpose: primary-only web service manager. It keeps the web port bound by a rejecting server while standby, and runs the real web UI/API server only while primary.

Important APIs/types/functions: `start`, `promote`, `demote`, `stop`, private `startRejectingServer`, `stopRejectingServer`, `waitForFree`, and `waitForBound`.

Control flow: `start` binds a `RejectingServer`. `promote` stops the rejecting server, waits for the port to free, and starts the inherited web server. `demote` stops the web server, waits for the port to free, and restarts the rejecting server. `stop` stops both, tolerating a null web server or rejecting server.

State and persistence: guarded nullable `RejectingServer` plus inherited guarded `WebServer`. No persistence.

Dependencies/integration: uses `RpcServerService.waitFor` for socket polling and `RejectingServer` for standby port behavior. Created by `WebServerService.Factory` when standby web is disabled or the process is not a full `AlluxioMasterProcess`.

Risks: no explicit precondition prevents double promotion from calling `startWebServer` when already running, but base `startWebServer` will reject an existing web server. Socket wait failures are swallowed.

Test signals: `WebServerServiceTest` should cover rejecting server bind on start, web readiness after promote, rejecting-server restoration after demote, stop cleanup, and port-bound assertions used by `AlluxioMasterProcessTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/PrimaryOnlyWebServerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/WebServerService.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/WebServerService.java

Purpose: abstract base for master web server lifecycle services, with factory selection for standby-enabled or primary-only behavior.

Important APIs/types/functions: guarded `WebServer mWebServer`, `isServing`, `startWebServer`, `stopWebServer`, and nested `Factory.create`.

Control flow: concrete services call `startWebServer` when their lifecycle mode should expose the web server. The helper checks no server exists, asks `MasterProcess.createWebServer`, and starts it. `stopWebServer` catches and logs stop failures, then clears the field. Factory chooses `AlwaysOnWebServerService` only for `AlluxioMasterProcess` with standby web enabled; otherwise it chooses `PrimaryOnlyWebServerService`.

State and persistence: service state is only the guarded `WebServer` reference. No journal persistence.

Dependencies/integration: implements `SimpleService`; integrates with master process service registration, web bind address configuration, and `MasterWebServer` creation.

Risks: `isServing` assumes `getServer()` is non-null after web server creation. Stop failures are logged but do not prevent clearing the reference, which could hide leaked Jetty resources.

Test signals: factory branch coverage, start/stop helper state, stop exception handling, and `isServing` behavior across lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/web/WebServerService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/DefaultThrottleMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/DefaultThrottleMaster.java

Purpose: optional master component that periodically monitors master load indicators and logs/throttles status through `SystemMonitor`.

Important APIs/types/functions: extends `AbstractMaster` and implements `NoopJournaled`; `setMaster`, `getDependencies`, `getName`, `start`, `getServices`, and nested `ThrottleExecutor`.

Control flow: construction registers the master in `MasterRegistry`. `setMaster` must be called before startup and creates a `ThrottleExecutor`. `start(isLeader)` starts the base master, verifies dependencies, and only for leaders submits a `HeartbeatThread` using `MASTER_THROTTLE_HEARTBEAT_INTERVAL`. The executor delegates heartbeat work to `SystemMonitor.run`.

State and persistence: holds `MasterProcess`, `ThrottleExecutor`, and the future for the heartbeat service. It is `NoopJournaled`, so no journal state is persisted and no gRPC services are exposed.

Dependencies/integration: declares dependencies on `BlockMaster`, `FileSystemMaster`, and `MetricsMaster`. Uses master context executor services, heartbeat framework, configuration, and `SystemMonitor`.

Risks: `setMaster` is a required out-of-band initialization step. Standby masters do not run monitoring. The future is stored but not otherwise managed in this file; stop behavior relies on `AbstractMaster`.

Test signals: verify factory enablement, dependency set, leader-only heartbeat start, null-precondition failures when `setMaster` is omitted, and executor heartbeat delegation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/DefaultThrottleMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/FileSystemIndicator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/FileSystemIndicator.java

Purpose: point-in-time snapshot of selected filesystem/master counters for throttle diagnostics, with support for delta computation against a prior snapshot.

Important APIs/types/functions: static `OBSERVED_MASTER_COUNTER`; constructors; `getCounter`, `getPitTimeMS`, `setCounter`, `setPitTimeMS`, `deltaTo`, and `toString`.

Control flow: construction populates a map by reading every observed counter from `MetricsSystem.METRIC_REGISTRY`. `deltaTo` subtracts baseline values for all observed counters, preserving only counters in the observed list. `SystemMonitor` creates these snapshots only when status is stressed or overloaded and logs deltas when consecutive stressed/overloaded samples exist.

State and persistence: state is an in-memory map of counter name to long plus snapshot time. No persistence.

Dependencies/integration: depends on counter-name constants from `MetricsMonitorUtils.FileSystemCounterName` and Dropwizard metrics registry. It gives `SystemMonitor` filesystem activity context during pressure events.

Risks: accessing counters through `METRIC_REGISTRY.counter(name)` creates missing counters with zero values, which may pollute the registry. The observed list is static and manual, so new critical filesystem metrics are missed until added.

Test signals: `IndicatorsTests` should cover snapshot values, copy construction, delta math with missing baseline counters, setter behavior, and string rendering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/FileSystemIndicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/MetricsMonitorUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/MetricsMonitorUtils.java

Purpose: centralized metric-name constants used by throttle monitoring code.

Important APIs/types/functions: nested classes `MemoryGaugeName`, `OSGaugeName`, `ServerPrefix`, `ServerGaugeName`, `FileSystemGaugeName`, and `FileSystemCounterName`.

Control flow: no runtime control flow beyond class initialization. Constants are composed from `MetricKey` and `MetricsSystem.getMetricName` where needed.

State and persistence: static constants only, no mutable state and no persistence.

Dependencies/integration: consumed by `ServerIndicator` for JVM/OS/RPC gauges and by `FileSystemIndicator` for filesystem counter snapshots. It ties throttle logic to the exact names registered by the metrics subsystem.

Risks: string constants such as `Master.getConfigHashInProgress` are hand-written and can drift from instrumentation names. Some nested constants include already-prefixed metric names while others are raw `MetricKey` names, so callers must know which registry lookup form to use.

Test signals: compile-time usage is the main guard. Useful tests would validate that each referenced gauge/counter name exists after normal master metric registration and that prefixed names match the registry keys read by `ServerIndicator`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/MetricsMonitorUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ServerIndicator.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ServerIndicator.java

Purpose: numeric load indicator for throttle decisions, representing heap, direct memory, CPU load, JVM pause time, Netty direct memory, RPC queue size, and snapshot time.

Important APIs/types/functions: constructors for point, copy, and scaled threshold indicators; static `getSystemTotalJVMPauseTime`, `createFromMetrics`, `createThresholdIndicator`; getters; `addition`; `reduction`; and `toString`.

Control flow: `createFromMetrics` reads JVM pause metrics conditionally, RPC queue length, memory gauges, and OS CPU load from the metrics registry with default fallback values. `createThresholdIndicator` converts configured heap ratio to absolute heap bytes based on current heap max. `addition` and `reduction` support sliding-window aggregate indicators; reduction clamps at zero.

State and persistence: all fields are in-memory scalar values. No persistence. Scaled copies multiply additive metrics by the window size while preserving heap max and point-in-time pause total.

Dependencies/integration: used by `SystemMonitor` for current samples, aggregate windows, and active/stressed/overloaded thresholds. Reads names from `MetricsMonitorUtils` and config flag `MASTER_JVM_MONITOR_ENABLED`.

Risks: `getMetrics` uses unchecked generic casts and catches all exceptions, so type/name mismatches silently become defaults. CPU and heap threshold logic in `SystemMonitor` currently emphasizes heap usage, so other fields may be diagnostic more than decisive.

Test signals: indicator tests should cover metric defaults, threshold scaling, addition/reduction clamping, JVM monitor enabled/disabled pause handling, and string content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ServerIndicator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/SystemMonitor.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/SystemMonitor.java

Purpose: non-thread-safe throttle monitor that samples server/filesystem indicators, maintains a sliding window, computes system status, and logs pressure diagnostics.

Important APIs/types/functions: enums `SystemStatus` and `StatusTransition`; constructor; `run`; `collectIndicators`; `collectServerIndicators`; `collectFileSystemIndicators`; `produceDeltaFilesystemIndicators`; `checkBoundary`; `checkAndBackPressure`; private `PitInfo`.

Control flow: each `run` records snapshot time, samples server indicators, conditionally samples filesystem counters based on current status, evaluates transitions, logs status, then stores PIT info for the next cycle. Thresholds are reinitialized at most every roughly 68 seconds using `System.nanoTime() >> 36`. Status moves IDLE <-> ACTIVE <-> STRESSED <-> OVERLOADED based on low/high PIT and aggregate thresholds; a delayed heartbeat beyond overloaded GC-time threshold forces OVERLOADED.

State and persistence: keeps recent `ServerIndicator` samples, aggregate indicator, current/previous filesystem indicators, delta indicator, threshold indicators, current status, previous PIT info, and heartbeat timing. It registers a `system.status` gauge. No journal persistence.

Dependencies/integration: driven by `DefaultThrottleMaster.ThrottleExecutor`; reads `PropertyKey.MASTER_THROTTLE_*` thresholds and metrics registry values through indicator classes.

Risks: despite monitoring CPU/RPC/direct memory, `checkBoundary` currently compares only heap used, so configured CPU/RPC thresholds do not influence transitions there. Constructor initializes `PitInfo` arguments in an order that appears inconsistent with its constructor names, so pause/time baseline interpretation deserves scrutiny. Not thread-safe; callers should keep one heartbeat thread.

Test signals: cover status escalation/de-escalation across thresholds, delayed heartbeat overload, sliding-window add/reduce, filesystem delta only during consecutive stressed/overloaded samples, threshold refresh, gauge registration, and JVM pause baseline behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/SystemMonitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ThrottleMasterFactory.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ThrottleMasterFactory.java

Purpose: factory for optional `DefaultThrottleMaster` creation.

Important APIs/types/functions: implements raw `MasterFactory`; `isEnabled` reads `MASTER_THROTTLE_ENABLED`; `getName` returns `Constants.THROTTLE_MASTER_NAME`; `create` returns null if disabled or constructs `DefaultThrottleMaster`.

Control flow: master startup asks the factory whether it is enabled, then `create` double-checks the config. When enabled it logs creation and lets `DefaultThrottleMaster` register itself with the registry during construction.

State and persistence: factory is stateless and thread-safe. Created master is `NoopJournaled`.

Dependencies/integration: integrates with Alluxio master factory discovery and throttle master optional configuration.

Risks: raw `MasterFactory` omits a generic type parameter. Returning null from `create` when disabled assumes caller tolerates null even though many factory flows call `isEnabled` first.

Test signals: enabled/disabled config behavior, factory name, created type, and registry registration side effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/throttle/ThrottleMasterFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/MasterUfsManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/MasterUfsManager.java

Purpose: master-side UFS manager that tracks mounted UFS roots and journaled physical UFS operation modes.

Important APIs/types/functions: extends `AbstractUfsManager` and implements `DelegatingJournaled`; `connectUfs`, `addMount`, `addMountWithRecorder`, `removeMount`, `hasMount`, `getPhysicalUfsState`, `setUfsMode`, `getDelegate`, `getJournalEntryIterator`, and nested `State`.

Control flow: mounting delegates to the abstract manager, then records the root URI and mount-id-to-root mapping. `setUfsMode` validates the root is managed, then applies and journals an `UpdateUfsModeEntry`. The nested state processes only `updateUfsMode` journal entries and emits one entry per stored mode during checkpoint iteration.

State and persistence: synchronized outer maps track managed roots and mount ids. Nested `State` persists `mUfsModes` through journal/checkpoint name `MASTER_UFS_MANAGER`. Default mode is `READ_WRITE` when no state exists for a root.

Dependencies/integration: used in `CoreMasterContext` and mount-table flows. `connectUfs` connects from the master RPC host using `NetworkAddressUtils`. Physical mode state informs file-system master behavior for reads/writes against UFS mounts.

Risks: removing a mount does not remove its root from `mUfsRoots`, so a removed physical root may remain accepted for mode updates if another mapping is absent. Journal state is separate from currently mounted IDs, so replayed modes can exist for roots not currently mounted.

Test signals: add/remove/hasMount, unknown-root rejection in `setUfsMode`, journal replay/checkpoint of modes, default read-write mode, and physical store state for multiple URIs sharing roots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/MasterUfsManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/UfsStatusCache.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/UfsStatusCache.java

Purpose: thread-safe cache from Alluxio namespace paths to UFS statuses and directory child listings, with optional asynchronous prefetch and absent-path integration.

Important APIs/types/functions: `addStatus`, `addChildren`, `remove`, `getStatus`, `hasStatus`, `fetchStatusIfAbsent`, `fetchChildrenIfAbsent`, package-private `getChildrenIfAbsent`, `getChildren`, `prefetchChildren`, and `cancelAllPrefetch`.

Control flow: explicit adds validate status name against URI basename, update absent cache, store status, and update global metrics. Child adds derive child paths and store each status plus the parent listing. Fetching a missing file resolves the mount, calls UFS `getStatus`, increments sync metrics, rewrites the status name to the Alluxio path name, and caches or records absence. Fetching children first waits for active prefetch with timeout/retry/cancel checks, then uses cached children, then optionally falls back to synchronous UFS listing.

State and persistence: all state is in concurrent maps for statuses, active prefetch jobs, and child collections. Absent state is delegated to `UfsAbsentPathCache`. No journal persistence. Metrics counters track cache size, child size, prefetch operations, retries, successes, failures, cancellations, and paths.

Dependencies/integration: integrates with `MountTable`, `RpcContext` cancellation, `UnderFileSystem`, `DefaultFileSystemMaster.Metrics`, `UfsAbsentPathCache`, and metadata sync code.

Risks: `fetchChildrenIfAbsent` removes the active prefetch job in the `finally` block even after a timeout, so later loops no longer find it in the map though they still wait on the local future. `remove` decrements status cache size for removed children even though those child statuses also remain in `mStatuses`, which can skew counters. Cached `Collection<UfsStatus>` objects may be externally mutable unless callers pass immutable collections.

Test signals: add validation, absent cache short-circuit, UFS fetch success/null/not-found/IOException, child cache metrics, prefetch reuse/cancel/failure/retry, RPC cancellation while waiting, executor rejection, and `cancelAllPrefetch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/underfs/UfsStatusCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/web/MasterWebServer.java -->
# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/web/MasterWebServer.java

Purpose: Jetty/Jersey web server for the Alluxio master REST API and optional static web UI.

Important APIs/types/functions: constructor sets up REST resources, servlet context attributes, static resources, and SPA 404 fallback; `stop` closes the filesystem client before stopping the base server. Public context keys expose the master process and filesystem client.

Control flow: construction validates `AlluxioMasterProcess`, creates a Jersey `ResourceConfig` scanning master packages and protobuf object mapper provider, creates a `FileSystem` client, and installs a custom `ServletContainer` whose `init` stores master and filesystem objects in servlet context. If `WEB_UI_ENABLED`, it sets base resources from `WEB_RESOURCES/master/build`, registers `DefaultServlet`, sets `index.html`, and maps 404s to `/`.

State and persistence: owns one `FileSystem` client to service web/REST handlers. No persistent state.

Dependencies/integration: extends `WebServer`; integrates Jersey REST packages, Jetty servlets/resources, `AlluxioMasterProcess`, `FileSystem.Factory`, and configuration for static assets.

Risks: malformed resource paths only log an error and leave REST available without UI resources. The filesystem client is created at construction and must be closed on stop. REST handlers depend on exact servlet context key names.

Test signals: web service tests should verify REST servlet registration, context attributes after init, static UI enabled/disabled behavior, 404 fallback, and filesystem client closure on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/web/MasterWebServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessEmergencyBackupTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessEmergencyBackupTest.java

Purpose: regression tests for master startup behavior when a UFS journal is corrupt and emergency backup on corruption is disabled.

Important APIs/types/functions: `before`, `failToGainPrimacyWhenJournalCorrupted`, `failToGainPrimacyWhenJournalCorruptedHA`, and helper `corruptJournalAndStartMasterProcess`.

Control flow: setup assigns reserved RPC/web ports, temp metastore/journal directories, and disables user metrics. Each test builds a UFS journal-backed `AlluxioMasterProcess`, either single-master primary selector or controllable HA selector forced to primary. The helper formats the journal, manually writes a bad delete-file entry for a non-existing path into the file-system master's UFS journal, starts the master, expects a runtime exception containing `NoSuchElementException`, stops the process, and verifies it is stopped.

State and persistence: manipulates real temporary UFS journal files. It deliberately corrupts journal replay state, not in-memory master state.

Dependencies/integration: uses UFS journal system classes, `UfsJournalLogWriter`, `NoopMaster`, `ControllablePrimarySelector`, and port/temp-folder JUnit rules.

Risks: the test asserts on exception message content from lower-level replay, so refactors that wrap exceptions differently may require updating expectations without changing behavior.

Test signals: protects fail-fast startup on corruption when backup is disabled, for both single-master and HA-primary paths, and verifies failed startup still leaves the process stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessEmergencyBackupTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessTest.java

Purpose: parameterized integration-style tests for `AlluxioMasterProcess` lifecycle under combinations of standby web and standby metrics settings.

Important APIs/types/functions: parameter data for four config combinations; `before`; tests `startStopPrimary`, `startStopStandby`, `startMastersThrowsUnavailableException`, ignored `stopAfterStandbyTransition`, ignored `restoreFromBackupLocal`, `startStopStandbyStandbyServer`; helpers `startStopTest`, `waitForSocketServing`, and `isBound`.

Control flow: tests configure temp ports, metastore, metrics, and journal folders, register RPC/web/metrics services, start the master in a thread, wait for socket or service readiness, then stop and assert ports are free. Standby tests vary expectations for real gRPC/web/metric serving according to config. The unavailable-start test spies `startMasterComponents` to throw `UnavailableException` and verifies the start loop does not exit as a success failure under demotion-exit config.

State and persistence: uses `NoopJournalSystem` for most cases and temporary directories for config isolation. It observes service state through sockets and service readiness rather than direct journal state.

Dependencies/integration: exercises `RpcServerService`, `WebServerService`, `MetricsService`, primary selectors, network address utilities, and master process service orchestration.

Risks: port binding tests can be timing-sensitive despite waits. Ignored tests document important but currently disabled behavior around demotion exit and restore-from-backup-local.

Test signals: protects primary and standby service binding, rejecting-server behavior, standby-enabled server modes, metric sink modes, clean shutdown of ports, and start-loop resilience to unavailable master component startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlluxioMasterProcessTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlwaysPrimaryPrimarySelector.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlwaysPrimaryPrimarySelector.java

Purpose: test `PrimarySelector` implementation that permanently reports primary state.

Important APIs/types/functions: `start`, `stop`, `getState`, `getStateUnsafe`, `onStateChange`, and `waitForState`.

Control flow: lifecycle methods do nothing; state getters return `NodeState.PRIMARY`; listener registration returns a no-op scoped handle; waiting for PRIMARY returns immediately while waiting for STANDBY sleeps indefinitely.

State and persistence: stateless and non-persistent.

Dependencies/integration: used by `MasterTestUtils` and block/master tests requiring a primary master context without real leader election.

Risks: waiting for standby intentionally blocks forever, so tests must not call it except when verifying blocking behavior. It never emits state-change callbacks.

Test signals: useful as a fixture; behavior is simple enough to be validated by consumers that require primary startup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/AlwaysPrimaryPrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/BackupManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/BackupManagerTest.java

Purpose: unit tests for backup behavior with server-module metastore dependencies, especially Rocks iterator handling.

Important APIs/types/functions: setup/teardown; helpers `createNewBlock`, `createNewFile`, `createRootDir`; tests `rocksBlockStoreIteratorClosed` and `rocksInodeStoreIteratorNotUsed`.

Control flow: setup creates a master registry, manual clock, and executor. The block-store test mocks `RocksBlockMetaStore.getCloseableIterator` to return a close-tracking iterator, starts metrics and block masters, runs `BackupManager.backup`, and asserts the iterator closed. The inode-store test mocks `RocksInodeStore` so global iterator throws but root `getChildren` works, starts block and filesystem masters, runs backup, and expects no exception.

State and persistence: writes backup output to temporary files and constructs real master registry state with mocked stores. No permanent repo artifacts.

Dependencies/integration: exercises `BackupManager`, `DefaultBlockMaster`, `DefaultFileSystemMaster`, heap and Rocks metastore interfaces, `MetricsMasterFactory`, and `MasterTestUtils`.

Risks: tests depend on backup traversal strategy. The inode test ensures backup walks the inode tree through child iteration instead of using unsupported full Rocks inode iteration.

Test signals: protects resource closure for block iterators and avoids using a disallowed Rocks inode iterator during backup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/BackupManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/ControllablePrimarySelector.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/ControllablePrimarySelector.java

Purpose: test primary selector whose state can be manually changed through inherited `AbstractPrimarySelector` behavior.

Important APIs/types/functions: overrides `start` and `stop` as no-ops; inherits `setState`, `getState`, listeners, and waiting behavior from `AbstractPrimarySelector`.

Control flow: tests instantiate it, call `setState(NodeState.PRIMARY/STANDBY)`, then pass it into master process or context code. Starting/stopping does not contact external election systems.

State and persistence: state is inherited in memory. No persistence.

Dependencies/integration: used by HA-flavored master process tests and emergency backup tests to force primary transitions.

Risks: class comment references `setState(State)` though actual state type is `NodeState` in consumers. Because start does nothing, tests must set initial state explicitly or inherited default behavior may be wrong for the scenario.

Test signals: useful for deterministic promotion/demotion tests, listener tests, and code paths that need primary selector state without real journal election.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/ControllablePrimarySelector.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MasterTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MasterTestUtils.java

Purpose: central helper for creating `CoreMasterContext` instances in unit tests with lightweight journal, metastore, safe-mode, backup, and UFS components.

Important APIs/types/functions: overloaded `testMasterContext` methods accepting journal system, user state, primary selector, block store factory, and inode store factory.

Control flow: simple overloads funnel to the full builder call. Defaults are `NoopJournalSystem`, heap block/inode stores, `AlwaysStandbyPrimarySelector` or `AlwaysPrimaryPrimarySelector` depending on overload, mocked `BackupManager`, `TestSafeModeManager`, start time/port `-1`, and new `MasterUfsManager`.

State and persistence: constructs in-memory contexts. Journal behavior depends on the supplied `JournalSystem`, but defaults are no-op.

Dependencies/integration: used widely by block, file, metastore, backup, and metrics master tests to avoid duplicating context setup.

Risks: default primary selector differs by overload, so tests must choose carefully. Mocked backup manager and test safe mode manager may hide behavior that full process tests need.

Test signals: consumers validate it indirectly. Direct tests would verify builder fields and supplied factories/selectors are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MasterTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MockMaster.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MockMaster.java

Purpose: minimal fake `Master` implementation for journal tests.

Important APIs/types/functions: constructor initializes an entry queue; `processJournalEntry` enqueues entries and returns true; `getJournalEntryIterator` returns a closeable iterator over queued entries; `createJournalContext` throws; other lifecycle/service/dependency methods are no-ops or null; `getCheckpointName` returns `NOOP`.

Control flow: journal replay or writer tests can hand entries to the fake master and later iterate them. It cannot create new journal contexts, so it is read/replay oriented.

State and persistence: in-memory `ArrayDeque<JournalEntry>`. No real persistence.

Dependencies/integration: implements `Master` and is used in UFS journal corruption setup where a journal object needs a master target.

Risks: methods returning null can break code expecting non-null master services/dependencies/context. Not thread-safe.

Test signals: use only where a simple journal receiver is sufficient; avoid for lifecycle tests requiring real master context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/MockMaster.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/SafeModeManagerTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/SafeModeManagerTest.java

Purpose: unit tests for `DefaultSafeModeManager` timing and notification behavior.

Important APIs/types/functions: setup with `ManualClock`; tests `defaultSafeMode`, primary/RPC start notifications, leaving safe mode after RPC wait time, staying safe after primary start, and re-entering safe mode while already in safe mode.

Control flow: configuration rule sets `MASTER_WORKER_CONNECT_WAIT_TIME` to 100 ms. Tests drive notifications, advance manual clock, and assert `isInSafeMode`. RPC-server start establishes a timer after which safe mode exits; primary-master start keeps or resets safe mode without an exit timer.

State and persistence: only in-memory safe-mode manager state and manual clock. No persistence.

Dependencies/integration: validates the manager used by master process and notified by `RpcServerService.startGrpcServer`.

Risks: expected behavior is time-sensitive but deterministic through `ManualClock`. It does not test concurrent notifications.

Test signals: protects startup safe mode default, RPC wait timeout exit, primary start staying safe, timer reset on repeated RPC notification, and timer clearing on primary notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/SafeModeManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/TestSafeModeManager.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/TestSafeModeManager.java

Purpose: no-op safe mode manager for tests that do not want safe-mode behavior.

Important APIs/types/functions: implements `notifyPrimaryMasterStarted`, `notifyRpcServerStarted`, and `isInSafeMode`.

Control flow: notification methods do nothing and `isInSafeMode` always returns false.

State and persistence: stateless and non-persistent.

Dependencies/integration: installed by `MasterTestUtils.testMasterContext` so unit tests using the context are not blocked by safe mode.

Risks: hides safe-mode gating from tests. Code whose correctness depends on safe-mode transitions should use `DefaultSafeModeManager` instead.

Test signals: fixture behavior is trivial; consumers validate it by proceeding without safe-mode waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/TestSafeModeManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterMetricsTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterMetricsTest.java

Purpose: unit tests for block master gauge registration and values exposed through `DefaultBlockMaster.Metrics`.

Important APIs/types/functions: setup clears metrics, mocks `DefaultBlockMaster`, supplies a `DefaultStorageTierAssoc`, and calls `Metrics.registerGauges`; tests capacity totals/free/used, tier capacity metrics, unique block count, and worker count.

Control flow: each test stubs block master methods, then reads gauges directly from `MetricsSystem.METRIC_REGISTRY` by metric key and tag suffix. Free capacity is validated as total minus used at both cluster and tier levels.

State and persistence: manipulates global metrics registry only; no master persistence.

Dependencies/integration: ties block master metric keys to `MetricsSystem` and storage tier association.

Risks: global registry requires clearing before tests to avoid stale gauges. Gauge names depend on tag string construction using `MetricInfo.TIER`.

Test signals: protects cluster capacity gauges, tier-tagged capacity gauges, unique block gauge, and worker count gauge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterMetricsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTest.java

Purpose: broad unit test suite for `BlockMaster` worker registration, worker state transitions, block metadata, heartbeats, decommissioning, metrics dependencies, and container id reservation.

Important APIs/types/functions: setup creates a `DefaultBlockMaster` with `MetricsMaster`, `MasterRegistry`, `ManualClock`, and no-op journal context; helper stream registration functions generate `RegisterWorkerPRequest` chunks and send them to `BlockMasterWorkerServiceHandler`; tests cover build version, capacity accounting, lost/decommissioned workers, register/stream-register upgrade scenarios, block removal, heartbeat deltas, lost storage, unknown workers, executor shutdown, `getBlockInfo`, and concurrent `getNewContainerId`.

Control flow: most tests register workers through direct or streaming APIs, mutate clock or worker state, invoke heartbeats/commits/removals, then assert worker reports, command types, block locations, and counts. Decommission upgrade tests ensure a worker can be decommissioned with `canRegisterAgain`, continue sending cleanup heartbeats/commits, then re-register with a newer build version. Removal upgrade tests verify stale blocks are scheduled for freeing after re-registration.

State and persistence: exercises in-memory block master worker/block maps plus journal-reserved container ids under a no-op journal system. Manual heartbeat scheduling drives lost worker detection. The executor service is owned by the master and shutdown is asserted.

Dependencies/integration: integrates `DefaultBlockMaster`, `MetricsMasterFactory`, `MasterTestUtils`, `HeartbeatScheduler`, worker protobuf commands, register streaming, and block metadata wire types.

Risks: tests rely on constants for medium/tier strings and manual heartbeat contexts. Concurrent container id test asserts reservation bounds rather than exact journal entry count. The suite is large enough that shared setup global configuration can affect later tests if not reset by rules.

Test signals: protects build version propagation, live/lost/decommissioned counts, auto-deletion of lost workers, re-registration after loss or decommission, block location visibility for decommissioned workers, worker heartbeat add/remove/lost-storage effects, orphaned block cleanup commands, unknown-worker register command, executor termination, block info shape, and thread-safe container id reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTestUtils.java

Purpose: assertion helpers for block master tests.

Important APIs/types/functions: `verifyBlockOnWorkers`, `verifyBlockNotExisting`, and `findWorkerInfo`.

Control flow: `verifyBlockOnWorkers` fetches block info, checks length and location count, constructs expected `BlockLocation` objects from worker IDs/addresses with MEM medium/tier, and compares as sets. `verifyBlockNotExisting` asserts `getBlockInfo` throws `BlockInfoException`. `findWorkerInfo` searches a list by worker id or throws assertion error.

State and persistence: no state or persistence.

Dependencies/integration: used by block master test suites to reduce repeated location assertions. Assumes MEM medium/tier for expected locations.

Risks: helper is specialized to MEM locations and will be wrong for tests involving other media unless extended. Set comparison ignores ordering by design.

Test signals: supports clear assertions for block existence, non-existence, and worker lookup in block master tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/block/BlockMasterTestUtils.java -->
