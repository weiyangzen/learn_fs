# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.1.xml - subset-b-007268

Chunk lines: 18780-25021.

## Purpose

This chunk is part of the Hadoop 0.18.1 JDiff XML API snapshot. It is not implementation code; it records public/protected API signatures, inheritance, implemented interfaces, deprecation metadata, checked exceptions, public fields, and embedded Javadoc for Hadoop common, IPC, logging, and old `mapred` APIs. The file is used by JDiff/dev-support tooling to compare Hadoop API surfaces across releases, so the source of truth here is the shape and documentation of API contracts rather than executable control flow.

The chunk starts in the tail of `org.apache.hadoop.io.UTF8`, continues through complete package sections for `org.apache.hadoop.io.compress`, `org.apache.hadoop.io.compress.lzo`, `org.apache.hadoop.io.compress.zlib`, `org.apache.hadoop.io.retry`, `org.apache.hadoop.io.serializer`, `org.apache.hadoop.ipc`, `org.apache.hadoop.ipc.metrics`, and `org.apache.hadoop.log`, then enters `org.apache.hadoop.mapred`. It ends inside the `JobConf` class immediately after the opening of `setOutputFormat`, so `JobConf` is only partially visible in this chunk.

## Important APIs, Types, and Contracts

### Hadoop IO serialization

- `UTF8.Comparator` is a `WritableComparator` optimized for serialized UTF8 keys. The surrounding `UTF8` tail shows string conversion, equality, hash, byte conversion, `readString(DataInput)`, and `writeString(DataOutput, String)`. `UTF8` is documented as deprecated in favor of `Text`, which is an API migration signal for any consumers still relying on old string writables.
- `VersionedWritable` implements `Writable` and requires `getVersion()`. Its `write(DataOutput)` and `readFields(DataInput)` contract stores/checks a version byte and may throw `VersionMismatchException`, giving older writable payloads an explicit compatibility hook.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length integers and longs. Their public API is the standard Hadoop writable shape: constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `Writable` defines the core serialization protocol: `write(DataOutput)` and `readFields(DataInput)`. Its Javadoc emphasizes reuse of existing storage during deserialization.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` and is documented as the expected key type for the old MapReduce framework.
- `WritableComparator` is the core comparator registry and byte-level comparison utility. It has synchronized static `get(Class)` and `define(Class, WritableComparator)` registry methods, object and raw byte comparison overloads, and byte parsing helpers such as `compareBytes`, `hashBytes`, `readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, and `readVInt`.
- `WritableFactories`, `WritableFactory`, and `WritableName` provide construction and name-alias indirection for writable types, including support for non-public writable classes and class renaming without invalidating serialized files containing class names.
- `WritableUtils` collects serialization utilities: compressed byte/string arrays, string arrays, cloning via serialization, zero-compressed `writeVInt`/`writeVLong` and `readVInt`/`readVLong`, variable-length integer size/sign helpers, enum serialization via strings, and `skipFully`.

### Compression APIs

- `CodecPool` is a global compressor/decompressor pool for reusing potentially native codec objects. Its API is `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`.
- `CompressionCodec` defines the codec abstraction: creating compression/decompression streams with or without caller-supplied `Compressor`/`Decompressor`, discovering compressor/decompressor classes, creating codec-specific codec engines, and reporting a default filename extension.
- `CompressionCodecFactory` maps filename suffixes to codec instances. It is configured from `io.compression.codecs`, defaults to gzip and zip per the doc, exposes static `getCodecClasses`/`setCodecClasses`, `getCodec(Path)`, `removeSuffix`, and a small `main` test hook. It publishes a public static final `LOG`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases over protected final `in`/`out`. They force subclasses to implement byte-array `read`/`write`, `resetState`, and output `finish`, preventing accidental leakage to the underlying stream.
- `Compressor` and `Decompressor` are stateful, stream-oriented interfaces modeled after `java.util.zip.Deflater` and `Inflater`. They expose input buffers, dictionaries, finish/finished state, byte counters, `compress`/`decompress`, `reset`, and `end`.
- `DefaultCodec`, `GzipCodec`, and `LzoCodec` implement `CompressionCodec` and in some cases `Configurable`. `GzipCodec` includes protected static bridge stream classes wrapping deflater/inflater streams. `LzoCodec` exposes `isNativeLzoLoaded(Configuration)` and depends on native LZO availability.
- `LzoCompressor` and `LzoDecompressor` implement `Compressor`/`Decompressor` with synchronized mutable methods and strategy enums. They include native-loaded checks, direct-buffer-size constructors, byte counters, reset/end, and `finalize` on the decompressor.
- Zlib support includes Java built-in wrappers (`BuiltInZlibDeflater`, `BuiltInZlibInflater`) and native-capable `ZlibCompressor`/`ZlibDecompressor` with enum types for compression header, level, and strategy. `ZlibFactory` chooses native or built-in compressor/decompressor implementations from `Configuration`.

