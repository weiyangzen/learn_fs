# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 30898-37232

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop 0.19.0, not implementation source. It starts at the tail of `org.apache.hadoop.mapred.lib.InputSampler.SplitSampler`, covers a large slice of old `mapred` helper APIs, aggregate and DB input/output helpers, Pipes submission, the original Hadoop metrics framework, and most of `org.apache.hadoop.net` through the beginning of `SocksSocketFactory`.

Because the file is generated compatibility XML, the control-flow, state, and persistence notes below are inferred from public signatures, inheritance, checked exceptions, fields, and embedded API docs rather than method bodies.

## Purpose

The chunk records public and protected API contracts that Hadoop clients, MapReduce jobs, metrics sinks, and network-aware placement code depended on in the 0.19 line. It is useful for compatibility research because it captures method names, overloads, parameter and return types, checked exceptions, visibility, static/synchronized markers, fields, and deprecation status.

At a high level, this slice documents:

- Old `org.apache.hadoop.mapred.lib` convenience mappers, reducers, input splitting, partitioning, multiple inputs, and multiple outputs.
- The `org.apache.hadoop.mapred.lib.aggregate` framework, which lets users describe simple counting/statistics jobs through descriptors and built-in aggregators instead of writing custom mapper/reducer logic.
- JDBC-backed `DBInputFormat` and `DBOutputFormat` contracts.
- `org.apache.hadoop.mapred.pipes.Submitter`, the API and CLI entry point for Hadoop Pipes jobs.
- Hadoop's pre-metrics2 metrics interfaces, contexts, records, file/Ganglia/JVM implementations, SPI records, and simple mutable metric wrappers.
- Networking utilities for DNS, rack mapping, socket factory selection, network topology, rack-distance sorting, non-blocking socket streams with timeouts, and SOCKS socket construction.

## Important APIs and Types

### `org.apache.hadoop.mapred.lib`

The first visible method is `InputSampler.SplitSampler.getSample(InputFormat<K,V>, JobConf)`, which samples the first `numSamples / numSplits` records from selected splits. The class itself begins in the previous chunk, so final synthesis should join this with adjacent lines.

`InverseMapper` is a `MapReduceBase` mapper that swaps input key/value order and emits `(value, key)`. `LongSumReducer` reduces `Iterator<LongWritable>` values by summing them for each key. `RegexMapper` and `TokenCountMapper` expose simple text-mapping helpers for regular-expression extraction and token counting.

`KeyFieldBasedComparator` extends `WritableComparator` and implements `JobConfigurable`. It compares serialized keys using a Unix/GNU sort-like subset: numeric sort, reverse sort, and `-k f[.c][opts][,f[.c][opts]]` key ranges separated by `map.output.key.field.separator`. `KeyFieldBasedPartitioner` applies a parallel field-selection grammar for partitioning and exposes a protected byte-range `hashCode` helper.

`MultipleInputs.addInputPath(...)` records input `Path` entries with path-specific `InputFormat` and optional `Mapper` classes, letting one job consume heterogeneous inputs. `NLineInputFormat` splits input so N lines form one split, aimed at parameter-sweep jobs where each line controls one mapper.

`MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` extension that creates composite record writers and lets subclasses derive output file names, actual keys, and actual values from `(key, value, leafName)`. It supports reducer-driven key-based file routing, map-only input-file-derived output names, and combinations of input file plus key. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` supply concrete base writers for SequenceFile and text outputs.

`MultipleOutputs` is the richer named-output API. Static configuration methods define named outputs, multi-named outputs, output format/key/value classes, and optional counters. Runtime `getCollector(namedOutput, reporter)` and `getCollector(namedOutput, multiName, reporter)` return collectors for additional output files, and `close()` closes all opened named-output writers. Named output names must be word-like and cannot be reserved `part`; mapper-side named-output writes bypass the job's reduce phase.

`MultithreadedMapRunner` implements `MapRunnable` with a configurable thread pool (`mapred.map.multithreadedrunner.threads`, default 10). Its contract explicitly requires mapper implementations to be thread-safe.

`NullOutputFormat` discards output and has no output specs to validate. `TotalOrderPartitioner` partitions keys according to a partition file (`DEFAULT_PATH`, `setPartitionFile`, `getPartitionFile`) and is configured by `JobConf`.

### Aggregate Framework

The `org.apache.hadoop.mapred.lib.aggregate` package exposes a data-driven aggregation framework. The mapper emits keys whose prefix encodes an aggregation type; combiners and reducers instantiate the corresponding `ValueAggregator` and combine values.

Built-in aggregators include `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. The numeric/string aggregators expose `addNextValue`, `getReport`, type-specific getters such as `getSum()` or `getVal()`, `reset()`, and combiner-output lists. `UniqValueCount` tracks a bounded set of unique objects with configurable maximum item count. `ValueHistogram` consumes string/frequency pairs and reports unique count, min, median, max, average, standard deviation, details, and a `TreeMap` view.

`ValueAggregator` is the minimal aggregator protocol: add value, reset, produce a report, and produce combiner output. `ValueAggregatorDescriptor` generates aggregation-id/value pairs from input key/value objects and can be configured with `JobConf`; it defines `TYPE_SEPARATOR` and `ONE`.

`ValueAggregatorBaseDescriptor` provides standard aggregation type constants and helper factories such as `generateEntry` and `generateValueAggregator`. Its default descriptor generates record counts and per-input-file counts when file split information is available. `UserDefinedValueAggregatorDescriptor` dynamically instantiates a user descriptor by class name, delegates `generateKeyValPairs`, and supports `configure`.

`ValueAggregatorJobBase` stores the protected `aggregatorDescriptorList` and common mapper/reducer setup. `ValueAggregatorMapper` iterates descriptors to emit aggregation pairs. `ValueAggregatorCombiner` and `ValueAggregatorReducer` reduce `Text` keys and values based on the aggregation-type prefix; their opposite map/reduce methods are documented as no-ops that should not be called. `ValueAggregatorJob` creates `JobConf` or `JobControl` instances, wires descriptor classes, and has a `main` entry point for aggregate jobs.

### JDBC MapReduce Helpers

`DBConfiguration.configureDB` stores JDBC driver, URL, and optional credentials in a `JobConf`. Public property constants cover driver, URL, username, password, input table/fields/conditions/order/query/count query/input class, and output table/fields.

`DBInputFormat<T extends DBWritable>` configures database reads, creates `DBInputSplit` ranges, builds count queries, creates record readers, and has `setInput` overloads for table-based and query-based input. `DBInputSplit` implements split serialization through `readFields`/`write`, exposes `getStart`, `getEnd`, `getLength`, and returns no host locality. `DBRecordReader` constructs select queries, iterates rows into `LongWritable` keys and `DBWritable` values, reports position/progress, and closes database resources. `NullDBWritable` is a no-op placeholder.

`DBOutputFormat<K,V>` builds insert queries, validates output specs, creates `DBRecordWriter`, and has `setOutput`. `DBRecordWriter` writes `DBWritable` records through a JDBC `PreparedStatement` and closes its connection/statement. `DBWritable` defines the row-level `readFields(ResultSet)` and `write(PreparedStatement)` contract.

### Pipes Submitter

`org.apache.hadoop.mapred.pipes.Submitter` is both CLI and API for Hadoop Pipes. It extends/configures around `Configuration`, exposes setters/getters for the executable and whether record reader, mapper, reducer, and record writer are Java-side, controls whether to keep the generated command file, and exposes `submitJob`, `runJob`, `jobSubmit`, `run`, and `main`. It integrates with `RunningJob` and generic Hadoop command-line handling.

### Metrics Framework

