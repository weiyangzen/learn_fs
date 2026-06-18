# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 18673-24869

## Chunk Scope

This chunk is a JDiff API snapshot for Hadoop 0.19.1. It starts inside `org.apache.hadoop.mapred.ClusterStatus`, then covers a large public `org.apache.hadoop.mapred` API section through `MultiFileSplit`. The visible surface includes counters, file input/output formats, splits, job submission/configuration/status/history APIs, the JobTracker service facade, text record readers, map execution contracts, and multi-file input splitting.

Because this is generated API XML rather than implementation source, control-flow, state, and persistence notes are inferred from exposed signatures, inheritance, synchronization flags, checked exceptions, deprecation markers, fields, and embedded Javadocs.

## Purpose

The chunk records the public compatibility surface of the old `mapred` MapReduce API. It shows how Hadoop 0.19.1 clients configure jobs, submit and monitor them, describe input/output formats, split files, read records, emit map output, collect counters, persist job status/profile/queue objects, and log/read job history.

This API surface is important for compatibility because it captures both user-facing extension points (`Mapper`, `MapRunnable`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `OutputCommitter`) and cluster/internal-facing integration points (`JobClient`, `JobTracker`, `JobHistory`, `JobStatus`, `JobID`, `Counters`). The XML also exposes older/deprecated overloads that migration tooling must preserve or intentionally replace.

## Important APIs and Types

### Cluster and Counter State

The chunk begins in the tail of `ClusterStatus`, showing capacity and health accessors such as `getMaxMapTasks()`, `getMaxReduceTasks()`, `getJobTrackerState()`, plus `Writable` serialization through `write(DataOutput)` and `readFields(DataInput)`. The class documents cluster size, map/reduce capacity, running task counts, and JobTracker state as values returned by `JobClient#getClusterStatus()`.

`Counters` implements `Writable` and `Iterable<Counters.Group>`. It provides synchronized APIs to retrieve group names, iterate groups, find counters by enum or `(group, name)`, increment counters, sum counters, compute total size, serialize/deserialize all groups, log values, and convert to compact or escaped compact strings. `fromEscapedCompactString(String)` can reconstruct a `Counters` object and throws `ParseException` on malformed text.

`Counters.Counter` is a synchronized `Writable` record with internal name, display name, current long value, binary read/write, compact escaped string rendering, display-name mutation, and `increment(long)`.

`Counters.Group` is a `Writable` and `Iterable<Counters.Counter>` grouping counters by enum class or group name. It exposes raw and display names, display-name mutation, compact escaped rendering, `getCounter(String)` returning zero for missing counters, deprecated numeric-id lookup, create-on-demand `getCounterForName(String)`, size, serialization, and iteration.

### File-Based Input and Splits

`FileInputFormat<K,V>` is the base class for file-backed `InputFormat`. It implements `InputFormat<K,V>` and exposes split sizing and path discovery behavior:

- `setMinSplitSize(long)`, `isSplitable(FileSystem, Path)`, `listStatus(JobConf)`, `getSplits(JobConf, int)`, `computeSplitSize(long, long, long)`, and `getBlockIndex(BlockLocation[], long)` define file listing and split planning.
- `setInputPathFilter(JobConf, Class<? extends PathFilter>)` and `getInputPathFilter(JobConf)` integrate path filters.
- Static path helpers set, add, and retrieve comma-separated or array-based input paths from `JobConf`.
- `getRecordReader(InputSplit, JobConf, Reporter)` remains abstract for concrete formats.

`InputFormat<K,V>` declares the central MapReduce input contract: `getSplits(JobConf, int)` computes logical work units, and `getRecordReader(InputSplit, JobConf, Reporter)` creates a reader for each split.

`InputSplit` extends `Writable` and exposes `getLength()` and `getLocations()`, carrying scheduler-relevant byte size and data-locality hostnames.

`FileSplit` implements `InputSplit` for a byte range of a single file. Constructors accept path, start, length, and either `JobConf` or explicit host locations. Accessors expose path, start, length, host locations, `toString()`, and Writable serialization.

