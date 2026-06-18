# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.2.xml lines 50040-53959

## Scope

This chunk is the final segment of the generated JDiff public API snapshot for Hadoop 0.20.2. It is XML API metadata rather than Java implementation code. The range begins inside the tail of `org.apache.hadoop.mapreduce.Counters`, then covers the main `org.apache.hadoop.mapreduce` job, context, ID, mapper, reducer, input, output, partitioning, and helper APIs. It also records `org.apache.hadoop.mapreduce.lib.input`, `lib.map`, `lib.output`, `lib.partition`, `lib.reduce`, and the start-to-finish public API entries for several `org.apache.hadoop.tools` utilities before closing the XML document.

The XML records compatibility surface: package and class names, inheritance, implemented interfaces, constructors, method signatures, parameters, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and embedded Javadoc. Runtime behavior below is inferred from signatures and documentation because this source does not include method bodies.

## Purpose and Major API Surface

The visible `Counters` tail exposes synchronized aggregate and serialization behavior: total counter count, `write(DataOutput)`, `readFields(DataInput)`, `toString()`, `incrAllCounters(Counters)`, `equals(Object)`, and `hashCode()`. Its documented external format is a collection of groups, each with display name, counters, optional display names, and values.

`ID` is the abstract base identifier for `JobID`, `TaskID`, and `TaskAttemptID`. It implements `WritableComparable`, stores a protected integer `id`, exposes `getId()`, `toString()`, `equals`, `hashCode`, numeric `compareTo(ID)`, and `readFields`/`write` serialization, and defines a protected separator character.

`InputFormat` and `InputSplit` define the new MapReduce input contract. `InputFormat.getSplits(JobContext)` validates and logically splits job input, while `createRecordReader(InputSplit, TaskAttemptContext)` creates readers for individual splits. `InputSplit` exposes split length and host locations for scheduling and locality; the Javadoc stresses that splits are logical byte-oriented views and record boundaries are handled by `RecordReader`.

`Job` is the submitter-facing mutable job configuration and control object. Constructors accept no arguments, a `Configuration`, or a `Configuration` plus job name. Before submission it configures reduce count, working directory, input/output formats, mapper, combiner, reducer, partitioner, key/value classes, sort and grouping comparators, job name, and job jar. After submission it exposes tracking URL, map/reduce progress, completion/success state, kill/fail operations for jobs and tasks, task completion events, counters, `submit()`, and `waitForCompletion(boolean)`. `Job.JobState` records `DEFINE` and `RUNNING`.

`JobContext` is the task-facing read-only job view. It wraps a `JobConf` and `JobID`, exposes configuration, job ID, reduce count, working directory, output and map-output key/value classes, job name, input/mapper/combiner/reducer/output/partitioner classes, sort and grouping comparators, and jar path. Its public string fields define configuration attribute names for input format, mapper, combiner, reducer, output format, and partitioner.

`JobID`, `TaskID`, and `TaskAttemptID` are immutable public identifiers extending the older `org.apache.hadoop.mapred.ID` base. They provide component constructors, no-arg constructors for deserialization, accessors, `equals`, `hashCode`, `compareTo`, `toString`, protected `appendTo(StringBuilder)`, static `forName(String)` parsers, and `readFields`/`write` methods. `JobID` carries a job-tracker identifier; `TaskID` carries a `JobID` plus map/reduce kind; `TaskAttemptID` carries a `TaskID` plus attempt number.

`MapContext`, `Mapper`, and `Mapper.Context` define mapper execution. `MapContext` extends `TaskInputOutputContext` and adds access to the input split while delegating current key/value and cursor advancement to the record reader. `Mapper` exposes the standard lifecycle methods `setup`, `map`, `cleanup`, and `run`, with default mapper behavior documented as processing each input pair through the map method.

