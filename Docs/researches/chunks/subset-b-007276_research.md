# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 18636-24770

## Chunk Scope

This chunk is a generated JDiff XML description of the public Hadoop 0.18.2 `org.apache.hadoop.mapred` API surface. It starts in the tail documentation for `JobClient`, covers most of the classic pre-YARN MapReduce client/configuration, job history, tracker, mapper/reducer, input/output, sequence-file, HTTP status, and ID/event APIs, and ends inside the `TaskID` class documentation.

Because this is JDiff XML, the source does not contain method bodies. The research below derives behavior from class signatures, method contracts, deprecation notes, and API documentation embedded in the XML.

## Purpose

The covered API surface describes the old `mapred` MapReduce programming model and its runtime integration points:

- `JobConf` is the central mutable job configuration object. It records job jar, input/output formats, mapper/reducer/partitioner classes, key/value classes, comparator classes, speculative execution, task counts, retry/failure thresholds, job priority, profiling/debug scripts, job-end notification, and localized per-job scratch directory settings.
- `JobClient`, `RunningJob`, `JobStatus`, `JobProfile`, `JobID`, `TaskID`, `TaskAttemptID`, and `TaskCompletionEvent` provide the client-side and protocol-facing model for submitting jobs, polling progress, killing jobs/tasks, reading task events, and serializing job/task identity.
- `JobTracker` is exposed as the central tracker implementation implementing `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`. Its API includes tracker lifecycle, heartbeat handling, job submission/control/status RPC endpoints, topology resolution, and cluster/job status queries.
- `JobHistory` and nested types describe append-style plain text job history persistence, parser callbacks, and log helpers for job, task, map-attempt, and reduce-attempt lifecycle events.
- `Mapper`, `Reducer`, `MapRunnable`, `MapRunner`, `MapReduceBase`, `OutputCollector`, `Reporter`, `Partitioner`, `RecordReader`, `RecordWriter`, `OutputFormat`, and `JobConfigurable` are the core user extension contracts for old-style MapReduce jobs.
- `LineRecordReader`, `KeyValueLineRecordReader`, `KeyValueTextInputFormat`, `MultiFileInputFormat`, `MultiFileSplit`, `MapFileOutputFormat`, `SequenceFile*` formats/readers, and `OutputLogFilter` are concrete input/output helpers for text, key-value text, multi-file splits, map files, sequence files, and output directory filtering.
- `StatusHttpServer` and nested servlets expose the tracker-side HTTP status surface and diagnostics/graph endpoints.

## Important APIs and Types

### Job configuration and lifecycle

