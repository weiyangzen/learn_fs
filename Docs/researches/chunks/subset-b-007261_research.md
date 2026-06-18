# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.17.0.xml lines 18821-25080

## Scope and Artifact Type

This chunk is part of the Hadoop 0.17.0 JDiff XML API snapshot. It records public and protected API metadata, inheritance, implemented interfaces, method signatures, exceptions, fields, deprecation markers, and embedded Javadoc for several Hadoop packages. It is not implementation source, so control flow and state behavior are inferred from the exposed contracts, docs, exceptions, and `Writable`/stream lifecycle APIs visible in the XML.

The chunk begins inside `org.apache.hadoop.io.compress.GzipCodec`, covers compression codecs and native zlib/lzo adapters, retry and serialization frameworks, IPC and RPC metrics/logging utilities, and then enters a large `org.apache.hadoop.mapred` section through the start of `JobStatus`.

## Purpose

The primary purpose of this XML section is API compatibility documentation for Hadoop common and old MapReduce (`mapred`) classes. It captures the Hadoop 0.17.0 public surface that downstream code could compile against:

- Compression APIs expose gzip, lzo, and zlib codec implementations and direct compressor/decompressor contracts.
- Retry APIs provide dynamic proxy wrapping around arbitrary interfaces with reusable retry policies.
- Serialization APIs define pluggable serializers/deserializers selected from configuration.
- IPC APIs expose Hadoop's `Writable`-based client/server RPC layer, versioned protocols, remote exception wrapping, and RPC metrics.
- Logging APIs expose runtime log-level adjustment via CLI and servlet.
- MapReduce APIs expose job submission, cluster/job status, input/output format contracts, split serialization, job configuration, counters, job history, persistence of retired jobs, notification, and CLI wrappers.

## Important APIs, Types, and Functions

### Compression

- `org.apache.hadoop.io.compress.GzipCodec` is only partially visible at the start of the chunk. The visible methods include `getCompressorType`, `createInputStream(InputStream)`, `createInputStream(InputStream, Decompressor)`, `createDecompressor`, `getDecompressorType`, and `getDefaultExtension`. The doc identifies it as a gzip compressor/decompressor factory.
- `GzipCodec.GzipInputStream` extends `DecompressorStream`. It has constructors from `InputStream` and protected `DecompressorStream`, plus `available`, `close`, `read()`, `read(byte[], int, int)`, `skip(long)`, and `resetState`.
- `GzipCodec.GzipOutputStream` extends `CompressorStream`. It has constructors from `OutputStream` and protected `CompressorStream`, plus `close`, `flush`, `write(int)`, `write(byte[], int, int)`, `finish`, and `resetState`. The class bridges `DeflaterOutputStream` into Hadoop's `CompressionOutputStream`.
- `LzoCodec` implements `Configurable` and `CompressionCodec`. It exposes `setConf`, `getConf`, static `isNativeLzoLoaded(Configuration)`, stream factories with optional `Compressor`/`Decompressor`, factory methods for compressor/decompressor instances and types, and `getDefaultExtension`.
- `LzoCompressor` implements `Compressor`. It supports a `CompressionStrategy` enum, direct buffer sizing, native-load checks, synchronized `setInput`, `setDictionary`, `finish`, `finished`, `compress`, `reset`, `getBytesRead`, `getBytesWritten`, and `end`.
- `LzoDecompressor` implements `Decompressor` with a matching `CompressionStrategy`, native-load checks, synchronized input/dictionary/state methods, `decompress`, `reset`, `end`, and protected `finalize`.
- `BuiltInZlibDeflater` extends `java.util.zip.Deflater` and implements Hadoop `Compressor`; `BuiltInZlibInflater` extends `java.util.zip.Inflater` and implements `Decompressor`. Both provide synchronized byte-array methods that throw `IOException`.
- `ZlibCompressor` and `ZlibDecompressor` implement direct-buffer native-style zlib compression/decompression with configurable headers, levels, strategies, byte counters, reset/end lifecycle, and dictionary support.
- `ZlibFactory` chooses zlib compressor/decompressor types and instances based on `Configuration`, falling back or selecting native code depending on `isNativeZlibLoaded`.

