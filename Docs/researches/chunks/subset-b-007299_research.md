# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml - subset-b-007299

Chunk lines: 24870-30908.

## Purpose

This chunk is part of the Hadoop 0.19.1 JDiff XML API snapshot. It is generated API metadata, not executable Java implementation. The file records public/protected class and interface signatures, inheritance, implemented interfaces, constructors, methods, fields, checked exceptions, deprecation text, and embedded Javadoc. The useful research signal is therefore the API contract exposed by Hadoop 0.19.1 and the behavior documented by those contracts.

The slice starts at the tail of `org.apache.hadoop.mapred.MultiFileSplit`, then covers old `org.apache.hadoop.mapred` output, record, reducer, reporter, running-job, sequence-file, skip-bad-record, task, task-log, task-tracker, text input/output, and job-control APIs. It then covers most of `org.apache.hadoop.mapred.join`, and finishes in `org.apache.hadoop.mapred.lib.InputSampler` after the opening of `writePartitionFile`. Because the chunk ends mid-class, `InputSampler` is incomplete and must be reconciled with the following chunk before making whole-file claims.

## Important APIs, Types, and Contracts

### Old mapred dataflow contracts

- `OutputCollector<K,V>` is the callback used by `Mapper` and `Reducer` implementations to emit key/value pairs via `collect(K,V)`.
- `OutputCommitter` is the abstract output lifecycle hook for a MapReduce job. It exposes `setupJob`, `cleanupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, and `abortTask`, all keyed by `JobContext` or `TaskAttemptContext`. Its contract is responsible for temporary output setup, commit promotion, and abort cleanup.
- `OutputFormat<K,V>` validates output specs and constructs `RecordWriter<K,V>` instances. `checkOutputSpecs(FileSystem, JobConf)` is expected to reject unsafe output, commonly pre-existing destinations, while `getRecordWriter` returns the writer for a task output part.
- `OutputLogFilter` implements `PathFilter` and rejects `_logs` paths when listing output directories.
- `Partitioner<K2,V2>` extends `JobConfigurable`; `getPartition(key,value,numPartitions)` maps intermediate map-output keys to reducer partitions.
- `RecordReader<K,V>` presents records from an `InputSplit` through `next`, factory methods for reusable key/value objects, position, close, and progress. The Javadoc documents the key MapReduce boundary: converting byte-oriented splits into record-oriented task inputs.
- `RecordWriter<K,V>` writes output records and closes with a `Reporter`.
- `Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and Hadoop `Closeable`. Its `reduce` contract receives a grouped key and iterator of values, writes through `OutputCollector`, and uses `Reporter` for liveness/progress. The Javadoc explicitly describes the shuffle, sort, and reduce phases and warns that the framework reuses key/value objects.
- `Reporter` is the task-side reporting API. It sets status text, gets/increments enum or string counters, exposes the current `InputSplit`, and provides `Reporter.NULL` for no-op progress reporting.
- `RunningJob` is the user-facing handle returned by `JobClient`. It exposes `JobID`, deprecated string job IDs, job name/file/tracking URL, setup/map/reduce/cleanup progress, completion/success checks, blocking wait, job state, kill, priority updates, task-completion events, task kill/fail, and counters.

### SequenceFile input and output formats

