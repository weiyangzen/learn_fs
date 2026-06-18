# Research: subset-b-000486

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksInodeStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksInodeStoreTest.java

## Purpose
`RocksInodeStoreTest` is a JUnit test suite for `RocksInodeStore`, focused on inode persistence, batch writes, iterator formatting, and concurrent interaction between read paths and destructive or exclusive operations such as close, checkpoint, restore, and clear. It is especially concerned with RocksDB shared/exclusive lock correctness and reader behavior when the underlying store generation changes.

## Important APIs, Types, and Functions
The suite exercises `RocksInodeStore.createWriteBatch`, `writeInode`, `addChild`, `get`, `getMutable`, `getChildIds`, `getCloseableIterator`, `writeToCheckpoint`, `restoreFromCheckpoint`, `clear`, and `close`. Test helpers include `submitListingJob`, `submitIterJob`, `submitGetInodeJob`, `submitAddInodeJob`, and the scenario helpers `testConcurrentReaderAndClose`, `testConcurrentReaderAndCheckpoint`, `testConcurrentReaderAndRestore`, and `testConcurrentReaderAndClear`. The nested `FlakyRocksInodeStore` wraps a delegate iterator and throws from `hasNext` or `next` to validate lock cleanup on iterator exceptions. `QuadFunction` lets the same concurrency harness run against list, get, and add workloads.

## Control Flow, State, and Persistence
`setUp` enables Alluxio test mode, configures the Rocks exclusive-lock timeout, creates a temporary Rocks store, and starts a cached executor. Most concurrency tests first call `prepareFiles` to create 400 directory inodes under parent 0, then start 20 reader/writer tasks. Latches stop tasks mid-stream, an exclusive store operation runs, and the tasks are released so the test can assert either completion, empty reads, or abort behavior. Checkpoint tests persist the database into a temp file through `writeToCheckpoint`; restore tests replay that file through `CheckpointInputStream`. Persistent state is limited to temporary RocksDB directories and checkpoint files.

## Dependencies and Integration Points
The file integrates the inode metastore with `MutableInodeDirectory`, `CreateDirectoryContext`, `ReadOption`, Alluxio configuration keys, checkpoint streams, and `CloseableIterator`. It also depends on `RocksStoreTestUtils.waitForReaders` to join asynchronous readers and on JUnit `TemporaryFolder` for isolated Rocks state.

## Risks
The tests are timing sensitive because they depend on 20 worker threads reaching a latch point before an exclusive operation. Test mode is deliberately disabled in long-running iterator cases so forced exclusive-lock behavior can be exercised; forgetting to restore global configuration in nearby tests can affect later suites. The list-reader abort expectations intentionally allow either completed readers or errors depending on scheduling. The `FlakyRocksInodeStore` creates an unused superclass Rocks store path, so resource lifetime must be watched if expanded.

## Test Signals
Useful signals are the full `RocksInodeStoreTest` suite, especially `longRunningIterAndRestore`, `longRunningIterAndCheckpoint`, and the `concurrent*` matrix. Passing tests indicate that shared lock counts return to zero, iterator exceptions close resources, checkpoints are non-empty, restore invalidates stale iterators, and the store remains usable after checkpoint/restore/clear scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksInodeStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTest.java

## Purpose
`RocksStoreTest` validates the lower-level `RocksStore` wrapper around RocksDB. It covers backup and restore, shared-lock reference counting, exclusive-lock modes for closing, checkpointing, and rewriting, and precedence rules when multiple exclusive operations overlap.

