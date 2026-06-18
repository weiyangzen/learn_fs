# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 25081-31138

## Scope

This chunk is a JDiff API XML slice for Hadoop 0.17.0. It begins inside `org.apache.hadoop.mapred.JobStatus`, covers most of the public old `mapred` package surface from `JobSubmissionProtocol` through `TextOutputFormat`, includes the `org.apache.hadoop.mapred` package overview, then covers `org.apache.hadoop.mapred.jobcontrol` and most of `org.apache.hadoop.mapred.join` through the start of `WrappedRecordReader`.

Because this source is generated API metadata, the research describes exported classes, interfaces, fields, method signatures, and Javadoc contracts rather than implementation bodies. Control-flow and state notes are inferred from method names, synchronization flags, inheritance, writable serialization methods, and embedded documentation.

## Purpose

The chunk documents Hadoop's pre-YARN MapReduce public API and daemon-facing protocols. It spans:

- Client to JobTracker RPC through `JobSubmissionProtocol` and its `JobTracker` implementation.
- JobTracker and TaskTracker process APIs, heartbeats, task assignment, task completion events, task logs, diagnostic reporting, and status web UI hooks.
- User-facing MapReduce programming interfaces: `Mapper`, `Reducer`, `MapRunnable`, `MapRunner`, `Partitioner`, `OutputCollector`, `Reporter`, `RecordReader`, `RecordWriter`, `InputFormat` and `OutputFormat` variants.
- File and sequence-file input/output adapters, text line readers, key-value line readers, multi-file splits, map-file outputs, and output compression settings.
- Higher-level job dependency orchestration in `mapred.jobcontrol`.
- Composable/join input APIs in `mapred.join`, including join expression parsing, composite splits/readers, resettable value iterators, and tuple serialization.

The package-level documentation in this range also states the classic MapReduce data-flow contract: input `<k1,v1>` pairs are mapped to intermediate `<k2,v2>` pairs, optionally combined, shuffled and partitioned by key, reduced to `<k3,v3>` output, and stored through an `OutputFormat`/`RecordWriter` on a Hadoop `FileSystem`.

## Important APIs, Types, and Functions

### Job and Tracker Control

`JobStatus` is partially visible at the start of the slice. The visible contract includes synchronized getters for map/reduce progress, run state, start time, and username; synchronized `setRunState(int)`; writable `write(DataOutput)`/`readFields(DataInput)`; and public state constants `RUNNING`, `SUCCEEDED`, `FAILED`, and `PREP`. It is documented as a compact status summary rather than a full `JobProfile`.

`JobSubmissionProtocol` extends `VersionedProtocol` and is the public RPC contract between `JobClient` and `JobTracker`. It allocates job ids (`getNewJobId()`), accepts staged jobs (`submitJob(String)`), exposes cluster status, kills jobs and task attempts, returns `JobProfile`, `JobStatus`, `Counters`, map/reduce `TaskReport[]`, task completion events, task diagnostics, filesystem name, incomplete jobs, and all jobs. Its `versionID` field makes wire compatibility explicit.

`JobTracker` implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. The public surface includes daemon lifecycle (`startTracker(JobConf)`, `stopTracker()`, `offerService()`, `main(String[])`), protocol version lookup, configured bind address lookup, tracker identity/ports/start time, job queues (`runningJobs()`, synchronized `getRunningJobs()`, `failedJobs()`, `completedJobs()`), TaskTracker state (`taskTrackers()`, `getTaskTracker(String)`), network topology placement (`resolveAndAddToTopology()`, `getNode()`, `getParentNode()`, cache-level counters), and RPC operations mirroring `JobSubmissionProtocol`. It also exposes heartbeat handling from TaskTrackers, tracker error reporting, task assignment lookup, and local job-file path lookup. Nested `JobTracker.IllegalStateException` and enum-like `JobTracker.State` are part of the public API.

