# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 50013-52140

## Scope

This chunk is the final segment of the generated JDiff public API snapshot for Hadoop 0.20.0. It is XML compatibility metadata rather than implementation code. The range begins inside the `org.apache.hadoop.mapreduce.Reducer.reduce(...)` method entry, completes the newer `org.apache.hadoop.mapreduce` task context and task identifier APIs, covers the `org.apache.hadoop.mapreduce.lib.input`, `lib.map`, `lib.output`, `lib.partition`, and `lib.reduce` helper packages, then records the start of the `org.apache.hadoop.tools` public utility APIs before closing the XML document.

The XML records the public surface: package/class names, inheritance, implemented interfaces, constructors, method signatures, parameters, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and embedded Javadoc. Behavioral notes below are inferred from signatures and Javadoc because method bodies are not present in this source.

## Purpose and Major API Surface

The `Reducer` tail documents the canonical reduce lifecycle. `setup(Context)` runs once, `reduce(Object, Iterable, Context)` runs once per grouped key with an identity default, `cleanup(Context)` runs once at task end, and `run(Context)` lets advanced users control the overall loop. The class Javadoc describes the reduce-side pipeline as shuffle, sort, and reduce. It also documents secondary sort through grouping and sort comparators, and notes that reducer output is not sorted again after user code writes through `Context.write`.

`Reducer.Context` extends `ReduceContext` and is constructed from a `Configuration`, `TaskAttemptID`, old-mapred `RawKeyValueIterator`, reduce input `Counter`, `RecordWriter`, `OutputCommitter`, `StatusReporter`, grouping `RawComparator`, and key/value classes. This is the bridge between framework-managed reduce input state and user reducer code.

`StatusReporter` is an abstract reporting facade. Implementations must provide counter lookup by enum or by group/name, `progress()`, and `setStatus(String)`. `TaskAttemptContext` extends `JobContext` and implements `Progressable`; it exposes the task attempt ID, status mutation/query, and a progress callback. `TaskInputOutputContext` extends `TaskAttemptContext` and adds the abstract input cursor (`nextKeyValue`, `getCurrentKey`, `getCurrentValue`) plus output writing, counter access, status/progress delegation, and access to the task `OutputCommitter`.

`TaskID` and `TaskAttemptID` are immutable public identifiers extending the old `org.apache.hadoop.mapred.ID` base. `TaskID` identifies a map or reduce task within a `JobID`; `TaskAttemptID` identifies a specific attempt for a `TaskID`. Both support constructors from component parts, zero-arg constructors for serialization, `getJobID`, map/reduce checks, `equals`, `hashCode`, `compareTo`, `toString`, protected `appendTo`, static `forName(String)` parsers, and `Writable`-style `readFields`/`write` methods. Their documented string forms are `task_<jt>_<job>_[m|r]_<task>` and `attempt_<jt>_<job>_[m|r]_<task>_<attempt>`.

The `lib.input` package supplies file-oriented input APIs. `FileInputFormat` is the base `InputFormat` for filesystem inputs, with configuration helpers for input paths, input filters, min/max split sizes, splitability, status listing, split generation, split size computation, and host block lookup. `FileSplit` is a writable `InputSplit` containing a `Path`, byte start, byte length, and host locations. `InvalidInputException` aggregates multiple input problems. `LineRecordReader` reads text lines keyed by byte offset. `TextInputFormat` wraps that reader and controls splitability for plain text. `SequenceFileInputFormat` and `SequenceFileRecordReader` handle `SequenceFile` inputs, including format-specific minimum split size and reader progress.

The `lib.map` package provides mapper helpers. `InverseMapper` swaps input keys and values. `TokenCounterMapper` tokenizes text input values and emits each token with a count of one. `MultithreadedMapper` runs an application mapper through a thread pool; its static configuration methods get/set the thread count and application mapper class, and its `run` method drives concurrent mapping.

The `lib.output` package supplies filesystem output behavior. `FileOutputCommitter` manages temporary task work directories and promotes successful task output into the final job output directory. `FileOutputFormat` is the base `OutputFormat` for file outputs, with helpers for compression settings, output path validation, work output paths, unique task filenames, default work files, and output committer creation. `TextOutputFormat` writes plain text files through the nested synchronized `LineRecordWriter`, while `SequenceFileOutputFormat` writes `SequenceFile` output and exposes sequence compression type configuration. `NullOutputFormat` discards all output.

`HashPartitioner` in `lib.partition` partitions keys by `Object.hashCode()`. `IntSumReducer` and `LongSumReducer` in `lib.reduce` are concrete reducer helpers that sum iterable numeric values for each key.

The `org.apache.hadoop.tools` entries expose distributed command-line utilities. `DistCh` is a MapReduce tool for recursively changing file properties such as owner, group, and permissions. `DistCp` implements `Tool` and recursively copies directories across filesystems; it includes configuration accessors, a static `copy(...)` helper, `run`, `main`, `getRandomId`, a public `LOG`, and `DuplicationException` for duplicated source files. `HadoopArchives` implements `Tool` for creating Hadoop archives from source paths into a destination. `Logalyzer` archives and analyzes Hadoop logs, with `doArchive`, `doAnalyze`, `main`, a configurable `LogComparator`, and a legacy mapred `LogRegexMapper` that extracts text matching a regular expression.