## Important APIs, Types, and Functions
The suite constructs `RocksStore` with explicit `DBOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, and an `AtomicReference<ColumnFamilyHandle>`. It exercises `checkAndAcquireSharedLock`, `lockForClosing`, `lockForCheckpoint`, `lockForRewrite`, `writeToCheckpoint`, `restoreFromCheckpoint`, `getDb`, `close`, `getSharedLockCount`, `isServiceStopping`, and `shouldAbort`. It asserts error semantics through `UnavailableRuntimeException` and `ExceptionMessage.ROCKS_DB_CLOSING` or `ROCKS_DB_REWRITTEN`.

## Control Flow, State, and Persistence
`setup` creates temporary Rocks and backup directories, initializes a single column family with a fixed-length long prefix extractor, and opens a test store. `backupRestore` writes keys into RocksDB under a shared lock, serializes a checkpoint, closes the store under a closing lock, opens a new store, restores under a rewrite lock, and verifies the keys. Lock tests acquire long-lived shared locks in executor tasks, then attempt exclusive operations with `TEST_MODE` either enabled to reject forced takeover or disabled to permit it. Exclusive-operation ordering tests assert that close has higher priority than checkpoint/rewrite and that checkpoint blocks rewrite.

## Dependencies and Integration Points
This test directly integrates with RocksDB Java objects (`RocksDB`, `WriteOptions`, `RocksObject`, `ColumnFamilyHandle`) and Alluxio metastore lock handles (`RocksSharedLockHandle`, `RocksExclusiveLockHandle`). It relies on Alluxio configuration keys for timeout and test mode and on checkpoint streams for restore.

## Risks
The suite deliberately manipulates global `Configuration` and forced-lock behavior, so isolation matters. Concurrent tests rely on latch ordering and a short lock timeout, making them sensitive to slow or overloaded CI environments. `tearDown` closes Rocks objects in reverse order, but earlier assertion failures inside lock scenarios can still leave resources to be closed by the teardown path.

## Test Signals
Passing tests show that reference counts do not go negative or leak after forced exclusive locks, readers may continue after checkpoint but not after rewrite, closing state is sticky, and backup/restore preserves column-family data. Any failures in these tests should be treated as high-risk for master metastore durability or shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTestUtils.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTestUtils.java

## Purpose
`RocksStoreTestUtils` is a tiny test utility class shared by Rocks metastore tests. It centralizes waiting on asynchronous reader futures so failures in background tasks surface as JUnit failures.

## Important APIs, Types, and Functions
The only public API is `waitForReaders(List<Future<Void>> futures)`. It iterates over each future, calls `get`, and fails the test if any future throws.

## Control Flow, State, and Persistence
The helper has no state and no persistence. It synchronously joins all submitted tasks in order. If `Future.get` throws, the exception stack trace is printed and `Assert.fail` is invoked with the exception message.

## Dependencies and Integration Points
It depends on Java `Future` and JUnit `fail`. It is imported by `RocksInodeStoreTest` to join reader/list/add task batches after latch-controlled concurrent operations.

## Risks
The helper does not enforce a timeout, so a deadlocked test worker can hang the suite. It prints stack traces directly, which is useful for local diagnosis but can add noise in CI logs. It preserves interrupt state only indirectly through the thrown exception path.

## Test Signals
The utility is indirectly covered by Rocks metastore concurrency tests. A good signal is that background task exceptions fail the owning test instead of being silently dropped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metastore/rocks/RocksStoreTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsMasterTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsMasterTest.java

## Purpose
`MetricsMasterTest` verifies `DefaultMetricsMaster` behavior around throughput gauges and cluster metric aggregation. It checks that master-local counters and timers are translated into cluster-visible metrics on the manually scheduled metrics heartbeat.

## Important APIs, Types, and Functions
The fixture creates `DefaultMetricsMaster` with `MasterTestUtils.testMasterContext`, a `ManualClock`, and a constant executor-service factory. Tests use `registerThroughputGauge`, `addAggregator`, `MetricsSystem.counter`, `MetricsSystem.timer`, `MetricsSystem.getMetricValue`, `Metric.getMetricNameWithTags`, `SingleTagValueAggregator`, and `HeartbeatScheduler.execute`.

## Control Flow, State, and Persistence
`before` clears all metrics, builds a `MasterRegistry`, registers the metrics master, and starts it as leader. `testThroughputGauge` increments a master counter and advances the manual clock to assert per-minute throughput calculation. `testRegisteredAggregator` creates UFS-tagged master counters/timers and manually triggers `MASTER_CLUSTER_METRICS_UPDATER`. `testMultiValueAggregator` creates per-UFS counters and verifies distinct cluster metrics are created after heartbeat execution. State is in the global in-memory `MetricsSystem` registry.

## Dependencies and Integration Points
This test touches the master registry lifecycle, heartbeat scheduler, Alluxio metric naming/tag escaping, Dropwizard `Counter` and `Gauge`, and cluster aggregator implementations. It relies on `ManuallyScheduleHeartbeat` to make background aggregation deterministic.

## Risks
Global metric state can leak if setup/teardown is bypassed. Throughput values depend on the manual clock and cumulative counter deltas, so changes to gauge semantics can break expectations. The UFS operation test selects the first `MetricInfo.UfsOps` enum value, which keeps the test generic but ties it to enum stability.

## Test Signals
Passing tests show that throughput gauges are registered and compute expected rates, UFS operation aggregators merge counter and timer counts, and multi-value aggregation keeps separate values by tag. These are strong unit signals for master cluster metric publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsMasterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsStoreTest.java

## Purpose
`MetricsStoreTest` validates `MetricsStore`, the component that accepts worker and client metric reports and updates cluster-level counters. It covers worker metrics, client metrics, UFS-tagged worker metrics, and clearing/reset time behavior.

## Important APIs, Types, and Functions
The test fixture uses `MetricsStore.initMetricKeys`, `putWorkerMetrics`, `putClientMetrics`, `clear`, and `getLastClearTime`. It builds `Metric` objects through `Metric.from`, uses `MetricKey` constants for worker/client/cluster metrics, and derives tagged metric names through `Metric.getMetricNameWithTags` plus `MetricInfo.TAG_UFS`.

## Control Flow, State, and Persistence
`before` resets the global `MetricsSystem`, creates a `MetricsStore` with `SystemClock`, and initializes metric keys. Each test submits synthetic metric batches for hosts or clients, then reads the corresponding cluster counter. UFS metrics are grouped by escaped UFS URI and also update all-UFS aggregate counters. `clearAndGetClearTime` records the previous clear time, writes metrics, sleeps briefly to avoid same-millisecond timestamps, clears the store, and asserts counters reset and clear time advances.

## Dependencies and Integration Points
The store integrates with Alluxio metric naming, Dropwizard counters via `MetricsSystem`, gRPC `MetricType`, and URI escaping for tagged UFS metrics.

## Risks
The tests rely on global in-memory metric state and real clock progression. `Thread.sleep(10)` reduces but does not eliminate timing sensitivity on extremely coarse or overloaded environments. Metric-name parsing is implicit in the store under test, so renamed metric keys can invalidate expectations.

## Test Signals
Passing tests show that metrics from multiple workers and clients are accumulated correctly, UFS metrics are split by UFS tag and summed globally, and `clear` resets cluster counters while updating the clear timestamp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/MetricsStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/TimeSeriesStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/TimeSeriesStoreTest.java

## Purpose
`TimeSeriesStoreTest` validates the in-memory metric time-series recorder used by the master metrics layer. It checks single-series recording, multiple named series, and preservation of point order.

## Important APIs, Types, and Functions
The tests use `TimeSeriesStore.record`, `getTimeSeries`, `TimeSeries.getName`, and `TimeSeries.getDataPoints`. Assertions inspect data-point counts and values.

## Control Flow, State, and Persistence
Each test creates a fresh `TimeSeriesStore`. `recordTimeSeries` records two values under one metric name, with a short sleep to avoid same-millisecond timestamps. `recordMultipleTimeSeries` records distinct metric names and locates both resulting `TimeSeries` objects. `orderedTimeSeries` records two values and polls the queue to verify insertion order. State is in-memory only.

## Dependencies and Integration Points
The test depends on Alluxio `TimeSeries`, `TimeSeriesStore`, and `CommonUtils.sleepMs`. It integrates with the metric time-series data model consumed by monitoring and reporting paths.

## Risks
The test uses real sleeps to separate timestamps and mutates the data-point queues via `poll` in order checks. If the store changes from queue-like storage to immutable snapshots, this test would need updates.

## Test Signals
Passing tests show that metric names are grouped, multiple series coexist, values are retained, and data points are returned in record order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/metrics/TimeSeriesStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/jvmmonitor/JvmMonitorServiceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/jvmmonitor/JvmMonitorServiceTest.java

## Purpose
`JvmMonitorServiceTest` verifies the simple-service wrapper around the JVM pause monitor. It checks factory selection, metric registration on start, lifecycle stability across primary/standby transitions, and protection against double start.

## Important APIs, Types, and Functions
The tests use `JvmMonitorService.Factory.create`, `SimpleService.start`, `promote`, `demote`, and `stop`, plus `MetricsSystem.startSinks`, `clearAllMetrics`, `stopSinks`, and `allMetrics`. `checkMetrics` counts registered metric names containing `Server.`.

## Control Flow, State, and Persistence
`before` starts metrics sinks from the configured metrics file; `after` clears metrics and stops sinks. With `MASTER_JVM_MONITOR_ENABLED=false`, the factory must return `NoopService`. With it enabled, start registers three JVM monitor metrics, promote/demote leave them present, and stop does not unregister them. `doubleStart` asserts a second `start` throws `IllegalStateException`.

## Dependencies and Integration Points
The file integrates master simple-service lifecycle code with `JvmMonitorService`, `NoopService`, Alluxio configuration, and the global metrics system.

## Risks
Metric counting by substring is broad and can become fragile if other `Server.` metrics are registered in the same global registry. The test starts metrics sinks, so environmental metrics configuration problems can affect it.

## Test Signals
Passing tests show the factory respects configuration, startup registers the expected JVM monitor gauges, role transitions are idempotent for metrics, and duplicate start is rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/jvmmonitor/JvmMonitorServiceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/metrics/MetricsServiceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/metrics/MetricsServiceTest.java

## Purpose
`MetricsServiceTest` verifies which metrics simple-service implementation is selected for a master and how it manages `MetricsSystem` lifecycle in primary and standby roles.

## Important APIs, Types, and Functions
The tests use `MetricsService.Factory.create`, `AlwaysOnMetricsService`, `PrimaryOnlyMetricsService`, `start`, `promote`, `demote`, `stop`, and `MetricsSystem.isStarted`. Configuration is driven by `STANDBY_MASTER_METRICS_SINK_ENABLED`.

## Control Flow, State, and Persistence
When standby metrics sinks are enabled, the factory returns `AlwaysOnMetricsService`; `start` starts `MetricsSystem`, and repeated promote/demote cycles keep it running until `stop`. When standby metrics sinks are disabled, `PrimaryOnlyMetricsService` keeps metrics stopped on `start`, starts them on promote, stops them on demote, and leaves them stopped after `stop`. State is the global metrics-system started flag.

## Dependencies and Integration Points
The test integrates simple-service role transitions with the global metrics subsystem and Alluxio master standby configuration.

## Risks
Because the test reads global `MetricsSystem.isStarted`, previous tests that fail to stop metrics can contaminate results. The test does not clear metric contents, only started/stopped state.

## Test Signals
Passing tests show that standby metrics are either always emitted or primary-only according to configuration and that service stop leaves the metrics system stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/metrics/MetricsServiceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTest.java

## Purpose
`RpcServerServiceTest` verifies RPC service lifecycle when standby master gRPC is disabled. In this mode, standby binds a rejecting server while the real RPC server only serves in primary state.

## Important APIs, Types, and Functions
The suite extends `RpcServerServiceTestBase` and uses `RpcServerService.Factory.create`, `start`, `promote`, `demote`, `stop`, `isServing`, `isGrpcBound`, and `waitForFree`. It configures `STANDBY_MASTER_GRPC_ENABLED=false`.

## Control Flow, State, and Persistence
`before` disables standby gRPC. `primaryOnlyTest` creates a service on a reserved port, confirms the socket is free, starts the service, and asserts the port is bound but not serving. Repeated promote/demote cycles toggle `isServing` while the port remains bound. Stop unbinds the port. Double-start tests assert that starting the rejecting server twice and promoting the RPC server twice throw `IllegalStateException`.

## Dependencies and Integration Points
The test uses PowerMock/Mockito through the base class to mock `AlluxioMasterProcess`, create a `GrpcServerBuilder`, and avoid real master services. It touches master registry, port reservation, sockets, and gRPC server lifecycle.

## Risks
Socket probing can be flaky on slow CI or systems with delayed port release. The asserted exception messages are literal and can drift with implementation wording.

## Test Signals
Passing tests show that standby-without-gRPC still occupies the RPC port with a rejecting server, primary promotion swaps into serving mode, demotion stops serving without freeing the socket, and duplicate lifecycle calls are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTestBase.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTestBase.java

## Purpose
`RpcServerServiceTestBase` provides shared fixtures for RPC simple-service tests. It reserves a port, mocks an `AlluxioMasterProcess`, and supplies socket helpers for testing whether the gRPC endpoint is bound.

## Important APIs, Types, and Functions
The base exposes `mPort`, `mRegistry`, `mRpcAddress`, and `mMasterProcess`. `setUp` stubs `createBaseRpcServer`, `createRpcExecutorService`, and `getSafeModeManager`. Helper methods are `isGrpcBound`, `isBound`, and `waitForFree`.

## Control Flow, State, and Persistence
Before each subclass test, a reserved port is converted to an `InetSocketAddress`, and the mocked master process returns a `GrpcServerBuilder` for that address with global configuration. Socket checks attempt a TCP connection to the reserved address. `waitForFree` polls until no connection can be made or a one-second timeout expires. There is no persistence.

## Dependencies and Integration Points
The base integrates JUnit `PortReservationRule`, Mockito/PowerMockito, Alluxio `GrpcServerBuilder`, `GrpcServerAddress`, `MasterRegistry`, and `CommonUtils.waitFor`.

## Risks
The helper treats any non-`ConnectException` I/O error as a runtime failure. Address binding uses `address.getAddress()` and port, so unresolved or unusual host handling could affect socket checks. The one-second wait can be short on heavily loaded systems.

## Test Signals
The base is indirectly covered by both standby-disabled and standby-enabled RPC service tests. Reliable socket-free and socket-bound checks are required for those suites to be meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerStandbyGrpcServiceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerStandbyGrpcServiceTest.java

## Purpose
`RpcServerStandbyGrpcServiceTest` verifies RPC service lifecycle when standby master gRPC is enabled. In this mode the real gRPC server remains serving in both standby and primary states.

## Important APIs, Types, and Functions
The class extends `RpcServerServiceTestBase` and uses `RpcServerService.Factory.create`, lifecycle methods, `isServing`, and socket helpers. `setUp` reloads configuration, sets `STANDBY_MASTER_GRPC_ENABLED=true`, then delegates to the base setup.

## Control Flow, State, and Persistence
`primaryOnlyTest` creates the service, starts it, and asserts the socket is bound and `isServing` is true immediately. Promote and demote cycles keep both the port binding and serving flag true. Stop clears serving state and releases the port. `doubleStartRpcServer` checks that double promotion and double demotion are rejected.

## Dependencies and Integration Points
This test integrates with the same mocked master-process gRPC builder as the base, but covers the always-on standby gRPC configuration branch.

## Risks
It relies on global configuration reload to isolate from other tests. Socket release timing remains a CI risk. Literal exception messages are part of the assertion contract.

## Test Signals
Passing tests show that standby gRPC keeps the server available across role transitions and that invalid duplicate promote/demote calls fail rather than silently corrupting lifecycle state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerStandbyGrpcServiceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/web/WebServerServiceTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/web/WebServerServiceTest.java

## Purpose
`WebServerServiceTest` verifies master web service lifecycle for both primary-only and always-on standby modes. It asserts port binding, serving-state changes, and duplicate lifecycle rejection.

## Important APIs, Types, and Functions
The tests use `WebServerService.Factory.create`, `PrimaryOnlyWebServerService`, `AlwaysOnWebServerService`, `start`, `promote`, `demote`, `stop`, and `isServing`. The fixture mocks `AlluxioMasterProcess.createWebServer` to return a `MasterWebServer` bound to a reserved port.

## Control Flow, State, and Persistence
`setUp` reserves a web port and stubs the master process. With `STANDBY_MASTER_WEB_ENABLED=false`, `start` binds a rejecting server while `isServing` remains false; promote/demote toggles serving while the socket stays bound; stop releases the socket. With standby web enabled, `start` serves immediately and promote/demote keep it serving. Double-start tests assert duplicate rejecting-server or web-server startup throws.

## Dependencies and Integration Points
The test integrates master simple services with Jetty-backed `MasterWebServer`, Alluxio network service naming, configuration, sockets, and `CommonUtils.waitFor`.

## Risks
Socket polling can be affected by slow port release. The test relies on the mocked web server being close enough to real server behavior for lifecycle semantics. Literal exception message checks can fail after harmless text changes.

## Test Signals
Passing tests show that master web UI/API availability matches standby configuration, that rejected standby mode still owns the port, and that repeated start calls are guarded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/web/WebServerServiceTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/throttle/IndicatorsTests.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/throttle/IndicatorsTests.java

## Purpose
`IndicatorsTests` validates `ServerIndicator`, the object used by throttling logic to snapshot and compare server resource indicators such as memory, CPU load, JVM pause time, RPC queue size, and Netty direct memory.

## Important APIs, Types, and Functions
The tests use `ServerIndicator.createFromMetrics`, copy/multiply constructors, `addition`, `reduction`, and getter methods for direct memory, Netty direct memory, heap max/used, CPU load, JVM pause values, RPC queue size, and snapshot time. The fixture starts a `JvmPauseMonitor` and registers JVM pause gauges.

## Control Flow, State, and Persistence
`before` enables JVM monitor configuration, starts a static `JvmPauseMonitor`, and registers three gauges in `MetricsSystem`. `basicIndicatorCreationTest` allocates direct buffers, captures indicators before and after a sleep, and compares direct memory and time fields. `basicIndicatorComparisonTest` constructs fixed indicators, verifies multiplication, reduction deltas, and addition/reduction aggregation arithmetic. State is runtime metric state and JVM memory allocation.

## Dependencies and Integration Points
The test integrates throttling indicators with `MetricsSystem`, `MetricKey`, direct buffer accounting, and JVM pause monitor metrics.

## Risks
Direct memory accounting can be JVM- and GC-sensitive. The first test uses real sleeps and assumes allocated direct buffers remain accounted for. The fixture starts a static monitor and stops it afterward, so failures before teardown can affect later tests.

## Test Signals
Passing tests show that server indicator snapshots can be built from metrics, time progresses, direct memory values are stable across snapshots, and arithmetic operations produce expected aggregate and delta indicators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/throttle/IndicatorsTests.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/underfs/UfsStatusCacheTest.java -->
# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/underfs/UfsStatusCacheTest.java

## Purpose
`UfsStatusCacheTest` validates `UfsStatusCache`, which caches UFS path statuses and child listings and supports asynchronous prefetch. It covers add/remove semantics, child association, fallback fetches, cancellation, rejected executor submissions, single-status fetches, and handling of duplicate child names under different parents.

## Important APIs, Types, and Functions
The tests exercise `addStatus`, `remove`, `getStatus`, `addChildren`, `getChildren`, `prefetchChildren`, `cancelAllPrefetch`, `fetchChildrenIfAbsent`, `fetchStatusIfAbsent`, and `getChildrenIfAbsent`. Fixtures include `LocalUnderFileSystem`, `MountTable`, `MasterUfsManager`, `MountInfo`, `NoopUfsAbsentPathCache`, `RpcContext`, `OperationContext`, and `CallTracker`. Helpers `spyUfs`, `createUfsFile`, and `createUfsDirs` create local UFS state and Mockito spies.

## Control Flow, State, and Persistence
`before` creates a temporary local UFS root, a single-thread executor, a cache, and a root mount table. Simple tests add mocked `UfsStatus` entries and verify cache hits/removal. Prefetch tests submit background child-listing jobs and then fetch or cancel them. Failure tests mock slow or throwing UFS `listStatus` and verify interrupt/cancellation behavior. Rejected-execution tests use a one-thread `ThreadPoolExecutor` with a `SynchronousQueue` to force prefetch rejection while a first job is blocked. Single-status tests call UFS `getStatus` only when the cache lacks a value. Persistent state is temporary local filesystem content under the JUnit folder.

## Dependencies and Integration Points
This file integrates the master mount table and UFS manager with local UFS implementation, absent-path cache policy, Alluxio URI/path utilities, RPC cancellation tracking, and Java executor/future behavior.

## Risks
Several tests depend on thread timing, locks, and cancellation visibility. The interrupted-fetch test sleeps for 30 hours in the mocked UFS call and relies on thread interruption to avoid hanging. The cache behavior around `fetchStatusIfAbsent` verifies the underlying UFS call count even when a status exists, so implementation changes must preserve or intentionally revise that contract. Path/name validation is sensitive to `UfsStatus.getName`.

## Test Signals
Passing tests indicate that cached statuses and children are keyed by full path, prefetch deduplicates in-flight jobs by path, cancellation propagates, rejected prefetch submissions return null, fallback synchronous fetch works, and status fetch errors return null rather than surfacing UFS exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/underfs/UfsStatusCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/pom.xml -->
# sources/distributed-fs/alluxio/core/server/pom.xml

## Purpose
This Maven POM defines the `alluxio-core-server` aggregator module. It groups Alluxio core server submodules under a single Maven parent and keeps build path properties available when Maven is invoked from this subtree.

## Important APIs, Types, and Functions
The file is declarative XML rather than executable code. Its important elements are the parent `org.alluxio:alluxio-core:2.10.0-SNAPSHOT`, artifact ID `alluxio-core-server`, packaging `pom`, and modules `common`, `master`, `proxy`, and `worker`.

## Control Flow, State, and Persistence
There is no runtime control flow. Maven uses the module list to order reactor builds and test execution. The `build.path` property points back to the repository `build` directory through `${project.parent.parent.basedir}`.

## Dependencies and Integration Points
This POM integrates the core server subtree with the broader Alluxio build. Its child modules include the master tests and proxy sources researched in this work item.

## Risks
Changing module names or ordering can break Maven reactor builds and downstream modules that rely on this aggregation. The relative `build.path` property exists to support running Maven from sub-project directories; changing it can break local submodule builds.

## Test Signals
Signals are Maven reactor commands from `core/server` or the repository root, for example compiling or testing `common`, `master`, `proxy`, and `worker` through this aggregator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/pom.xml -->
# sources/distributed-fs/alluxio/core/server/proxy/pom.xml

## Purpose
This POM defines the `alluxio-core-server-proxy` jar module. It declares dependencies for the Alluxio proxy service and configures Swagger documentation generation for the proxy REST API.

## Important APIs, Types, and Functions
The artifact is `org.alluxio:alluxio-core-server-proxy` with packaging `jar`. External dependencies include Jackson XML, Guava, commons-io, servlet API, Apache HttpClient/Core, Jetty, Jersey server/servlet/HK2/Jackson media, and Kerby utility. Internal dependencies are `alluxio-core-common`, `alluxio-core-client-fs`, and `alluxio-core-server-common`. The Swagger plugin scans `AlluxioProxyRestServiceHandler`, `PathsRestServiceHandler`, and `StreamsRestServiceHandler`.

## Control Flow, State, and Persistence
The file has no runtime control flow. Maven resolves dependencies, builds the proxy jar, and can generate REST docs under `generated/proxy/index.html` and `generated/proxy/swagger-ui` using a shared template.

## Dependencies and Integration Points
The POM connects the proxy Java sources to Jetty/Jersey REST hosting, XML serialization for S3 models, filesystem client APIs, and server common utilities. The Swagger documentation block depends on class annotations and endpoint constants in the proxy REST handlers.

## Risks
REST behavior depends on compatible Jersey, Jackson, Jetty, and servlet versions inherited from parent dependency management. Moving handler packages without updating Swagger locations would silently omit API docs. The `build.path` relative expression is specific to this module depth.

## Test Signals
Useful signals are `mvn -pl core/server/proxy test`, compilation of proxy sources, and Swagger generation verification that the proxy, paths, and streams endpoints appear in generated docs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/StreamCache.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/StreamCache.java

## Purpose
`StreamCache` stores open Alluxio `FileInStream` and `FileOutStream` objects for the REST proxy. Path endpoints return integer stream IDs, and stream endpoints use those IDs to read, write, or close the cached streams.

## Important APIs, Types, and Functions
The class exposes `getInStream`, `getOutStream`, overloaded `put(FileInStream)`, `put(FileOutStream)`, `invalidate`, and `size`. It uses an `AtomicInteger` ID counter and two Guava `Cache<Integer, ...>` instances. A static `RemovalListener<Integer, Closeable>` closes streams when entries expire or are invalidated.

## Control Flow, State, and Persistence
Construction creates input and output caches with `expireAfterAccess(timeoutMs)`. Each `put` increments the shared counter and stores the stream in the appropriate cache. `invalidate` checks the input cache first, then the output cache, invalidates the entry, and returns the stream that was removed. State is process-local and in-memory; stream lifetime is tied to cache access, explicit close, and Guava eviction.

## Dependencies and Integration Points
The class integrates with proxy REST handlers: `PathsRestServiceHandler.createFile` and `openFile` insert streams, and `StreamsRestServiceHandler` reads, writes, and closes them. It depends on Alluxio filesystem stream types and Guava cache.

## Risks
The counter is an `int`, so very long-lived proxies could eventually wrap IDs. Input and output caches share the same counter but are separate maps, so an ID collision after wrap could be ambiguous. Removal listener exceptions are logged but not surfaced to callers. Cache eviction closes streams asynchronously from the caller's perspective, so clients holding stale IDs receive "stream does not exist."

## Test Signals
Relevant tests should verify ID uniqueness, explicit invalidation closes streams, expiration closes idle streams, and read/write handlers return errors for invalid or expired IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/StreamCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxy.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxy.java

## Purpose
`AlluxioProxy` is the command-line entry point for the Alluxio proxy process. It validates invocation, ensures a master host is configured, marks the current process type as proxy, creates a `ProxyProcess`, and delegates runtime management to `ProcessUtils.run`.

## Important APIs, Types, and Functions
The only runtime method is `main(String[] args)`. It uses `ConfigurationUtils.masterHostConfigured`, `ConfigurationUtils.getMasterHostNotConfiguredMessage`, `CommonUtils.PROCESS_TYPE`, `ProxyProcess.Factory.create`, `ProcessUtils.fatalError`, and `ProcessUtils.run`.

## Control Flow, State, and Persistence
If any command-line arguments are supplied, the program logs usage and exits with `-1`. If master host configuration is missing, it terminates through `fatalError`. Otherwise it sets the process type to `PROXY`, creates an `AlluxioProxyProcess`, and runs it. There is no persisted state in this class.

## Dependencies and Integration Points
The entry point integrates the proxy jar with Alluxio's common process runner, runtime constants, and global configuration. It is the top of the lifecycle that eventually starts the proxy web server and master heartbeat.

## Risks
The argument contract is strict and does not support flags. Any failure during process creation terminates the JVM. Correct operation depends on master host configuration being set before startup.

## Test Signals
Signals include process startup tests with valid configuration, failure tests for non-empty arguments, and configuration validation tests for missing master host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyProcess.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyProcess.java

## Purpose
`AlluxioProxyProcess` implements the runtime proxy process. It starts the proxy web server, registers the runtime web port, creates a heartbeat executor to the primary master, and blocks until stopped.

## Important APIs, Types, and Functions
The process implements `ProxyProcess` methods `start`, `stop`, `waitForReady`, `getStartTimeMs`, `getUptimeMs`, and `getWebLocalPort`. It owns a `WebServer`, `ProxyMasterSync`, single-thread executor, start timestamp, and a `CountDownLatch`.

## Control Flow, State, and Persistence
`start` creates a `ProxyWebServer` bound to the configured proxy web address, writes the actual local port back to `PropertyKey.PROXY_WEB_PORT`, builds a proxy `NetAddress`, starts the web server, creates `ProxyMasterSync`, submits a heartbeat thread using `PROXY_MASTER_HEARTBEAT_INTERVAL`, and then waits on `mLatch`. `stop` stops the web server, closes master sync, shuts down the heartbeat executor, and releases the latch. `waitForReady` polls the REST `paths/%2f/exists` endpoint using Apache HttpClient until it receives HTTP 200 or times out.

## Dependencies and Integration Points
This class integrates Jetty-based `ProxyWebServer`, Alluxio networking utilities, master client context, heartbeat framework, proxy REST handlers, and process lifecycle management. It also updates global configuration with the effective web port.

## Risks
`start` blocks until `stop`, so callers must run it through the Alluxio process runner or a separate thread. `waitForReady` creates an HTTP client on each poll and depends on the filesystem REST handler being available and root existence checks succeeding. `stop` sets fields to null and is not synchronized, matching the class's not-thread-safe annotation.

## Test Signals
Useful signals are process lifecycle tests that start and stop the proxy, verify the REST readiness endpoint, assert heartbeat thread creation, and confirm the web port is released on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyRestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyRestServiceHandler.java

## Purpose
`AlluxioProxyRestServiceHandler` exposes general proxy process information through the REST API under `/proxy`. It returns runtime version, uptime, start time, and configuration values.

## Important APIs, Types, and Functions
The main endpoint is `GET /proxy/info`, implemented by `getInfo(Boolean rawConfiguration)`. It returns `AlluxioProxyInfo`. The query parameter `raw_configuration` controls whether raw or display configuration values are returned. `getConfigurationInternal` builds a sorted map from `Configuration.toMap`.

## Control Flow, State, and Persistence
The constructor retrieves `ProxyProcess` from the servlet context using `ProxyWebServer.ALLUXIO_PROXY_SERVLET_RESOURCE_KEY`. `getInfo` normalizes a null query value to false, then builds the response inside `RestUtils.call`. There is no local mutable state beyond the process reference.

## Dependencies and Integration Points
The handler integrates Jersey annotations, Swagger annotations, `RestUtils`, global configuration, `RuntimeConstants.VERSION`, `AlluxioProxyInfo`, and servlet-context resource injection from `ProxyWebServer`.

## Risks
The endpoint can expose a large configuration map; raw values may reveal unresolved or sensitive configuration if callers are authorized to access it. The handler assumes the servlet context contains a valid `ProxyProcess`. It has no field-selection mechanism.

## Test Signals
Signals include REST tests for `/proxy/info`, raw and display configuration modes, and verification that start time, uptime, and version are populated from the process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/AlluxioProxyRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/PathsRestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/PathsRestServiceHandler.java

## Purpose
`PathsRestServiceHandler` exposes Alluxio filesystem metadata and stream-opening operations through the proxy REST API under `/paths`. It is the metadata side of the proxy REST gateway.

## Important APIs, Types, and Functions
Endpoints include `create-directory`, `create-file`, `delete`, `download-file`, `exists`, `free`, `get-status`, `list-status`, `mount`, `open-file`, `rename`, `set-attribute`, and `unmount`. Methods accept Alluxio gRPC option objects such as `CreateDirectoryPOptions`, `CreateFilePOptions`, `DeletePOptions`, `ListStatusPOptions`, and others. `createFile` and `openFile` place `FileOutStream` or `FileInStream` instances into `StreamCache` and return integer IDs.

## Control Flow, State, and Persistence
The constructor obtains `FileSystem` and `StreamCache` from the proxy servlet context. Each endpoint wraps a filesystem call in `RestUtils.call`, constructs `AlluxioURI` from the path parameter, and uses no-options overloads when the JSON body is null. Mount and rename validate required query parameters with `Preconditions.checkNotNull`. `downloadFile` returns a live input stream directly with a `Content-Disposition` header. Persistent effects are the filesystem mutations requested by callers: create, delete, mount, rename, set attributes, free, and unmount.

## Dependencies and Integration Points
The handler integrates Jersey and Swagger annotations, Alluxio filesystem client APIs, gRPC option messages, `StreamCache`, `ProxyWebServer` servlet resources, and `RestUtils` error/response conversion.

## Risks
The catch-all `{path:.*}/` path parameter makes URL encoding and slash handling important. Returning open streams through `StreamCache` requires clients to close stream IDs or rely on timeout eviction. Null option bodies silently choose default filesystem overloads. The handler is annotated not thread-safe but Jersey may create/request instances depending on configuration; correctness relies on shared dependencies being thread-safe.

## Test Signals
Signals should cover each REST endpoint, null and non-null option bodies, required query validation for `src` and `dst`, stream ID creation, direct download headers, and error conversion for invalid or missing paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/PathsRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyMasterSync.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyMasterSync.java

## Purpose
`ProxyMasterSync` is a heartbeat executor that lets a proxy periodically register liveness and version information with the primary master. This supports administrative visibility into live proxy instances.

## Important APIs, Types, and Functions
The class implements `HeartbeatExecutor`. Its main methods are the constructor, `heartbeat(long timeLimitMs)`, and `close`. It owns the proxy `Address` and a `RetryHandlingMetaMasterProxyClient`.

## Control Flow, State, and Persistence
Construction creates the retrying master client with proxy address and start time, then logs the start timestamp. Each heartbeat calls `mMasterClient.proxyHeartbeat`. If an `IOException` occurs, it logs the failure and disconnects the client so a later heartbeat can reconnect. `close` is currently a no-op. State is process-local client connection state.

## Dependencies and Integration Points
It integrates the proxy process heartbeat thread with the meta master proxy gRPC service through `RetryHandlingMetaMasterProxyClient` and Alluxio `HeartbeatExecutor`.

## Risks
`close` does not close the underlying client explicitly. Repeated heartbeat failures are logged but do not stop the proxy, which is intentional for availability but can hide registration problems. The class is not thread-safe and is intended for one heartbeat thread.

## Test Signals
Useful tests should mock the client and verify successful heartbeat, disconnect on `IOException`, and tolerance of repeated failures without throwing from the heartbeat thread.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyMasterSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyProcess.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyProcess.java

## Purpose
`ProxyProcess` defines the process contract for an Alluxio proxy. It extends the common Alluxio `Process` lifecycle with proxy-specific runtime metadata.

## Important APIs, Types, and Functions
The interface adds `getStartTimeMs`, `getUptimeMs`, and `getWebLocalPort`. The nested `Factory.create` method returns a new `AlluxioProxyProcess`.

## Control Flow, State, and Persistence
The interface has no implementation state. The factory is a simple construction point used by `AlluxioProxy.main`. Concrete state and lifecycle live in `AlluxioProxyProcess`.

## Dependencies and Integration Points
It integrates the proxy module with the shared Alluxio `Process` abstraction and gives REST handlers a stable type for querying process metadata.

## Risks
The factory hard-codes `AlluxioProxyProcess`, so tests or alternative process implementations need mocking or code changes rather than dependency injection. `getWebLocalPort` is documented as unit-test oriented but is part of the public interface.

## Test Signals
Signals are compile-time usage by the proxy process and runtime tests that `Factory.create` returns a functioning `AlluxioProxyProcess`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/ProxyProcess.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/RetryHandlingMetaMasterProxyClient.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/RetryHandlingMetaMasterProxyClient.java

## Purpose
`RetryHandlingMetaMasterProxyClient` wraps the meta master proxy gRPC client with Alluxio master-client retry behavior. It sends proxy heartbeat requests containing address, start time, and build version.

## Important APIs, Types, and Functions
The class extends `AbstractMasterClient` and overrides `getRemoteServiceType`, `getServiceName`, `getServiceVersion`, and `afterConnect`. Its public operation is `proxyHeartbeat()`, which builds `ProxyHeartbeatPOptions` and calls the blocking gRPC stub through `retryRPC`.

## Control Flow, State, and Persistence
The constructor stores the proxy address and start timestamp. `afterConnect` creates a `MetaMasterProxyServiceBlockingStub` from `mChannel`. `proxyHeartbeat` builds `BuildVersion` from `RuntimeConstants.VERSION` and `REVISION_SHORT`, sets a deadline from `USER_RPC_RETRY_MAX_DURATION`, and sends `ProxyHeartbeatPRequest`. State is the gRPC channel/stub managed by the inherited master client.

## Dependencies and Integration Points
The client integrates proxy liveness with `MetaMasterProxyServiceGrpc`, Alluxio service version constants, master client context, cluster configuration, and retry logging.

## Risks
`mClient` is null until a connection is established by inherited logic, so calls must go through `retryRPC`/connect flow. The deadline uses the same maximum retry duration property as user RPCs. Incorrect address or version data affects master-side proxy registration.

## Test Signals
Useful tests should verify heartbeat request contents, service type/name/version constants, deadline application, and retry/disconnect behavior on gRPC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/RetryHandlingMetaMasterProxyClient.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/StreamsRestServiceHandler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/StreamsRestServiceHandler.java

## Purpose
`StreamsRestServiceHandler` exposes data operations for streams previously opened through the proxy path API. It lets clients read, write, and close cached stream IDs under `/streams`.

## Important APIs, Types, and Functions
Endpoints are `POST /streams/{id}/close`, `POST /streams/{id}/read`, and `POST /streams/{id}/write`. The handler uses `StreamCache.invalidate`, `getInStream`, `getOutStream`, and Guava `ByteStreams.copy`.

## Control Flow, State, and Persistence
The constructor retrieves `StreamCache` from the servlet context. `close` invalidates the stream ID, relying on the cache removal listener to close the underlying stream, and throws if no stream exists. `read` returns the cached `FileInStream` as an octet-stream response. `write` copies the request body into the cached `FileOutStream` and returns the byte count. Filesystem persistence occurs through the underlying stream writes and close semantics.

## Dependencies and Integration Points
This handler pairs with `PathsRestServiceHandler.createFile` and `openFile`, which create stream IDs. It integrates Jersey media types, `RestUtils`, `StreamCache`, and Alluxio file stream classes.

## Risks
There is no range-read support and write copies the entire request body in one call. Invalid or expired IDs produce an `IllegalArgumentException` through `RestUtils`. Clients must close output streams to commit/flush according to Alluxio stream semantics.

## Test Signals
Signals should cover successful read/write/close flows, invalid IDs, expired streams, close idempotency expectations, and byte-count reporting for writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/StreamsRestServiceHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ChunkedEncodingInputStream.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ChunkedEncodingInputStream.java

## Purpose
`ChunkedEncodingInputStream` decodes AWS S3 `aws-chunked` streaming request bodies into raw object bytes. It strips chunk headers and signatures while presenting a normal `InputStream` to callers.

## Important APIs, Types, and Functions
The class extends `FilterInputStream` and overrides `read()` and `read(byte[], int, int)`. Internal state is `mCurrentChunkLength` and `mCurrentChunkIdx`. `decodeChunkHeader` reads the next hexadecimal chunk length up to `;` and skips the fixed-size signature suffix.

## Control Flow, State, and Persistence
Before each read, the stream checks whether the current chunk is exhausted. If so, it parses a new header, resets the chunk index, and skips 82 bytes after the hex length. Bulk reads are capped at the current chunk boundary so callers never receive header bytes. A zero-length or exhausted chunk causes `read(byte[], ...)` to return `-1`. State is in-memory cursor state over the wrapped input stream.

## Dependencies and Integration Points
It is part of the S3 proxy upload path for clients using SigV4 streaming/chunked transfer. It depends only on Java I/O and Alluxio's S3 proxy package.

## Risks
The implementation does not verify chunk signatures. The fixed 82-byte skip assumes a specific `;chunk-signature=` layout and 64-character signature. `skip` returning zero could loop indefinitely on some streams. Malformed hex length throws `NumberFormatException`, not `IOException`. Single-byte reads do not explicitly stop at a zero-length terminal chunk until underlying reads indicate EOF.

## Test Signals
Useful tests should include valid multi-chunk streams, zero-length terminal chunks, bulk reads crossing chunk boundaries, malformed headers, short signatures, and streams whose `skip` returns partial or zero progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ChunkedEncodingInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadHandler.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadHandler.java

## Purpose
`CompleteMultipartUploadHandler` handles S3 `CompleteMultipartUpload` requests in the proxy. It parses the request body, validates uploaded parts, merges part files into the final object, records ETag/upload metadata, cleans temporary multipart state, and returns an XML result.

## Important APIs, Types, and Functions
The outer class extends Jetty `AbstractHandler` and implements `handle`. It owns metadata filesystem `mMetaFs`, an executor pool sized by `PROXY_S3_COMPLETE_MULTIPART_UPLOAD_POOL_SIZE`, keepalive settings, and the S3 URI prefix. The inner `CompleteMultipartUploadTask` implements `Callable<CompleteMultipartUploadResult>` with key methods `call`, `prepareForCreateTempFile`, `parseCompleteMultipartUploadRequest`, `validateParts`, `removePartsDirAndMPMetaFile`, `cleanupTempPath`, and `checkIfComplete`.

## Control Flow, State, and Persistence
`handle` ignores non-matching paths, non-POST requests, and requests without `uploadId`. For matching requests it extracts the S3 user from authorization, parses bucket/object/upload ID, reads the XML body, submits a task, optionally sends whitespace keepalives while the future runs, then serializes success or S3 error XML. The task validates bucket and upload metadata, parses ordered parts, lists and sorts temporary part files, enforces minimum size for all but the last part, creates a temporary object with upload/tag/content-type xAttrs, streams all parts through an MD5 `DigestOutputStream`, persists the ETag xAttr, renames the temp object over the target with multipart S3 syntax options, deletes the parts directory and metadata file, and cancels the multipart cleaner. On exception it checks whether a concurrent retry already completed the same upload ID and returns that ETag if present. Temporary object cleanup runs in `finally`.

## Dependencies and Integration Points
The handler integrates Jetty request handling, Alluxio `FileSystem`, S3 path utilities, XML parsing/serialization with Jackson `XmlMapper`, proxy access logging, S3 metrics timers, multipart cleaner, Alluxio xAttrs, write type selection, and rename semantics.

## Risks
Keepalive mode may commit HTTP status before the task outcome, so S3 errors after whitespace flushing can be encoded in the body with an already-OK status. `validateParts` ignores requested ETags and returns all uploaded parts, not just requested parts, after validating presence and size. Multipart completion races are handled by upload-ID xAttr idempotency but still depend on rename atomicity and xAttr propagation. The executor is created per handler and there is no explicit shutdown here. Parsing bucket/object by first slash assumes a valid S3 path after prefix stripping.

## Test Signals
High-value tests include successful multipart completion, missing upload ID metadata, invalid XML, invalid part order, missing part, too-small non-final part, retry/idempotency after prior successful rename, cleanup of temp object after failure, cleaner cancellation, keepalive response behavior, and preservation of tag/content-type xAttrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadRequest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadRequest.java

## Purpose
`CompleteMultipartUploadRequest` is the Jackson XML model for an S3 complete-multipart-upload request body. It carries the ordered list of parts the client wants to commit.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CompleteMultipartUploadRequest")` and `@JsonInclude(NON_EMPTY)`. It exposes `getParts` and `setParts`. The nested `Part` model exposes XML `ETag` and `PartNumber` properties. Constructors support normal validation and a unit-test-only `ignoreValidation` path.

