# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 24771-30886

## Scope

This chunk is part 5 of the generated JDiff public API snapshot for Hadoop 0.18.3. It is compatibility metadata, not executable Java source. The XML records package boundaries, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, checked exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation text, and embedded Javadoc contracts.

The chunk starts inside the tail Javadoc for `org.apache.hadoop.mapred.TaskID`, then covers a large public API segment from MapReduce task logging and task-tracker APIs through `org.apache.hadoop.mapred.jobcontrol`, `org.apache.hadoop.mapred.join`, `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, `org.apache.hadoop.mapred.pipes`, and the beginning of Hadoop's metrics SPI. It ends inside `org.apache.hadoop.metrics.spi.MetricsRecordImpl`; the rest of that class is in the next chunk.

## Purpose and Major API Surface

The opening MapReduce section exposes task-side runtime APIs. `TaskLog` locates user-log files by string or `TaskAttemptID`, purges old logs, reads task log length from `JobConf`, and wraps child commands to capture stdout, stderr, and debug output. `TaskLog.LogName` is the user-log selector enum. `TaskLogAppender` is a log4j `FileAppender` for task child logs, with task-id and total-log-size log4j properties. `TaskLogServlet` serves task logs over HTTP from TaskTrackers.

`TaskReport` is a `Writable` task-status snapshot with task id, progress, state string, diagnostics, counters, start time, finish time, and `write`/`readFields` serialization. It preserves the deprecated string `getTaskId()` alongside `getTaskID()`.

`TaskTracker` is the central worker daemon API. It implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`, is constructed from `JobConf`, and exposes lifecycle (`run`, `shutdown`, `close`, `cleanupStorage`, `main`), JobTracker linkage (`getJobClient`, `getProtocolVersion`), child task lookup (`getTask` by string or `TaskAttemptID`), task heartbeat/status/reporting methods (`statusUpdate`, `reportDiagnosticInfo`, `ping`, `done`, `shuffleError`, `fsError`, `mapOutputLost`), map-completion lookup, idle state, bound report address, and metrics access. Nested classes include `TaskTracker.Child` for child-process entry, `MapOutputServlet` for serving intermediate map outputs to reducers, and `TaskTrackerMetrics` as a metrics `Updater`.

`TextInputFormat` and `TextOutputFormat` provide standard line-oriented MapReduce I/O. `TextInputFormat` is a `FileInputFormat<LongWritable,Text>` and `JobConfigurable`, with splitability and record-reader creation. `TextOutputFormat` creates `RecordWriter<K,V>` instances, and `TextOutputFormat.LineRecordWriter` writes key/value text lines to a `DataOutputStream`.

The `org.apache.hadoop.mapred.jobcontrol` package models dependent job DAGs. `Job` wraps `JobConf`, job name, internal string id, assigned `JobID`, state, message, dependencies, readiness/completion checks, and `submit()`. It retains deprecated string MapReduce job-id access while adding `JobID`-typed access. `JobControl` is a `Runnable` controller with waiting, ready, running, successful, and failed job lists; it adds single or multiple jobs, reports state, can stop/suspend/resume, checks `allFinished`, and drives the state machine in `run()`.

The `org.apache.hadoop.mapred.join` package exposes the old mapred composite-input join framework. `ComposableInputFormat` returns `ComposableRecordReader` instances. `ComposableRecordReader` combines `RecordReader` and `Comparable`, exposing reader id, current key, key-copying, `hasNext`, `skip`, and `accept` for join coordination. `CompositeInputFormat` parses join expressions, sets input format strings in `JobConf`, validates input, computes composite splits, creates composite readers, and offers static `compose` helpers. `CompositeInputSplit` aggregates child `InputSplit`s and serializes/deserializes them as one split.

