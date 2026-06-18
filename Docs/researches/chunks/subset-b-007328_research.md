# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 50146-53832

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.20.1. It starts at the tail of the `org.apache.hadoop.mapreduce.InputFormat` documentation, then covers most of the public "new" `org.apache.hadoop.mapreduce` API surface, the `org.apache.hadoop.mapreduce.lib.*` helper packages for input, map, output, partition, and reduce, and the start of `org.apache.hadoop.tools`.

The source is generated API metadata rather than implementation code. The important research surface is the compatibility contract: packages, class names, inheritance, implemented interfaces, constructors, method signatures, declared exceptions, nested classes, fields, visibility/static/final/abstract/synchronized flags, deprecation markers, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.mapreduce` portion defines the 0.20-era MapReduce client and task API. It exposes the job configuration/submission object (`Job`), read-only job/task contexts, mapper/reducer lifecycle classes, input/output abstractions, partitioning, split and record reader/writer contracts, task status/counter reporting, and the ID types used to identify jobs, tasks, and attempts.

The `org.apache.hadoop.mapreduce.lib.input` and `lib.output` portions provide standard file-based implementations and helpers. They translate configured paths and file system metadata into input splits and record readers, and translate task output into committed job output under safe temporary directories.

The `lib.map`, `lib.partition`, and `lib.reduce` portions provide small reusable MapReduce components: key/value inversion, multithreaded map execution, token counting, hash partitioning, and integer/long sum reducers.

The `org.apache.hadoop.tools` portion exposes distributed filesystem tools and log utilities: recursive property changes (`DistCh`), distributed copy (`DistCp`), Hadoop archive creation (`HadoopArchives`), and log archiving/analysis (`Logalyzer` plus nested comparator/mapper helpers).

## Important APIs, Types, and Functions

### Core MapReduce API

- `InputFormat` is only represented by trailing documentation in this chunk. Its documented contract is to validate input, split logical input into `InputSplit`s, and create `RecordReader`s that preserve record boundaries for mapper tasks.
- `InputSplit` is an abstract mapper work unit. `getLength()` reports split size for scheduling/sorting, and `getLocations()` reports data-local host names. Both can throw `IOException` and `InterruptedException`.
- `Job` extends `JobContext` and is the user-facing job definition, submission, control, and monitoring handle. Constructors accept default configuration, a `Configuration`, or a `Configuration` plus job name. Setters configure reduce count, working directory, input/output format, mapper, combiner, reducer, partitioner, map/final key and value classes, sort/grouping comparators, job name, and jar. Runtime APIs expose jar path, tracking URL, map/reduce progress, completion/success state, counters, task completion events, task kill/fail operations, `submit()`, and `waitForCompletion(boolean)`.
- `Job.JobState` is an enum with `DEFINE` and `RUNNING`, plus standard `values()` and `valueOf(String)`.
- `JobContext` is the read-only job view supplied to tasks. It stores protected final `org.apache.hadoop.mapred.JobConf conf` and exposes configuration, job ID, reduce count, working directory, output/map-output classes, job name, input/mapper/combiner/reducer/output/partitioner classes, sort/grouping comparators, and jar path. Protected configuration-key fields name the class attributes used under the old `JobConf` bridge.
- `JobID`, `TaskID`, and `TaskAttemptID` extend the older `org.apache.hadoop.mapred.ID` base and provide constructors from structured parts, string rendering/parsing via `forName`, comparison, equality/hash, `appendTo`, and `Writable`-style `readFields`/`write`. Their docs define canonical string forms such as `job_...`, `task_..._m_...`, and `attempt_..._m_..._0`.
- `TaskAttemptContext` extends `JobContext` and implements `Progressable`. It exposes the task attempt ID, status get/set, and progress heartbeat reporting.
- `TaskInputOutputContext` extends `TaskAttemptContext` and adds task I/O operations: abstract `nextKeyValue()`, current key/value accessors, `write(key,value)`, counter lookup by enum or group/name, status, progress, and output committer access.
- `MapContext` extends `TaskInputOutputContext`, binds a `RecordReader`, `RecordWriter`, `OutputCommitter`, `StatusReporter`, and `InputSplit`, and adds `getInputSplit()`.
- `ReduceContext` extends `TaskInputOutputContext`, binds a `RawKeyValueIterator`, grouped-key counter, writer, committer, reporter, comparator, and key/value classes. It exposes `nextKey()`, `nextKeyValue()`, current key/value, and `getValues()`, where returned value objects are reused. Protected nested `ValueIterable` and `ValueIterator` implement the grouped value iteration contract.
- `Mapper` defines protected `setup`, `map`, and `cleanup` hooks plus public `run`. The default map behavior is an identity function; docs define the lifecycle as setup, map for every input key/value pair, then cleanup.
- `Reducer` mirrors the task lifecycle with protected `setup`, `reduce`, and `cleanup` hooks plus public `run`. Its documentation describes shuffle, sort, secondary sort via sort/grouping comparators, reduce invocation per grouped key, and the fact that reducer output is not re-sorted.
- `Mapper.Context` and `Reducer.Context` are public nested context types extending `MapContext` and `ReduceContext`.
- `OutputCommitter` is the abstract commit protocol for setup/cleanup, task setup, `needsTaskCommit`, `commitTask`, and `abortTask`.
- `OutputFormat` is the abstract output-specification contract: create a `RecordWriter`, validate job output specs, and provide an `OutputCommitter`.
- `RecordReader` is an abstract `Closeable` that initializes from a split/context, advances key/value pairs, returns current key/value, reports progress, and closes.
- `RecordWriter` writes output key/value pairs and closes with task context.
- `Partitioner` maps an intermediate key/value pair and reducer count to a reducer partition.
- `StatusReporter` abstracts counter lookup, progress, and status updates.

### Standard Input Helpers

- `FileInputFormat` is the base for file-backed input formats. It controls minimum and maximum split size, splitability, input path filters, input path setters/adders/getters, file status listing, split generation, split-size computation, and block-location lookup. `listStatus` and `getSplits` can throw `IOException`; path setters can throw `IOException`.
- `FileSplit` extends `InputSplit` and implements `Writable`. It persists path, byte start, byte length, and host locations; exposes path/start/length/location getters, `toString`, `write`, and `readFields`.
- `InvalidInputException` wraps a list of input problems without copying it, exposes the problem list, and concatenates problem messages for `getMessage()`.
- `LineRecordReader` reads text files as offset keys (`LongWritable`) and line values (`Text`), with split initialization, key/value advancement, progress, and synchronized close.
- `TextInputFormat` extends `FileInputFormat` for plain text, uses line records, and overrides splitability so stream-compressed files can remain unsplit.
- `SequenceFileInputFormat` extends `FileInputFormat` for `SequenceFile`s. It creates `SequenceFileRecordReader`s, can impose a format minimum split size, and overrides `listStatus`.
- `SequenceFileRecordReader` reads sequence-file records from a split, stores protected `Configuration conf`, exposes current key/value, progress within the byte range, and synchronized close.

### Standard Map, Partition, Reduce, and Output Helpers

- `InverseMapper` swaps input keys and values in `map`.
- `MultithreadedMapper` runs application mapper logic through a thread pool. Static methods get/set thread count and get/set the wrapped mapper class. The docs warn that wrapped mappers must be thread-safe and cite a default of 10 threads.
- `TokenCounterMapper` tokenizes `Text` values and emits each token with count 1.
- `HashPartitioner` partitions keys by `Object.hashCode()` modulo reducer count.
- `IntSumReducer` and `LongSumReducer` sum iterable numeric values into integer or long totals.
- `FileOutputCommitter` implements `OutputCommitter` for filesystem output. It creates and deletes the temporary root, treats task setup as no-op, moves task work files into the job output directory on commit, deletes work directories on abort, checks whether task output exists via `needsTaskCommit`, and exposes the work path. `TEMP_DIR_NAME` names the temporary output directory.
- `FileOutputFormat` is the base for file-backed output formats. It controls output compression enablement and codec class, validates output specs, sets/gets output path, computes task work output paths, creates unique task file names and default work files, and returns a synchronized output committer.
- `NullOutputFormat` consumes output with no persisted records and supplies no-op spec/committer behavior.
- `SequenceFileOutputFormat` writes sequence files and controls `SequenceFile.CompressionType`, defaulting to record compression according to the docs.
- `TextOutputFormat` writes plain text. Its protected static `LineRecordWriter` writes key/value pairs to a `DataOutputStream`, supports a configurable separator, synchronizes `write` and `close`, and stores protected `out`.

### Tools

- `DistCh` extends `DistTool` and exposes `run(String[])` and `main(String[])` for recursive owner, group, and permission changes.
- `DistCp` implements `Tool`, stores a `Configuration`, exposes static `copy(Configuration, String, String, Path, boolean, boolean)`, command-line `run`, `main`, static `getRandomId`, public `LOG`, and nested `DuplicationException` with public `ERROR_CODE`. Its docs describe recursive copy between filesystems by listing sources, distributing map input, copying files in mappers, and using an empty reduce.
- `HadoopArchives` implements `Tool`, stores configuration, exposes `archive(List, String, Path)`, command-line `run`, and `main` for creating Hadoop archive (`har`) files from source paths into a destination.
- `Logalyzer` exposes `doArchive`, `doAnalyze`, and `main` for archiving and analyzing logs with grep/sort parameters.
- `Logalyzer.LogComparator` extends `Text.Comparator` and implements `Configurable`, comparing raw UTF-8 log keys with configuration-aware column/sort behavior.
- `Logalyzer.LogRegexMapper` extends the old `mapred.MapReduceBase` and implements old `mapred.Mapper`, configuring from `JobConf` and extracting regex matches from `Text` values.

## Control Flow

Job setup flows through mutable `Job` setters while the job remains in `DEFINE` state. The setters write configuration into the underlying `JobConf` bridge. Once `submit()` or `waitForCompletion()` transitions the job into running state, the docs state that configuration setters throw `IllegalStateException`. Runtime calls then poll progress, counters, task events, and completion state, or issue kill/fail operations through task attempt IDs.

Input flow begins with an `InputFormat`. For file inputs, `FileInputFormat` reads configured input paths, applies an optional `PathFilter`, lists file statuses, validates that input exists, computes split sizes from block size plus min/max bounds, maps split offsets to block locations, and creates `FileSplit`s. Each map task receives an `InputSplit`; the task-specific `RecordReader` initializes on that split and repeatedly advances key/value records.

Mapper flow is explicit: the framework constructs a `Mapper.Context`, calls `setup(context)`, loops through `nextKeyValue()`, calls `map(currentKey,currentValue,context)` for each record, and finally calls `cleanup(context)`. `TaskInputOutputContext.write` forwards mapper output to the configured `RecordWriter`; `getCounter`, `progress`, and `setStatus` forward through `StatusReporter`.

Shuffle/reduce flow starts from sorted map outputs represented by `RawKeyValueIterator`. `ReduceContext.nextKey()` advances to a unique grouped key; `getValues()` returns an iterable that reuses the same value instance while walking values for that key. `Reducer.run` invokes setup, then `reduce(key, values, context)` for each grouped key, and then cleanup. Secondary sort is achieved by sorting with the full composite key while grouping with a comparator that ignores the secondary component.

Output flow begins when `OutputFormat.checkOutputSpecs` validates the destination before submission. Each task obtains a `RecordWriter` and an `OutputCommitter`. `FileOutputCommitter` creates a temporary root at job setup, lets tasks write into work directories, checks whether a task needs commit, moves successful attempt output to the final job output directory, aborts failed attempts by deleting work output, and cleans up temporary state at job completion.

Tool flow is command-line and MapReduce-backed. `DistCp`, `DistCh`, `HadoopArchives`, and `Logalyzer` parse arguments in `run`/`main`, use `Configuration` and `FileSystem` paths, and launch MapReduce work where needed. `DistCp.copy` is also exposed as a programmatic entry point for recursive copy with optional source-list and read-failure handling.

## State and Persistence Behavior

This XML file persists API metadata for compatibility comparison, not runtime state. The APIs in this range nevertheless define durable or process-visible state contracts.

`Job`, `JobContext`, and task contexts persist job configuration through `Configuration`/`JobConf`. The configured mapper/reducer/input/output/partitioner classes, comparator classes, key/value classes, jar path, working directory, paths, compression settings, and status strings are external configuration contracts.

`JobID`, `TaskID`, `TaskAttemptID`, and `FileSplit` define binary persistence through `DataInput`/`DataOutput` and string persistence through canonical ID formats. Changes to token prefixes (`JOB`, `TASK`, `ATTEMPT`), number formatting, map/reduce ordering, or `forName` parsing would break logs, job history, RPC payloads, and user code.

`InputSplit.getLocations()` and `FileSplit` host arrays persist data-locality hints that feed scheduler placement. `FileSplit` also persists byte offsets and lengths, so record readers must respect split boundaries without dropping or duplicating records at split edges.

`RecordReader` and `ReduceContext` reuse current key/value instances by contract. Applications retaining references beyond the current iteration can observe mutation. This is especially explicit for `ReduceContext.getValues()`.

`StatusReporter` and task contexts maintain counters, status text, and progress heartbeats. These are externally visible in job monitoring and can affect timeout/liveness behavior.

`FileOutputFormat` stores output-path and compression configuration in the job. `FileOutputCommitter` persists task output first under temporary work paths and then promotes output to the final directory. The temporary directory name is part of the output layout contract.

`LineRecordReader`, `SequenceFileRecordReader`, `TextOutputFormat.LineRecordWriter`, and `SequenceFileOutputFormat` persist records into Hadoop's writable/text/sequence-file formats. Text output writes key/value pairs through a `DataOutputStream`; sequence output persists key/value classes and optional compression type.

The tools persist distributed filesystem changes: `DistCh` mutates file metadata, `DistCp` copies files and may write logs, `HadoopArchives` creates archive files and index data, and `Logalyzer` creates archived and analyzed log outputs.

## Dependencies and Integration Points

- Java dependencies include `IOException`, `InterruptedException`, `ClassNotFoundException`, `IllegalStateException`, `DataInput`, `DataOutput`, `DataOutputStream`, collections, iterators, enums, and object `hashCode`.
- Hadoop configuration types (`Configuration`, `Configurable`, and old `JobConf`) are central to job setup, task contexts, file input/output paths, compression options, mapper selection, and tool configuration.
- Hadoop filesystem types (`Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `PathFilter`) integrate with `FileInputFormat`, `FileSplit`, `FileOutputFormat`, `FileOutputCommitter`, `DistCp`, `HadoopArchives`, and `Logalyzer`.
- Hadoop serialization and data types include `Writable`, `LongWritable`, `Text`, `SequenceFile`, `SequenceFile.CompressionType`, `RawComparator`, and raw `RawKeyValueIterator`.
- The new `mapreduce` API bridges to old `mapred` classes in multiple places: `JobConf`, `ID`, `TaskCompletionEvent`, `FileAlreadyExistsException`, `RawKeyValueIterator`, and the old `Mapper`/`MapReduceBase` used by `Logalyzer.LogRegexMapper`.
- Compression integrates through `org.apache.hadoop.io.compress.CompressionCodec` and output compression configuration.
- Monitoring integrates through counters, progress/status reporters, tracking URLs, task completion events, and kill/fail control operations.
- Tool classes integrate with `org.apache.hadoop.util.Tool`, `DistTool`, Commons Logging, and MapReduce jobs used internally for distributed file operations.

