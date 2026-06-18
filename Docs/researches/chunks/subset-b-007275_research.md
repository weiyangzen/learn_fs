# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.18.2.xml lines 12397-18635

## Scope

This chunk is a generated JDiff API snapshot for Hadoop 0.18.2, not executable implementation source. It starts in the middle of `org.apache.hadoop.io.Text` and ends inside the long class documentation for `org.apache.hadoop.mapred.JobClient`, so adjacent chunks are required for whole-class conclusions about those two APIs. Within this range the XML records public/protected API compatibility metadata: packages, class/interface names, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, synchronization/static/final flags, deprecation text, and Javadoc contracts.

The covered surface spans Hadoop's classic serialization layer (`org.apache.hadoop.io`), compression codecs and native codec adapters (`org.apache.hadoop.io.compress`, `compress.lzo`, `compress.zlib`), retry and serialization frameworks, IPC/RPC APIs and metrics, runtime log-level controls, and the opening of the old `org.apache.hadoop.mapred` MapReduce client/input/output APIs.

## Purpose and Major API Surface

The `org.apache.hadoop.io` section covers core Writable types and helpers. The visible tail of `Text` documents byte-backed UTF-8 text mutation, clearing, bytewise comparison, serialization with zero-compressed length, string encode/decode, UTF-8 validation, code point traversal, and encoded length calculation. `Text.Comparator` and `UTF8.Comparator` provide raw byte comparators for sorted data paths. `TwoDArrayWritable`, deprecated `UTF8`, `VersionedWritable`, `VersionMismatchException`, `VIntWritable`, and `VLongWritable` define serializable value containers and version checks.

`Writable` and `WritableComparable` are the serialization and key-comparison contracts used by classic MapReduce keys and values. `WritableComparator` is the raw comparison bridge used by sort-heavy paths, with static helpers for lexicographic byte comparison, byte-array primitive decoding, and vint/vlong decoding. `WritableFactories`, `WritableFactory`, and `WritableName` add factory and class-name alias registries for constructing or renaming Writable classes without breaking persisted data. `WritableUtils` centralizes compressed byte/string arrays, writable cloning through serialization buffers, vint/vlong encoding, enum serialization, and exact skip behavior.

