# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.3.xml lines 12397-18635

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.18.3. It begins inside the public API entry for `org.apache.hadoop.io.Text`, continues through the rest of `org.apache.hadoop.io`, `org.apache.hadoop.io.compress`, native LZO/zlib adapters, retry and serialization APIs, the Hadoop IPC/RPC API surface, runtime log-level helpers, and the beginning of `org.apache.hadoop.mapred`. It ends inside the long class documentation for `org.apache.hadoop.mapred.JobClient`.

The source is generated API metadata rather than Java implementation. The research surface is therefore the compatibility contract: public/protected classes and interfaces, inheritance, implemented interfaces, constructors, method signatures, declared exceptions, fields, visibility/static/final/synchronized/abstract flags, deprecation markers, and embedded Javadocs.

## Purpose

The `org.apache.hadoop.io` portion documents Hadoop's core `Writable` serialization contract and several key value types. It covers UTF-8 text representations, variable-length numeric writables, version-checked writable records, raw byte comparators, factories and aliases for writable instantiation, and shared utilities for compressed byte/string arrays, zero-compressed integers, enum serialization, cloning, and exact skipping.

The `org.apache.hadoop.io.compress` portion documents the streaming compression abstraction used by SequenceFiles, MapReduce input/output formats, and file suffix based codec discovery. It defines codec factories, compressor/decompressor pooling, compression stream base classes, Java zlib/gzip implementations, and optional native LZO/zlib wrappers.

The retry and serialization sections expose reusable infrastructure for proxy-level retry policies and pluggable object serialization. These APIs are used by Hadoop RPC clients and by MapReduce sorting/shuffling paths that need raw or deserialized comparison.

The `org.apache.hadoop.ipc` portion documents Hadoop's pre-protobuf Writable-based RPC framework: clients send one `Writable` parameter to servers, receive one `Writable` result, create dynamic protocol proxies, perform parallel calls, enforce protocol version checks, expose server-local call context, and publish RPC metrics through Hadoop metrics and JMX.

The `org.apache.hadoop.mapred` portion starts the old MapReduce API surface. It covers cluster status, counters, job history parsing, file input/output format bases, file splits, ID parsing/serialization, input format/split contracts, input/job configuration exception types, task isolation runner entry point, and the beginning of `JobClient`, the primary user-facing bridge to `JobTracker`.

## Important APIs, Types, and Functions

### Text and Writable Core