## Control Flow, State, and Persistence
`setParts` assigns the list and calls `validateParts`. Validation requires consecutive part numbers when more than one part is present; otherwise it wraps `S3ErrorCode.INVALID_PART_ORDER` in `IllegalArgumentException` so XML parsing surfaces an underlying S3 cause. State is an in-memory list of part descriptors.

## Dependencies and Integration Points
The model is consumed by `CompleteMultipartUploadHandler.parseCompleteMultipartUploadRequest`. It depends on Jackson XML annotations and S3 exception/error types.

## Risks
The root element name differs from AWS's usual `CompleteMultipartUpload` naming, so compatibility depends on how Jackson maps incoming documents. Setter methods in `Part` are both named `setKey` despite setting ETag and part number; annotations make it work, but it is confusing and brittle for reflection or maintainers. Validation checks order but not ETag format or part number range.

## Test Signals
Signals should cover XML deserialization, consecutive and non-consecutive part order, single-part requests, the ignore-validation constructor, and propagation of `INVALID_PART_ORDER` to the handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadResult.java

## Purpose
`CompleteMultipartUploadResult` is the XML response model for S3 multipart completion. It can represent either a successful completion with object location metadata or an error payload with code and message.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CompleteMultipartUploadResult")`, ordered fields `Location`, `Bucket`, `Key`, `ETag`, and non-empty inclusion. It exposes getters and setters for success fields and `Code`/`Message`, plus `toString`, `equals`, and `hashCode`.