`OutputCommitter`, `OutputFormat`, `RecordWriter`, and `Partitioner` define output and shuffle contracts. `OutputCommitter` controls job/task setup, task commit checks, commit, abort, and job cleanup. `OutputFormat` validates output specs, creates a `RecordWriter`, and supplies an `OutputCommitter`. `RecordWriter` writes key/value output pairs and closes with a task context. `Partitioner.getPartition` assigns a key/value pair to a reduce partition.

`RecordReader`, `ReduceContext`, `Reducer`, `Reducer.Context`, `StatusReporter`, `TaskAttemptContext`, and `TaskInputOutputContext` define task execution. `RecordReader` initializes from a split and task context, advances key/value records, exposes current key/value, progress, and close. `ReduceContext` wraps reduce-side merged input, grouping comparator, counters, output writer, committer, and status reporter; nested `ValueIterable` and `ValueIterator` expose values for the current key. `Reducer` exposes setup, reduce, cleanup, and run lifecycle hooks. `StatusReporter` supplies counters, progress, and status. `TaskAttemptContext` and `TaskInputOutputContext` expose attempt identity, status/progress, current input, output writes, counters, and committer access.

The `org.apache.hadoop.mapreduce.lib.input` package provides file-based inputs. `FileInputFormat` configures input paths, path filters, min/max split sizes, splitability, file listing, split generation, split-size computation, block index lookup, and input path getters/setters/adders. `FileSplit` is a writable split containing file path, byte start, length, and host locations. `InvalidInputException` aggregates input validation problems. `LineRecordReader` reads lines as `LongWritable` offsets and `Text` values. `TextInputFormat` creates line readers and handles splitability. `SequenceFileInputFormat` and `SequenceFileRecordReader` read Hadoop `SequenceFile`s and report split progress.

The `org.apache.hadoop.mapreduce.lib.map` package contains small mapper helpers. `InverseMapper` swaps input keys and values. `MultithreadedMapper` runs an application mapper through a thread pool and exposes static configuration helpers for thread count and mapper class. `TokenCounterMapper` tokenizes input values and emits tokens with count one.

The `org.apache.hadoop.mapreduce.lib.output` package contains file output behavior. `FileOutputCommitter` creates temporary output roots, handles task work directories, promotes successful task output, aborts failed task output, checks whether commit is needed, and exposes the work path. `FileOutputFormat` configures output compression, compressor class, output path, work output path, unique task filenames, default work files, and output committer creation. `NullOutputFormat` discards all output. `SequenceFileOutputFormat` writes `SequenceFile`s and configures `SequenceFile.CompressionType`. `TextOutputFormat` writes text output through the synchronized nested `LineRecordWriter`, which owns a `DataOutputStream`.

`HashPartitioner` partitions keys by `Object.hashCode()`. `IntSumReducer` and `LongSumReducer` are concrete reducers that sum iterable numeric values for each key.

The `org.apache.hadoop.tools` entries expose command-line and MapReduce utilities. `DistCh` recursively changes file properties such as owner, group, and permissions. `DistCp` implements `Tool` for recursive filesystem copies and exposes configuration accessors, a static `copy(...)` helper, `run`, `main`, `getRandomId`, public logging, and `DuplicationException` for duplicate source files. `HadoopArchives` implements `Tool` for creating Hadoop archives with `archive`, `run`, and `main`. `Logalyzer` archives and analyzes Hadoop logs through `doArchive`, `doAnalyze`, and `main`; nested `LogComparator` is configurable and compares log keys as `Text` bytes, while nested `LogRegexMapper` is an old `mapred` mapper that extracts regex matches.

## Control Flow and Behavioral Contracts

Job setup flow is configuration-first. Callers construct a `Job`, set input/output formats, mapper/reducer/combiner/partitioner classes, key/value classes, comparators, job name, working directory, reduce count, and output/input paths through helper formats. Mutating setters are documented to throw `IllegalStateException` after submission, making the transition from `DEFINE` to `RUNNING` a public control boundary.

