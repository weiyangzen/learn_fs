# subset-b-007364 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java

## Purpose
`UniqueNames` is a small private metrics2 helper that turns repeated metric or registry names into predictable unique names. The first caller receives the original name. Later collisions receive `name-1`, `name-2`, and so on.

## Important APIs and Types
The public surface is `uniqueName(String name)`. The nested `Count` type stores the original base name and the current suffix counter. A Guava `Joiner` formats suffixed names with `-`, and a mutable `Map<String, Count>` records every name already handed out.

## Control Flow
`uniqueName` is synchronized over the whole object. It checks whether the exact name is already in the map. If not, it inserts a counter and returns the name. If the name is present, it increments a counter and probes `name-N` until it finds an unused slot. Explicit user-provided names that already look suffixed are handled by probing until a free suffix exists.

## State and Persistence
All state is in memory and lifetime-bound to the `UniqueNames` instance. There is no expiry or reset API, so long-lived registries retain all allocated names.

## Dependencies and Integration Points
This class is private to metrics2 library code and supports registry/source implementations that need stable internal names. It depends only on Hadoop-shaded Guava and Hadoop audience annotations.

## Risks and Test Signals
The key risk is unbounded map growth if untrusted dynamic names are passed repeatedly. Tests should cover first-use identity, duplicate suffixes, explicit `foo-1` collisions, and concurrent callers receiving unique results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/UniqueNames.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/package-info.java

## Purpose
This package descriptor declares `org.apache.hadoop.metrics2.lib` as the public, evolving collection of helper classes used to implement metrics sources.

## Important APIs and Types
There are no executable APIs in this file. Its main exported behavior is package-level metadata via `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow
No runtime control flow exists. The file contributes Javadoc and annotations during compilation.

## State and Persistence
There is no state. Its effect persists only as generated Javadoc and class/package annotation metadata.

## Dependencies and Integration Points
The package documentation ties together the metrics source implementation helpers, such as mutable counters, gauges, rates, and registries elsewhere in `metrics2.lib`. It depends on Hadoop classification annotations.

## Risks and Test Signals
Risk is documentation/API-stability drift. When classes in `metrics2.lib` change audience or become internal-only, this package-level statement should be reviewed. Test signals are mainly Javadoc generation and package annotation visibility in downstream builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/lib/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java

## Purpose
This package descriptor is the user-facing overview for Hadoop Metrics 2.0. It explains the model of sources, sinks, records, tags, filters, mutable source libraries, JMX publication, configuration keys, and migration from the previous metrics system.

## Important APIs and Types
The file references the core contracts `MetricsSource`, `MetricsSink`, `MetricsCollector`, `MetricsRecordBuilder`, annotations such as `@Metrics` and `@Metric`, `DefaultMetricsSystem`, built-in filters, source helpers, and sink implementations. Its package annotations mark `org.apache.hadoop.metrics2` as public and evolving.

## Control Flow
There is no executable control flow. The Javadoc examples describe expected runtime flow: sources register with the default metrics system, sinks are configured under `[prefix].sink.[instance]`, and update cycles call `putMetrics` followed by `flush`.

## State and Persistence
The document describes persisted configuration in `hadoop-metrics2-[prefix].properties` or `hadoop-metrics2.properties`. It also describes runtime JMX exposure and filtering state managed by the metrics system.

## Dependencies and Integration Points
This documentation is the integration guide for Hadoop subsystems such as HDFS, YARN, RPC, and MapReduce that publish metrics. It also anchors compatibility expectations for third-party metrics sources and sinks.

## Risks and Test Signals
The largest risk is stale documentation, especially sink examples, filter precedence, migration names, and links. Tests cannot directly validate this file, so review should happen when metrics configuration parsing, annotations, or built-in sink names change. Javadoc generation should remain clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java

## Purpose
`FileSink` is a simple public metrics sink that writes each `MetricsRecord` as one text line to either stdout or a configured local file.

## Important APIs and Types
It implements `MetricsSink` and `Closeable`. `init(SubsetConfiguration)` reads `filename`; `putMetrics(MetricsRecord)` serializes timestamp, context, record name, tags, and metrics; `flush()` flushes the stream; `close()` closes it.

## Control Flow
Initialization chooses `System.out` when no filename is configured, otherwise it opens a UTF-8 `PrintStream` via NIO `Files.newOutputStream`. During each metrics update it prints `timestamp context.record: tag=value, metric=value` and terminates the line. Flush is explicit.

## State and Persistence
The only mutable state is the current `PrintStream`. When a filename is configured, metrics persist in that file and are overwritten or created according to `Files.newOutputStream` defaults. Without a filename, output goes to process stdout.

## Dependencies and Integration Points
The sink is loaded through metrics2 sink configuration and consumes `MetricsRecord`, `MetricsTag`, and `AbstractMetric` objects. It is a reference implementation for sink formatting.

## Risks and Test Signals
`close()` will close `System.out` when stdout mode is used, which callers must consider. There is no escaping of tag or metric values. Tests should cover stdout/file initialization, UTF-8 output, tag and metric ordering, flush behavior, and error wrapping in `MetricsException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/FileSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java

## Purpose
`GraphiteSink` publishes metrics2 records to a Graphite plaintext TCP endpoint. It converts record context, record name, tags, and metric names into Graphite path components.

## Important APIs and Types
The sink implements `MetricsSink` and `Closeable`. Configuration keys are `server_host`, `server_port`, and optional `metrics_prefix`. The nested `Graphite` class owns the socket, UTF-8 writer, reconnection, flush, close, and connection failure counting.

## Control Flow
`init` parses the host and port, normalizes a null prefix to the empty string, constructs a `Graphite` helper, and connects immediately. `putMetrics` builds one line per metric as `path value timestamp`, using seconds from the record timestamp. On write failure it logs, closes the helper, and relies on later writes to reconnect. `flush` flushes the helper and also closes on failure.

## State and Persistence
State is the configured prefix and the nested socket/writer. No metrics are buffered beyond the current `StringBuilder`. Connection failures are counted and connection attempts stop silently once the maximum is exceeded.

## Dependencies and Integration Points
It integrates metrics2 with external Graphite servers and uses Hadoop `MetricsException` for hard setup/close failures. `setGraphite` is available for tests.

