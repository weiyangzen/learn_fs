# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 24887-30897

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not Java implementation source. It records public and protected API metadata for a large part of the legacy `org.apache.hadoop.mapred` surface, then continues into `org.apache.hadoop.mapred.jobcontrol`, `org.apache.hadoop.mapred.join`, and the beginning of `org.apache.hadoop.mapred.lib`. The XML captures class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, field constants, visibility, static/final/abstract/synchronized/native flags, deprecation text, and embedded Javadoc contracts.

The chunk starts inside `org.apache.hadoop.mapred.OutputFormat` at `checkOutputSpecs`, then covers output log filtering, partitioning, record reader/writer contracts, reducer/reporter/job status APIs, sequence-file formats and filters, skip-bad-record configuration, task IDs/events/logs/reports, `TaskTracker`, text input/output formats, job-control orchestration, join input formats/readers/parsers/tuple state, chain mapper/reducer composition, multiple-input delegation, field selection, identity mapper/reducer helpers, and most of `InputSampler` through the `SplitSampler` constructors.

## Purpose and Major API Surface

`OutputFormat.checkOutputSpecs(FileSystem, JobConf)` validates output specifications before job submission, typically rejecting output paths that already exist. The preceding part of `OutputFormat` is outside this chunk, but the local lines also include the interface-level contract that an `OutputFormat` validates output specs and supplies a `RecordWriter` for job output stored in a `FileSystem`.

`OutputLogFilter` implements `PathFilter` and rejects paths containing `_logs`, allowing clients to list normal output files while hiding MapReduce log directories.

`Partitioner<K2,V2>` extends `JobConfigurable` and defines `getPartition(K2 key, V2 value, int numPartitions)`. It maps intermediate records to reduce partitions, normally by hashing the key or a key subset; the number of partitions matches the number of reduce tasks.

`RecordReader<K,V>` defines the map-input read contract: `next(K,V)`, `createKey()`, `createValue()`, `getPos()`, `close()`, and `getProgress()`. It converts byte-oriented `InputSplit` data into record-oriented key/value pairs for mappers and reducers. `RecordWriter<K,V>` is the output-side counterpart with `write(K,V)` and `close(Reporter)`.

`Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and Hadoop `Closeable`, with `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)`. Its Javadoc documents the shuffle, sort, and reduce phases, secondary-sort comparators, object reuse hazards for keys and values, reporter progress/counters/status, and the fact that reducer output is not re-sorted.

`Reporter` extends `Progressable` and exposes task status, counters, input-split access for maps, and a `Reporter.NULL` no-op instance. It supports `setStatus`, counter lookup by group/name, counter increments by enum or string group/name, `getInputSplit`, and progress reporting inherited from `Progressable`.

`RunningJob` is the client-facing handle for a submitted job. It exposes job identity/name/file/tracking URL, map/reduce/setup/cleanup progress, completion/success checks, blocking wait, integer job state, kill operations, priority changes, task-completion event retrieval, task-attempt kill by `TaskAttemptID`, deprecated task kill by string, and counters.

The sequence-file APIs provide binary/text/raw alternatives around `SequenceFile`:

- `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read raw key and value bytes into `BytesWritable`, expose key/value class names, support synchronized `next`, and track position/progress within a `FileSplit`.
- `SequenceFileAsBinaryOutputFormat` writes `BytesWritable` key/value pairs while allowing the persisted SequenceFile key/value classes to differ from the actual `BytesWritable` writer type. It exposes static setters/getters for output key/value classes, `getRecordWriter`, and `checkOutputSpecs`. Its protected `WritableValueBytes` wrapper implements `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert SequenceFile keys and values to `Text` by calling `toString`.
- `SequenceFileInputFilter` wraps `SequenceFileInputFormat` with a configurable `Filter`, plus `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`. Filters are configured through `Configuration` and decide acceptance from record keys using MD5 modulus, record-number frequency, or regex matching.
- `SequenceFileInputFormat`, `SequenceFileOutputFormat`, and `SequenceFileRecordReader` expose the base old-API SequenceFile read/write contracts, including listing statuses, creating record readers/writers, opening generated readers, setting/getting compression type, creating keys/values, synchronized reads/seeks/closes in the record reader, and protected `Configuration` state.

`SkipBadRecords` is a static configuration utility for skip mode. It controls attempts before skipping begins, automatic mapper/reducer processed-record counter increments, skip output path, maximum acceptable skipped records/groups around failures, and exposes the special counter group plus mapper/reducer processed counter names.

`StatusHttpServer` extends `HttpServer`, and nested `TaskGraphServlet` writes SVG task-status graphics with public width/height/margin constants.

`TaskAttemptContext` extends `JobContext` and exposes `getTaskAttemptID()` and `getJobConf()`.

`TaskAttemptID` and `TaskID` are immutable, writable, comparable identifiers. `TaskID` identifies a map or reduce task within a `JobID`; `TaskAttemptID` identifies an attempt within a `TaskID`. Both expose constructors from structured parts, accessors, `isMap`, equality/comparison/string/hash behavior, `readFields`, `write`, static `read`, static `forName`, and regex-pattern factory methods for matching IDs. Deprecated string parsing is explicitly discouraged in favor of constructors and `forName`.

`TaskCompletionEvent` is a `Writable` record used by the JobTracker to track task completion. It stores event id, task attempt id, task status enum, task tracker HTTP location, run time, map/reduce identity helpers, equality/hash/string behavior, serialization, and an `EMPTY_ARRAY` constant. Deprecated string task-id accessors are retained alongside typed `TaskAttemptID` accessors.

`TaskLog`, `TaskLog.LogName`, `TaskLogAppender`, and `TaskLogServlet` define user-log file lookup, log synchronization/cleanup, log length, stdout/stderr/debug wrapping for child commands, shell quoting, log4j task appending, and HTTP serving of task logs from TaskTrackers. `TaskLog` depends on the `hadoop.log.dir` system property, and command-capture methods can optionally tail output and write pid files.

`TaskReport` is a `Writable` task-state summary with typed and deprecated string task ids, progress, state, diagnostics, counters, start/finish time, equality/hash, and serialization.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. It is the worker daemon API for starting and tracking tasks, contacting the JobTracker, cleaning local storage, managing JVM/task memory, serving map outputs, processing child-task heartbeats, reporting diagnostics and next-record ranges, mediating commit permission, marking tasks done, handling shuffle/filesystem errors, retrieving map completion events, recording lost map output, exposing idle state, and providing a `main` entry point. Its nested `MapOutputServlet` serves map outputs over Jetty.

`TextInputFormat` reads plain text as `LongWritable` byte offsets and `Text` lines; it is configurable, checks splitability, and creates a line record reader. `TextOutputFormat` writes plain text, and its protected `LineRecordWriter` writes synchronized key/value lines to a `DataOutputStream` with configurable separator behavior implied by its constructor.

`org.apache.hadoop.mapred.jobcontrol.Job` wraps a `JobConf` plus dependencies and state. It exposes job name/id, assigned MapReduce `JobID`, `JobConf`, state, message, `JobClient`, dependency list, dependency addition only while waiting, completion/readiness checks, protected submit, and integer state constants `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`.

`JobControl` manages a group of dependent `Job` instances in a thread. It exposes state-specific job lists, synchronized job addition, batch addition, thread state, stop/suspend/resume, all-finished checks, and `run()` loop behavior that checks running jobs, updates waiting jobs, and submits ready jobs.

The join package provides composable old-API input and reader abstractions:

- `ResetableIterator<T>` defines a stateful FIFO replay iterator over `Writable` values with `hasNext`, `next`, `replay`, `reset`, `add`, `close`, and `clear`. Implementations include `EMPTY`, `ArrayListBackedIterator`, and `StreamBackedIterator`.
- `ComposableInputFormat` refines `InputFormat` to require a `ComposableRecordReader`. `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding reader id, current key cloning, non-empty probing, skip-through-key behavior, and collector acceptance for join keys.
- `CompositeInputFormat` parses `mapred.join.expr`, supports default and user-defined join operators via `mapred.join.define.<ident>`, accepts a comparator through `mapred.join.keycomparator`, builds aligned `CompositeInputSplit` instances, creates composable readers, and has static `compose` helpers for `tbl(...)` and operator expressions.
- `CompositeInputSplit` aggregates child `InputSplit` instances, exposes per-child and aggregate length/location metadata, and serializes as count/classes/splits. Child splits must have public default constructors.
- `CompositeRecordReader` is the abstract base for joins over sorted, partition-compatible child readers. It owns a `JoinCollector` and child reader array, maintains a priority queue ordered by `WritableComparator`, fills collectors for matching keys, delegates skip/close/progress, creates common keys/internal tuple values, and leaves concrete join behavior to `combine`.
- `InnerJoinRecordReader`, `OuterJoinRecordReader`, `OverrideRecordReader`, `JoinRecordReader`, and `MultiFilterRecordReader` implement or refine join semantics. Inner join emits only full tuples, outer join emits union-style tuples, override behavior selects override values, `JoinRecordReader` emits `TupleWritable`, and `MultiFilterRecordReader` emits a derived writable value through abstract `emit`.
- `Parser` and nested `Node`, token, numeric/string token, node token, and `TType` classes implement a simple shift-reduce parser for join expressions. `Parser.Node` keeps a static identifier-to-record-reader-constructor map and per-node id, identifier, and comparator class.
- `TupleWritable` stores multiple `Writable` children with presence bits, supports `has`, `get`, `size`, equality/hash, iteration, string formatting, and serialization of count/types/objects. Its docs warn that it is join-framework-specific rather than a general-purpose tuple type.
- `WrappedRecordReader` adapts a normal `RecordReader` into `ComposableRecordReader`, caches the head key/value pair, supports skip and collector acceptance for matching keys, delegates creation/progress/position/close, and implements ordering/equality by head key comparison.