Submission and monitoring flow runs through `submit()` or `waitForCompletion(boolean)`. Once submitted, callers poll map and reduce progress, completion, success, counters, and task completion events; they can kill the job or kill/fail individual task attempts. `waitForCompletion` optionally prints progress and returns job success.

Input flow starts with `InputFormat.getSplits`, where configured paths and format-specific rules produce logical `InputSplit`s. The framework assigns splits to mappers using length and location data, creates a `RecordReader`, calls `initialize`, and repeatedly calls `nextKeyValue` until false. `MapContext` exposes the split and current record to mapper code.

Mapper control flow is lifecycle-based: `setup(Context)` runs once, `map(KEYIN, VALUEIN, Context)` runs for each input pair, `cleanup(Context)` runs once, and `run(Context)` coordinates the default loop. Overriding `run` gives full control but also requires preserving expected setup, iteration, cleanup, progress, and exception behavior.

Shuffle and reduce flow is grouped-key based. Map output is partitioned by `Partitioner`, sorted by the configured sort comparator, grouped by the grouping comparator, and passed to `Reducer.reduce` once per key group. `ReduceContext.nextKey()` and `nextKeyValue()` move through grouped reduce input; `getValues()` returns an iterable that reuses value objects for the current key.

Output flow is guarded by specs and commit protocol. `OutputFormat.checkOutputSpecs` validates the job output configuration. Tasks obtain a `RecordWriter` and write key/value pairs to attempt-specific work output. The committer decides whether there is work to commit, promotes successful task output, aborts failed output, and cleans up job-level temporary state.

File input control flow expands configured input paths, applies optional filters, validates non-empty inputs, computes split sizes from format minimum, configured min/max, and block size, finds block locality, and emits `FileSplit` objects. Subclasses can override splitability, minimum split size, list status, and record reader creation.

File output control flow uses static configuration on `Job` for compression, codecs, output path, and sequence-file compression type. Task filenames are generated from task IDs plus map/reduce markers and extensions; work paths live under temporary task directories so failed and speculative attempts can be discarded.

Identifier flow depends on stable parse, format, comparison, and serialization. `forName(String)` constructs IDs from public string forms, null inputs produce null per Javadoc, malformed strings raise `IllegalArgumentException`, and `compareTo` orders IDs by their hierarchical components.

Tool flow is MapReduce-driver oriented. `DistCp.run` lists source paths recursively, distributes copy work across map inputs, performs copying in mappers, and uses no meaningful reduce step. `HadoopArchives.run` lists archive sources, has mappers create archive parts, and uses a reducer to create archive indexes. `Logalyzer` has separate archive and analyze flows, with grep pattern, sort columns, and separator parameters shaping analysis output.

## State, Persistence, and Side Effects

This XML file itself is persistent compatibility metadata. It does not hold runtime implementation state, but it defines the public APIs that downstream compatibility checks, application source code, serialized records, and generated documentation rely on.

`Counters`, `ID`, `JobID`, `TaskID`, `TaskAttemptID`, and `FileSplit` expose `DataInput`/`DataOutput` serialization. Their binary field order and string forms are compatibility-sensitive because job history, task logs, filenames, RPC payloads, and user tooling can persist or display these values.

`Job` and `JobContext` state is configuration-backed. Job setup mutates `Configuration`/`JobConf` keys for classes, paths, comparators, compression, split settings, reduce counts, and output settings. Once submitted, mutable client-side control state is replaced by cluster-facing job state such as progress, counters, task events, tracking URL, and terminal success/failure.

Task context state is framework-owned. `TaskAttemptContext` stores attempt identity and status. `TaskInputOutputContext` delegates current input cursor, output writes, counters, status, and progress. `ReduceContext` additionally stores reduce input iteration state and grouping/value iterator behavior.

