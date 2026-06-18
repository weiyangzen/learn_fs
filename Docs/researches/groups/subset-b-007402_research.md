# Research: subset-b-007402

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableMetrics.java

## Purpose
JUnit coverage for mutable metrics primitives in `org.apache.hadoop.metrics2.lib`: counters, gauges, rates, aggregated rates, stats, quantiles, inverse quantiles, and float gauges. It verifies snapshot naming, interval-vs-total accounting, numerical accuracy, concurrent aggregation, rollover behavior, and handling of no-change/empty windows.

## Important APIs, Types, And Functions
Uses `MetricsRegistry`, `MutableStat`, `MutableRates`, `MutableRatesWithAggregation`, `MutableQuantiles`, `MutableInverseQuantiles`, `MutableGaugeFloat`, `Quantile`, and `MetricsRecordBuilder`. `testSnapshot()` validates registry-created metric emission. `testMutableRates*()` covers protocol/interface-based and string-array initialization. `snapshotMutableRatesWithAggregation()` reads mocked counters/gauges to accumulate expected totals. Quantile tests inspect `previousSnapshot` and verify percentile gauges against allowed error.

## Control Flow
Tests create registries or metric instances, mutate them, snapshot to mocked builders, and assert emitted names/values with `MetricsAsserts` and Mockito. The many-thread aggregation test coordinates worker lifetimes with latches, takes snapshots while additions are in flight, then verifies totals after all and half of the workers have completed. Quantile rollover tests insert controlled samples across timed windows, sleep past the configured five-second interval, then assert emitted gauges.

## State And Persistence Behavior
State is in in-memory mutable metrics and their rolling/interval buffers. Aggregated rates depend on thread-local state being collected before worker objects disappear; the test explicitly keeps threads alive through snapshots. Quantiles retain a previous published snapshot after scheduled rollover. The registry persists metrics by name for the duration of each test only.

## Dependencies And Integration Points
Depends on Hadoop metrics2 test helpers, Mockito, Guava `Stats`, `SubjectInheritingThread`, and JUnit timeout support. It exercises the public surface used by metrics sources before data reaches sinks.

## Risks
Timed quantile sleeps can be slow or flaky on heavily loaded systems. The random sleep interleaving in the concurrency test can expose race bugs but also makes failures harder to reproduce, though it logs the seed. Snapshot naming is case-sensitive and tied to metrics2 capitalization conventions.

## Test Signals
Strong signals are exact counter/gauge names (`FooNumOps`, `FooAvgTime`, percentile gauge names), correct interval reset to zero, stable large-number means/stdevs, successful concurrent totals, and no missing data after some aggregation threads terminate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableRollingAverages.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableRollingAverages.java

## Purpose
Tests `MutableRollingAverages`, including empty rollovers, sliding-window average calculation, metrics-system annotation injection, and thread-local state collection.

## Important APIs, Types, And Functions
Uses `MutableRollingAverages`, `replaceScheduledTask()`, `snapshot()`, `add()`, `collectThreadLocalStates()`, and `getStats()`. `DummyTestMetric` exposes a `@Metric(valueName = "testing")` rolling average registered in `DefaultMetricsSystem`.

## Control Flow
The empty test snapshots before and after a scheduled rollover and verifies no gauges are emitted. The rollover test configures two five-second windows, inserts repeated constant values into successive windows, sleeps past each boundary, and checks the rolling average gauge. The annotation test registers a source, adds two named metrics, waits until thread-local stats are collected, then reads gauges from the metrics system.

## State And Persistence Behavior
Rolling average state is held in scheduled window buckets plus thread-local accumulators. Try-with-resources closes `MutableRollingAverages` in direct tests, which is important because it owns scheduled rollover work. The default metrics system registration persists during the test and may affect subsequent tests if not isolated.

## Dependencies And Integration Points
Integrates with metrics2 annotations, `DefaultMetricsSystem`, `GenericTestUtils.waitFor`, Hadoop `Time`, and mocked `MetricsRecordBuilder`.

## Risks
Timing is the main risk: tests sleep around five-second and one-second windows. Failure to collect thread-local state would make `getStats()` empty even when samples were added. Metric names include bracketed, capitalized sample names such as `[Foo2]RollingAvgTime`.

## Test Signals
Expected signals include no gauges for empty windows, rolling averages of 1.0/1.5/2.5 over two windows, and registered gauges `[Metric1]RollingAvgTesting=500.0` and `[Metric2]RollingAvgTesting=1000.0`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestMutableRollingAverages.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestUniqNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestUniqNames.java

## Purpose
Small unit test for `UniqueNames`, confirming that duplicate metric/source names are made unique with numeric suffixes.

## Important APIs, Types, And Functions
Uses `UniqueNames.uniqueName(String)` and JUnit `assertEquals`.

## Control Flow
`testCommonCases()` requests `foo` twice and expects `foo`, then `foo-1`. `testCollisions()` pre-allocates `foo`, then requests existing suffixed names and base names to prove collision handling recurses to available variants.

## State And Persistence Behavior
State is an in-memory `UniqueNames` instance per test. No external persistence exists.

## Dependencies And Integration Points
This supports metrics registry/source naming where repeated registration must not overwrite earlier objects.

## Risks
The key risk is suffix collision logic: names already containing `-N` must not be treated as free if already allocated. Ordering matters because the allocator tracks prior calls.

## Test Signals
Expected sequence is `foo`, `foo-1`, `foo-2`, `foo-1-1`, and `foo-2-1` depending on input order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/lib/TestUniqNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSinkTestBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSinkTestBase.java

## Purpose
Shared base for `RollingFileSystemSink` tests. It builds metrics-system configurations, creates sample metric sources, writes metrics to a filesystem target, reads rolled log files, validates output format, pre-creates existing log files, and wraps the sink to record errors.

## Important APIs, Types, And Functions
Key helpers are `initMetricsSystem()`, `doWriteTest()`, `readLogFile()`, `readLogData()`, `findMostRecentLogFile()`, `assertMetricsContents()`, `assertExtraContents()`, `doAppendTest()`, `preCreateLogFile()`, `getNowNotTopOfHour()`, and `assertFileCount()`. `MyMetrics1` and `MyMetrics2` are annotated sources. `MockSink` extends `RollingFileSystemSink` and tracks `errored`/`initialized`.