## Control Flow, State, and Persistence
Constructors initialize either empty success fields, success values, or error values. `hashCode` switches between success and error field sets depending on whether `mCode` is null. The class has no persistence or external side effects.

## Dependencies and Integration Points
It is serialized by `CompleteMultipartUploadHandler` through Jackson XML and compared in tests. It follows S3 response field names and is part of proxy S3 REST compatibility.

## Risks
The same root type is used for error responses, which may not match AWS's usual error XML shape in all clients. Empty-string defaults combined with `NON_EMPTY` affect which fields appear. Equality includes both success and error fields, so partially populated objects can behave unexpectedly.

## Test Signals
Signals should verify XML for success and error forms, equality/hash behavior, omitted empty fields, and correct ETag/bucket/key values from multipart completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CompleteMultipartUploadResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyObjectResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyObjectResult.java

## Purpose
`CopyObjectResult` is the XML response model for an S3 copy-object operation. It reports the copied object's ETag and last-modified timestamp.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CopyObjectResult")`. Its constructor accepts an ETag and a last-modified epoch in milliseconds, converting the timestamp with `S3RestUtils.toS3Date`. Getters expose XML `ETag` and `LastModified`.

## Control Flow, State, and Persistence
The object is immutable after construction because fields are final and there are no setters. There is no persistence or external side effect.