`CompositeRecordReader` is the base join coordinator. It is configurable, holds child readers in a priority queue, uses a `WritableComparator`, adds child readers, computes current keys, skips keys, fills join collectors, accepts values into `ResetableIterator`s, compares readers, creates keys/internal tuple values, exposes position/progress, and closes resources. `JoinRecordReader`, `InnerJoinRecordReader`, and `OuterJoinRecordReader` implement tuple-producing joins. `MultiFilterRecordReader` and `OverrideRecordReader` implement filtered and rightmost-source preference behavior. `ArrayListBackedIterator`, `StreamBackedIterator`, `JoinDelegationIterator`, `MultiFilterDelegationIterator`, `ResetableIterator`, and `ResetableIterator.EMPTY` define replayable stateful iteration over writable values. `TupleWritable` is the joined tuple value with bitset-style presence tracking, size, get, iterator, `has`, `write`, `readFields`, and `toString`.

`Parser` and its nested token/node classes parse join expressions. The docs describe a simple stateless shift-reduce parser whose function-call grammar maps identifiers to parser node types and `ComposableRecordReader` constructors through `Parser.Node.addIdentifier`. Token classes model string, numeric, node, and enum token types; invalid token access can throw `IOException`.

The `org.apache.hadoop.mapred.lib` package exposes reusable mapper/reducer/input/output utilities. `FieldSelectionMapReduce` is both `Mapper` and `Reducer`, selecting output fields from input records. `HashPartitioner` partitions by key hash. `IdentityMapper`, `IdentityReducer`, `InverseMapper`, `LongSumReducer`, `RegexMapper`, and `TokenCountMapper` are standard small map/reduce components. `KeyFieldBasedPartitioner` partitions by key fields and exposes option parsing/configuration helpers. `MultipleOutputFormat` is an abstract output format that derives output filenames, actual keys, and actual values from each record; concrete `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` create sequence-file or text base writers. `MultithreadedMapRunner` runs mapper calls through a configurable thread pool and requires thread-safe mapper implementations. `NLineInputFormat` makes input splits containing N lines for parameter-sweep workloads. `NullOutputFormat` discards all outputs.

The `org.apache.hadoop.mapred.lib.aggregate` package provides the Aggregate framework. Primitive aggregators include `DoubleValueSum`, `LongValueMax`, `LongValueMin`, `LongValueSum`, `StringValueMax`, `StringValueMin`, `UniqValueCount`, and `ValueHistogram`. They implement `ValueAggregator`, accept object/string or primitive values as appropriate, reset state, emit report strings, and produce combiner/reducer output records. `ValueAggregatorDescriptor` generates aggregation id/value pairs from input key/value records and has public `TYPE_SEPARATOR` and `ONE` constants. `ValueAggregatorBaseDescriptor` provides common descriptor behavior, `generateEntry`, aggregator creation by type, default key/value-pair generation, and `JobConf` configuration. `UserDefinedValueAggregatorDescriptor` reflectively instantiates user plugin descriptors. `ValueAggregatorJob` builds and runs aggregate jobs, including overloads accepting descriptor classes and a `setAggregatorDescriptors` helper. `ValueAggregatorJobBase`, `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` implement the generic mapper/combiner/reducer flow around descriptor lists and type-driven aggregation.

`org.apache.hadoop.mapred.pipes.Submitter` is the public submitter for Hadoop Pipes jobs. It stores and reads the C++ executable URI, toggles whether record reader, mapper, reducer, and record writer are Java-side, controls whether the downlink command file is kept for debugging, modifies a `JobConf` for pipes execution during `submitJob`, and exposes a command-line `main`.

The metrics section defines Hadoop's original metrics API and SPI. `ContextFactory` is a singleton factory backed by attributes loaded from `hadoop-metrics.properties`; it creates named `MetricsContext` implementations by `<context>.class` or returns no-op null contexts. `MetricsContext` defines monitoring lifecycle, record creation, updater registration, and `DEFAULT_PERIOD`. `MetricsException` is a runtime exception. `MetricsRecord` offers typed tag setters, tag removal, typed metric setters and incrementers, plus `update` and `remove`. `MetricsUtil` wraps context and record creation. `Updater` is the callback interface.