`MultiFileInputFormat<K,V>` extends `FileInputFormat` and returns `MultiFileSplit` instances. It groups whole files into nearly equal content-length splits; subclasses provide a record reader for each multi-file split.

`MultiFileSplit` implements `InputSplit` for a set of whole files rather than a byte range. Its constructor takes `JobConf`, `Path[]`, and `long[]` lengths. It exposes total length, per-file lengths, number of paths, individual/all paths, locations, serialization, and string conversion. The chunk ends before the next `OutputCollector` interface begins, so the complete end of `MultiFileSplit` is visible but following output APIs are outside this item.

### Output Paths and Commit

`FileOutputFormat<K,V>` implements `OutputFormat<K,V>` and is the base for file-backed job output. It provides output compression toggles and codec configuration, abstract `getRecordWriter(...)`, output-spec validation, output path get/set helpers, task work path creation, task output path helpers, unique task filename generation, and custom file path generation.

`FileOutputCommitter` defines the standard file-output commit lifecycle with `setupJob`, `cleanupJob`, `setupTask`, `commitTask`, `abortTask`, and `needsTaskCommit`. Its visible fields include `TEMP_DIR_NAME` and `LOG`. The class documentation ties it to files written under `FileOutputFormat#getTaskOutputPath(...)`, which are promoted during commit and cleaned on abort.

`MapFileOutputFormat` extends `FileOutputFormat<WritableComparable, Writable>`. It writes `MapFile`s, exposes a `RecordWriter`, opens generated outputs via static `getReaders(FileSystem, Path, Configuration)`, and retrieves a key through static `getEntry(MapFile.Reader[], Partitioner<K,V>, K, V)`.

### Exceptions and Identifiers

`FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are public failure types used by input/output validation and job configuration. `InvalidInputException` wraps multiple `IOException` problems, exposes `getProblems()`, and formats a summary message.

`ID` is the base `WritableComparable<ID>` for numeric identifiers. It stores protected `int id`, supports default/int constructors, `getId()`, string conversion, equality/hash, numeric ordering, read/write, static `read(DataInput)`, and `forName(String)`.

`JobID` extends the ID family for immutable job identifiers. It combines a JobTracker identifier with a job number, compares first by tracker identifier then job number, serializes/deserializes itself, parses string forms through `forName(String)`, and exposes `getJobIDsPattern(...)` for matching job IDs.

### Job Client and Configuration

`JobClient` implements `MRConstants` and `Tool`. It is the primary user-job interface to the MapReduce system. Constructors support default construction, construction from `JobConf`, and direct connection to a JobTracker `InetSocketAddress`. Important APIs include:

- Lifecycle and setup: `getCommandLineConfig()`, `init(JobConf)`, `close()`, and `getFs()`.
- Submission: `submitJob(JobConf)`, `submitJob(String)`, `isJobDirValid(Path, FileSystem)`, and static `runJob(JobConf)`.
- Monitoring: `getJob(JobID)`, deprecated `getJob(String)`, map/reduce/setup/cleanup task reports, cluster status, jobs to complete, all jobs, default map/reduce capacity, system directory, queues, queue info, and jobs from a queue.
- CLI support: `run(String[])`, `main(String[])`, and `TaskStatusFilter` getter/setter helpers backed by `JobConf`.

`JobClient.TaskStatusFilter` is an enum-like nested type exposed through `values()` and `valueOf(String)`, used to select which task outputs are printed.

`JobConf` is the central mutable job configuration and extends the Hadoop configuration stack. This slice exposes constructors from class, configuration, configuration plus example class, file path/string path, and a boolean controlling default resource loading. It has a broad set of typed getters/setters:

- Job packaging and local state: jar path, jar-by-class lookup, local dirs, local file deletion, local path allocation, user, working directory, job local scratch dir, and session ID.
- Input/output components: input format, output format, output committer, output key/value classes, map output key/value classes, comparators, grouping comparator, key-field comparator and partitioner options.
- Execution components: mapper, map runner, partitioner, reducer, combiner, map/reduce counts, max task attempts, max failures per tracker, tolerated map/reduce failure percentages, JVM task reuse count, speculative execution globally and per task type.
- Compression: map-output compression toggle and codec.
- Metadata and operations: job name, priority, queue name, profile enablement/parameters/ranges, debug scripts, and job-end notification URI.

The class field `DEFAULT_QUEUE_NAME` records the fallback queue. Many `JobConf` APIs are public compatibility hooks around string configuration keys, so behavior depends on stable key names and defaults even when method bodies are absent from the XML.

`JobConfigurable` is a small extension point with `configure(JobConf)`. `MapReduceBase`, `Mapper`, `MapRunnable`, and many input formats use it for job-scoped initialization.

`JobContext` exposes `getJobConf()` and `getProgressible()`, pairing job configuration with a progress callback.

### Job History

`DefaultJobHistoryParser` parses a job history log file into a `JobHistory.JobInfo` object, with `parseJobTasks(String, JobInfo, FileSystem)` as the visible parser entry point.

`JobHistory` provides static-style history logging and parsing support. It exposes initialization, parsing from `FileSystem` into a `JobHistory.Listener`, history disable toggles, and task log URL lookup. Fields include `LOG` and `JOB_NAME_TRIM_LENGTH`.

`JobHistory.HistoryCleaner` implements `Runnable` and deletes history files older than one month while updating the master index, according to its class docs.

`JobHistory.JobInfo` records job-level history and has helpers for all tasks, local job file path, URL encoding/decoding of history file paths/names, user extraction from job configuration, history log locations, user history locations, recovery of history file names, and event logging. Logging methods cover submitted, initialized, started, finished, failed, killed, priority, and job submit/launch info events.

`JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` model task and attempt history records. They provide logging APIs for start, finish, failure, and killed events, with map/reduce attempt overloads that capture host, tracker, error, and phase timing details. `Task#getTaskAttempts()` exposes attempts keyed by task-attempt ID.

