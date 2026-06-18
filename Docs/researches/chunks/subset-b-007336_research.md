# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 43883-50039

## Scope

This chunk is a middle segment of the generated JDiff public API snapshot for Hadoop 0.20.2. It is XML compatibility metadata, not implementation source. The range starts at the tail of `org.apache.hadoop.mapred.join.ArrayListBackedIterator`, covers the rest of the old `org.apache.hadoop.mapred.join` API, most of the legacy `org.apache.hadoop.mapred.lib` helper package, the `mapred.lib.aggregate` aggregation framework, JDBC-backed `mapred.lib.db` input/output APIs, the `mapred.pipes.Submitter` tool, `mapred.tools.MRAdmin`, and begins the newer `org.apache.hadoop.mapreduce` counter model.

The XML records public class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and exception types, fields, visibility, deprecation markers, method modifiers, and embedded Javadocs. Behavioral notes below are inferred from that public metadata and documentation because method bodies are not present in this file.

## Purpose and Major API Surface

The `org.apache.hadoop.mapred.join` package exposes the old MapReduce join framework. `ComposableInputFormat` refines `InputFormat` to return `ComposableRecordReader`. `ComposableRecordReader` adds join-aware cursor operations: `id()`, `key()`, key cloning, `hasNext()`, `skip(WritableComparable)`, and `accept(JoinCollector, WritableComparable)`.

`CompositeInputFormat` parses a join expression from `mapred.join.expr`, installs built-in and user-defined join operators from `mapred.join.define.<ident>`, builds child input formats, creates aligned `CompositeInputSplit` instances, and constructs the root `ComposableRecordReader`. Its static `compose(...)` helpers generate `tbl(...)` and operator expressions for class/path inputs. `CompositeInputSplit` stores a fixed set of child `InputSplit`s, aggregates lengths and locations, and serializes as count, split class names, then child split payloads.

`CompositeRecordReader` is the base join reader. It is `Configurable`, owns child `ComposableRecordReader` instances, exposes a priority queue of child readers ordered by a `WritableComparator`, fills a `JoinCollector`, implements key comparison and skipping, creates common key/internal tuple values, reports progress as the minimum child progress, and closes all children. Subclasses define `combine(Object[], TupleWritable)` and `getDelegate()`.

The join subclasses model concrete operators. `JoinRecordReader` emits `TupleWritable` values and delegates iteration through `JoinDelegationIterator`. `InnerJoinRecordReader` only combines full tuples where every source has the key. `OuterJoinRecordReader` emits all tuples from the collector. `MultiFilterRecordReader` emits a single `Writable` derived from a tuple through `emit(TupleWritable)`, with `MultiFilterDelegationIterator` as its proxy. `OverrideRecordReader` prefers the rightmost source for a key and overrides collector filling to skip lower-priority streams once a higher-priority value is available.

`Parser`, `Parser.Node`, token classes, and `Parser.TType` define the join-expression parser. The parser is documented as a simple shift-reduce parser. `Node` implements `ComposableInputFormat`, tracks an identifier, id, comparator class, and a constructor map for record-reader nodes. Token subclasses carry parsed nodes, strings, and numbers.

`ResetableIterator` is a stateful replayable iterator interface used by join collection. It supports `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`, deliberately not extending `java.util.Iterator`. `ResetableIterator.EMPTY` is a no-op implementation. `ArrayListBackedIterator` stores replay data in an `ArrayList` but is documented as less preferred than `StreamBackedIterator`, which stores added elements in a byte array. `TupleWritable` stores an array of `Writable` values plus per-position presence bits, is itself `Writable` and `Iterable`, and serializes written-element cardinality plus values.

`WrappedRecordReader` adapts a normal old-api `RecordReader` to `ComposableRecordReader`. It keeps a head key/value pair, compares by head key, supports `skip`, adds values to a join collector, forwards `createKey`, `createValue`, progress, position, and close to the proxied reader, and advances the proxied stream after emitting the current head.

The `org.apache.hadoop.mapred.lib` package contains old-api helpers. `ChainMapper` and `ChainReducer` let jobs run a mapper chain, or reducer followed by mapper chain, inside one task. They use static configuration methods to append mapper/reducer classes and key/value classes, then instantiate/configure/close the chain around `map` or `reduce` calls. `CombineFileInputFormat`, `CombineFileSplit`, and `CombineFileRecordReader` combine many small files into fewer splits, with split-size controls, node/rack minimums, path-filter pools, per-chunk record reader creation by reflection, byte-progress tracking, and split serialization of paths, offsets, lengths, locations, and job state.