Metrics implementations in this chunk include `metrics.file.FileContext`, `metrics.ganglia.GangliaContext`, `metrics.jvm.EventCounter`, `metrics.jvm.JvmMetrics`, and `metrics.spi.AbstractMetricsContext`. `FileContext` emits metrics records to a file or stream and flushes. `GangliaContext` emits metrics to Ganglia. `EventCounter` is a log4j appender that counts fatal/error/warn/info events. `JvmMetrics` registers as an updater for JVM process/session metrics. `AbstractMetricsContext` implements the common metrics table, period timer, monitoring lifecycle, updater registration, record creation, record update/remove buffering, attribute lookup, and abstract `emitRecord`. `MetricsRecordImpl` begins here as the concrete `MetricsRecord` implementation that delegates `update()` and `remove()` to its owning `AbstractMetricsContext`.

## Control Flow and Behavioral Contracts

Task execution flow is reflected by `TaskTracker` and `TaskLog`. A TaskTracker starts with a `JobConf`, cleans local storage on startup, enters a retrying `run()` loop to connect to the JobTracker, serves child tasks through `getTask`, receives task status through the `TaskUmbilicalProtocol` methods, and reports task completion or failure signals. Child JVMs interact through `TaskTracker.Child`, log output through `TaskLog` wrappers and `TaskLogAppender`, and expose logs through `TaskLogServlet`.

Map output fetch flow uses `TaskTracker.MapOutputServlet` and `getMapCompletionEvents`: reducers query completion events, then request map outputs over HTTP. `shuffleError`, `mapOutputLost`, and `fsError` are explicit feedback channels from tasks to the TaskTracker when local output or filesystem state becomes invalid.

Job-control flow is a state machine over dependent `Job` objects. `JobControl.run()` moves jobs from waiting to ready when dependencies complete, submits ready jobs, tracks running jobs through success/failure, and stops when instructed. `Job.isReady()` and `Job.isCompleted()` are the dependency gates.

Join flow starts with a composed expression string in `CompositeInputFormat`, parsed by `Parser` into node objects that know which `ComposableRecordReader` constructor to instantiate. Composite splits align child input splits. Composite readers coordinate child readers by comparable keys, collect per-key value streams in `ResetableIterator`s, and call `combine` in inner, outer, override, or custom reader subclasses to decide whether a tuple/value should be emitted.

Mapred library flow is mostly adapter based. Utility mappers and reducers transform input records into output records through the standard `map` and `reduce` callbacks. `MultipleOutputFormat` wraps a base writer selection flow: derive an output filename from key/value/input name, derive actual key/value, obtain or reuse the base writer, then write to separate named files. `MultithreadedMapRunner` parallelizes mapper calls over a thread pool, so mapper and collector interactions must be safe for concurrent use.

Aggregate flow is data driven. User or base descriptors convert each input record into one or more `Text` key/value pairs where the key encodes aggregation type and id. The mapper emits those pairs; the combiner and reducer inspect type prefixes, create the correct `ValueAggregator`, feed all values into it, and emit either combiner output or final report strings. `ValueAggregatorJob` assembles the `JobConf` and optional `JobControl` wrappers around this generic pipeline.

Pipes flow mutates a `JobConf` so Hadoop launches an external executable and decides which pipeline components are implemented in Java versus the pipes child process. When debugging is enabled, the command/downlink file is preserved and can be replayed by setting `hadoop.pipes.command.file`.

Metrics flow starts at `ContextFactory.getFactory()`, which reads classpath properties into attributes. `getContext(name)` constructs or reuses a context, defaulting to a null context if no implementation class is configured. Producers create `MetricsRecord`s, set tags and metrics, call `update` to buffer rows or `remove` to delete matching rows, while `Updater` callbacks run at the context period. `AbstractMetricsContext` periodically calls updaters, emits buffered records through subclass `emitRecord`, and then calls `flush`.