## Dependencies and Integration Points
It is serialized by S3 proxy copy-object handling and depends on S3 date formatting utilities and Jackson XML annotations.

## Risks
There is no default constructor, which is fine for serialization but can limit deserialization in tests or clients. Correctness depends on callers providing the already-computed ETag.

## Test Signals
Signals include XML serialization with correct element names and S3 date formatting from epoch milliseconds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyObjectResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyPartResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyPartResult.java

## Purpose
`CopyPartResult` is the XML response model for S3 upload-part-copy. It contains the ETag of the copied multipart part.

## Important APIs, Types, and Functions
The class is annotated with `@JacksonXmlRootElement("CopyPartResult")`, stores a final `mETag`, and exposes `getEtag` as XML `ETag`.

## Control Flow, State, and Persistence
Construction captures the ETag. There are no setters, side effects, or persistence.

## Dependencies and Integration Points
It integrates with the S3 multipart copy path and Jackson XML serialization.

## Risks
No default constructor means this is serialization-oriented only. It does not validate ETag formatting.

## Test Signals
Signals should verify XML element naming and correct propagation of the copied part ETag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/CopyPartResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsRequest.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsRequest.java

## Purpose
`DeleteObjectsRequest` is the Jackson XML model for S3 multi-object delete requests. It captures the quiet-response flag and the object keys to delete.