## Risks and Test Signals
Misconfigured or absent `server_port` throws during init. Paths include raw tag values and `name=value` segments, so special characters can create unexpected Graphite hierarchies. Tests should cover line formatting, timestamp conversion, reconnection after close, failure limit behavior, flush exceptions, and injected `Graphite` test doubles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/GraphiteSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java

## Purpose
`PrometheusMetricsSink` is an in-memory metrics2 sink for Prometheus exporters. It captures the latest flushed set of gauge and counter metrics and writes them in Prometheus text exposition format on request.

## Important APIs and Types
The core methods are `putMetrics`, `flush`, `writeMetrics(Writer)`, `prometheusName`, and private TopMetrics helpers. It stores two concurrent maps, `nextPromMetrics` for the current metrics cycle and `promMetrics` for the last flushed snapshot. A bounded Guava `LoadingCache` memoizes Hadoop-to-Prometheus name normalization.

## Control Flow
`putMetrics` ignores metric types other than `COUNTER` and `GAUGE`, builds a normalized key from record name plus metric name, and stores the metric under the record's tag collection. `flush` atomically swaps the next map into the exported map and resets the next map. `writeMetrics` emits `HELP`, `TYPE`, and sample lines, with special parsing for NameNode TopMetrics so operation and user are exported as labels instead of embedded in metric names.

## State and Persistence
All state is process memory. A scrape sees only the most recently flushed metrics cycle. The name cache is static and capped at 100,000 entries.

## Dependencies and Integration Points
This sink feeds HTTP or servlet exporter code that calls `writeMetrics`. It depends on metrics2 record/tag contracts, Guava cache, Apache Commons `StringUtils`, and Prometheus naming conventions.

## Risks and Test Signals
Labels are not escaped, and a shared mutable `extendMetricsTags` list is cleared inside nested loops, so TopMetrics behavior needs careful coverage. Tests should verify normalization cache fallback, map swap semantics, filtering to counters/gauges, label omission of `numopenconnectionsperuser`, TopMetrics parsing, and empty-state output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/PrometheusMetricsSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java

## Purpose
`RollingFileSystemSink` writes metrics2 records to a Hadoop `FileSystem`, typically HDFS, rolling output into GMT timestamped directories. It is intended for cluster-wide metrics logs where each process writes `source-host.log` files under a configured base path.

## Important APIs and Types
It implements `MetricsSink` and `Closeable`. Configuration keys include `basepath`, `source`, `ignore-error`, `allow-append`, `roll-interval`, `roll-offset-interval-millis`, `keytab-key`, and `principal-key`. Visible-for-testing hooks include supplied configuration/filesystem, roll timings, and flush flags.

## Control Flow
`init` records configuration, parses roll intervals, loads a Hadoop `Configuration`, configures UGI, and performs Kerberos login when security is enabled. Filesystem initialization is delayed until the first write. `rollLogDirIfNeeded` creates the base directory, validates append support, calculates the current GMT interval directory, closes an old stream, opens a new file, updates the next flush time, and schedules a timer task to close the prior stream. `putMetrics` serializes one line per record and calls `hflush` to make interval data durable.

## State and Persistence
Persistent state is the file data written to the configured filesystem. In-memory state tracks the active filesystem, directory, file path, print stream, FS stream, timer, and roll schedule. The sink serializes write/roll/close operations with a private lock.

## Dependencies and Integration Points
It integrates metrics2, Hadoop `FileSystem`, UGI/Kerberos, `SecurityUtil`, `Path`, and HDFS append semantics. External readers consume interval directories named `yyyyMMddHHmm`.

## Risks and Test Signals
Risks include filesystem-specific append behavior, expensive hflush calls, timer races with writes, suffix probing in large directories, incorrect `file.startsWith(base)` comparisons against file names, and misleading Javadoc around `ignore-error` defaults. Tests should cover roll interval parsing, non-negative offsets, secure login validation, append fallback, suffix selection, timer close behavior, first-write initialization failure, hflush errors, and concurrent `putMetrics`/`close` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/RollingFileSystemSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java

## Purpose
`StatsDSink` publishes Hadoop metrics2 counters and gauges to a StatsD daemon over UDP using paths shaped like `hostname.service.context.record.metric:value|type`.

## Important APIs and Types
The sink implements `MetricsSink` and `Closeable`. Configuration keys are `server.host`, `server.port`, `skip.hostname`, `host.name`, and `service.name`. The nested `StatsD` helper lazily creates a `DatagramSocket` and reuses a `DatagramPacket`.

## Control Flow
`init` reads server settings, optionally resolves a local hostname via `NetUtils.getHostname`, stores the service name, and creates the helper. `putMetrics` lets well-known tags override host, context, and process/service name, then builds a prefix. For each metric it maps counters to `c`, gauges to `g`, appends the metric value, and sends the line with `writeMetric`. The helper resolves the server during socket creation and sends UTF-8 datagrams.

## State and Persistence
There is no durable state. Runtime state is the configured names and a lazily created UDP socket/packet.

## Dependencies and Integration Points
It integrates metrics2 with StatsD/collectd style UDP collectors. It uses `MsInfo` tags for host/context/process overrides and `NetUtils.wrapException` for socket creation diagnostics.

## Risks and Test Signals
Metric types other than counter/gauge produce a null StatsD type rather than being skipped. UDP sends are lossy and no flush is implemented. Service name may be null if not configured. Tests should cover tag override precedence, hostname skipping and truncation at dot, metric type mapping, error wrapping, injected `StatsD`, and close/reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/StatsDSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java

## Purpose
`AbstractGangliaSink` is the shared base for Ganglia metrics2 sinks. It manages hostname discovery, server parsing, multicast/unicast socket setup, Ganglia per-metric configuration, sparse mode configuration, and XDR buffer primitives.

## Important APIs and Types
The class implements `MetricsSink`. Important types are `GangliaSlope`, `GangliaConfType`, `GangliaMetricVisitor`, and `GangliaConf`. Protected helpers include `getGangliaConfForMetric`, `getHostName`, `xdr_string`, `xdr_int`, `emitToGangliaHosts`, `resetBuffer`, and `isSupportSparseMetrics`.