- `JobClient.TaskStatusFilter` is an enum-like nested type with generated `values()` and `valueOf(String)` methods. The chunk starts immediately after `JobClient` docs explaining job completion/chaining options: blocking `runJob(JobConf)`, asynchronous `submitJob(JobConf)` returning `RunningJob`, and asynchronous job-end notifications via `JobConf#setJobEndNotificationURI(String)`.
- `JobConf extends Configuration` is the largest type in this range. Constructors accept no arguments, an example class for jar discovery, a parent `Configuration`, `(Configuration, Class)`, a config file path `String`, or a config `Path`.
- `JobConf` core class/job settings include `getJar`, `setJar`, `setJarByClass`, `getUser`, `setUser`, `getJobName`, `setJobName`, `getSessionId`, `setSessionId`, `getJobPriority`, and `setJobPriority`.
- File/path and local storage helpers include deprecated `getSystemDir`, `getLocalDirs`, `deleteLocalFiles`, `getLocalPath`, deprecated `setInputPath`, `addInputPath`, `getInputPaths`, `setWorkingDirectory`, `getWorkingDirectory`, deprecated `getOutputPath`, deprecated `setOutputPath`, and `getJobLocalDir`.
- Format/class settings include `getInputFormat`, `setInputFormat`, `getOutputFormat`, `setOutputFormat`, `getMapperClass`, `setMapperClass`, `getMapRunnerClass`, `setMapRunnerClass`, `getPartitionerClass`, `setPartitionerClass`, `getReducerClass`, `setReducerClass`, `getCombinerClass`, and `setCombinerClass`.
- Key/value and comparator settings include `getMapOutputKeyClass`, `setMapOutputKeyClass`, `getMapOutputValueClass`, `setMapOutputValueClass`, `getOutputKeyClass`, `setOutputKeyClass`, `getOutputValueClass`, `setOutputValueClass`, `getOutputKeyComparator`, `setOutputKeyComparatorClass`, `getOutputValueGroupingComparator`, and `setOutputValueGroupingComparator`.
- Compression settings include `setCompressMapOutput`, `getCompressMapOutput`, deprecated `setMapOutputCompressionType`, deprecated `getMapOutputCompressionType`, `setMapOutputCompressorClass`, and `getMapOutputCompressorClass`.
- Scheduling/failure/profiling/debug settings include `setCombineOnceOnly` and `getCombineOnceOnly`, speculative execution toggles for whole job/map/reduce, `getNumMapTasks` and `setNumMapTasks`, `getNumReduceTasks` and `setNumReduceTasks`, max map/reduce attempts, max task failures per tracker, max map/reduce task failure percentages, profiling enable/params/range accessors, map/reduce debug script accessors, and job-end notification URI accessors.
- `JobConfigurable` is the configuration callback contract with `configure(JobConf)`.
- `JobEndNotifier` exposes static lifecycle and notification APIs: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification(JobConf, JobStatus)`.

### Job history

- `JobHistory` is a static-style utility with `init(JobConf, String)`, `parseHistoryFromFS(String, Listener, FileSystem)`, `isDisableHistory`, `setDisableHistory`, and `JOBTRACKER_START_TIME`.
- `JobHistory.HistoryCleaner implements Runnable` cleans old history data, removing jobs older than one month and stale job tracker references.
- `JobHistory.JobInfo extends JobHistory.KeyValuePair` provides `getAllTasks`, local job-file path helpers, URL encode/decode helpers for job history paths/names, and `logSubmitted`, `logStarted`, `logFinished`, and `logFailed` overloads for string IDs and typed `JobID`.
- `JobHistory.Listener` is a parser callback: `handle(RecordTypes, Map<Keys,String>)`.
- `JobHistory.Keys`, `RecordTypes`, and `Values` are enum-like namespaces used in persisted history lines.
- `JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` provide event-specific static log methods. Task logs capture task start/finish/failure and attempts. Map attempt logs capture start/finish/failure/kill with host and error. Reduce attempt finish additionally captures shuffle-finished and sort-finished timestamps.

### Job identity, profile, and status

- `JobID extends ID` models immutable job identity from job tracker identifier plus job number. It supports `equals`, `compareTo`, `toString`, `hashCode`, `readFields`, `write`, static `read(DataInput)`, `forName(String)`, and `getJobIDsPattern(String,Integer)` for regex generation.
- `JobPriority` is an enum-like job priority type.
- `JobProfile implements Writable` carries user, job ID, job file, tracking URL, and job name. It has constructors for typed `JobID` and legacy string IDs, plus `write`/`readFields`.
- `JobStatus implements Writable` carries job ID, map/reduce progress, run state, start time, and username. Constants include `RUNNING`, `SUCCEEDED`, `FAILED`, and `PREP`.
- `RunningJob` is the client-facing handle for live jobs. It exposes job identity/profile fields, `mapProgress`, `reduceProgress`, non-blocking `isComplete`, `isSuccessful`, blocking `waitForCompletion`, `killJob`, task completion event paging, typed and deprecated string `killTask`, and `getCounters`.

### Job tracker and protocols

- `JobTracker` implements `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`.
- Lifecycle and service methods include static `startTracker(JobConf)`, `stopTracker`, `offerService`, `main`, `getProtocolVersion`, and `getAddress`.
- Cluster/tracker state methods include `getTotalSubmissions`, `getJobTrackerMachine`, `getTrackerIdentifier`, `getTrackerPort`, `getInfoPort`, `getStartTime`, `runningJobs`, `getRunningJobs`, `failedJobs`, `completedJobs`, `taskTrackers`, `getTaskTracker`, `getClusterStatus`, `jobsToComplete`, and `getAllJobs`.
- Topology and locality methods include `resolveAndAddToTopology`, `getNodesAtMaxLevel`, `getParentNode`, `getNode`, `getNumTaskCacheLevels`, and `getNumResolvedTaskTrackers`.
- Runtime RPC endpoints include `heartbeat(TaskTrackerStatus, boolean, boolean, short)`, `reportTaskTrackerError`, `getNewJobId`, overloaded `submitJob`, overloaded `killJob`, overloaded `getJobProfile`, overloaded `getJobStatus`, overloaded `getJobCounters`, map/reduce task report accessors, task completion event accessors, task diagnostic accessors, `getTip`, typed and string `killTask`, assigned tracker lookup, system directory lookup, overloaded `getJob`, and local job file path helpers.
- `JobTracker.IllegalStateException extends IOException` is a tracker-specific checked error. `JobTracker.State` is an enum-like tracker state.

### Core MapReduce user contracts

- `Mapper<K1,V1,K2,V2>` maps each input key/value to zero or more intermediate pairs via `map(K1,V1,OutputCollector<K2,V2>,Reporter)`. It extends `JobConfigurable` and `Closeable`. The docs emphasize that reporters must be used for long-running processing to avoid task timeout and that intermediate output is grouped, partitioned, optionally combined, and stored as `SequenceFile`s.
- `Reducer<K2,V2,K3,V3>` reduces grouped intermediate values via `reduce(K2, Iterator<V2>, OutputCollector<K3,V3>, Reporter)`. The documented flow is shuffle, sort/group, then reduce. It warns that key/value objects passed to reduce are reused and must be cloned if retained.
- `MapRunnable<K1,V1,K2,V2>` is an expert mapper driver abstraction. `MapRunner` is the default implementation that reads from a `RecordReader` and invokes a configured mapper.
- `MapReduceBase` provides no-op `configure(JobConf)` and `close()` for mapper/reducer subclasses.
- `OutputCollector<K,V>` abstracts collection of mapper intermediate output and reducer final output through `collect(K,V)`.
- `Reporter extends Progressable` provides task status, enum and string-group counter increments, current input split for mappers, and a `Reporter.NULL` no-op instance.
- `Partitioner<K2,V2>` maps intermediate key/value pairs to reducer partition numbers through `getPartition(K2,V2,int)`.
- `RecordReader<K,V>` converts an `InputSplit` into key/value records with `next`, `createKey`, `createValue`, `getPos`, `close`, and `getProgress`.
- `RecordWriter<K,V>` writes final key/value pairs with `write` and `close(Reporter)`.
- `OutputFormat<K,V>` validates output specs and creates `RecordWriter`s. `OutputFormatBase` is a deprecated abstract base superseded by `FileOutputFormat`; it still carries static compression helpers and default output spec validation.

### Text, map-file, multi-file, and sequence-file I/O

- `KeyValueLineRecordReader` reads text lines into `Text` key/value pairs using a separator located by `findSeparator`; it implements `RecordReader<Text,Text>`.
- `KeyValueTextInputFormat extends FileInputFormat<Text,Text>` and implements `JobConfigurable`; it configures separator behavior, declares splitability, and returns a key-value line reader.
- `LineRecordReader` reads line-oriented records as byte-position `LongWritable` keys and `Text` values. Constructors accept `Configuration + FileSplit` or explicit streams/start/end/max line length. Nested `LineReader` has `readLine` overloads and `close`.
- `MapFileOutputFormat extends FileOutputFormat<WritableComparable,Writable>` writes `MapFile`s and has static helpers `getReaders(FileSystem,Path,Configuration)` and `getEntry(MapFile.Reader[], Partitioner, key, value)`.
- `MultiFileInputFormat<K,V>` groups files into `MultiFileSplit`s via `getSplits` and leaves `getRecordReader` abstract/concrete to subclasses depending on implementation. `MultiFileSplit` implements `InputSplit` over arrays of `Path` and lengths, with aggregate length, path accessors, locations, serialization, and string conversion.
- `OutputLogFilter implements PathFilter` rejects output directory paths containing `_logs`.
- `SequenceFileInputFormat<K,V>` lists input paths and returns `SequenceFileRecordReader`.
- `SequenceFileRecordReader<K,V>` reads typed `SequenceFile` records and exposes key/value classes, key/value creation, two `next` overloads, current value retrieval, progress, position, seek, close, and a protected/public `conf` field in the JDiff output.
- `SequenceFileOutputFormat<K,V>` creates sequence-file writers, static readers for output directories, and static compression type configuration helpers.
- `SequenceFileAsBinaryInputFormat` and nested `SequenceFileAsBinaryRecordReader` read sequence-file keys and values as raw `BytesWritable` byte streams. The reader exposes original key/value class names and synchronized `next`.
- `SequenceFileAsBinaryOutputFormat` writes binary raw `BytesWritable` records while allowing configured logical key/value classes distinct from actual `BytesWritable`. Its protected nested `WritableValueBytes` implements `SequenceFile.ValueBytes` for `appendRaw`.
- `SequenceFileAsTextInputFormat` and `SequenceFileAsTextRecordReader` convert sequence-file keys and values to their `String` forms and emit `Text`.
- `SequenceFileInputFilter<K,V>` samples/filter sequence-file records. `setFilterClass(Configuration, Class)` chooses the filter, and nested `Filter` accepts/rejects by key. Built-in filters include `FilterBase`, `MD5Filter`, `PercentFilter`, and `RegexFilter`, each configured from `Configuration` with frequency or regex pattern state.

### HTTP status and task events/IDs

- `StatusHttpServer` wraps server setup for MapReduce status pages. It exposes attributes, servlet registration, port query, thread limits, SSL listener addition, start, and stop. Nested `StackServlet` and `TaskGraphServlet` extend `HttpServlet`; `TaskGraphServlet` has fixed drawing layout fields such as width, height, and margins.
- `TaskAttemptID extends ID` identifies one attempt for a `TaskID`. Constructors accept `(TaskID,int)` or raw `(jtIdentifier, jobId, isMap, taskId, attemptId)`. It exposes job/task accessors, `isMap`, equality/comparison/string/hash, Writable serialization, static read, `forName`, and regex pattern generation via `getTaskAttemptIDsPattern`.
- `TaskCompletionEvent implements Writable` captures event ID, task attempt ID, task status, map/reduce flag, task runtime, and task tracker HTTP location. It keeps deprecated string task ID accessors alongside typed `TaskAttemptID` accessors and has `EMPTY_ARRAY`.
- `TaskCompletionEvent.Status` is an enum-like status type.
- `TaskID extends ID` begins in this chunk and is incomplete at the chunk boundary. Covered members include constructors from `JobID` or raw parts, `getJobID`, `isMap`, equality/comparison/string/hash, Writable serialization, static read, `forName`, and `getTaskIDsPattern`. The docs state map/reduce tasks can have multiple attempts and each attempt is identified by `TaskAttemptID`.

## Control Flow

The documented MapReduce control flow is:

1. A client creates and populates `JobConf`, including input/output paths or formats, mapper/reducer/combiner/partitioner classes, key/value classes, compression, speculative execution, attempts/failure policies, debug scripts, and notification settings.
2. The client submits the job through `JobClient`/`JobTracker` APIs. Synchronous clients use `runJob(JobConf)` and block. Asynchronous clients use `submitJob(JobConf)`, hold a `RunningJob`, poll `JobStatus`/progress/events, or rely on job-end notification URI delivery.
3. `JobTracker` assigns job IDs, accepts job submissions, tracks cluster state, receives task tracker heartbeats, reports task tracker errors, returns task reports/diagnostics/counters/events, and handles kill requests.
4. Input formats create splits and record readers. `LineRecordReader`, `KeyValueLineRecordReader`, `SequenceFileRecordReader`, and sequence-file text/binary wrappers convert file data into typed key/value records.
5. The default `MapRunner` drives a `Mapper` by iterating `RecordReader.next(key,value)` and sending output through `OutputCollector`. Custom `MapRunnable` implementations can replace this for threaded/asynchronous mapping.
6. Intermediate mapper output is collected, partitioned by `Partitioner`, optionally combined, grouped/sorted by configured comparators, stored as `SequenceFile`s, and shuffled over HTTP to reducers.
7. Reducers run shuffle and sort/group phases, then invoke `Reducer.reduce` per grouped key. Reducer output is collected and written through the configured `OutputFormat`/`RecordWriter`.
8. Task and job lifecycle events are written through `JobHistory` helper methods and can later be parsed by `JobHistory.parseHistoryFromFS` through a listener callback.
9. Clients and framework components exchange typed job/task IDs and events through `Writable` serialization APIs on `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, and `TaskCompletionEvent`.