`DelegatingInputFormat`, `DelegatingMapper`, and `MultipleInputs` implement per-path input format and mapper selection. `MultipleInputs.addInputPath(...)` records path-specific input formats and optionally mapper classes, `DelegatingInputFormat` routes split and reader creation, and `DelegatingMapper` routes records to the mapper configured for their input path. `FieldSelectionMapReduce` is both a mapper and reducer that selects fields from text values based on configuration. `HashPartitioner`, `KeyFieldBasedComparator`, `KeyFieldBasedPartitioner`, and `TotalOrderPartitioner` provide partitioning and sorting utilities, including Unix-sort-like key field specifications and total-order partitioning from an externally generated SequenceFile of split points.

The simple mapper/reducer helpers include `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper`. Several old `mapred` classes are explicitly deprecated in favor of newer `org.apache.hadoop.mapreduce` equivalents, but the signatures remain compatibility-relevant. `InputSampler` and its `IntervalSampler`, `RandomSampler`, and `SplitSampler` collect key samples from old-api input formats and write partition files for `TotalOrderPartitioner`.

The output helpers include `MultipleOutputFormat`, `MultipleOutputs`, `MultipleSequenceFileOutputFormat`, `MultipleTextOutputFormat`, and `NullOutputFormat`. `MultipleOutputFormat` is an abstract `FileOutputFormat` that can derive output file names, actual output keys/values, and base record writers per key/value or input file. `MultipleOutputs` configures named and multi-named outputs, exposes static metadata accessors, optional counters, collector factories, and `close()` for opened writers. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide base writers for those formats. `NullOutputFormat` discards all output.

`MultithreadedMapRunner` is an old-api `MapRunnable` that runs mapper calls in a thread pool, controlled by `mapred.map.multithreadedrunner.threads`, and requires thread-safe mapper implementations. `NLineInputFormat` creates one split for every configured number of lines, intended for parameter sweep style workloads where each input line describes independent work.

The `org.apache.hadoop.mapred.lib.aggregate` package provides a generic aggregation framework. `ValueAggregator` defines `addNextValue`, `reset`, `getReport`, and `getCombinerOutput`. Built-ins include double/long sum, long min/max, string min/max, unique-value counting with a maximum retained item count, and histograms. `ValueAggregatorDescriptor` generates aggregation-id/value pairs from input records. `ValueAggregatorBaseDescriptor` supplies standard aggregation type names and factory logic, while `UserDefinedValueAggregatorDescriptor` reflectively delegates to user descriptor classes. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, `ValueAggregatorReducer`, and `ValueAggregatorJobBase` implement the map, combine, and reduce phases for Aggregate jobs. `ValueAggregatorJob` builds job controls and `JobConf`s for aggregate workloads and exposes a command-line entry point.

The `org.apache.hadoop.mapred.lib.db` package exposes JDBC-backed old-api I/O. `DBConfiguration` defines job configuration keys and static `configureDB(...)` methods for JDBC driver, URL, username, and password. `DBInputFormat` is an `InputFormat`/`JobConfigurable` for SQL input, with static `setInput(...)` overloads for table/query configuration, count-query generation, row-range splits, and a `DBRecordReader` that returns `LongWritable` keys and `DBWritable` values. `DBOutputFormat` writes reducer output keys to a SQL table through prepared statements and has static `setOutput(...)` configuration. `DBWritable` is the contract for translating objects to/from `PreparedStatement` and `ResultSet`; `NullDBWritable` is a no-op bridge implementation.

`org.apache.hadoop.mapred.pipes.Submitter` is the old Hadoop Pipes job launcher. It is a `Tool` and `Configured` class with accessors for the executable URI, booleans controlling whether record reader, mapper, reducer, and record writer are Java-side or native-side, command-file retention for debugging, deprecated `submitJob`, replacement `runJob`, lower-level `jobSubmit`, `run`, and `main`. `org.apache.hadoop.mapred.tools.MRAdmin` is an administrative `Tool` for connecting to the JobTracker and refreshing the service-level authorization policy.