## Control Flow and Behavioral Contracts

Reducer control flow is lifecycle-based. Framework code constructs the context, fetches and merge-sorts map output during shuffle/sort, groups keys with the configured grouping comparator, and calls user `reduce` once per key group. User output is written through the context to a `RecordWriter`; if users override `run`, they assume responsibility for preserving setup, reduce iteration, cleanup, progress, and interruption behavior.

Task contexts model cursor-style input and side-effectful output. `TaskInputOutputContext.nextKeyValue()` advances the current input pair; `getCurrentKey()` and `getCurrentValue()` read the current cursor contents; `write()` emits an output pair; counter/status/progress calls flow through the reporter. `OutputCommitter` access ties task code to commit/abort behavior.

Identifier control flow centers on stable parse/format/serialize round trips. `TaskID` compares first by `JobID`, then map/reduce kind, then numeric task id, with reduces ordered after maps per Javadoc. `TaskAttemptID` compares by task id and attempt number. `forName` returns null on null input and throws `IllegalArgumentException` for malformed strings, making identifier text formats compatibility-sensitive.

`FileInputFormat` flow starts from configured input paths, optionally applies a `PathFilter`, lists file statuses, validates non-empty input, computes split sizes using block size plus min/max configuration, and emits `FileSplit` instances with host locality. Subclasses can override `isSplitable`, `getFormatMinSplitSize`, `listStatus`, and record reader creation to alter the split and reading behavior.

Record reader flow is uniform: `initialize(InputSplit, TaskAttemptContext)` binds the reader to a split, `nextKeyValue()` advances, current-key/current-value methods expose the current record, `getProgress()` reports split progress, and `close()` releases resources. `LineRecordReader` maps byte offsets to text lines; `SequenceFileRecordReader` maps serialized sequence-file records to key/value objects.

Output flow is guarded by output specs and commit protocol. `FileOutputFormat.checkOutputSpecs` validates the configured output directory and can raise `FileAlreadyExistsException`. Tasks write to attempt-specific work paths under a temporary output tree. `FileOutputCommitter.setupJob` creates the temporary root, `commitTask` moves task files to the final output directory, `abortTask` deletes failed work, `needsTaskCommit` checks whether work exists, and `cleanupJob` removes temporary directories.

Tool flow is MapReduce-driver oriented. `DistCp.run` lists source files recursively, distributes the copy workload into map input files, performs copies in mappers, and has an empty reduce phase. `HadoopArchives.run` lists sources, has mappers create archive parts, and uses a reducer to create archive indexes. `Logalyzer` can archive logs from a URI list and analyze files with grep, sort-column, and separator parameters; its mapper/comparator bridge the older `org.apache.hadoop.mapred` API.

## State, Persistence, and Side Effects

The JDiff file itself is persistent API metadata for compatibility checking. It does not contain implementation bodies, but it captures public method and field contracts that downstream source and binary compatibility checks rely on.

Runtime state in the task APIs is mostly framework-owned. `TaskAttemptContext` stores the current attempt ID and status string. `TaskInputOutputContext` delegates mutable counters, reporter progress, and output writes. `Reducer.Context` carries reduce iteration state, output writer state, and commit/reporting hooks supplied by the framework.

`TaskID`, `TaskAttemptID`, and `FileSplit` are persisted through `DataInput`/`DataOutput` serialization. Their string formats are also persisted indirectly in logs, filenames, counters, temporary paths, and job metadata. Changing these formats or serialization order would affect compatibility with existing job history, tooling, and on-disk metadata.

`FileInputFormat` and `FileOutputFormat` persist behavior through job `Configuration` keys: input paths, split min/max settings, path filters, output paths, compression flags, compressor classes, and sequence-file compression type. These APIs are static setters/getters around job configuration and are therefore part of Hadoop's job submission contract.

Filesystem side effects are central in `FileOutputCommitter`, `FileOutputFormat`, and the tools package. Temporary directories, work files, side-effect files, committed output, copied files, changed ownership/permissions, archive output, and log-analysis output are all external state. Speculative execution is explicitly called out in the work-output path Javadoc: applications should write side files under attempt work directories so unsuccessful attempts can be discarded safely.

`TextOutputFormat.LineRecordWriter.write` and `close` are synchronized, indicating thread-safety concerns around the shared `DataOutputStream`. `MultithreadedMapper` introduces concurrent mapper execution; mapper implementations used with it must be thread-safe because multiple input records can be processed in parallel within one task.

## Dependencies and Integration Points

This chunk integrates the new `org.apache.hadoop.mapreduce` API with older Hadoop internals and legacy mapred APIs. `Reducer.Context` depends on `org.apache.hadoop.mapred.RawKeyValueIterator` and `org.apache.hadoop.io.RawComparator`; identifier classes extend `org.apache.hadoop.mapred.ID`; output spec validation references `org.apache.hadoop.mapred.FileAlreadyExistsException`; `Logalyzer.LogRegexMapper` implements the old `org.apache.hadoop.mapred.Mapper`.