`JobHistory.Keys`, `RecordTypes`, and `Values` are enum-like nested types for history log key names, line record types, and common values. `JobHistory.Listener#handle(RecordTypes, Map<Keys,String>)` is the callback contract for parsers.

### Job Metadata, Queues, and Status

`JobProfile` implements `Writable` and tracks user, job ID, job file, web UI URL, job name, and queue name. It keeps deprecated string job-id constructors and `getJobId()` alongside the typed `JobID` path.

`JobQueueInfo` implements `Writable` and carries queue name plus scheduling info, with default and `(queueName, schedulingInfo)` constructors and read/write support.

`JobStatus` implements `Writable` and `Cloneable`. It exposes constants `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`; constructors for job ID, map/reduce/setup/cleanup progress, run state, and priority; progress accessors; run-state mutation; start time; username; scheduling info; priority; clone; and binary serialization.

`JobPriority` is an enum-like priority type exposed through `values()` and `valueOf(String)`.

`JobShell` implements `Tool` and wraps command-line parsing for job submission through constructors, `init(JobConf)`, `run(String[])`, and `main(String[])`.

### JobTracker Service Surface

`JobTracker` implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. Its public/static surface represents both daemon lifecycle and RPC service behavior:

- Lifecycle and identity: `startTracker(JobConf)`, `stopTracker()`, `offerService()`, `main(String[])`, protocol version, restart/recovery flags, recovery duration, instrumentation class get/set, address, machine, tracker identifier, tracker/info ports, start time, build version, filesystem name, and local job file path.
- Cluster and topology: running/failed/completed jobs, task trackers, tracker lookup, network topology node resolution and lookup, cache-level counts, unique host counts, resolved tracker counts, and queue manager access.
- Scheduling integration: add/remove `JobInProgressListener`, `heartbeat(TaskTrackerStatus, boolean, boolean, short)` returning `HeartbeatResponse`, next heartbeat interval calculation, and task-tracker error reporting.
- Submission and job control: new job IDs, job submission, cluster status, kill job, set priority, job profile/status/counters, task reports, completion events, diagnostics, task lookup, task killing, assigned tracker lookup, jobs-to-complete, all jobs, system dir, queue list/info/jobs.