### Retry, serializer, and IPC APIs

- `RetryPolicies` is a factory and constants holder for immutable `RetryPolicy` implementations. It exposes fixed sleep, maximum time, proportional sleep, randomized exponential backoff, exception-class dispatch, remote-exception dispatch, `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`.
- `RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, return silently for void methods, or rethrow an exception. `RetryProxy.create` uses dynamic proxies to wrap an implementation with either one policy for all methods or a method-name-to-policy map.
- Serializer contracts are split into `Serializer<T>`, `Deserializer<T>`, `Serialization<T>`, and `SerializationFactory`. Serializers/deserializers are explicitly stateful but must not buffer across calls because other producers/consumers may interleave reads or writes on the same stream.
- `JavaSerialization`, `JavaSerializationComparator`, `DeserializerComparator`, and `WritableSerialization` bridge Hadoop's pluggable serialization system to Java `Serializable`, `Comparable`, `RawComparator`, and `Writable` contracts.
- `Client`, `Server`, `RPC`, `RPC.Server`, `RPC.VersionMismatch`, `RemoteException`, and `VersionedProtocol` describe the old Hadoop IPC/RPC layer. IPC calls pass and return `Writable` values; RPC protocols are Java interfaces with primitive, `String`, `Writable`, or array parameters/returns and should throw only `IOException`.
- `Client.call` supports single calls, user-ticket calls, and parallel batch calls to multiple addresses. `Server` exposes lifecycle (`start`, `stop`, `join`), listener/socket configuration, current server context, remote address helpers, queue/connection metrics, public `HEADER`/`CURRENT_VERSION`, and abstract `call(Writable, long)`.
- `RPC.getProxy`, `waitForProxy`, `stopProxy`, parallel `call`, and `getServer` create client proxies and server wrappers for `VersionedProtocol` implementations. `VersionedProtocol.getProtocolVersion` is the wire compatibility gate, with `RPC.VersionMismatch` carrying interface, client version, and server version.
- `RemoteException` wraps remote exception class names and can unwrap to specific lookup types or instantiate an `IOException`/`Throwable` with a string constructor when possible.

### Metrics, logging, and MapReduce APIs

- `RpcMetrics` implements `Updater`, publishes queue and processing time metrics, and registers JMX management. `RpcMgtMBean` exposes sampled RPC operation counts, average/min/max processing and queue times, reset, open-connection count, and call-queue length.
- `LogLevel` provides runtime log-level changes through a command-line `main` and a `LogLevel.Servlet` HTTP endpoint.
- `ClusterStatus` is a writable snapshot of old MapReduce cluster state, including task tracker counts, running map/reduce tasks, maximum capacities, state serialization, and textual representation.
- `Counters`, `Counters.Counter`, and `Counters.Group` are synchronized writable counter containers. Counters support enum and string group addressing, increment, lookup, summing, logging, compact string output, display names/localization, and a documented binary external format.
- `DefaultJobHistoryParser.parseJobTasks` populates a `JobHistory.JobInfo` object from a history log file on a `FileSystem`.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` model MapReduce configuration/input/output validation failures. `InvalidInputException` carries a list of `IOException` problems and synthesizes a message from them.
- `FileInputFormat<K,V>` is the base for file-based input formats. It validates/list statuses, computes splits from file blocks, supports path filters, manages input paths, and leaves `getRecordReader` abstract.
- `FileOutputFormat<K,V>` is the base for file-based output formats. It manages output compression configuration, output paths, per-task temporary work output paths, output-spec validation, and abstract record writer creation. Its documentation highlights speculative-execution side-file risks and the `_temporary/_${taskid}` promotion model.
- `FileSplit` is a writable `InputSplit` containing file path, byte start, byte length, and host locations. The constructor that takes `JobConf` is deprecated in favor of the host-list constructor.
- `ID` is the comparable/writable integer identifier base for `JobID`, `TaskID`, and `TaskAttemptID`.
- `InputFormat<K,V>` defines `validateInput`, `getSplits`, and `getRecordReader`; `InputSplit` defines `getLength`, `getLocations`, and extends `Writable`.
- `IsolationRunner.main` is a command-line hook to rerun failed tasks in isolation.
- `JobClient` is the primary old MapReduce client API. Visible methods cover construction, initialization/close, filesystem access, job submission by `JobConf` or job-file string, job lookup, map/reduce task reports, cluster status, job listing, blocking `runJob`, task output filtering, default map/reduce capacity lookup, system directory lookup, `Tool.run`, and `main`. Its documentation lays out the submission workflow: validate input/output, compute splits, set distributed-cache accounting, copy jar/config to the system directory, submit to `JobTracker`, then optionally monitor.
- `JobClient.TaskStatusFilter` is an enum represented by generated `values` and `valueOf`.
- `JobConf` begins here and is partial. Visible API covers constructors from default config, example class, `Configuration`, XML path/string, jar path resolution, local directories/files, deprecated old input/output path methods, user name, failed-task temporary file retention, task-file retention regexes, working directory, input/output format class accessors up to the start of `setOutputFormat`.