## Important APIs, Types, and Functions
The root element is `Delete`. Fields are XML `Quiet` and unwrapped repeated `Object` entries. Public methods include `setQuiet`, `setDeleteObject`, `getQuiet`, and `getToDelete`. The nested `DeleteObject` model exposes XML `Key`.

## Control Flow, State, and Persistence
The default constructor initializes `mQuiet` to true and an empty deletion list. The value constructor accepts a quiet flag and object list. The object is a request DTO with no external side effects or persistence.

## Dependencies and Integration Points
It is consumed by S3 delete-objects REST handling and serialized/deserialized by Jackson XML according to AWS field names.

## Risks
The default quiet value is true, while S3 defaults may be expected as false by some clients; compatibility should be confirmed by tests. Nested `DeleteObject` is package-private static, which is fine inside the package but limits direct external construction. Version IDs are not modeled.

## Test Signals
Signals include XML deserialization for multiple `Object` entries, quiet true/false behavior, empty request handling, and integration with delete response generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsRequest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsResult.java

## Purpose
`DeleteObjectsResult` is the XML response model for S3 multi-object delete. It records successful deletions and per-object errors.

## Important APIs, Types, and Functions
The root element is `DeleteResult`. It exposes unwrapped repeated XML `Deleted` and `Error` lists through `getDeleted`, `setDeleted`, `getErrored`, and `setErrored`. Nested `DeletedObject` models `Key`, `DeleteMarker`, `DeleteMarkerVersionId`, and `VersionId`. Nested `ErrorObject` models `Key`, `Code`, `Message`, and `VersionId`.

