# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 18683-24886

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.0, not executable Java implementation code. It records compatibility metadata for the classic `org.apache.hadoop.mapred` API: class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, abstract/static/final/synchronized/native flags, deprecation state, and embedded Javadoc contracts.

The range starts in the tail of `org.apache.hadoop.mapred.Counters` and ends just after the opening of `org.apache.hadoop.mapred.OutputFormat`, so adjacent chunks are required for complete class-level conclusions about those two APIs. The complete APIs inside the range cover counter internals, file input/output formats and splits, job submission and configuration, job history logging/parsing, job identity/profile/status/queue models, JobTracker control/query APIs, line-based input readers, mapper execution contracts, multi-file splitting, output collection, and output commit semantics.

## Purpose and Major API Surface

`Counters`, `Counters.Counter`, and `Counters.Group` define synchronized named MapReduce counters. The visible `Counters` tail covers group/string counter increments, enum counter lookup, merging another `Counters`, static `sum`, size, writable serialization, logging, textual compact forms, escaped compact round trips via `fromEscapedCompactString`, and `toString`. `Counter` exposes synchronized binary read/write, name/display-name access, display-name mutation, escaped compact formatting, current value, and increment. `Group` exposes group names/display names, localized display names, deprecated numeric counter lookup, lookup/create by counter name, size, read/write, and iteration over counters.

`DefaultJobHistoryParser` populates a precreated `JobHistory.JobInfo` from a job history file on a `FileSystem`. `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are MapReduce validation exceptions; `InvalidInputException` retains a list of underlying `IOException` problems and formats an aggregate message.

`FileInputFormat<K,V>` is the base file-backed `InputFormat`. It provides path configuration helpers, optional `PathFilter` instantiation, `listStatus`, split computation, block-location lookup, minimum split size control, and a protected `isSplitable(FileSystem, Path)` hook for stream-compressed or whole-file inputs. Subclasses supply `getRecordReader`.

`FileOutputCommitter` implements the `OutputCommitter` lifecycle for filesystem outputs under `${mapred.output.dir}`, with `setupJob`, `cleanupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, and `abortTask`. `TEMP_DIR_NAME` identifies the temporary directory convention. `FileOutputFormat<K,V>` is the base output format, with job-output compression configuration, compressor class lookup, output-spec validation, output path/work path/task output path helpers, and unique task-scoped filename/path generation for side-effect files.

`FileSplit` and `MultiFileSplit` are `InputSplit` implementations. `FileSplit` models one byte range in one file and serializes path, start, length, and host locations; its old constructor accepting `JobConf` is deprecated in favor of explicit host information. `MultiFileSplit` models whole-file collections, exposes per-file paths and lengths, computes total length, returns host locations, serializes with `Writable`, and formats itself with `toString`.

`ID` is the writable/comparable integer identity base with `getId`, `toString`, `hashCode`, `equals`, `compareTo`, binary read/write, static `read`, static `forName`, and protected `id` field. `JobID` extends it with a JobTracker identifier, parsing/pattern helpers, compare/equality/hash behavior, and binary read/write.

`InputFormat<K,V>` and `InputSplit` are the core input contracts. `InputFormat.getSplits(JobConf,int)` divides work, and `getRecordReader(InputSplit, JobConf, Reporter)` creates a reader for one split. `InputSplit.getLength()` reports byte length for scheduling and `getLocations()` reports locality hosts.

`JobClient` is the user-facing JobTracker client and implements `Tool`. It can construct against default or explicit JobTracker settings, initialize/close client resources, expose the staging `FileSystem`, submit jobs from a config file or `JobConf`, validate job directories for recovery, fetch `RunningJob` handles, task reports, cluster status, job lists, default map/reduce capacity, system directory, queue information, and run jobs synchronously through static `runJob`. Deprecated string-job-id overloads remain beside `JobID` overloads. `TaskStatusFilter` is the task-output filtering enum.

