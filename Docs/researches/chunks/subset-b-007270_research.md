# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 31138-37297

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not implementation source. The range starts inside the public API entry for `org.apache.hadoop.mapred.TaskTracker`, then completes several `mapred` utility APIs, covers the full `org.apache.hadoop.mapred.jobcontrol` package, most of `org.apache.hadoop.mapred.join`, `org.apache.hadoop.mapred.lib`, `org.apache.hadoop.mapred.lib.aggregate`, the Pipes job submitter, and the original Hadoop metrics API and SPI through the beginning of `org.apache.hadoop.metrics.util.MetricsLongValue`.

The XML records compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, exceptions, visibility/static/final/synchronized flags, deprecation notes, fields, and embedded Javadocs. Research below is based on those signatures and contracts. This is a line-bounded chunk: `TaskTracker` began before this range, and `MetricsLongValue` continues after it.

## Purpose and major API surface

The initial `org.apache.hadoop.mapred` section finishes `TaskTracker` APIs for cleanup, shutdown, task-child RPC, task status, diagnostics, heartbeat pings, task completion, shuffle and local filesystem error reporting, map-output-loss notifications, map completion event lookup, idle checks, and process startup. Nested `TaskTracker.Child` is the child-process `main`, `TaskTracker.MapOutputServlet` serves map outputs from the TaskTracker's Jetty HTTP server, and `TaskTracker.TaskTrackerMetrics` is a periodic metrics updater. The same package also exposes `TextInputFormat`, `TextOutputFormat`, and `TextOutputFormat.LineRecordWriter` for line-oriented text input/output, with text input keys as file offsets and values as lines.

`org.apache.hadoop.mapred.jobcontrol.Job` models a MapReduce job plus its dependency list. It tracks Hadoop job configuration, a JobControl-local ID, assigned MapReduce `JobID`, user message, dependency jobs, and states `WAITING`, `READY`, `RUNNING`, `SUCCESS`, `FAILED`, and `DEPENDENT_FAILED`. Deprecated string mapred job ID accessors coexist with typed `JobID` accessors. `JobControl` is a `Runnable` manager for a group of these jobs, assigning IDs, exposing lists of waiting/running/ready/successful/failed jobs, adding jobs or collections of jobs, and controlling its worker thread through run, stop, suspend, resume, state lookup, and all-finished checks.

`org.apache.hadoop.mapred.join` provides old MapReduce-side sorted join support. `ComposableInputFormat` refines `InputFormat` to return `ComposableRecordReader`; `ComposableRecordReader` extends `RecordReader` and `Comparable`, adding reader IDs, access to the current head key, key cloning, availability checks, skipping through keys, and accepting matching records into a join collector. `CompositeInputFormat` parses `mapred.join.expr`, default and user-defined join operators, table expressions, input paths, and join key comparator configuration; it validates child inputs, builds `CompositeInputSplit` arrays by aligning child splits, and constructs composable record readers. Static `compose` helpers build expression strings.

`CompositeInputSplit` serializes/deserializes a fixed collection of child splits, reports aggregate and per-child lengths, and unions child split locations. `CompositeRecordReader` is the abstract base for joins, managing child record-reader queues, key comparison, configuration, progress, position, close, child initialization, and a `combine` hook for subclasses. `JoinRecordReader`, `InnerJoinRecordReader`, and `OuterJoinRecordReader` build tuple-valued joins; `MultiFilterRecordReader` and `OverrideRecordReader` reduce multiple sources to one value stream. Parser classes (`Parser`, `Node`, `Token`, `NodeToken`, `NumToken`, `StrToken`, `TType`) describe the expression parser for composite joins.

Join buffering is represented by `ResetableIterator`, `ArrayListBackedIterator`, `StreamBackedIterator`, and `ResetableIterator.EMPTY`. The contract is FIFO replay after `reset`, `replay` of the last returned value, explicit `add`, `clear`, and `close`, with stream-backed storage preferred over the array-list implementation. `TupleWritable` is a `Writable`/`Iterable` container for heterogeneous writable children, preserving which tuple positions are populated and serializing count, element types, and objects. `WrappedRecordReader` adapts a normal `RecordReader` into the composable join protocol while caching the current head key/value and collecting values that match a join key.

