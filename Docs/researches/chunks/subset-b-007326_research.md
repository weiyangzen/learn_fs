# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.1.xml lines 37822-43957

## Scope

This chunk is part 7 of the generated JDiff public API XML for Hadoop 0.20.1. It is API metadata rather than Java implementation source, so behavior is inferred from public signatures, modifiers, declared exceptions, inheritance, implemented interfaces, field constants, and embedded Javadoc.

The range starts in the tail of `org.apache.hadoop.mapred.JobID`, continues through a large section of the old `org.apache.hadoop.mapred` MapReduce API, enters `org.apache.hadoop.mapred.jobcontrol`, and begins `org.apache.hadoop.mapred.join`. It ends inside the `CompositeInputFormat.compose(String, Class, Path[])` method documentation, so the final method body metadata is completed by the next chunk.

## Purpose

This slice captures the compatibility surface for the legacy `mapred` MapReduce runtime around job identity, job status, JobTracker and TaskTracker RPC/status APIs, input and output formats, mapper/reducer contracts, task reports, task logs, bad-record skipping, job dependency control, and the beginning of the composable join input framework.

As a JDiff artifact, its purpose is to freeze what Hadoop 0.20.1 exposed publicly: constructor overloads, return and parameter types, synchronization flags, static helpers, nested enums, deprecation guidance toward the newer `mapreduce` API, and the documented operational contracts relied on by users and downstream libraries.

## Important APIs and Types

### Job and cluster status APIs

The chunk begins with the remaining `JobID` APIs: `downgrade(org.apache.hadoop.mapreduce.JobID)`, `read(DataInput)`, `forName(String)`, and `getJobIDsPattern(String, Integer)`. `JobID` is documented as the immutable identifier formed from a JobTracker identifier and job number; applications are told to use constructors or `forName` rather than parse strings manually.

`JobPriority` is a public enum with `VERY_HIGH`, `HIGH`, `NORMAL`, `LOW`, and `VERY_LOW`. It supplies the usual `values()` and `valueOf(String)` methods and is used by job status and scheduling paths.

`JobProfile` implements `Writable` and carries durable job presentation metadata: user, job ID, job file, tracking URL, job name, and queue name. It has constructors using the newer `org.apache.hadoop.mapreduce.JobID` plus a deprecated string-ID constructor. Accessors include `getUser`, `getJobID`, deprecated `getJobId`, `getJobFile`, `getURL`, `getJobName`, and `getQueueName`, with `write` and `readFields` for Hadoop serialization.

`JobQueueInfo` also implements `Writable`. It exposes `queueName` and scheduling information with setters/getters plus serialization methods. Its Javadoc says unset scheduling information returns `"N/A"`, which is a compatibility detail for clients and UI display.

`JobStatus` implements `Writable` and `Cloneable`. It models job lifecycle and progress with constructor variants covering map/reduce/cleanup/setup progress, run state, and priority. Synchronized accessors cover map, reduce, cleanup, setup progress, run state, start time, username, scheduling info, and job priority. State constants are `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`. Deprecated `getJobId()` remains beside `getJobID()`.

### JobTracker public surface

`JobTracker` implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. It is documented as the central location for submitting and tracking MapReduce jobs in a network environment.

Public static lifecycle helpers include `startTracker(JobConf)`, `startTracker(JobConf, String)`, and `stopTracker()`. Public status and identity methods include `getProtocolVersion`, `hasRestarted`, `hasRecovered`, `getRecoveryDuration`, `getInstrumentationClass`, `setInstrumentationClass`, `getAddress`, `offerService`, `getTotalSubmissions`, `getJobTrackerMachine`, `getTrackerIdentifier`, `getTrackerPort`, `getInfoPort`, and `getStartTime`.

Cluster and topology visibility methods include `runningJobs`, synchronized `getRunningJobs`, `failedJobs`, `completedJobs`, `taskTrackers`, `activeTaskTrackers`, `taskTrackerNames`, `blacklistedTaskTrackers`, `isBlacklisted`, `getTaskTracker`, `resolveAndAddToTopology`, `getNodesAtMaxLevel`, static `getParentNode`, `getNode`, `getNumTaskCacheLevels`, `getNumResolvedTaskTrackers`, and `getNumberOfUniqueHosts`.