## Control Flow
`init` chooses a host name from `slave.host.name` or `DNS.getDefaultHost`, parses `servers` with default port 8649, applies multicast settings, loads arrays for `units`, `tmax`, `dmax`, and `slope`, creates a datagram or multicast socket, and records sparse support. `emitToGangliaHosts` sends the current XDR buffer to every configured server and then resets the buffer offset.

## State and Persistence
State is process-local: datagram socket, server list, hostname, XDR buffer and offset, config map, and sparse flag. Nothing is persisted by this class.

## Dependencies and Integration Points
Subclasses `GangliaSink30` and `GangliaSink31` use this base to encode protocol-specific packets. It depends on metrics2, Hadoop `DNS`, `Servers`, Java UDP sockets, and commons configuration.

## Risks and Test Signals
The fixed 1500 byte buffer has no bounds checks, so very long names or tags can overflow. Invalid `key=value` config can still fall through to array indexing. Tests should cover DNS fallback, multicast TTL setup, server parsing, per-metric config parsing, XDR padding, unresolved hosts, and buffer reset after exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/AbstractGangliaSink.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java

## Purpose
`GangliaConf` is a package-private value holder for per-metric Ganglia metadata: units, slope, `dmax`, and `tmax`.

## Important APIs and Types
The class exposes package-private getters and setters for `units`, `slope`, `dmax`, and `tmax`, plus `toString`. Defaults come from `AbstractGangliaSink` constants. `slope` may remain null to mean no explicit override.

## Control Flow
There is no complex flow. Instances are created by `AbstractGangliaSink.loadGangliaConf` and then mutated as each config type is parsed. Ganglia sinks read the object while emitting metrics.

## State and Persistence
State is in-memory only and scoped to a configured sink. It persists for the sink lifetime and is not synchronized.

## Dependencies and Integration Points
It is consumed by `GangliaSink30` and `GangliaSink31` during packet encoding. It depends on `AbstractGangliaSink.GangliaSlope`.

## Risks and Test Signals
The lack of validation means bad values are rejected only by the parser that sets them. The default null slope is intentional and must be interpreted by sink logic. Tests should cover default values, setter/getter behavior, null slope fallback, and `toString` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaConf.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java

## Purpose
`GangliaMetricVisitor` maps metrics2 metric values to Ganglia wire types and slopes without relying on concrete metric implementation classes.

## Important APIs and Types
It implements `MetricsVisitor`. `getType()` returns `int32`, `float`, or `double`; `getSlope()` returns `positive` for counters and null for gauges. Overloads handle int, long, float, and double gauges plus int and long counters.

## Control Flow
Each `AbstractMetric` calls back into the visitor through `metric.visit`. The visitor mutates its latest `type` and `slope` fields according to the metric overload. Sinks then read those fields immediately.

## State and Persistence
State is the last visited metric type and slope. It is reused by a sink instance and is not thread-safe, matching the Ganglia sink assumption that metrics sink calls are not concurrent.

## Dependencies and Integration Points
`GangliaSink30` uses the visitor before `emitMetric`; `GangliaSink31` inherits the same mapping. The class depends on metrics2 `MetricsInfo`, `MetricsVisitor`, and Ganglia slope enum.

## Risks and Test Signals
Long counters and long gauges are both emitted as `float`, which can lose precision for large values. Null slope for gauges relies on later fallback logic. Tests should exercise every visitor overload, repeated visits, and the sink slope precedence of explicit config over visitor-derived slope over default.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaMetricVisitor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java

## Purpose
`GangliaSink30` emits metrics2 records using the Ganglia 3.0 protocol. It can publish either dense metrics through a cache or sparse metrics directly from each update.

## Important APIs and Types
The class extends `AbstractGangliaSink`. Key methods are `init`, `appendPrefix`, `putMetrics`, `calculateSlope`, and protected `emitMetric`. It owns a `MetricsCache` for dense mode and `useTagsMap` for context-specific tag inclusion configured by `tagsForPrefix.*`.

## Control Flow
`init` delegates shared setup, enables comma list parsing, and loads tag inclusion rules. `putMetrics` constructs `context.record[.tag=value]` group/name prefixes. In dense mode it updates `MetricsCache` and emits every cached metric for the record; in sparse mode it emits only metrics in the current record. For each metric it visits the metric to determine Ganglia type/slope, merges configured `GangliaConf`, and writes a Ganglia 3.0 XDR packet.

## State and Persistence
Runtime state is the dense metrics cache, tag inclusion map, and inherited socket/buffer configuration. No durable state is written by the class itself.

## Dependencies and Integration Points
It integrates metrics2 with Ganglia 3.0 gmond endpoints. It consumes `MsInfo.Context` and `MsInfo.Hostname` to avoid duplicating those tags in metric names.

## Risks and Test Signals
Dense mode retains prior metric values and is sensitive to high-cardinality tags. `appendPrefix` includes raw tag values in names. Tests should cover tag rule parsing, all-tags wildcard, dense versus sparse behavior, slope precedence, null value/type guard paths, XDR packet fields, and IOException wrapping in `MetricsException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink30.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java

## Purpose
`GangliaSink31` adapts `GangliaSink30` emission logic to the Ganglia 3.1 protocol by overriding packet encoding.

## Important APIs and Types
The only overridden API is `emitMetric(String groupName, String name, String type, String value, GangliaConf gConf, GangliaSlope gSlope)`. All configuration, sparse/dense selection, tag prefix logic, and metric traversal come from `GangliaSink30` and `AbstractGangliaSink`.

## Control Flow
The method validates name, value, and type, logs at debug level, emits a metadata packet with metric id 128 and a `GROUP` extra field, sends it, then emits a value packet with metric id 133 and sends it. The buffer is reset by `emitToGangliaHosts` after each send.

## State and Persistence
No additional state is introduced. It uses inherited socket and XDR buffer state. Ganglia receives metadata and value datagrams for every emitted metric.

## Dependencies and Integration Points
It targets Ganglia 3.1 gmond. Protocol field order is documented as derived from `gm_protocol.x` and `gmetric` tracing.

## Risks and Test Signals
Metadata is resent every metric update rather than cached, increasing traffic. Buffer overflow risks are inherited. Tests should assert the two-packet sequence, metric ids, hostname/name/type/units/slope/tmax/dmax fields, GROUP extra field, null guard behavior, and inherited sparse/dense behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/ganglia/GangliaSink31.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/package-info.java

## Purpose
This package descriptor marks `org.apache.hadoop.metrics2.sink` as the public, evolving home of built-in metrics sinks.

## Important APIs and Types
There are no executable APIs. The package-level annotations are `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow
No runtime flow exists. The file contributes documentation and package annotation metadata during compilation.

