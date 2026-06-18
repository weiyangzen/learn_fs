# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 18690-24884

## Scope and Purpose

This chunk is a JDiff API descriptor for Hadoop 0.19.2, covering a large section of the old `org.apache.hadoop.mapred` public API. It is documentation and signature metadata rather than executable Java source. The API surface described here centers on MapReduce job configuration, submission, job tracking, counters, input/output formats, job history, record readers, mapper execution, and split abstractions.

The chunk starts inside the tail of `ClusterStatus`, fully covers many `mapred` classes from `Counters` through `MultiFileInputFormat`, and ends partway through `MultiFileSplit`. Any whole-file synthesis should merge this with adjacent chunks for complete class boundaries.

## Important APIs, Types, and Functions

### Cluster and Counters

- `ClusterStatus` tail: exposes writable serialization via `write(DataOutput)` and `readFields(DataInput)`, plus cluster state inspection such as `getJobTrackerState()`. Its documented role is client-visible status for cluster size, map/reduce capacity, running tasks, and `JobTracker` state, normally queried through `JobClient.getClusterStatus()`.
- `Counters`: a synchronized `Writable` and `Iterable<Counters.Group>` container for global MapReduce counters. Important methods include `getGroupNames()`, `getGroup(String)`, `findCounter(Enum)`, `findCounter(String,String)`, deprecated `findCounter(String,int,String)`, `incrCounter(...)`, `getCounter(Enum)`, `incrAllCounters(Counters)`, `sum(Counters,Counters)`, `size()`, `write/readFields`, `log(Log)`, `toString()`, `makeCompactString()`, `makeEscapedCompactString()`, and `fromEscapedCompactString(String)`.
- `Counters.Counter`: synchronized writable counter record with internal name, display name, mutable value, `increment(long)`, and compact escaped string rendering.
- `Counters.Group`: writable iterable grouping counters by enum class or raw group name, with display-name localization hooks, `getCounter(String)`, deprecated numeric-id lookup, `getCounterForName(String)`, `size()`, serialization, and iteration.

### Input and Output Contracts

- `InputFormat<K,V>`: defines `getSplits(JobConf,int)` and `getRecordReader(InputSplit,JobConf,Reporter)`. The docs describe logical splits, assignment to mappers, and the `RecordReader` responsibility to preserve record boundaries.
- `InputSplit`: `Writable` interface with `getLength()` and `getLocations()`, representing a byte-oriented slice passed to a mapper.
- `FileInputFormat<K,V>`: abstract base for file-backed inputs. It provides path configuration (`setInputPaths`, `addInputPaths`, `addInputPath`, `getInputPaths`), optional `PathFilter`, `listStatus(JobConf)`, default split generation (`getSplits`), split sizing (`computeSplitSize`), block locality lookup (`getBlockIndex`), and overridable `isSplitable(FileSystem,Path)`.
- `FileSplit`: concrete `InputSplit` for one file region with path, start offset, length, host locations, serialization, and string conversion. The constructor taking `JobConf` is deprecated in favor of the host-array constructor.
- `MultiFileInputFormat<K,V>`: abstract file format that returns `MultiFileSplit` instances and attempts to construct splits of nearly equal content length from files under the configured input paths.
- `MultiFileSplit` partial: writable split containing arrays of `Path` and lengths, total length, per-index accessors, path count, locations, serialization, and `toString()`; this chunk cuts off before the class closes.
- `FileOutputFormat<K,V>`: abstract base for file-backed outputs. It controls output compression (`setCompressOutput`, `getCompressOutput`, compressor class setters/getters), output path, output spec validation, task temporary output paths, unique task-scoped names, and custom-file paths.
- `FileOutputCommitter`: concrete `OutputCommitter` for committing files under `${mapred.output.dir}` using a temporary directory name. It exposes job/task setup, cleanup, commit, abort, and `needsTaskCommit`.
- `MapFileOutputFormat`: `FileOutputFormat` producing `MapFile` output, with helpers to open generated readers and retrieve an entry through a `Partitioner`.