The chunk ends in `org.apache.hadoop.mapreduce` with the start of the new counter API. `Counter` is a synchronized `Writable` with name, display name, value, increment, equality, and hash code. `CounterGroup` is a synchronized `Writable`/`Iterable` of counters with group display metadata, lookup/creation, serialization, size, equality, hash code, and `incrAllCounters`. `Counters` begins with lookup by group/name and enum, group-name listing, iteration, group retrieval, and `countCounters()`; the method body metadata continues in the next chunk.

## Control Flow and Behavioral Contracts

Join execution is expression driven. `CompositeInputFormat.setFormat` parses `mapred.join.expr`; default and configured identifiers map expression nodes to `ComposableRecordReader` constructors; `getSplits` aligns the i-th split from each child into a `CompositeInputSplit`; `getRecordReader` materializes the corresponding reader tree. Runtime join flow advances child readers in key order, uses `skip` to discard lower keys, asks matching children to `accept` a key into the `JoinCollector`, then emits tuples or filtered values according to the concrete join reader's `combine`/`emit` rules.

Replayable iterators are central to join correctness. Children add matching values into resettable iterators, the collector replays combinations for matching keys, and `reset` must be called after `add` to avoid concurrent modification problems. `TupleWritable` exposes sparse tuple positions through `has(int)` rather than assuming every child contributed.

Multi-input control flow depends on job configuration. `MultipleInputs` records path-to-input-format and path-to-mapper metadata; the delegating input format groups splits by input format and creates the right reader; the delegating mapper configures and invokes the mapper selected for each path. This allows one old-api job to consume heterogeneous input sources.

Combine-file flow groups files into logical splits and then iterates chunks inside a split. `CombineFileRecordReader.initNextRecordReader()` advances to the next path/offset/length segment, constructs the per-chunk reader by reflection, and accumulates progress in bytes processed. The `getRecordReader` method on `CombineFileInputFormat` is explicitly documented as not implemented in the abstract base.

Sampler and total-order partitioner flow is two-stage. `InputSampler` samples keys from input splits and writes a SequenceFile of partition boundaries. `TotalOrderPartitioner.configure` reads that file and chooses either a trie for natural-order `BinaryComparable` keys or binary search using the job's `RawComparator`; the partition file must have `numReduceTasks - 1` sorted keys.

Multiple-output flow is side-effect oriented. Job setup defines named outputs and optionally counters. Task code obtains a collector for a named output or a multi-named output, which lazily opens a writer with the configured `OutputFormat`, key class, and value class. `close()` must be called to flush and close all opened outputs. Named output records written from a mapper bypass the reduce phase unless written to the primary job collector.

Aggregate flow maps input records to aggregation-id/value pairs, combines values with matching aggregation ids, and reduces them through the selected `ValueAggregator`. Descriptor classes are responsible for turning arbitrary input key/value pairs into typed aggregation entries using the `TYPE_SEPARATOR` protocol and standard aggregation names.

DB input flow computes a row count, divides rows into `DBInputSplit` ranges, generates select queries with limit/offset style range constraints, and asks `DBWritable` instances to populate themselves from `ResultSet`. DB output flow constructs an insert prepared statement from configured table and field names, asks the output key to write fields into the statement, batches records, and closes JDBC resources.

Pipes submit flow mutates a `JobConf` so a Hadoop job launches a C++ pipes executable, with per-component switches deciding whether Java or pipes code handles reading, mapping, reducing, and writing. Keeping the command file writes `downlink.data` in the task directory for replay/debugging.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent public API metadata for compatibility checking. The source does not store runtime state, but it captures configuration keys, serialized forms, and public method contracts that downstream Hadoop applications depend on.

Join state lives in child record-reader heads, priority queues, `JoinCollector` contents, `ResetableIterator` buffers, tuple presence bits, and job configuration values such as `mapred.join.expr`, `mapred.join.define.<ident>`, and `mapred.join.keycomparator`. `CompositeInputSplit`, `TupleWritable`, and child splits are serialized through `DataOutput`/`DataInput`, so class names, ordering, and writable payload order are compatibility-sensitive.

Old mapred helper state is primarily `JobConf` state. Chain jobs persist mapper/reducer chain metadata and key/value class boundaries in configuration. Multiple inputs persist path-specific input formats and mapper classes. Field selection, key-field comparison/partitioning, total-order partitioning, multi-output definitions, counters-enabled flags, N-line splitting, multithreaded runner thread count, and DB connection/query properties are all configured through `JobConf`.

