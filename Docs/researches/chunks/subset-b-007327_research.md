# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 43958-50145

## Chunk Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.20.1, not implementation source. It starts at the tail of `org.apache.hadoop.mapred.join.CompositeInputFormat`, covers the remainder of the old `mapred` join framework, much of `org.apache.hadoop.mapred.lib`, `mapred.lib.aggregate`, `mapred.lib.db`, Pipes submission/admin entry points, and ends in the beginning of the new `org.apache.hadoop.mapreduce.InputFormat` API after `Counter`, `CounterGroup`, `Counters`, and `ID`.

Because the source is API XML, behavior below is inferred from class docs, method signatures, declared checked exceptions, inheritance, visibility, synchronization flags, fields, and deprecation text rather than method bodies.

## Purpose

The chunk documents public and protected compatibility contracts for several MapReduce support layers:

- The `mapred.join` package exposes composite input splits, composable record readers, tuple values, resettable iterators, and expression parsing for sorted, co-partitioned joins.
- The `mapred.lib` package supplies reusable old-API MapReduce utilities: mapper/reducer chains, combined-file splits, per-path input delegation, field selection, identity/inverse/token/regex mappers, sum reducers, sampling and total-order partitioning, multiple inputs, multiple outputs, multithreaded map execution, N-line splitting, and null output.
- The `mapred.lib.aggregate` package defines a configurable aggregation framework that turns input records into typed aggregation key/value pairs, combines them, and emits textual reports.
- The `mapred.lib.db` package integrates old-API MapReduce jobs with JDBC input and output.
- `mapred.pipes.Submitter` exposes job configuration and submission for Hadoop Pipes C++ applications; `mapred.tools.MRAdmin` is a command-line/admin `Tool`.
- The visible `mapreduce` package section starts the newer API's counters, IDs, and abstract `InputFormat` contract.

This is primarily an API-compatibility artifact: it captures method names, overloads, return/parameter types, fields, docs, and deprecation messages that downstream clients or JDiff-based checks compare across Hadoop releases.

## Important APIs and Types

### `org.apache.hadoop.mapred.join`

`CompositeInputSplit` implements `InputSplit` as a collection of child splits. It can be constructed empty or with a fixed capacity, accepts child `InputSplit`s through `add`, exposes per-child and aggregate lengths/locations, and serializes as a count, child split class names, then child split payloads. Its docs require inserted splits to have public default constructors; `readFields` can fail when child splits cannot be read, including failed access checks.

`CompositeRecordReader` is the abstract base for joins over child `ComposableRecordReader`s sharing a key type and partitioning. Important members are protected final `jc` (`JoinCollector`) and `kids` (`ComposableRecordReader[]`). It manages child registration by `id`, key comparison through a `WritableComparator`, a priority queue of readers, key cloning, skip propagation, progress as the minimum child progress, and close propagation. Subclasses implement `combine(Object[], TupleWritable)` and provide a `ResetableIterator` delegate appropriate to their output type. Adding duplicate child IDs has undefined behavior, and `createKey` can throw `ClassCastException` if children use different key classes.

`JoinRecordReader` extends `CompositeRecordReader` and implements `ComposableRecordReader` for tuple-producing joins. `next(WritableComparable, TupleWritable)` emits the next joined tuple for the operation, `createValue` returns a `TupleWritable`, and `JoinDelegationIterator` is a `ResetableIterator` proxy around the join collector. `InnerJoinRecordReader` emits only full tuples, while `OuterJoinRecordReader` allows partially populated tuples. `OverrideRecordReader` is a `MultiFilterRecordReader` variant that overrides emission/fill behavior.

`MultiFilterRecordReader` is the base for composite joins that reduce a tuple to one emitted `Writable` via abstract `emit(TupleWritable)`. It has its own delegation iterator over emitted writable values, `combine` filtering, and `next(WritableComparable, Writable)`.