### Retry Framework

- `RetryPolicy` defines `shouldRetry(Exception e, int retries)`, returning whether to retry, returning false for "do not retry but do not fail" semantics for void methods, or throwing to fail.
- `RetryPolicies` is a static factory and constants holder. It exposes `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, `RETRY_FOREVER`, fixed-sleep count/time policies, proportional sleep, exponential backoff with randomness, exception-class dispatch, and `RemoteException`-aware dispatch.
- `RetryProxy` creates dynamic proxies for an interface and implementation, either with one policy for all methods or a `Map<String, RetryPolicy>` keyed by method name. Missing method-specific policies default to `TRY_ONCE_THEN_FAIL`.

### Serialization

- `Serializer<T>` and `Deserializer<T>` define stateful stream lifecycle APIs: `open(OutputStream/InputStream)`, `serialize(T)` or `deserialize(T reuse)`, and `close`.
- Their docs explicitly warn they are stateful but must not buffer across calls because other producers/consumers may interleave on the same stream.
- `Serialization<T>` encapsulates an accepted class family and provides matching serializer/deserializer instances.
- `SerializationFactory` extends `Configured`; its constructor reads `io.serializations` from `Configuration` as a comma-delimited class list.
- `WritableSerialization` adapts Hadoop `Writable` to the generic serialization framework through `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`.
- `JavaSerialization` is marked experimental for `java.io.Serializable`; `JavaSerializationComparator` and `DeserializerComparator` compare byte ranges by deserializing objects and using regular comparators, while warning that direct `RawComparator` implementations are better for compare-heavy paths.

### IPC and RPC

- `Client` is Hadoop's low-level IPC client for single-`Writable` request/response calls. It has constructors with value class, `Configuration`, and optional `SocketFactory`; `stop`; `setTimeout`; single-address `call`; user-ticket-aware `call`; and parallel multi-address `call` returning nulls for timed-out or errored calls.
- `RemoteException` wraps remote exception class names and messages. `unwrapRemoteException(Class[])` can match desired exception types, and no-arg `unwrapRemoteException` tries to instantiate the wrapped throwable by class name/string constructor, otherwise returning itself.
- `RPC` builds dynamic client proxies for `VersionedProtocol`, waits for proxies, stops proxies, performs expert parallel reflective calls, and constructs `RPC.Server` instances.
- `RPC.Server` extends `Server` and dispatches `Writable` invocation requests to methods on a protocol implementation instance.
- `RPC.VersionMismatch` exposes protocol interface name, client version, and server version.
- `Server` is the abstract IPC service. It handles bind/listen lifecycle, thread start/stop/join, network timeout and send buffer configuration, listener address queries, static current server/remote IP/remote address accessors for code running under an RPC call, and an abstract `call(Writable, long)`.
- `VersionedProtocol` requires `getProtocolVersion(String protocol, long clientVersion)` and expects subclasses to define static `versionID`.
- `Server` exposes `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`.

### RPC Metrics and Runtime Log Control

- `RpcMetrics` implements `Updater`, registers JMX-facing RPC metrics, and publishes queue time, processing time, discarded operations, and a public metrics map. `doUpdates(MetricsContext)` pushes values to the metrics subsystem; `shutdown` tears down the metrics registration.
- `RpcMgtMBean` exposes sampled operation counts, average/min/max processing and queue times, discarded operation counts/queue time, open connection count, call queue length, and `resetAllMinMax`.
- `LogLevel` provides runtime log-level changes with a CLI `main(String[])`, a `USAGES` string, and `LogLevel.Servlet.doGet(HttpServletRequest, HttpServletResponse)` for HTTP-based changes.

### MapReduce Status, Persistence, Counters, and File Formats

- `ClusterStatus` implements `Writable` and reports task tracker count, running map/reduce counts, max map/reduce capacity, and `JobTracker.State`; `JobClient#getClusterStatus()` is the integration point.
- `CompletedJobStatusStore` implements `Runnable`; it persists retired job information in DFS when `persist.jobstatus.hours` is nonzero and exposes read methods for `JobStatus`, `JobProfile`, `Counters`, and ranges of `TaskCompletionEvent`.
- `Counters` implements `Writable` and `Iterable<Counters.Group>`. It groups counters by enum class/group, supports synchronized lookup, increment, merge, `sum`, size, binary read/write, logging, `toString`, and compact comma-separated `name=value` formatting.
- `Counters.Counter` and `Counters.Group` are `Writable` nested types. Counters hold display name/value and synchronized increments; groups localize display names, lookup counters by id/name, serialize themselves, and iterate over counters.
- `DefaultJobHistoryParser.parseJobTasks(String, JobHistory.JobInfo, FileSystem)` populates an object model from a job history log file.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are MapReduce validation exceptions. `InvalidInputException` wraps multiple input problems and exposes the list plus a concatenated message.
- `FileInputFormat<K,V>` is the base class for file-backed `InputFormat`. It defines splitability checks, static input path and path-filter configuration helpers, `listPaths`, default `validateInput`, default `getSplits`, split-size/block-index helpers, and abstract `getRecordReader`.
- `FileOutputFormat<K,V>` is the base class for file-backed `OutputFormat`. It defines output compression settings, compressor class selection, abstract `getRecordWriter`, output spec validation, output path configuration, and `getWorkOutputPath` for task-attempt temporary output.
- `FileSplit` implements `InputSplit` and `Writable`, representing a path/start/length plus host locations. The constructor taking `JobConf` is deprecated in favor of the host-list constructor.
- `InputFormat<K,V>` validates input, creates logical `InputSplit[]`, and returns a `RecordReader` that respects record boundaries.
- `InputSplit` is `Writable` and reports byte length plus locality hostnames.