Filesystem side effects appear in combine-file split planning, input sampling partition-file creation, total-order partition-file reads, multiple-output writer creation, sequence/text output writer creation, and null output discard behavior. Multiple outputs create additional output files beyond the default job output and optionally emit counters named after outputs.

Database side effects are external and transactional only to the degree provided by the implementation and JDBC connection handling. `DBInputFormat` reads table/query results; `DBOutputFormat` inserts reduce output keys into an SQL table through prepared statements. Configuration includes driver class, URL, username, and password, making credential handling and job-conf exposure relevant.

Pipes state includes the executable URI, Java/native component booleans, optional saved command file, task-local debugging artifacts, and submitted job handles. `MRAdmin` causes cluster-side administrative effects by refreshing service-level authorization policy through the JobTracker.

`Counter`, `CounterGroup`, and `Counters` are synchronized writable state containers. Counter names, display names, values, group membership, serialization, equality, and aggregate increment behavior are part of the public compatibility surface for job progress, metrics, history, and user code.

## Dependencies and Integration Points

This chunk is anchored in the legacy `org.apache.hadoop.mapred` API: `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `MapRunnable`, `OutputCollector`, `OutputFormat`, `RecordWriter`, `Reporter`, `Partitioner`, `JobConf`, `JobConfigurable`, `FileInputFormat`, `FileOutputFormat`, `MapReduceBase`, `RunningJob`, and `JobClient` style workflows.

Serialization and data dependencies include `org.apache.hadoop.io.Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `Text`, `LongWritable`, `BinaryComparable`, and `SequenceFile`. Filesystem dependencies include `Path`, `FileSystem`, path filters, split locations, and progress callbacks through `org.apache.hadoop.util.Progressable`.

The join framework integrates with Java collections and reflection through `PriorityQueue`, `Map`, `Comparable`, constructor maps, parser token classes, and class names configured in expressions. The chain, multiple input, combine-file, aggregate, DB, and pipes APIs also rely heavily on `java.lang.Class` values in `JobConf`.

External system dependencies are explicit in JDBC APIs: `java.sql.Connection`, `PreparedStatement`, `ResultSet`, and `SQLException`. Pipes integrates Java MapReduce job submission with an external native executable URI, commonly on HDFS. Logging uses Apache Commons Logging in several public `LOG` fields.

The newer `org.apache.hadoop.mapreduce` counter classes begin the bridge from old mapred helpers toward the newer API. Many old helpers in this chunk are deprecated with references to `org.apache.hadoop.mapreduce` replacements, which is important for compatibility and migration tooling.

## Risks and Compatibility Notes

The range starts inside `ArrayListBackedIterator` and ends inside `Counters.countCounters()`, so adjacent chunks are needed for complete class-level reconstruction. This chunk still contains complete entries for most join, lib, aggregate, DB, pipes, and MRAdmin classes.

Join APIs are high-risk because they combine sorted input assumptions, configured parsers, reflection, tuple serialization, comparator behavior, and iterator replay. Incorrect child split alignment, key comparator mismatch, duplicate child ids, missing public default constructors for serialized splits, or stale resettable iterator state can produce silent join loss or duplication.

`CompositeInputSplit.write/readFields` serializes class names before child split payloads. Renaming split classes, removing public no-arg constructors, changing child order, or changing writable payloads would break persisted splits and compatibility with running or recovered tasks.

`TupleWritable` sparse presence bits are a compatibility contract. Consumers must check `has(i)` before `get(i)` for outer joins; serialization must preserve which tuple positions were written, not just the writable array.

Configuration string formats are broad compatibility surfaces. Join expressions, key-field specs, path-specific input mappings, multiple-output names, total-order partition file paths, DB query/table/field settings, pipes executable URIs, and counter group/name strings are commonly embedded in job configs, tests, examples, and downstream applications.

`MultipleOutputs` has several correctness risks: named output names must be validated, `"part"` is reserved, mapper-side named-output records bypass reducers, counters are disabled by default, multi-output counter names concatenate output and multi-name with an underscore, and callers must close the object to release opened writers.

`MultithreadedMapRunner` exposes concurrency risk. Mapper implementations and any shared output/reporting/counter interactions must be thread-safe. Input readers and collectors also need careful coordination in the implementation because old mapred mappers usually assume single-threaded invocation.