`JobTracker.IllegalStateException` reports attempts to submit a job before the tracker is ready. `JobTracker.State` is an enum-like type exposed through `values()` and `valueOf(String)`.

### Text Record Readers and Map Execution

`KeyValueLineRecordReader` implements `RecordReader<Text,Text>`. It reads one line as a key/value pair separated by a configured separator, exposes key/value class creation, a `findSeparator(...)` helper, `next(Text, Text)`, progress, position, and close.

`KeyValueTextInputFormat` is a plain-text file input format that breaks files into lines and uses the separator to split key from value. It implements `JobConfigurable`, exposes `configure(JobConf)`, splitability, and a `RecordReader<Text,Text>`.

`LineRecordReader` implements `RecordReader<LongWritable,Text>` and treats each line as a record with the byte offset as key and line text as value. Constructors support `Configuration` plus `FileSplit`, and lower-level `InputStream`/start/end variants. It exposes key/value creation, `next(LongWritable, Text)`, progress, synchronized position, and synchronized close. `LineRecordReader.LineReader` is deprecated in favor of `org.apache.hadoop.util.LineReader`.

`Mapper<K1,V1,K2,V2>` extends `JobConfigurable` and Hadoop `Closeable`. Its `map(K1, V1, OutputCollector<K2,V2>, Reporter)` method emits zero or more intermediate key/value pairs and can report progress, status, and counters. The docs describe the standard old-API map flow: one map task per input split, optional initialization through `configure`, per-record `map` calls, intermediate `SequenceFile` storage, partitioning by `Partitioner`, optional combiner, comparator-configured grouping, and direct output when reducer count is zero.

`MapReduceBase` provides no-op `close()` and `configure(JobConf)` defaults for Mapper and Reducer implementations.

`MapRunnable<K1,V1,K2,V2>` extends `JobConfigurable` and lets advanced users control map execution by implementing `run(RecordReader<K1,V1>, OutputCollector<K2,V2>, Reporter)`. This is the hook for asynchronous or multithreaded mapper behavior.

`MapRunner` is the default `MapRunnable` implementation. It configures a mapper, runs the record-reader loop, writes output through the collector, and exposes protected `getMapper()` for subclasses.

## Control Flow and Behavioral Contracts

MapReduce input planning flows from `JobConf` input path configuration into `FileInputFormat.listStatus`, path filtering, block-location lookup, and split creation. Concrete input formats then receive each `InputSplit` and return a `RecordReader` that produces key/value objects for a mapper.

File split scheduling depends on `InputSplit.getLength()` and `getLocations()`. `FileSplit` models byte ranges with locality hints, while `MultiFileSplit` intentionally changes the unit of work to whole files grouped by total length.

Map execution flows through `MapRunner.run`: a `RecordReader` supplies records, the configured `Mapper.map` transforms them, `OutputCollector.collect` receives intermediate pairs, and `Reporter` carries liveness, status, and counter updates. Custom `MapRunnable` implementations can replace that loop.

Job submission flows through `JobClient` into a JobTracker: validate/stage job directory, request or use a `JobID`, submit job configuration, and obtain a `RunningJob`/status object for monitoring. `runJob(JobConf)` adds a polling loop until completion.

Cluster management and task scheduling flow through JobTracker RPC and heartbeat methods. TaskTrackers send heartbeats with status; JobTracker returns `HeartbeatResponse` instructions, tracks topology and cache levels for locality, maintains job lists, and exposes job/task control operations to clients.

Output flow uses `FileOutputFormat` to validate and assign output paths, `RecordWriter` to write task output, and `FileOutputCommitter` to move task-temporary outputs into final output during commit or remove them during abort.