## State, Persistence, and Side Effects

The XML file itself is persisted API compatibility state. Runtime state described by the APIs includes TaskTracker local storage, running task maps, task status and diagnostics, user-log files, task counters, job dependency lists, join parser constructor maps, replayable join iterator buffers, tuple presence bits, multiple-output writer caches, aggregate descriptor lists, aggregator accumulators, pipes configuration flags, metrics factory attributes, metrics contexts, buffered metric rows, registered updaters, JVM/log event counters, and metrics output destinations.

External side effects include purging and writing task logs, serving logs and map outputs over HTTP, cleaning TaskTracker temporary storage, starting child JVMs and external pipes processes, mutating `JobConf` objects, reading/writing split and report data through Hadoop `Writable`, writing multiple output files, reading input files for line-based formats, writing metrics to files or network endpoints, loading metrics properties from the classpath, and reflectively instantiating user classes for join readers, aggregate descriptors, and metrics contexts.

Many APIs are mutable and not documented as thread-safe. Explicit synchronization appears on selected TaskTracker lifecycle/status methods, `TaskLog.cleanup`, metrics factory/context creation and monitoring methods, but job-control lists, aggregate objects, resettable iterators, parser registries, multiple-output writer state, and many metrics records are caller-managed mutable state.

## Dependencies and Integration Points

This chunk is deeply integrated with the old `org.apache.hadoop.mapred` API: `JobConf`, `JobID`, `TaskID`, `TaskAttemptID`, `Task`, `TaskStatus`, `TaskCompletionEvent`, `Counters`, `Reporter`, `RecordReader`, `RecordWriter`, `InputSplit`, `InputFormat`, `OutputFormat`, `OutputCollector`, `Mapper`, `Reducer`, `MapRunnable`, `RunningJob`, `JobClient`, and `InterTrackerProtocol`.

Filesystem and I/O dependencies include `FileSystem`, `Path`, `DataInput`, `DataOutput`, `DataOutputStream`, `File`, servlet request/response classes, log4j appenders/events, Java reflection, Java collections, `Writable`, `WritableComparable`, `WritableComparator`, `Text`, `LongWritable`, and `Progressable`.

Cluster integration points are the TaskTracker to JobTracker RPC protocols, TaskUmbilical child communication, HTTP map-output shuffle and task-log serving, JobControl orchestration, Pipes executable submission, and metrics sinks such as file and Ganglia. Configuration keys mentioned in docs include `mapred.map.multithreadedrunner.threads`, `num.of.trailing.legs.to.use`, and pipes command-file/debug settings.

The metrics SPI bridges public metrics records to concrete sinks. `ContextFactory` resolves implementation classes from `hadoop-metrics.properties`; `AbstractMetricsContext` is the common base for `FileContext`, `GangliaContext`, and null/no-op contexts in adjacent code.

## Risks and Compatibility Notes

Because this is a JDiff snapshot, signature shape is the main contract. Changing method overloads, parameter types, exception declarations, visibility, static/final/abstract/synchronized flags, deprecation text, or field constants can break source or binary compatibility even when implementation behavior is unchanged.

This chunk has boundary caveats: it begins after the `TaskID` class declaration and ends before `MetricsRecordImpl` closes. Adjacent chunks are needed for the complete `TaskID` and `MetricsRecordImpl` API records.

Several APIs preserve legacy string identifiers beside typed IDs. `TaskReport.getTaskId`, `TaskTracker` string overloads, and job-control string job IDs are deprecated or legacy but still part of the compatibility surface. Removing them would break old 0.18-era mapred applications.

TaskTracker APIs are operationally sensitive. Incorrect status, ping, completion, shuffle-error, or map-output-lost behavior can cause duplicate task attempts, lost diagnostics, stuck reducers, or stale local storage. Log capture wrappers also have shell quoting and output truncation risks because they build command lists around user commands.

