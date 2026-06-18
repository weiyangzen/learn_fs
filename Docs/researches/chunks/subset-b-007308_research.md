# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 30924-37251

## Scope

This chunk is a Hadoop 0.19.2 JDiff API XML segment, not implementation source. It begins near the end of `org.apache.hadoop.mapred.lib.InputSampler`, covers the rest of the old `mapred.lib` helpers, aggregate and DB MapReduce adapters, Pipes job submission, the Hadoop metrics API/SPI and utility metrics classes, and the network utility package through the complete `SocketInputStream` declaration. The chunk ends at the opening of `org.apache.hadoop.net.SocketOutputStream`, whose members are outside this assigned range.

Because the source is generated API metadata, this research describes exported contracts, signatures, inheritance, deprecation markers, documented behavior, checked exceptions, and fields. Control flow, state, persistence, and risks are inferred from the public API and Javadocs visible in this XML rather than from method bodies.

## Purpose

The covered APIs expose a compatibility slice for Hadoop 0.19.2's classic `mapred` support libraries and common runtime services. The MapReduce section gives users reusable mappers, reducers, partitioners, multi-input/multi-output plumbing, total-order sampling, generic aggregation, JDBC input/output formats, and C++ Pipes submission controls. The metrics section defines how Hadoop components create metric contexts, create/update tagged metric records, register periodic updaters, send metrics to file or Ganglia sinks, count JVM/logging events, and implement provider-specific metrics backends. The network section defines DNS/rack mapping, socket factory selection, static host resolution for tests, network topology modeling, and channel-backed socket input with explicit read timeouts.

For compatibility work, the chunk is valuable because it captures old public names, overloads, configuration entry points, protected extension hooks, nested classes, and deprecated APIs that downstream code may still reference.

## Important APIs, Types, and Functions

### `org.apache.hadoop.mapred.lib`

`InputSampler` is partially visible at the start of the chunk. The visible tail includes command-line `run(String[])` and `main(String[])`, and documents that it configures a `JobConf` and writes a partition file for `TotalOrderPartitioner`.

`InputSampler.Sampler<K,V>` is the common interface for collecting representative input keys through an `InputFormat<K,V>` and `JobConf`. Implementations include:

- `IntervalSampler`, which samples records at regular intervals from all or a bounded number of splits. Its `getSample` emits keys when retained-record ratio is below the configured frequency, making it useful for already sorted data.
- `RandomSampler`, which randomizes split order, samples keys with a configured probability, caps total samples, and may replace earlier selected keys after a per-split quota is reached. Its docs warn that sampling all splits can be expensive because it reads them on the client.
- `SplitSampler`, which takes the first `numSamples / numSplits` records from each selected split, trading quality for low cost on random-looking inputs.

`InverseMapper<K,V>` extends `MapReduceBase` and implements `Mapper<K,V,V,K>`. Its `map` method swaps input key and value before collecting.

`KeyFieldBasedComparator` extends `WritableComparator` and implements `JobConfigurable`. It exposes `configure(JobConf)` and raw byte `compare(byte[], int, int, byte[], int, int)`. Its documented sort syntax is a Hadoop subset of Unix/GNU sort: numeric `-n`, reverse `-r`, and `-k pos1[,pos2]` field/character selection using `map.output.key.field.separator`.

`KeyFieldBasedPartitioner<K2,V2>` implements `Partitioner<K2,V2>`, with `configure(JobConf)`, `getPartition(K2,V2,int)`, and a protected byte-range `hashCode`. It partitions by the same field-position grammar documented for the comparator.

`LongSumReducer<K>` sums `LongWritable` values for a key.

`MultipleInputs` is a static configuration helper for jobs with different input paths using different `InputFormat` classes and optionally different `Mapper` classes. It writes the per-path input-format and mapper mapping into `JobConf`.

`MultipleOutputFormat<K,V>` is an abstract `FileOutputFormat` for deriving output file names and actual key/value pairs per record. Public `getRecordWriter` creates a composite writer. Protected hooks include `generateLeafFileName`, `generateFileNameForKeyValue`, `generateActualKey`, `generateActualValue`, `getInputFileBasedOutputFileName`, and abstract `getBaseRecordWriter`. The docs call out three use cases: reducers writing different files by key/value, map-only output names derived from input file paths, and map-only names based on both input files and keys.