History flow uses `JobHistory.JobInfo`, `Task`, and `TaskAttempt` logging methods to append key/value event records for submitted/started/finished/failed/killed jobs and attempts. Parsing reverses the flow through `DefaultJobHistoryParser` or `JobHistory.parseHistoryFromFS`, invoking a listener or populating object-model records.

Writable flow is consistent across counters, splits, IDs, profiles, queue info, status, and counter groups: `write(DataOutput)` persists fields in a Hadoop binary protocol and `readFields(DataInput)` reconstructs mutable objects.

## State and Persistence Behavior

The JDiff XML itself persists the 0.19.1 public API, but the exposed APIs describe several runtime state stores.

`Counters`, `Counters.Group`, and `Counters.Counter` are mutable in-memory job/task metrics with synchronized mutation and read paths. They persist through `Writable` binary serialization and through compact escaped text strings suitable for logs or UI transfer.

`JobConf` is mutable configuration state. Its typed methods persist job settings into configuration keys for input/output classes, jar location, paths, compression, comparators, mapper/reducer classes, task counts, retries, speculation, profiling, debugging, notifications, priority, queue, user, and working directories.

`FileSplit`, `MultiFileSplit`, `JobID`, `JobProfile`, `JobQueueInfo`, and `JobStatus` are wire/storage records. Their `Writable` methods are compatibility-sensitive because JobTracker, JobClient, task launch, and history tools exchange them across process boundaries.

`FileOutputCommitter` persists task outputs indirectly by manipulating filesystem paths under the configured temporary directory and final output directory. Commit and abort behavior determines whether speculative or failed task attempts leave visible data.

`JobHistory` persists append-only job, task, and attempt event records on a filesystem, has recovery helpers for partially generated history files, exposes per-user history log locations, and includes a cleaner runnable that removes old history data.

`JobTracker` owns central daemon state: submitted/running/failed/completed jobs, task tracker statuses, topology mappings, listener registrations, queue manager state, recovery/restart flags, tracker identity, heartbeat scheduling state, and counters/status/profile/task reports exposed over protocols.

Record readers keep per-split cursor state: current file position, split start/end, current line, configured key/value separator, and progress. `LineRecordReader` exposes synchronized `getPos()` and `close()`, implying concurrent status/cleanup access may occur.

## Dependencies and Integration Points

This chunk depends on Hadoop core IO and filesystem types: `Writable`, `WritableComparable`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`, `RawComparator`, compression codecs, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, and `PathFilter`.

MapReduce integration types visible in signatures include `JobConf`, `Reporter`, `RecordReader`, `RecordWriter`, `OutputCollector`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, `JobInProgress`, `TaskInProgress`, `TaskTrackerStatus`, `HeartbeatResponse`, `QueueManager`, `Partitioner`, `Reducer`, and protocol interfaces such as `JobSubmissionProtocol` and `InterTrackerProtocol`.

Java dependencies include `DataInput`, `DataOutput`, `IOException`, `InetSocketAddress`, collections, regex/pattern strings for task-file retention and ID matching, and URL handling in `JobProfile`.

Apache Commons Logging appears through public `LOG` fields in classes such as `FileInputFormat`, `FileOutputCommitter`, and `JobHistory`.

Operational integration points include filesystem-backed job staging/output/history directories, JobTracker RPC, TaskTracker heartbeat protocols, network topology resolution for locality, queue scheduling, history parsing/listener callbacks, and CLI `Tool` entry points in `JobClient` and `JobShell`.

## Risks and Edge Cases

This is generated API metadata, so it does not reveal exact implementation details such as lock ordering, retry logic, filesystem rename semantics, parser escaping code, or validation branches.

The chunk starts mid-`ClusterStatus` and ends before `OutputCollector`; adjacent chunks are needed for a complete per-file report around those boundary classes/interfaces.

Counter serialization and escaped compact strings are compatibility-sensitive. Malformed strings raise `ParseException`, and callers relying on display names must preserve group/counter name escaping.

Several APIs retain deprecated string or numeric-ID forms, including counter lookup by ID, `JobClient` string job IDs, and `JobProfile#getJobId()`. Compatibility code must handle both old and typed `JobID` paths.

