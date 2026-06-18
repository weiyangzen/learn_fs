# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml lines 25022-31137

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.1, not executable implementation source. It covers public API metadata in the old `org.apache.hadoop.mapred` package: the tail of `JobConf`, `JobConfigurable`, job end notification, job history records and listeners, job identifiers/profiles/statuses, most of `JobTracker`, text/sequence-file input and output helpers, the core map/reduce interfaces, task identifiers, task completion events, task logs, task reports, and the opening of `TaskTracker`.

The XML records API compatibility data: class and interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, visibility, deprecation text, and Javadoc contracts. Because the range starts inside `JobConf` and ends inside `TaskTracker`, adjacent chunks are required before making whole-class claims about those two types.

## Purpose and Major API Surface

`JobConf` is represented from map-output and output-format configuration through debug scripts, job-end notification, and job-local directory access. The visible methods configure map-output compression and compressor classes, map/final output key/value classes, raw comparators and grouping comparators, mapper/map-runner/partitioner/reducer/combiner classes, combine-once behavior, speculative execution for maps and reduces, map/reduce task counts, max task attempts, failure percentages, job name/session/priority, task profiling, map and reduce debug scripts, job-end notification URI, and task-local job directories. Several methods expose compatibility quirks, including deprecated sequence-file compression-type settings for intermediate map outputs and deprecated string job IDs in nearby job-status/profile APIs.

`JobConfigurable` is a small extension hook with `configure(JobConf)`. It is the old mapred-era dependency-injection mechanism used by input/output formats, partitioners, mappers, reducers, and utility classes to receive job configuration before execution.

`JobEndNotifier` exposes lifecycle entry points for asynchronous end-of-job notifications: starting/stopping the notifier, registering a completed `JobStatus`, and local-runner notification. It integrates with `JobConf` job-end notification URIs.

