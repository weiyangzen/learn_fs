# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 30909-37234

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.1, not implementation source. It records class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The range starts inside `org.apache.hadoop.mapred.lib.InputSampler`, after the class declaration and earlier methods, then covers the rest of `InputSampler` plus most of `org.apache.hadoop.mapred.lib`, all visible `org.apache.hadoop.mapred.lib.aggregate` and `org.apache.hadoop.mapred.lib.db` APIs, `org.apache.hadoop.mapred.pipes.Submitter`, Hadoop's original metrics API/SPI/provider/util classes, and most of `org.apache.hadoop.net` through the start of `SocketInputStream`. The final `SocketInputStream` class continues beyond this chunk, so its trailing Javadoc and any later members must be reconciled with the adjacent chunk.

## Purpose and Major API Surface

The initial `InputSampler` fragment documents total-order sampling support for old `mapred`. `writePartitionFile` samples keys from an `InputFormat`, sorts them with the job's output key comparator, selects split points for reduce ranks, and writes the partition file named by `TotalOrderPartitioner.getPartitionFile`. The nested `Sampler<K,V>` interface defines `getSample(InputFormat<K,V>, JobConf)`. `IntervalSampler`, `RandomSampler`, and `SplitSampler` implement it with regular-interval, probabilistic, and first-records-per-split strategies, each bounded by a maximum number of splits when configured.

`org.apache.hadoop.mapred.lib` contains stock old-API MapReduce helpers. `InverseMapper` swaps key/value pairs, `LongSumReducer` sums `LongWritable` values, `RegexMapper` emits regular-expression captures, `TokenCountMapper` tokenizes text values, and `NullOutputFormat` provides a sink output format. `NLineInputFormat` splits text input by a configured number of lines and returns `LongWritable`/`Text` readers.

`KeyFieldBasedComparator` and `KeyFieldBasedPartitioner` implement Unix-sort-like key field selection. The comparator supports numeric and reverse ordering plus `-k pos1[,pos2]`, interpreting fields separated by `map.output.key.field.separator`. The partitioner hashes configured key fields and exposes a protected byte-range `hashCode` helper. `TotalOrderPartitioner` consumes the partition file written by `InputSampler`; it has `configure`, `getPartition`, and static `setPartitionFile`/`getPartitionFile` methods plus `DEFAULT_PATH`.

`MultipleInputs` configures jobs with path-specific `InputFormat` classes, optionally path-specific `Mapper` classes. `MultipleOutputFormat` is an abstract `FileOutputFormat` that routes records to different files by overriding leaf filename generation, key/value-based filename generation, actual key/value generation, input-file-derived names, and the base writer. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide concrete sequence-file and text writers.

`MultipleOutputs` is the named-output API for old `mapred`. Static methods register single or multi named outputs in `JobConf`, inspect their output format/key/value classes, and enable counters. Instance methods create `OutputCollector`s for named or multi-named channels and close all opened writers. The docs constrain named output names to letters/numbers and disallow `part`; mapper-side named output records bypass the reduce phase unless also written to the main collector. Counters are disabled by default, use `MultipleOutputs` as the group, and use the named output or `namedOutput_multiName` as counter names.

`MultithreadedMapRunner` runs mapper calls concurrently under old `mapred`, exposing `configure(JobConf)` and `run(RecordReader, OutputCollector, Reporter)`.