Join APIs rely on sorted compatible keys, correct comparator classes, and replayable iterator semantics. `ResetableIterator.reset()` must be called after additions to avoid concurrent modification issues. Parser extension is fragile by its own docs: the shift-reduce parser has no states and treats parentheses as function calls, making grammar extensions risky.

`MultipleOutputFormat` can create many output files and depends on stable filename derivation. Bad key-derived paths, input-file-name derivation, or writer caching can create invalid paths, collisions, excess files, or leaked writers.

`MultithreadedMapRunner` is only safe for thread-safe mappers. Legacy mappers that mutate shared fields, reuse output objects unsafely, or assume single-threaded reporter/collector behavior may fail nondeterministically.

Aggregate APIs parse numbers and type prefixes from text. Bad input strings, overflow, malformed histogram values, descriptor class-loading failures, or mismatched combiner/reducer output formats can produce incorrect statistics or runtime failures. Some methods return raw `ArrayList`, `Set`, or `TreeMap`, so generic type tightening would be incompatible.

Pipes and metrics both invoke external or pluggable code. Pipes jobs depend on executable URIs and Java/native component flags being consistent. Metrics contexts depend on classpath property configuration and reflective construction; a bad `<context>.class` can throw checked reflection exceptions or silently fall back only when no class is configured.

## Test Signals

JDiff validation should verify this XML chunk remains well-formed with adjacent chunks, and that all package/class/interface records listed above preserve names, inheritance, implemented interfaces, constructors, methods, params, exceptions, fields, visibility, flags, and deprecation annotations.

Task runtime tests should cover `TaskLog` file lookup by string and `TaskAttemptID`, log retention cleanup, log-length configuration, stdout/stderr/debug command wrapping and quoting, `TaskLogAppender` close/size behavior, `TaskLogServlet` responses, `TaskReport` `Writable` round trips, and TaskTracker protocol flows for status, ping, done, diagnostics, shuffle errors, fs errors, map-output lost, map-completion queries, idle state, shutdown, and cleanup.

JobControl tests should build dependency DAGs with successful, failed, waiting, ready, running, suspended, resumed, and stopped jobs, checking state transitions, dependency readiness, ID assignment, and `allFinished()`.

Join tests should cover parser compose/parse round trips, custom identifier registration, split serialization, child split length/location aggregation, inner and outer joins, override joins preferring rightmost sources, tuple `has/get/iterator/write/readFields`, comparator ordering, skip behavior, reset/replay iterator order, stream-backed iterator cleanup, and malformed expression errors.

Mapred library tests should cover identity/inverse/token/regex/field-selection mappers and reducers, hash and key-field partitioning, multiple-output filename/key/value derivation, text and sequence multiple writers, null output behavior, N-line splitting for exact and trailing line counts, and multithreaded mapper execution with both safe and unsafe mapper examples.

Aggregate tests should cover each built-in aggregator's add/report/reset/combiner output behavior, numeric parsing failures, unique-count limits, histogram statistics and details, descriptor `generateEntry` and type mapping, user-defined descriptor reflection/configuration, mapper emission from descriptor lists, combiner aggregation, reducer final reports, and `ValueAggregatorJob` job-conf generation with generic Hadoop args.

Pipes tests should assert configuration round trips for executable URI, Java record reader/mapper/reducer/record writer booleans, keep-command-file behavior, `submitJob` mutations, and command-line submission failure reporting for missing executables or invalid args.

Metrics tests should cover singleton factory initialization from `hadoop-metrics.properties`, attribute set/remove/list behavior, null context creation, configured context reflection errors, start/stop/close lifecycle, updater registration/unregistration and periodic callbacks, record creation constraints, tag and metric typed setters/incrementers, update/remove row matching, file sink emission and flush, Ganglia emission hooks, log4j event counters by severity, JVM metrics updater output, and `MetricsRecordImpl` delegation to `AbstractMetricsContext`.
