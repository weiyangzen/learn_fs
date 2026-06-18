# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 43798-50012

## Chunk Scope

This chunk is a JDiff XML API snapshot for Hadoop 0.20.0. It starts inside the `org.apache.hadoop.mapred.lib.ChainReducer` class and continues through the rest of `org.apache.hadoop.mapred.lib`, the `org.apache.hadoop.mapred.lib.aggregate` framework, JDBC-backed `org.apache.hadoop.mapred.lib.db` APIs, `org.apache.hadoop.mapred.pipes.Submitter`, `org.apache.hadoop.mapred.tools.MRAdmin`, and the beginning of the newer `org.apache.hadoop.mapreduce` package. It ends inside `org.apache.hadoop.mapreduce.Reducer`, so reducer lifecycle details continue in a later chunk.

The file is documentation metadata, not executable source. Its purpose is to preserve public and protected Java API shape: packages, classes, interfaces, methods, fields, visibility, abstract/static/final/synchronized flags, exceptions, deprecation notes, and Javadoc CDATA.

## Purpose and Major Areas

The span documents compatibility and helper APIs around old `org.apache.hadoop.mapred` jobs and the emerging `org.apache.hadoop.mapreduce` API:

- `mapred.lib` utilities for chained map/reduce composition, combined file splits, multi-input routing, identity/inverse/simple reducers, field-based partitioning/comparison, total-order sampling, multiple named outputs, null output, regex/token mappers, n-line input, and multithreaded map execution.
- `mapred.lib.aggregate` provides a generic aggregation mini-framework. Users supply `ValueAggregatorDescriptor` implementations that emit aggregation id/value pairs; built-in aggregators sum, min/max, count unique values, and produce histograms; generic mapper/combiner/reducer classes perform aggregation by encoded key prefixes.
- `mapred.lib.db` exposes JDBC input/output formats. `DBConfiguration` defines `JobConf` property names, `DBInputFormat` creates row-range splits and record readers, `DBOutputFormat` writes via prepared statements, and `DBWritable` bridges Hadoop writable objects with SQL `ResultSet` and `PreparedStatement`.
- `mapred.pipes.Submitter` configures and launches C++/non-Java Hadoop Pipes jobs, including whether Java or native components provide record readers, mappers, reducers, and writers.
- `mapred.tools.MRAdmin` is an administrative `Tool` for connecting to the JobTracker and refreshing service-level authorization policy.
- `mapreduce` begins the new API surface: counters, counter groups, job IDs, `Job`/`JobContext`, split/input/output contracts, mapper contexts, output committers, partitioners, readers/writers, and reduce context support.

## Important APIs and Types

### `org.apache.hadoop.mapred.lib`

`ChainReducer` is visible only from its trailing methods here. It supports `setReducer`, `addMapper`, `configure`, `reduce`, and `close`. The docs emphasize that reducer output is piped through zero or more mappers inside the reduce task. Chain elements can pass key/value objects by value or by reference; by-reference is an optimization but unsafe if downstream code mutates reusable objects. Per-element `JobConf` values take precedence over the enclosing job at task runtime.

`CombineFileInputFormat` is an abstract `FileInputFormat` that returns `CombineFileSplit` instances. It has protected sizing controls `setMaxSplitSize`, `setMinSplitSizeNode`, and `setMinSplitSizeRack`, plus pool creation by `List` or `PathFilter[]`. Its `getSplits(JobConf,int)` implementation groups blocks by node and rack while respecting pools; subclasses must implement `getRecordReader`.

`CombineFileSplit` implements `InputSplit` and serializes multiple `Path` entries, start offsets, lengths, locations, and the associated `JobConf`. It reports total length, per-path length/offset, path count, path arrays, host locations, and supports `readFields`, `write`, and `toString`. `CombineFileRecordReader` is a generic `RecordReader` wrapper that iterates the chunks in a `CombineFileSplit`, constructs per-chunk readers by reflection (`rrClass`, `rrConstructor`), tracks `idx`, `progress`, `curReader`, `FileSystem`, and exposes `initNextRecordReader`.

`MultipleInputs`, `DelegatingInputFormat`, and `DelegatingMapper` work together to route distinct input paths to distinct `InputFormat` and optional `Mapper` classes. `MultipleInputs.addInputPath` stores the route in `JobConf`; the delegating format and mapper then dispatch splits and records to the configured implementation.