## Control Flow and Behavioral Semantics

Because this is a JDiff XML document, control flow is represented by API contracts and Javadoc rather than Java statements.

- Writable flow is `write(DataOutput)` followed by object reuse and `readFields(DataInput)`. `VersionedWritable` adds a leading version check, and variable-length integer utilities define byte-level encodings that consumers must read symmetrically.
- Raw comparator flow favors comparing serialized bytes first. `WritableComparator.compare(byte[],...)` falls back to deserializing two writable keys, then calling object comparison, unless subclasses override the raw comparator.
- Compression flow is push/pull state machine based: callers provide input when `needsInput()` is true, call `compress`/`decompress` into output buffers, signal `finish()`, check `finished()`, then `reset()` for reuse or `end()` to release resources. `CodecPool` makes this lifecycle reusable but requires explicit return of codec engines.
- Stream compression flow wraps caller streams in `CompressionInputStream`/`CompressionOutputStream`. Output streams must call `finish()` to flush codec trailers without necessarily closing the underlying stream; input streams can `resetState()` after repositioning underlying input.
- Retry flow is proxy-mediated. A failed method call is passed to `RetryPolicy.shouldRetry`; the result decides whether the proxy retries, returns for void-only silent policies, or rethrows.
- IPC/RPC flow is client proxy or writable call -> socket connection to `Server`/`RPC.Server` -> version/protocol checks for `VersionedProtocol` -> server `call` dispatch -> `Writable` response or `RemoteException`.
- MapReduce job flow in `JobClient` is explicitly documented: validate IO specs, compute splits, prepare distributed-cache metadata, copy the job jar/configuration into the distributed filesystem system directory, submit to `JobTracker`, and monitor through `RunningJob` or notification.
- File input flow lists `FileStatus` entries, optionally filters them, computes split sizes using target/min/block sizes, maps offsets to block indexes/locations, and creates `InputSplit` values consumed by `RecordReader`.
- File output flow validates destination paths, configures optional codec output, writes attempt output into a task-specific temporary path, then relies on framework promotion to final output for successful attempts.

## State and Persistence Behavior

- The XML itself persists public API state: class names, inheritance, method signatures, documentation, and deprecation strings. It is deterministic metadata for API comparison.
- `Writable` implementations persist object state to `DataOutput` and restore it from `DataInput`; versioned writables persist an implementation version byte.
- `WritableName` and `WritableFactories` hold static registries that affect deserialization/instantiation of named writable classes and non-public writable classes.
- Variable-length integer/string/compressed-array helpers define long-lived binary file and shuffle formats, so small encoding changes would break compatibility.
- Codec objects are mutable resources with internal buffers and optional native state. Pools, `reset`, and `end` are essential state-management boundaries.
- Serializer/deserializer instances are stateful around opened streams, but their contracts prohibit buffering that would hide bytes from other stream users.
- IPC client/server objects manage sockets, handler threads, call queues, connection counts, ping intervals, user tickets, and metrics.
- `RpcMetrics` persists runtime samples in metrics objects and publishes them through Hadoop metrics/JMX.
- MapReduce state appears in `JobConf` configuration properties, `ClusterStatus` snapshots, `Counters` binary payloads, `FileSplit` serialized split metadata, `JobClient` job submission artifacts, and filesystem output paths. `FileOutputFormat` documents persistence of side-effect files through attempt-specific temporary directories and promotion on success.

## Dependencies and Integration Points