- `SequenceFileAsBinaryInputFormat` returns a `RecordReader<BytesWritable,BytesWritable>` over raw serialized sequence-file keys and values. Its nested `SequenceFileAsBinaryRecordReader` exposes key/value class names, synchronized `next(BytesWritable,BytesWritable)`, position, close, and split progress.
- `SequenceFileAsBinaryOutputFormat` writes raw binary keys/values into SequenceFiles. It allows the configured output key/value class to differ from the in-memory `BytesWritable` writer type via `setSequenceFileOutputKeyClass`, `setSequenceFileOutputValueClass`, and corresponding getters. Its protected nested `WritableValueBytes` adapts `BytesWritable` to `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to `Text` by calling `toString()` on the original key/value objects. The record reader has synchronized `next`, `getPos`, and `close`.
- `SequenceFileInputFilter<K,V>` extends `SequenceFileInputFormat<K,V>` and installs a configurable key filter class. The nested `Filter` interface is `Configurable` and decides acceptance from a key. Built-in filters include `MD5Filter` (`MD5(key) % frequency == 0`), `PercentFilter` (record number modulo frequency), and `RegexFilter` (key string matches a configured regex). `FilterBase` holds configuration access.
- `SequenceFileInputFormat<K,V>` extends `FileInputFormat` for sequence files, with protected `listStatus` and `getRecordReader`.
- `SequenceFileOutputFormat<K,V>` extends `FileOutputFormat`, builds `RecordWriter` instances, opens generated output readers from a directory, and controls sequence-file compression type with `getOutputCompressionType` and `setOutputCompressionType`.
- `SequenceFileRecordReader<K,V>` is the standard synchronized sequence-file reader for file splits. It exposes runtime key/value classes, `createKey`, `createValue`, public and protected `next`, protected current-value and seek hooks, `getProgress`, `getPos`, `close`, and a protected `Configuration conf` field.

### Bad-record skipping and task metadata

- `SkipBadRecords` is a configuration utility for Hadoop's skip mode. It controls attempts before skipping starts, auto-increment behavior for mapper/reducer processed-record counters, skip output path, max skipped map records per bad record, and max skipped reduce groups per bad group.
- `SkipBadRecords` publishes counter names in `COUNTER_GROUP`, `COUNTER_MAP_PROCESSED_RECORDS`, and `COUNTER_REDUCE_PROCESSED_GROUPS`. The Javadoc says applications must increment these counters for bad-record detection, with framework auto-increment defaults that streaming/asynchronous apps may need to disable.
- `StatusHttpServer` extends `HttpServer`, with nested `TaskGraphServlet` rendering SVG task-status graphics through `doGet` and static graph dimension/margin fields.
- `TaskAttemptContext` extends `JobContext` and exposes `getTaskAttemptID` and `getJobConf`.
- `TaskAttemptID` and `TaskID` are immutable, comparable, writable identifiers. They construct from component parts, expose parent IDs and map/reduce role, implement equality, hash, comparison, string conversion, `readFields`/`write`, static `read`, static `forName`, and static regex pattern builders. The docs warn applications not to parse strings manually.
- `TaskCompletionEvent` is a writable job-tracker event describing task-attempt completion. It carries event ID, `TaskAttemptID`, status enum, task-tracker HTTP location, run time, map/reduce role helpers, writable serialization, equality, and `EMPTY_ARRAY`. Deprecated string task-id methods are retained beside typed `TaskAttemptID` methods.
- `TaskReport` is a writable task-state snapshot exposing typed `TaskID`, deprecated string ID, progress, state text, diagnostics, counters, start and finish times, equality/hash, and read/write methods.

### Task logging, servlets, and TaskTracker

- `TaskLog` is the task-specific user-log helper built around the `hadoop.log.dir` system property. It locates real/logical task log files and index files, synchronizes logs, purges old logs, reads configured max log length, quotes shell commands, wraps commands to capture stdout/stderr with optional setup and PID file, and captures debug output.
- `TaskLog.LogName` is an enum-like JDiff entry with `values`, `valueOf`, and `toString` for user-log streams.
- `TaskLogAppender` extends log4j `FileAppender` for child task system logs. It has activation, append, flush, synchronized close, task-id getter/setter, and total log size getter/setter.
- `TaskLogServlet` serves task logs over HTTP and provides static URL construction from tracker host, port, and task attempt ID.
- `TaskTracker` is the old worker daemon API. Public methods include instrumentation class selection, storage cleanup, shutdown/close, job client and report address access, JVM manager access, the server retry `run` loop, task fetch by child JVM, synchronized task status/diagnostic/range/progress/commit/done/shuffle/fs-error callbacks, map completion event fetch, map-output-lost reporting, idle checks, `main`, and task-memory-manager accessors. Its nested `MapOutputServlet` serves map outputs to reducers through Jetty.

### Text input/output formats

- `TextInputFormat` extends `FileInputFormat<LongWritable,Text>` and implements `JobConfigurable`. It configures from `JobConf`, determines splitability by filesystem/path, and creates line-oriented record readers. Keys are byte positions and values are line text.
- `TextOutputFormat<K,V>` extends `FileOutputFormat` and writes plain text output. Its protected static `LineRecordWriter<K,V>` writes synchronized records to a protected `DataOutputStream out`, using either a provided separator or default behavior, and closes with a `Reporter`.

### Job-control DAG APIs

- `org.apache.hadoop.mapred.jobcontrol.Job` encapsulates a `JobConf`, dependency jobs, a `JobClient`, a control ID, an assigned Hadoop `JobID`, message text, and state constants: `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`. It has synchronized state transitions and can add dependencies only while waiting. Its protected `submit` moves a ready job to running or failed depending on submission success.
- `JobControl` implements `Runnable` for a group of dependent jobs. It provides state-bucket accessors for waiting/running/ready/successful/failed jobs, synchronized `addJob`, bulk `addJobs`, thread state, stop/suspend/resume, synchronized `allFinished`, and a main loop that checks running jobs, updates waiting jobs, and submits ready jobs.

### Join framework

- `ArrayListBackedIterator<X>` and `StreamBackedIterator<X>` implement `ResetableIterator<X>`. The array-list implementation stores values in memory and is documented as less preferred than stream-backed storage. `ResetableIterator.EMPTY` is a no-op implementation.
- `ResetableIterator<T>` is not a Java `Iterator`; it is a stateful replay interface for join values with `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`. It requires FIFO replay after reset and warns that `next` may fail for nested joins even when `hasNext` is true.
- `ComposableInputFormat<K,V>` refines `InputFormat` to require a `ComposableRecordReader`. `ComposableRecordReader<K,V>` extends `RecordReader` and `Comparable`, adding child ID, key access/cloning, `hasNext`, `skip`, and `accept` into a join collector.
- `CompositeInputFormat<K>` parses `mapred.join.expr` expressions and configured `mapred.join.define.<ident>` join types, builds aligned `CompositeInputSplit` arrays from child input formats, constructs composable record readers, and provides static `compose` helpers for table and operation expressions. It assumes input sources are sorted and partitioned identically.
- `CompositeInputSplit` is a writable aggregate of child `InputSplit`s. It reports aggregate or child length, merged or child locations, and serializes as count, child split classes, then child split payloads. Child split classes must have public default constructors.
- `CompositeRecordReader<K,V,X>` is the shared base for joins over child `ComposableRecordReader`s. It exposes abstract `combine`, ID, configuration, priority queue/comparator access, child add, key/head access, skip, delegate creation, accept, join-collector filling, key/value creation, close, and progress as the minimum child progress.
- `JoinRecordReader<K>` emits `TupleWritable` values for join operations, with nested `JoinDelegationIterator` proxying the join collector. `InnerJoinRecordReader` emits only full tuples; `OuterJoinRecordReader` emits everything from the collector.
- `MultiFilterRecordReader<K,V>` emits a single writable derived from each tuple through abstract `emit`. `OverrideRecordReader` prefers the rightmost data source for a key and overrides collector filling to avoid cross-product expansion from lower-priority streams.
- `Parser` is documented as a simple shift-reduce parser for join expressions. `Parser.Node` maps identifiers to node types and `ComposableRecordReader` constructors through reflection, stores IDs, identifier, and key-comparator class. Token classes model node, numeric, string, generic token, and token type enum values.
- `TupleWritable` is a writable, iterable tuple for join outputs. It tracks which child positions are present, exposes `has`, `get`, `size`, equality/hash, iterator, string formatting, and serialization as count, type names, then object payloads. Its Javadoc warns it is not a general-purpose tuple and relies on join framework type safety.
- `WrappedRecordReader<K,U>` adapts a normal record reader to `ComposableRecordReader`, exposing child ID, head key, skip, accept into join collector, next/create/getProgress/getPos/close, comparison, equality, and hash.

### mapred.lib helpers

- `ChainMapper` and `ChainReducer` allow multiple mapper classes to be composed within a mapper task or after a reducer inside a reducer task. Static `addMapper` and `setReducer` write chain metadata into `JobConf`, including mapper/reducer class, input/output key/value classes, pass-by-value versus pass-by-reference behavior, and per-stage `JobConf` overrides. Runtime `configure`, `map`/`reduce`, and `close` execute and clean up the chain.
- `DelegatingInputFormat` and `DelegatingMapper` support `MultipleInputs` by dispatching paths to different input formats and mapper implementations.
- `FieldSelectionMapReduce` implements both mapper and reducer to select key/value fields from delimited text. Configuration keys include `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`, with numeric, range, and open-range field syntax.
- `HashPartitioner` partitions by `Object.hashCode()`.
- `IdentityMapper` and `IdentityReducer` pass records through unchanged.
- `InputSampler` is only partially visible: it implements `Tool`, has a `JobConf` constructor, `getConf`, `setConf`, and the start of static `writePartitionFile(JobConf, InputSampler.Sampler<K,V>)`. The rest of its sampling API is outside this chunk.

## Control Flow and Behavioral Semantics

This XML has no Java control-flow bodies. Behavioral flow is inferred from method contracts, inheritance, and Javadoc.

- Old `mapred` task flow is split-oriented: an `InputFormat` creates `InputSplit`s and `RecordReader`s; `Mapper`s emit via `OutputCollector`; partitioning routes intermediate keys to reducers; reducers consume grouped keys and values; `OutputFormat` and `RecordWriter` write task output; `OutputCommitter` controls setup, commit, and abort.
- Reducer flow explicitly includes shuffle over HTTP, sort/grouping by key, and reduce invocation. The framework may reuse key/value objects, so applications must clone data they retain beyond a call.
- Running-job control flow is client polling and control: query progress, fetch task completion events and counters, wait for completion, kill jobs/tasks, and adjust priority.
- SequenceFile readers convert file splits into typed, binary, or text records. Synchronized `next`, `getPos`, `seek`, and `close` methods on record readers signal mutable stream position and reader state.
- Skip-bad-record flow starts only after a configured number of failed attempts. Tasks report record ranges to the TaskTracker before processing; if a task crashes, subsequent attempts skip the last reported range and may write skipped records under the configured skip output path.
- TaskTracker flow is daemon-centered: connect/reconnect to JobTracker, spawn child JVM tasks, let children fetch tasks and periodically report status, handle commit arbitration, serve map outputs to reducers, and surface task logs over HTTP.
- Job-control flow is dependency-DAG scheduling: jobs start waiting, become ready when dependencies succeed, submit when ready, transition to success or failed, and propagate dependency failure.
- Join flow parses a configured expression into a tree of composable input formats/readers, aligns the ith split from every source into a composite split, orders child readers by key, fills a join collector for matching keys, and emits tuples or filtered values according to inner, outer, override, or custom operation semantics.
- Chain mapper/reducer flow pipes key/value pairs through configured stages inside one map or reduce task. By-value stages serialize/deserialize between stages for safety; by-reference stages skip copying for speed and require stricter no-mutation assumptions.

## State and Persistence Behavior

- The XML itself persists the public API state for Hadoop 0.19.1. Downstream JDiff tooling depends on exact class names, method signatures, visibility, deprecation strings, exception declarations, and documentation.
- `JobConf` and `Configuration` carry many behavioral settings: sequence-file filter class/frequency/pattern, sequence-file output key/value classes, compression type, skip-bad-record thresholds, skip output path, field-selection specs, join expressions, custom join type bindings, join key comparator, chained mapper/reducer metadata, and per-stage chain configurations.
- `Writable` implementations in this chunk persist task IDs, task attempts, task completion events, task reports, composite splits, tuple values, and sequence-file records to `DataOutput`/`DataInput`.
- `TaskID` and `TaskAttemptID` string formats are public compatibility boundaries, but the docs require callers to use constructors or `forName` rather than hand parsing.
- `TaskCompletionEvent`, `TaskReport`, and `RunningJob.getCounters` are persisted or remotely transported task/job status surfaces, integrating with JobTracker and client monitoring.
- `TaskLog` and `TaskLogAppender` persist stdout, stderr, syslog, debug output, index files, and bounded/tail log captures under task-specific log directories. Cleanup purges old user logs by retention hours.
- SequenceFile formats persist key/value class metadata, raw binary key/value payloads, compression type, and filtered/text conversion semantics. Binary output format additionally persists configured logical key/value classes that may differ from the runtime `BytesWritable` wrapper.
- Join state persists through serialized `CompositeInputSplit` and `TupleWritable` payloads. Runtime join iterators also hold replay buffers in memory or byte streams; `clear` and `close` define resource reuse/release boundaries.
- Job-control state is primarily in-memory, grouped by state tables, but it wraps actual submitted Hadoop jobs and assigned `JobID`s that persist in the MapReduce framework.

## Dependencies and Integration Points

- Java core APIs: `java.io.DataInput`, `DataOutput`, `DataOutputStream`, `File`, `IOException`; `java.util.Iterator`, `ArrayList`, `Collection`, maps, regex `PatternSyntaxException`; reflection constructors; and `java.lang.Enum`.
- Servlet/logging APIs: `javax.servlet.http.HttpServlet`, request/response, `ServletException`, log4j `FileAppender` and `LoggingEvent`, and Apache Commons Logging.
- Hadoop common APIs: `Configuration`, `Configurable`, `Path`, `FileSystem`, `FileStatus`, `PathFilter`, `Progressable`, `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, `SequenceFile`, and `HttpServer`.
- Old MapReduce APIs: `JobConf`, `JobClient`, `JobID`, `JobStatus`, `TaskStatus`, `TaskAttemptID`, `TaskID`, `TaskCompletionEvent`, `Counters`, `InputFormat`, `InputSplit`, `FileInputFormat`, `FileOutputFormat`, `Mapper`, `Reducer`, `Reporter`, `MapReduceBase`, `MultipleInputs`, `TaskTracker`, `JvmTask`, `JVMId`, `MapTaskCompletionEventsUpdate`, `SortedRanges.Range`, and `TaskMemoryManagerThread`.
- Filesystem and network integration points include task log directories, output directories, skip output paths, map output serving over TaskTracker Jetty, reducer shuffle over HTTP, and JobTracker/TaskTracker RPC-style callbacks.
- Tooling integration is JDiff/dev-support API comparison, not runtime Hadoop execution.