Filesystem integration uses `org.apache.hadoop.fs.Path`, `FileSystem` behavior implied by input/output formats, `BlockLocation` for split locality, and `PathFilter` for input filtering. Serialization and data-format dependencies include `org.apache.hadoop.io.Writable`, `LongWritable`, `Text`, `SequenceFile`, `SequenceFile.CompressionType`, and compression codecs configured through output formats.

MapReduce integration points include `Job`, `JobContext`, `TaskAttemptContext`, `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `Reducer`, `Partitioner`, `OutputFormat`, `RecordWriter`, `OutputCommitter`, `Counter`, and `StatusReporter`. The tools package also integrates with `org.apache.hadoop.util.Tool` and command-line `main` methods.

External Java dependencies include `java.io` streams and data inputs/outputs, `java.util` lists/iterables/iterators, `java.text.NumberFormat`, and `java.lang.Class`. `DistCp` exposes an Apache Commons Logging `Log`.

## Risks and Compatibility Notes

The chunk starts inside the `Reducer.reduce(...)` method entry, so the method header is immediately before this range. The final merge lane should combine this with adjacent chunks to reconstruct the complete class entry. This range itself contains the method documentation and the rest of the reducer class.

Reducer semantics are compatibility-sensitive because user subclasses often override protected lifecycle methods. Changes to the default identity reduce implementation, setup/cleanup ordering, exception propagation, or the `run` loop would break application code. The secondary-sort documentation is also a contract with job comparator configuration.

Task and attempt identifiers are high-risk compatibility points. Their string parsing, string formatting, ordering, equality, hash code, serialization, and map/reduce ordering are used across logs, filenames, history, web UIs, and tooling. The docs explicitly warn applications not to parse strings manually, but many external tools still observe those strings.

Input split behavior affects both correctness and performance. Edge cases include empty input lists, missing paths, path-filter behavior, compressed-file splitability, min/max split interactions, block locality selection, zero-length files, and `InvalidInputException` aggregation without copying the problem list.

Output commit behavior protects correctness under retries and speculative execution. Bugs in work path generation, unique filename generation, commit promotion, abort cleanup, or output directory checks can produce data loss, duplicate output, partial commits, or conflicts between simultaneous attempts. `getUniqueFile` is synchronized and should remain stable for concurrent callers.

`MultithreadedMapper` increases throughput only when user mappers and their dependencies are thread-safe. It is risky with mutable mapper fields, non-thread-safe output usage, shared counters/status calls, or readers that assume single-threaded access. Configuration defaults such as the documented 10-thread default are externally visible.

The tools APIs perform broad filesystem mutations. `DistCh` can recursively change permissions and ownership; `DistCp` can overwrite/copy large directory trees and must handle duplicate sources and read failures; `HadoopArchives` creates persistent archive indexes; `Logalyzer` accepts regex, sort, and separator inputs that affect output shape. These utilities need strong argument validation and failure reporting.

## Test Signals

JDiff-level validation should confirm the XML remains well formed through the final `</api>` marker and preserves class names, inheritance, implemented interfaces, constructors, method signatures, parameter types, declared exceptions, fields, visibility, synchronization flags, static/final/abstract flags, and deprecation states for all classes in this range.

Reducer tests should cover default identity reduce behavior, setup/reduce/cleanup ordering, custom `run` behavior, exception propagation for `IOException` and `InterruptedException`, context writes, progress/status/counter reporting, grouping comparator behavior, sort comparator behavior, and confirmation that reducer output is not resorted.

Identifier tests should cover `TaskID` and `TaskAttemptID` constructors, `forName(null)`, malformed strings, valid map and reduce strings, `toString` round trips, `readFields`/`write` round trips, equality/hash code, compare ordering by job/task/attempt, and reduce-after-map ordering.

Input tests should cover `FileInputFormat` path setters/getters for comma-separated and `Path[]` inputs, path filtering, min/max split configuration, split size calculation, block index selection, missing and empty inputs, unsplittable compressed text files, line reader offsets and CR/LF handling, sequence-file splits/readers/progress, `FileSplit` serialization, and `InvalidInputException` messages.

Map helper tests should cover `InverseMapper` key/value swapping, `TokenCounterMapper` tokenization and count emission, and `MultithreadedMapper` configuration of mapper class/thread count plus concurrent execution with a thread-safe mapper.

Output tests should cover output directory existence checks, compression flag and codec configuration, sequence-file compression type, default work file naming, unique file naming for map and reduce tasks, work output path behavior, side-effect file promotion, task commit/abort/cleanup semantics, `needsTaskCommit`, text output formatting and synchronized close/write behavior, and `NullOutputFormat` discarding output.

Tool tests should exercise `DistCh.run` argument handling and property changes, `DistCp.copy` and `run` for directory copies, duplicate-source failures, ignored read failures, log path use, generated random IDs, `HadoopArchives.archive` and archive index creation, `Logalyzer.doArchive`, `Logalyzer.doAnalyze` with grep/sort/separator options, `LogComparator` configuration and byte comparison, and `LogRegexMapper` regex extraction through the old mapred interfaces.