`org.apache.hadoop.mapred.lib.aggregate` is the old aggregation framework. `ValueAggregator` defines mutable aggregators with `addNextValue`, `reset`, `getReport`, and combiner output. Implementations include `LongValueSum`, `LongValueMax`, `LongValueMin`, `DoubleValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. They keep running sums, extrema, unique sets, or histograms and emit report strings plus combiner-friendly intermediate values.

`ValueAggregatorDescriptor` maps input key/value records to aggregation key/value pairs and exposes constants `TYPE_SEPARATOR` and `ONE`. `ValueAggregatorBaseDescriptor` supplies common type names such as `LONG_VALUE_SUM`, `DOUBLE_VALUE_SUM`, `VALUE_HISTOGRAM`, and extrema/string variants, and can generate typed aggregators or text entries. `UserDefinedValueAggregatorDescriptor` reflectively constructs user descriptors from a class name and `JobConf`. `ValueAggregatorJobBase` stores configured descriptor lists; mapper, combiner, and reducer subclasses implement the generic aggregation pipeline. `ValueAggregatorJob` creates `JobConf` or `JobControl` instances for complete aggregate jobs and can configure descriptor classes.

`org.apache.hadoop.mapred.lib.db` exposes JDBC input/output formats. `DBConfiguration` is a constants holder and setup utility for driver, URL, username, password, input table/fields/conditions/order, complete input query and count query, input DBWritable class, output table, and output fields. `DBInputFormat` implements `InputFormat<LongWritable,T extends DBWritable>` and `JobConfigurable`; it configures a database-backed reader, creates row-range splits, and supports table/conditions/order/fields or full query/count-query setup. `DBInputSplit` serializes start/end row indexes. `DBRecordReader` builds select queries, iterates rows into `DBWritable` values, tracks position/progress, and closes JDBC resources. `NullDBWritable` is a do-nothing DB/Writable bridge. `DBOutputFormat` writes reducer output keys extending `DBWritable` into SQL tables with a prepared insert query; its `DBRecordWriter` writes only the key and closes on task completion. `DBWritable` defines `write(PreparedStatement)` and `readFields(ResultSet)`.

`org.apache.hadoop.mapred.pipes.Submitter` is the public entry point for Hadoop Pipes jobs. It gets/sets the executable, toggles whether the record reader, mapper, reducer, and record writer are Java implementations, controls keeping the command file for debugging, submits or runs a configured job, and provides `run`/`main`.

The metrics packages describe Hadoop's original metrics subsystem. `ContextFactory` stores attributes, creates named contexts from configuration, and returns a singleton factory or null context. `MetricsContext` manages lifecycle, record creation, periodic updater registration, and the default period. `MetricsRecord` is the typed tag/metric interface with setters for string/int/long/short/byte tags, metric setters/incrementers for int/long/short/byte/float, and `update`/`remove`. `MetricsUtil` gets contexts and creates host-tagged records; `Updater` is the periodic callback.

Metrics providers and SPI include `FileContext` for file/stdout output, `GangliaContext` for Ganglia emission, `EventCounter` as a Log4J appender with fatal/error/warn/info counters, `JvmMetrics` as a JVM metrics updater, `AbstractMetricsContext` as the synchronized provider base, `MetricsRecordImpl` as the record implementation, `MetricValue` as absolute-vs-incremental numbers, `NullContext` and `NullContextWithUpdateThread`, `OutputRecord`, and `Util.parse` for server specifications.

`org.apache.hadoop.metrics.util` provides JMX and mutable metric helpers. `MBeanUtil` registers/unregisters Hadoop-format MBeans. `MetricsIntValue` and `MetricsLongValue` are synchronized non-time-varied gauges/counters with set/get/inc/dec/push behavior. `MetricsTimeVaryingInt` pushes per-period deltas. `MetricsTimeVaryingRate` tracks operation counts, average time for the previous interval, min/max operation time, and min/max reset.

The `org.apache.hadoop.net` section covers DNS, rack mapping, socket, and topology helpers. `CachedDNSToSwitchMapping` wraps a raw `DNSToSwitchMapping` with a cache. `DNS` performs reverse DNS, interface IP lookup, default IP/host lookup, and nameserver-based host lookup. `DNSToSwitchMapping` resolves names/IPs to rack strings. `ScriptBasedMapping` is a final configurable mapping implementation driven by `topology.script.file.name`.

`NetUtils` centralizes RPC/network helpers: socket factory lookup from class-specific and default configuration keys, socket address parsing from `host`, `host:port`, or URI strings, migration from old bind-address/port pairs to a combined address property, static host resolution mappings for tests, client connect address normalization for wildcard-bound servers, timeout-capable socket input/output stream wrappers, and host name normalization to textual IP addresses.

`NetworkTopology`, `Node`, and `NodeBase` model Hadoop's rack-aware cluster tree. `NetworkTopology` adds/removes leaf nodes, counts racks/leaves, looks up nodes by path, computes distance through closest common ancestors, checks rack co-location, chooses random nodes within or outside scopes, counts available nodes excluding a list, stringifies the tree, and pseudo-sorts replica locations by reader distance. `Node` exposes name, network location, parent, and level. `NodeBase` implements those fields plus path normalization and path construction constants.

`SocketInputStream` begins at the end of the range. It wraps a `ReadableByteChannel` or `Socket` as an `InputStream` and `ReadableByteChannel` with read timeouts. Construction configures the underlying selectable channel as non-blocking, zero timeout means infinite wait, negative timeout is invalid, `waitForReadable` waits with the stream timeout, and `close` is synchronized.

## Control Flow and Behavioral Contracts

Total-order partition setup flows from `InputSampler.run` or direct API use: configure a `JobConf`, instantiate a sampler, call `getSample` over selected input splits, sort sampled keys with the output key comparator, choose partition boundaries for reducer ranks, and persist them for `TotalOrderPartitioner`. `RandomSampler` shuffles split order and may replace earlier sampled keys after a split quota is full; `IntervalSampler` emits keys based on retained/seen record ratios; `SplitSampler` takes leading records from each sampled split. These operations run on the client side and can be expensive for many splits.

MapReduce helper control flow follows the old `Mapper`/`Reducer`/`OutputFormat` template. Mappers and reducers receive key/value pairs plus `OutputCollector` and `Reporter`; output formats validate and create writers; `MultipleOutputFormat` routes each record through filename/key/value hooks before delegating to a base writer. `MultipleOutputs` must be constructed during task `configure`, used to obtain collectors during map/reduce, and closed in `close`; unclosed collectors risk incomplete files.

Field-based comparison and partitioning are driven by `JobConf`. Callers configure sort or partition key specs, and the comparator/partitioner parse field and character positions using one-based indexes with end-position zero meaning end of field. Numeric and reverse modifiers affect comparator results; partitioning hashes byte ranges from selected key fields.

Aggregation flow is descriptor driven. The mapper iterates configured `ValueAggregatorDescriptor`s for each input record and emits `Text` aggregation IDs and values. Combiners and reducers select a `ValueAggregator` by type prefix, feed it values, and emit either combiner intermediates or final report strings. `ValueAggregatorJob` packages this configuration into one or more jobs.

DB input flow connects through JDBC during `configure`/reader construction, computes row counts through `getCountQuery`, divides rows into `DBInputSplit` start/end ranges, builds a select query per split, and calls `DBWritable.readFields(ResultSet)` for each row. DB output flow constructs an insert `PreparedStatement`, calls `DBWritable.write(PreparedStatement)` on output keys, and writes batches/commits during writer close. The API intentionally ignores output values.

Pipes submission flow mutates the supplied `JobConf` with executable and Java/non-Java component settings, optionally keeps a command file for debug replay, then submits or runs the job through the classic `JobClient` path. The command-line `run`/`main` methods expose the same setup to users.

Metrics flow is buffered and periodic. A caller obtains a `MetricsContext`, creates records, sets tags and metrics, and calls `update`. The context's internal table is keyed by record name plus tag values; matching rows are updated and new tag sets create new rows. Registered `Updater`s are called on the configured period, providers emit each buffered row through `emitRecord`, and `flush` runs after a period. `remove` deletes matching rows; `stopMonitoring` pauses provider output; `close` stops monitoring and clears buffered state.

Network flow starts with name/rack resolution. `DNS` and `DNSToSwitchMapping` turn interfaces, hostnames, IPs, and rack scripts into normalized addresses or rack paths. `CachedDNSToSwitchMapping` reduces repeated raw resolver calls. `NetworkTopology` consumes `Node`/`NodeBase` objects whose network locations are path-like rack/datacenter strings, then uses those locations for block placement style decisions such as distance ordering and rack diversity checks. `NetUtils` bridges configuration, static test resolutions, wildcard listener addresses, and timeout-capable channel streams.

`SocketInputStream` read flow is select-based. Reads on the non-blocking channel either read immediately or call `waitForReadable`; if the selector times out, the contract raises `SocketTimeoutException`. After wrapping a socket channel this way, the docs warn that using the socket's ordinary input/output streams can throw because the channel has been switched to non-blocking mode.

## State, Persistence, and Side Effects

The XML itself is persistent API compatibility data. Runtime persistent or externally visible state includes total-order partition files, job configuration keys, MapReduce output files, named-output files and counters, aggregate reports, JDBC connections/statements/result sets, SQL table rows, Pipes executable and command-file settings, metrics configuration attributes, buffered metrics tables, provider output files or Ganglia packets, Log4J event counts, JMX MBean registrations, DNS/rack caches, static host-resolution maps, network topology trees, and socket channel modes.

Most mapred helpers keep behavior in `JobConf`: input paths/formats/mappers, output format classes and named-output key/value classes, counter enablement, field separators, regex settings, line split settings, total-order partition file path, aggregate descriptor classes, DB connection details, and Pipes toggles. These settings are serialized through job submission and become part of task behavior.

The DB APIs have strong external side effects. Input formats run count and select SQL queries against configured databases. Output formats construct insert statements and write reducer keys into tables. `DBWritable` implementations own object-to-column mapping and must keep JDBC parameter/result-set ordering consistent with configured field names.

Metrics state is global and provider-specific. `ContextFactory` is a singleton attribute store. `AbstractMetricsContext` holds monitoring period, updater lists, and buffered records; `MetricsRecordImpl` holds mutable tags/metrics before update. `FileContext` opens configured files in append mode or uses stdout, while `GangliaContext` emits over the network. `NullContextWithUpdateThread` keeps periodic updater calls even though records are discarded.

Network state includes mutable static host resolutions in `NetUtils`, resolver caches in `CachedDNSToSwitchMapping`, mutable parent/level/name/location fields in `NodeBase`, and counts/tree links in `NetworkTopology`. `SocketInputStream` mutates the underlying channel by setting non-blocking mode and synchronizes close.

## Dependencies and Integration Points

This chunk is anchored in the old `org.apache.hadoop.mapred` API: `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `OutputCollector`, `Reporter`, `Partitioner`, `OutputFormat`, `RecordWriter`, `FileInputFormat`, `FileOutputFormat`, `SequenceFileOutputFormat`, `TextOutputFormat`, `RunningJob`, and `JobControl`. It also depends on Hadoop IO types such as `Writable`, `WritableComparable`, `LongWritable`, `Text`, and `WritableComparator`, plus filesystem types `Path` and `FileSystem`.