## Control Flow
Each test gets a method-specific directory. Configuration is written with a lowercase metrics prefix, sink class, base path, context filter, append/error flags, hourly roll interval, zero roll offset, and small queue. `doWriteTest()` registers sources, increments gauges, publishes once, stops and shuts down the metrics system, then reads the current or starting-hour directory. Append helpers create current-hour log files before the sink opens them.

## State And Persistence Behavior
Persistent state is local or configured Hadoop `FileSystem` content under `ROOT_TEST_DIR` and time-named directories. `DATE_FORMAT` is GMT and static. `methodDir` is static per current test method. `MockSink` flags are static volatile and must be reset by tests before checking error paths.

## Dependencies And Integration Points
Integrates with `MetricsSystemImpl`, `ConfigBuilder`, `TestMetricsConfig`, Hadoop `FileSystem`, `Path`, host name lookup for log file names, metrics annotations, and JUnit lifecycle extensions.

## Risks
Top-of-hour rollovers can make tests read the wrong directory, so `getNowNotTopOfHour()` avoids the last 20 seconds of an hour. Hostname-dependent log names and filesystem append semantics vary by environment. Regex assertions deliberately allow arbitrary tag/metric order but still require record order.

## Test Signals
Signals include exactly expected log file counts, correctly formatted metric records for both sources, preservation of pre-existing `"Extra stuff"` when append is allowed, and `MockSink.errored` reflecting whether errors are propagated or ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSinkTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestFileSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestFileSink.java

## Purpose
Tests the plain `FileSink` by writing two annotated metrics records to a temporary file and checking the emitted textual format.

## Important APIs, Types, And Functions
Uses `FileSink`, `MetricsSystemImpl`, `ConfigBuilder`, `TestMetricsConfig`, annotated `MyMetrics1`/`MyMetrics2`, `MutableGaugeInt`, and `IOUtils.copyBytes()`.

## Control Flow
The test creates a temp output file under `${java.io.tmpdir}/${user.name}`, configures the metrics system with a large period and context filter `test1`, starts the system, registers metric sources, increments gauges, publishes immediately, stops/shuts down, reads the file, and matches it against a multiline regex.

## State And Persistence Behavior
The only persisted artifact is `outFile`, deleted in `@AfterEach`. Metrics source instances and system state are scoped to the test and explicitly shut down.

## Dependencies And Integration Points
Exercises metrics2 annotation discovery, source registration, sink file output, context filtering, UTF-8 reading, and metric/tag ordering behavior.

## Risks
The regex permits tag and metric reordering but assumes both records are emitted in registration order. Temp-directory permissions and hostname text in output can affect the file contents.

## Test Signals
The sink should write `test1.testRecord1` with `Context`, two tags, `Hostname`, and two gauges, followed by `test1.testRecord2` with its tag and hostname.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestFileSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestGraphiteMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestGraphiteMetrics.java

## Purpose
Unit coverage for `GraphiteSink` line formatting, timestamp conversion, write failure handling, reconnect behavior, and close delegation.

## Important APIs, Types, And Functions
Uses `GraphiteSink`, nested `GraphiteSink.Graphite`, `setGraphite()`, `putMetrics()`, `flush()`, and `close()`. Helpers create mocked `AbstractMetric` and `Graphite` objects. Test records use `MetricsRecordImpl`, `MetricsTag`, and `MsInfo`.

## Control Flow
Tests build records with context/hostname tags and unordered metric sets, inject a mock Graphite connection, call `putMetrics()`, capture written strings, and compare against both possible set iteration orders. Failure testing makes the first write throw `IOException`, verifies close, resets the mock to disconnected, and confirms a later put writes expected lines.

## State And Persistence Behavior
No durable state is created. Sink state is its injected Graphite object and connection flag. Timestamps are converted from milliseconds to seconds in emitted lines.

## Dependencies And Integration Points
Integrates with metrics2 record/tag/metric abstractions and Graphite's plaintext protocol shape: path, value, epoch seconds.

## Risks
Metrics are stored in `HashSet`, so output order is nondeterministic. The expected path includes default/null prefixes and tag names, making tests sensitive to path-building changes. Error handling must close broken connections without losing future writes.

## Test Signals
Expected lines include `null.all.Context.Context=all.Hostname=host.foo1 1.25 10` and one-second timestamp differences for records 1000 ms apart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestGraphiteMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestPrometheusMetricsSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestPrometheusMetricsSink.java

## Purpose
Tests `PrometheusMetricsSink` publishing, deduplication by metric plus tags, flush freshness, Prometheus name normalization, and special TopMetrics label parsing.

## Important APIs, Types, And Functions
Uses `PrometheusMetricsSink.writeMetrics()`, `prometheusName()`, `DefaultMetricsSystem`, annotated `TestMetrics`, and a custom `TestTopMetrics implements MetricsSource`. Assertions check emitted text and normalized names.

## Control Flow
Publishing tests initialize the default metrics system, register the sink and sources, mutate counters, publish metrics, write sink output to a UTF-8 stream, and inspect the resulting exposition text. Dedup tests register two sources with different tag values. Flush tests unregister and re-register with different tags between publishes. Naming tests call `prometheusName()` directly.

## State And Persistence Behavior
Sink output is in-memory, but the sink maintains the most recent flushed metrics set. Tests stop and shut down the default metrics system after use; missing cleanup would cross-contaminate global metrics state.

## Dependencies And Integration Points
Integrates metrics2 source collection with Prometheus exposition formatting, Hadoop metric/tag naming conventions, `StringUtils.deleteWhitespace`, and NameNode TopMetrics-style record/metric names encoded with dot-separated label fragments.

## Risks
The global `DefaultMetricsSystem` is shared, so cleanup is essential. Deduplication must include labels/tags, not just metric name. Name normalization must handle camel case, periods, whitespace, hyphens, UUID-like strings, and embedded label syntax.

## Test Signals
Expected signals include `test_metrics_num_bucket_create_fails{context="dfs",testtag="testTagValueN"`, absence of stale tag values after flush, normalized snake_case names, and TopMetrics labels such as `op="rename"` and `user="hadoop/TEST_HOSTNAME.com@HOSTNAME.COM"`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestPrometheusMetricsSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSink.java

## Purpose
Direct unit tests for `RollingFileSystemSink` configuration parsing and roll/flush time calculations.

