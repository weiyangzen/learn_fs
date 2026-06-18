# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 24294-30693

## Scope

This chunk is a generated JDiff API-description slice for Hadoop Common 2.8.0. It starts inside the tail of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`, covers the end of the deprecated `org.apache.hadoop.metrics.spi` package, the public `org.apache.hadoop.metrics2` API core, selected metrics2 annotations, filters, library helpers, sinks, and utilities, then covers `org.apache.hadoop.net` DNS/rack-mapping and socket-factory APIs. It also includes most of the deprecated Hadoop Record I/O runtime and compiler API surface under `org.apache.hadoop.record`, `org.apache.hadoop.record.compiler`, `org.apache.hadoop.record.compiler.ant`, and the beginning of `org.apache.hadoop.record.compiler.generated.Rcc`.

Because the source is JDiff XML rather than executable Java source, control-flow and persistence notes are inferred from documented API contracts, inheritance, synchronization flags, exception signatures, and package-level documentation. The final merge should treat this as API compatibility metadata for the 2.8.0 release, not as implementation code.

## Purpose

The covered metrics APIs document Hadoop's transition from the deprecated original `org.apache.hadoop.metrics` SPI to `org.apache.hadoop.metrics2`. The old SPI entries describe buffered metric values, no-op contexts, output records, and parsing helpers that remain public for compatibility but are explicitly replaced by metrics2. The metrics2 entries define the live source/collector/record/builder/sink/plugin model used by Hadoop daemons to expose counters, gauges, tags, rates, quantiles, and JMX-backed management endpoints.

The network section documents the pluggable hostname/IP-to-rack mapping layer used by Hadoop placement and scheduling logic. It defines the `DNSToSwitchMapping` contract, caching wrapper behavior, script-based mapping configuration, topology diagnostics, and socket factories for standard and SOCKS-proxied connections.

The Record I/O section documents a deprecated serialization and code-generation system replaced by Avro. It still matters as a compatibility surface: generated record classes implement Hadoop `WritableComparable`, records can be serialized in binary, CSV, and XML forms, raw comparators can be registered, and the record compiler plus Ant task still expose public entry points. The package-level documentation also preserves the original DDL, encoding, and Java/C++ mapping contracts.

## Important APIs, Types, and Functions

- `org.apache.hadoop.metrics.spi.MetricValue` wraps a `Number` with either `ABSOLUTE` or `INCREMENT` semantics through `isAbsolute()`, `isIncrement()`, and `getNumber()`.
- `NoEmitMetricsContext`, `NullContext`, and `NullContextWithUpdateThread` extend `AbstractMetricsContext`. They are deprecated compatibility contexts for cases that store-but-do-not-emit, do nothing, or run update callbacks without emitting data.
- `OutputRecord` exposes copied tags and metrics plus lookup by tag or metric name. Its returned tag types are documented as string and small integral types; metrics are numeric.
- `org.apache.hadoop.metrics.spi.Util.parse(String, int)` parses comma/space-separated host or host:port server specs and falls back to localhost with the supplied default port.
- `org.apache.hadoop.metrics2.AbstractMetric` is the immutable metric base. It implements `MetricsInfo`, delegates `name()` and `description()` to its info object, and requires `value()`, `type()`, and `visit(MetricsVisitor)`.
- `MetricsCollector` creates `MetricsRecordBuilder` instances by record name or `MetricsInfo`. `MetricsRecordBuilder` is a fluent abstract builder for tags, metrics, counters, gauges, context tags, and returning to the parent collector.
- `MetricsException` is the unchecked wrapper used across metrics2 constructors, registration, and management calls.
- `MetricsFilter` is a `MetricsPlugin` that accepts or rejects names, tags, tag sets, and whole records. The record-level method is concrete in the API surface while name/tag/tag-set decisions are abstract.
- `MetricsInfo`, `MetricsTag`, `MetricsRecord`, `MetricsSource`, `MetricsSink`, `MetricsVisitor`, `MetricsPlugin`, `MetricsSystem`, and `MetricsSystemMXBean` define the central metrics2 vocabulary: immutable metadata, grouping tags, timestamped records, sources that snapshot into collectors, sinks that consume records, visitor dispatch by metric kind, plugin initialization, source registration, publishing, shutdown, and JMX lifecycle/config access.
- `MetricStringBuilder` is a `MetricsRecordBuilder` implementation that accumulates a formatted string dump using a prefix, separator, and suffix.
- `org.apache.hadoop.metrics2.annotation.Metric` and `Metrics` are annotation types used by the metrics system to infer source metadata and metric fields/methods from annotated objects.
- `GlobFilter` and `RegexFilter` extend `AbstractPatternFilter`, compiling glob or regex expressions for metrics filtering.
- `DefaultMetricsSystem` is a singleton enum-style facade exposing static `initialize(prefix)`, `instance()`, and `shutdown()`.
- `Interns` creates interned `MetricsInfo` and `MetricsTag` objects, reducing duplicate metadata/tag allocation.
- `MetricsRegistry` owns a record/group info object and synchronized metric/tag maps. It can create integer/long counters, integer/long gauges, quantiles, stats, rates, aggregated rates, tags, context tags, add samples by name, and snapshot all registered mutable metrics.
- `MutableMetric` is the abstract changed-tracked metric base. It exposes `snapshot(builder, all)`, a convenience `snapshot(builder)`, protected `setChanged()` and `clearChanged()`, and public `changed()`.
- `MutableCounter`, `MutableCounterInt`, `MutableCounterLong`, `MutableGauge`, `MutableGaugeInt`, `MutableGaugeLong`, `MutableStat`, `MutableRate`, `MutableQuantiles`, `MutableRates`, and `MutableRatesWithAggregation` are the public mutable metric families for counters, gauges, latency/throughput statistics, periodic quantile estimators, synchronized method-rate collections, and thread-local aggregated rate collections.
- `FileSink`, `GraphiteSink`, and `StatsDSink` implement `MetricsSink` and `Closeable`; each initializes from `SubsetConfiguration`, accepts records through `putMetrics()`, flushes, and closes. `StatsDSink` additionally exposes `writeMetric(String)` and documents the StatsD line format plus configuration keys.
- `MBeans` registers and unregisters Hadoop MBeans using the standard `hadoop:service=<serviceName>,name=<nameName>` object-name convention and can extract service/name fields from an `ObjectName`.
- `MetricsCache` stores latest records for sinks that cannot handle sparse updates. It updates from `MetricsRecord`, optionally caches tags for later lookup, and retrieves by record name and tag collection.
- `Servers.parse(String, int)` is the metrics2 replacement for the older SPI server-spec parser.
- `DNSToSwitchMapping` resolves hostnames or IP addresses to network paths such as `/rack`, with cache reload hooks for all nodes or selected nodes.
- `AbstractDNSToSwitchMapping` adds `Configurable`, configuration storage, topology diagnostics, `isSingleSwitch()` policy hooks, `getSwitchMap()`, and static `isMappingSingleSwitch(DNSToSwitchMapping)`.
- `CachedDNSToSwitchMapping` wraps a raw mapper, caches resolved locations, exposes a copy of the host-to-switch map, delegates single-switch queries to the raw mapper, and reloads cached mappings.
- `ScriptBasedMapping` is a cached mapper backed by a script configured by `CommonConfigurationKeys.NET_TOPOLOGY_SCRIPT_FILE_NAME_KEY`; constructors accept default config, a raw mapping, or explicit `Configuration`.
- `ConnectTimeoutException` extends `SocketTimeoutException` and is the timeout surfaced by `NetUtils.connect`.
- `SocksSocketFactory` and `StandardSocketFactory` extend `javax.net.SocketFactory`. The SOCKS variant is configurable and equality/hash behavior depends on proxy configuration; the standard factory exposes direct socket creation methods.
- `TableMapping` extends `CachedDNSToSwitchMapping`, is configurable, and reloads mappings from a table-backed source.
- `BinaryRecordInput`/`BinaryRecordOutput`, `CsvRecordInput`/`CsvRecordOutput`, and `XmlRecordInput`/`XmlRecordOutput` implement the deprecated `RecordInput` and `RecordOutput` contracts for primitive values, `Buffer`, records, vectors, and maps.
- `Buffer` is a deprecated mutable byte sequence with capacity/count distinction, copy/set/append/truncate/reset operations, comparison, equality, cloning, and string conversion.
- `Index` is the iterator-like deserialization cursor returned by `startVector()` and `startMap()`.
- `Record` is the generated-record base class. It implements `WritableComparable` and `Cloneable`, requiring tagged `serialize`, tagged `deserialize`, and `compareTo`, while providing untagged serialize/deserialize plus `write(DataOutput)`, `readFields(DataInput)`, and `toString()`.
- `RecordComparator` is a `WritableComparator` base for optimized raw comparison of serialized `Record` implementations, with synchronized static `define(Class, RecordComparator)`.
- `RecordInput` and `RecordOutput` define the serializer/deserializer interface for byte, bool, int, long, float, double, UTF-8 string, `Buffer`, record, vector, and map boundaries.
- `Utils` provides deprecated record encoding helpers: float/double reading, variable-length int/long read/write, variable-int size calculation, byte comparison, and hex characters.
- `org.apache.hadoop.record.compiler` includes `CodeBuffer`, constants, primitive and compound type descriptors (`JBoolean`, `JByte`, `JInt`, `JLong`, `JFloat`, `JDouble`, `JString`, `JBuffer`, `JMap`, `JVector`, `JRecord`, `JType`, `JField`), and `JFile.genCode(language, outputDirectory)`.
- `RccTask` is the Ant integration for the record compiler, accepting language, single file, filesets, destination directory, fail-on-error behavior, and `execute()`.
- `ParseException` is the JavaCC parser exception for record compiler parse failures, carrying `currentToken`, `expectedTokenSequences`, `tokenImage`, a special-constructor flag, and ASCII escaping for generated messages.
- `Rcc` begins in this chunk with parser constructors, `main`, `usage`, `driver`, grammar productions such as `Input`, `Include`, `Module`, `ModuleName`, `RecordList`, `Record`, `Field`, `Type`, `Map`, `Vector`, parser reinitialization overloads, token accessors, and the start of `generateParseException()`.

## Control Flow

The old metrics SPI flow is context-buffer oriented. `MetricsRecordImpl` collects tags and metric values, then delegates `update()` and `remove()` back to its owning context. `MetricValue` tells that context whether an incoming number replaces the stored value or increments it. `NoEmitMetricsContext` keeps enough state for retrieval, `NullContext` drops everything, and `NullContextWithUpdateThread` keeps periodic updater callbacks active without emitting to an external sink.

The metrics2 flow is source-pull and sink-push. A `MetricsSystem` registers source objects, either directly with a name/description or by deriving metadata from annotations. When collection occurs, each `MetricsSource.getMetrics(collector, all)` receives a collector, calls `addRecord()`, and fills a builder with tags and metrics. The collector produces `MetricsRecord` instances; sinks receive them through `putMetrics()` and may flush or close during system stop. `publishMetricsNow()` is documented as a best-effort synchronous snapshot-and-flush path, while normal publishing is periodic in the implementation.

Mutable metrics follow an update-then-snapshot pattern. Counters increment, gauges increment/decrement/set, stats and rates accumulate samples, and quantiles add long values. `MutableMetric` tracks whether a metric changed so `snapshot(builder, all)` can skip unchanged values unless the caller requests all. `MutableStat` and `MutableQuantiles` synchronize sample update and snapshot methods. `MutableRates` synchronizes all access to its managed rate set, while `MutableRatesWithAggregation` moves per-thread updates into local rate counts and aggregates during synchronized snapshot.

Filtering is layered into metrics collection and sink pipelines. `GlobFilter` and `RegexFilter` compile configured patterns. `MetricsFilter.accepts(record)` can consider the record's name and tags after the lower-level name/tag predicates. `MetricsCache` sits on the sink side: incoming sparse `MetricsRecord` updates are merged into a stored record so sinks that require full records can render current state.

Network mapping flow starts with a list of hostnames/IPs and requires a returned list of network paths in the same order. `CachedDNSToSwitchMapping.resolve()` checks its cache, delegates misses to `rawMapping`, stores results, and returns a full ordered list. Cache reload calls either clear all mappings or selected names. `ScriptBasedMapping` configures the raw mapper from Hadoop configuration, invokes the script-defined mapping implementation underneath, then inherits caching. `AbstractDNSToSwitchMapping.dumpTopology()` reports implementation, known node mappings, and unique switch count for diagnostics.

Socket factory flow follows the `javax.net.SocketFactory` contract: callers ask for sockets by host/port or address/port, and the factory returns configured direct or proxied sockets. `SocksSocketFactory` additionally receives Hadoop configuration through `setConf()` before use, so proxy settings are configuration-driven.

Record I/O flow is DDL-to-generated-code plus runtime serialization. A `.jr` file declares includes, one module, and records. The record compiler parses input into `JFile`, `JRecord`, `JField`, and `JType` objects, then `genCode()` emits Java or C++ record code. The Ant task wraps this driver over a single file or nested filesets and optionally fails the build on errors.

Runtime Record I/O flow is stream-recursive. Generated `Record` subclasses implement tagged `serialize(RecordOutput, tag)` and `deserialize(RecordInput, tag)`. Binary, CSV, and XML record inputs/outputs read or write primitives, buffers, record boundaries, vector boundaries, and map boundaries. For vectors and maps, `startVector()` or `startMap()` returns an `Index`; generated deserializers loop until `done()` and call `incr()` after reading each element. `Record.write()` and `readFields()` bridge the record serialization contract to Hadoop `Writable`.

## State and Persistence Behavior

The XML file itself is static generated API metadata and does not persist runtime state. It is part of the dev-support compatibility surface used to compare public API changes across releases.

Metrics2 runtime state is held in registries, mutable metrics, caches, sinks, MBeans, and the default metrics system singleton. `MetricsRegistry` persists in-process metric objects and tags for a source. `MutableMetric.changed` state determines whether a metric appears in sparse snapshots. Counters and gauges keep current numeric values; stats keep rolling sample summaries; quantiles keep online estimators and a `previousSnapshot` map; aggregated rates keep thread-local sample data that can be lost if a short-lived thread dies before snapshot. `DefaultMetricsSystem` holds global singleton lifecycle state. `MBeans.register()` persists a platform MBean registration until explicit unregister or metrics shutdown.

Metrics sink persistence depends on the sink. `FileSink` writes records to a file-like target and must flush/close. `GraphiteSink` and `StatsDSink` emit to external monitoring daemons over network connections and may drop or fail metrics depending on connection state. `MetricsCache` is memory-only and stores the latest complete view of sparse records for sink formatting.

Network mapping state is process-local. `CachedDNSToSwitchMapping` stores host-to-rack cache entries and returns copies for diagnostics. Reload methods invalidate all or selected entries so future `resolve()` calls can observe changed topology data. `ScriptBasedMapping` stores configuration and script policy; `TableMapping` stores configuration for table lookup. These mappings influence HDFS block placement, YARN scheduling, and other topology-aware policies, but the mapping APIs themselves do not persist cluster topology remotely.

Record I/O state is stream and object state. `Buffer` owns or references a backing byte array and tracks count and capacity; using `set(byte[])` adopts the supplied array as backing storage while `copy()` replaces data with a copied range. Record inputs/outputs maintain stream cursors and encoding-specific parser/formatter state. Generated `Record` instances own field values and can be persisted through Hadoop Writable serialization, binary record streams, CSV text streams, XML streams, or generated C++/Java code. `RecordComparator.define()` mutates global comparator registration state for raw comparisons.

Record compiler state is parse/generation state. `ParseException` captures parser token state and expected token sequences. `Rcc` parser instances retain token manager/input stream state and can be reinitialized against new streams or readers. `RccTask` stores Ant task configuration including language, destination directory, filesets, and fail-on-error behavior before `execute()`.

## Dependencies and Integration Points

Metrics2 integrates with `org.apache.commons.configuration.SubsetConfiguration` for plugin/sink initialization, SLF4J/logging in implementations outside this slice, JMX through `MetricsSystemMXBean` and `MBeans`, Java annotations through `Metric`/`Metrics`, and Hadoop daemon source objects through `MetricsSource`. It also depends on utility classes from `org.apache.hadoop.metrics2.util` and mutable metric implementations in `org.apache.hadoop.metrics2.lib`.

Metrics records and tags depend on `MetricsInfo` identity and naming. `Interns` is an integration point for reducing duplicate info/tag objects, while `MetricStringBuilder` gives logging/debug output a builder-compatible sink. File, Graphite, and StatsD sinks connect the same record abstraction to local files and external observability systems.

Network topology APIs integrate with `org.apache.hadoop.conf.Configuration`, `Configurable`, `CommonConfigurationKeys`, `NetworkTopology.DEFAULT_RACK`, `NetUtils`, and Java networking types such as `Socket`, `InetAddress`, `InetSocketAddress`, `Proxy`, and `SocketTimeoutException`. The rack mapping contract is used by higher-level distributed filesystem and cluster scheduler code that needs placement locality and single-rack/multi-rack policy decisions.

Record I/O integrates with Hadoop's `Writable`, `WritableComparable`, and `WritableComparator` APIs, Java `DataInput`/`DataOutput`, JavaCC-generated parser classes, Ant `Task`/`FileSet`/`BuildException`, and generated C++ support files described by the package docs. The API is explicitly deprecated in favor of Avro, but the compatibility surface remains public in 2.8.0.

## Risks and Edge Cases

The biggest metrics risk is concurrency and sparse-state semantics. Some `MetricsRegistry` and mutable metric methods are synchronized while others are not; callers need the implementation's thread-safety guarantees, especially around high-volume counters, gauges, and rates. `MutableRates` is documented as high-contention-unfriendly, and `MutableRatesWithAggregation` can lose samples produced by threads that die before the next snapshot.

Metric identity is name/tag driven. Duplicate metric names or tags in a `MetricsRegistry` can conflict, and tag override behavior must be explicit. `MetricsFilter` implementations can accidentally drop whole records if tag-set and record-level predicates do not match. `MetricsCache` can grow or evict based on max records per name; sinks relying on complete state need tests for eviction and tag-included lookup behavior.

Sink behavior is externally fragile. File, Graphite, and StatsD sinks depend on filesystem or network availability and on correct configuration keys. `publishMetricsNow()` is only best-effort, so tests and admin tooling must not assume all sinks are fully flushed before the call returns.

JMX registration has naming collision risk. `MBeans.register()` uses a standard `hadoop:service=...,name=...` convention, so duplicate service/name pairs or invalid object-name characters can fail registration or hide the intended MBean. `currentConfig()` deliberately avoids a getter name that JConsole would expose as an unsupported multiline attribute.

Network topology mapping has correctness risk because placement policy consumes the returned rack paths. `DNSToSwitchMapping.resolve()` must preserve input order and size; unresolved nodes should normally map to `NetworkTopology.DEFAULT_RACK`. Cache reload gaps can leave stale rack assignments in long-running processes. `AbstractDNSToSwitchMapping.isMappingSingleSwitch()` documentation is subtle and should be confirmed against implementation because single-switch detection changes block-placement and scheduling decisions.

Script-based mapping is operationally sensitive. Missing scripts, slow scripts, script failures, malformed output, and configuration reload behavior all affect cluster topology visibility. The public `NO_SCRIPT` text is only diagnostic; lack of a script generally means default rack behavior, not an executable mapping.

Socket factories can affect all client connections using them. SOCKS proxy equality/hash behavior matters if factories are cached. Misconfigured proxies can produce hard-to-diagnose connection failures, while `ConnectTimeoutException` should be preserved distinctly from read timeouts and generic socket errors.

Record I/O carries deprecation and compatibility risk. New code should not build on it, but existing serialized data and generated code may depend on exact binary, CSV, XML, comparison, and Writable behavior. The package docs show several historical spelling and markup issues; the final report should treat the generated API and implementation tests as authoritative over prose typos.

`Buffer` exposes backing array behavior: `get()` returns data valid only through `getCount()`, and `set(byte[])` adopts the supplied storage. Callers can accidentally mutate shared data or read capacity bytes beyond count. Capacity shrink/grow and append operations need bounds tests.

Record encodings have format-specific edge cases: variable-length integer encoding boundaries; UTF-8 normalization; percent escaping for CSV and XML strings/buffers; XML restrictions around null/control characters and carriage returns; CSV delimiter escaping; vector/map size handling; and cross-language C++/Java type mappings. Raw comparator registration is global and synchronized, so duplicate or incompatible comparators can affect sorting/job behavior.

The chunk ends inside `org.apache.hadoop.record.compiler.generated.Rcc`, so parser control-flow and parser fields are incomplete in this research document. Adjacent chunk reconciliation is needed before making final statements about the full generated parser API.

## Test Signals

Useful validation for the metrics surface should include:

- Old SPI compatibility tests for `MetricValue` absolute vs increment behavior, `OutputRecord` copied tag/metric maps, null/no-emit contexts, and server-spec parsing with null, comma, space, host-only, and host:port inputs.
- Metrics2 source lifecycle tests covering `MetricsSystem.register()` by object and by explicit name/description, duplicate source registration, unregister, callback registration, `publishMetricsNow()` best-effort behavior, and shutdown return value.
- Builder tests verifying tags, context tags, counters, gauges of every primitive width, abstract metrics, parent/endRecord chaining, and `MetricStringBuilder` formatting.
- Filter tests for glob and regex configuration, name/tag/tag-set/record predicate interactions, and rejection effects on records reaching sinks.
- `MetricsRegistry` tests for duplicate metrics/tags, override vs non-override tags, synchronized getters, creation of each mutable metric type, `add(name, value)`, `snapshot()`, and context tag output.
- Mutable metric tests for changed flag handling, `all=false` sparse snapshots, counter/gauge increments and decrements, stat mean/min/max/stddev behavior, quantile rollover intervals and invalid interval errors, and reset-min-max.
- Concurrency tests comparing `MutableRates` under contention with `MutableRatesWithAggregation`, including the documented case where samples from short-lived threads can be lost before snapshot.
- Sink tests for file output/flush/close, Graphite connection failure handling, StatsD line formatting with and without hostname, service name configuration, and `MetricsCache` sparse update merging and max-record eviction.
- JMX tests for `MBeans.register()` object-name format, service/name extraction, duplicate names, unregister idempotence, and metrics MBean start/stop through `MetricsSystemMXBean`.

Network and socket tests should include:

- `DNSToSwitchMapping.resolve()` preserving order and count for empty, known, unknown, hostname, and IP inputs, plus default-rack fallback.
- Cache hit/miss behavior in `CachedDNSToSwitchMapping`, `getSwitchMap()` returning a defensive copy, selected and full reload invalidation, and delegation of single-switch policy.
- `ScriptBasedMapping` behavior for no script, configured script, failing script, malformed output, configuration reload, and diagnostic `toString()`.
- `TableMapping` configuration loading and reload behavior.
- `SocksSocketFactory` and `StandardSocketFactory` socket creation overloads, equality/hash code, proxy configuration, connection timeout propagation as `ConnectTimeoutException`, and direct vs proxied connection routing.

Record I/O and compiler tests should include:

- Binary, CSV, and XML round trips for every primitive, nested records, vectors, maps, empty collections, large buffers, UTF-8 strings, percent-escaped CSV/XML characters, control characters, and variable-length integer boundary values.
- `Buffer` tests for constructor ownership/copy semantics, `set`, `copy`, `append`, `reset`, `truncate`, capacity changes, comparison, equality, clone, and string conversion with explicit charset.
- Generated `Record` tests for tagged and untagged serialize/deserialize, `Writable.write/readFields`, `compareTo`, `toString`, equality/hash behavior in generated classes, and raw `RecordComparator.define()` registration.
- `RecordInput`/`RecordOutput` tests that generated code correctly consumes `Index.done()` and `Index.incr()` for vectors/maps and handles mismatched collection sizes or malformed input.
- `Utils` tests for zero-compressed VInt/VLong read/write, size calculation, float/double network byte order, and byte comparison.
- Record compiler tests for includes, module parsing, primitive/compound type parsing, Java and C++ code generation output paths, generated package/namespace mapping, invalid DDL parse exceptions with expected-token messages, and `Rcc.ReInit()` reuse.
- `RccTask` Ant tests for single file vs fileset inputs, language selection, destination directory, fail-on-error true/false, and build exception behavior.

## Cross-Chunk Notes

This chunk starts after the beginning of `org.apache.hadoop.metrics.spi.MetricsRecordImpl`, so the full old-SPI record implementation API must be merged from the previous chunk. It also ends inside the `org.apache.hadoop.record.compiler.generated.Rcc` class, before the generated parser class is complete. The final per-file research should combine this with adjacent chunks and should keep the distinction clear between generated JDiff API metadata and actual Java implementation files.