## State and Persistence Behavior

- `JobConf` persists state as `Configuration` key/value settings. Many methods are typed accessors around configuration keys, including class names, booleans, integers, ranges, compression codecs, comparators, scripts, and notification URIs.
- `JobConf#getJobLocalDir` documents per-job localized scratch storage at `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/`, exposed as `job.local.dir` and as a system property. This is shared scratch space for tasks within a localized job.
- `JobHistory` persists append-only plain text history. Each line has a record type followed by key/value pairs. There is a master index containing start/stop times and job-level properties, plus per-job history files named by job tracker ID and job ID. `HistoryCleaner` removes old files and stale tracker references.
- `JobHistory.JobInfo.logSubmitted` creates a new history file for a job and disables history for later events if creation fails.
- Record readers and writers maintain stream/file positions and progress. `SequenceFileRecordReader`, binary/text sequence readers, and line readers expose byte position and progress for task reporting and split completion.
- `MultiFileSplit`, `JobID`, `TaskID`, `TaskAttemptID`, `JobProfile`, `JobStatus`, and `TaskCompletionEvent` expose `readFields`/`write` methods for Hadoop `Writable` persistence over RPC, task/job metadata storage, and framework communication.
- `TaskCompletionEvent` event IDs are assigned externally and incremented per job from zero, which matters for paged retrieval by `RunningJob#getTaskCompletionEvents(startFrom)` and `JobTracker#getTaskCompletionEvents`.