`ContextFactory` is the singleton factory for `MetricsContext` instances. It loads attributes from `hadoop-metrics.properties`, supports attribute get/set/remove/list, creates named contexts by `<contextName>.class`, and defaults to `NullContext` when no implementation is configured.

`MetricsContext` is the main context interface: context name, start/stop/isMonitoring, close, create record, register/unregister updater, and `DEFAULT_PERIOD`. `MetricsRecord` models a record name plus tags and metrics; it supports typed `setTag`, `removeTag`, typed `setMetric`, typed `incrMetric`, `update`, and `remove`. Docs define buffered row semantics keyed by tag sets and warn that `update()` is atomic across instances with the same tags but a single `MetricsRecord` instance should not be shared concurrently. `Updater.doUpdates` is the periodic callback interface. `MetricsUtil` wraps common context creation and record creation tagged with host name. `MetricsException` is the unchecked metrics error type.

Concrete contexts include `metrics.file.FileContext`, which appends metrics to a configured file or stdout and flushes/closes it; `metrics.ganglia.GangliaContext`, which emits records to Ganglia; and `metrics.jvm.JvmMetrics`, a singleton `Updater` reporting JVM metrics. `metrics.jvm.EventCounter` is a Log4J appender that counts fatal/error/warn/info events.

The SPI layer centers on `AbstractMetricsContext`, `MetricsRecordImpl`, `MetricValue`, `OutputRecord`, `NullContext`, and `NullContextWithUpdateThread`. `AbstractMetricsContext` manages lifecycle, record creation, updater registration, periodic updates, record buffering, `emitRecord`, `flush`, and monitoring period. `MetricValue` distinguishes absolute from increment values. `OutputRecord` exposes metric and tag names/values for sink emission. Null contexts discard output; one variant still runs an update thread.

`metrics.util` includes `MBeanUtil` for JMX registration/unregistration and four mutable metric wrappers: `MetricsIntValue`, `MetricsLongValue`, `MetricsTimeVaryingInt`, and `MetricsTimeVaryingRate`. The simple int/long wrappers publish a changed value once on the next update. The time-varying wrappers publish per-interval deltas or average operation times and expose previous interval values; the rate metric tracks min/max and can reset them.

### Networking and Topology

`DNSToSwitchMapping.resolve(List<String>)` maps hostnames/IPs to rack/network paths with one-to-one output correspondence. `CachedDNSToSwitchMapping` wraps a raw mapping and caches resolved locations. `ScriptBasedMapping` extends that cache and implements `Configurable`, using `topology.script.file.name`.

`DNS` provides static direct and reverse lookup helpers for specific network interfaces and nameservers: reverse DNS, all IPs/default IP, all hosts/default host. `NetUtils` selects socket factories from Hadoop configuration, creates socket addresses from `host`, `host:port`, or URI-like strings, migrates old host/port config pairs to combined addresses, manages static hostname resolutions for tests, maps wildcard server bind addresses to client-connect addresses, wraps socket input/output streams with timeout-aware channel streams when available, and normalizes host names to textual IP addresses.

`NetworkTopology` models cluster topology as a tree of racks/switches/leaves. It can add/remove leaf nodes, test containment, look up nodes by path, report rack and leaf counts, compute distance through closest common ancestor, test same-rack placement, choose random nodes within or outside a scope, count available nodes excluding a list, stringify the tree, and `pseudoSortByDistance` so local node, local rack, or a random replica is preferred at the front of an array. Public constants include `DEFAULT_RACK`, `DEFAULT_HOST_LEVEL`, and `LOG`.

`Node` defines the topology-node contract: name, network location, parent, and level getters/setters. `NodeBase` implements it, normalizes path strings, builds a full path from a node, and stores protected mutable `name`, `location`, `level`, and `parent` fields.