`JobConf` extends `Configuration` and is the central mutable MapReduce job description. This chunk covers constructors, jar selection, local directories and job-local scratch paths, user and working-directory settings, failed-task file retention, task JVM reuse, input/output format and output committer classes, map-output and job-output compression, map/final key/value classes, sort and grouping comparators, key-field comparator and partitioner options, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce task counts, max attempts and tolerated failure percentages, job name/session id/priority, profiling settings, map/reduce debug scripts, job-end notification URI, queue name, and `DEFAULT_QUEUE_NAME`.

`JobConfigurable`, `JobContext`, and `JobEndNotifier` define job-level configuration and notification hooks. `JobConfigurable.configure(JobConf)` initializes components from job configuration. `JobContext` exposes `JobConf` and `Progressable`. `JobEndNotifier` starts/stops the notifier and registers local or JobTracker notifications from `JobConf` plus `JobStatus`.

`JobHistory` and inner classes are the history log API. Top-level methods initialize history storage, parse history files through a listener, toggle history disablement, and derive task log URLs. `HistoryCleaner` deletes old history. `JobInfo` tracks task maps and job metadata, encodes/decodes history file names, recovers history files, and logs submitted, initialized, started, finished, failed, killed, priority, and restart/timing information. `Keys`, `RecordTypes`, and `Values` are enums for history records. `Listener` receives parsed records. `Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide event logging for task and attempt start/finish/fail/kill, including counters, tracker/http-port, state, shuffle/sort times, and task type; several older host-only overloads are deprecated.

`JobPriority`, `JobProfile`, `JobQueueInfo`, and `JobStatus` are job metadata/value objects. `JobProfile` stores user, typed and string job IDs, job file, URL, job name, queue name, and writable serialization; older string-ID constructor and `getJobId` are deprecated. `JobQueueInfo` stores queue name and scheduling info with writable serialization. `JobStatus` stores setup/map/reduce/cleanup progress, run state, start time, user, scheduling info, priority, clone support, synchronized accessors/mutators, writable serialization, and integer states `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`; its `getJobId` string accessor is deprecated.

`JobTracker` is the central MapReduce service API and implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. The public surface includes tracker startup/shutdown, protocol versioning, restart/recovery status, instrumentation class configuration, address resolution, the long-running `offerService`, submission counts, tracker host/ports/start time, running/failed/completed jobs, task tracker status, network topology resolution, cache levels, listeners, queue manager access, build/filesystem information, synchronized heartbeat handling, adaptive heartbeat intervals, task tracker error reports, job-id allocation, job submission, cluster status, kill/priority operations, job profiles/status/counters/task reports/completion events/diagnostics, task killing and assigned tracker lookup, system directory/local job file paths, queues, and a debug-oriented `main`. `JobTracker.IllegalStateException` reports submit-before-ready, and `JobTracker.State` is the service state enum.

`KeyValueLineRecordReader`, `KeyValueTextInputFormat`, `LineRecordReader`, and deprecated `LineRecordReader.LineReader` cover line-oriented text input. `KeyValueLineRecordReader` splits each line at a configurable separator byte, emits `Text` key/value pairs, and exposes synchronized `next`, `getPos`, and `close`. `KeyValueTextInputFormat` configures splitability and record readers for text key/value files. `LineRecordReader` emits `LongWritable` file offsets and `Text` lines from a split or stream. Its nested `LineReader` is deprecated in favor of `org.apache.hadoop.util.LineReader`.

`MapFileOutputFormat` writes `MapFile` outputs and can open generated readers or fetch an entry using a `Partitioner`. `Mapper`, `MapRunnable`, `MapRunner`, `MapReduceBase`, and `OutputCollector` define classic map execution. `Mapper.map` transforms one input pair into zero or more intermediate pairs, using `Reporter` for progress/status/counters. `MapRunnable.run` owns the full record-reading loop for advanced mapper behavior; `MapRunner` is the default runner. `MapReduceBase` supplies no-op `configure` and `close`. `OutputCollector.collect` emits mapper/reducer outputs.

`MultiFileInputFormat` creates nearly equal-length `MultiFileSplit`s from input files while leaving split readers to subclasses. `OutputCommitter` is the abstract job/task output commit protocol. It defines job setup/cleanup, task setup, `needsTaskCommit`, `commitTask`, and `abortTask`, and documents that commit promotes task temporary output to the final job output location. The range ends at the start of `OutputFormat`, showing only the beginning of `getRecordWriter`.

## Control Flow and Behavioral Contracts

The XML has no method bodies, but the public contracts imply the classic MapReduce control flow. A user constructs and mutates `JobConf`, selecting input/output formats, mapper/reducer/combiner/partitioner classes, comparators, compression, speculative execution, attempts, failure tolerance, debug scripts, profile settings, queue, and notifications. `JobClient.submitJob` validates input/output specs, computes `InputSplit`s, stages the jar/configuration into the MapReduce system directory, submits to `JobTracker`, and returns a `RunningJob`; `JobClient.runJob` then polls until completion.

File input flow starts with `FileInputFormat` static input path configuration. At submission or task setup time the format lists statuses, applies optional path filters, validates non-empty inputs, computes target split sizes from goal/min/block size, maps offsets to block locations for locality, and emits `InputSplit`s. A task passes each split to `getRecordReader`, and readers such as `LineRecordReader` or `KeyValueLineRecordReader` repeatedly fill caller-supplied key/value objects until `next` returns false.

Map execution flow is `MapRunner` by default: configure the mapper from `JobConf`, read key/value pairs from `RecordReader`, call `Mapper.map` for each record, emit outputs through `OutputCollector`, and use `Reporter` to keep the task alive, set status, and update counters. Custom `MapRunnable` implementations can replace that loop for advanced behavior such as asynchronous or multithreaded mapping.

Output flow has a two-stage commit contract. `OutputFormat.checkOutputSpecs` validates the configured output path before execution. `OutputCommitter.setupJob` prepares job output, `setupTask` prepares a task attempt, task code writes under the work output directory when using `FileOutputCommitter`, `needsTaskCommit` avoids unnecessary commits, `commitTask` promotes successful attempt output, and `abortTask` discards failed or killed attempt output. `cleanupJob` removes temporary job output after completion.

JobTracker flow is RPC/service oriented. TaskTrackers periodically call synchronized `heartbeat` with status and response ids; the JobTracker processes progress and returns launch/kill/reset instructions. Clients obtain new job IDs, submit jobs, query cluster/job/task state, fetch completion events and diagnostics, kill jobs or tasks, change priority, and query queues. Recovery APIs expose whether the JobTracker restarted, whether recovery completed, and how long it took.

History flow is append-and-parse. `JobHistory.init` sets up history files, `JobInfo.logSubmitted` creates a per-job history file and can disable future history when creation fails, subsequent job/task/attempt log methods append structured records, and final job/task methods close the job history file or mark terminal state. `parseHistoryFromFS` streams each parsed record to a `Listener`, while `DefaultJobHistoryParser` builds an object model in `JobInfo`.

Counter flow is synchronized mutable aggregation. Tasks and jobs increment counters by enum or string group/name, groups create counters on demand, `incrAllCounters` and `sum` merge counter sets, counters serialize through `Writable`, and escaped compact strings round-trip through parser/formatter APIs for history/log transport.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime persistence described by this chunk includes `Writable` binary formats for counters, counter groups, file splits, multi-file splits, IDs, job IDs, job profiles, queue info, and job status. Compatibility depends on stable field order, type names, string escaping, enum names, counter names/display names, and synchronized read/write symmetry.

`JobConf` is the largest mutable state holder in the chunk. It persists job behavior through configuration keys for jars, local dirs, user, working directory, format classes, committer class, codec classes, key/value classes, comparators, mapper/reducer/combiner/partitioner, speculative execution, task counts, retry/failure thresholds, priority, profiling, debug scripts, notifications, scratch directories, and queues. Some settings are admin-final configuration parameters and may not be alterable by applications.

Filesystem side effects are central. `FileInputFormat` lists input paths and block locations. `FileOutputFormat` checks output existence, creates task output paths, and exposes work output directories. `FileOutputCommitter` creates/removes temporary directories and promotes task outputs to final output. `JobClient` stages jar/configuration files into the system directory. `JobTracker` stores local job conf files and manages job state. `JobHistory` writes master and per-job history files and `HistoryCleaner` deletes old history.

Operational state includes live JobTracker service state, heartbeat response ids, job/task/attempt objects, task tracker topology and cache locality, listeners, queues, instrumentation, cluster status, progress values, counters, task reports, diagnostics, completion events, and notification registrations.

Line readers and record readers hold stream offsets, split boundaries, separators, current position, and open input streams. Their synchronized `next`, `getPos`, and `close` methods indicate mutable reader state that must not be concurrently advanced without coordination.

External side effects include job-end notification URIs, debug scripts distributed through `DistributedCache` and executed on failed tasks with stdout/stderr/syslog/jobconf arguments, profiler JVM arguments writing profile output into user logs, and `JobShell`/`IsolationRunner` command-line entry points for running jobs or isolated tasks.

## Dependencies and Integration Points

The covered APIs integrate with Hadoop filesystem types (`FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`), serialization types (`Writable`, `WritableComparable`, `RawComparator`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`), compression (`CompressionCodec`), configuration (`Configuration`, `JobConf`, integer ranges), progress (`Progressable`, `Reporter`), and distributed cache/debug facilities.

