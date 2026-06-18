# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.5.0.xml - subset-b-007237

## Scope

This chunk covers lines 30662-36701 of the Hadoop Common 3.5.0 JDiff XML API dump. It is API metadata rather than executable Java source. The slice starts inside the tail of `org.apache.hadoop.io.Text`, completes the remaining public `org.apache.hadoop.io` writable/serialization utility APIs, covers the public compression API families under `org.apache.hadoop.io.compress`, several small nested enum API dumps for bzip2/zlib/native IO/retry, erasure-code schema metadata, TFile public helpers, compatibility wrappers under `org.apache.hadoop.io.wrappedio`, and the beginning of the IPC package through `Client`, `Server`, and `ProcessingDetails.Timing`. It ends at the start of `org.apache.hadoop.metrics2.AbstractMetric`.

## Purpose

The XML records Hadoop Common's public binary/source API for compatibility checking. In this chunk, most APIs are core cross-cutting infrastructure:

- Writable encoding and raw comparison primitives used by Hadoop RPC, MapReduce sort/shuffle, filesystem metadata, and other binary protocols.
- Compression codec contracts, stream wrappers, codec lookup/pooling, and splittable codec behavior used by filesystems and input formats.
- Erasure coding and TFile public metadata helpers.
- Reflection-friendly wrapper classes that let downstream libraries use newer Hadoop filesystem/statistics APIs while still compiling against older Hadoop releases.
- IPC client/server entry points and observability hooks used by RPC engines, service authorization, metrics, call queues, and tests.

Because this is a JDiff file, the "control flow" is expressed by API contracts, constructor/method signatures, inheritance, exceptions, and documented lifecycle expectations rather than method bodies.

## Important APIs And Types

### `org.apache.hadoop.io` tail

- `Text` tail methods expose UTF-8 byte/string conversions and validation: `decode(byte[], int, int)`, `decode(byte[], int, int, boolean)`, `encode(String)`, `encode(String, boolean)`, `readString(DataInput[, int])`, `writeString(DataOutput, String[, int])`, `validateUTF8(byte[][, int, int])`, `bytesToCodePoint(ByteBuffer)`, `utf8Length(String)`, and `DEFAULT_MAX_LEN`. The API contract distinguishes replacement of malformed input from `CharacterCodingException`/`MalformedInputException` failures, and uses `DataInput`/`DataOutput` for wire persistence.
- `TwoDArrayWritable` is a `Writable` matrix wrapper with constructors for a value class and optional `Writable[][]`, plus `toArray`, `set`, `get`, `readFields`, and `write`.
- `VIntWritable` and `VLongWritable` are `WritableComparable` holders for zero-compressed variable-length integer encodings. Both expose no-arg/value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`.
- `VersionMismatchException` extends `IOException` and is thrown when a `VersionedWritable` stream version does not match the implementation version.
- `VersionedWritable` is an abstract `Writable` base with abstract `getVersion()`, plus concrete `write(DataOutput)` and `readFields(DataInput)` version checking.
- `Writable` defines the core Hadoop binary persistence contract: `write(DataOutput)` and `readFields(DataInput)`. Its documentation emphasizes that `readFields` must restore all fields written by `write`.
- `WritableComparable<T>` combines `Writable` with Java `Comparable<T>`.
- `WritableComparator` provides comparator registration and byte-level utilities. Important APIs include static `get(Class[, Configuration])`, static `define`, instance `newKey`, object and raw-byte `compare` overloads, `compareBytes`, `hashBytes`, primitive readers from byte arrays (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`), and `Configurable` methods `setConf`/`getConf`.
- `WritableFactories` and `WritableFactory` support factory registration for non-public writable types so `ObjectWritable` and other reflective paths can instantiate them.
- `WritableUtils` centralizes binary helper methods: compressed byte/string arrays, plain and compressed string arrays, display/debug byte dumps, serialization-based `clone`, deprecated `cloneInto`, VInt/VLong write/read/size/sign decoding, enum write/read, `skipFully`, `toByteArray`, and bounded `readStringSafely`.

### `org.apache.hadoop.io.compress`