`org.apache.hadoop.mapred.lib` supplies stock mapred helpers. `FieldSelectionMapReduce` performs configurable field selection over key/value text using `mapred.data.field.separator`, map output field specs, and reduce output field specs. `HashPartitioner` partitions by `Object.hashCode`; `KeyFieldBasedPartitioner` is a configurable partitioner with the same visible partitioning contract in this snapshot. `IdentityMapper`, `IdentityReducer`, `InverseMapper`, and `LongSumReducer` implement common pass-through, key/value swap, and long-summing behavior. `MultipleOutputFormat` routes output records to multiple files by overriding generated leaf names, file names for key/value pairs, actual keys/values, and input-file-based output names; `MultipleSequenceFileOutputFormat` and `MultipleTextOutputFormat` provide sequence-file and text implementations. `MultithreadedMapRunner`, `NLineInputFormat`, `NullOutputFormat`, `RegexMapper`, and `TokenCountMapper` round out utility mapred components for parallel map execution, fixed-line splits, no-output jobs, regex extraction, and token counting.

`org.apache.hadoop.mapred.lib.aggregate` is the old Aggregate framework for common counting/statistics jobs. Value aggregators include numeric sum/max/min classes, string max/min, unique value counting, and histograms. The `ValueAggregator` interface exposes `addNextValue`, reporting, combiner output, and reset. `ValueAggregatorDescriptor` generates aggregation ID/value pairs from input records, with a type separator and common `ONE` value. `UserDefinedValueAggregatorDescriptor` and `ValueAggregatorBaseDescriptor` provide descriptor implementations and plugin loading. `ValueAggregatorMapper`, `ValueAggregatorCombiner`, and `ValueAggregatorReducer` implement generic map/combine/reduce stages over `Text` aggregation keys and values; `ValueAggregatorJob` creates and submits configured aggregate jobs; `ValueAggregatorJobBase` stores configured descriptor lists and shared lifecycle behavior.

`org.apache.hadoop.mapred.pipes.Submitter` is the command-line/API entry point for Hadoop Pipes jobs. It gets and sets the executable URI, chooses whether record reader, mapper, reducer, and record writer are Java or non-Java components, controls retention of the downlink command file for debugging, mutates a `JobConf` for Pipes execution, submits it as a `RunningJob`, and exposes `main`.

The metrics packages define Hadoop's original metrics system. `ContextFactory` is a singleton configured from `hadoop-metrics.properties`, stores attributes, and constructs named `MetricsContext` instances by reflective `<contextName>.class` configuration or defaults to `NullContext`. `MetricsContext` manages lifecycle, records, periodic updater registration, and `DEFAULT_PERIOD`. `MetricsRecord` is the typed tag/metric update API with setters for string/integer/long/short/byte tags, setters and incrementers for numeric metrics, `update`, and `remove`. `MetricsUtil` simplifies context lookup and host-tagged record creation, and `Updater` is the periodic callback interface.

Provider packages include `FileContext`, which appends metrics to a configured file or stdout and flushes/closes the writer; `GangliaContext`, which emits metrics records to Ganglia; and JVM metrics classes. `EventCounter` is a Log4J appender that counts fatal, error, warn, and info events. `JvmMetrics` is a singleton `Updater` that periodically emits JVM metrics for a process/session.

`org.apache.hadoop.metrics.spi.AbstractMetricsContext` is the provider base class. It initializes from `ContextFactory`, exposes context attributes and attribute tables, starts/stops monitoring with a timer period, creates final public `MetricsRecord` instances, registers/unregisters updaters, keeps the internal buffered metric table, delegates provider output to abstract `emitRecord`, and allows subclasses to override `flush` and record creation. `MetricsRecordImpl` backs the public record API and delegates `update`/`remove` to its context. `MetricValue` distinguishes absolute and incremental numbers. `NullContext` discards metrics entirely; `NullContextWithUpdateThread` keeps periodic updater calls while suppressing output, useful when another system such as JMX samples state. `OutputRecord` is the emitted tag/metric view, and `Util.parse` parses comma/space-separated host[:port] lists.