`JobHistory` and nested history types define the old job-history logging API. `JobHistory.init(JobConf, String, String, long)` initializes history logging, `parseHistoryFromFS` replays a history file into a `JobHistory.Listener`, and disable/enable flags control history emission. `JobHistory.JobInfo`, `Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide static `logSubmitted`, `logStarted`, `logFinished`, `logFailed`, and `logKilled` methods, with overloads accepting either string IDs or typed `JobID`, `TaskID`, and `TaskAttemptID`. Enums `Keys`, `Values`, and `RecordTypes` describe the serialized record vocabulary. `HistoryCleaner` is a `Runnable` for purging old history.

`JobID`, `TaskID`, and `TaskAttemptID` are typed, immutable identifiers extending `ID`. They implement equality, ordering, string conversion, `Writable`-style `readFields`/`write`, static `read(DataInput)`, `forName(String)` parsing, and regex-pattern helpers. Their docs define canonical string forms such as `job_...`, `task_..._m_...`, and task-attempt IDs, and warn applications to avoid manual string parsing.

`JobPriority`, `JobTracker.State`, and `TaskCompletionEvent.Status` are enums used to classify scheduling priority, tracker lifecycle state, and task completion state. The JDiff metadata only shows standard `values()` and `valueOf()` entry points, but these enums are wire/API values and therefore compatibility-sensitive.

`JobProfile`, `JobStatus`, `TaskCompletionEvent`, and `TaskReport` are serializable job/task metadata carriers implementing `Writable` where applicable. `JobProfile` contains user, typed and deprecated string job IDs, job file, tracking URL, and job name. `JobStatus` stores map/reduce progress, run state, start time, and username. `TaskCompletionEvent` carries event ID, task attempt ID, tracker HTTP address, runtime, status, map/reduce classification, and per-job task index. `TaskReport` contains task ID, progress, reporter state string, diagnostics, counters, start time, and finish time.

`JobShell` is a `Configured` command-line `Tool` with `init`, `run`, and `main`, providing a mapred-era CLI entry around job submission and control.

`JobTracker` is the central old mapred master API. It implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. The visible surface starts and stops the tracker, serves RPC protocol versions, offers service, exposes tracker identity/ports/start time/build version, returns running/failed/completed jobs and task trackers, manages network topology resolution, accepts task-tracker heartbeats, reports tracker errors, allocates job IDs, submits jobs, returns cluster/job/task status, kills jobs/tasks, returns task completion events and diagnostics, resolves assigned trackers and task-in-progress objects, exposes system/local job directories, and has a `main` entry point.

Record input APIs include `LineRecordReader`, `LineRecordReader.LineReader`, `KeyValueLineRecordReader`, and `KeyValueTextInputFormat`. They implement or produce `RecordReader` instances over `LongWritable`/`Text` or `Text`/`Text`, handle split-aware reading, expose position/progress, and close underlying streams. `KeyValueLineRecordReader.findSeparator` and configurable key-value separator behavior are the main parsing concern.

Map/reduce execution contracts are represented by `Mapper`, `MapRunnable`, `MapRunner`, `MapReduceBase`, `Reducer`, `Partitioner`, `OutputCollector`, `Reporter`, `RecordReader`, `RecordWriter`, `OutputFormat`, and `OutputFormatBase`. `Mapper.map` and `Reducer.reduce` consume keys/values and emit via `OutputCollector.collect`. `MapRunner.run` drives records from a `RecordReader` into a mapper. `Reporter` exposes status updates, counters, and the current `InputSplit`. `Partitioner.getPartition` maps keys to reduce partitions. `RecordReader` and `RecordWriter` define streaming IO lifecycle methods. `MapReduceBase` provides no-op `configure` and `close` defaults for user code.

Output and split helpers include `MapFileOutputFormat`, `MultiFileInputFormat`, `MultiFileSplit`, `OutputLogFilter`, and `OutputFormatBase`. `MapFileOutputFormat` writes `MapFile` output and provides static readers/get-entry helpers. `MultiFileInputFormat` groups multiple files into `MultiFileSplit`; `MultiFileSplit` persists path and length arrays and exposes locations. `OutputLogFilter` filters output log paths. `OutputFormatBase` provides static compression configuration helpers plus abstract record-writer and output-spec checks.

Sequence-file APIs include binary/text input formats and readers, `SequenceFileInputFormat`, `SequenceFileRecordReader`, `SequenceFileOutputFormat`, `SequenceFileAsBinaryOutputFormat`, `WritableValueBytes`, and `SequenceFileInputFilter` with `Filter`, `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`. These APIs bridge Hadoop `SequenceFile` storage to mapred `RecordReader`/`RecordWriter`, expose key/value class discovery, raw byte records, text conversion, compression type configuration, and filter sampling by hash, percentage, or regex.

`RunningJob` is the client-facing job handle contract. It exposes typed and deprecated string job IDs, job name/file/tracking URL, progress, completion/success checks, blocking `waitForCompletion`, `killJob`, task completion event paging, task killing by string or typed attempt ID, and counters.

`StatusHttpServer`, `StackServlet`, and `TaskGraphServlet` describe a Jetty-style status HTTP server used by mapred daemons. The API sets attributes, adds servlets, reads attributes/port, configures threads, adds SSL listeners, starts/stops, and serves stack traces or task graphs via servlet `doGet`.

`TaskLog`, `TaskLog.LogName`, `TaskLogAppender`, and `TaskLogServlet` define task-local logging APIs. `TaskLog` locates per-task log files, purges old logs, calculates configured log-length caps, wraps commands to capture stdout/stderr or debug output, and quotes shell command components. `TaskLogAppender` is a log4j `FileAppender` for child task logs with task ID and total-log-size properties. `TaskLogServlet` exposes task logs over HTTP from task trackers.

`TaskTracker` begins at the end of the chunk. The visible metadata shows it implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`, has a `JobConf` constructor, exposes task-tracker metrics, and begins the RPC `getProtocolVersion` method. Its full behavior belongs to the next chunk.

## Control Flow and Behavioral Contracts

The XML has no executable control flow, but the Javadocs describe API-level flows. A job is configured through `JobConf`, submitted to `JobTracker.submitJob`, monitored via `RunningJob`, `JobStatus`, `JobProfile`, `TaskReport`, counters, diagnostics, and `TaskCompletionEvent`, and eventually killed or completed. `JobEndNotifier` and `JobHistory` are side channels triggered by job completion and task lifecycle transitions.

Map task flow is expressed by `RecordReader.next` producing input records, `MapRunner.run` invoking a configured `Mapper.map`, and `OutputCollector.collect` emitting intermediate records. The job configuration selects mapper, map runner, partitioner, combiner, reducer, map-output key/value types, comparators, grouping comparator, and compression. Reducer flow groups equal keys according to the grouping comparator and invokes `Reducer.reduce` with an iterator of values, emitting final output through the same collector abstraction.

