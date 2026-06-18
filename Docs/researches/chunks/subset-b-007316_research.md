# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 31421-37637

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.20.0. It is XML API metadata rather than Java implementation source. The range starts inside the tail of `org.apache.hadoop.mapred.Counters`, continues through a large section of the old `org.apache.hadoop.mapred` MapReduce API, and ends inside the `Mapper.map(Object,Object,OutputCollector,Reporter)` method documentation.

The XML records the compatibility surface: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared checked exceptions, public fields, visibility, static/final/abstract/synchronized flags, deprecation state, and embedded Javadoc. Runtime control flow and persistence behavior below are inferred from signatures and documentation, not method bodies.

## Purpose and Major API Surface

The chunk covers the legacy `mapred` package's core job configuration, file input/output, job submission, job-tracker control, job history, job identity, queue/status data, and line-oriented input APIs. Many types are explicitly deprecated in favor of the newer `org.apache.hadoop.mapreduce` APIs, but this XML captures the 0.20.0 compatibility contract for older applications.

`Counters` is completed at the beginning of the range. The visible tail includes synchronized `size()`, `write(DataOutput)`, `readFields(DataInput)`, `toString()`, `makeCompactString()`, `makeEscapedCompactString()`, `hashCode()`, and `equals(Object)`, plus static `fromEscapedCompactString(String)`. Its wire format is documented as groups followed by counters, and its escaped textual form is documented as round-trippable. `Counters.Counter` extends `org.apache.hadoop.mapreduce.Counter` and exposes `setDisplayName(String)`, `makeEscapedCompactString()`, and synchronized `getCounter()`. `Counters.Group` implements `Writable` and `Iterable`; it exposes raw/display names, counter lookup by name, deprecated lookup by numeric id and name, size, serialization, iteration, equality, and compact stringification.