`RunningJob` is the client handle for a submitted job. It exposes identifiers, job file, tracking URL, map/reduce progress, completion/success status, blocking `waitForCompletion()`, job kill, task completion event pagination, task kill, and counters.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. Its API covers construction from `JobConf`, task-tracker metrics, protocol version, storage cleanup, shutdown/close, connection to the JobTracker, report address, main run loop, task fetch, task status updates, diagnostic reporting, liveness ping, task completion, shuffle and local filesystem error reporting, map completion event fetch, lost map-output reporting, idle state, and process entry point. Nested public APIs include `TaskTracker.Child.main()` for child task JVMs, `MapOutputServlet` for serving map outputs over HTTP, and `TaskTrackerMetrics` as a metrics `Updater`.

`TaskCompletionEvent` is a writable event record for JobTracker task-completion history. It has a default writable constructor and a constructor carrying event id, task id, runtime, map/reduce flag, status, and task-tracker HTTP address. It provides getters/setters, `toString()`, helpers `isMapTask()` and `idWithinJob()`, writable serialization, `EMPTY_ARRAY`, and nested status enum values. The Javadoc requires event ids to be assigned incrementally per job starting at zero.

`TaskReport` is a writable task summary with task id, progress, state string, diagnostics, counters, finish time, start time, and `write()`/`readFields()`.

### MapReduce User Interfaces

`Mapper<K1,V1,K2,V2>` extends `JobConfigurable` and Hadoop `Closeable`. Its single `map(K1,V1,OutputCollector<K2,V2>,Reporter)` method is the user transform hook for one input key/value pair.

`Reducer<K2,V2,K3,V3>` extends `JobConfigurable` and `Closeable`. Its `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)` method receives grouped values for a key and emits final output.

`MapReduceBase` is the convenience base implementation for `JobConfigurable` and `Closeable`, with default `configure(JobConf)` and `close()` methods.

`MapRunnable<K1,V1,K2,V2>` extends `JobConfigurable` and defines `run(RecordReader<K1,V1>, OutputCollector<K2,V2>, Reporter)`. `MapRunner` is the default implementation, configuring itself from `JobConf` and iterating the reader to call the configured mapper.

`OutputCollector<K,V>` emits intermediate or final key/value pairs through `collect(K,V)`.

`Partitioner<K2,V2>` extends `JobConfigurable` and maps an intermediate key/value to a reducer partition through `getPartition(K2,V2,int)`.

`Reporter` extends `Progressable` and lets tasks update status, increment named counters, and access their `InputSplit`. `Reporter.NULL` is a public no-op reporter.

`RecordReader<K,V>` defines old-API split reads with caller-reused key and value objects: `next(K,V)`, `createKey()`, `createValue()`, `getPos()`, `getProgress()`, and `close()`.

`RecordWriter<K,V>` writes output key/value pairs and closes with a `Reporter`.

`OutputFormat<K,V>` creates a `RecordWriter` from `FileSystem`, `JobConf`, output name, and `Progressable`, and validates output specs through `checkOutputSpecs(FileSystem, JobConf)`.

`OutputFormatBase<K,V>` implements `OutputFormat` and adds static output compression configuration helpers: `setCompressOutput()`, `getCompressOutput()`, `setOutputCompressorClass()`, and `getOutputCompressorClass()`. Its writer/spec methods remain public hooks.

### Input and Output Formats

`LineRecordReader` reads text lines as `<LongWritable byteOffset, Text line>`. Constructors accept `Configuration`/`FileSplit` or raw `InputStream` with start/end offsets, optionally plus configuration. It provides key/value factories, `next()`, progress, position, and close. Nested `LineReader` wraps an `InputStream`, closes it, and reads a line into `Text` with a maximum length.

`TextInputFormat` extends `FileInputFormat<LongWritable,Text>`, is configurable, decides splitability, and creates `LineRecordReader` instances. Its Javadoc states lines are delimited by linefeed or carriage return, keys are byte positions, and values are line text.

`KeyValueLineRecordReader` reads each line into `Text` key and `Text` value by locating a separator with `findSeparator(byte[], int, int)`. `KeyValueTextInputFormat` configures the separator behavior, decides splitability, and creates this reader.

`TextOutputFormat<K,V>` extends `FileOutputFormat` and returns a line-oriented `RecordWriter`. Its protected nested `LineRecordWriter` synchronizes `write(K,V)` and `close(Reporter)` around a `DataOutputStream`.