Classic MapReduce integration points include `InputFormat`, `InputSplit`, `RecordReader`, `Mapper`, `MapRunnable`, `OutputCollector`, `Partitioner`, `Reducer`, `OutputFormat`, `RecordWriter`, `OutputCommitter`, `JobContext`, `TaskAttemptContext`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, and queue/job status models.

JobTracker APIs integrate across RPC protocols (`InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`), task trackers, topology nodes (`org.apache.hadoop.net.Node`), queue management, instrumentation, cluster status, recovery, and build/version information. JobClient integrates user applications with those protocols and with the `Tool` command-line contract.

History APIs integrate with `FileSystem`, counters, job/task/attempt IDs, task log URLs, plain-text key/value history file formats, URL encoding/decoding of file names, and listener-based parsing for web UIs or offline tools.

Compatibility tooling depends on exact XML signatures and attributes. Public/protected additions, removals, type changes, generic signature changes, exception list changes, synchronization flag changes, deprecation text changes, and Javadoc contract changes are meaningful JDiff signals for Hadoop 0.19.0.

## Risks and Compatibility Notes

This chunk is partial at both ends. It should not be used alone to summarize all of `Counters` or all of `OutputFormat`.

Several APIs expose legacy Hadoop `mapred` contracts and intentionally retain deprecated overloads. Removing string-job-id methods, the old `FileSplit(JobConf)` constructor, old history logging overloads, `JobProfile.getJobId`, `JobStatus.getJobId`, or nested `LineRecordReader.LineReader` would break source compatibility for older applications even when newer replacements exist.