- The chunk starts with the tail of `Text`: byte-range `append`, `clear`, `toString`, `readFields`, static `skip`, `write`, bytewise `compareTo`, equality/hash, UTF-8 `decode`/`encode` overloads with replacement control, static `readString`/`writeString`, UTF-8 validation overloads, `bytesToCodePoint(ByteBuffer)`, and `utf8Length(String)`.
- `Text.Comparator` extends `WritableComparator` and provides raw byte-array comparison optimized for serialized `Text` keys.
- `TwoDArrayWritable` wraps `Writable[][]` matrices with a declared value class, `toArray`, `set`, `get`, and Writable read/write.
- `UTF8` is a deprecated `WritableComparable` string type replaced by `Text`. It exposes raw bytes/length, string and copy constructors, setters, read/write/skip, comparison/equality/hash/string conversion, and static UTF-8 string helpers.
- `UTF8.Comparator` is the raw comparator counterpart for serialized `UTF8` keys.
- `VersionedWritable` is an abstract base for Writables with a single-byte implementation version. Its `readFields` checks the incoming version and raises `VersionMismatchException` when the serialized version differs from `getVersion()`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` wrappers using Hadoop variable-length integer encodings via `WritableUtils`.
- `Writable` defines the core `write(DataOutput)` and `readFields(DataInput)` protocol. The docs explicitly encourage object storage reuse during deserialization.
- `WritableComparable<T>` combines `Writable` and `Comparable<T>` for MapReduce keys.
- `WritableComparator` is the central comparator registry and raw comparison base. It can register optimized comparators with `define`, retrieve comparators with synchronized `get`, create new key instances, compare deserialized keys, compare raw serialized byte ranges, and parse primitive values or vint/vlongs from byte arrays.
- `WritableFactories` and `WritableFactory` provide synchronized class-to-factory registration for non-public Writables and reflective construction with optional `Configuration`.
- `WritableName` maps Writable classes to compact names/aliases and resolves aliases back to classes.
- `WritableUtils` provides compressed byte/string array helpers, plain string/string-array helpers, display formatting for byte arrays, serialization-based clone/cloneInto, vint/vlong read/write and size/sign helpers, enum string serialization, and `skipFully` for exact byte skipping.

### Compression

- `CodecPool` is a global compressor/decompressor pool. It gets compressors/decompressors for a `CompressionCodec`, creating new instances when no reusable object is available, and returns them to the pool for reset/reuse.
- `CompressionCodec` encapsulates a streaming compression/decompression pair. It creates compression input/output streams, optionally with supplied `Compressor`/`Decompressor` instances, exposes compressor/decompressor implementation types, creates fresh codec state, and reports a default file extension.
- `CompressionCodecFactory` reads configured codec classes from `io.compression.codecs` with gzip/zip defaults, maps filename suffixes to codecs, exposes static get/set helpers for codec class lists, removes suffixes, and has a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases that wrap protected final `in`/`out` streams. They require concrete `read`/`write`, `resetState`, and output `finish` implementations to avoid accidentally leaking raw underlying stream behavior.
- `Compressor` defines the Deflater-like contract: feed input, optional dictionary, `needsInput`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`.
- `Decompressor` defines the Inflater-like counterpart: feed input, optional dictionary, `needsInput`, `needsDictionary`, `finished`, `decompress`, `reset`, and `end`.
- `DefaultCodec` implements `CompressionCodec` and `Configurable`, using Hadoop configuration to create default deflate streams and zlib compressor/decompressor instances.
- `GzipCodec` extends `DefaultCodec` for gzip, with protected nested `GzipInputStream` and `GzipOutputStream` bridge classes around decompressor/compressor streams. The nested streams expose normal stream operations plus `resetState`; output streams support `finish` without closing the underlying stream.
- `LzoCodec` implements `CompressionCodec` and `Configurable` for streaming LZO. It exposes `isNativeLzoLoaded`, creates LZO streams/state, and reports the default LZO extension.
- `LzoCompressor` and `LzoDecompressor` implement native-backed `Compressor`/`Decompressor`, with constructors accepting compression strategy and direct buffer size, native-library availability checks, input/dictionary methods, finish/needs/finished state, byte counters for compression, reset/end, and a `finalize` cleanup path on the decompressor.
- `LzoCompressor.CompressionStrategy` and `LzoDecompressor.CompressionStrategy` are public enums with normal `values` and `valueOf`.
- `BuiltInZlibDeflater` and `BuiltInZlibInflater` adapt `java.util.zip.Deflater`/`Inflater` to Hadoop `Compressor`/`Decompressor`.
- `ZlibCompressor` and `ZlibDecompressor` are native-oriented zlib implementations with configurable compression level, strategy, header mode, and direct buffer size. Public nested enums model zlib header, compression level, and strategy options.
- `ZlibFactory` centralizes native-zlib availability and creation. It checks whether native zlib is loaded, returns zlib compressor/decompressor classes, creates compressor/decompressor instances, and gets/sets compression level and strategy through `Configuration`.

### Retry and Serialization