`MultipleOutputs` is a runtime/configuration helper for named outputs. Static APIs define named outputs, multi-named outputs, key/value/output format classes, counter enablement, and listing of configured names. Instance APIs create `OutputCollector`s for a single named output or a multi-named output and close all opened writers. Named-output writes from a mapper bypass the reduce phase; only records collected to the mapper's normal output collector continue to reducers. Counters are optional and grouped under the `MultipleOutputs` class name.

`MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` specialize `MultipleOutputFormat` by implementing `getBaseRecordWriter` with SequenceFile and text output semantics.

`MultithreadedMapRunner<K1,V1,K2,V2>` implements `MapRunnable`, with `configure(JobConf)` and `run(RecordReader, OutputCollector, Reporter)`. It uses a configurable thread pool (`mapred.map.multithreadedrunner.threads`, default 10) and requires mapper implementations to be thread-safe.

`NLineInputFormat` extends `FileInputFormat<LongWritable,Text>` and implements `JobConfigurable`. `getSplits` groups N input lines per split, `getRecordReader` reads those splits, and `configure` pulls split sizing from `JobConf`. Its documented use case is parameter-sweep jobs where each mapper receives one or more control-file lines.

`NullOutputFormat<K,V>` implements `OutputFormat` and discards all output through a no-op `RecordWriter`.

`RegexMapper<K>` emits `Text,LongWritable` counts for regex matches in `Text` values, configured from `JobConf`. `TokenCountMapper<K>` tokenizes `Text` values with `StringTokenizer` and emits token frequency pairs.

`TotalOrderPartitioner<K,V>` implements `Partitioner` and reads an externally generated sorted partition key SequenceFile. `configure(JobConf)` builds either a trie for natural-order `BinaryComparable` keys or a binary-search keyset using the job's `RawComparator`. Static `setPartitionFile(JobConf, Path)` and `getPartitionFile(JobConf)` configure the split-point file. `DEFAULT_PATH` is the public default partition-file path.

### `org.apache.hadoop.mapred.lib.aggregate`

The aggregate package defines old generic aggregation jobs. `ValueAggregator` is the minimal protocol: `addNextValue(Object)`, `reset()`, `getReport()`, and `getCombinerOutput()`.

