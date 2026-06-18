# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 31139-37383

## Scope

This chunk is a JDiff API snapshot for Apache Hadoop 0.17.0. It starts at the tail of `org.apache.hadoop.mapred.join.WrappedRecordReader`, includes package documentation for the join framework, then covers `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, `org.apache.hadoop.mapred.pipes`, the old Hadoop metrics API and SPI packages, network utilities in `org.apache.hadoop.net`, and the beginning of the record I/O package `org.apache.hadoop.record`. It ends inside `CsvRecordOutput`, after the `writeDouble(double, String)` signature.

The source is generated compatibility metadata, not implementation source. The research surface is therefore the externally visible contract: packages, classes, interfaces, inheritance, implemented interfaces, fields, constructors, method signatures, exceptions, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadocs.

## Purpose

The join tail documents `WrappedRecordReader` as the proxy that keeps the current head key/value and buffered matching values for a sorted-data join. The package documentation explains the pre-map join framework, its `mapred.join.expr` grammar, default identifiers (`inner`, `outer`, `override`), optional key comparator, and custom join-operation extension points.

The `org.apache.hadoop.mapred.lib` portion exposes common old-MapReduce building blocks: identity and inverse mappers, identity and summing reducers, hash and key-field partitioners, regex and token-count mappers, multithreaded map execution, null output, field selection, and multiple-output formats for splitting job output by key/value or source input file.

The `org.apache.hadoop.mapred.lib.aggregate` portion documents Hadoop's Aggregate framework. It turns mapper output into typed aggregation-id/value pairs, combines and reduces them with built-in aggregators, and allows user-defined descriptors to generate aggregation keys. Built-ins include numeric sums, long min/max, string min/max, unique value counting, and histograms.

The `org.apache.hadoop.mapred.pipes` portion exposes the Java submitter for Hadoop Pipes, allowing C++ components to participate in map/reduce jobs. It controls the executable URI, Java-versus-native reader/mapper/reducer/writer flags, debug command-file retention, and job submission.

The metrics packages document Hadoop's original metrics API. `ContextFactory`, `MetricsContext`, `MetricsRecord`, `Updater`, and `MetricsUtil` define the public metrics reporting model; `file`, `ganglia`, `jvm`, `spi`, and `util` packages provide file/Ganglia emitters, JVM/log4j counters, provider-side buffering, MBean registration, and convenience metric value objects.

The `org.apache.hadoop.net` portion documents network identity, socket, rack-topology, and socket-factory APIs. It includes DNS helpers, pluggable DNS-to-rack mapping, socket factory lookup from configuration, static hostname resolution for tests, timeout-capable NIO socket streams, network topology selection, and node path modeling.

The `org.apache.hadoop.record` portion starts Hadoop record I/O. It exposes binary and CSV record input/output adapters and the mutable `Buffer` byte sequence used as a record-native type.

## Important APIs, Types, and Functions

### Join Tail

- `WrappedRecordReader.compareTo(ComposableRecordReader<K, ?>)` compares current head keys, and `equals(Object)` follows the comparison contract. `close()` forwards to the proxied reader. This class is the visible per-source reader proxy used by composable join readers.
- Join package documentation defines the expression grammar `func ::= ident(func,...)` and `tbl(class,"path")`, required `mapred.join.expr`, optional `mapred.join.keycomparator`, and custom `mapred.join.define.<ident>` mapping.

### Mapred Library

- `FieldSelectionMapReduce` implements both `Mapper<K,V,Text,Text>` and `Reducer<Text,Text,Text,Text>`. It parses field lists from `map.output.key.value.fields.spec` and `reduce.output.key.value.fields.spec`, uses `mapred.data.field.separator`, ignores the map key for `TextInputFormat`, and emits selected fields as output keys and values.
- `HashPartitioner<K2,V2>` partitions by `Object.hashCode()`. `KeyFieldBasedPartitioner<K2,V2>` has the same public partitioner shape in this snapshot, with configuration plus `getPartition`.
- `IdentityMapper`, `IdentityReducer`, and `InverseMapper` provide direct pass-through map, pass-through reduce, and key/value swap map behavior over old `mapred` APIs.
- `LongSumReducer<K>` sums `LongWritable` values for each key.
- `MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` that returns a composite `RecordWriter`. Protected hooks include `generateLeafFileName`, `generateFileNameForKeyValue`, `generateActualKey`, `generateActualValue`, `getInputFileBasedOutputFileName`, and abstract `getBaseRecordWriter`.
- `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` implement base writer construction for sequence-file and text output.
- `MultithreadedMapRunner` implements `MapRunnable<K1,V1,K2,V2>` with `configure` and `run`, intended for maps whose bottleneck is not CPU.
- `NullOutputFormat` consumes output while still satisfying `OutputFormat` with `getRecordWriter` and `checkOutputSpecs`.
- `RegexMapper` extracts text matching a configured regular expression; `TokenCountMapper` emits token/frequency pairs using tokenization.

### Aggregate Framework

- `ValueAggregator` defines the aggregator lifecycle: `addNextValue(Object)`, `reset()`, `getReport()`, and `getCombinerOutput()`.
- `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram` implement `ValueAggregator`. Numeric aggregators accept object/string forms plus primitive overloads where present. Combiner output is a compact representation that downstream reducers can aggregate again.
- `UniqValueCount` supports `setMaxItems(long)`, exposes `getUniqueItems()`, and returns unique items for combiner use. Its max-item limit is an important memory-control contract.
- `ValueHistogram` accepts values in a value/count form, reports unique count, min, median, max, average, and standard deviation, and can expose details or a `TreeMap`.
- `ValueAggregatorDescriptor` creates aggregation-id/value pairs from input key/value pairs and can be configured with `JobConf`. Its fields include `TYPE_SEPARATOR` and `ONE`.
- `ValueAggregatorBaseDescriptor` supplies built-in aggregation type constants, default record counting, `generateEntry(type,id,val)`, `generateValueAggregator(type)`, and input-file-aware configuration.
- `UserDefinedValueAggregatorDescriptor` dynamically instantiates a user descriptor by class name and delegates `generateKeyValPairs`.
- `ValueAggregatorJobBase` holds the protected `aggregatorDescriptorList` used by mapper, combiner, and reducer classes.
- `ValueAggregatorMapper` iterates descriptors and emits aggregation pairs. `ValueAggregatorCombiner` combines values for a typed aggregation key. `ValueAggregatorReducer` creates the correct aggregator from the key prefix and emits final reports.
- `ValueAggregatorJob` creates `JobConf` or `JobControl` instances and has a `main` entry point for aggregate jobs, including descriptor class setup.

### Pipes

- `Submitter` exposes static `getExecutable`/`setExecutable` for the application executable URI, boolean toggles for Java record reader, mapper, reducer, and writer use, `getKeepCommandFile`/`setKeepCommandFile`, `submitJob(JobConf)`, and `main(String[])`.
- Pipes package documentation defines the CLI options and integration model: a separate C++ process communicates with Java map/reduce components over sockets using Writable serialization, with optional C++ combiners and partition functions.

### Metrics

- `ContextFactory` is a singleton-style factory with attributes loaded from `hadoop-metrics.properties`. It supports attribute get/list/set/remove, synchronized context construction by name, and null-context creation.
- `MetricsContext` defines monitoring lifecycle, record creation, updater registration, and `DEFAULT_PERIOD`.
- `MetricsRecord` defines tags and metrics with `String`, `int`, `short`, `byte`, and `float` overloads, plus `update()` and `remove()` for buffered metric table rows.
- `MetricsUtil` wraps context and record creation and tags records with host identity. `Updater.doUpdates(MetricsContext)` is the periodic callback contract.
- `FileContext` emits metrics to a configured file or standard output, with `fileName` and `period` attributes. `GangliaContext` emits records to Ganglia using server and per-metric metadata attributes.
- `EventCounter` is a log4j appender counting fatal, error, warn, and info events. `JvmMetrics` is a singleton `Updater` for JVM metrics.
- `AbstractMetricsContext` implements context lifecycle, timer period, updater registration, record buffering, update/remove row semantics, `flush`, and abstract `emitRecord`.
- `MetricsRecordImpl` stores record state and delegates update/remove back to its `AbstractMetricsContext`. `MetricValue` distinguishes absolute and incremental numbers.
- `NullContext` discards all metrics. `NullContextWithUpdateThread` keeps callbacks active without emitting records, useful when another system such as JMX reads sampled values.
- `OutputRecord` provides read-only access to emitted tags and metrics. `metrics.spi.Util.parse` parses comma/space separated host and optional port specifications.
- `MBeanUtil` registers and unregisters MBeans using Hadoop's standard `hadoop.dfs:service=...,name=...` naming pattern.
- `MetricsIntValue`, `MetricsTimeVaryingInt`, and `MetricsTimeVaryingRate` are synchronized helper objects that push changed, interval-delta, and rate/min/max metrics to a `MetricsRecord`.

### Network

- `DNS` provides reverse lookup against a specified nameserver, IP enumeration for an interface, default IP selection, host lookup with default or explicit nameserver, and default host lookup.
- `DNSToSwitchMapping.resolve(List<String>)` maps host names or IP addresses to rack-like network paths while preserving input/output order. `ScriptBasedMapping` implements it through a configured `topology.script.file.name`.
- `NetUtils` selects socket factories from configuration keys, creates socket addresses from `host:port` or URI-like forms, migrates old host/port config pairs to combined addresses, tracks static hostname resolutions, converts wildcard server bind addresses to connectable addresses, and returns timeout-aware socket streams.
- `NetworkTopology` models a hierarchical cluster tree. It can add/remove/lookup nodes, count racks and leaves, compute distance, test same-rack membership, choose random nodes within or outside a scope, count available nodes excluding a list, and pseudo-sort replica arrays by distance to a reader.
- `Node` and `NodeBase` define and implement network location, node name, parent, level, path normalization, path construction, and constants for path separators and root.
- `SocketInputStream` and `SocketOutputStream` wrap selectable channels with read/write timeouts, expose the underlying channel for zero-copy transfer, implement `ReadableByteChannel`/`WritableByteChannel`, and synchronize close.
- `SocksSocketFactory` is configurable and creates sockets through a SOCKS proxy. `StandardSocketFactory` creates normal sockets while matching the socket-factory API.

### Record I/O

- `BinaryRecordInput` and `BinaryRecordOutput` implement `RecordInput` and `RecordOutput` for `DataInput`/`DataOutput` or streams. Static `get(...)` methods return thread-local adapters for supplied data streams.
- `CsvRecordInput` and the visible part of `CsvRecordOutput` implement the same record input/output primitive methods for CSV streams.
- `Buffer` is a mutable, resizable byte sequence implementing `Comparable` and `Cloneable`. It exposes backing-array assignment, copying, append, count/capacity management, truncation, reset, lexicographic comparison, equality, hash code, string conversion with optional charset, and cloning.

## Control Flow

The XML does not contain executable method bodies, but the documented APIs imply several core paths.

In old MapReduce library jobs, `configure(JobConf)` initializes helpers, map methods consume key/value pairs through `OutputCollector` and `Reporter`, reduce methods iterate all values for a key, and output formats return record writers that translate collected key/value pairs into target files. `MultipleOutputFormat` inserts an extra dispatch layer: the composite writer derives a leaf name, output path, actual key, and actual value before delegating to a base writer.

Field-selection flow treats input as separator-delimited fields. The mapper builds fields from value only for text input, or from key plus value for other formats, then applies configured key/value field specs. The reducer repeats the same extraction style with the reduce key always included.

Aggregate flow is data driven. A mapper calls each configured `ValueAggregatorDescriptor.generateKeyValPairs`, emits keys with an aggregation-type prefix, then the combiner or reducer parses the prefix, constructs the matching `ValueAggregator`, calls `addNextValue` over all values, and emits either `getCombinerOutput` or `getReport`. Associativity and commutativity are required when combiners are used.

Pipes submission flow mutates a `JobConf` with the executable and Java/native component flags before submitting a job. At task runtime, Java map/reduce components communicate with an external C++ process over sockets using Writable serialization.

Metrics flow starts with `ContextFactory.getFactory()`, optional attribute inspection or mutation, `getContext(name)`, and `createRecord(recordName)`. Callers set tags and metrics on a `MetricsRecord`, call `update()` or `remove()`, and the context buffers rows until its monitoring timer invokes updaters and emits output records. Concrete contexts provide `emitRecord`; file and Ganglia contexts write to their respective sinks, while null contexts intentionally discard output.

Network flow includes configuration-driven socket factory selection, socket address creation, optional static hostname overrides, and stream wrapping through `NetUtils.getInputStream`/`getOutputStream`. If a socket has a channel, the returned stream uses non-blocking mode plus timeout handling; after that, direct use of `Socket.getInputStream()` or `getOutputStream()` can fail because the channel has been switched to non-blocking mode.

Topology flow maps hosts to rack paths, normalizes paths through `NodeBase`, adds leaf nodes into `NetworkTopology`, and uses distance/scope calculations for rack-aware placement. `pseudoSortByDistance` only moves local and same-rack candidates to the front and leaves the rest of the array largely untouched.

Record I/O flow follows `RecordInput`/`RecordOutput` callbacks: start/end record, vector, and map, with primitive reads and writes in between. Binary adapters work over `DataInput`/`DataOutput`; CSV adapters use streams. `Buffer` supports efficient in-memory mutation before serialization.

## State and Persistence Behavior

This JDiff file persists the Hadoop 0.17.0 public API for compatibility comparison. It does not store runtime data, but it documents classes whose runtime state is significant.

MapReduce helpers are mostly stateless per call, except for configuration-derived state such as field specs, regex patterns, aggregate descriptor lists, multithreaded runner settings, and multiple-output writer caches. Output formats and writers persist data to Hadoop filesystems; `NullOutputFormat` intentionally discards it.

Aggregate state lives inside `ValueAggregator` instances during each key group: sums, extrema, unique sets, histograms, and combiner output buffers. `UniqValueCount` and `ValueHistogram` can retain large in-memory sets/maps, making their state proportional to input cardinality. Descriptor configuration can persist an input file name and user class names in `JobConf`.

Pipes state is encoded in `JobConf`, including executable URI and Java/native component flags. The keep-command-file flag persists debug command data as `downlink.data` in task directories when enabled.

Metrics state is buffered in `AbstractMetricsContext` until periodic emission. `ContextFactory` has process-global attributes and context instances; `hadoop-metrics.properties` provides classpath-loaded configuration. `MetricsIntValue` tracks whether a set value has already been pushed, while time-varying helpers retain current and previous interval values. `FileContext` persists metrics by appending to a file when configured; `GangliaContext` sends UDP/network metrics; `NullContext` discards all metric records.

Network state includes process-local static hostname resolutions in `NetUtils`, configuration-backed socket factory selections, rack topology trees in `NetworkTopology`, parent/level/location fields in `NodeBase`, and proxy configuration in `SocksSocketFactory`. Socket streams mutate channel blocking mode and hold timeout settings until closed.

Record I/O state includes thread-local binary input/output adapters, current stream positions in underlying `DataInput`/`DataOutput`, and mutable byte arrays in `Buffer`. `Buffer.set(byte[])` uses the supplied array as backing storage, while `copy(byte[], int, int)` creates its own backing storage. Count and capacity are distinct, so callers must respect `getCount()`.

## Dependencies and Integration Points

This chunk depends on the old `org.apache.hadoop.mapred` API: `Mapper`, `Reducer`, `MapRunnable`, `MapReduceBase`, `OutputCollector`, `Reporter`, `JobConf`, `FileOutputFormat`, `RecordWriter`, `OutputFormat`, `RunningJob`, and `jobcontrol.JobControl`.

Filesystem and serialization dependencies include `FileSystem`, `Progressable`, `Writable`, `WritableComparable`, `LongWritable`, `Text`, `SequenceFileOutputFormat`, `TextOutputFormat`, Java `InputStream`/`OutputStream`, `DataInput`/`DataOutput`, byte arrays, `ArrayList`, `TreeMap`, and iterators.

Configuration integration is central. Aggregate descriptors, Pipes submitter settings, socket factory classes, topology script mapping, metrics context classes, metrics periods, file output paths, Ganglia servers, and proxy sockets are all selected or shaped by `JobConf`, `Configuration`, or metrics factory attributes.

Metrics integrations include log4j (`AppenderSkeleton`, `LoggingEvent`) for `EventCounter`, JMX (`ObjectName`) for `MBeanUtil`, Ganglia wire emission, file/stdout emission, and periodic callbacks through `Updater`.

Network integrations include Java DNS/JNDI (`NamingException`), `InetAddress`, `InetSocketAddress`, `Socket`, `SocketFactory`, `Proxy`, NIO selectable channels, byte buffers, Hadoop IPC `Server`, and Hadoop `VersionedProtocol`-oriented socket factory lookup.

Record integrations include `RecordInput`, `RecordOutput`, `Record`, `Index`, and the generated-record runtime conventions used by Hadoop's old record compiler.

## Risks and Edge Cases

- This chunk starts and ends mid-class. Full research for `WrappedRecordReader` and `CsvRecordOutput` requires adjacent chunks.
- JDiff metadata omits method bodies, so exact parsing, validation, synchronization internals, and serialization byte formats require implementation-source review.
- `HashPartitioner` and `KeyFieldBasedPartitioner` depend on hash stability and positive modulo behavior. Negative hash values and zero reducers are important failure edges.
- Field-selection specs include specific fields, ranges, and open ranges, but open ranges only apply to value fields. Off-by-one field indexing and separator escaping can break output compatibility.
- `MultipleOutputFormat` can create many writers if filenames are key-dependent. Writer lifecycle, path sanitization, and close-on-failure behavior are high-risk.
- Multithreaded map execution can expose mapper implementations that are not thread safe. Shared collector/reporter use and exception propagation need explicit tests.
- Aggregate keys encode type and id in a single `Text` key. Missing separators, unknown type names, descriptor bugs, or ids containing the separator can misroute values.
- Combiner correctness depends on associative and commutative aggregators. Unique counts and histograms can consume unbounded memory without configured limits.
- Dynamic descriptor loading in `UserDefinedValueAggregatorDescriptor` can fail due to classpath, constructor, type, or access problems.
- Pipes jobs mix Java and native code over sockets. Writable serialization mismatches, executable URI errors, command-file leakage, and C++ combiner ordering by `memcmp` instead of Java comparators are compatibility risks.
- Metrics API defaults differ between docs in this span: `ContextFactory.getContext` says missing context classes create `NullContext`, while package docs describe `FileContext` as default. This mismatch should be reconciled against implementation and tests.
- Metrics records are buffered, so callers expecting immediate emission after `update()` can observe delayed output. Tags define row identity, and `remove()` semantics can remove broad sets when few tags are set.
- `ContextFactory` and `AbstractMetricsContext` have synchronized lifecycle methods but can interact with updater callbacks and emitters; deadlocks or missed updates are possible if emitters call back into context state.
- File metrics append to local paths and flush periodically. File permission, disk full, restart, and stop/close behavior need coverage.
- Ganglia emission depends on server parsing and UDP/network availability; malformed per-metric attributes can silently weaken reporting.
- `EventCounter` is static-counter-like API surface; tests must verify level mapping and reset behavior if any exists outside this chunk.
- DNS APIs depend on host network interfaces and external nameservers. Tests should isolate default interface, missing interface, reverse lookup failure, and default nameserver behavior.
- `NetUtils.createSocketAddr` accepts both `host:port` and URI-like forms; malformed ports, IPv6 literals, missing ports, and wildcard bind addresses are sensitive cases.
- Static host resolution is process-global and test-oriented. Tests must clean up or isolate it to avoid cross-test contamination.
- `SocketInputStream` and `SocketOutputStream` require selectable channels and non-negative timeouts. They mutate channel blocking mode, so mixed direct socket stream use can throw `IllegalBlockingModeException`.
- `NetworkTopology.add` requires leaf nodes and rejects adding under leaves. Distance and same-rack calculations must handle null nodes and nodes outside the topology.
- Scope strings beginning with `~` invert selection in topology APIs. Empty scopes, unresolved/default racks, and excluded-node overlap are high-risk placement paths.
- `NodeBase.normalize` and path construction must preserve root and separator behavior. Bad normalization breaks rack identity and topology lookup.
- `ScriptBasedMapping` relies on an external script. Missing script, timeout, partial output, and output order mismatch can cause wrong rack assignments.
- `SocksSocketFactory.equals`/`hashCode` must reflect proxy configuration; otherwise RPC connection caching can reuse the wrong socket factory.
- `StandardSocketFactory` documentation says SOCKS proxy even though the class is standard. This apparent Javadoc copy/paste error is a documentation compatibility signal.
- Binary record input/output thread-local adapters must be safe when reused with different `DataInput`/`DataOutput` instances on the same thread.
- `Buffer.get()` exposes backing storage; callers must not read past `getCount()` or mutate unexpectedly. `set(byte[])` aliases caller storage while `copy` does not.
- `Buffer.setCapacity` shrinking below count, append growth, lexicographic comparison of signed bytes, charset conversion, and clone independence need focused coverage.
- CSV record output is incomplete in this chunk, so final API review must merge continuation lines before claiming complete CSV output behavior.

## Test Signals

Useful validation for this API surface should include:

- API compatibility checks that confirm every public/protected package, class, interface, field, constructor, method, exception, visibility flag, synchronized/static/final/abstract marker, and deprecation marker in lines 31139-37383.
- Join framework tests for sorted input joins, `WrappedRecordReader` head-key comparison, equality/hash behavior, close forwarding, configured key comparator, nested join expressions, and custom `mapred.join.define.<ident>` operations.
- `FieldSelectionMapReduce` tests for text versus non-text input field construction, custom separators, simple/range/open-range specs, map and reduce specs, empty fields, invalid specs, and field ordering.
- Mapper/reducer/partitioner tests for identity, inverse, long sum, regex extraction, token counting, hash partitioning with negative hashes, and key-field partitioning configuration.
- `MultipleOutputFormat` tests for generated leaf names, key/value-derived filenames, input-file-derived filenames, actual key/value rewrites, multiple writer creation, close propagation, and sequence/text concrete formats.
- `MultithreadedMapRunner` tests with thread-safe and non-thread-safe mappers, exception propagation, reporter progress, and configurable thread count.
- `NullOutputFormat` tests that output is accepted and no files are written.
- Aggregate framework tests for every built-in aggregator, object and primitive add paths, reset, report formatting, combiner output round trips, unique-count limits, histogram detail output, unknown aggregation type, and key ids containing separators.
- Aggregate job tests for descriptor configuration, user descriptor dynamic loading failures, mapper descriptor iteration, combiner/reducer type parsing, default record counting, input-file counting, and `ValueAggregatorJob` argument parsing.
- Pipes submitter tests for all Java/native component flags, executable URI configuration, keep-command-file behavior, `submitJob` JobConf mutations, CLI parsing, and mixed Java/C++ component combinations.
- Metrics factory tests for `hadoop-metrics.properties` loading, attribute mutation/removal, context class selection, null-context fallback, and singleton behavior.
- Metrics record tests for all tag and metric overloads, absolute versus incremental values, `update()` row merge, `remove()` row matching, callback registration/removal, timer period changes, close/stop/start lifecycle, and exception handling.
- File and Ganglia context tests for configured periods, file append/stdout output, flush, stop/close, server-list parsing, malformed server specs, and per-metric metadata attributes.
- JVM metrics and log event counter tests for singleton initialization, periodic update output, and log level counters.
- Metrics utility tests for MBean name construction/unregistration and synchronized helper metrics pushing exactly once or per interval as documented.
- DNS and network utility tests for interface lookup, explicit/default nameserver behavior, static resolution add/get/list, socket address parsing, legacy host/port config migration, wildcard listener connect address, socket factory lookup and fallback, malformed factory properties, and SOCKS proxy configuration.
- Socket stream tests for read/write timeout, zero timeout, negative timeout rejection, close synchronization, channel exposure, NIO `ByteBuffer` read/write, and illegal blocking mode behavior after wrapping.
- Network topology tests for add/remove/contains/getNode, rack and leaf counts, distance, same-rack checks, random selection in normal and inverted scopes, excluded-node counts, unresolved/default rack paths, and pseudo distance sorting.
- `NodeBase` tests for constructors, `normalize`, `getPath`, parent/level setters, root path handling, path separator constants, and string rendering.
- `ScriptBasedMapping` tests with successful script output, missing script, wrong output count, null/empty name lists, and configuration replacement.
- Record I/O tests for binary primitive read/write round trips, record/vector/map boundaries, thread-local adapter reuse, CSV primitive parsing/writing, invalid input, and `IOException` propagation.
- `Buffer` tests for aliasing versus copying, count/capacity behavior, append growth, truncate/reset, lexicographic compare, equality/hash, string conversion with unsupported charset, clone independence, and reading only valid bytes between zero and `getCount() - 1`.