`Parser` and nested token/node types model the join expression language used by `CompositeInputFormat`. `Parser.Node` implements `ComposableInputFormat`, tracks a reader constructor map (`rrCstrMap`), ID, identifier, and comparator class, and supports `addIdentifier`, `setID`, and `setKeyComparator`. `Parser.TType` enumerates token types such as `CIF`, `IDENT`, comma, parentheses, quote, and number.

`ResetableIterator` is the iterator contract used by the join collector. It supports `hasNext`, forward `next`, `replay` of previous values, `reset`, `add`, `close`, and `clear`. `ResetableIterator.EMPTY` is a no-op implementation, while `StreamBackedIterator` stores/replays values using stream-backed state. `TupleWritable` implements `Writable` and `Iterable`, carrying an array of `Writable` slots plus presence bits; callers inspect `has(i)`, `get(i)`, and `size()`, and it supplies equality/hash/string, iteration, and binary serialization. `WrappedRecordReader` adapts an ordinary `RecordReader` into the composable join protocol by tracking its current head key/value, accepting matching join keys into a collector, forwarding `next`, `createKey`, `createValue`, progress, position, and close, and comparing by current key.

### `org.apache.hadoop.mapred.lib`

`ChainMapper` and `ChainReducer` compose old-API `Mapper`/`Reducer` instances inside one task. Static `addMapper` and `setReducer` mutate a `JobConf` with each element's classes, per-element `JobConf`, key/value types, and by-value versus by-reference passing mode. Runtime `configure`, `map`/`reduce`, and `close` instantiate and pipe records through the chain. The docs emphasize that adjacent key/value classes must match because the chain performs no conversion, and that by-reference mode depends on downstream code not mutating reused objects incorrectly.

`CombineFileInputFormat` is an abstract `FileInputFormat` that returns `CombineFileSplit`s built from blocks under input paths. Protected controls include maximum split size, minimum leftover split size per node/rack, and path-filter pools that prevent files from different pools from landing in one split. It combines same-node blocks first when max size is specified, then rack-local leftovers, and leaves `getRecordReader` abstract.

`CombineFileSplit` implements `InputSplit` as arrays of paths, offsets, lengths, and locations, plus a `JobConf` reference. It differs from `FileSplit` because one split can contain chunks from multiple files; it supports per-path and aggregate length queries, path arrays, location arrays, `Writable` serialization, and `toString`. `CombineFileRecordReader` iterates through a `CombineFileSplit`, reflectively constructing a per-chunk `RecordReader` from `rrClass`/`rrConstructor`; protected state includes current index, processed byte progress, current reader, filesystem, reporter, and split/job references.

`DelegatingInputFormat` and `DelegatingMapper` are used by `MultipleInputs` to dispatch records by input path to configured `InputFormat` and `Mapper` classes. `MultipleInputs.addInputPath` overloads register path-to-format and optional path-to-mapper mappings in `JobConf`.

`FieldSelectionMapReduce` implements both `Mapper` and `Reducer`, selecting configured input fields from text records and emitting rearranged fields. It exposes `map`, `reduce`, `configure`, `close`, and a commons-logging `LOG`.

Basic utility mappers/reducers include `HashPartitioner` (`hashCode`-based partitioning), `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and deprecated `TokenCountMapper` in favor of the newer `mapreduce.lib.map.TokenCounterMapper`.

`InputSampler` is a `Tool` for building partition files. It wraps a `JobConf`, writes partition files, and has nested `Sampler` implementations: `RandomSampler`, `IntervalSampler`, and `SplitSampler`, each returning sampled keys from an input format. These integrate with `TotalOrderPartitioner`, whose `configure` reads a sorted SequenceFile of `R-1` partition keys for `R` reducers. It can build a trie for `BinaryComparable` natural ordering or fall back to binary search with the job's `RawComparator`. Static `setPartitionFile` and `getPartitionFile` manage the partition-file path; `DEFAULT_PATH` is public.

`KeyFieldBasedComparator` and `KeyFieldBasedPartitioner` provide Unix-sort-like key-field selection for comparison and partitioning, configured through `JobConf`.

`MultipleOutputFormat` is an abstract `FileOutputFormat` that lets subclasses customize leaf file names, actual keys, and actual values before delegating to `getBaseRecordWriter`. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` implement base writers for SequenceFile and text outputs.