`SequenceFileInputFormat<K,V>` lists input paths and creates `SequenceFileRecordReader<K,V>`. `SequenceFileRecordReader` exposes key/value classes, factories, both standard and raw-ish `next()` forms, current value access, progress, position, `seek(long)`, close, and a protected `conf` field.

`SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` adapt sequence file records to `Text` keys and values.

`SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` adapt sequence file keys/values to `BytesWritable` and expose original key and value class names.

`SequenceFileInputFilter` extends sequence-file input with a configurable filter class. The nested `Filter` interface is `Configurable` and tests keys with `accept(Object)`. `FilterBase` stores configuration. `MD5Filter`, `PercentFilter`, and `RegexFilter` provide static configuration setters and implement key acceptance by MD5 frequency, percent frequency, and regular expression matching respectively.

`SequenceFileOutputFormat` writes sequence files, creates `SequenceFile.Reader[]` for existing output directories, and controls output compression type through `getOutputCompressionType(JobConf)` and `setOutputCompressionType(JobConf, SequenceFile.CompressionType)`.

`MapFileOutputFormat` writes map files, opens multiple `MapFile.Reader` instances, and retrieves an entry by partitioning a key across readers with `getEntry(...)`.

`MultiFileInputFormat<K,V>` groups multiple files into splits and delegates reader creation to subclasses. `MultiFileSplit` is a writable `InputSplit` over parallel `Path[]` and `long[]` lengths, with total length, per-path length, path accessors, locations, serialization, and `toString()`.

`OutputLogFilter` implements `PathFilter` to reject output-log paths from output listings.

### Status HTTP, Logs, and Diagnostics

`StatusHttpServer` is an embedded Jetty wrapper for daemon status pages. It constructs from server name, bind address/name, port, and `findPort`; exposes webapp attributes; installs servlets; reports the selected port; configures thread counts and SSL listener; starts and stops. The documented contexts are `/logs/`, `/static/`, and `/` JSP content from `src/webapps/<name>`.

`StatusHttpServer.StackServlet` serves current stack traces and logs them. `TaskGraphServlet` emits SVG task-status graphs and exposes public graph dimension/margin constants.

`TaskLog` manages task user logs. Static APIs resolve task log files by task id and log name, purge old logs, read the configured maximum log length, wrap commands so stdout/stderr are captured to files with optional tail truncation and setup commands, quote commands through `addCommand()`, and capture debug output. Nested `LogName` is an enum-like type with `toString()`. Nested `TaskLog.Reader` is an `InputStream`-style reader over one task log name and byte range.

`TaskLogAppender` is a log4j appender with task id and total log file size properties. It activates options, appends logging events, and closes.

`TaskLogServlet` exposes task logs over HTTP through `doGet()`.

### JobControl

`org.apache.hadoop.mapred.jobcontrol.Job` wraps a `JobConf` with dependency and state management. It has constructors with or without depending jobs, getters/setters for job name, internal job id, MapReduce job id, job conf, state, and message; dependency access; `addDependingJob(Job)`; readiness and completion checks; `submit()`; and `main()`. Public state constants are `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`.

`JobControl` is a `Runnable` manager for dependent jobs. It is constructed with a group name and exposes lists for waiting, running, ready, successful, and failed jobs. It can add one or more jobs, report controller state, stop, suspend, resume, determine whether all jobs are finished, and run its scheduler loop.

### Join and Composite Input APIs

`ArrayListBackedIterator<X extends Writable>` implements `ResetableIterator<X>` using an in-memory `ArrayList`. It supports construction with an empty or supplied list, `hasNext()`, copying next/replayed values into a supplied writable, reset, add, close, and clear.

`ResetableIterator<T extends Writable>` is the core stateful replay iterator abstraction. It can test availability, copy the next element into a caller-provided writable, replay the last value, reset to the start, add elements, close data sources, and clear state for reuse. The Javadoc requires FIFO replay order after reset and warns that `next()` may fail for nested joins even when more elements exist if join constraints are not satisfied. `ResetableIterator.EMPTY` is a no-op implementation.

`StreamBackedIterator<X extends Writable>` implements `ResetableIterator` with a byte-array-backed stream, trading memory representation and serialization for replayability.