`MultipleOutputFormat` is an abstract `FileOutputFormat` for deriving different output file names, keys, and values from a record. Important protected hooks are `generateLeafFileName`, `generateFileNameForKeyValue`, `generateActualKey`, `generateActualValue`, `getInputFileBasedOutputFileName`, and abstract `getBaseRecordWriter`. `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide concrete base writers for sequence and text files.

`MultipleOutputs` is the higher-level named-output helper. Static configuration methods register single or multi named outputs, inspect output format/key/value classes, and enable counters. Instance methods are used from mapper/reducer `configure`, `getCollector` returns named or multi-named `OutputCollector`s, `getNamedOutputs` enumerates channels, and `close` must close every opened output. Names are constrained to word-like letters/numbers and must not be `part`.

`InputSampler` writes partition files for `TotalOrderPartitioner`. It is a `Tool`/configured utility with samplers: `SplitSampler` takes first records from sampled splits, `IntervalSampler` emits at regular intervals, and `RandomSampler` samples probabilistically with a replacement/quota strategy. The docs warn that sampling every split can be expensive because it reads splits on the client.

Other `mapred.lib` helpers include `HashPartitioner`, `IdentityMapper`, `IdentityReducer`, `InverseMapper` (deprecated in favor of the newer mapreduce lib), `LongSumReducer` (deprecated in favor of new reduce lib), `KeyFieldBasedComparator`, `KeyFieldBasedPartitioner`, `FieldSelectionMapReduce`, `MultithreadedMapRunner`, `NLineInputFormat`, `NullOutputFormat`, `RegexMapper`, `TokenCountMapper`, and `TotalOrderPartitioner`. Field-based comparison/partitioning mimics a subset of Unix sort `-k`, `-n`, and `-r` behavior using configured key-field separators.

### `org.apache.hadoop.mapred.lib.aggregate`

`ValueAggregator` is the common contract for aggregators: `addNextValue`, `reset`, `getReport`, and `getCombinerOutput`. Implementations in this chunk include `DoubleValueSum`, `LongValueSum`, `LongValueMax`, `LongValueMin`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`.

`ValueAggregatorDescriptor` converts an input key/value pair into one or more aggregation id/value pairs. It exposes constants `TYPE_SEPARATOR` and `ONE`. `ValueAggregatorBaseDescriptor` provides built-in aggregation type names such as `UNIQ_VALUE_COUNT`, `LONG_VALUE_SUM`, `DOUBLE_VALUE_SUM`, `VALUE_HISTOGRAM`, `LONG_VALUE_MAX`, `LONG_VALUE_MIN`, `STRING_VALUE_MAX`, and `STRING_VALUE_MIN`, plus an `inputFile` field and helper methods `generateEntry`, `generateValueAggregator`, `generateKeyValPairs`, and `configure`.

`UserDefinedValueAggregatorDescriptor` loads user-provided descriptor classes from `JobConf`, creates instances, delegates `generateKeyValPairs`, and logs/describes configuration via `toString` and `configure`.