The compression API defines reusable codec infrastructure. `CodecPool` pools compressors and decompressors. `CompressionCodec` is the common stream factory contract for output/input streams, compressor/decompressor type discovery, instance creation, and default file extension. `CompressionCodecFactory` reads configured codec classes, maps filename extensions to codecs, removes suffixes, and exposes a command-line entry point. `CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with reset/finish behavior, while `Compressor` and `Decompressor` define stateful streaming engines with input buffers, dictionaries, byte counters, finish/reset/end lifecycle, and compress/decompress calls.

Concrete compression classes include `DefaultCodec`, `GzipCodec`, `GzipCodec.GzipInputStream`, `GzipCodec.GzipOutputStream`, and `LzoCodec`. The LZO and zlib packages expose native-aware engines: `LzoCompressor`, `LzoDecompressor`, their `CompressionStrategy` enums, `BuiltInZlibDeflater`, `BuiltInZlibInflater`, `ZlibCompressor` with `CompressionLevel`, `CompressionStrategy`, and `CompressionHeader`, `ZlibDecompressor` with `CompressionHeader`, and `ZlibFactory` for selecting native or built-in compressor/decompressor classes.

The retry API contains immutable retry policy contracts and proxy construction. `RetryPolicies` exposes constants for try-once/fail, try-once/do-not-fail for void methods, and retry-forever, plus factory methods for fixed sleep, time-bounded retry, proportional sleep, exponential backoff, exception-specific policies, and remote-exception-specific policies. `RetryPolicy.shouldRetry(Exception, int)` decides retry, silent non-failure, or rethrow. `RetryProxy` builds dynamic proxies using either one policy for all methods or a method-name-to-policy map.

The serializer API abstracts Hadoop object encoding beyond Writable. `Serializer` and `Deserializer` are stateful stream-bound contracts that must not buffer across calls because other producers/consumers may share the stream. `Serialization<T>` pairs serializers and deserializers with an `accept(Class)` check. `SerializationFactory` loads implementations from the `io.serializations` configuration key. `WritableSerialization` delegates to `Writable.write` and `readFields`; `JavaSerialization` and `JavaSerializationComparator` support experimental Java `Serializable` objects; `DeserializerComparator` compares raw bytes by deserializing objects before using the normal comparator path.

The IPC/RPC section covers old Hadoop RPC plumbing. `Client` sends single Writable calls to an address, authenticated calls with `UserGroupInformation`, and parallel calls to multiple addresses, with a configurable ping interval and a `stop()` lifecycle. `RemoteException` carries remote exception class names and can unwrap to matching `IOException` types or construct wrapped exceptions by class name. `RPC` builds client proxies for `VersionedProtocol`, waits for proxies, stops proxies, performs parallel reflective calls, and constructs `RPC.Server` instances. `RPC.Server` dispatches Writable RPC calls to a protocol implementation. `RPC.VersionMismatch`, `Server`, and `VersionedProtocol` define protocol version checking, server lifecycle/binding/thread metrics, remote address context, and call dispatch.

`org.apache.hadoop.ipc.metrics` exposes `RpcMetrics` and `RpcMgtMBean`. These publish queue time, processing time, method-level metrics, open connection count, call queue length, and min/max reset behavior through Hadoop metrics and JMX. `org.apache.hadoop.log.LogLevel` and `LogLevel.Servlet` provide command-line and servlet paths for changing log levels at runtime.

The `org.apache.hadoop.mapred` section starts the classic MapReduce API. `ClusterStatus` is a Writable snapshot of task tracker count, running maps/reduces, maximum map/reduce capacity, and `JobTracker.State`. `Counters`, `Counters.Counter`, and `Counters.Group` represent synchronized named counters grouped by enum class or string group, with serialization, iteration, increments, sum, logging, compact string output, display names, localization hooks, and deprecated id-based counter access. `DefaultJobHistoryParser` populates a `JobHistory.JobInfo` model from history files on a `FileSystem`.

MapReduce file I/O APIs include `FileAlreadyExistsException`, abstract `FileInputFormat<K,V>`, abstract `FileOutputFormat<K,V>`, `FileSplit`, `ID`, `InputFormat<K,V>`, and `InputSplit`. `FileInputFormat` handles path configuration, optional path filtering, listing input status, validation, split calculation, block-location lookup, and splitability decisions before delegating records to subclasses' `RecordReader`. `FileOutputFormat` handles output compression settings, output codec class selection, output path/work path/task output path calculation, output-spec validation, and subclass `RecordWriter` construction. `FileSplit` serializes path/start/length/locations, while `ID` is a WritableComparable integer identity base with parsing and static read helpers.

The chunk closes with MapReduce validation and client entry points: `InvalidFileTypeException`, `InvalidInputException`, `InvalidJobConfException`, `IsolationRunner`, and a partial `JobClient`. `JobClient` implements `MRConstants` and `Tool`, constructs against default or explicit `JobTracker` addresses, initializes/closing client resources, returns the filesystem used for job staging, submits jobs from a file or `JobConf`, queries `RunningJob` handles, map/reduce `TaskReport`s, cluster status, running/submitted jobs, default map/reduce capacity, system directory, task output filters, `runJob`, `run`, and `main`.

## Control Flow and Behavioral Contracts

The XML has no executable control flow, but the Javadoc captures intended API flow. Writable values use a strict `write(DataOutput)` and `readFields(DataInput)` protocol, and implementations are expected to reuse existing object storage during deserialization where possible. Sort paths may compare by object deserialization or by optimized raw byte comparators; optimized comparators must preserve natural ordering semantics expected by `WritableComparable`.

Text serialization uses UTF-8 bytes with zero-compressed length prefixes. Decode methods can either replace malformed input with U+FFFD or throw `MalformedInputException` through the `CharacterCodingException` path. `bytesToCodePoint(ByteBuffer)` advances the buffer position and changes any mark, so callers cannot treat it as a pure inspection helper.

Compression flow is stateful and lifecycle-driven. Codecs create streams and optionally accept pooled compressors/decompressors. Compressors receive input with `setInput`, report `needsInput`, can accept dictionaries, are finished via `finish`, emit bytes through `compress`, and are reset or ended. Decompressors mirror that lifecycle and can require dictionaries. `CodecPool` requires borrowers to return compressors/decompressors so native resources and buffers are reusable.

Native compression selection is conditional. LZO APIs expose `isNativeLzoLoaded`; zlib exposes `ZlibFactory.isNativeZlibLoaded` plus compressor/decompressor class selection. Built-in zlib wrappers adapt `java.util.zip.Deflater` and `Inflater` to Hadoop's `Compressor` and `Decompressor` interfaces. Native engines have direct buffer sizes, synchronized mutation methods, byte counters, and explicit or finalizer-assisted cleanup.

Retry flow is proxy-mediated. A failed proxied method calls `RetryPolicy.shouldRetry`, passing the exception and retry count. The policy may return true to retry, false to suppress failure for void methods, or throw to stop retrying. Method-specific proxy maps default to `TRY_ONCE_THEN_FAIL` when no policy is configured for a method.

Serializer flow is stream-bound: `open(stream)`, repeated `serialize` or `deserialize`, then `close()`. Deserializers may mutate a supplied non-null instance to avoid allocation; serializers/deserializers must not buffer because other code may read or write the same stream between calls.

IPC flow uses Writable request/response values for low-level `Client` calls and Java interface proxies for `RPC`. Protocols must use primitive, `String`, `Writable`, `void`, or arrays of those types, and methods should throw only `IOException`. RPC server instances expose current server and remote address context during call handling, while versioned protocols allow client/server version mismatch detection.

MapReduce job submission flow is documented in the partial `JobClient` class: validate input and output specs, compute `InputSplit`s, set up `DistributedCache` accounting, copy the job jar and configuration to the distributed filesystem system directory, then submit to the `JobTracker` and optionally monitor status. `JobClient.runJob` submits and polls until completion.

File input flow starts with configured input paths and optional `PathFilter`, lists `FileStatus` entries, validates non-empty inputs, computes split sizes from requested split count, min split size, and block size, locates block indexes, and creates `InputSplit`s for `RecordReader`s. `isSplitable` lets subclasses prevent splitting, especially for stream-compressed files. File output flow checks output specs, rejects existing outputs unless policy allows overwrite, configures optional compression, and computes task/work output paths for writers.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent compatibility metadata. Runtime persistence described here belongs to the APIs it documents.

Writable, Text, UTF8, versioned writable, vint/vlong writable, counters, cluster status, file splits, and IDs persist binary state through `DataInput`/`DataOutput`. Compatibility depends on stable field ordering, length encodings, class names or registered aliases, and read/write symmetry. `WritableName` aliases explicitly exist to keep old files readable after class renames.

Compression state includes input buffers, dictionaries, finish flags, native handles, direct buffers, byte counters, codec configuration, and pooled compressor/decompressor objects. Incorrect lifecycle management can leak native resources, contaminate future pooled uses, or produce truncated output when `finish()`/`close()` is skipped.

Retry state is primarily immutable policy configuration plus per-call retry counts inside proxy invocation. Serializer/deserializer state is bound to open streams and may reuse object instances. `SerializationFactory` depends on the process configuration key `io.serializations`.

IPC/RPC state includes client connection threads, ping interval configuration, socket factories, UGI tickets, server listener sockets, handler thread counts, call queues, remote address context, protocol versions, and metrics/JMX registries. `Client.stop`, `RPC.stopProxy`, and `Server.stop/join` are lifecycle boundaries.

MapReduce state includes job configuration, staged job files in the JobTracker system directory, job IDs, running job handles, task reports, cluster capacity snapshots, counters, history log parsing results, configured input/output paths, output compression settings, task output filters, and task-local isolation directories. File input and output APIs interact with `FileSystem` for listing, block locations, existence checks, and output directory/work path creation.

## Dependencies and Integration Points

The serialization layer depends on `java.io.DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `IOException`, NIO buffers and charset exceptions, Java reflection/class loading, `Configuration`, and Hadoop comparator/sort users. Its direct consumers include MapReduce keys/values, SequenceFile sorting, ObjectWritable-style dynamic construction, and RPC Writable payloads.

