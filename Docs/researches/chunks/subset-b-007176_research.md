# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.2.xml lines 24259-30698

## Scope

This chunk is a generated JDiff API snapshot for Apache Hadoop Common 2.8.2. It starts inside the tail of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`, covers the remaining legacy metrics SPI records and contexts, the main `org.apache.hadoop.metrics2` public API, metrics2 annotations, filters, mutable metric library classes, sinks, metrics utilities, network topology/socket factory contracts, deprecated Hadoop Record I/O, deprecated record compiler model classes, the Ant task wrapper for the record compiler, and the beginning of the generated record compiler parser package.

The file is API metadata rather than implementation source. The research surface is therefore the public compatibility contract: package boundaries, classes/interfaces, inheritance, implemented interfaces, constructors, methods, fields, visibility, deprecation state, checked exceptions, and embedded Javadocs.

## Purpose

The metrics portions document the transition from the deprecated `org.apache.hadoop.metrics` SPI to the `org.apache.hadoop.metrics2` framework. The legacy SPI still exposes record/tag/metric mutation and null/no-emit contexts, while metrics2 defines collector, record, tag, plugin, source, sink, visitor, registry, mutable metric, cache, MBean, and sink APIs used by Hadoop daemons to publish operational metrics.

The network portion documents rack-awareness and socket factory contracts. DNS-to-switch mappings resolve hostnames or IP addresses to rack paths, cache those resolutions, reload stale mappings, and provide diagnostics. Socket factories supply standard and SOCKS-proxy-backed socket creation for Hadoop IPC/network clients.

The record portion documents deprecated Hadoop Record I/O and its compiler. It preserves binary, CSV, and XML record input/output APIs, buffer and comparator utilities, `WritableComparable` record integration, compiler type-model classes, an Ant task for invoking the compiler, and the beginning of JavaCC-generated parser classes. The package-level docs explicitly mark this stack as replaced by Avro.

## Important APIs, Types, and Functions

### Legacy Metrics SPI

- The chunk begins inside `MetricsRecordImpl`, exposing `getRecordName`, overloaded `setTag` for `String`, `int`, `long`, `short`, and `byte`, `removeTag`, overloaded `setMetric` and `incrMetric` for integer/floating numeric values, plus `update` and `remove`. Javadocs say `update` writes buffered data by tag identity and `remove` deletes the buffered row matching current tags.
- `MetricValue` wraps a `Number` as either absolute or incremental state, with `ABSOLUTE`, `INCREMENT`, `isIncrement`, `isAbsolute`, and `getNumber`.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` are deprecated `AbstractMetricsContext` implementations. They respectively retain records without emitting, do nothing as the default context, or keep periodic update-thread behavior without emitting.
- `OutputRecord` exposes tag and metric names/values and copy-out methods for `AbstractMetricsContext.TagMap` and `MetricMap`.
- Legacy `Util.parse(String, int)` parses comma/space-delimited `host[:port]` server specs into socket addresses, defaulting to localhost and the provided port.

### Metrics2 Core

- `AbstractMetric` implements `MetricsInfo` and defines the common immutable metric contract: `name`, `description`, `info`, abstract `value`, `type`, visitor dispatch, equality, hash, and string conversion.
- `MetricsCollector` creates `MetricsRecordBuilder` instances from a record name or `MetricsInfo`.
- `MetricsException` is the runtime exception used by the framework.
- `MetricsFilter` is a `MetricsPlugin` that accepts or rejects metrics by name, tag, metric object, or record.
- `MetricsInfo`, `MetricsPlugin`, `MetricsRecord`, `MetricsSink`, `MetricsSource`, `MetricsSystemMXBean`, and `MetricsVisitor` are the principal extension interfaces. They cover metric metadata, plugin initialization, timestamped records with tags and metrics, sink `putMetrics`/`flush`, source `getMetrics`, metrics system lifecycle/MBean controls, and visitor callbacks for gauges/counters.
- `MetricsRecordBuilder` is the fluent builder surface for tags, arbitrary metrics, context, counters, gauges for `int`, `long`, `float`, and `double`, and record completion through `parent`/`endRecord`.
- `MetricsSystem` implements `MetricsSystemMXBean` and exposes source registration/unregistration, immediate publication, and shutdown.
- `MetricsTag` implements `MetricsInfo` with `info`, `value`, equality, hash, and string conversion.
- `MetricStringBuilder` is a `MetricsRecordBuilder` subclass that formats tags and metrics into a delimited string while still satisfying builder methods.