The beginning of `org.apache.hadoop.mapred.lib` covers reusable MapReduce building blocks:

- `ChainMapper` lets multiple mapper classes run inside a single map task, storing chain configuration through static `addMapper`, then invoking configured mappers in `configure`, `map`, and `close`.
- `ChainReducer` composes one reducer followed by zero or more mappers inside a reduce task, with static `setReducer` and `addMapper` plus runtime `configure`, `reduce`, and `close`.
- `DelegatingInputFormat` and `DelegatingMapper` support `MultipleInputs`, delegating splits and mapper behavior by input path.
- `FieldSelectionMapReduce` is both mapper and reducer for selecting delimited fields into output keys and values using `mapred.data.field.separator`, `map.output.key.value.fields.spec`, and `reduce.output.key.value.fields.spec`.
- `HashPartitioner` implements `Partitioner` using `Object.hashCode()`.
- `IdentityMapper` and `IdentityReducer` pass records through unchanged.
- `InputSampler` implements `Tool`, writes partition files for `TotalOrderPartitioner`, and provides command-line driver behavior. Nested sampler types include `IntervalSampler`, `RandomSampler`, `Sampler`, and the visible start of `SplitSampler`.

## Control Flow and Behavioral Contracts

The old MapReduce data path described by this chunk starts with `InputFormat` creating `RecordReader` instances over `InputSplit`s. `RecordReader.next` fills caller-provided reusable key/value objects until EOF, while `getProgress` and `getPos` report progress. Mapper output is partitioned through `Partitioner.getPartition`, shuffled and sorted by the framework, then passed to `Reducer.reduce` once per grouped key with an iterator of values. Reducers and long-running readers/writers are expected to use `Reporter` to report liveness, status, and counters.

Output flow is mediated through `OutputFormat`. The framework calls `checkOutputSpecs` at submission time to catch invalid output targets, then uses `getRecordWriter` to write task outputs. Text and SequenceFile output formats adapt this contract to line-oriented files or SequenceFiles, with `RecordWriter.close(Reporter)` serving as the finalization hook.

Job monitoring flow uses `JobClient` to obtain a `RunningJob`, then repeatedly queries progress and completion state, fetches counters/events, waits for completion, changes priority, or kills jobs/task attempts. `TaskCompletionEvent` supplies the event stream for completed task attempts, while `TaskReport` supplies current task diagnostics/progress/counters.

Task execution flow centers on `TaskTracker`. Its `run` method is documented as a server retry loop that reconnects to the JobTracker and reinitializes stale state. Child JVMs call `getTask`, then periodically invoke synchronized `statusUpdate`, `ping`, diagnostic reporting, commit-pending/done notifications, and error callbacks through the task umbilical protocol. Reduce tasks ask for map completion events and may report shuffle errors; map outputs are served by `MapOutputServlet`.