Concrete aggregators include `DoubleValueSum`, `LongValueMax`, `LongValueMin`, `LongValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. Numeric aggregators parse object string representations and expose typed getters such as `getSum()` or `getVal()`. String max/min track lexical extrema. `UniqValueCount` keeps a bounded set of unique objects with `setMaxItems(long)` and `getUniqueItems()`. `ValueHistogram` accepts values in `value\tcount` form, emits summary statistics and detailed frequency pairs, and exposes a `TreeMap` view.

`ValueAggregatorDescriptor` generates aggregation id/value entries from input key/value pairs and is `JobConfigurable`. `ValueAggregatorBaseDescriptor` supplies static helpers such as `generateEntry` and `generateValueAggregator`, descriptor list management, default user descriptor discovery, and default `generateKeyValPairs`.

`UserDefinedValueAggregatorDescriptor` wraps a dynamically loaded descriptor class name, creates an instance, delegates `generateKeyValPairs`, and implements `configure(JobConf)` as a no-op wrapper-level operation.

`ValueAggregatorJobBase<K1,V1>` is the common mapper/reducer base that configures the descriptor list. `ValueAggregatorMapper` emits aggregation id/value pairs generated by descriptors and has a no-op reducer. `ValueAggregatorReducer` consumes `Text` keys whose prefixes encode aggregation type, aggregates `Text` values using the selected `ValueAggregator`, and has a no-op mapper.

`ValueAggregatorCombiner` performs combiner-side aggregation with `Text` keys and `Text` values. `ValueAggregatorJob` configures and runs aggregate jobs, including static `createValueAggregatorJob` overloads and `main`. `ValueAggregatorJobBase` and job helpers are integration points between user descriptors, `JobConf`, `Mapper`, `Reducer`, and aggregate output.

### `org.apache.hadoop.mapred.lib.db`

`DBConfiguration` is a container for public configuration property names and static `configureDB` overloads. It stores JDBC driver, URL, optional username/password, input table/query/count-query/class fields, input field names/conditions/order, and output table/field names.

`DBInputFormat<T extends DBWritable>` implements `InputFormat<LongWritable,T>` and `JobConfigurable`. It has `configure`, `getSplits`, `getRecordReader`, protected `getCountQuery`, and two static `setInput` overloads: one for table plus fields/conditions/order and one for explicit input query plus count query. It emits row numbers as `LongWritable` keys and user `DBWritable` tuple objects as values.

`DBInputFormat.DBInputSplit` implements `InputSplit`, stores start/end row offsets, returns length, no location affinity, and serializes with `readFields(DataInput)` and `write(DataOutput)`.

`DBInputFormat.DBRecordReader<T>` implements `RecordReader<LongWritable,T>`, is constructed from a split, tuple class, and `JobConf`, exposes protected `getSelectQuery`, and supports `createKey`, `createValue`, `next`, `getPos`, `getProgress`, and `close`.

`DBInputFormat.NullDBWritable` implements both `DBWritable` and Hadoop `Writable` with no-op read/write methods for SQL and binary serialization.

`DBOutputFormat<K extends DBWritable,V>` implements `OutputFormat`. Protected `constructQuery` builds the SQL insert statement, `checkOutputSpecs` validates output configuration, `getRecordWriter` returns a writer, and static `setOutput` records output table and fields. Its `DBRecordWriter` writes only the key object to a `PreparedStatement`, then closes/commits via its connection and statement.

`DBWritable` is the tuple contract: `write(PreparedStatement)` and `readFields(ResultSet)`. Implementations usually also implement Hadoop `Writable` to participate in MapReduce serialization.

### `org.apache.hadoop.mapred.pipes`

`Submitter` extends `Configured` and implements `Tool`. It is the command-line and API entry point for Hadoop Pipes jobs. Static configuration helpers get/set the C++ executable URI, booleans for Java record reader, mapper, reducer, and record writer usage, and whether to keep the debugging command file (`downlink.data`) in task directories. `submitJob(JobConf)` is deprecated in favor of `runJob(JobConf)`. `runJob` mutates the job configuration for Pipes and submits it. `jobSubmit` submits to the MapReduce framework and returns a `RunningJob`. Instance `run(String[])` and static `main(String[])` provide CLI integration. A protected static `LOG` field is exposed.

### `org.apache.hadoop.metrics`

`ContextFactory` is the singleton factory for `MetricsContext` instances. It stores attributes, loads `hadoop-metrics.properties` from the classpath, and constructs a named context using `<contextName>.class`, defaulting to `org.apache.hadoop.metrics.spi.NullContext` when no class is configured. Attribute management uses `getAttribute`, `getAttributeNames`, `setAttribute`, and `removeAttribute`; `getContext` is synchronized and may throw class-loading and construction exceptions. `getNullContext` returns a no-op context.

`MetricsContext` defines monitoring lifecycle and updater registration: `startMonitoring`, `stopMonitoring`, `isMonitoring`, `close`, `createRecord`, `registerUpdater`, and `unregisterUpdater`. `DEFAULT_PERIOD` is the public default emit period in seconds.

`MetricsRecord` is the main mutable record API. It supports overloaded `setTag` for string and integer-like values, `removeTag`, overloaded `setMetric` and `incrMetric` for numeric values, `update`, and `remove`. The docs define records as named rows with zero or more tags and metrics. `update()` atomically updates or creates a buffered row matching the current tag set; `remove()` removes matching buffered rows. Separate `MetricsRecord` instances can safely update the same row concurrently, but the same instance should not be shared by threads.

`MetricsException` is the public runtime exception for metrics configuration/type conflicts. `MetricsUtil` simplifies context lookup and record creation, including host tagging. `Updater` is the timer callback interface invoked from a context.

### Metrics sinks, JVM metrics, SPI, and metric helper values

`FileContext` extends `AbstractMetricsContext` and emits records to an append-mode file configured by `<contextName>.fileName` or to stdout; it also honors a period property, flushes output, and closes files on `stopMonitoring`.

`GangliaContext` extends `AbstractMetricsContext` and sends emitted records to Ganglia.

`EventCounter` is a Log4J `AppenderSkeleton` that counts fatal, error, warn, and info events through static getters. `JvmMetrics` is a singleton `Updater` that periodically emits JVM metrics tagged by process name and session id.

`AbstractMetricsContext` is the central SPI base class. It implements `MetricsContext`, stores context name/factory, exposes protected attribute access, manages monitoring start/stop/close, creates final public metric records through protected `newRecord`, registers/unregisters updaters, maintains the internal table of metric rows, and calls abstract protected `emitRecord(contextName, recordName, OutputRecord)` each period. `flush()` is a protected no-op hook for sinks.

`MetricsRecordImpl` implements `MetricsRecord`, keeps a back-pointer to its `AbstractMetricsContext`, buffers tag/metric changes, and delegates `update()` and `remove()` back to the context.

`MetricValue` wraps a `Number` as either absolute or incremental using public `ABSOLUTE` and `INCREMENT` booleans, with `isAbsolute`, `isIncrement`, and `getNumber`.

`NullContext` discards all records and does not start monitoring. `NullContextWithUpdateThread` emits nothing but still uses the update thread so time-varying metrics can be sampled for systems such as JMX.

`OutputRecord` is an immutable-ish output view used by providers, exposing tag names, tag values, metric names, and metric values. `Util.parse` parses comma/space separated host or host:port specs into `InetSocketAddress` values, defaulting null specs to localhost with a supplied port.

`MBeanUtil` registers and unregisters JMX MBeans. `MetricsIntValue` and `MetricsLongValue` are set/inc/dec style metrics that publish only once after being changed. `MetricsTimeVaryingInt` publishes per-interval deltas and exposes previous-interval value. `MetricsTimeVaryingRate` records operation counts and times, publishes previous-interval average time and operation count, and tracks resettable min/max operation time. These helper classes synchronize mutators and `pushMetric(MetricsRecord)`.

### `org.apache.hadoop.net`

`DNSToSwitchMapping` maps hostnames or IP addresses to rack/network paths while preserving one-to-one input/output list correspondence. `CachedDNSToSwitchMapping` wraps another mapping in a cache and exposes protected `rawMapping`.

`ScriptBasedMapping` is a final `CachedDNSToSwitchMapping` that implements `Configurable` and delegates rack resolution to a script configured by `topology.script.file.name`.

`DNS` provides static direct and reverse lookup helpers: `reverseDns(InetAddress,String)`, `getIPs(interface)`, `getDefaultIP(interface)`, `getHosts(interface[, nameserver])`, and `getDefaultHost(interface[, nameserver])`.

`NetUtils` centralizes network address and stream construction. Socket factory helpers choose per-protocol or default factories from configuration keys such as `hadoop.rpc.socket.factory.class.<ClassName>` and `hadoop.rpc.socket.factory.class.default`. Address helpers parse `host`, `host:port`, and URI-like strings with optional default ports. `getServerAddress` bridges legacy separate bind/port keys to a combined address. Static resolution helpers add, fetch, and list test host mappings. `getConnectAddress(Server)` rewrites wildcard listener addresses to loopback client addresses. `getInputStream` and `getOutputStream` return channel-backed `SocketInputStream`/`SocketOutputStream` when a socket has a channel, otherwise regular socket streams. `normalizeHostName` and `normalizeHostNames` convert hostnames to textual IP addresses.

`NetworkTopology` models a cluster as a hierarchical tree of racks, data centers, and leaves. Public APIs add/remove leaf nodes, test containment, look up a path, return rack and leaf counts, compute distance, test same rack, choose a random node inside or outside a scope, count available nodes outside exclusions, stringify the tree, and pseudo-sort replica nodes by distance to a reader. Public fields include `DEFAULT_RACK`, `DEFAULT_HOST_LEVEL`, and `LOG`.

`Node` is the topology node interface: network location, name, parent, and level getters/setters. `NodeBase` implements it with constructors for path, name/location, and full parent/level state. It exposes static `getPath(Node)` and `normalize(String)`, constants `PATH_SEPARATOR`, `PATH_SEPARATOR_STR`, and `ROOT`, plus protected fields `name`, `location`, `level`, and `parent`.

`SocketInputStream` extends `InputStream` and implements `ReadableByteChannel`. Constructors accept a selectable readable channel plus timeout, a socket plus timeout, or a socket using its `SO_TIMEOUT`. The constructor configures the channel non-blocking, `read` methods wait for readability with timeout semantics, `getChannel` exposes the underlying channel for transfer operations, `isOpen` reports channel state, `close` is synchronized, and `waitForReadable` throws `SocketTimeoutException` on select timeout. The docs warn that after wrapping a socket channel, regular `Socket.getInputStream()` and `Socket.getOutputStream()` operations on the associated socket will throw `IllegalBlockingModeException`; callers should use `SocketOutputStream` for writes.

## Control Flow and Behavioral Contracts

MapReduce helper flow is configuration-driven. Client code records path-specific input formats through `MultipleInputs`, output side channels through `MultipleOutputs`, comparator/partition field specs through `JobConf`, partition-file locations through `TotalOrderPartitioner`, and DB/Pipes settings through their static helpers. Runtime flow then passes through `InputFormat`/`RecordReader`, mappers or reducers, `OutputCollector`, `Reporter`, `OutputFormat`, and optional counters.

Total-order sorting flow is split between sampling and partitioning. `InputSampler` reads input splits at the client, writes sorted split points to a SequenceFile, and `TotalOrderPartitioner.configure` loads that file before reducer assignment. The key comparator and split file must agree with the job comparator and reducer count.

Generic aggregation flow is data-driven. Descriptor classes convert input key/value pairs into `Text` aggregation id/value pairs. The key prefix names an aggregation type, `ValueAggregatorReducer` instantiates or selects the matching aggregator, consumes all values, and emits each aggregator's report. Combiners use the same aggregator output shape to reduce shuffle volume.

DB input flow computes a count query, splits row ranges with `LIMIT`/`OFFSET` style boundaries implied by `DBInputSplit`, and lets `DBRecordReader` execute a select query and fill user tuple objects through `DBWritable.readFields(ResultSet)`. DB output flow creates an insert `PreparedStatement`, calls `DBWritable.write(PreparedStatement)` on keys, batches or writes rows, and closes SQL resources.

Metrics flow starts at `ContextFactory.getFactory()` and `getContext(name)`. A context creates records, components set tags and metrics, `MetricsRecord.update()` writes into the context's buffered row table, and a monitoring thread periodically invokes registered `Updater`s, snapshots rows as `OutputRecord`s, calls provider `emitRecord`, then optional `flush`. `remove()` stops matching rows from being emitted in later periods.

Network flow resolves hostnames to rack paths through a raw or script-based `DNSToSwitchMapping`, caches results where configured, inserts `Node` instances into `NetworkTopology`, and uses the topology for rack locality decisions. Socket I/O flow chooses a configured socket factory, opens sockets, wraps channel-backed sockets in timeout-aware streams, and uses selector readiness rather than blocking socket streams.

## State and Persistence Behavior

The XML itself is static API metadata. Runtime state exposed by these contracts includes:

- `JobConf` entries for multiple inputs, multiple outputs, output counters, total-order partition files, DB connection/query/output settings, and Pipes executable/debugging/Java-component flags.
- Partition files stored as sorted SequenceFiles containing `numReduceTasks - 1` keys for total-order partitioning.
- Aggregator instances holding sums, extrema, unique-value sets, histograms, and combiner-output values during mapper, combiner, and reducer execution.
- JDBC connections, SQL statements, result sets, and row-range split offsets in DB input/output formats.
- Metrics factory attributes loaded from `hadoop-metrics.properties`, singleton contexts, context monitoring state, buffered metrics tables keyed by record name and tag sets, updater lists, file handles for `FileContext`, network sockets for `GangliaContext`, and Log4J event counters.
- Metrics helper values storing current, changed, previous-interval, min/max, and delta state. Their public mutator/push methods are synchronized, so tests should assume stateful interval transitions.
- DNS-to-switch caches, static host resolutions in `NetUtils`, network topology node/rack counts, parent/level links in `NodeBase`, and non-blocking channel state plus timeout configuration in `SocketInputStream`.

Persistence is primarily externalized through configuration files (`hadoop-metrics.properties`, job XML), HDFS/local paths for partition and output files, SQL databases for DB formats, task-local Pipes debugging files, metrics sink files or Ganglia packets, and Hadoop Writable serialization for input splits.

## Dependencies and Integration Points

Key dependencies visible in signatures and docs include:

- Classic MapReduce APIs: `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `OutputCollector`, `Reporter`, `Mapper`, `Reducer`, `MapRunnable`, `Partitioner`, `OutputFormat`, `FileInputFormat`, `FileOutputFormat`, `TextOutputFormat`, `SequenceFileOutputFormat`, `RunningJob`, and `JobClient`.
- Hadoop common APIs: `Configuration`, `Configured`, `Configurable`, `Tool`, `Progressable`, `Writable`, `WritableComparable`, `WritableComparator`, `LongWritable`, `Text`, `Path`, `FileSystem`, `SequenceFile`, `RawComparator`, and IPC `Server`.
- Java platform APIs: collections, regex/string tokenization implied by mappers, `IOException`, JDBC (`Connection`, `PreparedStatement`, `ResultSet`, `SQLException`), networking (`InetAddress`, `InetSocketAddress`, `Socket`, socket factories), NIO channels/selectors, JNDI `NamingException`, JMX, and Log4J.
- External systems: SQL databases through JDBC, C++ Hadoop Pipes executables, metrics files/stdout, Ganglia, DNS/name servers, topology scripts, and configured RPC socket factories.