`FileInputFormat` path handling has many edge cases: comma-separated path parsing, filters, missing/invalid inputs, splitability for compressed files, block-index selection, and min/max split sizing.

`FileOutputCommitter` behavior is high risk under failure or speculative execution because duplicate task attempts may write temporary data and only one should become committed output.

`JobConf` exposes many loosely typed class and configuration settings. Missing mandatory attributes surface as `InvalidJobConfException`, but class mismatches or default fallback behavior require implementation review.

`JobTracker` is a central mutable service with many public methods. Heartbeat interval calculations, recovery state, topology resolution, queue manager behavior, and task killing can affect cluster correctness and availability.

Job history recovery and cleanup can lose diagnostic data if recovery chooses the wrong file, URL encoding/decoding changes, or the history cleaner removes files still needed by tools.

Text record readers must handle split boundaries, separators, long lines, compressed splitability, byte offsets, and final lines without terminators. Incorrect position/progress reporting can cause duplicate or skipped records.

`MultiFileSplit` changes the split unit from byte ranges to whole files, so it can produce poor load balance when individual files are large even if total split lengths are nearly equal.

## Test Signals

Useful tests inferred from this API slice include:

- `Counters` round trips through `Writable`, compact string, and escaped compact string forms, including display names, missing counters, enum counters, deprecated numeric lookup, group iteration, and concurrent-style synchronized access.
- `FileInputFormat` tests for input path set/add/get, comma-separated paths, path filters, invalid input aggregation, split sizing, block index selection, unsplittable files, and `FileSplit` location serialization.
- `MultiFileInputFormat` and `MultiFileSplit` tests for whole-file grouping, total/per-file length reporting, path serialization, location reporting, and string output.
- `FileOutputFormat` tests for output path validation, compression codec settings, task output/work paths, unique names, custom file paths, and output directory already-exists failures.
- `FileOutputCommitter` tests for setup, commit, abort, cleanup, `needsTaskCommit`, failed attempts, and speculative duplicate attempts.
- `JobConf` tests for every major typed getter/setter pair: classes, compression, comparators, task counts, retries, speculation, profiling, debug scripts, notification URI, priority, queue, local dirs, working directory, and jar-by-class.
- `JobClient` integration tests for job submission, invalid job directory detection, job lookup by typed and deprecated IDs, task reports, cluster status, queues, task output filters, and CLI `run`.
- `JobHistory` tests for submitted/started/finished/failed/killed event logging, map/reduce attempt events, parser listener callbacks, object-model population, filename/path encoding, recovery file selection, disable-history behavior, and cleaner expiry.
- `JobStatus`, `JobProfile`, `JobQueueInfo`, `ID`, and `JobID` `Writable` compatibility tests, including equality, ordering, hash codes, string parsing, and deprecated accessor behavior.
- `JobTracker` service tests around heartbeat responses, new job IDs, submission readiness, kill job/task, priority changes, task diagnostics, queue information, cluster status, recovery flags, and topology-aware tracker/node lookups.
- `LineRecordReader` and `KeyValueLineRecordReader` tests for split-boundary correctness, separator discovery, missing separators, offset keys, progress/position, close idempotence, and long-line handling.
- `Mapper`, `MapRunner`, and `MapRunnable` tests that verify configure/map/close order, reporter progress and counters, zero-reducer direct output behavior, custom map runners, and exception propagation.

## Chunk Boundary Notes

The preceding chunk is needed for the beginning of `ClusterStatus` and earlier `org.apache.hadoop.mapred` APIs. The following chunk is needed for `OutputCollector`, `OutputCommitter`, output formats beyond this range, reducers, reporters, records, task IDs/statuses, and the rest of the old `mapred` package. The final merged report should preserve that this chunk is a middle slice of the package rather than a complete package summary.