## Risks and Edge Cases

- Chunk-boundary risk: the first lines are the tail of `MultiFileSplit`, and the chunk ends inside `InputSampler.writePartitionFile`; adjacent chunks are required for complete class coverage.
- API compatibility risk is high because this is an API snapshot. Changing signatures, visibility, deprecation metadata, or documented exception types can alter JDiff output and break downstream compatibility analysis.
- Object reuse risk: `Reducer` and `RecordReader` contracts use reusable key/value instances. Applications retaining references without cloning can observe later mutation.
- Output commit risk: failures or speculative execution require correct `OutputCommitter` behavior. Incorrect `needsTaskCommit`, `commitTask`, or `abortTask` semantics can lose output, publish partial attempts, or leak temporary data.
- SequenceFile binary risk: `SequenceFileAsBinaryOutputFormat` lets logical key/value classes differ from `BytesWritable`; misconfiguration can create files whose declared classes do not match the raw bytes.
- Filter risk: `MD5Filter`, `PercentFilter`, and `RegexFilter` are configured through generic `Configuration` properties. Bad frequencies, invalid regexes, or filter classes without expected constructors/configuration behavior can fail at task startup or skew sampling.
- Skip-bad-record risk: enabling skip mode accepts data loss around failing records/groups. Streaming or asynchronous applications must manage processed-record counters themselves if framework auto-increment does not match actual processing.
- Task-log shell risk: `TaskLog.captureOutAndError` and `addCommand` build shell-wrapped commands. Quoting and executable path handling are correctness and security-sensitive.
- TaskTracker risk: many public TaskTracker methods are synchronized callbacks from child tasks. Incorrect blocking behavior can stall progress reports, commit decisions, map-output loss handling, or shutdown.
- Join correctness risk: all sources must be sorted and partitioned the same way, and key classes/comparators must match. Misaligned split counts, inconsistent comparators, or non-default-constructible child splits can break composite split creation or produce incorrect joins.
- Join memory risk: inner/outer joins can create cross products for duplicate keys. `OverrideRecordReader` avoids some cross-product expansion, but generic joins can consume large replay buffers.
- ChainMapper/ChainReducer risk: by-reference chaining can be faster but unsafe when later stages mutate key/value objects expected to be stable. Stage input/output class mismatches are not converted by the chain code and will fail at runtime.
- Deprecation migration risk: visible deprecated methods include `RunningJob.getJobID`, string `killTask`, `TaskCompletionEvent.getTaskId`/`setTaskId`, `TaskReport.getTaskId`, and job-control string mapred job ID methods. Typed `JobID`, `TaskID`, and `TaskAttemptID` APIs are the preferred replacements.