`ValueAggregatorJob` creates aggregate jobs and optional `JobControl` wrappers from command-line arguments and descriptor classes. `setAggregatorDescriptors` writes descriptor class configuration. `ValueAggregatorJobBase` is the shared mapper/reducer base holding `aggregatorDescriptorList` and common `configure`, `logSpec`, and `close` behavior. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` implement the generic map, combine, and reduce phases.

### `org.apache.hadoop.mapred.lib.db`

`DBConfiguration` defines all JDBC configuration property names and two `configureDB` overloads with and without credentials. The documented properties cover driver class, URL, username, password, input table, input field names, input conditions, order by, whole input query, input count query, input tuple class, output table, and output field names.

`DBInputFormat` implements `InputFormat` and `JobConfigurable`. Static `setInput` has two modes: table plus conditions/order/field names, or explicit select query plus count query. `getSplits` divides SQL rows into `DBInputSplit` ranges, `getRecordReader` returns `DBRecordReader`, and `getCountQuery` is protected for subclass customization.

`DBInputSplit` implements `InputSplit` for a row interval and serializes start/end indices with `readFields` and `write`. It returns no meaningful locality and reports row count as length. `DBRecordReader` reads SQL rows, emits `LongWritable` record numbers and `DBWritable` tuple values, and has an overridable `getSelectQuery`.

`DBOutputFormat` implements `OutputFormat`. It builds insert prepared statements via `constructQuery`, validates output specs, creates `DBRecordWriter`, and has `setOutput` for table and field names. `DBRecordWriter` writes records to JDBC and closes the statement/connection. `DBWritable` requires SQL `write(PreparedStatement)` and `readFields(ResultSet)`, and the documentation shows implementations also commonly implement Hadoop `Writable`.

### `org.apache.hadoop.mapred.pipes` and `org.apache.hadoop.mapred.tools`

`Submitter` is a `Configured` `Tool` and the main API/CLI entry point for Pipes jobs. It stores the executable URI in `JobConf`, toggles Java/native record reader, mapper, reducer, and writer roles, controls whether to keep the command file `downlink.data` for debugging, and exposes `runJob`, deprecated `submitJob`, lower-level `jobSubmit`, `run`, and `main`. Submitting a Pipes job modifies the supplied `JobConf`.

`MRAdmin` is a small administrative `Tool` with constructors, `run`, and `main`. The documented capability in this chunk is connecting to the `JobTracker` and refreshing service-level authorization policy.

### `org.apache.hadoop.mapreduce`

`Counter`, `CounterGroup`, and `Counters` are `Writable` state containers for job progress and application metrics. Many methods are synchronized. `Counter` stores name, display name, and long value with `increment`, `readFields`, and `write`. `CounterGroup` groups counters, implements `Iterable`, can find counters by name, read/write itself, report size, and merge another group. `Counters` finds counters by enum or group/name, lists group names, counts total counters, serializes the group/counter set, produces text, and merges another `Counters`.

`ID` is a `WritableComparable` base with protected `id`, separator constant, numeric comparison, equality/hash, and binary serialization. `JobID` extends the old `org.apache.hadoop.mapred.ID`, includes `jtIdentifier`, formatted job number, `forName` parsing, `appendTo`, and string form such as `job_200707121733_0003`.

`InputFormat` is abstract and defines `getSplits(JobContext)` and `createRecordReader(InputSplit, TaskAttemptContext)`. `InputSplit` is abstract and defines `getLength` and `getLocations`; locality is explicitly not required to be serialized. `RecordReader` is abstract/closeable with `initialize`, `nextKeyValue`, current key/value getters, progress, and close.

`Job` extends `JobContext` and is the job submitter-facing mutable wrapper. Constructors accept optional configuration and job name. Setters configure reducer count, working directory, input/output formats, mapper, jar, combiner, reducer, partitioner, map output key/value classes, final output key/value classes, sort comparator, grouping comparator, and job name. These setters throw `IllegalStateException` after submission. Runtime methods return tracking URL, map/reduce progress, completion/success status, task completion events, counters, and allow `submit`, `waitForCompletion`, `killJob`, `killTask`, and `failTask`. Nested `Job.JobState` has `DEFINE` and `RUNNING`.

`JobContext` is the read-only task-side job view. It wraps a final old `JobConf` and exposes configuration, job ID, reducer count, working directory, output and map-output classes, job name, input/mapper/combiner/reducer/output/partitioner classes, sort comparator, jar path, and grouping comparator. Protected configuration key constants record the class attributes used by `Job` setters/getters.

`Mapper` defines the new lifecycle: `setup`, repeated `map`, `cleanup`, and `run`. The default `map` is identity; overriding `run` allows custom task control. `MapContext` extends `TaskInputOutputContext` and delegates current key/value and iteration to a `RecordReader`, while `Mapper.Context` is the concrete nested context type.

`OutputFormat` validates output specs, creates `RecordWriter`, and supplies an `OutputCommitter`. `OutputCommitter` owns job/task setup, cleanup, needs-commit checks, commit, and abort for task output. `RecordWriter` writes key/value pairs and closes with task context. `Partitioner` maps intermediate key/value pairs to reduce partitions.

`ReduceContext` extends `TaskInputOutputContext` and consumes a `RawKeyValueIterator`, reduce input counter, `RecordWriter`, `OutputCommitter`, reporter/progressable, grouping comparator, and key/value classes. It can advance by unique key (`nextKey`) or raw key/value pair (`nextKeyValue`), expose current key/value, and provide a reusable `Iterable` of values for the current key. Nested `ValueIterable` and `ValueIterator` implement value iteration. The chunk starts `Reducer` with `setup` and `reduce`; the rest of the reducer contract is outside this chunk.

## Control Flow and Lifecycle

Old `mapred` helper control flow is configuration first, runtime dispatch second. `MultipleInputs`, `MultipleOutputs`, `DBInputFormat`, `DBOutputFormat`, `Submitter`, and aggregate jobs write metadata into `JobConf`; task-side objects read that metadata in `configure`, `getSplits`, `getRecordReader`, `getCollector`, or submission methods. Many APIs intentionally mutate the provided `JobConf`, so callers should not treat it as immutable.

Combined-file input flow is: input paths and optional pools are scanned, blocks are grouped into `CombineFileSplit`s based on max split, node minimum, rack minimum, and pool boundaries, then `CombineFileRecordReader` iterates each split path/chunk by constructing a chunk-specific record reader and advancing `idx`/`progress`.

Multiple-output flow is: register named output definitions before submit; instantiate `MultipleOutputs` in mapper/reducer `configure`; request collectors during map/reduce; emit additional records; call `close` from task close. Multi named outputs generate file names from the base output name plus user multi-name, and optional counters are incremented per named output.

Aggregate flow is: descriptors generate aggregation-prefixed keys in the mapper; combiner/reducer inspect the key prefix to choose a `ValueAggregator`; each value is added; the combiner emits compact intermediate values from `getCombinerOutput`; the reducer writes final `getReport` strings.

DB flow is: `configureDB` and `setInput`/`setOutput` write JDBC metadata; `DBInputFormat` counts rows and creates row-range splits; `DBRecordReader` issues split-limited queries and populates `DBWritable` values from result sets; `DBRecordWriter` uses prepared statements to insert each output record and closes resources at task end.

New `mapreduce` task flow is: `Job` is configured until `submit` or `waitForCompletion`; `InputFormat` validates/splits input and creates a `RecordReader`; `Mapper.run` calls `setup`, loops over `Context.nextKeyValue`, invokes `map`, then `cleanup`; intermediate records are partitioned, sorted, optionally combined, grouped by comparator, and delivered through `ReduceContext.getValues`; `OutputFormat` and `OutputCommitter` manage output writing and commit/abort.

## State and Persistence Behavior

Persistent wire formats are explicitly part of the API snapshot. `CombineFileSplit`, `DBInputSplit`, `Counter`, `CounterGroup`, `Counters`, `ID`, and `JobID` expose `readFields`/`write` methods. `Counters.write` documents a nested external format containing group names, display names, counter names, optional display names, and long values. `JobID` string parsing is part of compatibility via `forName`, but docs warn applications should not manually parse IDs.

Job configuration is the dominant state store. Old and new APIs store class names, paths, DB connection details, named outputs, Pipes execution flags, reducer count, comparators, partitioners, and key/value classes in `JobConf`/`Configuration`. `JobContext` in the new API keeps a final `JobConf`, while `Job` enforces a state transition from mutable definition to submitted/running by throwing on setters after submit.

Runtime state includes open record readers/writers, JDBC connections/statements/result sets, output commit temporary directories, named-output collectors, aggregation descriptor lists, counters, and current map/reduce key/value objects. Several reduce APIs warn that value objects are reused, so retaining references across iterations is unsafe.

External persistence/integration points include HDFS or other `FileSystem` outputs, partition files for `TotalOrderPartitioner`, SQL tables for DB formats, Pipes executable URIs and optional task command files, JobTracker state, and task output commit directories.

## Dependencies and Integration Points

This chunk depends heavily on Hadoop core types: `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `RecordWriter`, `OutputCollector`, `Reporter`, `MapReduceBase`, `Mapper`, `Reducer`, `Partitioner`, `FileOutputFormat`, `FileSystem`, `Path`, `PathFilter`, `Writable`, `WritableComparable`, `Text`, `LongWritable`, `RawComparator`, `Progressable`, `GenericOptionsParser`, `JobClient`, `RunningJob`, `JobControl`, `TaskCompletionEvent`, `TaskAttemptID`, `TaskAttemptContext`, `TaskInputOutputContext`, and `StatusReporter`.