## Control Flow, State, and Persistence
Both lists default to empty `ArrayList`s. Nested objects are simple XML DTOs. There is no persistence or control flow beyond getters and setters.

## Dependencies and Integration Points
It is serialized by S3 delete-object handling and depends on Jackson XML annotations. It mirrors AWS response field names sufficiently for non-versioned and partially versioned responses.

## Risks
Nested classes are package-private, so external tests may need package access. Quiet delete behavior must be implemented by callers because this model always has both lists available. `ErrorObject` fields are public as well as exposed by accessors, which allows mutation outside setters.

## Test Signals
Signals should verify XML serialization with no wrapper around repeated elements, success-only, error-only, mixed results, and quiet-mode omission behavior in the caller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/DeleteObjectsResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/InitiateMultipartUploadResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/InitiateMultipartUploadResult.java

## Purpose
`InitiateMultipartUploadResult` is the XML response model for S3 multipart upload initiation. It reports the bucket, key, and generated upload ID.

## Important APIs, Types, and Functions
The root element is `InitiateMultipartUploadResult`, with ordered XML fields `Bucket`, `Key`, and `UploadId`. The class provides default and value constructors plus getters and setters for all fields.

## Control Flow, State, and Persistence
The default constructor initializes strings to empty values for serialization/deserialization. The value constructor stores the supplied initiation metadata. There are no side effects or persistence.

## Dependencies and Integration Points
It is returned by S3 proxy initiate-multipart-upload handling and serialized with Jackson XML.

## Risks
The class does not validate bucket, key, or upload ID values. Empty defaults may serialize as empty elements depending on mapper inclusion settings.

## Test Signals
Signals include XML serialization/deserialization and correct propagation of generated upload IDs from the initiate path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/InitiateMultipartUploadResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListAllMyBucketsResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListAllMyBucketsResult.java

## Purpose
`ListAllMyBucketsResult` is the XML response model for listing S3 buckets. It converts Alluxio `URIStatus` entries into S3 bucket name and creation-date elements.

## Important APIs, Types, and Functions
The constructor accepts a list of `URIStatus` objects and maps each to a nested `Bucket`. `getBuckets` serializes as XML `Buckets` containing repeated `Bucket` elements. Each `Bucket` exposes `Name` and `CreationDate`.

## Control Flow, State, and Persistence
Construction streams over statuses, using `URIStatus.getName` and `getCreationTimeMs`, converting timestamps through `S3RestUtils.toS3Date`. State is the in-memory bucket list only.

## Dependencies and Integration Points
It integrates Alluxio filesystem status objects with S3 bucket-list XML serialization through Jackson.

## Risks
There is no default constructor, so this is response-only. The nested `Bucket` is a non-static inner class, which carries an implicit reference to the outer result. Creation date accuracy depends on `URIStatus` values supplied by the caller.

## Test Signals
Signals should verify bucket list XML structure, timestamp formatting, empty-list behavior, and mapping of Alluxio directory statuses to bucket names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListAllMyBucketsResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketOptions.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketOptions.java

## Purpose
`ListBucketOptions` is a mutable options object for S3 list-object operations. It supports both ListObjects v1 and ListObjectsV2 request parameters.

## Important APIs, Types, and Functions
Defaults are `DEFAULT_MAX_KEYS = 1000` and `DEFAULT_ENCODING_TYPE = "url"`. Fields include marker, prefix, max keys, delimiter, encoding type, list type, continuation token, and start-after. The class provides `defaults`, getters, fluent setters, `equals`, `hashCode`, and `toString`.

## Control Flow, State, and Persistence
`defaults` returns a new private-constructor instance with prefix `""`, max keys `1000`, delimiter and encoding null, marker null, list type null, continuation token null, and start-after null. Setters mutate and return `this`. There is no validation here; validation occurs in consumers such as `ListBucketResult`.

## Dependencies and Integration Points
It is consumed by S3 bucket-list response construction and likely request parsing. Guava `Objects` and `MoreObjects` provide equality and string formatting.