Filesystem side effects are central to `FileInputFormat`, `FileOutputFormat`, `FileOutputCommitter`, and the tools package. Input listing reads path metadata and block locality. Output committers create and delete temporary directories, move task outputs, and remove work directories. `DistCh`, `DistCp`, `HadoopArchives`, and `Logalyzer` can change ownership/permissions, copy trees, create archives and indexes, archive logs, and write analysis output.

Configuration side effects are exposed through many static helper methods. `FileInputFormat` persists input paths, path filters, and split bounds into the job. `FileOutputFormat` persists compression flags, compressor class, and output path. `SequenceFileOutputFormat` persists sequence-file compression type. `MultithreadedMapper` persists mapper class and thread count.

Concurrency is visible in two places. `TextOutputFormat.LineRecordWriter.write` and `close` are synchronized around a shared `DataOutputStream`. `MultithreadedMapper` intentionally invokes mapper logic concurrently, so application mapper implementations and any shared dependencies must be thread-safe.

## Dependencies and Integration Points

The chunk is centered on the newer `org.apache.hadoop.mapreduce` API but still bridges older Hadoop internals. `JobContext` stores an old `org.apache.hadoop.mapred.JobConf`; ID classes extend `org.apache.hadoop.mapred.ID`; `ReduceContext` depends on `org.apache.hadoop.mapred.RawKeyValueIterator`; `Logalyzer.LogRegexMapper` implements old `org.apache.hadoop.mapred.Mapper`; several APIs reference old task completion and output validation types.

Filesystem integration uses `org.apache.hadoop.fs.Path`, `FileSystem` behavior, file statuses, block locations, and `PathFilter`. File splits, output work paths, archive destinations, copy destinations, and log-analysis outputs all depend on Hadoop filesystem semantics.

Serialization and data-format dependencies include `org.apache.hadoop.io.Writable`, `WritableComparable`, `LongWritable`, `Text`, `RawComparator`, `SequenceFile`, `SequenceFile.CompressionType`, and compression codecs. Java IO dependencies include `DataInput`, `DataOutput`, `DataOutputStream`, `IOException`, and `Closeable`.