### Job Submission, Configuration, and Status

- `JobClient`: client-side interface to the `JobTracker`. It can initialize/close a tracker connection, get a `FileSystem`, submit jobs from a job file or `JobConf`, validate a job directory, retrieve `RunningJob` handles, get task reports, cluster status, all jobs or incomplete jobs, run a job synchronously, configure task output filtering, query default map/reduce capacities, system directory, queues, jobs in queues, and queue info. Deprecated string-based job ID overloads are preserved but point users toward `JobID`.
- `JobConf`: central `Configuration` subclass for describing old MapReduce jobs. It has constructors from defaults, classes, existing configs, XML paths, and load-defaults flag. It configures job jar, local dirs, reported user, keep-failed-task-file behavior, working directory, tasks per JVM, input/output format, output committer, compression, key/value classes, comparators, key-field comparator/partitioner options, mapper, map runner, partitioner, reducer, combiner, speculative execution, map/reduce counts, max attempts, tolerated failure percentages, priority, profiling, debug scripts, end-notification URI, job-local scratch directory, and queue name.
- `JobStatus`: writable/cloneable current status view with job ID, setup/map/reduce/cleanup progress, run state, start time, username, scheduling info, priority, completion check, and state constants `RUNNING`, `SUCCEEDED`, `FAILED`, `PREP`, and `KILLED`.
- `JobProfile`: writable metadata for a job, including user, typed `JobID`, job configuration file path, web UI URL, job name, and queue name. Deprecated string job-id access remains.
- `JobQueueInfo`: writable queue metadata with queue name and scheduling information, defaulting missing scheduling information to `"N/A"`.
- `JobPriority`: enum for job priority.
- `JobShell`: `Tool` wrapper for command-line job submission, including `-libjars`, `-archives`, `-files`, input jar, and arguments.
- `JobConfigurable`: interface for objects initialized from a `JobConf`.
- `JobContext`: exposes `JobConf` and a progress mechanism for committers and related job/task context code.

### Job Tracker and Runtime Coordination

- `JobTracker`: central service for submitting and tracking MapReduce jobs. It implements `MRConstants`, `InterTrackerProtocol`, `JobSubmissionProtocol`, and `TaskTrackerManager`. Public API includes `startTracker(JobConf)`, `stopTracker()`, protocol versioning, restart/recovery status and duration, instrumentation class configuration, tracker address, `offerService()` main loop, tracker identity/ports/start time, running/failed/completed jobs, task tracker collection and lookup, topology resolution, listener registration, queue manager, build version, synchronized `heartbeat(...)`, heartbeat interval calculation, filesystem name, task tracker error reporting, job ID allocation, job submission, cluster status, job kill/priority operations, job profile/status/counters, task reports, completion events, diagnostics, TIP lookup, task kill, assigned tracker lookup, all/incomplete jobs, system dir, localized job file path, queue APIs, and `main`.
- `JobTracker.IllegalStateException`: `IOException` for clients submitting before the tracker is ready.
- `JobTracker.State`: enum representing tracker state.
- `IsolationRunner`: command-line utility for running a single task from a task directory, useful for debugging isolated task execution.
- `JobEndNotifier`: static lifecycle and dispatch API for job completion notifications, including `startNotifier`, `stopNotifier`, `registerNotification(JobConf,JobStatus)`, and `localRunnerNotification`.

### Job History