- `RetryPolicies` exposes stock immutable `RetryPolicy` implementations: try once and fail, try once and ignore void failures, retry forever, limited fixed sleep, limited maximum-time fixed sleep, proportional sleep, exponential backoff, exception-specific retry maps, and remote-exception-specific retry maps.
- `RetryPolicy.shouldRetry(Exception, int)` decides whether a failed method invocation should be retried based on the thrown exception and retry count.
- `RetryProxy.create` builds dynamic proxies over implementation objects, either with one policy for every interface method or a method-name map with a default fallback policy.
- `Serializer<T>` and `Deserializer<T>` provide `open`, per-object serialize/deserialize, and `close` contracts over streams. `Deserializer.deserialize(T)` may reuse a supplied object.
- `Serialization<T>` pairs serializers and deserializers and declares an `accept(Class<?>)` check.
- `SerializationFactory` reads `io.serializations` from configuration, instantiates serialization implementations, and chooses serializer/deserializer support for a target class.
- `WritableSerialization` adapts Hadoop `Writable.write`/`readFields` to the generic serialization framework.
- `JavaSerialization` is an experimental serialization for `java.io.Serializable`.
- `DeserializerComparator<T>` is a raw comparator that deserializes both byte ranges before comparing normally; `JavaSerializationComparator<T>` specializes that path for Java-serialized comparable objects.

### IPC, RPC, and Metrics

- `Client` is the Writable IPC client. Constructors bind a value class, configuration, and optional `SocketFactory`; static `setPingInterval` writes ping interval configuration; `call` sends a `Writable` to one address, to one address with ticket/user context, or to many addresses in parallel; `stop` terminates all client threads.
- `RemoteException` carries a remote exception class name and message. `unwrapRemoteException` either unwraps to one of requested lookup types or reflectively instantiates an `IOException`/`Throwable` with a string constructor.
- `RPC` creates protocol proxies (`getProxy` overloads and `waitForProxy`), stops proxies, performs parallel calls, and constructs `RPC.Server` instances for protocol implementations. The docs define an RPC protocol as a Java interface whose parameters and returns are supported Writable/primitive/string/array forms and whose protocol version is checked.
- `RPC.Server` extends the abstract IPC `Server` and dispatches incoming Writable calls to the implementation instance. Its constructors bind instance, configuration, address, port, handler count, and verbosity.
- `RPC.VersionMismatch` reports protocol incompatibility with interface name, client version, and server version getters.
- `Server` is the abstract IPC service. It binds sockets, starts/stops/joins handler threads, exposes listener address, call queue length, open connection count, socket send buffer sizing, a no-longer-used timeout setter, static access to current server and remote caller IP/address during a call, and an abstract `call(Writable, long)` handler.
- `VersionedProtocol.getProtocolVersion(String, long)` is the base protocol-version negotiation method. Implementing protocol interfaces are expected to expose a static final `versionID`.
- `RpcMetrics` publishes queue and processing time metrics, a map of per-method rates, and registers a JMX MBean. It implements Hadoop metrics `Updater` with `doUpdates` and supports `shutdown`.
- `RpcMgtMBean` is the JMX management interface for sampled operation counts, processing-time averages/min/max, queue-time averages/min/max, min/max reset, open connections, and queued calls.

### Logging and MapReduce APIs