`DefaultJobHistoryParser` has `parseJobTasks(String, JobHistory.JobInfo, FileSystem)`, which populates a pre-created job history model from a history log on a Hadoop `FileSystem`. `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are public `IOException` subclasses used by validation and submission paths. `InvalidInputException` carries a list of problems and overrides `getMessage()`.

`FileInputFormat` is the abstract base for file-backed old-API `InputFormat`s. It implements `InputFormat` and provides input path configuration, optional `PathFilter` configuration, `listStatus(JobConf)`, generic `getSplits(JobConf,int)`, split sizing helpers, block-location/rack locality helpers, and abstract `getRecordReader(InputSplit,JobConf,Reporter)`. It is deprecated in favor of `mapreduce.lib.input.FileInputFormat`.

`FileOutputCommitter` implements output commit lifecycle hooks over `JobContext` and `TaskAttemptContext`: `setupJob`, `cleanupJob`, `setupTask`, `commitTask`, `abortTask`, and `needsTaskCommit`. `FileOutputFormat` is the abstract base for old-API `OutputFormat`s. It configures output compression and compression codec classes, validates output specs, sets and retrieves output paths, exposes task work output paths, and provides helpers for unique task file names and custom file paths.

`FileSplit` extends the new `mapreduce.InputSplit` while implementing old `mapred.InputSplit`. It stores a file `Path`, byte start, byte length, and host locations; it is `Writable` through `write(DataOutput)` and `readFields(DataInput)`. `ID` similarly bridges to `org.apache.hadoop.mapreduce.ID`.

`InputFormat` defines the old API's two primary methods: `getSplits(JobConf,int)` and `getRecordReader(InputSplit,JobConf,Reporter)`. `InputSplit` is a `Writable` interface with `getLength()` and `getLocations()`. These interfaces form the split planning and per-split reading contract consumed by mappers.

`JobClient` extends `Configured` and implements `MRConstants` and `Tool`. It is the client-side submission and monitoring facade for the old MapReduce system. Public methods connect to the default or explicit `JobTracker`, close the client, obtain the staging `FileSystem`, submit jobs from a job file or `JobConf`, validate job directories, retrieve `RunningJob` handles, fetch task reports, display task subsets, query cluster status, list incomplete or all jobs, run and monitor jobs, configure task output filtering, expose default map/reduce capacity, retrieve the system directory, inspect queues, and run as a CLI tool.

`JobClient.TaskStatusFilter` is an enum with `NONE`, `KILLED`, `FAILED`, `SUCCEEDED`, and `ALL`. It controls which task outputs are printed by monitoring/display flows.

`JobConf` extends `Configuration` and is the main old-API job description object. It includes constructors from classes, configurations, files, paths, and default-loading flags. Its methods configure the job jar, local dirs, user, failed-task file retention, working directory, task JVM reuse, input/output formats, output committer, compression, map output key/value classes, final output key/value classes, raw comparators, key-field comparator and partitioner options, grouping comparator, old/new mapper/reducer toggles, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce task counts, max attempts, job name, session id, failure thresholds, priority, profiling, debug scripts, completion notification URI, localized job scratch dir, virtual/physical memory limits, and queue name. Public constants include disabled memory limit, default queue name, and memory configuration keys.

`JobConfigurable` defines `configure(JobConf)`. `JobContext` extends `org.apache.hadoop.mapreduce.JobContext` while exposing old `JobConf` and a `Progressable`.

`JobEndNotifier` starts/stops notification handling, registers job-completion notification, and supports local-runner notification. `JobHistory` manages old job history logging and parsing. It can initialize history, parse history from a filesystem path, enable/disable history, and build task-log URLs. `JobHistory.HistoryCleaner` is a `Runnable` cleanup helper. `JobHistory.JobInfo` extends a key/value history record and manages task maps, encoded history paths/file names, user name, log locations, recovery of history files, and logging of submitted, initialized, started, finished, failed, killed, priority, and generic job-info records.

`JobHistory.Keys`, `RecordTypes`, and `Values` are enums describing the persisted history schema. Keys include job tracker id, times, job id/name/user/conf, map/reduce totals and completions, status, task ids, host, task type, error, attempt id, phase timestamps, counters, splits, priority, tracker name, state string, and version. Record types include job tracker, job, task, map attempt, reduce attempt, and meta. Values include success, failed, killed, map, reduce, cleanup, running, prep, and setup. `JobHistory.Listener` receives parsed history records through `handle(RecordTypes, Map)`. `MapAttempt`, `ReduceAttempt`, `Task`, and `TaskAttempt` expose static logging helpers for attempt and task lifecycle events.

`JobID` extends `org.apache.hadoop.mapreduce.JobID` and supports construction from tracker id and number, downgrade from the new API type, reading from `DataInput`, parsing with `forName(String)`, and generating job-id regex patterns. `JobPriority` is the public priority enum with `VERY_HIGH`, `HIGH`, `NORMAL`, `LOW`, and `VERY_LOW`.

`JobProfile`, `JobQueueInfo`, and `JobStatus` are public `Writable` data carriers. `JobProfile` stores user, job id, job file, tracking URL, job name, and queue name. `JobQueueInfo` stores queue name and scheduling info. `JobStatus` stores job progress, run state, start time, username, scheduling info, and priority; it defines integer states `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`, supports cloning, and serializes/deserializes itself.

`JobTracker` is the central server-side MapReduce coordinator. It implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, and `RefreshAuthorizationPolicyProtocol`. Its public API includes tracker startup/shutdown, protocol version, restart/recovery state and duration, instrumentation class configuration, network address and service loop, submission count and tracker identity/ports, running/failed/completed job lists, task-tracker collections and blacklist checks, topology lookups, job-progress listeners, queue manager access, build version, task-tracker heartbeats, filesystem/system directory queries, task-tracker error reporting, new job ids, job submission and control, cluster status, job profile/status/counters, task reports, task completion events, diagnostics, task lookup/kill, queue queries, and service ACL refresh. Nested `IllegalStateException` signals client submission before readiness, and `State` exposes `INITIALIZING` and `RUNNING`.

The tail covers text input helpers. `KeyValueLineRecordReader` implements `RecordReader` for lines split into key/value text by a configurable separator byte, with `findSeparator(byte[],int,int,byte)`, synchronized `next(Text,Text)`, position/progress, and close. `KeyValueTextInputFormat` extends `FileInputFormat`, implements `JobConfigurable`, configures separator behavior, determines splitability, and creates key/value record readers. `LineRecordReader` reads lines as `(LongWritable offset, Text line)`, with constructors from `Configuration`/`FileSplit` or raw streams, synchronized `next`, position, close, and progress. Its nested `LineReader` extends `org.apache.hadoop.util.LineReader` and is deprecated in favor of that utility. `MapFileOutputFormat` extends `FileOutputFormat`, writes `MapFile`s, opens generated `MapFile.Reader` arrays, and retrieves entries with a `Partitioner`. The chunk ends inside `Mapper`, an old-API interface extending `JobConfigurable` and `Closeable`; the visible `map` method emits zero or more intermediate pairs through `OutputCollector` and uses `Reporter` for progress/liveness.

## Control Flow and Behavioral Contracts

The old file input flow is: configure input paths and optional filters on `JobConf`; `FileInputFormat.listStatus` expands the paths and validates non-empty input; `getSplits` divides file statuses according to target split count, minimum split size, block size, splittability, and block locations; the framework passes each `InputSplit` to `getRecordReader`; mapper code receives records from the reader. Split locality is part of the contract through `getSplitHosts`, `getBlockIndex`, and `InputSplit.getLocations()`.

The output flow is: configure output path and compression on `JobConf`; `FileOutputFormat.checkOutputSpecs` validates target state before submission; tasks write through an `OutputFormat`/`RecordWriter`; task-attempt output is placed under a work path when using `FileOutputCommitter`; successful attempts are promoted by `commitTask`, failed or killed attempts are discarded by `abortTask`, and job-level cleanup finalizes the output directory. The Javadoc emphasizes side-effect-file handling under `${mapred.output.dir}/_temporary/_${taskid}` to avoid collisions from speculative attempts.

The job submission flow runs through `JobClient`: initialize a connection to `JobTracker`, prepare job files on the submission filesystem, validate a job directory, submit a `JobConf` or job-file path, and return a `RunningJob`. Monitoring then polls `RunningJob`/`JobTracker` for progress, reports task failures according to `TaskStatusFilter`, and returns success/failure from `monitorAndPrintJob` or throws from `runJob` if the job fails.

The server control flow centers on `JobTracker`: service startup creates a central scheduler/coordinator; task trackers heartbeat with status and receive `HeartbeatResponse` work/control messages; clients submit jobs and query status over `JobSubmissionProtocol`; listeners observe job progress; topology and tracker collections feed locality and scheduling; administrative paths refresh service ACLs and inspect queues. State transitions visible in this chunk include `INITIALIZING` to `RUNNING`, restart/recovery tracking, and illegal submission while not ready.

The job-history flow is append-oriented logging plus later parsing. Job, task, map-attempt, and reduce-attempt helper classes emit records keyed by `JobHistory.Keys` and typed by `RecordTypes`; `DefaultJobHistoryParser` and `JobHistory.parseHistoryFromFS` reconstruct `JobInfo` and task/attempt maps; listeners can receive record callbacks. File-name encoding/decoding and recovery helpers make history files part of the persisted job state.

The record-reader flow for line-based inputs reads bytes from a split, handles split boundaries, reports offsets/progress, and emits Hadoop writable keys/values. `KeyValueLineRecordReader` scans a line for a separator byte; absent a separator, `KeyValueTextInputFormat` documents the whole line as key and empty value. `LineRecordReader` emits the byte offset as key and line text as value.

## State, Persistence, and Side Effects

This XML file itself is persistent API compatibility data. It does not persist runtime values, but it defines stable serialization methods, configuration keys, and wire-facing signatures that old Hadoop applications depend on.

`Counters`, `Counters.Group`, `FileSplit`, `JobProfile`, `JobQueueInfo`, and `JobStatus` implement or expose `Writable` serialization. Their `write`/`readFields` contracts are compatibility-sensitive because job submission, history, RPC, and persisted metadata can rely on their binary shape. `Counters` also has compact and escaped textual encodings used in logs/history.

`JobConf` is stateful configuration. Nearly every setter mutates configuration keys that later drive job submission, task launch, scheduler choices, task memory management, compression codecs, comparator classes, distributed debug scripts, output paths, queue placement, and end notification. Public memory-key constants describe behavior that spans JobTracker scheduling and TaskTracker enforcement.

`FileInputFormat` and `FileOutputFormat` store paths, filters, compression, codecs, work output directories, and task-specific file names in `JobConf`. `FileOutputCommitter` mutates filesystem state by creating temporary output directories, promoting successful task output, and deleting or ignoring unsuccessful attempt output.

`JobClient` owns a connection to the MapReduce cluster and a filesystem handle, and its synchronized `close()` and `getFs()` indicate shared mutable client state. Submission methods stage job artifacts and create server-side jobs. CLI/monitoring methods write status to user-visible output.

`JobTracker` owns central cluster state: job maps/lists, task trackers, blacklists, queue manager, topology, recovery flags, submission counters, heartbeat state, and service ACL policy. Many accessors return mutable collection types such as `Vector`, `List`, and `Collection`, so callers may have relied on legacy object shapes even if implementations should protect internal state.

`JobHistory` persists history logs on a `FileSystem`; `HistoryCleaner` removes old history; task-log URL generation bridges persisted history with web/log access. `JobEndNotifier` sends external completion notifications and therefore has network side effects. Debug-script configuration depends on `DistributedCache` localization and task log files.

`KeyValueLineRecordReader` and `LineRecordReader` hold stream position and split boundaries, mutate caller-provided writable key/value objects on each `next`, and close underlying streams. `MapFileOutputFormat` writes `MapFile` output and opens `MapFile.Reader` instances for later lookup.

## Dependencies and Integration Points

The chunk is centered on `org.apache.hadoop.mapred`, but many classes bridge to the newer `org.apache.hadoop.mapreduce` package: `Counters.Counter`, `FileSplit`, `ID`, `JobContext`, and `JobID` extend or convert to/from new API types. Deprecation tags document migration pressure while preserving old API behavior.

Filesystem integration is pervasive through `org.apache.hadoop.fs.FileSystem`, `Path`, `FileStatus`, `BlockLocation`, and `PathFilter`. File input uses block locations and `org.apache.hadoop.net.NetworkTopology` for locality; file output uses HDFS-style temporary directories and output promotion.

Configuration integration flows through `org.apache.hadoop.conf.Configuration`, `JobConf`, and `Configuration.IntegerRanges`. Reflection/class configuration is used for input/output formats, mapper/reducer/combiner/partitioner classes, comparators, compression codecs, output committers, and instrumentation classes.

Cluster RPC/protocol integration is exposed by `JobTracker` implementing `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, and `RefreshAuthorizationPolicyProtocol`; `JobClient` and task trackers consume this surface. Types referenced include `RunningJob`, `ClusterStatus`, `TaskReport`, `TaskCompletionEvent`, `TaskTrackerStatus`, `HeartbeatResponse`, `TaskAttemptID`, `TaskInProgress`, `JobInProgress`, and `QueueManager`.