### Job Client, Configuration, History, and CLI

- `JobClient` extends `Configured`, implements `MRConstants` and `Tool`, and is the primary client-side interface to `JobTracker`. It constructs/connects to default or specified job trackers, initializes with `JobConf`, closes resources, gets the submission `FileSystem`, submits jobs by job-file path or `JobConf`, retrieves `RunningJob`, map/reduce task reports, cluster status, pending/incomplete jobs, all jobs, and runs a job synchronously by polling progress. It also manages `TaskStatusFilter` in instance or `JobConf` form and has `run`/`main`.
- `JobConf` extends `Configuration` and is the central job description object. It has constructors from defaults, class/jar inference, inherited configuration, XML path/string, and extensive getters/setters for jar, system/local directories, user, input/output paths, input/output formats, compression, key/value classes, comparators, mapper/map-runner/partitioner/reducer/combiner classes, speculative execution, map/reduce counts, retry/failure tolerances, job priority, profiling, debug scripts, job-end notifications, and localized job scratch directory.
- `JobConfigurable` defines `configure(JobConf)` for components initialized from job configuration.
- `JobEndNotifier` manages asynchronous job-completion notification: `startNotifier`, `stopNotifier`, `registerNotification(JobConf, JobStatus)`, and `localRunnerNotification`.
- `JobHistory` handles append-mode job history files, master index files, listener-based parsing, initialization, disable toggles, and cleanup. It exposes `LOG` and `JOBTRACKER_START_TIME`.
- `JobHistory.HistoryCleaner` deletes history older than one month and updates the master index.
- `JobHistory.JobInfo` logs job submitted/started/finished/failed events, exposes all tasks, local job file path, and URL encoding/decoding helpers for history paths and filenames.
- `JobHistory.Keys`, `RecordTypes`, and `Values` are enums for history key namespace, record type tokens, and common string values.
- `JobHistory.Listener` handles parsed history records as `RecordTypes` plus key/value maps.
- `JobHistory.Task`, `TaskAttempt`, `MapAttempt`, and `ReduceAttempt` log task/TIP and attempt lifecycle events with timestamps, hostnames, shuffle/sort times for reduces, counters, and errors.
- `JobPriority` is an enum describing priority.
- `JobProfile` implements `Writable`, tracking user, job id, job configuration file path, web UI URL, and job name for living or retired jobs.
- `JobShell` extends `Configured` and implements `Tool`; it parses `hadoop jar`-style submission flags for `-libjars`, `-archives`, and `-files`.
- `JobStatus` starts at the chunk end. Visible API includes constructors and the beginning of `getJobId`; it implements `Writable` and represents job id, map progress, reduce progress, and run state.