Skip-bad-record flow is attempt-driven. After the configured number of failed attempts, tasks report next record ranges to the TaskTracker so later attempts can skip suspect ranges. Counters named by `COUNTER_MAP_PROCESSED_RECORDS` and `COUNTER_REDUCE_PROCESSED_GROUPS` are central to range detection; automatic increments can be disabled for asynchronous or buffered applications such as streaming.

SequenceFile input flow varies by adapter. Binary readers expose raw bytes and class names, text readers stringify keys/values, filtered readers consult the configured `Filter.accept(key)` before emitting, and base record readers support seeking and synchronized read/close operations. Output flow can set persisted key/value metadata separately from actual `BytesWritable` values for raw binary writes.

Job-control flow is a dependency scheduler. `JobControl.run` repeatedly checks running jobs, promotes waiting jobs whose dependencies succeeded, submits ready jobs, and moves failures into failed/dependent-failed states. `Job.addDependingJob` is synchronized and allowed only while waiting, so dependencies are intended to be immutable once execution begins.

Join flow requires every child source to be sorted and partitioned identically. `CompositeInputFormat` parses the join expression, builds one composite split per aligned child-split index, and constructs a tree of composable readers. `CompositeRecordReader` keeps child readers in a priority queue by current key, fills a `JoinCollector` with values from children whose keys match, then concrete `combine` implementations decide whether a tuple/value should be emitted. Resetable iterators allow join collectors to replay values for nested or cross-product-style joins.

Chain mapper/reducer flow is in-task composition. Static configuration calls describe each mapper/reducer class, type transitions, per-stage `JobConf`, and pass-by-value versus pass-by-reference semantics. Runtime `configure` instantiates/configures the chain, `map` or `reduce` pipes records through the configured stages, and `close` tears all stages down.

Sampling flow for total-order partitioning calls a `Sampler` against an `InputFormat` and `JobConf`, sorts sampled keys with the job output key comparator, chooses partition boundary keys, and writes them to the partition file path from `TotalOrderPartitioner`. `RandomSampler`, `IntervalSampler`, and `SplitSampler` differ in how they choose records and splits.

## State, Persistence, and Side Effects

The XML itself is persistent API compatibility data for Hadoop 0.19.0. Runtime state represented by this chunk includes mutable job configuration, reader positions, writer output streams, reducer lifecycle state, reporter counters/status, running job state, task IDs, task completion events, task reports, task tracker daemon state, join parser/reader queues, tuple presence bits, job-control dependency and state tables, chain configuration, and sampler parameters.

Persistence and external effects are prominent. `OutputFormat` implementations validate and create filesystem outputs. Text and SequenceFile writers write to `FileSystem` paths. SequenceFile readers consume files and track byte positions. `SkipBadRecords` persists skip settings in `Configuration`/`JobConf` and writes skipped records under an output `_logs` subdirectory unless disabled. `TaskLog` resolves and mutates task log files under `hadoop.log.dir`, wraps commands to redirect stdout/stderr/debug output, may write pid files, and cleans old logs. `TaskLogServlet`, `StatusHttpServer.TaskGraphServlet`, and `TaskTracker.MapOutputServlet` write HTTP responses.