Serialization and IO dependencies include `Writable`, `DataInput`, `DataOutput`, Java `IOException` subclasses, `Closeable`, `InputStream`, `Text`, `LongWritable`, `WritableComparable`, and `MapFile.Reader`. Logging uses Apache Commons Logging `Log`; progress callbacks use `Reporter` and `Progressable`.

History and diagnostic integration includes task logs, web URLs, history file names and paths, counters, split metadata, task attempt phases, debug scripts localized through `DistributedCache`, and completion callbacks through job-end notification URIs.

## Risks and Compatibility Notes

The range starts mid-way through `Counters`; the class declaration and earlier counter APIs are outside this chunk. The range also ends inside the `Mapper.map` method documentation, so the final per-file reconciliation must merge adjacent chunks for complete class/interface coverage.

Old `mapred` APIs remain compatibility-sensitive even when deprecated. Removing deprecated string-id overloads, changing return types from arrays to collections, altering `Writable` field order, or changing enum constants would break existing Hadoop 0.20-era applications and serialized metadata.

`FileInputFormat` splitting is vulnerable to off-by-one and locality regressions. Splittability, compressed inputs, zero input paths, hidden/filtered files, block boundary calculations, rack-vs-host contribution logic, and minimum split size all influence mapper parallelism and data locality.