Compression integrates with Java streams, `java.util.zip`, Hadoop `Configuration`, `Configurable`, native libraries for LZO/zlib, codec configuration keys, and file formats that infer compression from filename suffixes. MapReduce file output integrates with `CompressionCodec` to compress job outputs.

Retry and RPC integrate through dynamic proxies, `VersionedProtocol`, `UserGroupInformation`, socket factories, `InetSocketAddress`, reflection `Method`, `RemoteException`, and Hadoop metrics. `RetryPolicies.retryByRemoteException` is specifically designed for exception names transported across RPC boundaries.

MapReduce APIs integrate with `JobConf`, `JobTracker`, `RunningJob`, `JobID`, `TaskReport`, `JobStatus`, `DistributedCache`, `FileSystem`, `Path`, `FileStatus`, `BlockLocation`, `PathFilter`, `RecordReader`, `RecordWriter`, `Reporter`, `Progressable`, `Mapper`, `MRConstants`, `Tool`, and `JobHistory.JobInfo`.

Compatibility tooling depends on the exact XML signatures and attributes in this source file. Public/protected signature changes, exception list changes, deprecation text changes, field additions/removals, or documentation contract edits in these APIs affect JDiff comparisons for Hadoop 0.18.2.

## Risks and Compatibility Notes