Scheduling and job management APIs include `addJobInProgressListener`, `removeJobInProgressListener`, `getQueueManager`, `heartbeat`, `getNextHeartbeatInterval`, `getFilesystemName`, `reportTaskTrackerError`, `getNewJobId`, `submitJob`, `getClusterStatus(boolean)`, deprecated no-arg `getClusterStatus`, `killJob`, `initJob`, `failJob`, `setJobPriority`, `getJobProfile`, `getJobStatus`, `getJobCounters`, task report accessors for map/reduce/cleanup/setup, `getTaskCompletionEvents`, `getTaskDiagnostics`, `getTip`, `killTask`, `getAssignedTracker`, `jobsToComplete`, `getAllJobs`, `getSystemDir`, `getJob`, `getLocalJobFilePath`, `main`, queue APIs, and `refreshServiceAcl`.

Nested `JobTracker.IllegalStateException` extends `IOException` for job submission before readiness. Nested `JobTracker.State` exposes `INITIALIZING` and `RUNNING`.

### Record readers, input formats, and map execution

`KeyValueLineRecordReader` implements `RecordReader` for lines split into `Text` key/value pairs by configurable separator `key.value.separator.in.input.line`, defaulting to tab. It exposes `findSeparator(byte[], int, int, byte)`, synchronized `next`, synchronized `getPos`, `getProgress`, and `close`.

`KeyValueTextInputFormat` extends `FileInputFormat` and implements `JobConfigurable`. It configures splitability and creates `KeyValueLineRecordReader` instances. `LineRecordReader` is the old API line reader, deprecated in favor of `org.apache.hadoop.mapreduce.lib.input.LineRecordReader`; it treats keys as file offsets and values as lines. The nested `LineRecordReader.LineReader` is itself deprecated in favor of `org.apache.hadoop.util.LineReader`.

`MapFileOutputFormat` writes `MapFile`s and exposes `getRecordWriter`, static `getReaders`, and static `getEntry` that uses a `Partitioner` to locate an entry across output readers.

`Mapper` is the old API mapper interface, deprecated in favor of `org.apache.hadoop.mapreduce.Mapper`. It extends `JobConfigurable` and `Closeable` and defines `map(Object key, Object value, OutputCollector output, Reporter reporter)`. The Javadoc describes one map task per `InputSplit`, optional combiner use, grouping, partitioning, intermediate `SequenceFile`s, progress reporting, counters, and zero-reducer behavior.

`MapReduceBase` supplies no-op `configure(JobConf)` and `close()` helpers. `MapReducePolicyProvider` integrates MapReduce with Hadoop service authorization. `MapRunnable` defines `run(RecordReader, OutputCollector, Reporter)` and `MapRunner` provides the default implementation that drives a configured mapper over records.

`MultiFileInputFormat` and `MultiFileSplit` expose old combined-input support. `OutputCollector` defines `collect(Object, Object)` for mapper and reducer outputs.

### Output, partitioning, and raw iteration

`OutputCommitter` extends the newer `org.apache.hadoop.mapreduce.OutputCommitter` while exposing old API abstract hooks: `setupJob(JobContext)`, `cleanupJob(JobContext)`, `setupTask(TaskAttemptContext)`, `needsTaskCommit(TaskAttemptContext)`, `commitTask(TaskAttemptContext)`, and `abortTask(TaskAttemptContext)`. It also provides final bridge methods accepting `org.apache.hadoop.mapreduce` contexts, making it an explicit old/new API compatibility adapter.

`OutputFormat` is the old output-specification interface, deprecated in favor of the new API. It provides `getRecordWriter(FileSystem, JobConf, String, Progressable)` and `checkOutputSpecs(FileSystem, JobConf)`. `OutputLogFilter` is a `PathFilter` excluding `_logs` paths from output listings.

`Partitioner` is deprecated in favor of `org.apache.hadoop.mapreduce.Partitioner` and defines `getPartition(Object key, Object value, int numPartitions)`. `RawKeyValueIterator` exposes raw sorted/merged intermediate records via `DataInputBuffer` key/value accessors, `next`, `close`, and `getProgress`.

`RecordReader` and `RecordWriter` are the old input/output data contracts. `RecordReader` creates key/value instances, reads into them, reports byte position and progress, and closes. `RecordWriter` writes key/value pairs and closes with a `Reporter`.