### Metrics2 Annotations, Filters, Library Classes, and Sinks

- `@Metric` and `@Metrics` are annotation types used by the metrics framework to derive metric and source metadata from fields/classes.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter` by compiling glob or regex specifications into `Pattern` instances.
- `DefaultMetricsSystem` is an enum singleton facade with `initialize`, `instance`, and `shutdown`.
- `Interns` centralizes interned `MetricsInfo` and `MetricsTag` creation.
- `MetricsRegistry` owns a named registry of mutable metrics and tags. It creates counters, gauges, quantiles, stats, rates, aggregated rates, stores tags with optional override, sets context, and snapshots all registered state into a `MetricsRecordBuilder`.
- `MutableMetric` tracks a changed flag and exposes `snapshot(builder, all)`. Counters, gauges, rates, stats, quantiles, and aggregated rates extend this base.
- `MutableCounterInt` and `MutableCounterLong` expose increment, value, and snapshot operations. `MutableGaugeInt` and `MutableGaugeLong` expose value, increment, decrement, set, and snapshot operations.
- `MutableQuantiles` maintains sampled latency/size distributions at a configured interval, exposes `add`, `snapshot`, `getInterval`, and fields for configured `Quantile[]` plus `previousSnapshot`.
- `MutableStat`, `MutableRate`, `MutableRates`, and `MutableRatesWithAggregation` publish count/average and optional extended statistics for operations, including per-method rates initialized from a protocol/interface class.
- `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`. They initialize from `SubsetConfiguration`, consume `MetricsRecord`, flush, and close; Graphite and StatsD add network-oriented metric emission, with `StatsDSink.writeMetric(String)` visible.

### Metrics2 Utilities

- `MBeans` registers and unregisters Hadoop-standard JMX names of the form `hadoop:service=<serviceName>,name=<nameName>`, and extracts service/name components from `ObjectName`.
- `MetricsCache` caches full records for sinks that cannot handle sparse updates, with constructors accepting default or explicit maximum records per name, update overloads with optional tag caching, and lookup by record name plus tags.
- `Servers.parse(String, int)` is the metrics2 replacement for server-spec parsing.

### Network Topology and Socket APIs

- `AbstractDNSToSwitchMapping` implements `DNSToSwitchMapping` and `Configurable`. It stores configuration, exposes single-switch predicates, diagnostic switch-map copy/dump methods, and static `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `DNSToSwitchMapping` resolves a list of hostnames/IPs to rack paths and exposes cache reload methods for all mappings or selected names. The Javadoc requires output cardinality to match input cardinality and recommends `NetworkTopology.DEFAULT_RACK` for unresolved names.
- `CachedDNSToSwitchMapping` wraps a raw mapping, caches resolved rack paths, exposes the protected final `rawMapping`, returns a cached host-to-rack map copy, delegates single-switch checks, and reloads all or named cache entries.
- `ScriptBasedMapping` extends the cached mapper and reads topology via a configured script, with `NO_SCRIPT`, configuration accessors, and constructors for default, raw mapping, or configuration setup.
- `TableMapping` extends the cached mapper and reads a whitespace-separated two-column mapping file from `net.topology.table.file.name`, defaulting unknown hosts to `/default-rack`.
- `ConnectTimeoutException` extends `SocketTimeoutException` for timed-out `NetUtils.connect(...)` calls.
- `SocksSocketFactory` implements `Configurable` and creates sockets through a SOCKS proxy, with constructors for default or explicit `Proxy`, five `createSocket` overloads, configuration accessors, equality, and hash.
- `StandardSocketFactory` exposes the same socket creation overloads without configuration, plus equality and hash.