## Important APIs, Types, And Functions
Uses `RollingFileSystemSink.init()`, `setInitialFlushTime()`, `updateFlushTime()`, `getRollInterval()`, and the package-visible fields `rollIntervalMillis`, `rollOffsetIntervalMillis`, `basePath`, `ignoreError`, `allowAppend`, `source`, and `nextFlush`.

## Control Flow
`testInit()` builds a subset configuration and asserts every parsed field. `testSetInitialFlushTime()` constructs sinks with zero, bounded, and pathological offset windows, seeds a `Calendar`, and checks the calculated initial `nextFlush`. `testUpdateRollTime()` verifies advancement after exact, slightly late, and far-late times. `testGetRollInterval()` iterates supported units and invalid units.

## State And Persistence Behavior
State is limited to sink fields and `Calendar` objects. No filesystem writes occur.

## Dependencies And Integration Points
Depends on Apache Commons `SubsetConfiguration`, `ConfigBuilder`, Hadoop `Path`, and `MetricsException`.

## Risks
Roll interval parsing is user-facing configuration logic; invalid units must fail loudly. Offset calculation permits a random negative offset, so assertions use ranges instead of exact values in those cases.

## Test Signals
Signals include `10m` becoming `600000`, default interval of one hour for bare `1`, supported minute/hour/day suffix variants, and `MetricsException` for unsupported suffixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithLocal.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithLocal.java

## Purpose
Local-filesystem integration tests for `RollingFileSystemSink`, using `RollingFileSystemSinkTestBase` to validate writes, pre-existing files, append/roll suffixes, and error handling.

## Important APIs, Types, And Functions
Extends `RollingFileSystemSinkTestBase` and uses `initMetricsSystem()`, `doWriteTest()`, `doAppendTest()`, `preCreateLogFile()`, `assertMetricsContents()`, and `MockSink.errored`.

## Control Flow
Tests use the method directory URI as sink base path. Normal and silent writes publish metrics and assert contents. Existing-file tests pre-create current-hour log files and expect the sink to create suffixed files when append is disabled. Failure tests make the directory non-writable before publishing and then inspect whether the mock sink reports an error depending on `ignore-error`.

## State And Persistence Behavior
Filesystem state is created under the per-method local test directory and cleaned by the base class. Directory writability is restored in `finally` blocks. `MockSink.errored` is reset before failure assertions.

## Dependencies And Integration Points
Exercises the sink through the real metrics system and local Hadoop `FileSystem`, with host-based log file names and actual file permissions.

## Risks
Permission behavior can differ by platform or privileged user. The method `testSilentExistingWrite()` passes `ignoreErrors=false` despite its name/comment, so its behavior matches non-silent existing write rather than an ignore-error variant.

## Test Signals
Expected signals are valid metrics contents, one file for fresh writes, two or three files when pre-existing names force suffixes, propagated errors for non-writable directories, and no `MockSink.errored` when ignore-error is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestRollingFileSystemSinkWithLocal.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestStatsDMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestStatsDMetrics.java

## Purpose
Tests `StatsDSink` datagram formatting for counter and gauge metrics, including hostname omission when the hostname tag is null.

## Important APIs, Types, And Functions
Uses `StatsDSink`, nested `StatsDSink.StatsD`, `setStatsd()`, `putMetrics()`, and `close()`. Metrics are mocked `AbstractMetric` instances with `MetricType.COUNTER` or `MetricType.GAUGE`.

## Control Flow
Each test opens a local `DatagramSocket`, injects a StatsD client pointed at that socket, sends a metrics record, receives one datagram, decodes it as UTF-8, and checks it against acceptable strings because metric set iteration is unordered.

## State And Persistence Behavior
State is ephemeral UDP socket state. The sink is closed in `finally`.

## Dependencies And Integration Points
Integrates metrics2 record/tag objects with StatsD UDP line protocol, including tag-derived prefixes for hostname, process, context, and record name.

## Risks
UDP receives can time out or see only one of multiple metrics depending on send behavior; tests accept either metric line. Hostname-null behavior must avoid leading empty components.