## Dependencies and Integration Points

- Hadoop core configuration and filesystem types: `Configuration`, `Path`, `FileSystem`, `PathFilter`, `FileAlreadyExistsException`, and local path helpers.
- Hadoop IO types: `Writable`, `WritableComparable`, `Text`, `LongWritable`, `BytesWritable`, `RawComparator`, `MapFile.Reader`, `SequenceFile.Reader`, `SequenceFile.ValueBytes`, and `SequenceFile.CompressionType`.
- Compression integration: `CompressionCodec` classes configured through `JobConf`, `OutputFormatBase`, and sequence-file output compression helpers.
- MapReduce protocols and runtime types: `InputSplit`, `FileSplit`, `InputFormat`, `FileInputFormat`, `FileOutputFormat`, `Counters`, `ClusterStatus`, `TaskReport`, `TaskTrackerStatus`, `TaskInProgress`, `JobInProgress`, `HeartbeatResponse`, `MRConstants`, `InterTrackerProtocol`, and `JobSubmissionProtocol`.
- Networking and topology: `InetSocketAddress`, `org.apache.hadoop.net.Node`, tracker HTTP locations, HTTP shuffle references, and status servlet endpoints.
- Servlet/status integration: `HttpServlet`, request/response `doGet`, and status server servlet registration.
- Java platform dependencies: `IOException`, `DataInput`, `DataOutput`, `DataOutputStream`, `Iterator`, `Map`, `Vector`, `List`, `Collection`, `Enum`, `Class`, `Runnable`, `Closeable`, and `URL`.