## State and Persistence
There is no state. Persistence is limited to generated Javadoc and compiled package metadata.

## Dependencies and Integration Points
The descriptor covers sink classes such as file, rolling filesystem, Graphite, Prometheus, StatsD, and Ganglia sinks. It depends only on Hadoop classification annotations.

## Risks and Test Signals
The file can become stale as sink classes are added, removed, or moved. Javadoc generation and downstream API scans are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/sink/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java

## Purpose
`JvmMetrics` is a private metrics2 source that publishes JVM memory, garbage collection, pause, GC time percentage, and thread-state metrics for Hadoop daemons.

## Important APIs and Types
It implements `MetricsSource`. Public/static entry points include `create`, `reattach`, `initSingleton`, `shutdownSingleton`, `name`, and `description` via enum `JvmMetricsInfo`. Instance setters attach `JvmPauseMonitor` and `GcTimeMonitor`. The singleton enum stores one registered implementation.

## Control Flow
`create` reloads a `Configuration` to decide whether to use `ThreadMXBean`, constructs the source, and registers it with a `MetricsSystem`. `getMetrics` creates a `JvmMetrics` record tagged with process and session, then calls memory, GC, and thread collection helpers. GC collection iterates JVM GC beans, skips ZGC cycle counters, emits per-GC counters through a cached `MetricsInfo[]`, totals count/time, and appends pause monitor and GC time monitor values when present.

## State and Persistence
State is process-local: MXBean references, process/session strings, optional monitors, and a concurrent cache of generated GC metric info names. The singleton registration is mutable for tests and daemon lifecycle.

## Dependencies and Integration Points
It integrates Java management MXBeans, Hadoop `DefaultMetricsSystem`, `MetricsCollector`, `JvmPauseMonitor`, `GcTimeMonitor`, and metrics info enums.

## Risks and Test Signals
Thread enumeration races are handled by null checks, but thread group fallback only sees the current group. New GC names create dynamic metric names. Tests should cover singleton lifecycle, registration reattach, memory max `-1`, ZGC cycle skip, pause/gc monitor values, per-GC info caching, and both thread collection modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java

## Purpose
`JvmMetricsInfo` centralizes the `MetricsInfo` names and descriptions emitted by `JvmMetrics`.

## Important APIs and Types
It is an enum implementing `MetricsInfo`. Constants include the record `JvmMetrics`, memory gauges, GC counters, thread gauges, log counters, pause counters, and GC percentage. `description()` returns the configured text and `name()` is inherited from enum constants.

## Control Flow
There is no dynamic flow beyond enum initialization and simple method calls. `JvmMetrics` passes these constants to `MetricsRecordBuilder`.

## State and Persistence
Each enum constant stores one immutable description string for the JVM lifetime.

## Dependencies and Integration Points
The enum is used by metrics source code and potentially tests expecting stable metric names. It depends on metrics2 `MetricsInfo` and Hadoop audience annotations.

## Risks and Test Signals
Renaming enum constants changes metric names and can break dashboards. Descriptions are user-facing in sinks such as Prometheus. Tests should validate emitted `JvmMetrics` records include these names and that `toString` remains diagnostic rather than a metric identity dependency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/source/JvmMetricsInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java

## Purpose
`Contracts` provides lightweight argument checking helpers for metrics2 code, supplementing generic precondition utilities with return-the-argument convenience methods.

## Important APIs and Types
The class is private and non-instantiable. It offers overloaded `checkArg` methods for object, int, long, float, and double arguments.

## Control Flow
Each overload checks a supplied boolean expression. If false, it throws `IllegalArgumentException` with `msg + ": " + arg`; otherwise it returns the original argument.

## State and Persistence
There is no state and no persistence.

## Dependencies and Integration Points
It is available to metrics2 utility/source/sink code for local validation. It depends only on Hadoop classification annotations.

## Risks and Test Signals
Because the caller supplies the boolean expression, incorrect predicates are not detectable here. The message always includes the argument, which can leak sensitive values if misused. Tests should cover every overload, true-path value preservation, false-path exception type/message, and behavior with null object arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Contracts.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java

## Purpose
`MBeans` is a public stable utility for registering and unregistering Hadoop-standard JMX MBeans under object names shaped as `Hadoop:service=...,name=...[,extra=...]`.

## Important APIs and Types
Main APIs are `register(serviceName, nameName, Object)`, `register(serviceName, nameName, Map<String,String>, Object)`, `unregister(ObjectName)`, `getMbeanNameService(ObjectName)`, `getMbeanNameName(ObjectName)`, and test-visible `getMBeanName`.

## Control Flow
Registration builds an `ObjectName` with `DefaultMetricsSystem.newMBeanName`, then calls the platform MBean server. Duplicate instances are logged and return null. Other exceptions are logged and return null. Unregister removes the MBean from the platform server and then removes the name from `DefaultMetricsSystem`.

## State and Persistence
State lives in the JVM MBean server and in `DefaultMetricsSystem`'s MBean name registry. This class itself is stateless.

## Dependencies and Integration Points
It integrates Hadoop services with JMX and metrics system name tracking. Additional ObjectName properties are joined directly from the provided map.

## Risks and Test Signals
Additional property keys/values are not quoted or escaped here, relying on `ObjectName` creation to reject invalid names. The parser regex only recognizes the standard prefix/order. Tests should cover successful registration/unregistration, duplicate handling, null property rejection, invalid names returning null, parser failures, and cleanup of metrics system MBean names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MBeans.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java

## Purpose
`Metrics2Util` contains small support types for metrics2 producers and sinks, currently a value pair and fixed-size top-N queue.

## Important APIs and Types
`NameValuePair` stores a metric name and long value, implements `Comparable`, and exposes getters. `TopN` extends `PriorityQueue<NameValuePair>`, keeps at most `n` largest values, and records the total value of all offered entries.