`TotalOrderPartitioner` correctness depends on sorted partition files, exactly `R - 1` split keys for `R` reducers, and comparator consistency between sampling, partition-file sorting, and runtime partitioning. Trie depth and natural-order settings can affect both correctness and performance.

Aggregate APIs rely on string-encoded type/value protocols and reflection. Typos in aggregation type names, descriptor class names, or `TYPE_SEPARATOR` handling can route data to the wrong aggregator or fail at runtime. Numeric aggregators parse values from string representations, so malformed input values are a test and error-handling concern.

DB APIs can leak credentials through job configuration and have external side effects. Query construction, count queries, limit/offset semantics, prepared-statement field ordering, batching, connection cleanup, SQL exceptions, and database-specific syntax are all risky. `DBOutputFormat` writes only the key, so users must encode all DB fields in the key's `DBWritable` implementation.

Pipes submission mutates `JobConf` and starts external executables. Component-mode flags must be coherent with provided Java classes and native code. Saved command files are useful for debugging but can expose task data in local task directories.

Counter APIs use synchronized public methods and writable serialization. Any change to synchronization, serialization order, equality/hash code, display-name handling, enum mapping, or group aggregation can affect job metrics, UI display, history, and user assertions.

## Test Signals

JDiff-level validation should confirm the XML remains well formed across this chunk, preserves package/class/interface names, inheritance, implemented interfaces, constructors, method signatures, parameter and exception types, fields, visibility, deprecation text, and synchronization/static/final/abstract/native flags.

Join tests should cover `CompositeInputFormat.compose` output, parsing of nested expressions, custom `mapred.join.define.<ident>` operators, comparator configuration, aligned split creation, `CompositeInputSplit` serialization round trips, missing split constructors, `WrappedRecordReader` key advancement, skip semantics, inner join full-tuple behavior, outer join sparse tuples, override rightmost-source preference, tuple `has/get` behavior, and `ResetableIterator` add/reset/replay/clear/close semantics.

Legacy lib tests should cover chain mapper/reducer configuration and lifecycle ordering, multiple input path routing, delegating mapper selection, field selection specs, hash and key-field partitioning, key-field comparator numeric/reverse/range behavior, total-order partitioning from sampled split points, and deprecation-compatible behavior of identity, inverse, regex, token-count, and long-sum helpers.

Combine-file tests should cover max split size, min split size per node/rack, path-filter pools, split serialization, location aggregation, per-chunk record reader reflection, progress accounting, zero-length files, and cleanup when moving between chunk readers.

Sampler tests should cover interval, random, and split samplers against multiple input splits; sample-count limits; random split ordering; partition-file writing; and compatibility with `TotalOrderPartitioner`.

Output tests should cover `MultipleOutputFormat` filename/key/value customization hooks, input-file-based output naming, named-output metadata accessors, name validation including reserved `part`, single and multi named collectors, counter enablement and counter naming, mapper-side bypass of reducers, close behavior for all opened outputs, sequence/text writer creation, and `NullOutputFormat` discarding records.

Aggregate tests should cover every built-in aggregator's add/reset/report/combiner-output behavior, malformed numeric values, unique-value maximum enforcement, histogram report details, descriptor-generated entries, user-defined descriptor reflection/configuration, mapper/combiner/reducer data flow, and `ValueAggregatorJob` configuration helpers.

DB tests should cover JDBC configuration keys, `setInput` table and query modes, count query customization, split row ranges and serialization, select-query construction, `DBWritable` read/write callbacks, null writable no-op behavior, output insert query construction with explicit and null field lists, prepared statement field order, batch/close behavior, SQL exception paths, and cleanup of connections/statements/result sets.

Pipes and admin tests should cover executable URI setters/getters, Java/native component flags, keep-command-file behavior, deprecated `submitJob` delegation to `runJob`, `jobSubmit` returning a `RunningJob`, command-line `run/main` argument validation, and `MRAdmin` refresh authorization command handling.

Counter tests should cover synchronized `Counter` read/write/increment/equality/hash code, display-name updates, `CounterGroup` lookup and creation semantics, group serialization, iteration, `incrAllCounters`, `Counters.findCounter` by enum and group/name, group-name listing, empty-group retrieval, counter counting, and serialization compatibility across old job history or metrics consumers.