### Deprecated Hadoop Record I/O

- `BinaryRecordInput`/`BinaryRecordOutput`, `CsvRecordInput`/`CsvRecordOutput`, and `XmlRecordInput`/`XmlRecordOutput` implement `RecordInput`/`RecordOutput` for primitive values, strings, `Buffer`, records, vectors, and maps. Binary variants include thread-local `get(DataInput/DataOutput)` helpers.
- `Index` exposes `done` and `incr` for iterating record vectors/maps.
- `RecordInput` and `RecordOutput` define format-independent read/write contracts with tagged fields and `IOException` on all stream operations.
- `Buffer` is a mutable comparable byte sequence with constructors for empty, backing-array, or copied range; mutators for set/copy/capacity/reset/truncate/append; accessors for backing bytes, count, and capacity; comparison, equality, hash, string conversion, and clone.
- `Record` implements `WritableComparable` and `Cloneable`; it bridges record serialization/deserialization to Hadoop `Writable` through `write`, `readFields`, `compareTo`, and `toString`.
- `RecordComparator` extends `WritableComparator`, compares byte slices, and registers comparators with `define`.
- `Utils` provides float/double and variable-length integer read/write helpers, variable-int size calculation, byte-slice comparison, and a `hexchars` table.

### Deprecated Record Compiler

- `CodeBuffer` exposes `toString` for generated code accumulation.
- `Consts` exposes constants used by generated record I/O code, including `RIO_PREFIX`, `RTI_VAR`, `RTI_FILTER`, `RTI_FILTER_FIELDS`, `RECORD_OUTPUT`, `RECORD_INPUT`, and `TAG`.
- `JType` is the abstract base for compiler type models. Primitive or compound subclasses in this chunk include `JBoolean`, `JByte`, `JDouble`, `JFloat`, `JInt`, `JLong`, `JBuffer`, `JString`, `JVector`, `JMap`, and `JRecord`.
- `JField` pairs a field name with a type. `JFile` represents a record definition file and generates code with `genCode(language, destDir, options)`.
- `RccTask` is an Ant `Task` wrapper for the record compiler. It accepts `language`, single `file`, nested `FileSet`s, `destdir`, `failonerror`, and runs compilation in `execute`, throwing `BuildException` on configured failures.
- `ParseException` is the JavaCC parser exception with special constructor state, `currentToken`, `expectedTokenSequences`, `tokenImage`, `eol`, customized `getMessage`, and `add_escapes`.
- The chunk ends at the constructors for generated parser class `Rcc`, which implements `RccConstants` and can be constructed from `InputStream`, encoded `InputStream`, `Reader`, or `RccTokenManager`.

## Control Flow

The XML itself has no executable control flow, but the public contracts imply several important flows:

- Legacy metrics flow starts with a metrics record accumulating tags and absolute/incremental metric values. `update` merges the current record into context-owned buffered rows keyed by tags, while `remove` deletes the matching row.
- Metrics2 source flow calls `MetricsSource.getMetrics(collector, all)`, sources add records through `MetricsCollector`, records are populated by `MetricsRecordBuilder`, mutable metrics snapshot into builders, filters accept or reject records/metrics/tags, and sinks receive `MetricsRecord` instances through `putMetrics` before `flush`.
- Metrics registry flow constructs mutable metrics and tags, tracks changed state in `MutableMetric`, and snapshots either changed metrics or all metrics depending on the `all` flag.
- Sink flow initializes from metrics2 configuration, formats or caches records as needed, writes to a file, Graphite endpoint, or StatsD daemon, then flushes/closes resources.
- Rack mapping flow resolves input host lists through raw, script, or table mappings; cached wrappers avoid repeated raw lookups; reload methods invalidate all or selected cache entries; Hadoop block placement and diagnostics query single-switch and switch-map state.
- Socket factory flow is selected/configured by callers, then delegates one of the standard `SocketFactory.createSocket` overloads to either direct sockets or SOCKS proxy sockets.
- Record I/O flow is generated-code driven. Generated `Record` implementations call `startRecord`, per-field read/write methods, vector/map start/end methods, and `endRecord` against a selected binary/CSV/XML implementation. `Index` drives collection traversal on reads.
- Record compiler flow loads `.jr` definitions through the generated `Rcc` parser into `JFile`, `JRecord`, `JField`, and `JType` model objects, then `JFile.genCode` emits Java or C++ output. `RccTask` wraps this flow for Ant builds and applies `failonerror` policy.