## Control Flow and Lifecycle

Because this is JDiff XML, implementation branches are not visible, but public lifecycle contracts are clear:

- Compression stream flow is `createOutputStream`/`createInputStream` from a codec, optionally using externally supplied compressor/decompressor instances, followed by repeated `write`/`read`, then `finish`/`flush`/`close`, with `resetState` for stream reuse. Raw compressor/decompressor flow is `setInput`, optional `setDictionary`, `compress`/`decompress` while consulting `needsInput`, `finish`/`finished`, `reset`, then `end`.
- Native codec selection flows through `LzoCodec.isNativeLzoLoaded` and `ZlibFactory.isNativeZlibLoaded`, then type/instance factory methods choose the concrete compressor/decompressor exposed to codecs and jobs.
- Retry flow wraps an implementation in a dynamic proxy. On failure, the proxy calls `RetryPolicy.shouldRetry(e, retries)`, sleeps according to the policy where applicable, retries, returns silently for allowed void failures, or rethrows.
- Serialization flow is factory selection from `io.serializations`, `accept(Class)` matching, `open`, repeated serialize/deserialize operations with potential object reuse, and `close`.
- IPC flow is client construction, proxy or direct `Client.call` invocation, server-side `Server.start`, queued request dispatch to `call(Writable, receiveTime)`, metrics update, and `stop`/`join` teardown. `RPC.getProxy` adds protocol-version checking through `VersionedProtocol`.
- MapReduce submission flow documented on `JobClient`: validate input and output specs, compute input splits, set up `DistributedCache` accounting, copy job jar/configuration into the distributed system directory, submit to `JobTracker`, and optionally monitor with `runJob`.
- File input flow is `FileInputFormat.validateInput`, `listPaths`, split computation bounded by filesystem block size/min split size, `InputFormat.getSplits`, then `getRecordReader` per split.
- File output flow is `FileOutputFormat.checkOutputSpecs`, `getRecordWriter`, task writes to `mapred.work.output.dir`, and successful task-attempt output promotion from `${mapred.output.dir}/_temporary/_${taskid}` to final output.
- Job history flow is `JobHistory.init`, append log records for job/task/attempt lifecycle, parse history with a listener or `DefaultJobHistoryParser`, then cleanup of old history files.
- Completed job persistence flow is `CompletedJobStatusStore.store(JobInProgress)` at retirement, later `readJobStatus`, `readJobProfile`, `readCounters`, and `readJobTaskCompletionEvents` from DFS.

## State and Persistence Behavior