## Control Flow
`TopN.offer` always adds the offered value to the running total. If the queue is already at capacity, it compares the new value with the current smallest item. Values not greater than the smallest are rejected; larger values replace the smallest.

## State and Persistence
All state is in-memory: pair fields, queue contents, capacity `n`, and running total.

## Dependencies and Integration Points
The utility supports metrics that report top users, operations, or other ranked counts. It depends only on Java collections and Hadoop audience annotations.

## Risks and Test Signals
`NameValuePair.compareTo` casts a long difference to int, which can overflow and produce incorrect ordering for very large differences. Equality and hash code ignore the name and depend only on value. Tests should cover ordering, equal values with different names, total accumulation for rejected entries, capacity behavior, and overflow-sized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Metrics2Util.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java

## Purpose
`MetricsCache` stores the latest values for metrics records, mainly for sinks that need dense updates even when the metrics system supplies sparse records.

## Important APIs and Types
The public APIs are constructors, `update(MetricsRecord)`, `update(MetricsRecord, boolean includingTags)`, and `get(name, tags)`. Nested `Record` exposes tag lookup, metric value lookup, metric instance lookup, tag entry sets, deprecated numeric metrics, and current metric entry sets. Nested `RecordCache` is an LRU-like `LinkedHashMap` capped by `maxRecsPerName`.

## Control Flow
`update` looks up a cache by record name, creates it if absent, then looks up a `Record` by the record's tag collection. It stores or overwrites metrics by metric name and optionally copies tags by tag name. `RecordCache.removeEldestEntry` drops the eldest entry once the per-name limit is exceeded and logs the first overflow.

## State and Persistence
All state is in memory. The top-level map grows by record name; each record name is bounded by `maxRecsPerName`, but metric names inside each record are not independently bounded.

## Dependencies and Integration Points
Ganglia dense mode uses this cache. Other sinks can use it when their backend expects full record schemas.

## Risks and Test Signals
The key uses `Collection<MetricsTag>` equality and therefore depends on tag collection equality/order semantics. The class is not synchronized. Tests should cover sparse-to-dense merging, includingTags behavior, per-record eviction, overflow logging, deprecated `metrics()` values, and lookup by equivalent tag collections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/MetricsCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java

## Purpose
`Quantile` describes one target quantile and acceptable error bound for the streaming `SampleQuantiles` estimator.

## Important APIs and Types
It is a private comparable class with public final fields `quantile` and `error`. It implements `equals`, `hashCode`, `compareTo`, and `toString`.

## Control Flow
Construction stores the two doubles. Equality compares exact `doubleToLongBits` for both fields. Ordering uses Guava `ComparisonChain` by quantile first and error second. `toString` formats a percent-style description.

## State and Persistence
Instances are immutable and can be used as keys in maps, such as `TreeMap<Quantile, Long>` returned by `SampleQuantiles.snapshot`.

## Dependencies and Integration Points
It integrates with `SampleQuantiles` and `QuantileEstimator` consumers. It depends on Hadoop-shaded Guava for comparison chaining.

## Risks and Test Signals
There is no validation that quantile and error are within sensible ranges, so callers must avoid zero, negative, greater-than-one, or NaN values that can break estimator math. Tests should cover equality bit semantics, ordering, hash stability, string formatting, and invalid-value behavior through `SampleQuantiles`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Quantile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java

## Purpose
`QuantileEstimator` defines the minimal interface for streaming quantile estimators used by Hadoop metrics code.

## Important APIs and Types
The interface declares `insert(long value)`, `snapshot()`, `getCount()`, and `clear()`. `snapshot` returns a map from configured `Quantile` targets to estimated long values.

## Control Flow
There is no implementation flow here. Implementations define insertion, estimation, and reset behavior. `SampleQuantiles` is the implementation in this group.

## State and Persistence
State is implementation-defined. The interface implies estimators track a count and mutable stream summary that can be cleared.

## Dependencies and Integration Points
Metrics classes can depend on this abstraction instead of a concrete estimator. It uses Java `Map` and the local `Quantile` type.

## Risks and Test Signals
The interface does not specify null versus empty map semantics for an empty estimator, thread safety, snapshot clearing behavior, or error guarantees. Tests should be written against concrete implementations and should document those behavioral choices for callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/QuantileEstimator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java

## Purpose
`SampleQuantiles` implements the CKMS/GK-style streaming estimator for targeted high-percentile approximate quantiles used by metrics histograms and latency tracking.

## Important APIs and Types
It implements `QuantileEstimator`. Public synchronized APIs are `insert`, `snapshot`, `getCount`, `clear`, test-visible `getSampleCount`, and `toString`. Internal `SampleItem` stores a sampled value, lower-rank delta `g`, and rank error `delta`.

## Control Flow
`insert` appends values to a 500-slot buffer, increments the total count, and when full, sorts and merges the batch into the ordered sample list before compression. `allowableError` computes the CKMS bound for a rank across configured quantiles. `compress` merges adjacent samples whose combined rank gap remains within error. `snapshot` flushes the buffer, returns null when empty, and queries each target quantile by scanning rank ranges.

## State and Persistence
State is in-memory: total count, ordered sample list, insertion buffer, buffer count, and configured quantiles. Methods that mutate or read estimator state are synchronized.

## Dependencies and Integration Points
Metrics code uses this through `QuantileEstimator` to summarize streams without storing every value. It depends on Hadoop `Preconditions`, test annotations, and shaded Guava `Joiner`.

## Risks and Test Signals
Invalid quantile values can divide by zero or produce bad error bounds. `snapshot` mutates state by flushing the buffer. Tests should cover empty snapshot null, monotonic count, exact small streams, buffer flush boundaries, compression reducing samples, target accuracy bounds, clear, toString, and concurrent synchronized access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleQuantiles.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java

## Purpose
`SampleStat` computes running sample count, total, mean, variance, standard deviation, min, and max for metrics that aggregate observations.

## Important APIs and Types
The class exposes `reset`, `copyTo`, `add(double)`, `add(long, double)`, `numSamples`, `total`, `mean`, `variance`, `stddev`, `min`, `max`, and `toString`. Nested public `MinMax` tracks minimum and maximum.