`org.apache.hadoop.metrics.util` starts with `MBeanUtil`, which registers/unregisters MBeans under the standard Hadoop `hadoop.dfs:service=...,name=...` naming convention, and `MetricsIntValue`, a synchronized helper for a non-time-varied int metric that pushes only once after updates while JMX reads through `get()`. The chunk ends during the analogous `MetricsLongValue` API after constructor, `set`, `get`, `inc`, and the start of `dec`.

## Control flow and behavioral contracts

TaskTracker control flow is task-child and JobTracker coordinated. Startup can clean temporary storage from previous runs; `run()` is a retry loop that reconnects to the JobTracker when TaskTracker state becomes stale; child processes call back to fetch `Task` data, report progress, send diagnostics, ping the parent, mark completion, and report shuffle/filesystem/map-output failures. Shutdown and close are synchronized lifecycle boundaries that stop tasks/threads and clean local disk state so a TaskTracker can restart in the same JVM.

JobControl flow is dependency-driven. A `Job` starts in `WAITING`; if it has no dependencies or all dependencies reach `SUCCESS`, it becomes `READY`; dependency failure moves it to `DEPENDENT_FAILED`; successful submission moves it to `RUNNING`; runtime completion moves it to `SUCCESS` or `FAILED`. The `JobControl.run()` loop checks running jobs, updates waiting jobs, and submits ready jobs. Dependency additions are only accepted while a job is still waiting.

Composite join flow starts from a join expression in `mapred.join.expr` or one built with `CompositeInputFormat.compose`. The input format parses the expression, validates child inputs, obtains child splits, aligns the ith split from each child into a `CompositeInputSplit`, and constructs a tree of composable record readers. Readers compare head keys, skip through sorted streams, collect all values matching a key into resettable iterators, and subclasses combine child values into either tuple outputs or filtered single-value outputs. The contracts assume participating data sources are sorted and partitioned the same way.

Resettable iterator flow is stateful: callers `add` values, call `reset` before replaying, use `next` to copy successive writable values into caller-provided objects, and can `replay` the last returned value. `close` releases resources and makes later calls undefined; `clear` releases current data sources while preserving reusable internal resources.

Mapred library flows are conventional MapReduce pipelines. Field selection parses configured field specs and emits selected key/value text fields in map and reduce phases. Multiple output routing creates a composite writer; each output record can derive a destination file name and transformed key/value before delegation to a base writer. Aggregate jobs map each input record through configured descriptors into aggregation-type-prefixed IDs, combine values of the same aggregation key, and reduce them into final reports.

Pipes submission flow mutates the supplied `JobConf` to include executable and Java/non-Java component choices, optionally keeps a command file for debugging, then submits to the MapReduce cluster. The command-file debugging path depends on task-directory retention settings and the `hadoop.pipes.command.file` environment variable when replaying externally.

Metrics flow is provider driven. A client obtains the singleton `ContextFactory`, gets or creates a named context, creates records, sets tags/metrics, calls `update`, and starts monitoring. Contexts periodically call registered `Updater` instances, buffer rows keyed by record name and tag values, emit rows each period through provider-specific `emitRecord`, then flush. `remove` deletes rows matching a record's tags, and `stopMonitoring` pauses emission without necessarily freeing buffered rows; `close` stops and resets buffered state.

## State, persistence, and side effects

The JDiff XML itself is persistent API compatibility data. Runtime persistence described by this chunk includes TaskTracker local temporary storage, task process state, map output files served by Jetty, child-to-parent task status, JobTracker RPC state, text output files, serialized input splits and tuples, aggregate framework output, Pipes command files, metrics configuration attributes, metrics buffers, metrics files, Ganglia network packets, log event counters, JVM metrics records, and JMX MBean registrations.

TaskTracker APIs are state-heavy and partially synchronized. They expose task tables, report address binding, task status updates, diagnostics, failure notifications, map completion event state, idle detection, cleanup, and restart-oriented shutdown semantics. Correctness depends on coordinated cleanup of local disk and child processes.

JobControl maintains multiple tables/lists of jobs by state, a group-local ID space, per-job dependency lists, Hadoop-assigned job IDs, messages, and thread state. The public getters return `ArrayList` views in this old API surface, so caller mutation and synchronization are compatibility concerns unless implementations defensively copy.

Join APIs store parser trees, child split collections, current head key/value for each wrapped reader, priority queues of readers sorted by key, tuple populated-position bits, and resettable value buffers. `CompositeInputSplit` and `TupleWritable` both have explicit binary serialization formats that are part of job submission/task execution compatibility.