These APIs sit at integration boundaries, so compatibility depends as much on configuration keys and documented side effects as on Java signatures.

## Risks and Edge Cases

- This chunk is API XML only. It does not reveal exact parser behavior, locking granularity, SQL dialect details, cleanup paths, or resource ownership beyond documented contracts.
- The chunk starts in the middle of `InputSampler` and ends immediately after `SocketInputStream`; adjacent chunks are needed for complete `InputSampler` and `SocketOutputStream` coverage.
- `RandomSampler` can be expensive when configured to sample all splits because it reads input at the client.
- `MultithreadedMapRunner` requires thread-safe mapper implementations; old mappers often use mutable reusable objects and may fail under concurrency.
- Key-field comparator and partitioner behavior depends on exact field separator, 1-based field/character positions, numeric parsing, reverse flags, and raw byte slicing. Misconfiguration can silently break sort or partition order.
- `TotalOrderPartitioner` requires a sorted partition file with exactly reducer-count minus one keys and a comparator compatible with the job. Bad files can cause skew, incorrect global order, or configure-time failures.
- `MultipleOutputs.close()` must be called by mapper/reducer code or extra writers may leak or leave incomplete output files. Multi-named outputs can create many files and counters.
- Aggregate descriptors are dynamically loaded by class name. Bad class names, missing configuration, or malformed aggregation id prefixes can fail at runtime. `UniqValueCount` can grow memory until its configured cap.
- DB formats depend on JDBC driver availability, SQL dialect support for count/select/offset patterns, stable row ordering, correct user `DBWritable` parameter indexes, and safe credential storage in `JobConf`.
- `DBOutputFormat` writes only keys, so jobs expecting value-side DB writes will silently use the wrong object unless configured carefully.
- Pipes job submission mutates `JobConf`; callers sharing a `JobConf` instance may see side effects. Keeping command files for debugging can expose serialized task commands and paths.
- Metrics records should not be shared concurrently by threads even though updates to a row are atomic through separate instances.
- `ContextFactory` defaults to `NullContext`, so missing metrics configuration silently discards data. `MetricsUtil.getContext` also logs failures and returns a null context rather than failing callers.
- File and Ganglia metrics sinks depend on external filesystem/network availability; `FileContext` append-mode files and `flush()` behavior are important for durability tests.
- `NullContextWithUpdateThread` emits no records but still samples; tests should distinguish sampling state from emitted data.
- DNS and rack mapping can return incomplete or misordered lists; the `DNSToSwitchMapping` contract requires one-to-one correspondence.
- `NetworkTopology.add` rejects non-leaf additions and additions under leaves; distance and same-rack methods may throw for null or out-of-cluster nodes.
- `NetUtils` static host resolution is process-global test state and can leak between tests.
- `SocketInputStream` forces non-blocking mode on the socket channel, making ordinary socket input/output streams invalid afterward. Timeout zero means infinite wait, while negative timeout is invalid.