- `CompressionCodec` is the central codec interface. It creates compression/decompression streams with or without explicit `Compressor`/`Decompressor` instances, exposes compressor/decompressor classes and factories, and declares a default filename extension.
- `BZip2Codec` implements `Configurable` and `SplittableCompressionCodec`. Its docs state it can choose native bzip2 or pure Java based on configuration, that compressor/decompressor argument overloads may be unsupported in pure-Java mode, and that split input uses the pure-Java path to align at block boundaries.
- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-based compressors/decompressors to Hadoop streams. The documented format stores an uncompressed block length followed by one or more length-prefixed compressed blocks.
- `CodecConstants` publishes default extension constants for default, bzip2, gzip, lz4, passthrough, snappy, and zstandard codecs.
- `CodecPool` leases and returns reusable `Compressor` and `Decompressor` instances. It also exposes leased compressor/decompressor counts, which are useful as leak test signals.
- `CompressionCodecFactory` constructs a codec registry from `Configuration`, supports static `getCodecClasses`/`setCodecClasses`, and resolves codecs by path, class name, short name, or class. It also has `removeSuffix` and a diagnostic `main`.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases with state reset and IO statistics hooks. Input streams additionally expose position/seek/seek-to-new-source methods; output streams expose `finish`, `flush`, `resetState`, and the wrapped `out`.
- `Compressor`, `Decompressor`, `DirectDecompressionCodec`, and `DirectDecompressor` define stateful compression primitives. The contracts expose input/dictionary management, byte counters, `finish`/`finished`, `needsInput`, `needsDictionary`, `reset`, `end`, `reinit(Configuration)`, and direct `ByteBuffer` decompression.
- `CompressorStream` and `DecompressorStream` are stream implementations around those stateful primitives, with protected buffers and `closed`/`eof` fields that matter for lifecycle correctness.
- `DefaultCodec` implements the standard deflate-style codec and direct decompression factory. `GzipCodec` extends it for gzip streams. `PassthroughCodec` implements `CompressionCodec` without transforming bytes and is documented as a way to disable decompression for configured extensions such as `.gz`.
- `SplittableCompressionCodec` and its nested `READ_MODE` enum define the split-aware compressed input contract. `SplitCompressionInputStream` tracks adjusted start/end offsets after a codec aligns a requested split to actual compressed-block boundaries.

### Compression nested enum packages

- `org.apache.hadoop.io.compress.bzip2.CBZip2InputStream.STATE` appears as public nested enum metadata with `values`/`valueOf`, representing decoder state labels.
- `org.apache.hadoop.io.compress.zlib.ZlibCompressor.CompressionHeader`, `ZlibDecompressor.CompressionHeader`, `ZlibCompressor.CompressionLevel`, `ZlibCompressor.CompressionStrategy`, and `BuiltInGzipDecompressor.GzipStateLabel` expose `values`/`valueOf`; the compression header enums also expose `windowBits()`.

### Erasure coding