Mapred utility classes persist configuration-driven behavior in `JobConf`: field separators/specs, multiple-output filename derivation, input-file trailing-leg count, multithreaded runner settings, regex/token settings, aggregate plugin descriptors, and Pipes executable/component flags. Aggregate objects keep running sums, extrema, unique sets, and histograms; histogram reports can include full value/frequency detail.

Metrics APIs maintain global singleton factory state, context attributes from `hadoop-metrics.properties`, monitoring timers, registered updater lists, per-context buffered metric tables, record tag/metric maps, absolute vs incremental metric values, provider output handles, and MBean registrations. `MetricsIntValue` and the visible portion of `MetricsLongValue` use synchronized access around mutable counters and an updated-since-last-push flag implied by the push contract.

## Dependencies and integration points

TaskTracker integrates with `JobTracker` through `InterTrackerProtocol`, child task processes, `TaskAttemptID`, `TaskStatus`, `TaskCompletionEvent`, local filesystem storage, Jetty/servlet APIs, and the metrics framework.

Text input/output integrate with `FileInputFormat`, `FileOutputFormat`, `RecordReader`, `RecordWriter`, `LongWritable`, `Text`, `FileSystem`, `Path`, `JobConf`, `Reporter`, `Progressable`, and `DataOutputStream`.

JobControl depends on `JobConf`, `JobID`, `RunningJob`-style MapReduce execution, Java `Runnable`, collections, and `IOException`. It is an orchestration layer above classic `org.apache.hadoop.mapred`.

The join package integrates with `InputFormat`, `InputSplit`, `RecordReader`, `Reporter`, `Writable`, `WritableComparable`, `WritableComparator`, `WritableUtils`-style serialization, `Configuration`, `Path`, Java `PriorityQueue`, arrays/collections, and expression parsing. It depends on sorted, identically partitioned inputs and reflectively loaded input formats/join operators.

The utility MapReduce package integrates with `Mapper`, `Reducer`, `Partitioner`, `OutputCollector`, `Reporter`, `MapReduceBase`, `SequenceFileOutputFormat`, `TextOutputFormat`, text and sequence inputs, regex APIs, and job configuration properties.

The aggregate framework integrates with the same old `mapred` Mapper/Reducer APIs, `Text`, `Writable`, `WritableComparable`, `JobControl`, generic Hadoop option parsing, plugin descriptor classes, and collection types such as `ArrayList`, `Map.Entry`, and `TreeMap`.

Pipes integrates Java MapReduce submission with non-Java executable URIs, HDFS-distributed binaries, Java/non-Java component toggles, task local directories, command files, and `RunningJob`.

Metrics integrates with `hadoop-metrics.properties`, reflective provider construction, file IO, Ganglia, Log4J appenders/events, JVM runtime metrics, JMX MBeans, `InetSocketAddress` parsing, and Hadoop components such as DataNode/TaskTracker that register periodic `Updater`s.

## Risks and compatibility notes

This chunk has partial boundaries. Earlier `TaskTracker` fields and methods are outside the range, and `MetricsLongValue` is incomplete here, so final per-file reconciliation needs adjacent chunks before making whole-class conclusions for those two classes.

The JDiff file is a compatibility artifact. Changes to signatures, visibility, generic type parameters, exception declarations, field constants, deprecation metadata, or embedded contracts can represent source or binary compatibility changes for old Hadoop clients.

TaskTracker APIs are concurrency and lifecycle sensitive. Misordered shutdown, stale JobTracker reconnect state, unsynchronized status transitions, or failure-report handling can leak child processes, lose diagnostics, leave map outputs behind, or make restarts in the same JVM unsafe.

JobControl depends on correct state transitions and dependency semantics. Allowing dependency mutation after submission, misclassifying dependent failures, or failing to stop/suspend/resume the worker loop correctly can submit jobs too early, never submit ready jobs, or leave orchestration threads running.

Composite joins are fragile around input assumptions. Inputs must be sorted and partitioned identically, child split counts must align, configured key comparators must match the serialized key type, and parser expressions must resolve reflectively. Incorrect resettable-iterator ordering or head-key comparison can duplicate or drop joined records.