## Risks
The object is mutable and not thread-safe. It does not reject negative `maxKeys` or unsupported `listType`, leaving callers to validate. Default `encodingType` is null despite the constant, so callers must explicitly set URL encoding when desired.

## Test Signals
Signals include default values, fluent setter chaining, equality/hash behavior, and integration with `ListBucketResult` for v1/v2 marker and continuation-token behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketOptions.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketResult.java

## Purpose
`ListBucketResult` builds the XML response for S3 ListObjects and ListObjectsV2. It filters Alluxio child statuses by prefix, marker or continuation token, delimiter, start-after, and max-keys, then formats contents, common prefixes, truncation flags, and next tokens.

## Important APIs, Types, and Functions
The main constructor accepts bucket name, child `URIStatus` list, and `ListBucketOptions`. Core helpers are `buildListBucketResult`, `isVersion2`, `encodeToken`, and `decodeToken`. Response accessors expose `Name`, `KeyCount`, `MaxKeys`, `IsTruncated`, `Prefix`, `Delimiter`, `EncodingType`, `Marker`, `NextMarker`, `ContinuationToken`, `NextContinuationToken`, `StartAfter`, repeated `Contents`, and repeated `CommonPrefixes`. Nested DTOs are `CommonPrefix` and `Content`.

## Control Flow, State, and Persistence
Construction validates non-empty bucket name and non-negative max keys, initializes v1 or v2 fields, handles `maxKeys == 0`, and builds results from sorted children. The builder strips the bucket prefix from each status path, applies prefix/marker/start-after filters, converts folders to keys with trailing slash and size `0`, rolls keys into unique common prefixes when delimiter is set, counts both contents and common prefixes against `maxKeys`, and marks truncation when the count limit is hit. URL encoding is applied to keys, common prefixes, and start-after when encoding type is `"url"`. V2 continuation tokens encode the last marker as hex plus a SHA-256 digest separated by `-`.

## Dependencies and Integration Points
The class integrates Alluxio `URIStatus` with S3 XML response semantics, S3 date formatting, Apache Commons Hex/Digest/StringUtils, Java URL encoding, and Jackson XML/JSON inclusion annotations.

## Risks
The stream uses `.limit(mMaxKeys + 1)` after filtering that already flips truncation when `keyCount == maxKeys`; edge cases around exactly `maxKeys` versus more than `maxKeys` require careful tests. URL encoding uses `URLEncoder`, which encodes spaces as `+` and may not match all S3 expectations. Continuation tokens are reusable and not session-bound by design TODO. Delimiter support assumes string matching and comments note only `/` is effectively supported. The constructor mutates the supplied `children` list by sorting it.

## Test Signals
Important tests include empty bucket names, negative and zero max keys, v1 marker pagination, v2 continuation token pagination and invalid token rejection, prefix filtering, delimiter common-prefix grouping, URL encoding, folder key formatting, truncation flags, and key-count sanity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListBucketResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListMultipartUploadsResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListMultipartUploadsResult.java

## Purpose
`ListMultipartUploadsResult` is the XML response model for S3 multipart upload listing. It converts multipart metadata file statuses into upload entries for a specific bucket.

## Important APIs, Types, and Functions
`buildFromStatuses(String bucket, List<URIStatus> children)` is the main factory. It filters statuses by xAttrs `UPLOADS_BUCKET_XATTR_KEY` and `UPLOADS_OBJECT_XATTR_KEY`, maps matching entries to nested `Upload` objects, and returns a result. Accessors expose XML `Bucket` and repeated unwrapped `Upload` entries. `Upload` exposes `Key`, `UploadId`, and `Initiated`.

## Control Flow, State, and Persistence
The factory streams over metadata statuses, skips entries missing required xAttrs with a warning, filters to the requested bucket by xAttr value, uses status name as upload ID, formats last modification time as initiation time, and stores the resulting list. No persistent state is changed.

## Dependencies and Integration Points
It integrates Alluxio metadata xAttrs used by S3 multipart upload bookkeeping with Jackson XML serialization and S3 date formatting.

## Risks
The TODO notes unsupported fields such as `MaxUploads`, upload markers, and next markers, so pagination is incomplete. Entries with malformed or missing metadata are silently skipped except for logs. Character-set assumptions depend on `S3Constants.XATTR_STR_CHARSET`.

## Test Signals
Signals should cover filtering by bucket xAttr, skipping missing metadata, upload ID from status name, initiation date formatting, empty result behavior, and future pagination when implemented.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListMultipartUploadsResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListPartsResult.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListPartsResult.java

## Purpose
`ListPartsResult` is the XML response model for listing parts of an S3 multipart upload. It carries bucket, object key, upload ID, storage class, truncation flag, and per-part metadata.

## Important APIs, Types, and Functions
Top-level accessors expose XML `Bucket`, `Key`, `UploadId`, `StorageClass`, `IsTruncated`, and repeated `Part`. Nested `Part` exposes `PartNumber`, `LastModified`, `ETag`, and `Size`, with a factory `fromURIStatus(URIStatus status)`.

## Control Flow, State, and Persistence
The default constructor initializes strings to empty values, storage class to `STANDARD`, truncation to false, and an empty part list. `Part.fromURIStatus` parses the part number from the status file name, formats last modification time, and copies length as size. State is in-memory DTO state only.

## Dependencies and Integration Points
It integrates Alluxio temporary part files with S3 list-parts XML and `S3RestUtils.toS3Date`. It is used by multipart upload list-parts handling.

## Risks
The TODO notes unsupported pagination fields such as max parts and part-number markers. `fromURIStatus` assumes part file names are valid integers and does not populate ETag from xAttrs. Default values may produce empty XML elements.

## Test Signals
Signals include XML serialization, `fromURIStatus` parsing, invalid part file names, storage class defaults, truncation flag behavior, and pagination once supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/ListPartsResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/MultipartUploadCleaner.java -->
# sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/MultipartUploadCleaner.java

## Purpose
`MultipartUploadCleaner` lazily schedules automatic abortion of S3 multipart uploads after a configured timeout. Instead of scanning the filesystem, it tracks known upload IDs and deletes their temporary part directory and metadata file when expired.

## Important APIs, Types, and Functions
The singleton API includes `getInstance`, `shutdown`, static `apply`, static `cancelAbort`, `tryAbortMultipartUpload`, and `getRetryDelay`. Internal helpers include `apply(AbortTask,long)`, `removeTaskRecord`, `containsTaskRecord`, and `canRetry`. Nested `AbortTask` implements `Runnable` and defines equality/hash by bucket, object, and upload ID.

## Control Flow, State, and Persistence
The singleton is lazily initialized with timeout, retry count, retry delay, scheduled-pool size, and a `ConcurrentHashMap<AbortTask,ScheduledFuture<?>>`. `apply` schedules an abort task immediately and records its future. `tryAbortMultipartUpload` computes the multipart temp directory, checks upload metadata/status, returns a positive delay if the upload has not expired, otherwise deletes the user temp directory recursively and deletes the metadata file from the meta filesystem. Missing files mean the upload was already completed or aborted and no retry is needed. `AbortTask.run` reschedules itself for the returned delay, removes itself after success/no-retry, or retries after I/O/Alluxio failures until the configured count is exceeded.

## Dependencies and Integration Points
It integrates S3 multipart initiate/upload/complete/abort paths with Alluxio `FileSystem`, S3 temp-path utilities, upload ID metadata files, Java scheduled executors, and proxy configuration keys. `CompleteMultipartUploadHandler` cancels cleaner tasks after successful completion.

## Risks
`apply` overwrites existing task records after scheduling a new future, so duplicate scheduling can leave an older future not cancelled. `shutdown` stops the executor but does not clear `mTasks` before nulling the singleton. Error logging swaps bucket/object argument order in one message. Retry exhaustion leaves task records unless the final failure path removes them. Equality ignores filesystem instances, so same bucket/object/upload ID across different FS contexts collides intentionally or accidentally.

## Test Signals
Important tests include scheduling and cancellation, duplicate apply behavior, not-yet-expired rescheduling, expired upload deletion, already-missing upload handling, retry and retry exhaustion, singleton shutdown/recreation, and integration with successful complete-multipart cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/proxy/src/main/java/alluxio/proxy/s3/MultipartUploadCleaner.java -->