- `LogLevel` is a runtime log-level tool with command-line `main` and usage text; `LogLevel.Servlet` provides the HTTP servlet implementation through `doGet`.
- `ClusterStatus` is a Writable cluster summary: task tracker count, current map/reduce task counts, maximum map/reduce capacity, `JobTracker.State`, and read/write serialization.
- `Counters` is a Writable iterable of counter groups. It creates/looks up groups and counters by enum or group/name strings, increments individual counters, sums/increments all counters, reports size, logs, and emits normal or compact string forms.
- `Counters.Counter` is a Writable value with name, display name, current long count, and increment operation.
- `Counters.Group` is a Writable iterable of counters with group name/display name, counter lookup, value lookup, size, and read/write.
- `DefaultJobHistoryParser.parseJobTasks` parses job history task data into `JobInfo`.
- `FileAlreadyExistsException`, `InvalidFileTypeException`, `InvalidInputException`, and `InvalidJobConfException` are typed `IOException` surfaces for output collisions, unexpected file/directory types, accumulated input validation problems, and invalid/missing job configuration.
- `FileInputFormat<K,V>` is the base `InputFormat`. It manages minimum split size, splitability, record reader creation, input path filters, status/path listing, deprecated `validateInput`, split generation, split-size computation, block-index lookup, input path setters/adders, and input path retrieval.
- `FileOutputFormat<K,V>` is the base `OutputFormat`. It manages compression enablement and codec class configuration, record writer creation, output spec checking, final output path, work output path, and task output path.
- `FileSplit` implements `InputSplit` with path, byte start, byte length, host locations, Writable serialization, and string rendering.
- `ID` is the numeric WritableComparable base for `JobID`, `TaskID`, and `TaskAttemptID`, with protected `id`, parse/format helpers, equality/hash/order, and static `read`/`forName`.
- `InputFormat<K,V>` defines input validation, split generation, and `RecordReader` creation. Its docs make the split-to-mapper and record-boundary responsibilities explicit.
- `InputSplit` is a Writable byte-oriented unit of work with length and location hostnames.
- `IsolationRunner.main` runs a single task from a task directory, supporting isolated task debugging/reproduction.
- `JobClient` implements `MRConstants` and `Tool` and is the primary user-job interface to `JobTracker`. In this chunk it exposes constructors for default or explicit JobTracker connection, synchronized command-line configuration access, initialization, close, filesystem access for staging, job submission by job file or `JobConf`, job lookup by `JobID` or deprecated string ID, map/reduce task reports by `JobID` or deprecated string ID, cluster status, running/submitted job lists, static `runJob`, task-output filter get/set helpers, `run`, default map/reduce capacity queries, system directory lookup, and `main`.

## Control Flow

Writable control flow is conventional and explicit: callers construct or reuse an object, invoke `write(DataOutput)` to emit fields, then `readFields(DataInput)` to restore fields into an existing object. Comparator control flow can avoid object allocation by using `WritableComparator.compare(byte[], int, int, byte[], int, int)` over serialized key bytes; custom comparators are registered globally and fetched by key class.

Text and UTF-8 flows operate on byte arrays rather than Java characters where possible. `Text` can append byte ranges, validate UTF-8, decode with either replacement or strict error handling, encode strings to `ByteBuffer`, traverse code points from a `ByteBuffer`, and compute encoded lengths. Serialized strings use Hadoop's length-prefixed forms; `skip` helpers allow consumers to move over encoded data without allocating the string.

Versioned writable flow starts by reading an implementation version byte, comparing it with `getVersion()`, and failing with `VersionMismatchException` before subclass-specific state is accepted. This gives evolving records an early compatibility gate.

Compression flow is pull/push oriented. Codecs create compression streams directly or with pooled compressor/decompressor instances. A compressor receives input when `needsInput()` is true, optionally receives a preset dictionary, then `compress` fills caller-provided output buffers until `finish`/`finished`. Decompressors mirror that with `needsDictionary`, `decompress`, and reset/end lifecycle. `CompressionInputStream.resetState` is specifically intended for cases where the underlying stream is repositioned.

Codec discovery flow starts with `CompressionCodecFactory` loading configured classes, registering default extensions, then choosing a codec by filename suffix. MapReduce output paths use `FileOutputFormat` compression configuration to decide whether and how to wrap record writers.

Retry flow wraps an implementation with `RetryProxy`; each thrown exception is passed to `RetryPolicy.shouldRetry` with the current retry count. Policies either rethrow, suppress void failures, sleep and retry, or consult exception/remote-exception maps.

Serialization flow starts from `SerializationFactory`, which reads configured serialization classes and chooses the first implementation whose `accept` method supports the target class. `Serializer.open`/`Deserializer.open` bind the stream, per-object calls move data, and `close` releases resources. Raw comparators built on deserialization deserialize byte slices before normal comparison.

IPC flow starts with an `RPC.getProxy`/`waitForProxy` or raw `Client` creation. The client serializes a Writable request, sends it to the server address, and returns a Writable response or unwraps network/remote exceptions. `RPC.Server` receives calls through `Server`, checks/uses protocol version information, invokes the protocol implementation, and records queue/processing metrics. Static `Server.get`, `getRemoteIp`, and `getRemoteAddress` expose per-call context during request handling.