Aggregate and DB integration reaches outside HDFS/MapReduce. Aggregation uses Java collections and text-encoded intermediate keys/values. DB formats depend on JDBC `Connection`, `PreparedStatement`, `ResultSet`, `SQLException`, configured JDBC driver classes, and SQL dialect support for count/select/limit/offset style queries implied by split readers.

Pipes integrates Java job submission with non-Java executables, distributed job resources, and task-local command files. Correctness depends on matching the Java/non-Java component flags to the actual executable protocol.

Metrics integrates with `hadoop-metrics.properties`/`ContextFactory` attributes, provider reflection, file IO, Ganglia, Log4J, JVM runtime metrics, JMX `ObjectName`s, and Hadoop components that register `Updater`s. `MetricsUtil` hides provider creation failures by logging and returning a null context.

Networking integrates with Java networking (`InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `SocketChannel`, selectable NIO channels), Hadoop IPC `Server` and `VersionedProtocol`-style configuration, external topology scripts, DNS infrastructure, and HDFS block placement concepts represented by rack-aware `Node`s.

## Risks and Compatibility Notes

This range has partial boundaries. `InputSampler` starts before line 30909 and `SocketInputStream` continues after line 37234, so final per-file research must merge adjacent chunks before making whole-class conclusions for those two APIs.

Because this is a JDiff compatibility artifact, seemingly small changes to signatures, generic type text, visibility, checked exceptions, static/final/synchronized flags, fields, deprecation metadata, or Javadocs can indicate source or binary compatibility changes for Hadoop 0.19.1 clients.

Sampling and total-order partitioning are correctness-sensitive. If sampled keys are sparse, skewed, or sorted with a comparator different from task output comparison, reducer ranges can be unbalanced or incorrect. Client-side sampling can read many splits, so `RandomSampler` over all splits is explicitly expensive.

Field-based comparator/partitioner behavior is fragile around one-based field indexes, character offsets, numeric parsing, reverse flags, separators, and byte-range hashing. Parser changes can break jobs that model Unix `sort` keys in configuration strings.

Multiple output APIs can create many task output files. Bad named-output validation, filename derivation, multi-name handling, missing `close`, or counter naming changes can cause file collisions, invalid paths, leaked writers, missing data, or incompatible counters.

Aggregation keys encode type and aggregation ID in text. Separator collisions, malformed numeric inputs, inconsistent combiner output, very large unique sets or histograms, and descriptor class-loading failures can corrupt results or exhaust memory.

DB formats are exposed to SQL correctness and transactional risk. Count/select mismatch, unstable ordering, SQL injection through configuration strings, driver-specific limit/offset behavior, incorrect `DBWritable` field order, commit/rollback behavior, and connection leaks can produce duplicate/missing rows or failed tasks.

Metrics APIs are mutable and partly concurrent. The docs say `MetricsRecord.update` is atomic for separate record instances with the same tags, but the same `MetricsRecord` instance should not be used concurrently. Provider misconfiguration can silently fall back to null metrics through `MetricsUtil`, while updater exceptions, incremental-vs-absolute handling, tag matching in `remove`, and monitoring lifecycle races affect observability.

Network APIs are environment-dependent. DNS and topology scripts can fail or return mismatched list lengths; static resolutions are process-global; wildcard address normalization must preserve reachable ports; socket factory properties may be malformed; non-blocking channel wrapping can surprise callers that later use raw socket streams.

Network topology assumes nodes are leaves when added, have normalized path-like locations, and belong to the same cluster for distance/rack checks. Wrong parent/level state or unsynchronized mutation can break rack-aware placement calculations.

## Test Signals

JDiff validation should confirm this XML range stays well formed at chunk boundaries and preserves each public/protected class, interface, constructor, method, field, generic signature, exception declaration, visibility/static/final/abstract/synchronized flag, and deprecation marker.

Sampling and partitioning tests should cover `SplitSampler`, `IntervalSampler`, and `RandomSampler` across empty inputs, many splits, `maxSplitsSampled`, sorted and skewed data, replacement behavior, comparator ordering, partition file write/read round trips, `TotalOrderPartitioner.getPartition`, and command-line `InputSampler.run` argument handling.

Mapred helper tests should cover inverse mapping, long summing, regex capture configuration, token counting, null output writer behavior, N-line split construction, multithreaded map runner concurrency/error propagation, multiple input path registration and mapper selection, key-field comparison/partition parsing, numeric/reverse sort options, and separator edge cases.

Multiple output tests should cover named output validation, rejection of `part`, single vs multi named outputs, configured output format/key/value class lookups, counters enabled/disabled and counter names, mapper-side output bypassing reducers, collector reuse, writer close, sequence/text base writers, filename/key/value override hooks, and invalid multi-name paths.

Aggregate tests should cover every aggregator with normal and malformed values, reset behavior, combiner output round trips, unique-count maximum behavior, histogram reports/details/items, descriptor-generated entries, user descriptor loading/configuration, mapper/combiner/reducer integration, and `ValueAggregatorJob` creation with explicit and default descriptors.

DB tests should use a test JDBC database to cover `configureDB`, both `DBInputFormat.setInput` overloads, count query generation/override, split start/end serialization, select query generation/override, `DBWritable` read/write field ordering, reader progress/position/close, output insert query construction with known and null field names, writer batching/close behavior, failed SQL handling, and value-ignored output semantics.

Pipes tests should cover executable get/set, Java component toggles, command-file retention configuration, `submitJob` mutation of `JobConf`, missing executable failures, `runJob`/`jobSubmit` return behavior, and command-line parsing.

Metrics tests should cover `ContextFactory` singleton and attribute lifecycle, reflective provider creation and null fallback, context start/stop/restart/close, updater registration and periodic calls, record tag/metric setter overloads, incremental vs absolute metrics, atomic updates from separate records, `remove` matching rules, file append/stdout output, Ganglia emission error handling, Log4J event counting, JVM updater initialization, SPI record creation, `MetricValue` flags, null contexts, output record views, server-spec parsing, MBean register/unregister names, and synchronized metric helper push/reset behavior.

Network tests should cover DNS lookups with controlled interfaces/nameservers, rack mapping cache hits/misses, script-based mapping configuration, socket factory property resolution and malformed properties, socket address parsing forms and default ports, static resolution add/get/list, wildcard listener connect addresses, timeout-capable input/output stream selection with and without socket channels, host normalization, topology add/remove/contains/getNode/counts/distance/rack checks, random scoped selection including `~` exclusion, available-node counts with exclusions, pseudo-sort by local node/rack/random fallback, `NodeBase` path normalization, and `SocketInputStream` timeout/read/close/isOpen behavior.