## Test Signals
Expected datagrams include `host.process.jvm.Context.foo1:1.25|c`, `host.process.jvm.Context.foo2:2.25|g`, or without hostname `process.jvm.Context.fooN:value|type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/TestStatsDMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricsTestHelper.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricsTestHelper.java

## Purpose
Package-local test helper that exposes `AbstractGangliaSink.setDatagramSocket()` to tests outside the sink implementation.

## Important APIs, Types, And Functions
Defines `GangliaMetricsTestHelper.setDatagramSocket(AbstractGangliaSink, DatagramSocket)`.

## Control Flow
The static helper directly calls the package-private/protected sink setter. There is no branching.

## State And Persistence Behavior
It mutates the supplied sink's socket reference only. No persistent state.

## Dependencies And Integration Points
Depends on `AbstractGangliaSink` and `java.net.DatagramSocket`. It exists in the same package as Ganglia sinks to access non-public API.

## Risks
The helper can inject sockets whose lifecycle is owned elsewhere, so tests must close them. If sink visibility changes, the helper may become unnecessary or fail compilation.

## Test Signals
Useful signal is successful compilation and ability for Ganglia tests to inject a socket without reflection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricsTestHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/TestGangliaSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/TestGangliaSink.java

## Purpose
Tests `GangliaSink30` socket creation and server-list configuration.

## Important APIs, Types, And Functions
Uses `GangliaSink30.init()`, `getDatagramSocket()`, `getMetricsServers()`, `ConfigBuilder`, `DatagramSocket`, and `MulticastSocket`.

## Control Flow
Tests initialize the sink with default config, explicit `multicast=false`, explicit `multicast=true`, multicast TTL override, and a comma-separated servers property. Assertions inspect socket type, multicast TTL, and server count.

## State And Persistence Behavior
State is in the sink's configured socket and metrics server list. No external persistence.

## Dependencies And Integration Points
Exercises Ganglia metrics sink config parsing and Java networking socket classes.

## Risks
Sockets opened by `init()` are real OS resources. Multicast socket behavior and TTL APIs may vary in restricted environments.

## Test Signals
Default and disabled multicast should produce a non-multicast `DatagramSocket`; enabled multicast should produce `MulticastSocket` with TTL 1 or configured 3; two configured servers should parse into two targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/sink/ganglia/TestGangliaSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/source/TestJvmMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/source/TestJvmMetrics.java

## Purpose
Tests JVM metrics collection and monitor integration: pause monitor metrics, GC time monitor metrics/alerts, monitor lifecycle edge cases, singleton semantics, and thread-count collection performance.

## Important APIs, Types, And Functions
Uses `JvmMetrics`, `JvmPauseMonitor`, `GcTimeMonitor`, `MetricsCollectorImpl`, `ServiceOperations.stop()`, and `SubjectInheritingThread`. `teardown()` stops monitors. `updateThreadsAndWait()` scales helper thread population for performance runs.

## Control Flow
Presence tests start monitors, attach them to `JvmMetrics`, collect metrics via mocked builders, and verify tags/gauge families. Lifecycle tests double-start/stop or stop before init/start and expect service-state behavior. GC tests allocate garbage and call `System.gc()` until monitor data and alerts appear. Singleton tests call `initSingleton()` with same/different names. Performance test creates 100-3000 sleeping threads and times two collection modes.

## State And Persistence Behavior
Monitor threads and helper test threads are the main state. `@AfterEach` stops monitors, and performance cleanup reduces helper threads to zero. `JvmMetrics.initSingleton()` is process-global, so tests rely on singleton persistence.

## Dependencies And Integration Points
Integrates metrics2 source collection with Hadoop service lifecycle, JVM MXBeans/thread groups, GC monitoring, pause monitoring, and test metrics assertions.

## Risks
GC alert tests are environment-sensitive because JVM GC behavior is nondeterministic. Performance test prints timings but has no hard performance assertion. Singleton global state can leak process name expectations across tests.

## Test Signals
Signals include `JvmMetrics` records tagged with process/session, memory/thread gauges, `GcTimePercentage`, expected `ServiceStateException` text for invalid lifecycle transitions, positive GC count/percentage/alerts, and singleton object identity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/source/TestJvmMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/DummyMXBean.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/DummyMXBean.java

## Purpose
Minimal MXBean interface used by MBean registration tests.

## Important APIs, Types, And Functions
Defines `int getCounter()`.

## Control Flow
No implementation or branching; classes implementing this interface expose a JMX `Counter` attribute.

## State And Persistence Behavior
No state in the interface. Implementations provide the value.

## Dependencies And Integration Points
Used by `TestMBeans` so Java's platform `MBeanServer` recognizes the implementation as an MXBean-compatible management interface.

## Risks
Method naming controls the exported JMX attribute name. Changing `getCounter()` would break JMX attribute assertions.

## Test Signals
Successful MBean registration should allow reading attribute `Counter`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/DummyMXBean.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMBeans.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMBeans.java

## Purpose
Tests Hadoop `MBeans` helper registration, additional ObjectName properties, service-name extraction, and cleanup.

## Important APIs, Types, And Functions
Implements `DummyMXBean`. Uses `MBeans.register()`, `MBeans.unregister()`, `MBeans.getMBeanName()`, `MBeans.getMbeanNameService()`, platform `MBeanServer`, and JMX `ObjectName`.

## Control Flow
Registration tests set `counter`, register the test object, read JMX attribute `Counter` from the platform server, assert the value, and unregister in `finally`. Additional-property test passes a `Map` containing `flavour=server`. Name test builds object names with and without custom properties and extracts service.

## State And Persistence Behavior
State is the test instance field `counter` and registered platform MBeans. `finally` cleanup is essential because ObjectNames are process-global.

## Dependencies And Integration Points
Integrates Hadoop metrics2 utility naming with Java Management Extensions and the `DummyMXBean` interface.

## Risks
Duplicate ObjectName registration can fail if prior cleanup did not run. Additional property ordering must be valid for JMX ObjectName syntax. Platform MBeanServer state is shared in the JVM.

## Test Signals
Signals are readable `Counter` values 23 and 42 through JMX and extracted service string `Service`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMBeans.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMetricsCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMetricsCache.java

## Purpose
Tests `MetricsCache` record update, lookup, tag retention, null-tag handling, metric instance retention, and overflow eviction.

## Important APIs, Types, And Functions
Uses `MetricsCache.update()`, `update(record, true)`, `get()`, `Record.metrics()`, `Record.tags()`, `getMetric()`, `getMetricInstance()`, and `MAX_RECS_PER_NAME_DEFAULT`. Helpers mock `MetricsRecord`, `MetricsTag`, and `AbstractMetric`.

## Control Flow
`testUpdate()` inserts a record, updates same name/tags with new and old metrics, then inserts same name with different tag value and verifies a separate record. `testGet()` checks empty and populated lookup. `testNullTag()` validates hash/key behavior with null tag values. `testOverflow()` inserts one more record than the per-name max and checks the oldest entry is evicted.

## State And Persistence Behavior
Cache state is in-memory and indexed by record name plus tag set. Metrics persist across updates for a record unless overwritten. Tags are only stored in cached records when requested.

## Dependencies And Integration Points
Supports sink implementations that need latest metrics by source/tag identity. Depends on metrics2 interned metadata helpers and Mockito.

## Risks
Incorrect tag equality/hash behavior can merge or lose records. Overflow eviction can silently drop old tag combinations. By default tags are not retained unless `update(..., true)` is used.

## Test Signals
Signals include metric `m` updating from 0 to 2 while `m1` remains, new `m2`, separate record for tag value `tv3`, null tag retrieval, and eviction of the first tag set after max+1 inserts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestMetricsCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleQuantiles.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleQuantiles.java

## Purpose
Tests the `SampleQuantiles` streaming quantile estimator for count tracking, clear/reset, normal quantile error bounds, inverse quantile error bounds, and string formatting.

## Important APIs, Types, And Functions
Uses `SampleQuantiles`, `Quantile`, `insert()`, `snapshot()`, `clear()`, `getCount()`, `getSampleCount()`, and `MutableInverseQuantiles.INVERSE_QUANTILES`.

## Control Flow
Each test initializes an estimator. Count test checks empty snapshot, inserts one value, snapshots, and checks `toString()`. Clear test inserts 1000 values then resets. Error tests build values 1..100000, shuffle them with a fixed seed across ten repeats, insert all values, snapshot, and assert estimates fall within each quantile's allowed absolute error.

## State And Persistence Behavior
Estimator state is an in-memory sampled summary plus total counts. `clear()` must reset both total and sample counts. Snapshots do not write external data.

## Dependencies And Integration Points
Supports `MutableQuantiles` and `MutableInverseQuantiles`, where approximate percentile gauges are emitted from the estimator.

## Risks
The shuffle uses `Arrays.asList(values)` on a primitive `int[]`, which creates a single-element list and therefore does not actually shuffle individual values. The sorted input still exercises estimator bounds, but less broadly than intended. Large insert loops can be CPU-heavy.

## Test Signals
Signals include null snapshot when empty, exact one-value output for all quantiles, zero counts after clear, and estimates between `actual +/- error` for both normal and inverse quantile arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleQuantiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleStat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleStat.java

## Purpose
Tests `SampleStat` running statistics for empty state, incremental values, min/max, variance/stddev, and reset.

## Important APIs, Types, And Functions
Uses `SampleStat`, `add()`, `reset()`, `numSamples()`, `mean()`, `variance()`, `stddev()`, `min()`, `max()`, and `SampleStat.MinMax` default constants.

## Control Flow
The test asserts initial defaults, adds value 3, checks one-sample statistics, chains `add(2).add(1)`, checks three-sample statistics, resets, and verifies defaults again.

## State And Persistence Behavior
State is in-memory running aggregate data. No persistence.

## Dependencies And Integration Points
`SampleStat` underpins mutable stat metrics where online updates must avoid storing all samples.

## Risks
The test uses a very small epsilon and exact simple values; it validates basic math but not numerical stability for large sample counts or magnitudes.

## Test Signals
Expected sequence includes mean 3 then 2, variance/stddev 0 then 1, min/max 3 then 1/3, and default min/max restored after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/metrics2/util/TestSampleStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/MockDomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/MockDomainNameResolver.java

## Purpose
Test `DomainNameResolver` implementation with deterministic forward and reverse DNS behavior for Hadoop network tests.

## Important APIs, Types, And Functions
Implements `getAllByDomainName()`, `getHostnameByIP()`, `getAllResolvedHostnameByDomainName()`, and testing setter `setAddressMap()`. Constants define the default domain, two IP byte arrays/strings, and two FQDNs.

## Control Flow
Constructor builds `InetAddress` objects for `10.1.1.1` and `10.1.1.2`, maps `test.foo.bar` to both, and maps each address to a hostname. Forward lookup throws `UnknownHostException` for unknown domains. Resolved-hostname lookup returns either FQDNs from `ptrMap` or raw IP strings depending on `useFQDN`.

## State And Persistence Behavior
State is per-instance maps: a `TreeMap` for domain to addresses and a `HashMap` for address to PTR name. `setAddressMap()` can replace forward mappings for tests.

## Dependencies And Integration Points
Used through `DomainNameResolverFactory` when `HADOOP_DOMAINNAME_RESOLVER_IMPL` points at this class.

## Risks
`UNKNOW_DOMAIN` is misspelled but public and used by tests. Replacing only `addrs` with `setAddressMap()` can make forward and reverse maps inconsistent. `getHostnameByIP()` returns null for missing PTRs rather than throwing.

## Test Signals
Default resolver should return exactly two addresses for `DOMAIN`, FQDNs when requested, IP strings otherwise, and throw for `UNKNOW_DOMAIN`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/MockDomainNameResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/ServerSocketUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/ServerSocketUtil.java

## Purpose
Utility for tests that need available TCP ports or need to wait until a port is released.

## Important APIs, Types, And Functions
Provides `getPort(int port, int retries)`, private `isPortAvailable(int)`, `waitForPort(int, int)`, and `getPorts(int)`.

## Control Flow
`getPort()` tries a requested port or random port in `[port, 65535)`, binds a loopback `ServerSocket`, returns the successful port, and retries on `IOException`. `waitForPort()` polls once per second until binding succeeds or retries are exhausted. `getPorts()` opens `numPorts` ephemeral sockets, records their assigned ports, then closes all sockets.

## State And Persistence Behavior
State is a static `Random` and transient sockets. Returned ports are not reserved after the method returns.

## Dependencies And Integration Points
Used by tests that need low-collision ports for daemons or sockets. Depends on Java networking and loopback binding.

## Risks
All methods suffer TOCTOU races: another process can bind returned ports after sockets are closed. `getPort(0, ...)` randomizes from zero but skips zero. `isPortAvailable()` binds all interfaces, while `getPort()` binds loopback only, so semantics differ.

## Test Signals
Useful signals are successful bind/close with logged selected ports, retry failure throwing the last `IOException`, and `getPorts()` returning unique ports during its reservation window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/ServerSocketUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/StaticMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/StaticMapping.java

## Purpose
Static in-memory `DNSToSwitchMapping` implementation for tests and mini-cluster simulations needing deterministic host-to-rack mappings.

## Important APIs, Types, And Functions
Extends `AbstractDNSToSwitchMapping`. Provides config key `hadoop.configured.node.mapping`, `setConf()`, compatibility `setconf()`, static `addNodeToRack()`, `resolve()`, `isSingleSwitch()`, `getSwitchMap()`, `resetMap()`, and no-op reload methods.

## Control Flow
`setConf()` parses comma-delimited `host=rack` strings from configuration and adds them to the static map. `resolve()` synchronizes on the map and returns a rack for each input or `NetworkTopology.DEFAULT_RACK`. `isSingleSwitch()` delegates to script-policy logic rather than map contents.

## State And Persistence Behavior
The host-to-rack map is static JVM-wide and persists across instances until `resetMap()` is called. Configuration-loaded entries are not removed when an instance is discarded.

## Dependencies And Integration Points
Integrates with `AbstractDNSToSwitchMapping`, `ScriptBasedMapping` policy semantics, `Configuration`, and `NetworkTopology`.

## Risks
Static state can leak between tests unless reset. Config parsing assumes every mapping contains `=` and preserves spaces as significant. Single-switch reporting depends on topology script configuration, not whether multiple racks are present.

## Test Signals
Expected signals include known hosts resolving to configured racks, unknown hosts resolving to `/default-rack`, `getSwitchMap()` returning a defensive copy, and reload methods not changing state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/StaticMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestClusterTopology.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestClusterTopology.java

## Purpose
Tests core `NetworkTopology` behavior: available-node counts with exclusions/scopes, random selection distribution, excluded-scope selection, path normalization, and topology-distance weights.

## Important APIs, Types, And Functions
Defines `NodeElement implements Node`. Uses `NetworkTopology.getInstance()`, `add()`, `remove()`, `countNumOfAvailableNodes()`, `chooseRandom()`, `NodeBase.normalize()`, `getWeight()`, and `getWeightUsingNetworkLocation()`.

## Control Flow
Tests build small synthetic topologies with rack paths, add nodes, and query counts or random choices. Random distribution is checked with a chi-square test across three runs. Excluded tests select from a scope while excluding subscopes or nodes. Weight tests compare same node, same rack, different rack, and different pod levels.

## State And Persistence Behavior
Each test creates a new topology instance from configuration. Nodes hold mutable parent/location/level assigned by topology insertion.

## Dependencies And Integration Points
Depends on Hadoop network topology classes, Apache Commons Math `ChiSquareTest`, and tuple helpers.

## Risks
Random distribution tests can be probabilistic; the test tolerates up to two rejected chi-square runs out of three. Assertions accidentally use `assertSame("node3", node.getName())`, relying on string interning rather than value equality.

## Test Signals
Signals include correct available counts under root/rack/negative scopes, random coverage of all eligible nodes, null when exclusions remove all candidates, normalization of trailing slashes, and expected weights 0/2/4/6 by topology distance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestClusterTopology.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNS.java

## Purpose
Tests Hadoop `DNS` utility behavior for local host/IP lookup, caching, null/default parameters, reverse DNS, hosts-file fallback, invalid interfaces, and localhost resolution.

## Important APIs, Types, And Functions
Uses `DNS.getDefaultHost()`, `getDefaultIP()`, `getIPs()`, `reverseDns()`, `getCachedHostname()`, `setCachedHostname()`, and helper `getLoopbackInterface()`.

## Control Flow
Tests call default host/IP lookups, compare repeated calls for speed and equality, validate null/default DNS server equivalence, verify unknown interface exceptions, perform reverse DNS with assumptions on unsupported environments, and test fallback behavior by forcing cached hostname to a dummy value and using invalid DNS server `0.0.0.0`.

## State And Persistence Behavior
`DNS.cachedHostname` is static process state. Fallback tests save and restore it in `finally`. Network interface and resolver state come from the host OS.

## Dependencies And Integration Points
Depends on Java `NetworkInterface`, JNDI DNS exceptions, Hadoop `Time`, platform assumptions, and local `/etc/hosts`/resolver configuration.

## Risks
Highly environment-dependent: reverse DNS, hosts-file contents, Windows behavior, link-local/loopback addresses, and resolver latency can affect tests. `testGetLocalHostIsFast()` uses a broad 20-second threshold to detect caching.

## Test Signals
Signals include non-null local hostname/IP, unknown interface message `No such interface ...`, default IP matching local address, reverse DNS either succeeds or is assumed away, and invalid-DNS fallback returning either a hosts-file result or cached dummy hostname depending on the flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNSDomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNSDomainNameResolver.java

## Purpose
Tests that `DNSDomainNameResolver.getHostnameByIP()` returns the canonical hostname even when an `InetAddress` instance was constructed with an unresolved host string equal to its IP address.

## Important APIs, Types, And Functions
Uses static `DNSDomainNameResolver DNR`, `InetAddress.getLocalHost()`, `InetAddress.getByAddress(String, byte[])`, and `getHostnameByIP()`.

## Control Flow
The test obtains localhost, assumes canonical name lookup is supported, builds an unresolved-style address whose host name is the IP string, calls the resolver, and asserts the result differs from the IP but equals localhost's canonical host name.

## State And Persistence Behavior
No persistent state beyond JVM/OS DNS caches.

## Dependencies And Integration Points
Exercises resolver behavior around Java `InetAddress` caching and canonical reverse lookup.

## Risks
Skipped when local canonical hostname equals host address. Results depend on OS DNS/PTR configuration.

## Test Signals
Expected signal is canonical name recovery despite the input address initially reporting its host name as the numeric IP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestDNSDomainNameResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestMockDomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestMockDomainNameResolver.java

## Purpose
Tests creation and default behavior of `MockDomainNameResolver` through the configured `DomainNameResolverFactory`.

## Important APIs, Types, And Functions
Uses `Configuration`, `CommonConfigurationKeys.HADOOP_DOMAINNAME_RESOLVER_IMPL`, `DomainNameResolverFactory.newInstance()`, `getAllByDomainName()`, and constants from `MockDomainNameResolver`.

## Control Flow
`@BeforeEach` configures the resolver implementation class. One test creates the resolver and asserts the default domain returns two expected IP addresses. The other asserts lookup of the configured unknown domain throws `UnknownHostException`.

## State And Persistence Behavior
Configuration is per-test. Resolver instance has default in-memory maps.

## Dependencies And Integration Points
Validates that Hadoop configuration can instantiate a custom domain resolver and that consumers see deterministic forward lookup behavior.

## Risks
Class-name configuration must remain compatible with factory reflection. Test name `testMockDomainNameResolverCanNotBeCreated()` actually verifies failed lookup, not construction failure.

## Test Signals
Expected signals are two addresses `10.1.1.1` and `10.1.1.2` for the known domain and an exception for `unknown.foo.bar`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestMockDomainNameResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetUtils.java

## Purpose
Broad unit coverage for `NetUtils`: loopback connection prevention, invalid host handling, socket read timeouts, local address detection, hostname verification, exception wrapping, socket address parsing, static resolution, resolver search-order behavior, canonical URI generation, host normalization, host/port parsing, local binding, and IOException message decoration.

## Important APIs, Types, And Functions
Uses `NetUtils.connect()`, `getInputStream()`, `getLocalInetAddress()`, `verifyHostnames()`, `isLocalAddress()`, `wrapException()`, `createSocketAddr()`, `createSocketAddrForHost()`, `getConnectAddress()`, `getCanonicalUri()`, `normalizeHostNames()`, `getHostNameOfIP()`, `getPortFromHostPortString()`, `bindToLocalAddress()`, and `addNodeNameToIOException()`. Test DNS behavior is driven by `NetUtilsTestResolver.install()`.

## Control Flow
The file first tests real socket behavior and timeout wrappers, then validates exception-message enrichment for multiple `IOException` subclasses. Resolver tests install a custom resolver globally, reset it before each test, and inspect the exact search suffix sequence for qualified/unqualified names. Later tests verify canonical URI host/port rewriting, hostname normalization, and exception cloning/decorating behavior.

## State And Persistence Behavior
Global state includes installed `NetUtilsTestResolver`, static host resolutions, and cached URI/host behavior. Socket tests create and close real sockets. Configuration is reset before each resolver test.

## Dependencies And Integration Points
Integrates with Java sockets, DNS resolution, Hadoop configuration, security exception types, shell Java-version checks, and URI normalization used by Hadoop clients.

## Risks
Environment-sensitive areas include local network interfaces, external DNS for `1.kanyezone.appspot.com`, Java-version-specific unresolved-host exception text, and timing thresholds. Custom resolver installation is global and must be reset. Exception wrapping depends on reflective constructors and class accessibility.

## Test Signals
Signals include loopback self-connect rejection, read timeouts within `TIME_FUDGE_MILLIS`, wrapped messages containing wiki/local/remote details, exact resolver search arrays, canonical URIs using `host.a.b`, normalized `localhost` to `127.0.0.1`, and inaccessible private exception classes returning the original exception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetworkTopologyWithNodeGroup.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetworkTopologyWithNodeGroup.java

## Purpose
Tests `NetworkTopologyWithNodeGroup`, adding node-group awareness below rack level for distance, sorting, random selection, and topology validation.

## Important APIs, Types, And Functions
Uses static `NetworkTopologyWithNodeGroup cluster`, `NodeBase` test nodes, `add()`, `getNumOfLeaves()`, `getNumOfRacks()`, `isOnSameRack()`, `isOnSameNodeGroup()`, `getDistance()`, `sortByDistance()`, `chooseRandom()`, and `getNodeGroup()`.

## Control Flow
Static initializer populates the cluster with eight nodes under `/domain/rack/nodegroup`. Tests check rack/nodegroup relationships, distance values, sorted ordering relative to local or compute nodes, random exclusion of a node path, root result for empty nodegroup, null location exception, and invalid rack-only topology rejection.

## State And Persistence Behavior
The cluster and data nodes are static and shared across all tests. Invalid add attempts are expected to fail without corrupting existing topology.

## Dependencies And Integration Points
Exercises Hadoop network topology extensions used by placement policies that distinguish rack and node group.

## Risks
Static topology state can make tests order-sensitive if a mutation unexpectedly succeeds. Random selection test assumes 100 picks cover all non-excluded nodes. Invalid topology validation must reject `/r2` rack-only nodes for node-group topology.

## Test Signals
Signals include eight leaves, three racks, same-rack and same-nodegroup booleans, distances 0/2/4/6/8, local/local-nodegroup/local-rack sort ordering, excluded node never chosen, and `IllegalArgumentException` containing `illegal network location`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestNetworkTopologyWithNodeGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMapping.java

## Purpose
Tests `ScriptBasedMapping` behavior when no script is configured, when a script is configured, when argument count is invalid, and when configuration is null/reset.

## Important APIs, Types, And Functions
Uses `ScriptBasedMapping`, `SCRIPT_ARG_COUNT_KEY`, `MIN_ALLOWABLE_ARGS`, `SCRIPT_FILENAME_KEY`, `resolve()`, `isSingleSwitch()`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
Tests create configurations, instantiate mapping via `setConf()`, and call `resolve()` or `isSingleSwitch()`. Invalid argument-count test expects `resolve()` to return null. Script presence makes mapping multi-switch; resetting config removes the script and returns it to single-switch.

## State And Persistence Behavior
State is per mapping instance and its current `Configuration`.

## Dependencies And Integration Points
Validates topology script policy used by DNS-to-switch mapping and by classes that delegate single-switch checks.

## Risks
The test sets the script filename key twice in one method, harmlessly. It does not execute scripts, so it validates configuration policy rather than script output.

## Test Signals
Expected signals are null resolve for invalid args, single-switch with no/null config, multi-switch with any script filename, and single-switch again after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMappingWithDependency.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMappingWithDependency.java

## Purpose
Tests `ScriptBasedMappingWithDependency` configuration behavior for normal resolution policy and dependency-script lookup.

## Important APIs, Types, And Functions
Uses `ScriptBasedMappingWithDependency`, inherited `ScriptBasedMapping` keys, `DEPENDENCY_SCRIPT_FILENAME_KEY`, `resolve()`, `getDependency()`, `isSingleSwitch()`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
The invalid-args test configures both topology and dependency script names but uses script execution settings that cause both `resolve()` and `getDependency()` to return null. Other tests mirror `ScriptBasedMapping`: no script means single switch, script means multi-switch, reset config returns to single switch, null config is single switch.

## State And Persistence Behavior
State is per mapping instance and configuration. No external script is executed in these tests.

## Dependencies And Integration Points
Exercises the dependency-aware mapping variant used by placement logic that may need secondary topology dependencies.

## Risks
The test sets `SCRIPT_ARG_COUNT_KEY` first below the minimum and later to 10, so the null result depends on script execution failure/nonexistent filenames more than the method name implies. Coverage remains focused on policy and null handling, not real dependency script parsing.

## Test Signals
Expected signals are null mapping/dependency results for dummy scripts, single-switch status with no script/null config, and multi-switch status when a script filename is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestScriptBasedMappingWithDependency.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSocketIOWithTimeout.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSocketIOWithTimeout.java

## Purpose
Tests Hadoop `SocketInputStream` and `SocketOutputStream` timeout and interrupt behavior using NIO pipes, including multithreaded scenarios.

## Important APIs, Types, And Functions
Uses `SocketInputStream`, `SocketOutputStream`, `Pipe.SourceChannel`, `Pipe.SinkChannel`, `MultithreadedTestUtil.TestContext`, `TestingThread`, executor services, `NativeIO.POSIX.getCacheManipulator().getOperatingSystemPageSize()`, and helper `doIO()`.

## Control Flow
Primary test opens a pipe, writes bytes and a high-bit byte, fills output until timeout, reads expected bytes, waits for read timeout, changes timeout, interrupts a blocking reader, checks channel/stream close behavior, and closes endpoints. Multithread tests run 64 independent pipe IO tasks or 64 blocking reads interrupted by `shutdownNow()`.

## State And Persistence Behavior
State is transient pipe channels, stream wrappers, test threads, executor pools, and atomic counters. No external persistence.

## Dependencies And Integration Points
Exercises Hadoop socket stream wrappers built on selectable channels and native page-size information. It complements DFS tests that cover normal IO.

## Risks
Timing and scheduler load can make timeout assertions fragile. Windows partial-write behavior differs, so one closed-output assertion is skipped on Windows. The 64-thread tests require enough CPU/scheduler capacity to finish inside short waits.

## Test Signals
Signals include `SocketTimeoutException` within `TIME_FUDGE_MILLIS`, exact byte round-trip including high-bit read as unsigned, `InterruptedIOException` containing timeout detail, open channels after interrupt, closed channels after stream close, and all multithreaded interrupted reads counted as exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSocketIOWithTimeout.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestStaticMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestStaticMapping.java

## Purpose
Tests `StaticMapping` and its interaction with `CachedDNSToSwitchMapping`, including static map reset, config-loaded mappings, single/multi-switch policy, positive and negative cache entries.

## Important APIs, Types, And Functions
Uses `StaticMapping.resetMap()`, `addNodeToRack()`, `resolve()`, `getSwitchMap()`, `dumpTopology()`, `setConf()`, `CachedDNSToSwitchMapping`, and `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`.

## Control Flow
Helper `newInstance()` resets static state before creating mappings. Tests assert single-switch with no script and multi-switch with a script, add a node and resolve known/unknown hosts, parse config `n1=/r1,n2=/r2`, and verify cached mappings relay single-switch/multi-switch queries and fill cache after resolve.

## State And Persistence Behavior
The underlying mapping is static JVM state and is reset by helpers. Cached mapping has its own cache, which can include negative/default-rack entries for unknown hosts.

## Dependencies And Integration Points
Validates test mapping behavior used by mini clusters and topology-aware tests, plus the caching wrapper used in production-style resolution paths.

## Risks
Static map leakage is the largest risk. Single-switch status is driven by script config, not rack entries, which can surprise callers. Negative caching stores unknown hosts, so later additions may not be visible through an existing cache without reload.

## Test Signals
Signals include `/r1` for `n1`, default rack for unknown, switch map sizes 0/1/2 as cache fills, and correct delegation of single/multi-switch status through cache wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestStaticMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSwitchMapping.java

## Purpose
Tests generic `DNSToSwitchMapping` single-switch detection and cached wrapper string delegation.

## Important APIs, Types, And Functions
Uses `AbstractDNSToSwitchMapping.isMappingSingleSwitch()`, `CachedDNSToSwitchMapping`, `ScriptBasedMapping`, and a private `StandaloneSwitchMapping implements DNSToSwitchMapping`.

## Control Flow
Standalone non-abstract mapping is treated as multi-switch. Cached wrapper around it also reports multi-switch. Script mapping tests check that `toString()` for both direct and cached mappings includes either the configured script name or `ScriptBasedMapping.NO_SCRIPT`. Null mapping is treated as not single-switch.

## State And Persistence Behavior
State is per mapping object and its configuration. No external persistence.

## Dependencies And Integration Points
Confirms wrapper behavior for arbitrary `DNSToSwitchMapping` implementations and diagnostics from cached mappings.

## Risks
The default for unknown mapping implementations is conservative multi-switch, which may reduce optimization opportunities but avoids unsafe single-rack assumptions. String assertions are tied to diagnostic text.

## Test Signals
Expected signals are `false` for standalone and null mapping single-switch checks, and cached `toString()` containing the inner script name or no-script marker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestSwitchMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestTableMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestTableMapping.java

## Purpose
Tests file-backed `TableMapping` host-to-rack resolution, caching, missing/bad file fallback, cache clearing, and reload behavior.

## Important APIs, Types, And Functions
Uses `TableMapping`, config key `NET_TOPOLOGY_TABLE_MAPPING_FILE_KEY`, `resolve()`, `reloadCachedMappings()`, Guava `Files.asCharSink()`, and temp files.

## Control Flow
Tests create temporary mapping files with space/tab-separated host and rack entries, configure mapping, and resolve two host names. Caching test modifies config after first read and expects cached results. No-file, missing-file, and bad-file tests expect default rack. Clearing test empties the map file, reloads, and expects default rack.

## State And Persistence Behavior
State exists in temp files and the mapping's internal cache. Files are marked `deleteOnExit`. Reload clears/reloads cached mappings from file content.

## Dependencies And Integration Points
Validates topology table mapping for deployments that use a static host/rack file instead of scripts.

## Risks
Bad file parsing should not throw to callers but should fall back to default rack. Cache can hide later config/file changes until reload. Temp-file cleanup relies on JVM exit.

## Test Signals
Expected signals are `/rack1` and `/rack2` for valid files, same cached values after config points to a bad path, and `/default-rack` for missing, nonexistent, emptied, or malformed files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/TestTableMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TemporarySocketDirectory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TemporarySocketDirectory.java

## Purpose
Utility for Unix domain socket tests that creates a short temporary directory path suitable for socket files and deletes it on close/finalization.

## Important APIs, Types, And Functions
Implements `Closeable`. Provides constructor, `getDir()`, `close()`, and `finalize()`.

## Control Flow
Constructor picks `${java.io.tmpdir}/socks.${System.nanoTime()}`, creates the directory, and marks it writable. `close()` deletes the directory recursively with Commons IO and nulls the field. `finalize()` delegates to `close()`.

## State And Persistence Behavior
State is the `File dir` field and the on-disk temporary directory. The directory persists until `close()` or finalization.

## Dependencies And Integration Points
Supports tests for Hadoop Unix domain sockets where path length limits are around 110 bytes. Depends on `FileUtils.deleteDirectory()` and `FileUtil.setWritable()`.

## Risks
`finalize()` is deprecated/unreliable for cleanup timing, so tests should use try-with-resources or explicit close. Directory name uniqueness depends on `nanoTime()` and does not check `mkdirs()` success. Socket path length still depends on the configured temp directory prefix.

## Test Signals
Expected signal is a writable, short directory returned by `getDir()` and recursive deletion with `dir` set to null after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/net/unix/TemporarySocketDirectory.java -->