- Java core APIs: `java.io` streams and `DataInput`/`DataOutput`, `java.net` sockets/addresses, `java.util` collections/comparators/enums, `java.util.concurrent.TimeUnit`, `java.util.zip` deflater/inflater, reflection `Method`, servlet APIs for log-level changes, and JMX/metrics interfaces.
- Hadoop common APIs: `Configuration`, `Configured`, `Configurable`, `Path`, `FileSystem`, `FileStatus`, `BlockLocation`, `PathFilter`, `Progressable`, `UserGroupInformation`, metrics contexts/util classes, and Hadoop `Writable`/`RawComparator`.
- Native integration points: LZO and zlib codecs can use native libraries, with explicit `isNativeLzoLoaded` and `isNativeZlibLoaded` checks and built-in Java zlib fallback wrappers.
- MapReduce integration: `JobClient`, `JobConf`, `InputFormat`, `InputSplit`, `RecordReader`, `Reporter`, `OutputFormat`, `RecordWriter`, `TaskReport`, `JobStatus`, `RunningJob`, `DistributedCache`, and `JobTracker` are linked by Javadoc and signatures.
- Tooling integration: as a `dev-support/jdiff` artifact, this XML integrates with API-diff generation rather than runtime Hadoop services.

## Risks and Edge Cases

- Boundary risk: this chunk starts in the middle/tail of `UTF8` and ends inside `JobConf`, so a final merged file report must combine adjacent chunks before claiming full API coverage.
- Compatibility risk: many APIs define binary formats (`Writable`, `Counters`, `FileSplit`, VInt/VLong, compressed arrays). Signature or encoding changes can break persisted Hadoop data, shuffle data, or RPC payloads.
- Native resource risk: LZO/zlib compressors and decompressors carry native/direct-buffer state; missed `reset`, `end`, or pool return can leak resources or corrupt reuse.
- Threading risk: many counter and codec methods are synchronized, but pool and registry APIs also expose shared mutable global state. Callers must respect object lifecycle and not share mutable compressors across concurrent streams unless designed for it.
- API deprecation risk: visible deprecated APIs include `UTF8`, `FileInputFormat.listPaths`, old `FileSplit(Path,long,long,JobConf)`, `InputFormat.validateInput`, `JobClient` string job-id overloads, several `JobConf` input/output path helpers, `JobConf.getSystemDir`, and numeric counter lookup. Later code should prefer the documented replacements.
- Documentation quality risk: several Javadocs contain typos or malformed escaped text, including `DataOuput`, `deseriablize`, `mutliplied`, `invalidiating`, and escaped fragments in a `JobConf.setOutputPath` deprecation string. JDiff consumers should treat signature attributes as authoritative over prose.
- Remote error risk: `RemoteException.unwrapRemoteException` depends on class-name lookup and constructors, which can fail or return the wrapper when a local class is unavailable or incompatible.
- MapReduce output risk: `FileOutputFormat.getWorkOutputPath` documents speculative task attempts writing side files; applications must use attempt-unique temporary paths or rely on work output paths to avoid duplicate writers.
- Retry risk: `RETRY_FOREVER` and exponential retry policies can mask persistent failures or increase load if paired with non-idempotent methods.

## Test Signals and Validation Targets

- API-diff tests should verify that this XML remains well-formed, that class/interface boundaries match expected JDiff output, and that deprecated strings are preserved exactly because downstream comparisons may be textual.
- Serialization compatibility tests should round-trip `Writable`, `VersionedWritable`, `VIntWritable`, `VLongWritable`, `Counters`, `Counter`, `Group`, `FileSplit`, and `ID` through `DataOutput`/`DataInput`.
- Byte comparator tests should compare raw `WritableComparator` output with object-level `compareTo` behavior and validate `compareBytes`, hash, primitive readers, and VInt/VLong byte decoding.
- Codec tests should exercise codec factory lookup by suffix, configured codec class lists, compressor/decompressor pooling, `finish`/`finished`, `reset`, and native-zlib/native-lzo fallback behavior.
- Retry/proxy tests should cover fixed, proportional, exponential, exception-specific, remote-exception-specific, and no-fail/forever policies, especially exception propagation semantics.
- IPC tests should cover client/server round trips, parallel calls, proxy stop, protocol version mismatch, remote exception unwrapping, listener address reporting, connection counts, and call queue metrics.
- Metrics/logging tests should validate `RpcMetrics.doUpdates`, JMX bean values, min/max reset, and log-level servlet/CLI behavior.
- MapReduce tests should cover input path parsing/filtering, split computation from block locations, output path validation and compression class configuration, work output path isolation for speculative attempts, job submission path preparation, task report lookup overloads, and `JobConf` deprecated-method compatibility.

## Chunk Merge Notes

- Preceding chunk is needed for the beginning of `org.apache.hadoop.io.UTF8` and any package preamble before line 18780.
- Following chunk is needed for the rest of `org.apache.hadoop.mapred.JobConf` and later `mapred` API classes.
- This chunk should be merged as an API-surface section, not as implementation source analysis. The final per-file report should explain that `hadoop_0.18.1.xml` is a generated JDiff snapshot for API compatibility research.