## Risks and Edge Cases

- The chunk starts inside `InputFormat` documentation, so the complete class signature and earlier methods require an adjacent chunk.
- JDiff metadata omits method bodies. Exact configuration keys, path escaping, split computation math, output commit rename semantics, comparator behavior, and tool argument parsing require implementation-source review.
- Raw `java.lang.Class` method signatures erase generic type information. API compatibility must preserve the erased contract even if source generics are improved elsewhere.
- `Job` setters are documented to throw after submission. Race conditions around concurrent submit and configuration mutation are implementation-dependent and should be pinned by tests.
- `JobContext` uses old `JobConf` internally, so compatibility depends on new API setters and old `mapred` configuration keys staying aligned.
- `TaskInputOutputContext.nextKeyValue()` documentation says "returning null if at end" although the signature returns boolean; downstream documentation or generated docs may confuse implementers.
- `MapContext`, `ReduceContext`, and nested context constructors expose many framework internals. Signature drift can break custom tests, subclasses, or framework adapters even when ordinary users do not construct them directly.
- Value object reuse in `ReduceContext.getValues()` is a common source of subtle application bugs when reducers store references instead of copying values.
- `InputSplit.getLocations()` does not serialize locality by default; concrete split types must decide what host data is durable.
- `FileInputFormat` must handle missing inputs, empty files, directories, recursive/globbed paths, path filters, unsplittable stream-compressed files, min/max split sizes, and stale block locations.
- `InvalidInputException` does not copy its problem list. External mutation after construction can change exception state and message output.
- `LineRecordReader` must handle split boundaries, CR/LF variants, final lines without terminators, very long lines, compressed streams, and progress calculations near EOF.
- `SequenceFileInputFormat` and `SequenceFileRecordReader` must respect sync markers and avoid starting in the middle of a record when processing split byte ranges.
- `FileOutputCommitter` commit/abort semantics are sensitive to speculative execution and filesystem rename atomicity. Duplicate successful attempts, partial commits, and cleanup failures can corrupt or orphan output.
- `FileOutputFormat.checkOutputSpecs` must fail before submission when output exists, but races with concurrent creators remain possible.
- `getUniqueFile` is synchronized and task-ID based. Incorrect formatting or task attempt handling can collide output filenames, especially with side-effect files.
- `TextOutputFormat.LineRecordWriter.write` is synchronized, but writing mutable key/value objects while another thread mutates them can still produce inconsistent output.
- `MultithreadedMapper` requires user mapper thread-safety and has shared context interactions; counters, writer calls, and record reader access need careful synchronization in implementation.
- `HashPartitioner` must handle negative hash codes and zero reducer counts correctly; modulo bugs can route keys outside valid partitions.
- Sum reducers must handle null values, overflow, and type mismatches according to actual writable types used by callers.
- `DistCp` has many operational risks not visible from signatures: duplicate sources, destination overwrite behavior, partial copy cleanup, read-failure ignore semantics, log path conflicts, and cross-filesystem metadata preservation.
- `HadoopArchives` must maintain archive index consistency and validate archive names/destinations.
- `Logalyzer` mixes old `mapred` APIs with raw text comparators and configurable sort/grep parameters; malformed regexes, column separators, and sort columns need explicit validation.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility tests for every public/protected class, nested class, constructor, method, field, declared exception, deprecation marker, and visibility/static/final/abstract/synchronized flag in this line range.
- `Job` lifecycle tests covering constructor variants, all configuration setters/getters through `JobContext`, illegal setter calls after submit, jar lookup, progress polling, counters, task events, task kill/fail, `submit`, and `waitForCompletion`.
- ID tests for `JobID`, `TaskID`, and `TaskAttemptID`: structured constructors, canonical `toString`, `forName` success/failure, compare ordering, equality/hash, append helpers, and read/write round trips.
- Mapper/reducer lifecycle tests proving setup/map-or-reduce/cleanup order, default identity behavior, overridden `run` behavior, context write/counter/status/progress forwarding, and exception propagation.
- `ReduceContext` tests for grouped-key iteration, value reuse semantics, `nextKey` versus `nextKeyValue`, and secondary-sort comparator behavior.
- `InputSplit` and `FileSplit` tests for length/location reporting, path/start/length preservation, serialization round trips, null host arrays, and string rendering.
- `FileInputFormat` tests for input path set/add/get with comma-separated and array paths, path filters, min/max split sizes, block-index lookup, unsplittable files, empty/missing input, directory handling, and split locality.
- `LineRecordReader` tests for split-start alignment, CR/LF handling, EOF without newline, long lines, compressed unsplittable input through `TextInputFormat`, progress, and synchronized close.
- `SequenceFileInputFormat` and `SequenceFileRecordReader` tests for sync marker alignment, split boundaries, current key/value reuse, progress, close, and minimum split size.
- `OutputFormat`/`OutputCommitter` tests for output-spec validation, existing destination failure, work path creation, side-effect file path generation, unique file names, commit, abort, cleanup, speculative attempt isolation, and filesystem rename failure.
- `TextOutputFormat` and `SequenceFileOutputFormat` tests for plain text serialization, null key/value behavior, separator behavior, compression flag/codecs, sequence compression type get/set, and writer close behavior.
- Utility component tests for `InverseMapper`, `TokenCounterMapper`, `MultithreadedMapper` thread count/class configuration and thread-safety assumptions, `HashPartitioner` negative hash values, and int/long sum reducers including overflow boundaries.
- Tool tests for `DistCh`, `DistCp`, `HadoopArchives`, and `Logalyzer` command-line argument validation, configuration propagation, failure codes, duplicate-input handling, partial-output cleanup, generated logs/archives, comparator ordering, regex extraction, and old/new MapReduce API interoperability.