MapReduce submission flow in `JobClient` is documented as: validate input/output specs, compute `InputSplit`s, prepare `DistributedCache` accounting, copy the job jar/configuration to the JobTracker system directory in the distributed filesystem, submit to `JobTracker`, and optionally monitor progress. `runJob` composes submission and polling until completion.

File input flow in `FileInputFormat` lists configured input paths, applies an optional `PathFilter`, validates input early, computes split sizes from block size/min split constraints, maps split offsets to block locations, and creates `FileSplit`s that become mapper work units. `InputFormat.getRecordReader` must then preserve record boundaries for the split.

File output flow in `FileOutputFormat` checks destination validity, configures compression, writes task attempt output under a task/work path, and later relies on the MapReduce commit path outside this chunk to promote task output to the final output directory.

Counters flow through nested group/counter lookup. Callers increment counters by enum or explicit group/name; groups lazily find or create counters; counters are serialized with the job/task state and can be rendered for logs or compact reporting.

## State and Persistence Behavior

This JDiff XML persists the Hadoop 0.18.3 public API for compatibility comparison. It does not contain runtime state itself, but the APIs define several durable or process-local state contracts.

`Writable`, `Text`, `UTF8`, `TwoDArrayWritable`, `VersionedWritable`, `VIntWritable`, `VLongWritable`, `ClusterStatus`, `Counters`, `FileSplit`, `ID`, and `InputSplit` define binary persistence through `DataInput`/`DataOutput`. Changes to field order, length encoding, version bytes, class names, or vint/vlong rules are wire-format compatibility risks.

`Text` and `UTF8` store byte arrays plus encoded lengths. APIs that expose raw bytes require callers to respect logical lengths; backing capacity may be larger than valid data. `Text` additionally defines strict versus replacing UTF-8 decode behavior, which affects data validation and corruption handling.

`WritableComparator`, `WritableFactories`, and `WritableName` maintain process-global registries. Their synchronized registration and lookup affect how ObjectWritable, sort comparators, and non-public Writable construction behave across the JVM.

`WritableUtils` clone/cloneInto persists temporary state through in-memory serialization buffers. Its compressed byte/string helpers persist data in compressed binary form, and its enum helpers persist enum names as strings rather than ordinals.

`CodecPool` is process-global mutable state for reusable native or Java compression objects. Returned compressor/decompressor instances can retain buffers and native resources until reused or ended.

Compression streams wrap underlying streams and may buffer data. `finish()` persists final compressed bytes without closing the underlying stream, while `close()` generally finishes and closes. `resetState()` discards codec state but intentionally does not reset underlying stream position.

Native LZO/zlib compressors and decompressors hold native state and direct buffers. Their `end` and finalization behavior is a resource-management boundary; leaks or reuse after `end` can affect long-running daemons.

`SerializationFactory` persists configured serialization class lists in `Configuration`. Serialized data compatibility depends on both the selected `Serialization` implementation and the target class availability.

`Client`, `Server`, and `RPC.Server` maintain sockets, handler/client threads, call queues, connection counts, ping intervals, listener addresses, and per-call thread-local context. RPC metrics persist process-local rolling rates and publish them to Hadoop metrics/JMX until shutdown.

`RemoteException` persists a remote class name and message over the wire. Unwrapping behavior depends on local class availability and constructors, so the same remote failure can materialize differently on different clients.

`FileInputFormat` and `FileOutputFormat` store job configuration keys for input paths, filters, min split size, output path, compression flag, and codec class. They persist intent in `JobConf`, while actual file data and task output are persisted through the configured `FileSystem`.

`FileSplit` persists path, start offset, length, and host locations, allowing computed client-side split plans to be shipped to task trackers.

`Counters` persist grouped long values as part of job/task progress and history. Counter names and group display names are externally visible in logs, web UI, and job history.

`JobClient` state includes the JobTracker connection, filesystem handle used for staging, command-line configuration, and task output filter. Its job submission path persists job jar/configuration and split metadata into the JobTracker system directory.