`MultipleOutputs` manages named and multi-named side outputs from mapper/reducer code. Static configuration methods register named outputs with output format/key/value classes, identify multi outputs, list named outputs, and enable counters. Runtime `getCollector` overloads lazily create `OutputCollector`s for single or multi named outputs and `close` closes all opened writers. Docs state side-output records emitted from mappers do not participate in reduce; optional counters use the `MultipleOutputs` class name as group and named output or named_output_multiName as counter names.

`MultithreadedMapRunner` implements `MapRunnable` with a configurable thread pool (`mapred.map.multithreadedrunner.threads`, default 10). The docs require thread-safe mapper implementations and recommend it for non-CPU-bound map work.

`NLineInputFormat` is a `FileInputFormat`/`JobConfigurable` that creates splits containing N lines each, defaulting to one line per map. It is aimed at parameter-sweep jobs where a control file line drives one task. `NullOutputFormat` consumes all output and is deprecated in favor of the newer `mapreduce.lib.output.NullOutputFormat`.

### `org.apache.hadoop.mapred.lib.aggregate`

`ValueAggregator` is the core mutable aggregate interface: `addNextValue`, `reset`, `getReport`, and `getCombinerOutput`. Implementations include `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. Most aggregators accept objects by parsing string values, expose the current numeric/string result, return a string report, reset state, and produce combiner-friendly string lists.

`UniqValueCount` tracks a bounded set of unique objects with configurable max item count. `ValueHistogram` tracks string-frequency pairs and reports summary statistics, detailed value/frequency output, combiner output, and a `TreeMap` of report items.

`ValueAggregatorDescriptor` generates aggregation key/value pairs from an input key/value and is configurable. `ValueAggregatorBaseDescriptor` provides built-in type names (`UNIQ_VALUE_COUNT`, `LONG_VALUE_SUM`, `DOUBLE_VALUE_SUM`, `VALUE_HISTOGRAM`, `LONG_VALUE_MAX`, `LONG_VALUE_MIN`, `STRING_VALUE_MAX`, `STRING_VALUE_MIN`), a type separator, an input file field, and helper methods to generate entries and aggregator instances. `UserDefinedValueAggregatorDescriptor` reflectively creates and delegates to user descriptor classes.

`ValueAggregatorJobBase` implements both mapper and reducer roles with an `aggregatorDescriptorList`, `configure`, `logSpec`, and `close`. `ValueAggregatorMapper`, `ValueAggregatorReducer`, and `ValueAggregatorCombiner` specialize map/reduce behavior for generating, combining, and reducing aggregate records. `ValueAggregatorJob` builds complete aggregate jobs or `JobControl` pipelines and can set descriptor classes.

### `org.apache.hadoop.mapred.lib.db`

`DBConfiguration` exposes public configuration keys for JDBC driver, URL, username, password, input table/fields/conditions/order/query/count-query/input class, and output table/fields. Static `configureDB` overloads set database connection properties with or without credentials.

`DBInputFormat` implements `InputFormat` and `JobConfigurable` for SQL table reads. It emits `LongWritable` row numbers as keys and `DBWritable` values. Static `setInput` overloads configure either table/conditions/order/field names or a full input query plus count query. Protected `getCountQuery` is an extension point for custom row counts. Nested `DBInputSplit` persists row index ranges (`start`, `end`) as an `InputSplit`. Nested `DBRecordReader` builds select queries, creates `LongWritable` keys and `DBWritable` values, reports row progress/position, and reads rows for a split. `NullDBWritable` is a do-nothing implementation used where no fields need transfer.

`DBOutputFormat` implements `OutputFormat` for SQL writes. `setOutput` configures target table and fields; protected `constructQuery` builds an INSERT prepared statement, accepting null field names when only field count is known. Its `DBRecordWriter` writes only the key when the key implements `DBWritable`, batching through JDBC and closing with a `Reporter`.

`DBWritable` is the JDBC-side companion to Hadoop `Writable`: implementations populate a `PreparedStatement` in `write(PreparedStatement)` and read fields from a `ResultSet` in `readFields(ResultSet)`.

### Pipes, Admin, and New `mapreduce` APIs

`org.apache.hadoop.mapred.pipes.Submitter` extends `Configured` and implements `Tool`. It is both API and command-line entry point for Hadoop Pipes. Static accessors mutate/read the Pipes executable URI, booleans for Java versus native record reader/mapper/reducer/record writer, and whether to keep the command file (`downlink.data`) for debugging. `submitJob` is deprecated in favor of `runJob`; `runJob` and `jobSubmit` submit a modified `JobConf` and return `RunningJob`. It has a protected static commons-logging `LOG`.

`org.apache.hadoop.mapred.tools.MRAdmin` extends `Configured`, implements `Tool`, and exposes constructors, `run(String[])`, and `main(String[])` for MapReduce administrative commands.

`org.apache.hadoop.mapreduce.Counter` is the newer API's synchronized mutable counter. It implements `Writable`, stores name/display name/value, supports `increment`, synchronized serialization, equality, and hash code. `CounterGroup` groups counters by logical enum/class group, implements `Writable` and `Iterable`, supports finding/creating counters, synchronized group serialization, size, equality/hash, and `incrAllCounters`. `Counters` contains groups, implements `Writable` and `Iterable`, supports lookup by group/counter names or enum key, group-name listing, group access, total counter count, merging, string rendering, and serialization with a documented wire format.

`org.apache.hadoop.mapreduce.ID` is the abstract `WritableComparable` base for `JobID`, `TaskID`, and `TaskAttemptID`. It stores protected integer `id`, uses protected `SEPARATOR`, compares by numeric id, and serializes/deserializes the integer.

The chunk ends inside `org.apache.hadoop.mapreduce.InputFormat`. The visible contract is abstract `getSplits(JobContext)` returning logical input splits and abstract `createRecordReader(InputSplit, TaskAttemptContext)`, with `IOException` and `InterruptedException`. Docs state that `InputFormat` validates input, creates logical splits, and provides `RecordReader`s initialized by the framework.

## Control Flow and Behavioral Contracts

Join processing flows from a `CompositeInputFormat` expression into parser nodes, child input formats, a `CompositeInputSplit`, wrapped child record readers, and then a `CompositeRecordReader` priority queue ordered by `WritableComparator`. At each join key, children that can offer the key feed `ResetableIterator`s into a `JoinCollector`; concrete join readers decide through `combine` whether a tuple should be emitted.

Old-API task composition flows through `JobConf` mutation. `ChainMapper.addMapper`, `ChainReducer.setReducer`, and `ChainReducer.addMapper` store class and per-stage configuration metadata. At runtime `configure` builds the chain, map/reduce calls pipe outputs to the next stage, and `close` cascades cleanup.

Combined-file input flow starts with input path discovery and block locality, groups blocks by pool, node, rack, and configured size thresholds, returns `CombineFileSplit`s, then `CombineFileRecordReader` advances through each chunk and instantiates the appropriate chunk reader.

Multiple input flow dispatches by path: `MultipleInputs` records path-specific input format and mapper classes, `DelegatingInputFormat` creates splits from each format, and `DelegatingMapper` invokes the mapper associated with the originating path.

Multiple output flow is lazy: static configuration validates named outputs, runtime `MultipleOutputs.getCollector` opens a writer on first use, emits to that writer, optionally increments counters, and `close` must flush/close every opened named output.

Sampling and total-order flow is: sample input keys through one of the `InputSampler.Sampler` implementations, write sorted split points with `InputSampler.writePartitionFile`, configure `TotalOrderPartitioner` with that partition file, then partition each map output key by trie or binary-search lookup.

Aggregate job flow is: descriptors inspect input records and emit aggregation-id/value pairs; combiners use each aggregator's `getCombinerOutput`; reducers rebuild aggregators from intermediate values and write reports. User descriptors are instantiated reflectively and configured through `JobConf`.

DB input flow configures JDBC properties and input query metadata, obtains a total row count, splits row ranges into `DBInputSplit`s, and each `DBRecordReader` selects a range with limit/offset-style semantics inferred from the docs. DB output flow constructs an INSERT `PreparedStatement`, lets `DBWritable` keys bind parameters, and writes batches on close.

Pipes submission flow mutates the job to launch a native executable, records whether Java components are used for each stage, optionally preserves command data for debugging, and submits the job through the MapReduce framework.

New `mapreduce` counter flow is synchronized mutation/serialization of counters, groups, and group collections. `InputFormat` flow is the newer split creation plus record reader creation/initialization contract.

## State and Persistence

Persistent and mutable state in this chunk includes:

- `CompositeInputSplit`, `CombineFileSplit`, `DBInputSplit`, `TupleWritable`, `Counter`, `CounterGroup`, `Counters`, and `ID` implement Hadoop `Writable` persistence.
- Join readers maintain in-memory reader queues, current head keys/values, child reader arrays, join collector state, and resettable iterator buffers. `StreamBackedIterator` implies spill/stream-backed replay state for join values.
- `JobConf` is the persistence medium for chain definitions, multiple input/output mappings, input sampler/partitioner files, aggregator descriptors, DB connection/query settings, Pipes executable and booleans, and N-line/multithreaded runner settings.
- `CombineFileRecordReader` tracks current split index, current reader, and processed byte count for position/progress.
- `MultipleOutputs` tracks opened named-output collectors/writers and must close them explicitly.
- Aggregators hold mutable sums, extrema, unique sets, histograms, or descriptor lists until reset or task close.
- DB formats persist row-range split boundaries and rely on external database tables for durable input/output data.
- `Counter`, `CounterGroup`, and `Counters` persist job metrics through a documented binary format and support synchronized mutation/merge.

## Dependencies and Integration Points

Major dependencies visible from signatures include old MapReduce APIs (`JobConf`, `Mapper`, `Reducer`, `MapRunnable`, `InputFormat`, `InputSplit`, `RecordReader`, `OutputFormat`, `RecordWriter`, `OutputCollector`, `Reporter`, `Partitioner`, `RunningJob`, `JobClient`), Hadoop IO (`Writable`, `WritableComparable`, `WritableComparator`, `RawComparator`, `LongWritable`, `Text`, SequenceFile-related partition files), filesystem types (`Path`, `PathFilter`, `FileSystem`), configuration/tooling (`Configuration`, `Configured`, `Tool`, `Progressable`), Java reflection, Java SQL (`Connection`, `PreparedStatement`, `ResultSet`, `SQLException`), Java collections, and commons logging.

Integration points are intentionally broad:

- Join APIs plug into `CompositeInputFormat` expressions and user-defined join identifiers via `mapred.join.define.<ident>` and key comparators via `mapred.join.keycomparator`.
- Chain, multiple input, multiple output, and aggregate helpers are configured through `JobConf`, making them composable with old `mapred` jobs without changing user mappers/reducers.
- `TotalOrderPartitioner` depends on partition files created by `InputSampler`, and its correctness depends on matching sort comparators and reducer count.
- DB formats bridge Hadoop record processing with JDBC row objects implemented by user `DBWritable` classes.
- Pipes `Submitter` bridges Java job submission with external C++ executables and task command streams.
- The visible `mapreduce` types show parallel newer-API contracts living beside old-API utilities in this snapshot.

## Risks and Edge Cases

- The chunk starts mid-`CompositeInputFormat` and ends mid-`mapreduce.InputFormat`; adjacent chunks are needed for complete class docs.
- API XML omits method bodies, so exact exception ordering, resource cleanup, SQL dialect handling, object reuse, synchronization internals, and spill behavior are not directly visible.
- Join correctness depends on all data sources being sorted and partitioned identically with compatible key classes and comparators; `createKey` can fail when child key classes differ.
- `CompositeInputSplit` deserialization requires child split classes with public default constructors, and access checks can make a serialized split unreadable.
- Duplicate `ComposableRecordReader.id()` values have undefined behavior and can corrupt tuple slot assignment.
- Resettable join iterators can retain large key groups in memory or stream-backed buffers; high-duplication join keys are a likely stress point.
- ChainMapper/ChainReducer do no key/value conversion between stages. A bad type declaration or by-reference mutation can fail at runtime or produce corrupted records.
- `CombineFileInputFormat` trades fewer tasks for more complex locality; split pools, node/rack thresholds, and max split size can produce surprising locality or imbalance.
- `CombineFileRecordReader` uses reflection for child readers; constructor signature drift or visibility changes can break jobs late.
- `MultithreadedMapRunner` requires thread-safe mappers and collectors; old mappers often assume single-threaded object reuse.
- `MultipleOutputs` requires explicit `close`; failing to close can lose side-output data. Named-output counters can grow with multi-name cardinality.
- `TotalOrderPartitioner` requires exactly `numReduceTasks - 1` sorted split keys using the same comparator as map-output sort; stale partition files or reducer-count changes mispartition output.
- Aggregators parse values from object string representations; malformed numeric strings, overflow, NaN, or locale-sensitive formatting can affect results. `UniqValueCount` has bounded-memory semantics that can undercount once the limit is reached.
- DB input/output is SQL-dialect-sensitive, especially count queries, limit/offset selection, transaction boundaries, batching, and generated insert SQL. Credentials are stored in `JobConf` properties.
- Pipes debugging command files can contain task protocol data and should be treated as sensitive. The executable URI must be distributed and executable on task nodes.
- Several old-API helpers are deprecated or point to newer `mapreduce` replacements, so compatibility work must distinguish intentional legacy support from migration targets.

## Test Signals

Useful tests inferred from this API surface:

- Round-trip `Writable` serialization for `CompositeInputSplit`, `CombineFileSplit`, `DBInputSplit`, `TupleWritable`, `Counter`, `CounterGroup`, `Counters`, and `ID`.
- Join tests covering inner, outer, override, and multi-filter joins with sorted/co-partitioned sources; duplicate keys; missing tuple slots; incompatible key classes; custom comparators; skip behavior; progress; close propagation; and parser expression errors.
- `WrappedRecordReader` and `ResetableIterator` tests for replay/reset/clear semantics, large duplicate-key groups, empty iterators, and stream-backed replay cleanup.
- Chain tests verifying mapper/reducer order, per-stage configuration precedence, type mismatch failures, by-value versus by-reference mutation behavior, and close ordering.
- CombineFile tests for max split size, node/rack minimum thresholds, path-filter pools, location hints, copy constructor, reflective reader construction, position/progress, and chunk-to-reader handoff.
- MultipleInputs tests confirming path-specific `InputFormat` and mapper dispatch, including multiple paths with different formats.
- MultipleOutputs tests for named and multi-named output registration, duplicate/invalid names, side-output file creation, counter names, mapper side-output bypass of reduce, and required close behavior.
- InputSampler/TotalOrderPartitioner tests with random/interval/split samplers, sorted SequenceFile partition files, reducer-count changes, natural binary trie path, custom comparator binary-search path, and boundary keys equal to split points.
- Aggregate framework tests for each built-in aggregator, combiner output compatibility, histogram report details, unique-count max item behavior, descriptor reflection/configuration, and malformed values.
- DB format tests against representative JDBC backends for generated count/select/insert SQL, row-range splits, `DBWritable` binding/reading, transaction close behavior, null field names, and credential/config propagation.
- Pipes Submitter tests verifying each configuration accessor, command-file retention flag, deprecated `submitJob` parity with `runJob`, and job configuration mutations before submission.
- New `mapreduce` counter tests for synchronized increments, group/counter lookup, merge semantics, documented binary format, equality/hash code, and enum-key lookup.