`SocketInputStream` and `SocketOutputStream` adapt selectable socket channels to `InputStream`/`OutputStream` plus `ReadableByteChannel`/`WritableByteChannel` with read/write timeouts. Constructors configure the channel as non-blocking; docs warn that using the normal socket streams afterward can throw `IllegalBlockingModeException`. They expose `getChannel`, `isOpen`, synchronized `close`, `waitForReadable`/`waitForWritable`, and ByteBuffer-based channel methods. `SocketOutputStream.transferToFully(FileChannel, long, int)` loops until the requested byte count is transferred or throws EOF/timeout/IO errors.

`SocksSocketFactory` begins at the chunk boundary. Visible API includes constructors with default reflection-friendly initialization or an explicit `Proxy`, five `createSocket` overloads for unconnected, address, address+local bind, host, and host+local bind variants, and the beginning of `hashCode()`. The class continues in the next chunk.

## Control Flow and Behavioral Contracts

MapReduce helper control flow is mostly job-configuration driven. Static helpers such as `MultipleInputs`, `MultipleOutputs`, `DBInputFormat.setInput`, `DBOutputFormat.setOutput`, `TotalOrderPartitioner.setPartitionFile`, and aggregate job builders write contract information into `JobConf`; task-side objects then read it in `configure()` and execute through mapper/reducer/input/output interfaces.

Multiple-output writes flow from mapper/reducer code through a `MultipleOutputs` instance created in `configure()`, into named or multi-named `OutputCollector`s, then into output-format-specific record writers. The explicit `close()` contract is important because additional writers are opened lazily and are not the same as the job's default collector.

Aggregate jobs flow from descriptor-generated `(Text aggregationKey, Text value)` pairs to combiner/reducer grouping. The aggregation key prefix selects an aggregator implementation, values are added through `addNextValue`, and final output is produced through `getReport` or combiner output lists.

DB input flow is count query or split-range generation, split serialization, per-split SQL select construction, row iteration, and user `DBWritable.readFields(ResultSet)`. DB output flow is output configuration, SQL insert construction, per-record `DBWritable.write(PreparedStatement)`, and close/commit cleanup inferred from the writer API.

Metrics flow starts with `ContextFactory.getFactory()` loading attributes, `getContext()` constructing or reusing a context, `createRecord()` creating record buffers, application code setting tags/metrics and calling `update()`, and `AbstractMetricsContext` periodically invoking registered `Updater`s and sink-specific `emitRecord`/`flush`.

Networking flow uses configuration to choose socket factories and DNS/rack mapping implementations. Topology-aware code resolves names to rack paths, builds/updates a `NetworkTopology`, computes locality/distance, and reorders replica choices with `pseudoSortByDistance`.

Timeout stream flow depends on whether a socket has an associated channel. Channel sockets are switched to non-blocking mode and use select-style waits with timeouts; non-channel sockets fall back to JVM streams and normal socket timeout semantics.

## State and Persistence

Persistent or mutable state visible in this chunk includes:

- `JobConf` keys for multiple inputs/outputs, named-output counters, total-order partition files, aggregate descriptors, DB connection properties, DB input/output properties, Pipes executable and Java/native component choices, and N-line input settings.
- Runtime writer state in `MultipleOutputs`, which tracks opened named-output collectors until `close()`.
- Aggregator instance state: numeric sums/min/max, string min/max, unique-value sets, histogram maps, and descriptor lists.
- JDBC resources in DB record readers/writers: connections, statements, result sets, split ranges, current row position, and progress.
- Metrics factory attributes loaded from `hadoop-metrics.properties`; metrics context lifecycle state; buffered metric tables keyed by record name and tag set; update-thread state; file writer handles; Ganglia socket/output state; JVM/logging counters; and mutable metric wrapper values plus changed/previous-interval flags.
- DNS-to-switch cache entries, static hostname resolutions in `NetUtils`, network topology tree parent/level counters, rack/leaf counts, node path strings, and socket stream open/closed state.
- `NodeBase` stores mutable topology identity and hierarchy through protected fields, so topology operations can mutate parent and level during add/remove.