`TupleWritable` is a writable, iterable tuple of child `Writable` values. It has empty and array constructors, `has(int)`, `get(int)`, `size()`, equality/hash/string methods, iterator support that does not flatten nested tuples, and writable serialization. The documented wire format is count, child types, then child objects.

`ComposableInputFormat<K,V>` extends `InputFormat` and returns `ComposableRecordReader<K,V>`. `ComposableRecordReader<K,V>` extends `RecordReader` and `Comparable`, adding stream id, current key access/copy, `hasNext()`, key skipping, and `accept(CompositeRecordReader.JoinCollector,K)` to register matching values with a join collector.

`CompositeInputFormat<K>` implements `ComposableInputFormat<K,TupleWritable>`. It has static expression helpers `compose()` and `addDefaults()`, validates input, creates composite splits, and constructs composite record readers from a join expression. Its Javadoc-visible role is expression-based composition of multiple input formats.

`CompositeInputSplit` is a writable `InputSplit` that groups child splits. It supports empty and capacity constructors, `add(InputSplit)`, child access, total and indexed lengths, aggregate and indexed locations, and serialization.

`CompositeRecordReader<K,V,X>` is a configurable base for join readers. It is constructed with stream id, child count, and comparator class; exposes abstract-ish `combine(Object[], TupleWritable)` behavior, id, configuration, a priority queue of child readers, the comparator, child add, key access/copy, `hasNext()`, `skip(K)`, delegate iterator creation, collector accept/fill, comparison, key/value creation, position, close, progress, and fields for the join collector and children.

`JoinRecordReader<K>` implements `ComposableRecordReader<K,TupleWritable>` for joins that emit `TupleWritable` values. It has `next(K,TupleWritable)`, tuple factory, and delegate iterator. Its nested `JoinDelegationIterator` implements resettable tuple replay.

`InnerJoinRecordReader`, `OuterJoinRecordReader`, and `OverrideRecordReader` specialize join semantics. Inner and outer readers expose `combine(...)`; override readers expose `emit(TupleWritable)` and override `fillJoinCollector(...)`, indicating value selection from competing streams.

`MultiFilterRecordReader<K,V>` is another composite-reader specialization that emits one value type instead of a full tuple. It defines `emit(TupleWritable)`, `combine(...)`, `next(K,V)`, `createValue()`, and a resettable delegate. Its nested `MultiFilterDelegationIterator` replays emitted values.

`Parser` and nested token/node types parse join expressions. `Parser.Node` implements `ComposableInputFormat`, stores an identifier, stream id, comparator class, and a static map from identifiers to composable record-reader constructors. It can register identifiers, assign id, and set key comparator. `NodeToken`, `NumToken`, `StrToken`, generic `Token`, and `TType` model parser tokens.

`WrappedRecordReader<K,U>` is partially visible at the end of the chunk. It implements `ComposableRecordReader<K,U>` by wrapping a normal `RecordReader`; the visible API includes id, current key access/copy, `hasNext()`, `skip(K)`, protected advancement, collector accept, public `next(K,U)`, key/value factories, progress, position, and close.

## Control Flow

Job submission flow begins with `JobClient` calling `JobSubmissionProtocol.getNewJobId()`, staging job files under the JobTracker system directory for that id, then calling `submitJob(jobName)`. The JobTracker returns a `JobStatus`; clients can poll status/profile/counters/task reports, page through task completion events, ask for diagnostics, or kill jobs/tasks.

Tracker daemon flow is split across two protocols. TaskTrackers call JobTracker-side heartbeat/reporting APIs and receive `HeartbeatResponse` assignments. Child task JVMs call TaskTracker-side `TaskUmbilicalProtocol` methods visible through `TaskTracker`: `statusUpdate()`, diagnostic reporting, liveness ping, `done()`, shuffle/local filesystem error reporting, and map-output-lost reporting. Reduce tasks obtain map completion locations through completion event pagination and fetch outputs through `TaskTracker.MapOutputServlet`.