- `JobHistory`: append-mode history facility with initialization, filesystem parsing through a listener, enable/disable flag, and task-log URL lookup. The documentation describes plain-text line records with record type plus key/value pairs, a master index of jobs, per-job history files named from jobtracker ID and job ID, and versioned escaping semantics.
- `DefaultJobHistoryParser`: parses a job history file from a `FileSystem` into a `JobHistory.JobInfo` object.
- `JobHistory.HistoryCleaner`: `Runnable` deleting history older than one month, updating the master index, and pruning jobtracker references with no recent jobs.
- `JobHistory.JobInfo`: key/value record model for job-level history and static logging helpers. It manages task maps, local/history file path discovery, URL encode/decode of history paths/names, username extraction, recovery file selection, and job lifecycle logging (`logSubmitted`, `logInited`, deprecated/modern `logStarted`, `logFinished`, `logFailed`, `logKilled`, priority and timing info).
- `JobHistory.Task`: logs task/TIP start, finish, failure, failed-due-to-attempt, and exposes task attempts.
- `JobHistory.TaskAttempt`: base class for map/reduce attempts.
- `JobHistory.MapAttempt` and `ReduceAttempt`: static helpers for start/finish/failure/kill events. Modern overloads add tracker name, HTTP port, task type, state string, counters, and for reduces shuffle/sort finish times. Older overloads using only host names are deprecated.
- `JobHistory.Keys`, `RecordTypes`, and `Values`: enums defining global namespaces for history keys, line record types, and common string values.
- `JobHistory.Listener`: callback API `handle(RecordTypes, Map<Keys,String>)` invoked by history parsing.

### Record Readers and Mapper Execution

- `LineRecordReader`: `RecordReader<LongWritable,Text>` treating file offsets as keys and lines as values. It supports constructors over `Configuration`/`FileSplit` or raw streams with start/end/max line length, `next`, progress, position, and close.
- `LineRecordReader.LineReader`: deprecated subclass of `org.apache.hadoop.util.LineReader`.
- `KeyValueLineRecordReader`: `RecordReader<Text,Text>` reading a line and splitting it into key/value by a separator byte configured with `key.value.separator.in.input.line`, default tab. It exposes `findSeparator`, key/value creation, next, progress, position, and close.
- `KeyValueTextInputFormat`: `FileInputFormat<Text,Text>` and `JobConfigurable` for text files split into lines, with key/value division by separator and empty value when the separator is absent. It can override splitability and create `KeyValueLineRecordReader`.
- `Mapper<K1,V1,K2,V2>`: application extension point that maps one input pair to zero or more intermediate pairs using `OutputCollector` and `Reporter`; it also inherits `JobConfigurable` and `Closeable`. Docs describe mapper lifecycle, one map task per input split, grouping/sorting/partitioning of intermediate output, combiners, SequenceFile-backed intermediate storage, compression, and direct filesystem output when reducers are zero.
- `MapReduceBase`: no-op base implementation of `close()` and `configure(JobConf)` for mapper/reducer implementations.
- `MapRunnable<K1,V1,K2,V2>`: expert interface for controlling map processing over a `RecordReader`, `OutputCollector`, and `Reporter`.
- `MapRunner`: default `MapRunnable` that configures and runs a mapper, with protected `getMapper()`.

### Exceptions and Identifiers