The XML itself persists no runtime state; it is the API compatibility artifact consumed by JDiff tooling.

## Dependencies and Integration Points

Major dependencies visible in this chunk:

- Old Hadoop `mapred` APIs: `JobConf`, `Mapper`, `Reducer`, `MapRunnable`, `RecordReader`, `OutputCollector`, `Reporter`, `InputFormat`, `OutputFormat`, `FileInputFormat`, `FileOutputFormat`, `SequenceFileOutputFormat`, `TextOutputFormat`, `RunningJob`, and `jobcontrol.JobControl`.
- Hadoop value and filesystem types: `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `LongWritable`, `Path`, `FileSystem`, `InputSplit`, and `Progressable`.
- Hadoop configuration and utility layers: `Configuration`, `Configured`, `GenericOptionsParser`, `Tool`-style command execution, and IPC `Server`/`VersionedProtocol` references.
- Java standard APIs: `Iterator`, `ArrayList`, `Map.Entry`, `TreeMap`, `Set`, JDBC `Connection`/`PreparedStatement`/`ResultSet`, Java IO streams/files/channels, sockets, proxies, `InetAddress`, `InetSocketAddress`, `UnknownHostException`, JNDI `NamingException`, and reflection exceptions.
- Logging and monitoring integrations: Apache Commons Logging, Log4J appenders/events, JMX `ObjectName`, file output, and Ganglia.
- Cluster placement integrations: rack scripts via `topology.script.file.name`, DNS/network-interface lookups, static host resolution for tests, and socket factory configuration keys such as class-specific and default Hadoop RPC socket factories.

## Risks and Edge Cases

- This chunk is API XML only, so exact locking, cleanup, SQL transaction behavior, cache eviction, exception wrapping, and thread lifecycle details are not visible.
- The chunk starts mid-`InputSampler.SplitSampler` and ends mid-`SocksSocketFactory`; final per-file reconciliation must merge those class summaries with adjacent chunks.
- `MultithreadedMapRunner` can corrupt results if mapper implementations, output collectors, or shared user state are not thread-safe.
- `MultipleOutputs` requires explicit `close()`; forgetting it risks missing or truncated side outputs.
- Named output names have validation constraints and reserve `part`; collisions with generated part names or multi-name suffixes are compatibility risks.
- Mapper-side named-output records do not enter the reduce phase, which can surprise jobs expecting all mapper emissions to be reduced.
- `KeyFieldBasedComparator` and `KeyFieldBasedPartitioner` depend on field separators and sort-key grammar; off-by-one field/character positions or numeric parsing failures can change partition/sort behavior.
- `TotalOrderPartitioner` depends on external partition-file distribution and consistency with key comparator behavior.
- Aggregate framework keys encode type and id in `Text`; malformed prefixes or unknown aggregation types can route data to the wrong aggregator or fail late in reduce.
- `UniqValueCount` can grow memory until its maximum item bound; incorrect bounds can trade accuracy for memory pressure.
- Histogram input expects `value\tcount`-style strings; malformed counts affect statistics.
- DB formats expose credentials in `JobConf` and rely on JDBC driver availability. Query construction, split boundaries, transaction/commit semantics, and SQL dialect differences are likely failure points.
- DB input splits report no locality, so large table reads depend on database throughput rather than data-local scheduling.
- Metrics records are buffered and periodically emitted; `update()` does not immediately publish externally. Long-lived rows continue to emit until `remove()` is called.
- Metrics docs allow concurrent `update()` from different record instances with the same tags but warn against sharing one record instance concurrently.
- File metrics append to configured files or stdout; file permissions, disk-full errors, and flush/close handling are operational risks.
- DNS and reverse-DNS behavior depends on network interfaces, nameserver availability, and local resolver configuration.
- `CachedDNSToSwitchMapping` may retain stale rack mappings if topology changes.
- `NetworkTopology` requires leaf/non-leaf invariants and normalized paths; invalid parents or levels can break distance and same-rack decisions.
- `pseudoSortByDistance` only partially sorts: it promotes local/local-rack/random first choices and intentionally leaves the rest untouched.
- Channel-backed `SocketInputStream`/`SocketOutputStream` switch sockets to non-blocking mode; code that later uses `Socket.getInputStream()` or `Socket.getOutputStream()` directly may fail.
- Timeout handling differs between channel and non-channel sockets because non-channel streams ignore the wrapper timeout argument and rely on socket SO_TIMEOUT or blocking writes.

## Test Signals

Useful tests inferred from this API slice include:

- Compatibility parsing tests that verify all classes, interfaces, constructors, methods, fields, visibility, static/synchronized/final flags, and checked exceptions in this chunk remain stable for JDiff consumers.
- `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper` functional tests for representative key/value inputs and IOException propagation.
- Key-field comparator and partitioner tests for `-k`, numeric, reverse, separator, missing-field, character-offset, and partition stability cases.
- `MultipleInputs` tests with two paths using distinct `InputFormat` and mapper classes.
- `MultipleOutputFormat` subclass tests for leaf-name, key/value rewrite, input-file-derived names, lazy writer creation, and close behavior.
- `MultipleOutputs` tests for single named outputs, multi named outputs, counter enablement, reserved/invalid names, mapper-side bypass of reduce, and required close.
- `MultithreadedMapRunner` tests with configurable thread counts, exception propagation from worker maps, reporter/output collector behavior, and non-thread-safe mapper documentation coverage.
- `NLineInputFormat` tests for default one-line splits, custom N lines per split, offsets as keys, empty files, and location hints spanning whole files.
- `TotalOrderPartitioner` tests for partition-file loading, boundary keys, and comparator compatibility.
- Aggregate tests for every built-in aggregator, combiner output round trips, unknown type handling, descriptor configuration, user-defined descriptor reflection, record-count and per-file-count generation, and histogram malformed input.
- DB format tests using an embedded JDBC database for table and query input modes, split boundaries, count query, row read/write through `DBWritable`, output query construction, credential configuration, and cleanup on failure.
- Pipes submitter tests for executable configuration, Java/native component flags, keep-command-file behavior, API submission, CLI parsing, and missing executable errors.
- Metrics tests for factory property loading, context class selection/default null context, updater registration/unregistration, start/stop/close idempotency, record tag/metric type handling, `update()`/`remove()` row semantics, file context output/flush, Ganglia emit stubbing, JVM metrics singleton behavior, and Log4J event counting.
- Metrics util wrapper tests for changed-only publishing, increment/decrement, time-varying interval reset, rate average/min/max, and JMX MBean register/unregister.
- DNS/NetUtils tests for interface lookups with mocks or controlled hosts, socket-address parsing, old/new config migration, static host resolution, wildcard bind address conversion, socket factory selection, and host normalization.
- Rack/topology tests for add/remove/contains, duplicate and invalid leaf handling, normalized paths, rack/leaf counts, distance and same-rack logic, scoped random choice including `~` exclusion scopes, available-node counts, and `pseudoSortByDistance` promotion rules.
- Socket stream tests using channel-backed sockets for read/write timeouts, ByteBuffer reads/writes, synchronized close, `transferToFully` EOF/timeout paths, and direct socket stream incompatibility after non-blocking configuration.
- `SocksSocketFactory` tests should be completed with the next chunk, because this chunk only contains the class beginning.

## Chunk Boundary Notes

The preceding chunk is required for the beginning of `InputSampler.SplitSampler` and earlier `mapred.lib` APIs. The following chunk is required for the rest of `SocksSocketFactory` and subsequent APIs. The final merged source research should preserve that this chunk is a generated API-compatibility view and should not overstate implementation details that are not present in the XML.