The old MapReduce application flow is explicitly described in package documentation. An `InputFormat` creates `InputSplit`s. Each map task uses a `RecordReader` to repeatedly fill reusable key/value objects and passes those to `Mapper.map()`. The mapper uses `OutputCollector.collect()` and `Reporter` updates. Intermediate keys are partitioned by `Partitioner`, optionally combined, fetched by reducers over HTTP, grouped by key, and supplied to `Reducer.reduce()`. Reducers emit final records through a `RecordWriter` created by the configured `OutputFormat`.

Reader/writer control flow is pull-based and object-reuse-oriented. Callers allocate keys and values via `createKey()` and `createValue()`, then loop while `next(key,value)` returns true. Implementations expose byte position and fractional progress so tasks can report progress. Writers accept key/value pairs until `close(Reporter)`.

Text and key-value input formats follow line-oriented flow: split a file, choose whether the file is splitable, read lines within split boundaries, derive key/value pairs from byte offset or separator position, and close the stream. Sequence-file readers instead use Hadoop `SequenceFile.Reader` metadata and support typed object creation plus seeking.

Status HTTP flow is daemon-local. A `StatusHttpServer` creates a Jetty server, publishes daemon objects through context attributes, installs servlets, optionally binds SSL, starts asynchronously, and is later stopped. Stack, task graph, task log, and map-output servlets expose diagnostic or shuffle data through servlet `doGet()` methods.

JobControl flow is a small scheduler loop. Jobs start in waiting states, dependencies are checked through `isReady()` and `isCompleted()`, ready jobs are submitted, running jobs transition to success or failure, and dependent jobs can become `DEPENDENT_FAILED`. `JobControl` can be suspended, resumed, stopped, or run until all jobs finish.

Join flow starts with a composition expression built by `CompositeInputFormat.compose()` or supplied directly in configuration. `Parser` builds a tree of `Parser.Node` instances that resolve identifiers to composable record-reader constructors. `CompositeInputFormat` validates inputs, builds one `CompositeInputSplit` from child splits, creates child `ComposableRecordReader`s, and delegates to a `CompositeRecordReader` subclass. Composite readers keep child readers in a priority queue ordered by key comparator, collect matching values for the current key into resettable iterators, and combine them according to inner, outer, override, or multi-filter semantics.

## State and Persistence Behavior

The XML file itself is generated public API inventory and has no runtime persistence. The APIs it describes are heavily stateful.

Writable state appears in `JobStatus`, `MultiFileSplit`, `ReduceTaskStatus`, `TaskCompletionEvent`, `TaskReport`, `CompositeInputSplit`, and `TupleWritable`. These types use Hadoop `DataInput`/`DataOutput` serialization and therefore are compatibility-sensitive in RPC, split planning, task status propagation, and join value materialization.

Tracker state is distributed and process-local. `JobTracker` owns job queues, task-tracker registrations, job ids, topology resolution, job counters, task completion events, task diagnostics, and filesystem/system-directory locations. `TaskTracker` owns local task execution state, local storage cleanup, map output availability, user logs, task child processes, and the HTTP endpoint used by reducers.

MapReduce task state is communicated by status objects, reporters, counters, and completion events. Several JobTracker and TaskTracker methods are marked synchronized in the API XML, especially progress/state reads or task-update callbacks, signaling concurrent access from RPC, timer, and worker threads.

Input split and reader state is transient but serializable where needed. Splits persist enough path/offset/length/location metadata to move from JobTracker planning to TaskTracker execution. RecordReaders track current stream position and progress. `LineRecordReader` and `SequenceFileRecordReader` own open streams/readers until `close()`.

Output state is controlled by `OutputFormatBase` compression settings in `JobConf` and by `RecordWriter` implementations that write to `FileSystem` streams. `TextOutputFormat.LineRecordWriter` synchronizes writes and close, indicating possible shared access or defensive serialization around its stream.

Task logging state lives in local log files and log4j appenders. `TaskLog` APIs cap log size, capture stdout/stderr, purge old user logs, quote command lines, and expose bounded readers. Incorrect cleanup or capture behavior directly affects post-failure diagnostics.

JobControl state is explicit through integer constants and job lists: waiting, ready, running, successful, failed, and dependent-failed. A `Job` stores both the wrapper id and the underlying MapReduce job id, plus a human message and its dependency list.