## Dependencies and Integration Points

- Java platform dependencies include `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, `ByteBuffer`, `Serializable`, collections, enums, reflection, sockets, `SocketFactory`, servlet APIs for log-level servlet, and `java.util.zip` deflater/inflater classes.
- Hadoop configuration (`org.apache.hadoop.conf.Configuration`, `Configurable`, and `JobConf`) drives writable construction, codec registration, serialization selection, zlib settings, RPC ping intervals, MapReduce input/output paths, compression settings, and JobClient staging.
- Hadoop filesystem types (`FileSystem`, `Path`, `FileStatus`, `PathFilter`, and block location data) integrate with `FileInputFormat`, `FileOutputFormat`, `FileSplit`, and `JobClient.getFs`.
- Hadoop MapReduce types referenced in this chunk include `JobTracker`, `JobStatus`, `RunningJob`, `TaskReport`, `RecordReader`, `RecordWriter`, `Reporter`, `Mapper`, `OutputFormat`, `MRConstants`, and `DistributedCache`.
- Hadoop metrics integration appears through `org.apache.hadoop.metrics.Updater`, `MetricsTimeVaryingRate`, the RPC metrics subsystem, and JMX MBean exposure.
- Hadoop IPC integration depends on `Writable` request/response types, `VersionedProtocol`, protocol `versionID` fields, `RemoteException`, and server/client socket lifecycle.
- Compression integrates with native Hadoop code availability, zlib/lzo native libraries, Java gzip/deflate streams, codec suffix conventions, and MapReduce output compression configuration.
- Serialization integrates with Hadoop's `RawComparator` and with sort/shuffle paths where raw byte comparisons are used to avoid full object construction.
- Logging uses Apache Commons Logging and exposes runtime mutation through a CLI and servlet.

## Risks and Edge Cases

- The chunk starts mid-`Text` and ends mid-`JobClient` documentation; adjacent chunks are required for full class-level coverage of those two API entries.
- JDiff metadata omits method bodies. Exact byte layouts, synchronization internals, buffer ownership, codec reset behavior, RPC framing, and JobClient staging details require implementation-source review.
- `Text` and `UTF8` compatibility is sensitive to byte length versus array capacity. Callers that treat raw backing arrays as fully valid data can compare or serialize stale bytes.
- Strict versus replacement UTF-8 decoding changes whether malformed data fails fast or silently substitutes U+FFFD. Tests must pin both modes.
- `UTF8` is deprecated but still public. Removing or weakening it can break old serialized keys and user code from the Hadoop 0.18 era.
- `VersionedWritable` uses a single byte for versions and throws on mismatch. Classes that need backward-compatible migration must implement custom handling carefully around this gate.
- VInt/VLong encoding boundaries are subtle, especially negative values and first-byte size/sign decoding. Incompatibility here breaks Writables, Text lengths, counters, and many Hadoop wire formats.
- `WritableComparator` raw comparison must match object comparison exactly. Divergence causes MapReduce sort/group partitioning bugs that are hard to diagnose.
- Global registries in `WritableComparator`, `WritableFactories`, `WritableName`, and `CodecPool` can leak test state between cases and can be affected by duplicate registrations.
- `WritableUtils.cloneInto` documentation appears to reverse source/destination wording in the parameter text; callers should confirm implementation semantics before relying on the docs alone.
- Compression `finish`, `flush`, `close`, and `resetState` have distinct meanings. Calling them in the wrong order can produce truncated output, extra members, or stale decompressor state after seeking.
- `CompressionInputStream.resetState` assumes the underlying stream may be repositioned. Implementations that retain buffered compressed data after reset can corrupt split-based reads.
- Native LZO/zlib availability is environment-sensitive. Code must handle missing native libraries and fall back or fail explicitly.
- `LzoDecompressor.finalize` is a weak cleanup guarantee. Long-running daemons need explicit `end`/pool discipline to avoid native memory retention.
- `CodecPool` can hand out reused mutable compressor state. Returning a compressor before a stream has fully finished or reusing it without reset can cross-contaminate compressed data.
- `CompressionCodecFactory` suffix matching can be ambiguous for nested suffixes or unknown extensions. Codec registration order and file naming should be tested.
- Retry policies that suppress void failures or retry forever can hide outages or stall callers indefinitely if applied too broadly.
- `RetryProxy` dispatches by method name for policy maps; overloaded methods can share a name but require different retry behavior.
- Java serialization is marked experimental and depends on Java class compatibility/serialVersionUID. It is risky for durable cross-version data.
- `DeserializerComparator` allocates/deserializes during raw comparison; using it in high-volume sort paths can be much slower than a true raw comparator.
- RPC protocol version negotiation relies on protocol classes exposing `versionID` and implementations returning compatible versions. Incorrect versions cause `RPC.VersionMismatch` or silent incompatibility.
- `RemoteException.unwrapRemoteException` depends on local exception constructors and class availability. Missing classes degrade error specificity.
- `Client.call` parallel mode returns null for timed out or errored calls. Callers must not treat null as a successful null response.
- `Server.getRemoteIp` and `getRemoteAddress` return null outside valid RPC context or on error; authorization/audit code must handle that.
- `Server.setTimeout` is documented as no longer used, so callers relying on it for connection or request deadlines may get no effect.
- RPC metrics are sampled/interval-based. Tests and monitoring should distinguish instantaneous counts from last-interval averages/min/max.
- Runtime `LogLevel.Servlet` can mutate logging levels over HTTP; deployments need access control outside this API surface.
- `InputFormat.validateInput` is marked deprecated with guidance that `getSplits` can validate. Old callers may still rely on early validation behavior.
- `FileInputFormat` split computation must handle empty files, unsplittable compressed files, directories versus files, globbed paths, filters, block location lookups, and min split size bounds.
- `InputSplit.getLocations` affects data locality scheduling. Incorrect hostnames degrade performance or cause scheduler imbalance.
- `FileOutputFormat.checkOutputSpecs` must fail before job submission when output exists. Races with concurrent writers can still surface later.
- `Counters` names/display names are externally visible and serialized. Renaming groups/counters breaks history parsing, dashboards, and tests.
- `InvalidInputException` stores the provided problem list without copying; external mutation can change exception state after construction.
- `JobClient` submission crosses filesystem, distributed cache, split computation, job jar copying, RPC, and monitoring boundaries. Partial failures can leave staged files or submitted jobs with incomplete client state.
- Deprecated string-based `JobClient` and report APIs coexist with `JobID` overloads. Compatibility tests should cover both until old callers are dropped.

## Test Signals

Useful validation for this API surface should include:

- JDiff/API compatibility checks for every public/protected class, interface, constructor, method, field, exception, visibility flag, generic signature, deprecation marker, and nested type in this line range.
- `Text` tests for byte-range append, clear, read/write/skip, bytewise comparison, equality/hash, malformed UTF-8 strict and replacement decode, encode limits, validation, code-point traversal, and encoded-length calculation.
- `UTF8` compatibility tests against legacy serialized bytes, including skip, static read/write string helpers, raw comparator behavior, and deprecation-preserving API checks.
- `TwoDArrayWritable` read/write round trips with empty, rectangular, and ragged arrays plus declared value-class mismatch cases.
- `VersionedWritable` tests for matching version read/write and mismatch exception messages/string rendering.
- `VIntWritable`, `VLongWritable`, and `WritableUtils` tests at every encoding boundary: one-byte positive/negative values, multi-byte values, min/max int/long, sign/size decode, byte-array decode, and malformed/truncated inputs.
- `WritableComparator` tests proving raw byte comparison matches object comparison, plus registration/retrieval, key construction, primitive byte parsing, and hash byte behavior.
- `WritableFactories` and `WritableName` tests for synchronized registration, configured new instances, non-public Writable construction, aliases, unknown aliases, and registry isolation.
- `WritableUtils` tests for compressed byte/string arrays, string arrays, enum name round trips, display formatting, serialization clone/cloneInto, and `skipFully` short-skip failures.
- `CodecPool` tests for get/return/reuse/reset behavior, null returns, multiple codec types, and concurrent access.
- `CompressionCodecFactory` tests for configured codec class loading, defaults, extension selection, nested suffixes, `removeSuffix`, unknown file extensions, and diagnostic string output.
- Stream tests for `CompressionInputStream`/`CompressionOutputStream`: close/flush/finish order, reset after underlying seek, no leakage to raw stream reads/writes, and exception propagation.
- Compressor/decompressor contract tests for `setInput`, `needsInput`, dictionaries, finish/finished, zero-byte output cases, byte counters, reset/end, and reuse after pool return.
- Codec tests for `DefaultCodec`, `GzipCodec`, `LzoCodec`, built-in zlib, and native zlib/lzo availability paths. Include missing-native behavior and round trips over small, large, empty, and incompressible data.
- Zlib configuration tests for compression level, strategy, header mode, direct buffer size, and `ZlibFactory` class selection.
- Retry policy tests for try-once, suppress-void, retry forever with bounded harness, fixed/max/proportional/exponential sleep decisions, exception-specific maps, remote-exception maps, overloaded method names, and retry count increments.
- Serialization tests for configured `SerializationFactory` ordering, Writable serialization reuse, Java serialization compatibility, serializer/deserializer open-close lifecycle, and deserializer object reuse.
- Comparator tests for `DeserializerComparator` and `JavaSerializationComparator`, including invalid bytes and non-comparable Java-serialized objects.
- IPC client/server integration tests for single calls, parallel calls with timeout/error nulls, ping interval configuration, client stop behavior, server start/stop/join, listener address, socket bind errors, send buffer size, and per-call remote address context.
- RPC tests for proxy creation, wait-for-proxy retry, stopProxy resource cleanup, protocol version success and `VersionMismatch`, remote exception wrapping/unwrapping, server method dispatch, and parallel RPC calls.
- RPC metrics/JMX tests for queue and processing time updates, per-method metrics, interval sampling, min/max reset, open connection count, call queue length, and shutdown cleanup.
- LogLevel tests for command-line parsing and servlet GET behavior, with separate deployment tests for access controls.
- `ClusterStatus` Writable round trips and getter correctness for task trackers, running tasks, max capacities, and JobTracker state.
- `Counters` tests for group/counter lazy creation, enum and string lookup, increments, sum/incrAllCounters, iteration, serialization, compact string rendering, logging, and display-name stability.
- `DefaultJobHistoryParser` tests on representative job history files with tasks, attempts, counters, failures, and malformed records.
- `FileInputFormat` tests for input path setters/adders, glob expansion, filters, empty input, directories, invalid paths, splitability, min split size, split size computation, block index lookup, and deprecated `validateInput` behavior.
- `FileOutputFormat` tests for output path/work path/task path derivation, existing output rejection, compression flag/codec class configuration, and record writer integration.
- `FileSplit` tests for path/start/length/location serialization, zero-length splits, null/empty host arrays, and string rendering.
- `ID` tests for numeric comparison, read/write, `forName` parsing, malformed/null strings, equality/hash, and subclass compatibility.
- `InputFormat` and `InputSplit` contract tests ensuring split length/location data is honored by scheduling and record readers preserve record boundaries.
- Exception tests for message constructors, accumulated `InvalidInputException` messages, uncopied problem list behavior, and invalid job configuration surfacing.
- `IsolationRunner` tests with an isolated task directory fixture, missing arguments, missing files, and task failure propagation.
- `JobClient` integration tests for initialization/close, filesystem staging, submit by file and `JobConf`, `runJob` polling, job lookup, task reports by `JobID` and deprecated string IDs, cluster status, jobs-to-complete/all-jobs queries, task output filter config, default map/reduce capacity queries, system directory lookup, and cleanup after partial submission failure.