## Risks and Compatibility Notes

- This chunk contains old `mapred` APIs. Several methods are explicitly deprecated in favor of newer helpers: `JobConf` input/output path methods prefer `FileInputFormat`/`FileOutputFormat`; `JobConf#getSystemDir` prefers `JobClient#getSystemDir`; `OutputFormatBase` prefers `FileOutputFormat`; string job/task IDs are deprecated in favor of typed `JobID`, `TaskID`, and `TaskAttemptID`.
- `JobConf#setNumMapTasks` is documented as only a hint to the framework. Tests and callers should not assume exact map count when input splitting determines actual tasks.
- Reducer docs explicitly warn that key and value objects are reused. User reducers retaining references without cloning can corrupt results.
- Reporter progress is operationally important. Long-running map/reduce code that does not call `Reporter.progress()` or update status/counters may be killed as timed out unless `mapred.task.timeout` is adjusted.
- Job history creation failure disables history for later events. Consumers should tolerate missing history even when jobs run successfully.
- Job history is text and key/value based; escaping, URL encoding/decoding, and listener parsing are likely compatibility-sensitive. File names with special characters are covered by encode/decode helpers and should be tested.
- `TaskCompletionEvent#getTaskStatus` doc contains the typo `SUCESS`; consumers must rely on enum values rather than documentation spelling.
- `SequenceFileAsBinaryOutputFormat` allows logical sequence-file key/value classes that differ from actual `BytesWritable` objects. Misconfiguration can produce unreadable or misleading sequence files.
- `SequenceFileInputFilter` behavior depends on configuration-loaded filter classes and filter-specific frequency/pattern settings. Invalid filter class, invalid regex, zero/negative frequency, or missing configuration should be tested.
- `OutputLogFilter` rejects `_logs` paths; callers listing output directories must ensure this does not hide legitimate data paths named with that segment.
- The requested range starts after the beginning of `JobClient` and ends before the end of `TaskID`, so a final merged per-file report should reconcile these partial boundaries with adjacent chunks.