Join state is centered on resettable iterators and tuple bitsets. `ArrayListBackedIterator` stores values in memory; `StreamBackedIterator` stores replay data in a byte array; `ResetableIterator.EMPTY` represents no values. `TupleWritable` stores child writables plus per-position presence state. Composite readers maintain a priority queue, child array, join collector, comparator, and delegate iterators for repeated combination.

## Dependencies and Integration Points

The APIs integrate with Hadoop core interfaces from `org.apache.hadoop.io`, `org.apache.hadoop.fs`, `org.apache.hadoop.conf`, `org.apache.hadoop.ipc`, `org.apache.hadoop.net`, `org.apache.hadoop.util`, and old MapReduce classes such as `JobConf`, `JobClient`, `JobProfile`, `ClusterStatus`, `Counters`, `TaskStatus`, `InputSplit`, `FileInputFormat`, and `FileOutputFormat`.

RPC integration is through `VersionedProtocol`, `JobSubmissionProtocol`, `InterTrackerProtocol`, and `TaskUmbilicalProtocol`. The version id fields and protocol-version methods are important for old Hadoop daemon/client compatibility.

Filesystem integration is broad: input/output formats use `FileSystem`, `Path`, `PathFilter`, split locations, map/sequence files, compression codecs, and task output naming. The package documentation assumes most job input and output is stored in a Hadoop `FileSystem`.

Serialization integration uses Hadoop `Writable`, `WritableComparable`, `WritableComparator`, `BytesWritable`, `Text`, `LongWritable`, `SequenceFile`, `MapFile`, and `DataInput`/`DataOutput`. Join and sequence-file APIs depend on stable writable class names and constructors.

HTTP integration uses embedded Jetty and servlet APIs (`HttpServlet`, requests, responses, `ServletException`) for daemon status, task logs, task graphs, stack traces, and map-output shuffle serving.

Logging and metrics integration uses Apache Commons Logging, log4j appenders/events, and Hadoop metrics `Updater`/`MetricsContext`.

JobControl integrates with `JobConf` and old `JobClient` submission semantics while adding its own wrapper-level dependency graph. Join APIs integrate with `InputFormat` implementations through reflection-like constructor registration in `Parser.Node.rrCstrMap`.

## Risks and Edge Cases

This is old `mapred` API surface, so compatibility risk is high. Public signatures, writable field ordering, RPC method names, protocol versions, and enum/state constants can affect clients, daemons, serialized splits, task status messages, and on-disk/intermediate data.

The line range starts inside `JobStatus` and ends inside `WrappedRecordReader`. A final reconciled report must merge adjacent chunks to avoid treating either class as complete based only on this slice.

Job and task kill APIs distinguish killing a task attempt from failing it through `killTask(taskId, shouldFail)`. Tests and callers need to preserve this distinction because it affects whether a failed attempt counts toward job failure.

Task completion event pagination depends on monotonically increasing per-job event ids and correct `fromEventId`/`maxEvents` handling. Off-by-one errors can make reducers miss map outputs or clients miss diagnostics.

Tracker methods are concurrent RPC entry points. The synchronized flags visible on heartbeat, status update, diagnostics, ping, done, shuffle error, filesystem error, map-output-lost, and idle checks indicate thread-safety pressure around mutable tracker state.

Text input edge cases include split boundaries, CR/LF handling, very long lines, and key-value separator detection. Incorrect boundary logic can duplicate or drop lines at split edges.

Sequence-file adapters depend on stored key/value class metadata. Binary and text adapters must preserve bytes or text conversion without corrupting arbitrary writable data.

Output compression settings are stored in `JobConf`, so defaults, codec class lookup, and compression type need compatibility with existing jobs. `OutputFormat.checkOutputSpecs()` must reject invalid output paths early enough to avoid partial writes.

HTTP servlets expose operational data and shuffle data. Risks include leaking logs, mishandling byte ranges, serving stale or lost map outputs, incorrect SSL listener configuration, and blocking daemon threads in servlet handlers.

`TaskLog.captureOutAndError()` and `addCommand()` manipulate shell commands. Quoting, executable path handling, setup command ordering, and tail truncation are security and diagnostics sensitive.