Serialization compatibility is high risk. Counter, split, ID, profile, queue, and status binary formats are used across task/job RPC, history, and persisted staging data. Changing read/write order, string encodings, enum names, ID parsing, or counter escaped compact formats can break old jobs, history parsers, or clients.

File output commit behavior is correctness-critical under speculative execution. The docs require attempt-specific temporary output under `_temporary/_${taskid}` so simultaneous attempts do not clobber each other. Writers that bypass `getWorkOutputPath`, use non-unique side-effect paths, or promote failed attempt output can corrupt final job output.

Input splitting affects correctness, locality, and parallelism. Incorrect `isSplitable` decisions can split non-splittable compressed streams or whole-file formats; wrong split-size/block-index logic can miss bytes, duplicate bytes, or reduce data locality. `MultiFileSplit` changes the atomic split unit from byte range to whole file, which record readers must honor.

JobConf settings interact in subtle ways. Map-output classes can differ from final output classes, grouping comparators can differ from sort comparators, combiner behavior must be compatible with reducer semantics, and `setNumMapTasks` is advisory through split generation. Admin-final parameters may reject application overrides.

JobTracker APIs expose synchronized and unsynchronized state access. The XML marks key mutating/query methods synchronized (`heartbeat`, job submission, kill/priority, task reports, counters, diagnostics), but many collection-returning methods are not synchronized. Callers and maintainers should treat returned vectors/lists/status objects as snapshots or shared mutable state depending on implementation.