`TaskID`, `TaskAttemptID`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable` all implement Hadoop `Writable` serialization contracts. These serialized forms can cross RPC boundaries, be embedded in job/task metadata, or be persisted in intermediate data; method signatures and field ordering are compatibility-sensitive even though the XML does not show concrete field layouts.

`TaskTracker` has broad side effects: local disk cleanup on startup, shutdown of tasks/threads, communication with the JobTracker through `InterTrackerProtocol`, management of child JVM task assignment through `JvmManager`, task memory monitoring, task commit authorization, shuffle/map-output serving, and local filesystem error handling.

Join and chain APIs are stateful even when configured through static helpers. Join readers maintain cached head records, priority queues, `JoinCollector` iterators, parser constructor maps, and tuple writable values. Chain mapper/reducer configuration mutates `JobConf` so later task setup can reconstruct the pipeline.

Sampling and partition-file generation read input splits on the client side and write a partition file for `TotalOrderPartitioner`. `RandomSampler` explicitly warns that reading every split at the client can be expensive.

## Dependencies and Integration Points

The chunk is tightly integrated with the legacy `org.apache.hadoop.mapred` API: `JobConf`, `JobClient`, `RunningJob`, `InputFormat`, `InputSplit`, `FileSplit`, `FileInputFormat`, `FileOutputFormat`, `Mapper`, `Reducer`, `OutputCollector`, `Reporter`, `Counters`, `TaskStatus`, `TaskUmbilicalProtocol`, `InterTrackerProtocol`, `JvmManager`, `TaskMemoryManagerThread`, `MapTaskCompletionEventsUpdate`, and `SortedRanges.Range`.

Filesystem and IO dependencies include `org.apache.hadoop.fs.FileSystem`, `Path`, `PathFilter`, `FileStatus`, Java `DataInput`, `DataOutput`, `DataOutputStream`, `File`, and `IOException`. Sequence-file integration depends on `org.apache.hadoop.io.SequenceFile`, `SequenceFile.Reader`, `SequenceFile.ValueBytes`, `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, and compression type configuration.

Runtime services include Apache Commons Logging, log4j `FileAppender` and `LoggingEvent`, servlet APIs (`HttpServlet`, requests, responses, `ServletException`), Hadoop `HttpServer`, Java networking (`InetSocketAddress`), Java collections, Java regex (`PatternSyntaxException`), reflection constructors for join parser nodes/readers, and command-line tooling through `Tool`.

Configuration keys and integration points visible in docs include `mapred.task.timeout`, `mapred.join.expr`, `mapred.join.define.<ident>`, `mapred.join.keycomparator`, `mapred.data.field.separator`, `map.output.key.value.fields.spec`, `reduce.output.key.value.fields.spec`, and the partition-file path used by `TotalOrderPartitioner`.

Compatibility integration is also explicit: deprecated string identifiers in `RunningJob`, `TaskCompletionEvent`, `TaskReport`, `Job`, and task-kill APIs remain beside typed `JobID`, `TaskID`, and `TaskAttemptID` replacements.

## Risks and Compatibility Notes

This chunk starts in the middle of `OutputFormat` and ends in the middle of `InputSampler.SplitSampler`; adjacent chunks are required for complete per-file synthesis. Within this chunk, however, all listed class/interface blocks between those boundaries were read and summarized.

The XML describes public API, not implementation bodies. Behavioral detail comes from signatures, synchronization flags, inheritance, and Javadoc, so implementation-specific algorithms must be verified against Java source if exact code paths are needed.

The old MapReduce API relies heavily on object reuse. `RecordReader.next` fills caller-provided objects, and reducer docs explicitly warn that framework-provided keys/values are reused. User code that retains keys or values must clone them; changing reuse semantics would affect memory and compatibility.

Task and job identifier APIs are compatibility-sensitive. String formats such as `task_...` and `attempt_...`, `forName`, regex-pattern helpers, `Writable` serialization, equality, comparison ordering, and deprecated string accessors are all observable by clients and logs.

Several APIs expose raw or weakly typed generics (`Class`, raw `OutputCollector`, raw `Mapper`/`Reducer` in chain runtime methods, parser reflection maps). Tightening signatures could break source compatibility with Hadoop 0.19 clients.

Threading is mixed. Some critical `TaskTracker`, `Job`, and writer/reader methods are synchronized, but many mutable objects (`JobControl` lists, join readers/iterators, task events/reports, task logs, chain stages) are not documented as thread-safe. Callers should assume task-local or externally synchronized use unless the contract says otherwise.

Skip-bad-record behavior can silently drop data around deterministic failures. The thresholds and counters must be tested carefully because `Long.MAX_VALUE`, zero, automatic counter increments, and null skip-output path all have special behavior.

Join APIs assume identical sort order and partitioning across inputs. If split alignment, key comparator, partitioning, or child input sort order differs, `CompositeRecordReader` may miss matches, produce incorrect tuples, or report misleading progress. `TupleWritable` is explicitly not a general-purpose persistence format.