## Control Flow
Single-sample `add` updates min/max then delegates to weighted add. Weighted add updates sample count and applies a weighted incremental Welford variance algorithm using `xTotal / nSamples`. Accessors return zero mean/variance for insufficient samples.

## State and Persistence
State is mutable in memory: sample count, mean, variance accumulator `s`, and min/max. There is no synchronization.

## Dependencies and Integration Points
Mutable metrics such as rates and stats use this to compute snapshot values without storing raw samples. Ganglia-related comments explain why `MinMax` defaults use float range values.

## Risks and Test Signals
`add(long, double)` does not update min/max and divides by `nSamples`, so callers must not pass zero. `Float.MIN_VALUE` is the smallest positive float, so negative-only samples will update max correctly only after `add` is called, but reset defaults are unusual. Tests should cover Welford accuracy, copy/reset, weighted adds, min/max behavior, negative values, no-sample accessors, and zero-weight rejection by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/SampleStat.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java

## Purpose
`Servers` parses compact server address lists for metrics sinks.

## Important APIs and Types
The sole public method is `parse(String specs, int defaultPort)`, returning a list of `InetSocketAddress` values. The class is public, evolving, and non-instantiable.

## Control Flow
If `specs` is null, it returns `localhost:defaultPort`. Otherwise it splits the string on spaces and commas, then delegates each token to `NetUtils.createSocketAddr` with the default port.

## State and Persistence
There is no mutable state or persistence.

## Dependencies and Integration Points
Ganglia sink setup uses this parser for the `servers` property. Other metrics utilities can use it for comma/space separated endpoint lists. It depends on Hadoop `NetUtils` and `Lists`.

## Risks and Test Signals
An empty but non-null string can produce an empty token and rely on `NetUtils` to reject it. IPv6 address handling depends on `NetUtils.createSocketAddr`. Tests should cover null defaults, comma and whitespace mixtures, explicit ports, default ports, invalid tokens, and IPv6 forms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/Servers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/package-info.java

## Purpose
This package descriptor marks `org.apache.hadoop.metrics2.util` as the public, evolving home of general helpers for implementing metrics sources and sinks.

## Important APIs and Types
There are no executable APIs. Package metadata is expressed through `@InterfaceAudience.Public` and `@InterfaceStability.Evolving`.

## Control Flow
No runtime control flow exists.

## State and Persistence
There is no state or persistence beyond documentation and compiled package annotations.

## Dependencies and Integration Points
The descriptor covers utilities such as metrics caches, quantile estimators, sample stats, server parsing, and MBean helpers. It depends only on Hadoop classification annotations.

## Risks and Test Signals
The file can become stale if utilities move or audience guarantees change. Javadoc generation and package annotation scans are the main checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/metrics2/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java

## Purpose
`AbstractDNSToSwitchMapping` is the recommended base class for pluggable host-to-rack mapping implementations. It provides configuration storage, default topology diagnostics, and a single-switch predicate.

## Important APIs and Types
It implements `DNSToSwitchMapping` and `Configurable`. APIs include constructors, `getConf`, `setConf`, `isSingleSwitch`, `getSwitchMap`, `dumpTopology`, `isSingleSwitchByScriptPolicy`, and static `isMappingSingleSwitch`.

## Control Flow
The base class does not implement `resolve`. `dumpTopology` obtains a diagnostic map, emits mapping implementation identity, each host-to-switch entry, and counts unique switches. `isSingleSwitchByScriptPolicy` checks whether no topology script is configured. The static helper returns true only when the mapping is an `AbstractDNSToSwitchMapping` that reports single switch.

## State and Persistence
State is a retained `Configuration` reference. There is no persistent data.

## Dependencies and Integration Points
Network topology and block placement code query this base to decide whether multi-rack policies apply. Subclasses can expose cache contents through `getSwitchMap`.

## Risks and Test Signals
The Javadoc says non-derived mappings are assumed multi-switch, and the helper implements that by returning false for non-derived mappings. Tests should cover config retention, diagnostics with null/non-null maps, unique switch counts, script-policy behavior, and static predicate behavior for null, non-derived, and derived mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/AbstractDNSToSwitchMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java

## Purpose
`CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` and caches normalized host or IP to rack/network-location results.