`FileOutputFormat` and `FileOutputCommitter` carry high risk around speculative execution and failed attempts. Incorrect temporary directory naming, cleanup, or promotion can cause duplicate output, lost side-effect files, or corruption when multiple attempts for the same task run concurrently.

`JobConf` setters interact subtly. Mapper/reducer class choices, old/new API toggles, map output types, grouping comparators, speculative execution, failure thresholds, profiling ranges, memory limits, queue names, and debug scripts can affect scheduling, task launch command lines, and failure semantics. Configuration key compatibility is as important as Java signature compatibility.

`JobClient` and `JobTracker` expose distributed-system failure surfaces: filesystem staging failures, invalid job confs, jobtracker readiness, RPC timeouts, interrupted submission, tracker heartbeat races, recovery/restart state, queue lookup failures, and ACL refresh errors. Methods returning mutable legacy containers increase accidental coupling risk.

History APIs are schema-sensitive. Changes to `JobHistory.Keys`, `RecordTypes`, `Values`, compact counter strings, history filename encoding, or lifecycle logging order can break parsers, web UIs, recovery, audits, and downstream tooling that consumes history logs.

Line readers and key/value text readers must preserve byte-level separator behavior, split boundary handling, CR/LF handling, position reporting, and mutation of reusable writable objects. Unicode text is carried in `Text`, but separator search is byte-based, so multibyte input and custom separator bytes are relevant edge cases.