- The compressors/decompressors are explicitly stateful: input buffers, dictionaries, counters, finish/finished flags, direct buffer size, native library state, and byte counters are observable. Many methods are synchronized, indicating mutable shared state protection on the object.
- Serializer/deserializer instances are stateful stream adapters but are contractually not allowed to buffer data beyond calls because streams can be shared with other producers/consumers.
- `Configuration`/`JobConf` is the persistent job control surface: most `JobConf` methods set named configuration properties that affect cluster behavior, submission, task JVMs, compression, scheduling, speculative execution, profiling, debug scripts, and notifications.
- `Writable` persistence is central. `ClusterStatus`, `Counters`, `Counters.Counter`, `Counters.Group`, `FileSplit`, `JobProfile`, and `JobStatus` are serialized through `DataOutput`/`DataInput` for RPC, DFS persistence, and job tracker/client communication.
- `Counters.write` documents a binary external format: group count followed by groups, display names, counter counts, and counter name/value pairs.
- `CompletedJobStatusStore` stores retired job data in DFS subject to a configured retain time; a daemon thread removes old persisted job files.
- `JobHistory` persists plain-text append-only records with `[type (key=value)*]` lines. A master index records job tracker/job start/stop information, and each job gets a separate history file named from job tracker id and job id.
- `FileOutputFormat.getWorkOutputPath` documents task-attempt temporary directories and promotion semantics, which are a persistence boundary for exactly-once output under failures/speculation.
- `JobConf.getJobLocalDir` exposes a localized per-job scratch directory under `${mapred.local.dir}/taskTracker/jobcache/$jobid/work/`, also available as a system property.
- RPC metrics maintain interval state and min/max state through `MetricsTimeVaryingRate` fields exposed publicly and via JMX.

## Dependencies and Integration Points

- Compression depends on Java `InputStream`, `OutputStream`, `Deflater`, `Inflater`, Hadoop `CompressionCodec`, `CompressionInputStream`, `CompressionOutputStream`, `Compressor`, `Decompressor`, and `Configuration`.
- Native compression selection integrates with external zlib/lzo libraries and configuration-driven native-code availability.
- Retry integrates with Java dynamic proxy-style interface wrapping, `TimeUnit`, exception-class maps, and `RemoteException`.
- Serialization integrates with Hadoop `Configuration` through `io.serializations`, `Writable`, Java `Serializable`, `RawComparator`, and stream APIs.
- IPC integrates with sockets, `SocketFactory`, `InetSocketAddress`, `UserGroupInformation`, reflection `Method`, Hadoop `Writable`, metrics, JMX, and versioned protocol interfaces.
- Runtime log-level control integrates with servlet APIs and command-line execution.
- MapReduce APIs integrate with `FileSystem`, `Path`, `PathFilter`, `BlockLocation`, `FileStatus`, `DistributedCache`, `Mapper`, `Reducer`, `Partitioner`, `MapRunnable`, `RecordReader`, `RecordWriter`, `OutputCollector`, `Reporter`, `Progressable`, `Tool`, `JobTracker`, `RunningJob`, `TaskReport`, `TaskCompletionEvent`, and `SequenceFile.CompressionType`.
- Job history and completed-job store integrate with DFS/HDFS through `FileSystem` and with user-facing web UI through `JobProfile.getURL`.

## Risks and Edge Cases

- This chunk is API metadata only; method bodies, private fields, exact configuration keys for many setters, and runtime error handling details require source cross-checking outside this XML.
- Many compression objects expose mutable synchronized state. Incorrect pooling, missing `reset`, missing `end`, or mixing dictionaries can corrupt compression streams or leak native/direct-buffer resources.
- Native lzo/zlib availability is configuration- and environment-dependent. Code must tolerate factory fallback and `isNative*Loaded` false paths.
- `finalize` on decompressor classes implies cleanup may rely on GC as a backstop; callers should still use `end` deterministically.
- Retry policies can hide failures, especially `TRY_ONCE_DONT_FAIL` on void methods and `RETRY_FOREVER`; policy selection affects idempotency and backpressure.
- Serialization docs prohibit buffering because streams may be shared. A custom serializer/deserializer that buffers aggressively can break downstream readers/writers.
- `DeserializerComparator` deserializes for comparisons and is likely expensive in sort-heavy MapReduce paths; custom `RawComparator` is the intended optimization.
- `RemoteException.unwrapRemoteException` depends on class lookup and string constructors; missing classes or incompatible constructors fall back to the wrapper.
- RPC protocol versions are explicit through `VersionedProtocol`; missing or wrong `versionID`/`getProtocolVersion` behavior causes `RPC.VersionMismatch`.
- `Server.get`, `getRemoteIp`, and `getRemoteAddress` are context-sensitive and may return null outside valid RPC call contexts.
- `FileOutputFormat.getWorkOutputPath` warns about side-effect file races under speculative execution. Writers must use task-attempt-specific paths or the work output directory to avoid duplicate attempts writing the same HDFS path.
- The `JobConf.getNumMapTasks` doc visible here appears to say "reduce tasks" despite being a map method; this looks like a documentation typo in the API snapshot.
- `JobConf` contains deprecated input/output path methods; callers should use `FileInputFormat` and `FileOutputFormat` static helpers to avoid compatibility drift.
- `InvalidInputException` does not copy its problem list according to docs, so callers must not mutate the list after passing it or after retrieving it.
- `JobHistory` plain-text history parsing and URL encoding helpers make file naming, escaping, and backward-compatible parse behavior important.
- Completed job persistence is disabled when retain time is zero; callers of read methods must handle nulls or empty arrays.
- Runtime log-level servlet/CLI changes are operationally powerful and need access control in deployments, although this XML does not describe security checks.