## Test Signals and Validation Targets

- JDiff validation should assert the XML is well-formed across this chunk, class/interface boundaries are preserved, and deprecation strings remain stable.
- Old `mapred` contract tests should cover `OutputCollector`, `Partitioner`, `RecordReader`, `RecordWriter`, `Reducer`, `Reporter`, `OutputFormat`, and `OutputCommitter` lifecycle ordering, especially commit/abort paths.
- `RunningJob` tests should cover progress values, completion/success transitions, task completion event pagination, counters, priority changes, job kill, typed task kill, and deprecated string compatibility.
- SequenceFile tests should round-trip standard, binary, text, filtered, and compressed record readers/writers; validate declared key/value classes for binary output; and test split progress/seek/close behavior.
- Filter tests should exercise MD5, percent, regex, bad regex configuration, and configured custom filter class loading.
- Skip-bad-record tests should simulate deterministic mapper/reducer failures, counter auto-increment on/off, threshold narrowing, `Long.MAX_VALUE` no-narrowing behavior, and skip output path null/default behavior.
- Writable status tests should round-trip `TaskID`, `TaskAttemptID`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable`, including malformed ID strings and deprecated string accessors.
- Task-log tests should validate log file/index location, sync, cleanup retention, tail-length capture, debug capture, log4j appender flush/close, and task-log servlet URL/output behavior.
- TaskTracker integration tests should cover child task fetch, status updates, diagnostics, commit pending/can commit/done, shuffle and filesystem error reporting, map completion events, map output lost, map-output servlet serving, idle state, and memory manager enablement.
- Job-control tests should cover dependency addition limits, waiting-to-ready transitions, dependent failure propagation, successful submission, failed submission, thread stop/suspend/resume, and `allFinished`.
- Join tests should cover expression parsing, default and custom identifiers, composite split serialization, split-count mismatch, inner/outer/override joins, duplicate-key cross products, tuple serialization, reset/replay iterators, and comparator/key-class mismatch.
- Chain tests should verify mapper and reducer chains with by-value and by-reference stages, per-stage `JobConf` precedence, output key/value class inference from the last stage, close ordering, and class mismatch failures.

## Chunk Merge Notes

- Merge with the preceding chunk for the full `MultiFileSplit` definition and any immediately prior `mapred` APIs.
- Merge with the following chunk for the remainder of `InputSampler` and later `org.apache.hadoop.mapred.lib` APIs.
- The final per-file report should describe `hadoop_0.19.1.xml` as a generated JDiff API snapshot and avoid treating this chunk as implementation source.