This chunk is partial at both ends. It should not be used alone to summarize all of `Text` or all of `JobClient`.

Serialization compatibility is high risk. Changing Writable field order, vint/vlong encoding, Text length encoding, UTF-8 replacement behavior, Writable class names, comparator ordering, or counter binary formats can break persisted data, sorted shuffle output, RPC payloads, and historical MapReduce data.

Raw comparators are performance-critical and correctness-critical. A comparator that disagrees with object `compareTo`, mishandles offsets/lengths, or misreads variable-length integers can corrupt sort order. `DeserializerComparator` is simpler but can be too slow for compare-heavy paths.

Compression lifecycle is easy to misuse. Pooled compressor/decompressor instances must be reset and returned; native codecs may be unavailable; `finish`, `flush`, `close`, and `end` have distinct resource and stream-completeness semantics; finalizer cleanup on decompressor classes is not a reliable primary lifecycle.

Retry policies can duplicate side effects. Retrying non-idempotent RPC or filesystem/job operations may submit work twice or mutate state multiple times. `TRY_ONCE_DONT_FAIL` can hide failures for void methods, while `RETRY_FOREVER` can hang callers when failures are permanent.

RPC compatibility depends on protocol versions, allowed parameter/return types, IOException-only method contracts, and remote exception class names. Remote exception unwrapping by class name can fail when classes are absent or constructors do not match.

MapReduce file input/output behavior has operational edge cases. Input validation may aggregate multiple path problems, splitability decisions affect task parallelism, stream-compressed files should not be split, output directories must be checked before job execution, and configured path strings/comma-separated paths need stable parsing.

Counters are synchronized mutable state with deprecated id-based access. Compatibility with old serialized counter groups and display/localized names must be preserved while newer string-name access is preferred.

## Test Signals

JDiff validation should confirm the XML remains well-formed and preserves all class/interface boundaries in this line range, including the partial `Text` tail and partial `JobClient` entry. API compatibility checks should cover method signatures, constructors, fields, visibility, static/final/synchronized flags, exceptions, generic type strings, implemented interfaces, and deprecation text.

Writable tests should round-trip `Text`, `UTF8`, `TwoDArrayWritable`, `VersionedWritable` subclasses, `VIntWritable`, `VLongWritable`, counters, cluster status, file splits, and IDs through `DataOutput`/`DataInput`. Comparator tests should compare object ordering against raw byte ordering for Text/UTF8/vint/vlong-backed data and validate byte primitive readers.

UTF-8 tests should cover malformed byte replacement versus exception behavior, range decode, encode buffer limits, validation failures, code point traversal side effects on `ByteBuffer.position`, and encoded length calculations.

Compression tests should cover codec factory registration by configuration and suffix lookup, default/gzip/lzo/zlib stream round trips, pooled compressor/decompressor borrow/reset/return, native-library unavailable paths, dictionary and finish behavior, byte counters, resetState, close/flush semantics, and zlib built-in fallback.

Retry tests should verify fixed, time-bounded, proportional, exponential, exception-specific, remote-exception-specific, try-once, silent-void, and retry-forever policies with bounded harnesses. Proxy tests should ensure method-specific defaults and exception propagation match the policy contract.

Serialization tests should load serializations from `io.serializations`, select Writable versus Java serialization correctly, reuse supplied deserialization objects when supported, avoid buffering across shared streams, and compare serialized objects through `DeserializerComparator` and `JavaSerializationComparator`.

IPC/RPC tests should exercise single and parallel Writable client calls, calls with UGI tickets, proxy creation and stop, wait-for-proxy behavior, protocol version mismatch reporting, remote exception unwrap cases, server bind/start/stop/join, remote address context, call queue metrics, processing/queue time metrics, and JMX reset behavior.

MapReduce tests should cover `ClusterStatus` writable round trips, counter increments/sums/serialization/compact strings/localized display names, history parser population from a filesystem-backed log, `FileInputFormat` path parsing/filtering/listing/validation/splitting/block-index calculation, unsplittable compressed inputs, `FileOutputFormat` output path validation/compression codec selection/task work paths, `FileSplit` serialization and locations, `ID` compare/parse/read behavior, aggregated invalid input exceptions, and `JobClient` submit/query/report/status/runJob flows against a controlled or mocked JobTracker.