## State and Persistence Behavior

The JDiff file persists release API metadata for compatibility comparison. It does not persist runtime application state.

Metrics state is primarily in-memory and time-series oriented. Legacy contexts buffer records by tag sets; no-emit contexts retain data for servlet/JMX-style retrieval without external emission. Metrics2 registries hold mutable metric/tag objects, changed flags, counters, gauges, stats, quantile snapshots, and cached sink records. Sinks are the persistence/export boundary: `FileSink` writes records to files, while Graphite and StatsD export records to external daemons.

Rack mapping state is configuration and cache driven. `AbstractDNSToSwitchMapping` holds a `Configuration`; `CachedDNSToSwitchMapping` persists host-to-rack entries in memory until reload; `TableMapping` reads a durable two-column mapping file; script-based mapping depends on configured external script output. These mappings influence block placement and topology-aware scheduling decisions but do not themselves persist cluster data.

Record I/O APIs define durable wire/file formats. Binary, CSV, and XML record inputs/outputs read and write tagged primitive fields, buffers, records, vectors, and maps. `Record` bridges these formats into Hadoop `Writable` serialization. `Buffer` exposes mutable backing bytes and logical length/capacity, so callers must distinguish valid bytes from allocated storage.

Record compiler state is mostly build-time. `RccTask` holds Ant task configuration and file sets; parser classes hold token/parse-error state; compiler model objects represent parsed record definitions and generate source files into a destination directory. The generated code and serialized record data are the durable outputs.

## Dependencies and Integration Points