History files have explicit format evolution. Version 0 used quoted values, while Version 1 changes delimiter and escapes values. Parsers and loggers must preserve escaping, record types, keys, and terminal close behavior so web/history tools can parse both older and newer logs.

Notifications, debug scripts, and profiling run at operational boundaries. URI substitution for `$jobId`/`$jobStatus`, distributed-cache symlink requirements, child JVM profiler arguments, and failed-task script execution all have security, quoting, and failure-propagation risks.

## Test Signals

JDiff validation should confirm this XML remains well-formed and preserves all public/protected class/interface boundaries in the line range, including partial `Counters` and partial `OutputFormat`. Compatibility checks should compare constructors, methods, fields, generic type strings, declared exceptions, visibility, static/final/abstract/synchronized flags, implemented interfaces, inheritance, and deprecation text.

Counter tests should cover enum and string counter creation, group display names, deprecated numeric lookup, increment and merge behavior, `sum`, synchronized read/write round trips, `size`, iterator contents, `makeCompactString`, escaped compact string round trips including separator escaping, logging, and parse failures.

File input tests should cover input path set/add/get helpers, comma-separated paths, path filters, missing/empty inputs and aggregated invalid input errors, subclass `listStatus`, split-size calculation, block-location index lookup, splitability for compressed and non-compressed files, and `RecordReader` creation for concrete formats.

File output and commit tests should cover output compression flags and codec class lookup, missing output paths, existing output path rejection through `FileAlreadyExistsException`, invalid job conf failures, `getWorkOutputPath`, `getTaskOutputPath`, unique custom filenames, speculative attempt side-effect files, `setupJob`, `setupTask`, `needsTaskCommit`, `commitTask`, `abortTask`, and `cleanupJob`.

Split and ID tests should round-trip `FileSplit`, `MultiFileSplit`, `ID`, and `JobID` through `DataOutput`/`DataInput`; verify file path/start/length/locations, multi-file path/length arrays and total length, host locality, string parsing through `forName`, compare/equality/hash behavior, and job ID pattern generation.

JobClient and JobTracker tests should use controlled or mocked protocols to cover initialization/close, filesystem handle acquisition, job submission from file and `JobConf`, job directory validation for recovery, `RunningJob` lookup, task reports for map/reduce/setup/cleanup, cluster status, job listing, synchronous `runJob` polling, task output filters, system directory, queues, job priority changes, kill job/task, diagnostics, completion events, heartbeat response handling, adaptive heartbeat interval calculation, restart/recovery state, queue manager access, and submit-before-ready errors.

JobConf tests should verify every covered setter/getter pair and default: jar and jar-by-class detection, local dir cleanup/path selection, user and working directory, failed-task file retention and patterns, tasks per JVM including `-1`, default input/output format and committer classes, map/job compression codec classes, map and final key/value classes, raw comparators, key-field comparator/partitioner option strings, mapper/map runner/partitioner/reducer/combiner classes, speculative execution flags, task counts, attempts, failure percentages, job name/session/priority, profile ranges and params, debug scripts, job-end notification URI substitution, job-local dir, and queue name default.

History tests should cover initialization success/failure, disabling history, listener parsing, `DefaultJobHistoryParser` object population, task log URL construction with missing fields, history cleaner retention, filename/path encode/decode, history file recovery choosing the oldest duplicate, all job/task/map-attempt/reduce-attempt log event methods including deprecated overload compatibility, counters in finished events, shuffle/sort times, task type values, escaped values, and Version 0/Version 1 parsing.

Text input and mapper tests should cover line boundary handling, split starts that begin mid-line, progress and position reporting, close idempotence, configurable key/value separator bytes, missing separator producing empty value, compressed splitability in `KeyValueTextInputFormat`, default `MapRunner` invoking mapper for all records, no-op `MapReduceBase`, custom `MapRunnable`, reporter progress/status/counters, output collection, and map-only jobs with zero reducers.

MapFile and multi-file tests should cover `MapFileOutputFormat` writer creation, opening partition readers, `getEntry` partition selection, `MultiFileInputFormat` nearly equal-length split construction, empty and many-small-file inputs, `MultiFileSplit` serialization, and record readers that treat each path as an atomic file.