- `ECSchema` is a final `Serializable` metadata holder for erasure-code schema parameters. Constructors accept an all-options map, `(codecName, numDataUnits, numParityUnits)`, or key parameters plus extra options. Accessors include `getCodecName`, `getExtraOptions`, `getNumDataUnits`, `getNumParityUnits`, plus `toString`, `equals`, and `hashCode`. Public keys are `NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, and `CODEC_NAME_KEY`.

### TFile

- `Compression.Algorithm` is an enum-like public nested type with abstract `createCompressionStream`, `createDecompressionStream`, and `isSupported`, plus compressor/decompressor leasing helpers, `getName`, shared `conf`, and `CONF_LZO_CLASS`.
- `MetaBlockAlreadyExists` and `MetaBlockDoesNotExist` are public `IOException` subclasses for TFile metadata block errors.
- `RawComparable` exposes byte range accessors `buffer`, `offset`, and `size`; comparisons are delegated to a `RawComparator`.
- `TFile` exposes static helper APIs `makeComparator(String)`, `getSupportedCompressionAlgorithms()`, and `main(String[])`, along with public constants `COMPRESSION_GZ`, `COMPRESSION_LZO`, `COMPRESSION_NONE`, `COMPARATOR_MEMCMP`, and `COMPARATOR_JCLASS`.
- `Utils` exposes TFile-local VInt/VLong encoding and decoding, string write/read helpers, and generic `lowerBound`/`upperBound` binary search utilities over lists with comparators.

### Native IO and retry enum fragments

- `NativeIO.Windows.AccessRight` exposes `values`, `valueOf`, and `accessRight()` for Windows access masks.
- `Errno` exposes POSIX/native errno enum metadata.
- `NativeIO.POSIX.SupportState` exposes `values`, `valueOf`, `getStateCode`, and `getMessage`.
- `RetryPolicy.RetryAction.RetryDecision` exposes enum metadata for retry/fail/failover style decisions.

### Serialization packages

- `JavaSerialization` accepts `Serializable` values and creates corresponding Hadoop `Serializer`/`Deserializer` instances.
- `JavaSerializationComparator<T>` extends `DeserializerComparator<T>` and compares serialized Java objects at byte-array offsets.
- `WritableSerialization` extends `Configured` and accepts `Writable` values, returning serializers/deserializers for Hadoop writables.
- `AvroReflectSerializable` is a marker interface.
- `AvroSerialization<T>` is the configured base for Avro serializers/deserializers, requiring schema, writer, and reader hooks, and publishing `AVRO_SCHEMA_KEY`.
- `AvroReflectSerialization` accepts reflect-serializable objects/packages, with `AVRO_REFLECT_PACKAGES`, and supplies Avro reflect schema/reader/writer.
- `AvroSpecificSerialization` accepts Avro `SpecificRecord` values and supplies specific Avro schema/reader/writer.

### Wrapped compatibility APIs

- `WrappedIO` is a final static facade for reflection-friendly access to newer filesystem APIs. It wraps bulk delete page size and delete calls, path and stream capability probing, `FileSystem.openFile(Path)` with optional policy/status/length/options, `FileSystem.getEnclosingRoot(Path)`, and `ByteBufferPositionedReadable` positioned read helpers.
- `WrappedStatistics` is a final facade around IOStatistics APIs. It can test object types, create/load/save/retrieve/aggregate `IOStatisticsSnapshot` values, serialize/deserialize JSON strings, expose counters/gauges/minimums/maximums/means maps, manage thread-level `IOStatisticsContext`, pretty-print statistics, and apply functions to valid snapshots.
- The package documentation explicitly says public classes here are intended for reflective loading by downstream libraries, and tests should themselves use reflection to guarantee that compatibility surface.

### `org.apache.hadoop.ipc`

- `CallerContext` is an immutable audit context with context/signature accessors, validity, equality/hash/string behavior, static thread-local `getCurrent`/`setCurrent`, and public string constants for client IP, port, id, call id, real user, and proxy user port.
- `Client` is the core IPC client and implements `AutoCloseable`. It constructs from a `Writable` value class, `Configuration`, and optional `SocketFactory`; manages async response retrieval (`getAsyncRpcResponse`, `getResponseFuture`), call id/retry state, external handlers, max async calls, ping/connect/RPC timeout configuration, synchronous/asynchronous mode, `nextCallId`, `call(...)` overloads, `stop`, `close`, and logging.
- `RPC.RpcKind` appears as a nested enum dump with `values` and `valueOf`.
- `Server` is the abstract IPC service. Constructors bind address/port, request class, handler/readers/queue sizing, configuration, server name, token secret manager, and optional port range configuration. Public/static APIs include logging exception filters, alignment context, protocol engine registration, invoker lookup, thread-local current server/call details, remote IP/port/address/user/protocol/client id lookup, call id/retry count/priority, slow RPC settings, bind helpers, metrics accessors, service ACL refresh, call queue refresh/queueing, auxiliary listeners, socket send buffer sizing, tracing, lifecycle `start`/`stop`/`join`, listener address queries, abstract modern `call(RPC.RpcKind, String, Writable, long)`, deprecated legacy `call(Writable, long)`, and operational counters/backoff/failover/queue/reader/max-idle/server-name accessors.
- `ProcessingDetails.Timing` appears as a nested enum dump with `values`/`valueOf` for RPC timing stages.

### `org.apache.hadoop.metrics2`

- The chunk starts `AbstractMetric`, an abstract `MetricsInfo` implementation with a protected `MetricsInfo` constructor, concrete `name`, `description`, protected `info`, and abstract `value()`. The class continues in the next chunk, so this report only covers the visible prefix.

## Control Flow And Lifecycle Contracts

- Writable flow is consistently `write(DataOutput)` followed by `readFields(DataInput)` on a reused or newly constructed object. Versioned writables add a leading version byte and throw `VersionMismatchException` during `readFields` if the stream version is incompatible.
- Raw comparison flow in `WritableComparator` favors byte-array comparison for performance-sensitive sorting. Object comparison can instantiate keys through registered factories, while optimized subclasses can override the byte-level compare path and use static primitive readers.
- Variable-length integer flow is shared across `VIntWritable`, `VLongWritable`, `WritableUtils`, `WritableComparator`, and TFile `Utils`: a first byte encodes sign and encoded width; subsequent non-zero bytes are stored high-order first.
- Compression flow is codec -> optional pooled compressor/decompressor -> stream wrapper -> `finish`/`close`/`resetState` -> return pooled primitive. Direct decompression bypasses heap byte arrays through `ByteBuffer`.
- Splittable compression flow gives codecs a requested compressed start/end range and a `READ_MODE`; codecs may adjust boundaries and expose final values through `SplitCompressionInputStream.getAdjustedStart()`/`getAdjustedEnd()`.
- `CodecPool` creates shared mutable resource flow: callers lease compressors/decompressors and must return them. `getLeasedCompressorsCount` and `getLeasedDecompressorsCount` are direct observability for resource leaks.
- `WrappedIO` and `WrappedStatistics` convert availability-sensitive APIs into stable reflective helper calls. Several methods deliberately convert checked `IOException` into `UncheckedIOException` or boolean false for compatibility.
- IPC client flow is construct client -> configure call id/retry/async/thread-local response state -> invoke `call` against a `ConnectionId` -> read a `Writable` response or async future -> `stop`/`close`. Static asynchronous mode and response future APIs imply thread-local/global state that must be reset carefully in tests.
- IPC server flow is construct/bind -> optionally register protocol engines and configure ACLs/call queues/tracing/slow-RPC logging -> `start` service threads -> queue and dispatch calls to the abstract `call(RpcKind, protocol, param, receiveTime)` -> report metrics and state -> `stop` and optionally `join`.

## State And Persistence Behavior

- Binary persistence is dominated by Hadoop's `Writable` protocol and Java `DataInput`/`DataOutput`. Public API stability here matters because the same bytes are used in files, RPC requests/responses, and sorted keys.
- `Text` and `WritableUtils` both serialize strings with explicit lengths and UTF-8 bytes; `readStringSafely` adds length bounds before consuming the payload.
- Compressed byte arrays/strings in `WritableUtils` and block compression streams introduce secondary persistence formats inside the writable stream. Block compression stores uncompressed sizes and length-prefixed compressed chunks.
- `ECSchema` is `Serializable` and map-backed enough for schema options to persist across configuration or RPC/file metadata boundaries.
- Avro serialization relies on schemas from configuration (`AVRO_SCHEMA_KEY`) or reflected/specific Avro types. Changes to accepted classes, schema discovery, or writer/reader types are compatibility-sensitive.
- `WrappedStatistics` explicitly persists IO statistics snapshots as JSON through Hadoop `FileSystem` paths and can reload them as serializable snapshots.
- IPC server/client state includes thread-local current call/server context, call ids, retry counts, async futures, caller context, metrics objects, call queue state, listener sockets, auxiliary listener sockets, slow RPC flags, service ACLs, and secret manager integration. These are runtime state surfaces, not file persistence, but they are observable and API-stable.

## Dependencies And Integration Points

- Core Java dependencies: `java.io`, `java.nio.ByteBuffer`, `java.nio.charset`, `java.net`, `java.util`, `java.util.concurrent.CompletableFuture`, `java.util.concurrent.atomic.AtomicBoolean`, and enum/serialization infrastructure.
- Hadoop dependencies: `Configuration`, `Configured`, `Writable`, `RawComparator`, `FileSystem`, `FSDataInputStream`, `FileStatus`, `Path`, filesystem statistics APIs, security `UserGroupInformation`, token `SecretManager`/`TokenIdentifier`, service authorization `PolicyProvider`/`ServiceAuthorizationManager`, RPC `AlignmentContext`, `RPC.RpcInvoker`, tracing `Tracer`, and IPC metrics classes.
- External dependencies: SLF4J logging, Avro `Schema`, `DatumReader`, `DatumWriter`, `SpecificRecord`, zlib/bzip2 native or Java codecs, and optional LZO class support in TFile compression.
- Integration-sensitive public packages in this chunk are explicitly used by downstream projects: `org.apache.hadoop.ipc` package docs warn that changes to `RPC` and `RpcEngine` signatures break other ASF projects, including shaded/unshaded protobuf deployments.

## Risks And Compatibility Concerns

- This XML is generated API metadata. It is useful for signature compatibility but cannot prove method-body behavior, exception ordering, synchronization correctness, resource cleanup, or thread-local cleanup.
- `Writable` and variable-length integer encodings are long-lived wire/file formats. Any signature or behavior drift in read/write, length bounds, sign decoding, or byte order can corrupt persisted data or break RPC compatibility.
- `Text` malformed UTF-8 handling has two modes. Replacing invalid bytes vs throwing `MalformedInputException` affects security and input validation paths.
- `WritableFactories` and `WritableComparator` rely on reflection/configuration and global registrations. Factory or comparator registration changes can alter deserialization and sort behavior process-wide.
- Compression APIs are stateful and resource-backed. Leaked compressors/decompressors, incorrect `reset`/`end`/`return*` behavior, or direct `ByteBuffer` position mishandling can cause native memory leaks, corrupted streams, or bad split boundaries.
- `BZip2Codec` has divergent native and pure-Java behavior, including documented unsupported compressor/decompressor overloads in pure-Java mode and split support only through pure Java. Tests must exercise both configuration branches where available.
- `PassthroughCodec` intentionally disables decompression by extension. Registering it broadly can silently pass compressed bytes to callers expecting decompressed data.
- Wrapped compatibility facades trade compile-time type safety for reflection-friendly APIs. Wrong object types are documented to produce `IllegalArgumentException`, `ClassCastException`, `UncheckedIOException`, or false capability probes; downstream callers may depend on those exact failure modes.
- IPC `Client`/`Server` APIs expose global/thread-local state, async state, call ids that wrap back to zero, service ACL refresh, failover/backoff behavior, and metrics/test accessors. Concurrency bugs or signature changes here have high blast radius.
- Deprecated APIs remain part of the API dump, including `WritableUtils.cloneInto`, `Client.getTimeout`, and legacy `Server.call(Writable, long)`. Removal or behavior changes can break older downstream tests and integrations.
- The chunk ends mid-`AbstractMetric`, so metrics API conclusions are incomplete until the next chunk is merged.

## Test Signals

- JDiff/API compatibility tests should ensure the signatures, visibility, deprecation text, thrown checked exceptions, static/final/abstract flags, and field visibility in this XML remain stable unless an intentional compatibility change is recorded.
- Writable round-trip tests should cover `Text`, `TwoDArrayWritable`, `VIntWritable`, `VLongWritable`, `VersionedWritable`, factories, and `WritableUtils` string/array/compressed helpers, including max-length and malformed UTF-8 cases.
- Raw comparator tests should compare object-order and byte-order paths, primitive byte readers, VInt/VLong readers, custom `WritableComparator.define`, and configured comparator construction.
- Compression tests should cover codec factory lookup by extension/name/class, configured codec lists, pool lease/return counters, compressor/decompressor reset/end behavior, block stream round trips, direct decompressor `ByteBuffer` position changes, and splittable bzip2 adjusted start/end values.
- Codec-specific tests should include bzip2 native vs pure-Java configuration, gzip/default direct decompression, passthrough extension override, and TFile compression algorithm support detection.
- Serialization tests should cover Java serialization acceptance, writable serialization acceptance, Avro reflect package configuration, Avro specific record schemas, and comparator behavior on serialized byte slices.
- WrappedIO tests should intentionally use reflection to call the public methods, as the package docs require. Cases should cover unsupported bulk delete, invalid paths outside base, capability false-on-IO behavior, `openFile` options/status/length wiring, and ByteBuffer positioned-read detection through wrapped streams.
- WrappedStatistics tests should cover valid and invalid snapshot objects, JSON save/load/from-string/to-string, aggregate behavior, thread context set/reset/snapshot, and map accessor stability for counters/gauges/min/max/means.
- IPC tests should exercise sync and async `Client.call`, `CompletableFuture` retrieval, call id wrapping/non-negative masking, retry count propagation, connection timeout/ping/RPC timeout configuration, fallback-to-simple-auth flag behavior, and close/stop idempotence.
- IPC server tests should verify bind error clarity, port-range binding, service ACL refresh paths, call queue refresh, auxiliary listener addresses, metrics handles, slow-RPC flag/threshold, connection/drop/queue counters, client backoff/failover settings, and deprecated legacy `call` delegation to the modern abstract call path.