Java dependencies include reflection (`Class`, `Constructor`), collections (`List`, `ArrayList`, `Iterator`, `Iterable`, `Set`, `TreeMap`, `Collection`), I/O (`DataInput`, `DataOutput`, `IOException`, `Closeable`), SQL (`Connection`, `PreparedStatement`, `ResultSet`, `SQLException`), formatting (`NumberFormat`), and logging via `org.apache.commons.logging.Log`.

Important external integration surfaces are JDBC drivers/databases, Hadoop Pipes native executables, JobTracker administrative RPC, file-based output committers, partition files consumed by total-order partitioning, and mapred/mapreduce compatibility classes. The new `mapreduce` classes still bridge to old `mapred` internals in this snapshot, for example `JobContext` stores `JobConf`, `JobID` extends `org.apache.hadoop.mapred.ID`, `Job.getTaskCompletionEvents` returns old `TaskCompletionEvent[]`, and `ReduceContext` consumes `org.apache.hadoop.mapred.RawKeyValueIterator`.

## Risks and Edge Cases

The chunk documents several API risks:

- Object reuse: `ReduceContext.getValues` reuses value objects; storing references beyond the iteration can corrupt user results.
- By-reference chain passing: `ChainReducer` and chained mappers can avoid serialization by passing references, but this is unsafe if any mapper/reducer mutates objects under by-value assumptions.
- Lifecycle leaks: `MultipleOutputs.close`, `RecordReader.close`, `RecordWriter.close`, JDBC writer/reader close, and output committer cleanup/abort are required for correctness and resource release.
- Configuration mutation: `Submitter.runJob`, `submitJob`, Pipes flags, multiple input/output registration, DB configuration, and `Job` setters all mutate job configuration; sharing a mutable `JobConf` across jobs can leak settings.
- Late mutation: `Job` setters throw once submitted, so tests and callers must configure all classes, comparators, and output types before `submit`/`waitForCompletion`.
- SQL correctness/security: `DBInputFormat` and `DBOutputFormat` build SQL from table names, conditions, field names, and custom queries. Bad quoting, unsafe user strings, missing count queries, driver availability, transaction handling, or unsupported `LIMIT/OFFSET` behavior can break jobs.
- Sampling cost and skew: `InputSampler.RandomSampler` can read every split on the client; split/interval sampling may produce poor partitions for skewed or sorted data.
- Multi-output naming: named outputs reject reserved or non-word names; multi-name construction and input-file-based naming can cause unexpected file layouts or collisions if not tested.
- Combine file splits: combining blocks across files/racks improves small-file efficiency but can reduce locality or break record readers that assume one file per split unless designed for `CombineFileSplit`.
- Deprecated old helpers: `InverseMapper`, `LongSumReducer`, and Pipes `submitJob` point to newer alternatives; compatibility code should verify both old and new APIs where applicable.
- Threading: `MultithreadedMapRunner` introduces mapper concurrency; mapper implementations and output collectors must be safe under its execution model.
- Counter synchronization: many counter methods are synchronized, but collection iteration and merges still need validation under concurrent updates.