- `ID`: base writable comparable integer identifier for `JobID`, `TaskID`, and `TaskAttemptID`, with `getId`, comparison, equality, serialization, static `read`, and string parser `forName`.
- `JobID`: immutable unique job identifier with jobtracker identifier plus integer job number, typed serialization/parsing, comparison by tracker identifier then job number, and regex pattern helper for job IDs.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException`: user-facing `IOException` subclasses for output overwrite conflicts, unexpected file types, aggregated input problems, and invalid/missing job configuration attributes. `InvalidInputException` preserves a list of underlying `IOException`s and summarizes messages.

## Control Flow and State Behavior

The described MapReduce flow is: users build a `JobConf`, set input and output paths/formats, mapper/reducer/combiner/partitioner/comparator classes, optional compression/debug/profiling/notification settings, then call `JobClient.submitJob` or `JobClient.runJob`. Submission validates input/output specs, computes `InputSplit`s, prepares distributed cache accounting, copies jar/configuration to the system directory on the distributed filesystem, submits to `JobTracker`, and optionally monitors completion.

At runtime, `FileInputFormat` lists input status entries and computes logical splits using desired split count, min split size, filesystem block size, and block locations. `InputFormat` instances produce `RecordReader`s, which feed key/value records to `Mapper` through a `MapRunnable` such as `MapRunner`. Mapper output is collected, optionally combined, partitioned by `Partitioner`, sorted/grouped with configured comparators, and sent to reducers unless the reducer count is zero, in which case map output is written directly to the output filesystem.

`FileOutputFormat` separates final output path from per-task work output path. With `FileOutputCommitter`, task attempts write under `${mapred.output.dir}/_temporary/_${taskid}` and successful attempts are promoted to the final output directory, while unsuccessful attempt directories are discarded. The docs emphasize speculative execution hazards and the need for unique task-attempt names for side-effect files unless using the work output directory.

`JobTracker` owns service lifecycle, heartbeats, job submission, task assignment, cluster and queue status, task diagnostics, job killing, priority changes, and topology-aware scheduling data. `TaskTracker` instances periodically call synchronized `heartbeat(...)` with status and receive instructions to start/stop tasks/jobs or reset. Heartbeat interval scales with cluster size by adding one second for every 50 nodes.

Job history is append-oriented: job, task, map attempt, and reduce attempt helpers log lifecycle events into text records. Parsing is streaming through `JobHistory.Listener`, allowing consumers to build a model or inspect selected records without holding the full file in memory.

## Persistence and Serialization

Most runtime DTOs implement Hadoop `Writable`: `Counters`, `Counter`, `Group`, `FileSplit`, `ID`, `JobProfile`, `JobQueueInfo`, `JobStatus`, `InputSplit` implementations, and `MultiFileSplit`. The chunk documents binary read/write APIs but not byte-level implementation details.

Persistent state surfaces include:

- Job configuration XML and user jar paths in `JobConf`.
- Job submission files copied to a JobTracker system directory on the distributed filesystem.
- Task temporary output directories and final output directories in `FileOutputFormat`/`FileOutputCommitter`.
- Local scratch and localized job paths under `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/` and localized job conf file paths.
- Append-only job history files plus a master history index, with URL-encoded history filenames and recovery behavior choosing the oldest recovery file while leaving only one.
- User log/profile output directories for failed task files, debug script artifacts, task stdout/stderr/syslog/jobconf arguments, and profiling output.
- Queue, job status, counters, and split metadata serialized over RPC or stored in history/status records.

## Dependencies and Integration Points

This API section integrates with:

- Hadoop core types: `Configuration`, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `PathFilter`, `Writable`, `WritableComparable`, `RawComparator`, `Text`, `LongWritable`, `MapFile`, `SequenceFile`, `CompressionCodec`, `Progressable`, and `LineReader`.
- MapReduce protocols and services: `JobTracker`, `TaskTracker`, `InterTrackerProtocol`, `JobSubmissionProtocol`, `TaskTrackerManager`, `HeartbeatResponse`, `TaskReport`, `TaskCompletionEvent`, `TaskInProgress`, `JobInProgress`, `QueueManager`, and `JobTrackerInstrumentation`.
- User extension points: `InputFormat`, `RecordReader`, `Mapper`, `MapRunnable`, `Reducer`, `Partitioner`, `OutputFormat`, `OutputCommitter`, `RawComparator`, `PathFilter`, debug scripts, job-end notification URI handlers, and distributed cache symlinks/files.
- Logging and diagnostics: Apache Commons Logging `Log`, `JobHistory`, task logs URL generation, counters, reporter progress/status, and profiler JVM arguments.
- Network topology: `org.apache.hadoop.net.Node` for resolving task tracker hosts and cache levels.

## Risks and Edge Cases

- This chunk is metadata-only; implementation details such as exact config keys, synchronization internals, serialization encoding, and error handling are inferred only from signatures and docs.
- Many APIs are synchronized on mutable status/counter objects. Incorrect external assumptions about thread safety can cause stale reads or lock contention, especially around `Counters`, `JobStatus`, `JobClient.close`, and `JobTracker` task/job query methods.
- Deprecated string-based job ID and counter numeric-ID APIs remain, creating compatibility burden and parsing risks. Callers should prefer typed `JobID` and string counter names.
- `JobConf.setNumMapTasks` is only a hint; actual map count is controlled by `InputFormat.getSplits`. Tests and user code that assume exact map counts from this setter can be wrong.
- Reducer count zero bypasses shuffle/sort and writes mapper output directly to the filesystem, which changes output ordering, committer behavior, and failure semantics.
- Speculative execution can cause multiple task attempts to write side-effect files. The docs warn that unique names or task work output paths are necessary to avoid collisions.
- Job history writes can be disabled globally if history file creation fails during `logSubmitted`; downstream history consumers need to tolerate missing or partial history.
- Job history parsing uses string key/value records with versioned escaping. Consumers should test special characters and old delimiter formats.
- `JobEndNotifier` and debug scripts invoke external URIs/scripts and depend on distributed cache symlinks; misconfiguration can silently break job chaining or failure diagnostics.
- `KeyValueLineRecordReader` depends on a single-byte separator; multi-byte delimiters or absent separators produce different key/value boundaries than users may expect.
- Compression class lookup can throw `IllegalArgumentException` if a configured codec class is missing.
- `FileOutputFormat.checkOutputSpecs` can fail when output exists or job config is invalid; overwrite behavior must be explicit elsewhere.
- `JobTracker.main` docs say it is used for debugging and normally should run as part of the DFS Namenode process, reflecting older Hadoop deployment coupling.
- This chunk cuts off mid-`MultiFileSplit`; any final report must avoid treating the class as fully covered until the next chunk is merged.

## Test Signals

Useful verification targets derived from this API surface:

- Serialization round trips for `Counters`, `Counters.Counter`, `Counters.Group`, `FileSplit`, `ID`, `JobID`, `JobProfile`, `JobQueueInfo`, `JobStatus`, and `MultiFileSplit`.
- Counter behavior: enum and string lookup identity, missing counter default `0`, display name mutation, localization fallback, compact and escaped compact string parse/render, and aggregate `sum`.
- `FileInputFormat` split generation with normal files, unsplittable compressed files, min split sizes, block boundaries, path filters, empty input sets, comma-separated path parsing, and `getBlockIndex`.
- `FileOutputFormat` output spec checks, compression toggles, compressor class resolution failure, task work output path creation, unique task names, and custom file path generation.
- Committer tests for setup/cleanup, successful task promotion, aborted task cleanup, speculative task side-file collision avoidance, and `needsTaskCommit`.
- `JobConf` default values and setters/getters for all major job knobs: input/output formats, classes, compression, comparators, speculative execution, task counts, attempts, failure percentages, profiling, debug scripts, notification URI, local dir, and queue.
- `JobClient` integration tests around submit, run-and-poll, job lookup by typed ID, task reports, queues, cluster status, and invalid job directory validation.
- `JobTracker` service tests for startup with port zero mutating config, heartbeat response IDs, task assignment/kill/fail behavior, queue APIs, topology resolution, restart/recovery flags, and synchronized report methods.
- Job history tests for submit/init/start/finish/fail/kill records, map/reduce attempt records with counters and tracker HTTP ports, URL encoding/decoding, recovery file selection, disabled-history mode, streaming listener parsing, and old deprecated overload compatibility.
- `LineRecordReader` and `KeyValueLineRecordReader` tests for split boundary line handling, CR/LF endings, max line length, separator placement, no separator, progress/position reporting, and close behavior.
- Mapper contract tests for reporter progress/status/counters, zero/many output records, custom `MapRunnable`, combiner integration, grouping comparator vs sort comparator behavior, and reducer-none direct output.