## Test Signals

Useful tests inferred from this API slice include:

- Input sampler tests for interval, random, and split sampling across different split counts, maximum-split caps, empty inputs, client-side IO errors, and generated partition files compatible with `TotalOrderPartitioner`.
- Comparator/partitioner tests for `-k` field ranges, numeric and reverse sorting, character offsets, field separator configuration, hash stability, and compatibility between `KeyFieldBasedComparator` and `KeyFieldBasedPartitioner`.
- `TotalOrderPartitioner` tests for trie versus binary-search selection, reducer-count boundaries, missing/unsorted/wrong-length partition files, custom comparators, and `setPartitionFile`/`getPartitionFile` round trips.
- `MultipleInputs` tests for per-path input format and mapper resolution. `MultipleOutputFormat` tests for filename/key/value generation hooks and input-file-based output naming. `MultipleOutputs` tests for named and multi-named collectors, counter names, mapper bypass of reducers, and mandatory close behavior.
- `MultithreadedMapRunner` tests using thread-safe and intentionally unsafe mappers, configured thread counts, exception propagation, and reporter/output collector concurrency.
- `NLineInputFormat`, `RegexMapper`, `TokenCountMapper`, `InverseMapper`, `LongSumReducer`, and `NullOutputFormat` tests for basic emitted pairs and edge cases such as empty lines, unmatched regex, repeated tokens, and discarded output.
- Aggregate package tests for every `ValueAggregator` reset/add/report/combiner output path, histogram statistics and detailed output, unique-value caps, descriptor loading, mapper descriptor iteration, combiner aggregation, reducer prefix dispatch, and aggregate job configuration.
- DB tests with an embedded JDBC database for configureDB, table/query `setInput`, count query generation, split start/end serialization, record reader progress and close, `DBWritable` parameter/result mapping, output insert query construction, and SQL resource cleanup.
- Pipes `Submitter` tests for all boolean/executable/keep-command configuration helpers, deprecated `submitJob` compatibility, `runJob` configuration mutation, and CLI argument validation.
- Metrics tests for `ContextFactory` property loading, default null context fallback, context lifecycle, updater registration/removal, record tag and metric type conflicts, atomic row update semantics, row removal by tags, and `MetricsUtil.createRecord` host tagging.
- Metrics SPI tests for `AbstractMetricsContext` periodic emission, provider `emitRecord` and `flush`, `MetricsRecordImpl` delegation, `MetricValue` absolute/increment handling, `OutputRecord` tag/metric views, `NullContext` discard behavior, and `NullContextWithUpdateThread` sampling without emission.
- Sink/JVM/helper tests for `FileContext` append/stdout behavior and flush, `GangliaContext` packet emission with mock sockets where possible, `EventCounter` Log4J levels, `JvmMetrics.init` singleton behavior, `MBeanUtil` register/unregister, and synchronized metric helper interval transitions.
- Network tests for DNS interface/default-host helpers, reverse DNS failure paths, script-based and cached rack mapping order preservation, static resolution add/get/list isolation, socket factory class selection, address parsing, wildcard listener rewrite, hostname normalization, topology add/remove/distance/same-rack/random-scope/counting/pseudo-sort behavior, and `NodeBase` path normalization.
- `SocketInputStream` tests for channel-backed reads, byte-buffer reads, close/isOpen behavior, timeout and infinite-timeout behavior, `waitForReadable`, invalid negative timeout, and the documented non-blocking side effect on the underlying socket channel.

## Chunk Boundary Notes

The preceding chunk is needed for the full `InputSampler` class declaration and earlier `org.apache.hadoop.mapred.lib` APIs. This chunk includes the complete declarations for most `mapred.lib`, aggregate, DB, Pipes `Submitter`, metrics, and network classes listed above, but it ends at the start of `SocketOutputStream`, so output-stream timeout behavior must be reconciled with the following chunk.