- Metrics2 integrates with `org.apache.commons.configuration.SubsetConfiguration`, Java collections, `java.io.Closeable`, JMX `ObjectName`, Hadoop metrics2 utility classes such as `Quantile` and `SampleStat`, and external telemetry systems including files, Graphite, and StatsD.
- Metrics plugin integration is explicit through `MetricsPlugin.init`, `MetricsSource.getMetrics`, `MetricsSink.putMetrics/flush`, `MetricsFilter`, `MetricsVisitor`, and `MetricsSystem.register`.
- Deprecated legacy metrics classes integrate with `org.apache.hadoop.metrics.spi.AbstractMetricsContext` and `MetricsServlet`-style retrieval.
- Network classes integrate with `Configuration`, `Configurable`, `NetUtils`, `NetworkTopology`, `SocketFactory`, `Proxy`, `Socket`, `InetAddress`, and `IOException`/`UnknownHostException` handling.
- Record I/O integrates with Java `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, `IOException`, Hadoop `WritableComparable`, `WritableComparator`, and Java collections used for vectors/maps.
- Record compiler APIs integrate with Ant `Task`, `FileSet`, `BuildException`, JavaCC-generated parser/token classes, destination directories, and generated Java/C++ source code.
- Many APIs in this chunk are deprecated. The metrics SPI points to metrics2 replacements, and Hadoop Record I/O/compiler APIs point to Avro.

## Risks and Edge Cases

- This chunk starts in the middle of `MetricsRecordImpl` and ends in the middle of generated parser class `Rcc`; adjacent chunks are needed for complete per-class reporting.
- Because this is generated JDiff XML, it proves API shape and Javadocs, not implementation details. Exact synchronization, data structures, network timeouts, formatting, and error messages require source validation.
- Legacy metrics and Hadoop Record I/O are deprecated but still public. Removing or changing them can break old downstream code even if modern replacements exist.
- Metrics names, tag names, contexts, and filter rules are compatibility-sensitive. Changes can silently break dashboards, alerts, sink routing, and cached sparse-update behavior.
- `MutableMetric.changed` semantics affect whether snapshots emit only changed values or all values. Incorrect clearing or failure to set changed can lose metric updates for sparse sinks.
- Quantile and rate metrics carry interval/window semantics. Misconfigured intervals or stale `previousSnapshot` values can make operational latency signals misleading.
- File, Graphite, and StatsD sinks expose operational risks around file permissions, endpoint availability, hostname/service-name formatting, flush/close failures, and metric cardinality.
- Rack mapping must preserve one-to-one correspondence between input hosts and returned rack paths. Missing entries, script failures, bad table files, or stale caches can skew block placement and locality.
- Single-switch predicates are policy inputs. Returning the wrong value can change replication/block-placement decisions in ways that are hard to diagnose.
- SOCKS proxy configuration affects all sockets created by `SocksSocketFactory`; equality/hash behavior can matter if socket factories are cached.
- `Buffer` exposes backing arrays and separate count/capacity. Consumers that serialize or compare capacity bytes instead of count bytes can leak stale data or produce wrong ordering.
- Record comparator and variable-length integer utilities are binary-compatibility sensitive; changes can corrupt sort order or persisted record streams.
- The Ant record compiler task can compile multiple files and optionally continue on errors. `failonerror=false` may hide partial generation failures from builds.
- JavaCC `ParseException` has public fields and constructor-dependent message behavior. Customizing it can break parser diagnostics if those fields are not preserved.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that the documented classes, interfaces, constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, deprecation flags, and visibility remain stable for Hadoop Common 2.8.2.
- Legacy metrics tests for tag/metric overloads, absolute vs incremental `MetricValue`, record update/remove matching by tags, null/no-emit context behavior, and server-spec parsing.
- Metrics2 source/collector/builder tests for record construction, tags, context, counters/gauges of each numeric type, visitor dispatch, equality/hash/string behavior, and exception propagation.
- Metrics registry tests for duplicate names, tag override behavior, changed-flag handling, `snapshot(all=false)` vs `snapshot(all=true)`, counter/gauge/rate/stat/quantile creation, and aggregated method-rate initialization.
- Metrics filter tests for glob and regex compilation, acceptance by name/tag/metric/record, invalid patterns, and configuration initialization.
- Sink tests for configuration parsing, file output, Graphite/StatsD formatting, hostname skipping, service/context/name composition, flush behavior, close behavior, and network or IO failure handling.
- Metrics cache tests for sparse record updates, optional tag caching, maximum records per name, lookup by name/tags, and eviction/error behavior when limits are exceeded.
- MBean tests for standard object-name registration, duplicate registration, unregister idempotence, and service/name extraction.
- DNS-to-switch tests for list cardinality, unresolved-host fallback, table-file parsing, script absence via `NO_SCRIPT`, cache hit/miss behavior, selected and full reload, `dumpTopology`, and single-switch policy.
- Socket factory tests for all `createSocket` overloads, proxy configuration, equality/hash, local bind overloads, and `ConnectTimeoutException` propagation through `NetUtils.connect`.
- Record I/O round-trip tests for binary/CSV/XML primitive fields, strings, buffers, nested records, vectors, maps, empty collections, malformed input, and tagged start/end ordering.
- `Buffer` tests for backing-array aliasing, copied ranges, count/capacity mutations, truncation, append growth, comparison, clone, equality, and string rendering.
- `Record`/`RecordComparator` tests for `Writable` bridge methods, byte-slice comparison equivalence with object comparison, and comparator registration via `define`.
- Record compiler tests for parser success/failure diagnostics, `ParseException.getMessage`, code generation for primitive/compound types, Java/C++ language selection, destination directory handling, Ant `FileSet` processing, and `failonerror` behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `MetricsRecordImpl`. The next chunk should complete `org.apache.hadoop.record.compiler.generated.Rcc` and the remaining generated parser/token-manager APIs. The merge lane should reconcile these boundaries before creating the final per-file report.