MapReduce integration points include `Configuration`, `Job`, `JobContext`, `TaskAttemptContext`, `TaskInputOutputContext`, `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `Partitioner`, `OutputFormat`, `RecordWriter`, `OutputCommitter`, `Counter`, `Counters`, and `StatusReporter`. The tools package integrates with `org.apache.hadoop.util.Tool` and command-line `main` methods.

External Java dependencies include `java.util.List`, `Iterable`, `Iterator`, arrays, `Class`, `StringBuilder`, and `java.text.NumberFormat`. `DistCp` exposes Apache Commons Logging through a public `Log` field. `Logalyzer.LogComparator` integrates with `org.apache.hadoop.conf.Configurable`.

## Risks and Compatibility Notes

The chunk begins inside the `Counters` class, so the class declaration and earlier counter APIs are in the preceding chunk. This range also closes the full XML document. The final merge lane should combine all nine chunks for this source file before producing a per-file report.

Because this file is a JDiff snapshot, signature-level changes are the primary risk. Altering method names, parameter types, checked exceptions, visibility, synchronized flags, inheritance, implemented interfaces, enum fields, or deprecation states would change the recorded Hadoop 0.20.2 compatibility contract.

Job mutability boundaries are important. Setters that are only valid before submission must continue to reject post-submission changes, and monitoring/control methods must preserve communication errors through declared `IOException` or interruption where documented.

Identifier compatibility is high-risk. `JobID`, `TaskID`, and `TaskAttemptID` string formats, parser behavior, compare ordering, equality, hash codes, and writable serialization are observed by logs, filenames, job history, UI links, and external tools. The docs warn against manual string parsing, but the public strings remain de facto integration points.

Input splitting affects correctness and performance. Edge cases include empty or missing input paths, path-filter behavior, compressed-file splitability, min/max split interactions, zero-length files, block-locality selection, and `InvalidInputException` aggregation without copying the problem list.

Output commit behavior protects correctness under retries and speculative execution. Bugs in work path generation, unique filename generation, existing-output checks, task commit promotion, abort cleanup, or job cleanup can produce duplicate output, partial output, lost side-effect files, or conflicts between simultaneous attempts.

Mapper and reducer lifecycle changes can break user subclasses. Setup/map-or-reduce/cleanup ordering, default identity behavior, exception propagation, object reuse in reduce values, counter/status/progress delegation, and custom `run` semantics are all part of application-visible behavior.

`MultithreadedMapper` is risky with mutable mapper fields, non-thread-safe libraries, shared output collectors, counters, status reporters, or record readers that assume single-threaded access. Its thread-count and mapper-class configuration keys are externally visible through the static getters/setters.

The tools APIs perform broad filesystem mutations. `DistCh` can recursively alter permissions and ownership, `DistCp` can copy or overwrite large directory trees and must handle duplicate sources and read failures, `HadoopArchives` creates persistent archive structure and indexes, and `Logalyzer` accepts regex/sort/separator inputs that can heavily affect output shape.

## Test Signals

JDiff-level validation should confirm the full XML remains well formed through the final `</api>` marker and that this chunk preserves all package names, class names, inheritance, implemented interfaces, constructors, methods, parameter types, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation states, and Javadoc blocks.

Counter and ID tests should cover `Counters` write/read round trips, total size calculation, textual output, `incrAllCounters`, equality/hash code, `ID` numeric comparison and serialization, and `JobID`/`TaskID`/`TaskAttemptID` constructor, parser, `toString`, `appendTo`, equality, hash, compare, map/reduce kind, and malformed/null parse behavior.

Job and context tests should cover every major setter/getter pair, post-submission mutation rejection, job jar lookup, tracking URL, map/reduce progress, completion/success checks, kill/fail task operations, task completion event paging, counters retrieval, `submit`, `waitForCompletion`, and configuration-backed class resolution in `JobContext`.

Mapper/reducer context tests should cover lifecycle ordering, default mapper and reducer behavior, custom `run`, current key/value cursor behavior, output writes, counter lookup by enum and group/name, status/progress delegation, reduce grouping behavior, value iterator object reuse, and exception propagation for `IOException` and `InterruptedException`.

Input tests should cover `FileInputFormat` path setters/adders/getters, comma-separated path handling, path filters, empty/missing inputs, min/max split settings, split-size computation, block index lookup, unsplittable compressed inputs, `FileSplit` writable round trips, `InvalidInputException` messages, `LineRecordReader` offsets/progress/close, `TextInputFormat` splitability, and sequence-file reader initialization/progress/current key/value behavior.

Map helper tests should cover `InverseMapper` key/value swapping, `TokenCounterMapper` tokenization and count emission, and `MultithreadedMapper` thread-count and mapper-class configuration plus concurrent execution with a deliberately thread-safe mapper.

Output tests should cover output path validation, existing-output rejection, compression flag and codec configuration, sequence-file compression type, work output path generation, unique map/reduce filenames, default work files, task setup/commit/abort/needs-commit/cleanup behavior, text output formatting and synchronized write/close, and `NullOutputFormat` discarding output.

Partition and reducer helper tests should cover `HashPartitioner` behavior for positive, negative, and zero hash codes across reduce counts, plus `IntSumReducer` and `LongSumReducer` sums for empty, single-value, multiple-value, negative, and overflow-adjacent inputs.

Tool tests should exercise `DistCh.run` argument handling and property changes, `DistCp.copy` and `run` for directory copies, duplicate source failures, ignored read failures, log path behavior, random ID generation, `HadoopArchives.archive` and archive index creation, `Logalyzer.doArchive`, `Logalyzer.doAnalyze` with grep/sort/separator options, `LogComparator` configuration and byte comparison, and `LogRegexMapper` extraction through old `mapred` mapper interfaces.