### Reducer, reporting, and running jobs

`Reducer` is the old reducer interface, deprecated in favor of `org.apache.hadoop.mapreduce.Reducer`. It extends `JobConfigurable` and `Closeable` and defines `reduce(Object key, Iterator values, OutputCollector output, Reporter reporter)`. Its documentation describes shuffle, sort, secondary sort via grouping comparator, reducer output behavior, object reuse risks, counters, status, and progress reporting.

`Reporter` extends `Progressable` and allows task code to set status, fetch or increment enum/string counters, and obtain the current map `InputSplit`. Its public `NULL` field is a no-op reporter.

`RunningJob` is the client-side job handle. It exposes job identity and metadata (`getID`, deprecated `getJobID`, name, file, tracking URL), progress for map/reduce/setup/cleanup, completion/success checks, blocking `waitForCompletion`, `getJobState`, `killJob`, `setJobPriority`, task completion events, task killing and failure APIs, counters, and diagnostic retrieval.

### SequenceFile formats and skip records

The sequence-file section covers binary and text wrappers:

- `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read raw binary key/value bytes.
- `SequenceFileAsBinaryOutputFormat` writes binary key/value bytes and includes nested `WritableValueBytes`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to their string forms.
- `SequenceFileInputFormat`, `SequenceFileOutputFormat`, and `SequenceFileRecordReader` expose old API sequence-file reading/writing, with deprecation guidance toward the new `mapreduce.lib` formats for input/output formats.

`SequenceFileInputFilter` adds sampling/filtering over sequence files. The nested `Filter` interface is `Configurable` and defines `accept(Object key)`. `FilterBase` stores configuration. `MD5Filter` selects records where `MD5(key) % frequency == 0`, `PercentFilter` selects by record number modulo frequency, and `RegexFilter` accepts keys matching a configured regex.

`SkipBadRecords` is a static configuration utility for skip mode. It exposes getters/setters for attempts before skipping, automatic mapper/reducer processed counters, skip output path, mapper max skip records, and reducer max skip groups. Public counter names are `COUNTER_GROUP`, `COUNTER_MAP_PROCESSED_RECORDS`, and `COUNTER_REDUCE_PROCESSED_GROUPS`. Documentation explains the runtime protocol: after enough deterministic failures, tasks report record ranges to the TaskTracker so failed ranges can be skipped on later attempts.

### Task identity, reports, logs, and trackers

`TaskAttemptContext` is the old API context extending the new `mapreduce.TaskAttemptContext`, deprecated in favor of the new class. It exposes `getTaskAttemptID`, `getProgressible`, `getJobConf`, and `progress`.

`TaskAttemptID` and `TaskID` both extend their newer `org.apache.hadoop.mapreduce` counterparts while preserving old API return types and parsing helpers. They provide constructors, `downgrade(...)`, `read(DataInput)`, `forName(String)`, and regex pattern builders for matching task IDs or attempt IDs. Documentation emphasizes immutable IDs and warns applications not to parse ID strings manually.

`TaskCompletionEvent` is `Writable` and `Comparable`, carrying event ID, task ID, task tracker HTTP address, status, runtime, and event-string formatting. Nested `Status` enum includes `FAILED`, `KILLED`, `SUCCEEDED`, `OBSOLETE`, and `TIPFAILED`.

`TaskGraphServlet` and `TaskLogServlet` are HTTP servlets for job/task visualizations and logs. `TaskLog` is a static utility around user logs under `hadoop.log.dir`, exposing log-file lookup, real log location lookup, index-file lookup, synchronized log syncing, cleanup, configured log length, command wrapping for stdout/stderr capture with tailing and pid-file support, command quoting, and debug-output capture. Nested `TaskLog.LogName` enum includes `STDOUT`, `STDERR`, `SYSLOG`, `PROFILE`, and `DEBUGOUT`. `TaskLogAppender` is a log4j `FileAppender` with task ID and total log size properties.

`TaskReport` implements `Writable` and contains task ID, progress, state string, diagnostics, counters, `TIPStatus`, start/finish times, successful attempt, running attempts, equality/hash behavior, and serialization.

`TaskTracker` implements `MRConstants`, `TaskUmbilicalProtocol`, and `Runnable`. It exposes instrumentation configuration, storage cleanup, shutdown/close, JobTracker connection access, report address, JVM manager, server retry loop, child-task RPC methods (`getTask`, `statusUpdate`, diagnostics, next record range, ping, commit-pending/can-commit/done), shuffle/fs/fatal error reporting, map completion event lookup, lost map-output reporting, idleness, `main`, and task memory-manager access. `TaskTracker.MapOutputServlet` serves map outputs over Jetty to reducer nodes.

`TextInputFormat` and `TextOutputFormat` provide old API text IO, deprecated in favor of newer mapreduce formats. `TextOutputFormat.LineRecordWriter` writes lines to a `DataOutputStream`. `TIPStatus` enum models task-in-progress states `PENDING`, `RUNNING`, `COMPLETE`, `KILLED`, and `FAILED`.

### Job control and joins

`org.apache.hadoop.mapred.jobcontrol.Job` encapsulates a MapReduce job plus dependencies. It holds job name, control-layer job ID, assigned mapred job ID, `JobConf`, state, message, `JobClient`, and depending jobs. State constants are `SUCCESS`, `WAITING`, `RUNNING`, `READY`, `FAILED`, and `DEPENDENT_FAILED`. It can add dependencies only while waiting, test completion/readiness, and submit when ready.

`JobControl` implements `Runnable` and tracks groups of dependent jobs in state-specific collections. It exposes getters for waiting/running/ready/successful/failed jobs, `addJob`, `addJobs`, control-thread state, `stop`, `suspend`, `resume`, `allFinished`, and `run`. The main loop checks running jobs, updates waiting jobs, and submits ready jobs.

The `org.apache.hadoop.mapred.join` section begins the composable join framework. `ArrayListBackedIterator` implements `ResetableIterator` with in-memory storage, replay, reset, add, close, and clear operations. `ComposableInputFormat` refines `InputFormat` to return a `ComposableRecordReader`. `ComposableRecordReader` extends `RecordReader` and `Comparable`, exposing reader ID, current key access/cloning, `hasNext`, `skip`, and `accept` into a `CompositeRecordReader.JoinCollector`.

`CompositeInputFormat` implements `ComposableInputFormat`. It parses composite expressions from `mapred.join.expr`, installs default parser identifiers, creates aligned `CompositeInputSplit`s from child input formats, constructs a composable record reader, and exposes static `compose` helpers for table and operation expressions. This chunk ends before the `Path[]` compose overload is fully closed.

## Control Flow and Behavioral Contracts

The old MapReduce execution flow captured here runs from job submission through JobTracker scheduling and TaskTracker execution. Clients obtain a `JobID`, submit with `JobTracker.submitJob`, monitor `JobStatus`/`RunningJob`, inspect counters and task reports, and optionally kill jobs or tasks. JobTracker accepts TaskTracker heartbeats, returns launch/kill/reset instructions, allocates job IDs, tracks active/blacklisted trackers, exposes queue state, and serves RPCs for diagnostics and task events.

Task execution flows through input formats creating `RecordReader`s, the default `MapRunner` repeatedly invoking a configured `Mapper`, `OutputCollector` buffering outputs, partitioning/grouping/sorting through `Partitioner` and raw iterators, `Reducer.reduce` consuming grouped values, and `OutputFormat`/`RecordWriter` writing final output. `OutputCommitter` controls setup, temporary output, task commit, abort, and cleanup, while bridging old and new context classes.

TaskTracker control flow is callback/RPC heavy: child JVMs fetch tasks, report progress/status, ask whether they can commit, signal completion, and report errors. Reducers fetch map completion events and map outputs through TaskTracker HTTP servlets. Log flow wraps child commands to capture stdout/stderr/debug output, syncs log indexes, and serves logs over HTTP.

Bad-record skipping is a retry feedback flow. After configured failure attempts, task code or framework counters identify processed ranges; tasks report the next record range to the TaskTracker; if a task crashes, the last reported range can be skipped on subsequent attempts. Mapper and reducer auto-increment flags decide whether the framework or application owns processed-record/group counters.

`jobcontrol` adds a dependency orchestration flow above MapReduce jobs. Jobs begin `WAITING`; dependency success moves them to `READY`; dependency failure moves them to `DEPENDENT_FAILED`; ready jobs are submitted and become `RUNNING`; final job state becomes `SUCCESS` or `FAILED`. `JobControl.run` maintains separate state tables and can be stopped, suspended, or resumed.

The join API flow starts with a composite expression string, parses it into child input formats and join operators, aligns the ith split from each child into a composite split, then drives `ComposableRecordReader`s that can compare keys, skip ahead, and accept matching records into a join collector.

## State, Persistence, and Side Effects

The XML itself persists the Hadoop 0.20.1 public API surface. Runtime state appears in the APIs it describes:

- `Writable` types (`JobProfile`, `JobQueueInfo`, `JobStatus`, `TaskCompletionEvent`, `TaskReport`) persist RPC and history-facing state through `DataInput`/`DataOutput`.
- Job and task IDs encode JobTracker identifier, job number, map/reduce marker, task number, and attempt number in stable string forms; regex pattern helpers expose that format.
- `JobTracker` holds mutable scheduler state, tracker state, blacklists, queues, job tables, topology data, counters, and listener registrations.
- `TaskTracker` holds local storage, child JVM/task state, map outputs, logs, status reports, memory manager state, and the connection to JobTracker.
- Input and output formats persist job results through `FileSystem`, `MapFile`, `SequenceFile`, and text outputs.
- `OutputCommitter` is responsible for temporary and final output directories, so its behavior is a persistence boundary.
- `TaskLog` and `TaskLogAppender` persist task stdout, stderr, syslog, profiler output, and debug output under local log directories.
- `SkipBadRecords` stores behavior in `Configuration`/`JobConf` and writes skipped records to a configured output path unless disabled.
- `JobControl` maintains in-memory dependency state and submitted mapred job IDs.

Several APIs are synchronized in the XML, especially job status accessors, JobTracker mutation/RPC methods, TaskTracker child callbacks, and TaskLog sync/cleanup operations. That marks them as concurrency-sensitive public contracts even though the XML does not show locking internals.

## Dependencies and Integration Points

This chunk sits at the intersection of Hadoop's old and new MapReduce APIs. Many old `mapred` classes extend or bridge to `org.apache.hadoop.mapreduce` equivalents (`JobID`, `TaskID`, `TaskAttemptID`, `TaskAttemptContext`, and `OutputCommitter`), while deprecation text points users toward newer input/output/mapper/reducer classes.

Core Hadoop dependencies include `JobConf`, `Configuration`, `FileSystem`, `Path`, `Writable`, `WritableComparable`, `SequenceFile`, `MapFile`, `Counters`, `Progressable`, `Progress`, `Node`, `QueueManager`, `JobClient`, `JobInProgress`, `TaskInProgress`, `TaskStatus`, `TaskTrackerStatus`, `HeartbeatResponse`, `JvmManager`, `JVMId`, and `SortedRanges.Range`.

External dependencies include Java IO and networking (`DataInput`, `DataOutput`, `IOException`, `File`, `InetSocketAddress`), collections, servlet APIs (`HttpServlet`, request/response, `ServletException`), log4j (`FileAppender`, `LoggingEvent`), Commons Logging (`Log`), and Java regex for sequence-file filtering.

Operational integration points are broad: JobTracker RPC services, TaskTracker umbilical RPC, HTTP map-output shuffle, HTTP task logs, Hadoop service authorization, queue management, filesystem output commit, local task logs, child process command wrapping, and MapReduce application callbacks through `Mapper`, `Reducer`, `Reporter`, and `OutputCollector`.

## Risks and Compatibility Notes

This range starts and ends at chunk boundaries inside class/method entries. The `JobID` class starts in the previous chunk, and the final `CompositeInputFormat.compose(String, Class, Path[])` method continues in the next chunk. Final per-file reconciliation should merge these boundaries before drawing file-wide conclusions.

Because this is generated XML, it cannot answer implementation details such as exact null handling, validation rules, exception messages, locking scope, filesystem path layout, or serialization byte order beyond the `Writable` method signatures. Those need implementation-source confirmation.

Old/new API bridging is compatibility-sensitive. `downgrade` helpers and bridge methods must preserve old return types and string forms while interoperating with newer `mapreduce` identifiers and contexts. Removing deprecated old APIs would break Hadoop 0.20-era clients.

Job and task ID parsing is a likely regression surface. Public docs warn applications not to parse strings manually, but many integrations historically do. Changes to `forName`, regex pattern helpers, zero padding, map/reduce marker characters, or null wildcard behavior can break tooling.

JobTracker and TaskTracker APIs expose synchronized mutable cluster control paths. Heartbeat processing, task commit authorization, failure reporting, blacklisting, queue introspection, job kill/fail actions, and map-output loss reporting are operationally critical; races or changed state transitions can lose work, double-commit output, or strand tasks.

Output commit and task log APIs are persistence boundaries. Incorrect temporary-output promotion, cleanup, log truncation, command quoting, or index syncing can cause data loss, overwritten outputs, missing diagnostics, or command execution vulnerabilities.

`SkipBadRecords` trades correctness for progress by dropping records or groups. Defaults, thresholds, counter ownership, and skip-output path semantics need careful testing because users may rely on deterministic bad records being skipped without hiding too much data loss.

The sequence-file filters rely on configuration and key string/digest semantics. MD5 modulo, percent counters, and regex matching must remain stable for reproducible sampled jobs.

The join API relies on sorted/compatible child inputs and matching split counts. The XML documents split alignment by index and composable reader contracts, so mismatched child splits, non-comparable keys, parser expression errors, or unbounded in-memory `ArrayListBackedIterator` use are important risks.

## Test Signals

JDiff-level checks should verify this XML segment remains well formed across class/package boundaries, preserves all public/protected signatures, implemented interfaces, deprecation strings, synchronized/static/final/abstract flags, field constants, checked exceptions, and Javadoc-bearing contracts.

Job identity and status tests should cover `JobID`, `TaskID`, and `TaskAttemptID` constructors, `downgrade`, `read`, `forName`, regex pattern helpers with null wildcards, malformed IDs, deprecated string getters, `Writable` round trips for `JobProfile`, `JobQueueInfo`, `JobStatus`, `TaskCompletionEvent`, and `TaskReport`, clone behavior, and all documented enum constants.

JobTracker and TaskTracker integration tests should exercise job ID allocation, submission, cluster status, queue lookup, heartbeat response sequencing, tracker blacklisting, topology lookup, task report retrieval, diagnostics, task kill/fail, map completion events, lost map output, commit-pending/can-commit/done flows, shuffle/fs/fatal error reports, shutdown/cleanup, and service ACL refresh.

MapReduce API tests should cover mapper and reducer progress/counter reporting, object reuse warnings, default `MapRunner`, custom `MapRunnable`, `Partitioner` routing, raw key/value iterator progression, reporter `NULL`, record reader/writer close behavior, output spec validation, and output committer setup/commit/abort/cleanup including the new-context bridge methods.

Input/output format tests should cover text and key-value separators, compressed and unsplittable files if supported by implementation, line offsets and progress, map file writing/reading/partitioned lookup, sequence-file input/output, binary sequence wrappers, text sequence wrappers, and sequence-file filter behavior for MD5, percent, and regex filters.

Skip-record tests should cover default disabled behavior, attempts-before-skipping, mapper/reducer auto counter flags, application-owned counters, skip output path null/non-null behavior, max skip thresholds including `0` and `Long.MAX_VALUE`, repeated deterministic failures, and reporting of next record ranges to TaskTracker.

Task log and servlet tests should cover log file and index path construction, cleanup retention, synchronized log syncing, stdout/stderr/debug command wrapping with and without tailing and pid files, shell quoting edge cases, log4j appender flush/close, task log URL construction, servlet log retrieval, and map-output servlet serving behavior.

JobControl tests should cover dependency addition only while waiting, state transitions from `WAITING` to `READY`, dependency failure to `DEPENDENT_FAILED`, successful submission to `RUNNING`, completion to `SUCCESS` or `FAILED`, `allFinished`, and suspend/resume/stop behavior in the control thread.

Join tests should cover composite expression parsing from `mapred.join.expr`, default and user-defined join identifiers, table expression composition, `String[]` and `Path[]` compose helpers, split count alignment, `ComposableRecordReader` key comparison/skip/accept contracts, and memory behavior of `ArrayListBackedIterator` versus stream-backed alternatives.