## Test Signals

Useful tests for code corresponding to this API surface would include:

- Codec round trips for gzip, zlib, and lzo where available; factory fallback tests when native libraries are unavailable; `getDefaultExtension` and compressor/decompressor type consistency.
- Compressor/decompressor lifecycle tests covering `setInput`, partial reads/writes, `needsInput`, `finish`, `finished`, byte counters, `reset`, and `end`, including synchronized reuse paths.
- Retry proxy tests for fixed-count, max-time, proportional, exponential, exception-specific, remote-exception-specific, void-method no-fail, and forever policies with idempotent fake implementations.
- Serialization factory tests using `io.serializations`, `WritableSerialization`, Java serialization, object reuse in `deserialize(T)`, and stream interleaving behavior.
- IPC tests for direct `Client.call`, parallel calls with timeout/null results, UGI-ticket calls, proxy creation/stop, `VersionedProtocol` version mismatch, remote exception wrapping/unwrapping, server start/stop/join, listener address, call queue length, and remote address context methods.
- Metrics tests verifying `RpcMetrics.doUpdates`, JMX bean values, discarded-operation tracking, min/max reset, open connection count, and call queue length.
- `FileInputFormat` tests for path parsing, path filters, nonexistent/mixed input validation, split sizing around block size and `mapred.min.split.size`, unsplittable inputs, and host locality in `FileSplit`.
- `FileOutputFormat` tests for output path validation, existing-output failure, compression codec configuration, work output path formation, and promotion/cleanup behavior under failed and speculative task attempts.
- `Counters` tests for enum and string lookup, localization fallback, synchronized increments, merge/sum behavior, binary write/read compatibility, compact string generation, and logging output.
- `JobClient` tests for submission preflight order, job-file and `JobConf` submission, polling in `runJob`, task report retrieval, task output filter persistence in `JobConf`, and resource close behavior.
- `JobConf` tests for class/jar inference, XML/path constructors, deprecated path compatibility, mapper/reducer/combiner/partitioner/input/output format class storage, compression settings, speculative toggles, failure thresholds, profiling ranges/params, debug script DistributedCache expectations, notification URI substitution, and local/system directory resolution.
- Job history tests for init success/failure, disabled history, submitted/started/finished/failed/killed records, map/reduce attempt records including shuffle/sort times, listener-based streaming parse, object-model parse, URL encode/decode helpers, master index updates, and history cleanup retention.
- Completed job store tests for disabled retain time, DFS write/read of status/profile/counters/events, range slicing of task completion events, null/empty responses on missing jobs, and cleanup daemon behavior.

## Chunk Boundary Notes

The first visible lines are the tail of `GzipCodec`; earlier gzip class declarations and output-stream factory methods are outside this chunk. The final visible line starts `JobStatus.getJobId`; the rest of `JobStatus` is outside this chunk and must be covered by the following chunk before producing the merged per-file report.