JobControl uses integer state constants and mutable dependency lists. Cyclic dependencies, dependency failure propagation, suspension/resume races, duplicate job submission, and inconsistent wrapper id versus MapReduce job id are natural edge cases.

Join APIs are complex and stateful. Resettable iterators require callers to call `reset()` after `add()` to avoid concurrent modification; nested joins can have available elements that do not satisfy join constraints; stream-backed replay depends on writable serialization; tuple serialization depends on writable class availability; and comparator mismatches across sources can break grouping.

`CompositeInputSplit` must keep child splits aligned with child input formats. Incorrect length/location aggregation can hurt scheduling locality or create invalid task assignments.

## Test Signals

For `JobSubmissionProtocol` and `JobTracker`, tests should cover job id uniqueness, system-directory staging assumptions, successful submission, invalid/missing job files, cluster status reporting, job/profile/status/counter lookups, map/reduce task reports, task diagnostics, job kill, task kill with both `shouldFail` values, task completion event pagination, and protocol version compatibility.

Tracker integration tests should cover TaskTracker heartbeat initial contact, response id sequencing, task assignment, task status updates, diagnostic reporting, child liveness ping, `done()` promotion behavior, shuffle error handling, filesystem error handling, map output lost notification, idle detection, TaskTracker shutdown/cleanup, and map-output servlet fetches.

Writable round-trip tests should exist for every visible writable type: `JobStatus`, `TaskCompletionEvent`, `TaskReport`, `MultiFileSplit`, `ReduceTaskStatus`, `CompositeInputSplit`, and `TupleWritable`. Tests should include empty/default constructors because those are required by Hadoop deserialization.

MapReduce programming contract tests should cover mapper and reducer invocation with reusable objects, `MapRunner` iteration over a `RecordReader`, reporter status and counters, partitioner bounds, `Reporter.NULL`, and correct close/configure ordering through `MapReduceBase`.

Input format tests should exercise line splitting at file boundaries, CR/LF variants, long lines, compressed versus splitable files where applicable, key-value separator configuration, empty values, sequence-file class metadata, binary sequence-file reads, text sequence-file conversion, filter configuration, MD5/percent/regex filter acceptance, multi-file split serialization, and locality arrays.

Output format tests should cover text output formatting for null/empty keys or values, synchronized close behavior, compression flags and codec class settings in `JobConf`, sequence-file compression type, map-file output lookup across partitioned readers, and `OutputLogFilter` rejection of log paths.

Status server and logging tests should cover port selection with `findPort`, context attributes, servlet registration, SSL listener setup failures, start/stop lifecycle, stack servlet response, task graph servlet response, task log file resolution, log cleanup by retain hours, command quoting, stdout/stderr capture with whole-output and tail modes, debug-output capture, `TaskLog.Reader` byte ranges, and appender task id/log-size properties.

JobControl tests should cover dependency readiness, successful submission order, failed dependency propagation to `DEPENDENT_FAILED`, state-list membership, `allFinished()`, suspend/resume/stop behavior, duplicate dependencies, and cyclic dependency handling or rejection.

Join tests should cover `CompositeInputFormat.compose()` expression strings, parser identifier registration, comparator selection, composite split child alignment, inner join emission only on all matching sources, outer join emission with missing tuple positions, override join value selection, multi-filter emission, priority queue ordering, key skip behavior, resettable iterator FIFO replay, `reset()` after `add()`, `EMPTY` iterator no-op behavior, stream-backed iterator writable serialization, tuple `has()`/`get()`/iteration/string/equality/hash semantics, and serialization round trips for nested tuples.

## Cross-Chunk Notes

The preceding chunk contains the beginning of `JobStatus`; this chunk only captures its trailing methods and constants.

The following chunk should contain the rest of `WrappedRecordReader` and any remaining `org.apache.hadoop.mapred.join` API declarations. Merge/reconciliation should combine those fragments before making final per-file conclusions about the join package.

The API references many classes declared outside this range, including `JobClient`, `JobConf`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `TaskStatus`, `ClusterStatus`, `Counters`, `HeartbeatResponse`, `Task`, `InterTrackerProtocol`, and `TaskUmbilicalProtocol`. Final file-level research should connect this chunk to the chunks where those declarations appear.