Serialization formats for `CompositeInputSplit` and `TupleWritable` are externally visible during job submission and task execution. Changing class-name encoding, count ordering, child split ordering, tuple type ordering, or populated-slot semantics would break old jobs.

`MultipleOutputFormat` can create many output files and derives names from keys, values, and input paths. Bugs in path derivation or user overrides can collide files, create invalid paths, or expose unexpected input path fragments in output layout.

Aggregate framework keys encode aggregation type and ID in text. Bad descriptor output, separator collisions, malformed histogram value/frequency strings, or inconsistent combiner/reducer report formats can produce incorrect statistics.

Pipes job submission mutates the supplied `JobConf` and coordinates Java with external executables. Risks include missing executable URIs, wrong Java/non-Java toggles, unavailable distributed binaries, command-file leakage when debugging, and failure to preserve task directories needed for replay.

Metrics APIs are highly stateful. Provider construction falls back to `NullContext`, so configuration mistakes can silently discard metrics if callers use `MetricsUtil`. Periodic updater thread safety, record-row matching by tags, incremental vs absolute metric handling, `stopMonitoring` vs `close`, file append behavior, Ganglia network failures, and MBean naming collisions all matter for observability correctness.

## Test signals

JDiff validation should ensure this XML range remains well formed around partial boundaries and preserves package/class/interface boundaries, constructor and method signatures, generic parameter text, declared exceptions, synchronized/static/final flags, field constants, deprecation text, and Javadocs.

TaskTracker tests should cover cleanup-on-startup, shutdown/close idempotence, child `getTask`, periodic `statusUpdate`, diagnostic reporting, ping liveness, task `done`, shuffle/fs/map-output error handling, map completion event lookup, idle detection, report address binding, map-output servlet responses, and metrics updater registration.

Text format tests should cover splitability decisions, line reader behavior for linefeed/carriage return, offset keys, record writer separators, synchronized line writes, close behavior, and interaction with configured output paths.

JobControl tests should cover dependency graph state transitions, dependency failure propagation, rejection of dependency additions after waiting state, job ID assignment, typed assigned `JobID` accessors, deprecated string ID accessors, run-loop submission of ready jobs, suspend/resume/stop, all-finished detection, and list getters by state.

Join tests should cover expression parsing and `compose`, user-defined join operators, invalid expressions, child input validation, split-count alignment, `CompositeInputSplit` serialization and location aggregation, inner/outer/override join semantics, comparator configuration, skip/accept behavior, resettable iterator FIFO replay, `clear` vs `close`, stream-backed buffering, `TupleWritable` has/get/iterator/string/write/readFields, and wrapped reader head-key comparison/progress/position forwarding.

Mapred utility tests should cover identity mapper/reducer passthrough, inverse mapper swapping, hash and key-field partitioning, long summing, field selection specs including ranges and open ranges, multiple-output filename/key/value overrides, input-file-based output naming, sequence/text multiple-output writers, multithreaded map runner behavior, N-line split generation, null output writer behavior, regex extraction, and token count emission.

Aggregate tests should cover each numeric/string/unique/histogram aggregator, malformed inputs, combiner output round trips into reducers, descriptor plugin configuration, generated aggregation ID/value pairs, mapper iteration across descriptor lists, reducer report output, job creation with and without explicit descriptor classes, and integration with `JobControl`.

Pipes tests should cover executable get/set, Java component toggles for record reader/mapper/reducer/record writer, command-file retention configuration, `submitJob` mutation of `JobConf`, missing executable failures, command-line parsing in `main`, and debugging replay expectations around `downlink.data`.

Metrics tests should cover `ContextFactory` singleton loading from `hadoop-metrics.properties`, attribute set/remove/table behavior, reflective context creation and null fallback, context lifecycle start/stop/restart/close, updater registration/unregistration and periodic calls, record creation and host tagging, tag/metric setter overloads, incremental vs absolute metrics, atomic update behavior across separate records with matching tags, remove semantics, provider emit/flush behavior for file and Ganglia contexts, Log4J event counts, JVM metrics singleton initialization, `OutputRecord` lookup views, server-spec parsing defaults, MBean register/unregister naming, and synchronized `MetricsIntValue` plus visible `MetricsLongValue` counter operations.