## Test Signals

Useful tests for code behind this API snapshot would include:

- JDiff/schema tests ensuring the XML still exposes documented public/protected classes, methods, fields, exceptions, synchronization flags, and deprecation text for the line span.
- Serialization round trips for `CombineFileSplit`, `DBInputSplit`, `Counter`, `CounterGroup`, `Counters`, `ID`, and `JobID`, including `JobID.forName` malformed-string rejection.
- Combine-file split construction tests for max split size, min node/rack sizes, pool isolation, locality reporting, and `CombineFileRecordReader` progress across multiple paths.
- Multiple input tests verifying path-to-input-format and path-to-mapper delegation.
- Multiple output tests for named and multi named outputs, invalid/reserved names, counter enablement, collector reuse, file naming hooks, and required close behavior.
- Aggregate tests for every built-in aggregator, combiner output compatibility with reducer input, descriptor configuration, user-defined descriptor loading, histogram details, and unique-value max-item behavior.
- DB format tests with an embedded JDBC database covering table-based input, explicit query input, split boundaries, count queries, insert query generation with named and null fields, `DBWritable` read/write, and resource closing on success/failure.
- Pipes submitter tests that assert executable URI and Java/native component flags are written to `JobConf`, command-file retention is honored, and `runJob` mutates/submits jobs as documented.
- New `mapreduce` API tests for job setter pre-submit behavior, post-submit `IllegalStateException`, mapper lifecycle order, record reader initialization and close, output spec validation, output committer commit/abort paths, partitioner bounds, reduce value reuse behavior, and counter merging.

## Cross-Chunk Notes

This chunk begins after the start of `ChainReducer`; upstream chunks contain the class declaration and `setReducer` prelude. It ends immediately after the first `Reducer.reduce` signature; downstream chunks should capture the rest of `Reducer`, its nested `Context`, and subsequent `org.apache.hadoop.mapreduce` APIs. The merge lane should avoid treating this chunk as a complete source-file report and should reconcile duplicate package-level themes with adjacent chunks from the same XML file.