Input flow is split-aware. `LineRecordReader` and `KeyValueLineRecordReader` track current byte position and progress; `LineReader` has overloads for max line length and max bytes to consume; `KeyValueTextInputFormat` decides splitability and constructs readers for file splits. `MultiFileInputFormat` creates grouped splits and corresponding readers.

Output flow is controlled by `OutputFormat.getRecordWriter` and `checkOutputSpecs`. `OutputFormatBase` centralizes output compression settings. `SequenceFileOutputFormat` and `MapFileOutputFormat` construct storage-specific writers, while `RecordWriter.close(Reporter)` is the completion hook. `OutputLogFilter` excludes task/log artifacts from output path listings.

Sequence-file reader flow wraps `SequenceFile.Reader` and exposes typed or raw key/value records. Binary readers expose `BytesWritable` and class-name metadata; text readers convert keys and values to `Text`; filter readers apply configured `SequenceFileInputFilter.Filter` instances before records reach the mapper. Filter configuration is job-conf driven, with `MD5Filter`, `PercentFilter`, and `RegexFilter` reading frequency or pattern settings from configuration.

Job history flow writes lifecycle records using static logging helpers and can parse persisted history from a filesystem path into a listener callback. History events are represented as key/value pairs keyed by `JobHistory.Keys`, with values constrained by `JobHistory.Values` and record categories by `RecordTypes`.

JobTracker flow is RPC-heavy. Task trackers send `heartbeat` requests containing tracker status, accept/response ID, initial-contact flags, and response IDs; clients call job-submission protocol methods for IDs, submission, status, diagnostics, reports, counters, task completion events, and kill operations. Topology helpers resolve task trackers into network nodes for locality-aware scheduling.

Task log flow wraps child task commands in shell invocations that redirect stdout/stderr to per-task files, optionally retaining only a tail segment. The servlet and appender surface the same task-specific logs through HTTP and log4j.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API metadata used by compatibility tooling. Runtime state described in the chunk belongs to the Hadoop APIs.

Configuration state lives primarily in `JobConf`: selected classes, compression flags/codecs, comparator classes, speculative execution flags, task counts, retry/failure thresholds, priority, profiling parameters, debug scripts, notification URIs, and local job directories. These settings influence task JVM launch, shuffle output, scheduling, monitoring, and cleanup behavior.

Persistent job metadata includes job history files, local job file paths, system job directories, job profiles/statuses, task reports, counters, task completion events, and task logs. `JobHistory.JobInfo.encode*` and `decodeJobHistoryFileName` indicate filesystem-stored history paths and filenames must be URL/path safe and reversible.

Identifier classes persist over RPC and storage via `readFields`/`write`. `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`, and `MultiFileSplit` are wire-format classes, so field ordering and parsing behavior are compatibility-sensitive.

Filesystem side effects occur through job submission, local job file path management, mapred output writers, sequence/map file writers, history logging, log cleanup, command-output capture, HTTP log serving, and task/job kill operations. Many methods throw `IOException`, and servlet entry points throw `ServletException`/`IOException`.

Mapred execution state includes record-reader positions, reader progress, reporter status strings, counters, input split identity, map/reduce progress, task start/finish times, task diagnostics, task attempt runtime, and tracker assignment. `RunningJob.waitForCompletion` is explicitly blocking, while `JobTracker.offerService` runs master service loops.

## Dependencies and Integration Points

The chunk is centered on the legacy `org.apache.hadoop.mapred` API and depends on Hadoop IO types such as `Writable`, `WritableComparable`, `RawComparator`, `LongWritable`, `Text`, `BytesWritable`, `SequenceFile`, `MapFile`, and compression codecs. It also depends on Hadoop filesystem types including `Path`, `FileSystem`, `FileStatus`, `PathFilter`, `FileSplit`, and `InputSplit`.

Mapred integration points include `JobConf`, `JobConfigurable`, `Mapper`, `Reducer`, `MapRunnable`, `Partitioner`, `OutputCollector`, `Reporter`, `InputFormat`, `OutputFormat`, `RecordReader`, `RecordWriter`, `RunningJob`, `JobSubmissionProtocol`, `InterTrackerProtocol`, `TaskUmbilicalProtocol`, `HeartbeatResponse`, `TaskTrackerStatus`, `ClusterStatus`, `Counters`, and `MRConstants`.