Chain mapper/reducer pass-by-reference mode is an optimization with mutation risk. A mapper or reducer that modifies key/value objects unexpectedly can corrupt downstream stages unless pass-by-value serialization is used.

`TaskLog.captureOutAndError`, task log serving, map output serving, and `InputSampler.RandomSampler` can be expensive or security-sensitive. They touch local files, shell command strings, stdout/stderr redirection, HTTP endpoints, and client-side reads over potentially large inputs.

`HashPartitioner` depends on `Object.hashCode()`. Keys with unstable, non-deterministic, or poorly distributed hash codes can skew reducers or route equivalent logical keys inconsistently.

## Test Signals

JDiff-level validation should confirm this XML chunk remains well-formed around the package/class boundaries it covers, preserves every class/interface listed here, and keeps method names, generic signatures, parameter order, declared exceptions, visibility, synchronization/static/final/abstract flags, fields, and deprecation text stable.

Core old-API MapReduce tests should cover `RecordReader` object creation/reuse, EOF behavior, position/progress, close idempotence; `RecordWriter.write/close`; output-spec validation failures; `Partitioner.getPartition` bounds; reducer iterator processing, reporter progress/counters/status, and object-cloning expectations.

Reporter and running-job tests should cover no-op `Reporter.NULL`, enum and string counters, map-only `getInputSplit` failure outside mappers, progress values for map/reduce/setup/cleanup, non-blocking completion checks, `waitForCompletion`, job/task kill paths, priority changes, task completion event pagination, and counter retrieval.

SequenceFile tests should cover binary raw read/write class metadata, raw `BytesWritable` payload sizes, text conversion with `toString`, filtered reads for MD5/percent/regex filters, filter configuration validation, compression type round trips, reader seek/position/progress, split boundaries, and output-spec checks.

Skip-bad-record tests should cover default attempt threshold, zero disables skipping, `Long.MAX_VALUE` accepts broad ranges, auto-increment flags for mapper/reducer counters, manual counter increments for buffered/asynchronous processing, null skip output path, and skipped-record output under `_logs`.

Task identity and event tests should cover `TaskID` and `TaskAttemptID` constructors, string formatting, `forName` valid/malformed/null inputs, regex pattern generation with null wildcards, map/reduce comparison ordering, `Writable` read/write round trips, deprecated string accessors, `TaskCompletionEvent.Status`, map-task helpers, and event equality/hash.

TaskTracker and logging tests should cover startup cleanup, shutdown/close cleanup, JobTracker reconnect behavior, child `getTask`, heartbeat/status update, diagnostics, next-record range reporting, commit-pending/can-commit/done flow, shuffle/filesystem error handling, map-output-lost reporting, idle detection, memory-manager enabled/disabled branches, task log file lookup, log sync/cleanup, command wrapping with tail length and pid file, log4j appender close/flush, log servlet URL construction, and HTTP serving of map outputs/task logs.

Text format tests should cover compressed versus uncompressed splitability, CR/LF line endings, byte-offset keys, reporter usage during line reading, text writer separator handling, null key/value output behavior if supported by implementation, synchronized writer close, and filesystem output path creation.

Job-control tests should cover dependency addition while waiting versus after start, state transitions among waiting/ready/running/success/failed/dependent-failed, assigned `JobID` propagation, failure message propagation, `JobControl` suspend/resume/stop, all-finished detection, concurrent synchronized additions, and the run loop submitting only ready jobs.

Join tests should cover parser expression composition, default and custom join identifiers, comparator configuration, malformed expressions, composite split serialization/deserialization, child split capacity errors, aligned split count requirements, inner/outer/override semantics, nested joins, resetable iterator FIFO/replay/reset/clear/close, tuple presence bits and serialization, wrapped reader head caching, skip-through-key behavior, and progress as the minimum of child readers.

Library helper tests should cover chain mapper/reducer type compatibility, pass-by-value versus pass-by-reference mutation behavior, per-stage `JobConf` precedence, close ordering, delegating input format/mapper path dispatch through `MultipleInputs`, field-selection separator and range grammar including open ranges, identity mapper/reducer pass-through, hash partition bounds/distribution, and `InputSampler` interval/random/split sampling plus partition-file output for `TotalOrderPartitioner`.