## Important APIs and Types
The class extends `AbstractDNSToSwitchMapping`. Important APIs are constructor, `resolve`, `getSwitchMap`, `isSingleSwitch`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String>)`. It uses a `ConcurrentHashMap` for cache storage.

## Control Flow
`resolve` normalizes all input names with `NetUtils.normalizeHostNames`, returns empty for empty input, identifies uncached hosts, resolves only those through the raw mapping, caches non-null results, then returns the full list from cache. If the raw mapping returns null for uncached hosts, the final lookup returns null if any requested host remains missing.

## State and Persistence
State is the in-memory cache. Reload methods clear all or selected host entries. The raw mapping is final and not owned by this class.

## Dependencies and Integration Points
This wrapper is commonly used by Hadoop network topology code to avoid repeated external script or DNS lookups. Single-switch behavior delegates to the raw mapping via `AbstractDNSToSwitchMapping.isMappingSingleSwitch`.

## Risks and Test Signals
Selective reload removes the exact supplied names without normalization, while `resolve` stores normalized names, so callers passing hostnames may fail to evict normalized IP keys. Tests should cover normalization, null raw results, partial cache hits, cache snapshots, clear/reload behavior, and raw mapping call counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/CachedDNSToSwitchMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java

## Purpose
`ConnectTimeoutException` distinguishes timeout during socket connection from other socket timeout operations.

## Important APIs and Types
It extends `SocketTimeoutException`, declares a stable serial version UID, and has a single message constructor.

## Control Flow
There is no custom flow. `NetUtils.connect` catches `SocketTimeoutException` from connection attempts and wraps it as this type.

## State and Persistence
State is the inherited exception message and stack trace.

## Dependencies and Integration Points
RPC and network clients can catch this specific subtype when connect timeout handling differs from read timeout handling.

## Risks and Test Signals
It does not preserve a cause because `SocketTimeoutException` lacks a cause constructor in this usage. Tests should cover `NetUtils.connect` producing this type on timeout and preserving a useful message.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/ConnectTimeoutException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java

## Purpose
`DNS` provides Hadoop utilities for reverse DNS lookup, network-interface IP discovery, host discovery, and cached local host/address fallbacks.

## Important APIs and Types
Public APIs include `reverseDns`, `getIPs`, `getDefaultIP`, `getHosts`, `getDefaultHost`, `getIPsAsInetAddressList`, and test-visible cached hostname accessors. Static state includes `cachedHostname`, `cachedHostAddress`, and `LOCALHOST`.

## Control Flow
`reverseDns` constructs an IPv4 PTR lookup name, queries JNDI DNS, strips a trailing dot, and returns the host. `getIPs` handles `"default"` by returning the cached address, otherwise resolves a network interface or subinterface and returns ordered addresses, optionally excluding subinterface addresses. `getHosts` reverse-resolves interface addresses, optionally falls back to canonical host names, and finally falls back to the cached hostname. `getDefaultHost` normalizes `"default"` inputs and returns the first host.

## State and Persistence
Local hostname/address are cached statically at class load and can be changed for tests. No external persistence occurs.

## Dependencies and Integration Points
Ganglia sinks and Hadoop daemons use this class for bind/interface host names. It integrates Java `NetworkInterface`, `InetAddress`, JNDI DNS, and shaded Guava `InetAddresses`.

## Risks and Test Signals
`reverseDns` assumes IPv4 dotted decimal addresses and does not support IPv6 PTR construction. Static caches can become stale if host networking changes. Tests should cover default interface fallback, subinterface inclusion/exclusion, reverse DNS trailing dot removal, fallback canonical lookup, cached hostname override, invalid interfaces, and socket exception fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNS.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java

## Purpose
`DNSDomainNameResolver` is the default `DomainNameResolver` implementation. It uses Java DNS for forward lookup and reverse lookup to produce IP addresses or fully qualified host names.

## Important APIs and Types
It implements `getAllByDomainName`, `getHostnameByIP`, and `getAllResolvedHostnameByDomainName`.

## Control Flow
Forward lookup delegates to `InetAddress.getAllByName`. Reverse lookup starts with `InetAddress.getCanonicalHostName`, strips a trailing dot, and if Java returns the raw IP address from cache, attempts `DNS.reverseDns`. Bulk resolution first resolves all addresses, then either reverse-resolves each to FQDNs or returns host address strings depending on `useFQDN`.

## State and Persistence
The class has no mutable state. It uses JVM and OS DNS caches indirectly.

## Dependencies and Integration Points
`DomainNameResolverFactory` creates this as the default resolver. HA clients, routers, and secure environments use it to convert service hostnames into IPs or FQDNs for Kerberos-aware connection logic.

## Risks and Test Signals
Reverse DNS failures after Java returns an IP are logged and the IP-like host may be returned. IPv6 reverse fallback inherits `DNS.reverseDns` limitations. Tests should cover multi-address forward lookup, FQDN mode, non-FQDN mode, trailing dot stripping, IP-cache fallback, and reverse lookup failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSDomainNameResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java

## Purpose
`DNSToSwitchMapping` is the pluggable contract for resolving hostnames or IP addresses to network topology paths such as rack locations.

## Important APIs and Types
The interface declares `resolve(List<String> names)`, `reloadCachedMappings()`, and `reloadCachedMappings(List<String> names)`.

## Control Flow
Implementations must maintain one-to-one correspondence between input hosts and returned network paths. Empty input should return an empty list. Implementations are encouraged to use `NetworkTopology.DEFAULT_RACK` when a name cannot be resolved.

## State and Persistence
State is implementation-defined. The reload methods imply that implementations may cache mappings and must provide a way to clear all or selected entries.

## Dependencies and Integration Points
HDFS and other Hadoop placement policies depend on this interface to map data nodes to racks or fault domains. `CachedDNSToSwitchMapping` and script-based mappings are common implementations.

## Risks and Test Signals
Returning a wrong-sized list can corrupt topology assumptions. Null results have special meanings in some wrappers. Tests for implementations should cover empty input, unresolved hosts, ordering, cache reload, and consistency with network topology path syntax.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMappingWithDependency.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMappingWithDependency.java

## Purpose
`DNSToSwitchMappingWithDependency` extends rack mapping with cross-node dependency discovery for block placement policies that must avoid shared fault domains beyond rack or node-group topology.

## Important APIs and Types
It extends `DNSToSwitchMapping` and adds `getDependency(String name)`, returning dependent hostnames for a given data node.

## Control Flow
There is no implementation flow in the interface. Implementations must resolve the supplied data-node host or IP to other nodes sharing a compute/storage fault domain.

## State and Persistence
State is implementation-defined and may include caches or external topology data.

## Dependencies and Integration Points
HDFS block placement policies can use this contract to avoid placing replicas on dependent nodes, especially in virtualized deployments where compute and storage fault domains differ.

## Risks and Test Signals
The contract requires names to match `dfs.datanode.hostname` when configured, otherwise FQDNs. Inconsistent naming will cause dependency checks to miss conflicts. Tests should cover configured-hostname and FQDN modes, empty dependency lists, cache reload interactions, and placement policy consumption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DNSToSwitchMappingWithDependency.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java

## Purpose
`DomainNameResolver` abstracts service discovery for Hadoop components that need to resolve domain names to addresses or hostnames, including NameNodes, routers, and resource managers.

## Important APIs and Types
It declares `getAllByDomainName`, `getHostnameByIP`, and `getAllResolvedHostnameByDomainName`.

## Control Flow
The interface describes a two-step secure mode flow: forward-resolve a domain to all IP addresses, then optionally reverse-resolve each IP to an FQDN for service principals.

## State and Persistence
State is implementation-defined. Implementations may use DNS, ZooKeeper, static maps, or other discovery mechanisms.

## Dependencies and Integration Points
`DomainNameResolverFactory` instantiates configured implementations. Hadoop failover proxy and HA client code can use the abstraction to discover all endpoints behind a logical domain.

## Risks and Test Signals
The contract does not define ordering, duplicate handling, caching, or null semantics. Implementation tests should cover multi-address domains, reverse lookup behavior, `useFQDN` choices, `UnknownHostException`, and service-specific configuration integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolver.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java

## Purpose
`DomainNameResolverFactory` creates `DomainNameResolver` instances from Hadoop configuration, supporting default and host-specific resolver classes.

## Important APIs and Types
The factory is private/evolving and non-instantiable. Overloads of `newInstance` accept `(Configuration, URI, configKey)`, `(Configuration, host, configKey)`, or `(Configuration, configKey)`.

## Control Flow
The URI overload extracts the URI host and appends it to the config key. The host overload builds `configKey.host`. The core overload reads a class from configuration with `DNSDomainNameResolver` as default and `DomainNameResolver` as the required interface, then instantiates it through `ReflectionUtils`.

## State and Persistence
The factory is stateless. Resolver instances may hold their own state depending on implementation.

## Dependencies and Integration Points
HA and service discovery code use this to plug in custom domain resolvers per nameservice or YARN service. It depends on Hadoop `Configuration` and reflection utilities.

## Risks and Test Signals
Host-specific configuration depends on exact host strings from URIs. Misconfigured classes fail at instantiation time. Tests should cover default resolver creation, host-suffixed key lookup, URI host extraction, custom resolver class loading, and invalid class/interface handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/DomainNameResolverFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java

## Purpose
`InnerNode` defines the mutable interior-node contract for Hadoop network topology trees. Interior nodes represent racks, switches, or higher-level topology components and contain children.

## Important APIs and Types
The interface extends `Node`. It declares nested `Factory<N extends InnerNode>`, `add`, `getLoc`, `getChildren`, `getNumOfChildren`, `getNumOfLeaves`, `remove`, and `getLeaf`.

## Control Flow
Implementations must add and remove nodes in subtrees, resolve path-like locations, expose children, count leaves, and return the indexed leaf while optionally excluding a node or subtree.

## State and Persistence
State is implementation-defined but expected to be an in-memory tree. No persistence is implied.

## Dependencies and Integration Points
`InnerNodeImpl` implements this interface, and Hadoop network topology/block placement code traverses it to choose replica locations and count fault domains.

## Risks and Test Signals
The `getLeaf` contract depends on stable child ordering and correct exclusion accounting. Tests for implementations should cover adding/removing leaves and inner nodes, path lookup, leaf counts, excluded leaf and subtree behavior, and factory construction from paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java

## Purpose
`InnerNodeImpl` is the default in-memory implementation of `InnerNode`, representing non-leaf network topology nodes such as racks or switches.

## Important APIs and Types
It extends `NodeBase` and implements `InnerNode`. Important members are ordered `children`, lookup `childrenMap`, `numOfLeaves`, static `FACTORY`, constructors, `isRack`, `isAncestor`, `isParent`, `getNextAncestorName`, `add`, `remove`, `getLoc`, and `getLeaf`.

## Control Flow
`add` verifies the new node is a descendant. If this node is the direct parent, it sets parent/level and inserts or replaces the child. Otherwise it finds or creates the next inner ancestor and delegates. `remove` mirrors this traversal, pruning empty intermediate parents and decrementing leaf counts. `getLoc` recursively follows path segments. `getLeaf` walks ordered children, adjusting indices for an excluded leaf or subtree.

## State and Persistence
The topology tree is mutable in memory. Child ordering is preserved in `children`; fast lookup is mirrored in `childrenMap`; leaf counts are manually maintained.

## Dependencies and Integration Points
Network topology management uses this tree to store data nodes and select leaves for placement. It relies on `NodeBase` path, level, parent, and separator conventions.

## Risks and Test Signals
`getLeaf` casts children to `InnerNodeImpl` in non-rack mode, so mixed custom inner implementations can fail. Replacing a direct child returns false and does not update `numOfLeaves`, which is intentional for replacement. Tests should cover path-derived parent creation, duplicate replacement, subtree pruning, leaf count correctness, rack detection, exclusion by leaf/subtree, invalid ancestor errors, and path lookup edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/InnerNodeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java

## Purpose
`NetUtils` is Hadoop's broad network utility class for socket factories, address parsing/canonicalization, static host overrides, socket I/O wrappers, connect behavior, hostname normalization, exception diagnostics, subnet matching, and free-port helpers.

## Important APIs and Types
Major APIs include `getSocketFactory`, `getDefaultSocketFactory`, `getSocketFactoryFromProperty`, `createSocketAddr` variants, `createSocketAddrUnresolved`, `createSocketAddrForHost`, `getCanonicalUri`, static resolution getters/setters, `getConnectAddress`, socket input/output stream wrappers, `connect`, hostname/IP normalization, `verifyHostnames`, host/port formatting, local-address checks, `wrapException`, `addNodeNameToIOException`, subnet helpers, `getFreeSocketPort(s)`, and `bindToLocalAddress`.

## Control Flow
Address creation trims input, wraps bare `host:port` with a dummy URI scheme, validates host/port/path, uses an optional short-lived URI cache, and either resolves through `SecurityUtil.getByName` or creates an unresolved socket address. `connect` optionally binds a local address, uses normal socket connect or Hadoop `SocketIOWithTimeout` for channels, converts connect timeouts, maps unresolved addresses to `UnknownHostException`, and rejects accidental loopback self-connections. `wrapException` detects common socket/ACL exception types and creates same-type exceptions with richer diagnostics and wiki links when possible.

## State and Persistence
Static state includes host-to-static-resolution mappings, a bounded expiring URI cache, and a concurrent canonicalized hostname cache. No durable persistence exists.

## Dependencies and Integration Points
This class is central to Hadoop RPC, IPC server clients, metrics sinks such as StatsD, filesystem URI handling, security-aware resolution, and test port allocation. It integrates with `SocketInputStream`, `SocketOutputStream`, `SocketIOWithTimeout`, `SecurityUtil`, Apache Commons `SubnetUtils`, Guava cache, and dynamic constructors.

## Risks and Test Signals
`getPortFromHostPortString` and IP regex helpers are IPv4/simple-host oriented and can mishandle IPv6. Static and canonical host caches can become stale. Free-port helpers are inherently race-prone. Tests should cover URI forms with and without schemes, unresolved address creation, static host aliases, canonical URI defaults, socket channel and plain-socket connect paths, loopback self-connect detection, exception wrapping by type, hostname verification, subnet matching including subinterfaces, free-port bounds, and wildcard bind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/NetUtils.java -->