Daemon and monitoring dependencies include servlet APIs (`HttpServlet`, `HttpServletRequest`, `HttpServletResponse`, `ServletException`), log4j (`FileAppender`, `LoggingEvent`), network types (`InetSocketAddress`, topology `Node`), URL/HTTP strings, and Java process command wrapping.

Compatibility tooling depends on XML structure and attributes, not implementation bytecode. Public/protected signature changes, deprecation changes, thrown-exception changes, enum value changes, or Javadoc contract changes in these APIs can affect JDiff comparisons against other Hadoop releases.

## Risks and Compatibility Notes

This line window is partial at both ends. `JobConf` begins before line 25022 and `TaskTracker` continues after line 31137, so this chunk must not be treated as complete coverage of either type.

The old `mapred` APIs mix typed IDs with deprecated string IDs. Callers and compatibility tests must preserve deprecated accessors such as `getJobId`, `getTaskId`, and string-based kill/submission overloads while preferring typed `JobID`, `TaskID`, and `TaskAttemptID`.

Map-output type and comparator configuration is easy to misconfigure. The docs explicitly allow map-output key/value classes to differ from final output classes. Grouping comparator and sort comparator can differ to support secondary sort-like behavior, but the reduce sort is not guaranteed stable.

Combiner behavior is not equivalent to reducer behavior unless the operation is associative and safe for repeated or skipped execution. `setCombineOnceOnly` exists, but the general combiner contract still requires care because combiners may otherwise run zero or more times.

Speculative execution, task-attempt limits, and failure-percentage thresholds affect correctness for jobs with side effects. Output commit protocols and idempotent mappers/reducers are important because this API allows duplicate attempts and task killing.

Sequence-file binary/text adapters expose raw bytes or stringified values. Tests and downstream tools must verify that key/value class metadata, raw byte boundaries, compression settings, and text conversion are consistent with `SequenceFile` semantics.

Command wrapping in `TaskLog.captureOutAndError`, debug-script capture, and `addCommand` is shell-sensitive. Quoting, executable path handling, log truncation, and setup commands are portability and injection-risk areas.

`JobTracker` public methods expose many internal types (`JobInProgress`, `TaskInProgress`, task tracker status, topology nodes). That broad surface makes API compatibility fragile and ties clients/tests to master internals.

## Test Signals

JDiff validation should confirm the XML remains well-formed across this line range and preserves all class/interface boundaries, including partial `JobConf` and partial `TaskTracker`.

API compatibility tests should check method signatures, generic bounds, visibility, declared exceptions, deprecation strings, enum presence, and constructor overloads for the covered `mapred` classes and interfaces.

Job configuration tests should cover map-output compression/codecs, map/final output key/value classes, comparator and grouping comparator classes, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution flags, task counts, attempt limits, failure percentages, job priority, profiling ranges, debug scripts, and job-end notification URI.

Map/reduce contract tests should exercise `MapRunner` driving a `Mapper`, reducer grouping behavior with custom comparators, `OutputCollector.collect`, reporter status/counters/input split, no-op `MapReduceBase.configure/close`, and `RecordReader`/`RecordWriter` lifecycle behavior.

Input/output tests should cover line and key-value readers across split boundaries, separator handling, max line length behavior, `MultiFileSplit` writable round trips, output spec validation, compression setting propagation, map-file lookups, and output-log filtering.

Sequence-file tests should cover typed record reads, raw binary reads/writes, text conversion readers, key/value class-name exposure, compression type configuration, `WritableValueBytes`, and MD5/percent/regex filtering from `JobConf`.

JobTracker/client tests should exercise job ID allocation, submission, profile/status/counter/report retrieval, task completion event paging, diagnostics, job/task kill paths, cluster status, tracker heartbeat response compatibility, tracker error reporting, and topology helper behavior.

Serialization tests should round-trip `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`, and `MultiFileSplit`, including deprecated string accessors and `forName` malformed-input failures.

History and log tests should verify job/task/attempt history logging overloads, history parsing through a listener, history disable behavior, encoded history paths/names, history cleanup, task-log file selection by `LogName`, old-log cleanup, stdout/stderr capture with tail length, debug-output capture, appender close/size behavior, and servlet `doGet` error handling.