## Test Signals

JDiff-level validation should confirm this XML range remains well formed in the full file, preserves class/interface names, inheritance, implemented interfaces, method signatures, parameter types, checked exceptions, field names/types, deprecation text, synchronized/static/final/abstract flags, and Javadoc contracts.

Counter tests should cover `Counters` binary serialization, escaped compact round trips, group display names, missing counters returning zero, numeric-id deprecated lookup, iterator behavior, equality/hash code, and parsing failures from malformed compact strings.

File input tests should cover path setters/adders/getters, comma-separated path parsing, input path filters, empty input validation, compressed non-splittable files, custom `isSplitable`, split sizing, block index selection, host/rack locality ranking, and `FileSplit` read/write round trips including null or empty host arrays.

File output tests should cover compression flags/codecs, output path validation, existing output rejection via `FileAlreadyExistsException`, invalid job conf handling, work output path behavior with and without `FileOutputCommitter`, unique name generation for map and reduce tasks, custom file path generation, task commit/abort cleanup, and speculative attempt collision scenarios.

JobClient tests should exercise initialization against default and explicit tracker addresses, filesystem handle retrieval, job directory validation, submit from `JobConf` and job file, `RunningJob` retrieval by `JobID`, deprecated string-id paths, cluster status with and without details, task report queries by task kind, task display filters, queue inspection, `runJob`, `monitorAndPrintJob`, and CLI `run(String[])` exit codes.

JobConf tests should verify every major getter/setter pair persists expected configuration values: jar, user, local dirs, failed-task retention, working directory, JVM reuse, input/output formats, committer, compression, key/value classes, comparators, mapper/reducer/combiner/partitioner classes, speculative execution, task counts, max attempts, job name/session, failure percentages, priority, profiling, debug scripts, notification URI substitution tokens, memory limits, and queue name.

Job history tests should write and parse representative job/task/map-attempt/reduce-attempt lifecycle records, verify all enum keys and values used by log helpers, test filename/path encode/decode and recovery helpers, parse history from a test `FileSystem`, confirm listener callbacks, validate counters and splits in history records, and cover disabled history and cleaner behavior.

Job status/profile/queue/id tests should cover `Writable` read/write compatibility, old/new `JobID` downgrade and parse behavior, regex pattern generation, priority enum values, job progress fields, run-state constants, clone behavior, scheduling info, queue name, tracking URL, and username/job-file preservation.

JobTracker integration tests should cover startup state, illegal submission while initializing, heartbeat response behavior, tracker blacklist state, topology node resolution, job submission/control/query APIs, task kill semantics, task diagnostics and completion events, queue APIs, recovery flags/duration, system dir, protocol version, instrumentation class configuration, and service ACL refresh.

Record-reader tests should cover `LineRecordReader` offsets, CR/LF variants, split starts in the middle of a line, max line length behavior from configuration, progress/position reporting, close idempotence, `KeyValueLineRecordReader.findSeparator`, missing separators, custom separator bytes, empty keys or values, UTF-8 text, and reuse of caller-provided `Text` objects. `MapFileOutputFormat` tests should write map-file output, open readers, and retrieve entries through a partitioner.