## Test Signals

Useful tests or verification targets implied by this API surface:

- `JobConf` round-trip configuration tests for class settings, key/value defaults, compression codec classes, comparator classes, speculative execution flags, task counts, max attempts/failure percentages, profiling ranges, debug scripts, job priority, and notification URI.
- Deprecation compatibility tests showing old `JobConf` input/output path methods still delegate to or interoperate with `FileInputFormat` and `FileOutputFormat`.
- Local directory tests for `getLocalDirs`, `getLocalPath`, `deleteLocalFiles`, and `getJobLocalDir`, including multi-directory placement and cleanup.
- `JobID`, `TaskID`, and `TaskAttemptID` tests for `toString`, `forName`, malformed input rejection, `compareTo`, equality/hash consistency, regex pattern generation with null wildcards, and `Writable` serialization compatibility.
- `TaskCompletionEvent` tests for event ID ordering, typed and deprecated task ID accessors, status serialization, map/reduce flag, runtime, tracker HTTP location, and `EMPTY_ARRAY`.
- Job history tests for `init`, disable/enable behavior, append logging for submitted/started/finished/failed/killed events, encode/decode path helpers, parser listener callbacks, and history cleaner retention rules.
- `RunningJob`/`JobTracker` protocol tests for progress, completion/success states, counters, task completion event paging, diagnostics, kill job/task semantics, and overloaded typed/string ID compatibility.
- Record reader tests for line splitting at split boundaries, max line length, key-value separator handling, progress/position reporting, close idempotency, and empty/last-line behavior.
- Multi-file split tests for aggregate length, per-file lengths, path accessors, locations, serialization, and record readers that treat one file as one record.
- Sequence-file tests for typed input/output, text conversion, raw binary reads/writes, compression type settings, logical class metadata in binary output, raw `ValueBytes` sizes, seek/progress/position, and reader close behavior.
- `SequenceFileInputFilter` tests for MD5 deterministic sampling, percent/frequency behavior, regex matching, configuration propagation through `Configurable`, and invalid configuration handling.
- Mapper/reducer contract tests using `MapRunner`, `MapReduceBase`, `OutputCollector`, `Reporter.NULL`, custom reporter counters/status, custom partitioners, custom grouping comparators, combiner behavior, zero-reducer direct output, and reducer object reuse hazards.
- `StatusHttpServer` tests for servlet registration, attributes, port/thread/SSL configuration, start/stop lifecycle, stack servlet output, and task graph servlet rendering parameters.
