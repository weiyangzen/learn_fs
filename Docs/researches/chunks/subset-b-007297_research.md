# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.1.xml lines 12393-18672

## Scope

This chunk is a generated JDiff public API snapshot for Hadoop 0.19.1, not Java implementation source. The range starts immediately after `org.apache.hadoop.io.SequenceFile.Sorter.RawKeyValueIterator`, covers the rest of a large part of `org.apache.hadoop.io`, all visible compression/retry/serializer APIs in the range, the Hadoop IPC/RPC API surface, RPC metrics/JMX interfaces, runtime log-level control, and ends inside the opening part of `org.apache.hadoop.mapred.ClusterStatus`.

The XML records compatibility metadata: packages, classes/interfaces, inheritance, implemented interfaces, constructors, methods, parameters, declared exceptions, fields, visibility, static/final/abstract/synchronized/native flags, deprecation notes, and embedded Javadocs. Research below is based on those signatures and docs. This is a line-bounded chunk: the containing `org.apache.hadoop.io` package began before this range, `SequenceFile` began before this range, and `ClusterStatus` continues after this range.

## Purpose and Major API Surface

The opening `org.apache.hadoop.io` section is the core serialization and sequence-file API surface. `SequenceFile.Sorter.SegmentDescriptor` models a merge segment with file offset, length, and `Path`; it implements `Comparable`, reads raw keys and raw values, exposes the stored raw key as a `DataOutputBuffer`, can perform sync checks, can preserve or delete input files, and has overridable cleanup semantics. `SequenceFile.ValueBytes` abstracts raw sequence-file value bytes, with methods to write uncompressed or compressed bytes and report stored size. `SequenceFile.Writer` writes sequence-format key/value files over a `FileSystem` and `Path`, exposes key/value classes and compression codec, supports explicit sync points, synchronized close and append methods, raw append, current synchronized output length, and protected serializers for keys and compressed/uncompressed values.

`SetFile` is a `MapFile` specialization for key-only sets. `SetFile.Reader` seeks, iterates, and resolves matching `WritableComparable` keys. `SetFile.Writer` appends strictly increasing keys, supports element-class or comparator construction, accepts `SequenceFile.CompressionType`, and preserves a deprecated constructor that lacks a `Configuration`.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes the standard sorted-map view operations (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `entrySet`, `keySet`, `values`) plus mutators and `Writable` serialization through `readFields` and `write`. `Stringifier<T>` is a closeable object/string conversion contract with `toString`, `fromString`, and `close`.

`Text` is the main mutable UTF-8 string type, extending `BinaryComparable` and implementing `WritableComparable<BinaryComparable>`. It exposes byte storage access, byte length, Unicode scalar lookup by byte position, substring search, setters from `String`, byte arrays, and other `Text` values, appending, clearing, string conversion, `Writable` read/write, static string read/write helpers, static UTF-8 decode/encode helpers, UTF-8 validation, code-point extraction, and UTF-8 length calculation. `Text.Comparator` is an optimized raw `WritableComparator`.

`TwoDArrayWritable` serializes two-dimensional arrays of a fixed `Writable` value class. `UTF8` is the deprecated predecessor to `Text`, with comparable byte/string storage, `WritableComparable` methods, static UTF-8 helpers, and `UTF8.Comparator`. `VersionedWritable` adds version checking to `Writable` implementations via abstract `getVersion`, and `VersionMismatchException` reports mismatched byte versions.

`VIntWritable` and `VLongWritable` are mutable variable-length encoded integer/long `WritableComparable` types with set/get, read/write, equality/hash, comparison, and string conversion. `Writable` defines Hadoop's binary serialization contract, and `WritableComparable<T>` combines `Writable` with Java `Comparable<T>`.

`WritableComparator` is the central raw comparator registry and byte-level comparison utility. It constructs comparators for `WritableComparable` classes, can instantiate keys, compares either serialized byte slices or deserialized objects, registers optimized comparators, and exposes byte parsing helpers for unsigned short, int, float, long, double, vint, and vlong. `WritableFactories` maps classes to `WritableFactory` instances and creates new `Writable` instances with optional `Configuration`. `WritableName` maps writable implementation classes to stable aliases and back. `WritableUtils` provides compressed byte/string array IO, string array IO, display helpers, deep clone/cloneInto by serialization, variable-length integer/long encoding and decoding, enum read/write, `skipFully`, and conversion of multiple writables to a byte array.

The `org.apache.hadoop.io.compress` section defines Hadoop's stream compression abstraction. `CompressionCodec` creates input/output compression streams with or without pooled `Compressor`/`Decompressor` instances, reports compressor/decompressor classes, constructs compressor/decompressor instances, and gives a default file extension. `CodecPool` rents and returns reusable compressor/decompressor objects. `CompressionCodecFactory` discovers configured codec classes, maps file suffixes to codecs, removes suffixes, exposes codec classes for configuration, has a diagnostic `main`, and logs through Commons Logging.

`CompressionInputStream` and `CompressionOutputStream` are base wrappers over `InputStream` and `OutputStream` with `resetState`, plus close/flush/read/write/finish behavior as applicable. `Compressor` and `Decompressor` are state-machine interfaces for setting input/dictionaries, testing need for input or dictionaries, reporting bytes read/written, finishing, compressing/decompressing byte slices, resetting reusable state, and ending native resources.

`BZip2Codec`, `DefaultCodec`, `GzipCodec`, `LzoCodec`, and `LzopCodec` are codec implementations. `DefaultCodec` is `Configurable`; `GzipCodec` adds gzip-specific nested input/output streams; `LzoCodec` and `LzopCodec` expose native LZO availability and lzop container behavior. `LzopCodec.LzopDecompressor` handles lzop headers and data/compressed checksum verification, while `LzopInputStream` and `LzopOutputStream` read/write lzop headers around block compressor streams.

`org.apache.hadoop.io.compress.bzip2` exposes pure-Java bzip2 building blocks. `BZip2Constants` defines block-size, Huffman, run marker, selector, and overshoot constants. `BZip2DummyCompressor` and `BZip2DummyDecompressor` satisfy the generic compressor interfaces for stream wrappers that do their own work. `CBZip2InputStream` and `CBZip2OutputStream` implement bzip2 stream decoding/encoding without the file header bytes; output includes block-size selection, Huffman code-length generation, finish/close/flush, and many algorithm constants.

`org.apache.hadoop.io.compress.lzo` exposes native LZO compressor/decompressor classes and compression-strategy enums. Both report native availability and native library version. The compressor follows the generic compressor state machine; the decompressor adds dictionary requirements and a `finalize` cleanup hook. `org.apache.hadoop.io.compress.zlib` provides built-in `Deflater`/`Inflater` adapters, native-capable `ZlibCompressor` and `ZlibDecompressor`, enum types for compression header, compression level, and compression strategy, and `ZlibFactory` selection between native zlib and built-in Java implementations.

`org.apache.hadoop.io.retry` defines retry policy construction and dynamic retry proxies. `RetryPolicies` exposes constants for fail, ignore, and forever-retry behavior plus factories for fixed-sleep retry by count or maximum time, proportional sleep, exponential backoff, retry-by-exception, and retry-by-remote-exception. `RetryPolicy.shouldRetry(Exception, int)` decides whether another attempt should run or throws. `RetryProxy.create` wraps an implementation behind a Java proxy using either one policy or a method-name-to-policy map.

`org.apache.hadoop.io.serializer` defines pluggable object serialization. `Serializer<T>` opens an `OutputStream`, serializes values, and closes. `Deserializer<T>` opens an `InputStream`, deserializes into an optional reuse instance, and closes. `Serialization<T>` accepts classes and returns serializers/deserializers. `SerializationFactory`, a `Configured` class, chooses a registered serialization for a class. `WritableSerialization` handles Hadoop `Writable` types; `JavaSerialization` handles `Serializable`; `DeserializerComparator` and `JavaSerializationComparator` implement raw comparison by deserializing objects and comparing them.

`org.apache.hadoop.ipc` defines Hadoop's Writable-based IPC and RPC layer. `Client` sends `Writable` parameters to remote addresses, supports a default or provided `SocketFactory`, can set ping intervals in `Configuration`, stops related threads, performs single calls with optional `UserGroupInformation`, and performs parallel calls to multiple addresses. `RemoteException` preserves a remote exception class name/message, unwraps to matching local exception types, serializes to XML, and reconstructs from XML attributes.

`RPC` builds higher-level Java proxies over `VersionedProtocol`. It can wait for a proxy, create proxies with client/server protocol versions, socket factories, and user tickets, stop proxies, make multiple parallel reflective calls, and create server instances. `RPC.Server` extends the generic IPC `Server` for a protocol implementation object and invokes protocol methods from `Writable` call payloads. `RPC.VersionMismatch` reports interface name, client version, and server version.

`Server` is the abstract IPC service. It listens on a bind address and port, handles a configured `Writable` parameter class with a handler thread count, exposes a thread-local current server and remote client IP/address while serving calls, binds sockets with better exceptions, tunes response socket send buffers, starts/stops/joins the service, reports listener address, defines abstract `call(Writable, long)`, and reports open connection and call queue counts. Public fields include the Hadoop RPC connection header, current wire version byte, log, and protected `RpcMetrics`.

`VersionedProtocol` is the marker contract for RPC protocols and requires `getProtocolVersion(String protocol, long clientVersion)`. The Javadoc states subclasses should also expose a static final `versionID` field.

`org.apache.hadoop.ipc.metrics` covers RPC observability. `RpcMetrics` implements `Updater`, publishes queue and processing time metrics through Hadoop metrics contexts, exposes public `MetricsTimeVaryingRate` fields plus a `metricsList` map, registers JMX, and can shut down. `RpcMgtMBean` is the JMX interface for sampled RPC operation counts, average processing/queue times, min/max times since reset, reset, open connection count, and call queue length.

`org.apache.hadoop.log.LogLevel` changes log levels at runtime. It has a command-line `main`, a public `USAGES` constant, and nested `LogLevel.Servlet` with `doGet(HttpServletRequest, HttpServletResponse)` for HTTP-based log-level inspection or mutation.

The range ends in `org.apache.hadoop.mapred.ClusterStatus`. The visible part shows it implements `Writable` and exposes getters for task tracker count, currently running map tasks, and currently running reduce tasks. Additional fields and methods for the full cluster status are outside this chunk.

## Control Flow and Behavioral Contracts

Sequence-file writer flow is append-oriented. Construction chooses the destination filesystem/path, key and value classes, optional progress reporting, replication/block sizing, and metadata. Callers append object or raw byte key/value records, optionally create sync points, and close the writer. `getLength()` documents that returned offsets are synchronized reader seek targets but may point to an earlier key than the most recently written key when block compression is involved.

Sequence-file sort/merge flow uses `SegmentDescriptor` instances as comparable merge inputs. A descriptor reads the next raw key, then the matching raw value, exposes the raw key buffer for ordering, performs sync checks, and cleans up after a segment is consumed. The preservation flag controls whether backing segment files are deleted during cleanup.

Set-file flow inherits sorted `MapFile` behavior. Writers require strictly increasing keys; readers seek to a key, iterate keys, or return a matching key/null. Because set values are implicit, the observable contract is keyed lookup and sorted traversal rather than key/value retrieval.

Writable flow is explicit binary serialization. Implementations write all fields to a `DataOutput` and read them back from a `DataInput` in the same order. `VersionedWritable` prepends or checks a version byte, and `VersionMismatchException` is the documented failure mode when serialized data uses an incompatible version.

Text/UTF8 flow distinguishes byte length from Java character count. `Text` stores UTF-8 bytes, supports byte-position character lookup, validates byte ranges before decoding, can replace malformed input depending on the decode overload, and uses raw comparators for byte-level sort keys. Callers that use `getBytes()` must respect `getLength()` because the backing array can be larger than the active content.

Comparator flow is optimized for sorting large serialized datasets. `WritableComparator.compare(byte[],...)` can compare raw serialized records without object allocation; subclasses such as `Text.Comparator` and `UTF8.Comparator` specialize this path. Object comparison remains available for generic callers. Registry methods let Hadoop components obtain or override comparators by key class.

`WritableUtils` flow covers several persisted wire formats. Compressed byte arrays and strings are length-delimited, variable-length integers use Hadoop's zero-compressed vint/vlong encoding, enum values are stored by string name, and `clone`/`cloneInto` use serialization as a copy mechanism. `skipFully` is a defensive read-loop helper for streams that may skip fewer bytes than requested.

Compression flow is a reusable state machine. A codec creates a stream directly or around a pooled compressor/decompressor. Callers set input on compressors/decompressors, loop while `needsInput`/`finished` determine progress, call `finish` for compressor EOF, and call `reset` before reuse or `end` to release resources. `CompressionOutputStream.finish()` finalizes compressed data without necessarily closing the underlying stream; `resetState()` prepares a stream for a new logical member.

Codec discovery flow maps file names to codecs by extension. `CompressionCodecFactory` reads configured codec classes, builds suffix mappings, selects a codec for a `Path`, and can strip a matched suffix. This is an integration point for input formats that auto-detect compressed inputs.

LZO/lzop flow is split between raw native LZO compression and lzop container framing. `LzoCodec` depends on native availability. `LzopCodec` wraps block streams with lzop header parsing/writing and checksum verification. Its decompressor initializes header flags, resets checksums, feeds data through `setInput`, and verifies decompressed and compressed checksums during `decompress`.

Retry flow is proxy/interceptor driven. A caller picks a default or per-method `RetryPolicy`, wraps an implementation with `RetryProxy`, and invokes interface methods normally. On exception, the proxy asks the policy whether to retry based on the exception and retry count; policy implementations may sleep before returning or throw to stop retries.

SerializationFactory flow selects a `Serialization` implementation by testing `accept(Class<?>)`, then opens serializers/deserializers over supplied streams. `DeserializerComparator` raw-comparison flow deserializes two byte-array records into objects and delegates to `Comparable`, which is simpler but more allocation-heavy than custom raw comparators.

IPC client flow creates or reuses client-side connection threads, sends a single `Writable` parameter to a server address, waits for a `Writable` result, can send parallel requests to multiple addresses, and must be stopped to release threads. Ping interval is stored in configuration and affects connection liveness.

RPC flow layers Java interfaces over the IPC client. A proxy is created for a `VersionedProtocol`, checks protocol version compatibility, marshals method calls into `Writable` invocation payloads, and returns Java objects. `waitForProxy` repeatedly attempts proxy acquisition until the requested protocol/server becomes available. On the server side, `RPC.Server` receives a `Writable`, invokes the implementation instance reflectively, and returns a `Writable` response or a `RemoteException`.

Generic `Server` lifecycle is explicit: construct with bind address, port, parameter class, handlers, and configuration; optionally tune socket send buffer; call `start()` before requests are handled; call `stop()` to reject new calls; call `join()` to wait for the service to stop. The abstract `call` method receives both the decoded parameter and receive timestamp, allowing subclasses to measure queue and processing time.

RPC metrics flow samples server state and operation timings. `RpcMetrics.doUpdates` pushes queue and processing rates into a metrics context. `RpcMgtMBean` exposes last-interval averages plus min/max values since reset; its docs note that metrics are collected regardless of the chosen metrics context, but averages require a context with periodic updates such as `NullContextWithUpdateThread`.

Log-level flow has two entry points. The command-line path runs through `LogLevel.main(String[])`; the servlet path handles `GET` requests and can read or change logging levels at runtime through HTTP.

## State, Persistence, and Side Effects

The JDiff XML itself is persistent API compatibility data. Runtime state described by the covered APIs includes sequence-file output streams, raw key/value buffers, segment paths and deletion policy, sorted map contents, mutable text byte arrays, two-dimensional writable arrays, version bytes, variable-length numeric values, writable comparator/factory/name registries, codec discovery maps, pooled compressor/decompressor instances, stream wrappers, native compression contexts, retry proxy counters, serializer stream state, IPC connection pools, RPC server listener/handler threads, current server/remote-address thread-local context, RPC metrics, JMX MBean state, servlet responses, and cluster status counters.

Persistent external formats are central here. `Writable` binary layouts, `Text` and deprecated `UTF8` encodings, vint/vlong encodings, compressed string/byte-array formats, `SequenceFile` records and sync markers, set-file `MapFile` layouts, bzip2/gzip/lzo/lzop/zlib stream formats, lzop header/checksum fields, XML representation of `RemoteException`, and RPC wire headers are all compatibility-sensitive.

Several APIs have external side effects. `SequenceFile.Writer` and `SetFile.Writer` create and append files in a Hadoop `FileSystem`; segment cleanup may close file handles and delete intermediate segment files. Compression streams write or read compressed data from caller-supplied streams and may retain native resources until `end`, `close`, or finalization. `CodecPool` can hold reusable native buffers beyond a single call. `RetryProxy` can repeat side-effecting method calls unless policies and wrapped methods are chosen carefully. IPC/RPC clients open sockets and background threads; servers bind ports, accept connections, and run handler threads. RPC metrics register with the metrics and JMX subsystems. `LogLevel.Servlet` writes HTTP responses and may mutate process logging configuration.

Threading is mixed. `SequenceFile.Writer.close`, `append`, `appendRaw`, and `getLength` are synchronized in this snapshot; many other IO and collection types are mutable without documented synchronization. `Server.start`, `stop`, `join`, and `getListenerAddress` are synchronized lifecycle operations. Compressor/decompressor instances are stateful and should be treated as single-thread owned while checked out of a pool.

## Dependencies and Integration Points

The IO APIs integrate with Hadoop's `FileSystem`, `Path`, `Configuration`, `Progressable`, `MapFile`, `SequenceFile`, `Writable`, `WritableComparable`, `WritableComparator`, `DataInput`, `DataOutput`, `DataOutputBuffer`, Java collections, and serializer APIs. `SequenceFile.Writer` depends directly on `org.apache.hadoop.io.serializer.Serializer` and `org.apache.hadoop.io.compress.CompressionCodec`.

Text and UTF-8 helpers depend on `java.nio.ByteBuffer`, `CharacterCodingException`, `MalformedInputException`, and Java charset behavior. They are heavily used by MapReduce keys, sequence files, RPC payloads, and configuration utilities.

Compression integrates with Java streams, `java.util.zip.Deflater`/`Inflater`, Hadoop configuration, codec discovery from configured class lists, native zlib and LZO libraries, bzip2 algorithm constants, block compressor/decompressor streams, checksum handling, and filename/path extension conventions.

Retry integrates with Java dynamic proxies, exception classification, `RemoteException` classification, `TimeUnit`, and service interfaces where retrying is semantically acceptable.

Serialization integrates with Hadoop `Writable`, Java `Serializable`, `Comparable`, raw comparators, and `Configured`/`Configuration`. It is a common extension point for sequence files, MapReduce shuffle/sort, and RPC payloads.

IPC/RPC integrates with `Writable` messages, `InetSocketAddress`, `SocketFactory`, `ServerSocket`, `UserGroupInformation`, Java reflection `Method`, Commons Logging, Hadoop metrics, JMX, XML/SAX attributes for remote exception persistence, and protocol interfaces implementing `VersionedProtocol`.

RPC metrics bridge the IPC server with the older Hadoop metrics subsystem (`MetricsContext`, `Updater`, `MetricsTimeVaryingRate`) and JMX management. Runtime log-level control integrates with servlet APIs and the process logging framework.

The visible `ClusterStatus` fragment connects classic `mapred` cluster state to `Writable` serialization, but most of the class surface is outside the chunk.

## Risks and Compatibility Notes

This chunk has partial boundaries. It starts after `SequenceFile.Sorter.RawKeyValueIterator` and after the containing `SequenceFile`/`org.apache.hadoop.io` declarations; it ends before `ClusterStatus` is complete. Final per-file reconciliation should combine adjacent chunks before making whole-class conclusions for those APIs.

This file is a public API compatibility artifact. Changes to class names, nesting, inheritance, implemented interfaces, constructor signatures, method parameters, return types, checked exceptions, field visibility/finality, synchronized flags, deprecation strings, or documented contracts can break old Hadoop clients even if implementation code still compiles internally.

Sequence-file and set-file APIs are storage-format sensitive. Changing sync marker behavior, `getLength()` seek guarantees, raw append semantics, serializer selection, key/value class reporting, segment cleanup/deletion policy, or strict key ordering in `SetFile.Writer` can corrupt data or make old readers unable to recover/split files.

Writable formats are wire and disk compatibility contracts. Reordering fields in implementations, changing vint/vlong encoding, altering compressed string formats, replacing `UTF8` behavior despite deprecation, or changing `WritableName` aliases can break persisted data, MapReduce shuffle keys, and RPC messages.

`Text` exposes its backing bytes, so callers can misuse array capacity as active length. UTF-8 validation and replacement behavior must remain precise; accepting malformed data silently or throwing on formerly accepted replacement paths can break data pipelines. `charAt` works on byte positions and returns Unicode scalar values, which is easy to confuse with Java `char` indexing.

Raw comparator behavior is performance and correctness critical. Comparator registry mistakes, inconsistent raw/object comparison, endian/sign errors in byte parsing helpers, or incorrect vint/vlong parsing can mis-sort map outputs and sequence-file indexes.

Compression APIs are resource-sensitive. Pooling a compressor after `end`, failing to `reset` before reuse, losing `finish()` data, mishandling native-library availability, ignoring dictionary requirements, or leaking native LZO/zlib state can cause data loss, hangs, memory leaks, or platform-specific failures. Lzop header and checksum verification is especially compatibility-sensitive because it determines whether existing `.lzo`/`.lzo_deflate` style files can be read.

Retry proxies can duplicate operations. They are safest for idempotent calls; applying retry policies to methods with non-idempotent side effects can produce duplicate writes, repeated submissions, or inconsistent remote state. Retry-by-exception maps also depend on correct `RemoteException` class-name unwrapping.

SerializationFactory order and accept logic are compatibility points. If both Java serialization and Writable serialization can accept a class, selection order affects wire format. Deserializing comparators allocate and depend on `Comparable`; they are safer functionally but can be too slow for sort-heavy paths.

IPC/RPC APIs are protocol-version, threading, and resource sensitive. Version mismatch handling must preserve interface/client/server version details. Client `stop()` must release threads and sockets. Server lifecycle must avoid accepting calls before `start` or after `stop`, and `getRemoteIp`/`getRemoteAddress` are only meaningful inside an RPC handler. Header or current-version changes are wire-incompatible.

RPC metrics and log-level control are operational surfaces. Metrics averages depend on periodic update contexts; using the null metrics context can hide sampled data unless configured as documented. Runtime log-level mutation through a servlet must validate inputs and avoid exposing sensitive logging controls without deployment-side protection.

## Test Signals

JDiff-level validation should confirm this XML range remains well formed across partial boundaries and preserves every covered package/class/interface boundary, nested class name, constructor and method signature, parameter type, checked exception, visibility/static/final/abstract/synchronized flag, field constant, deprecation note, and Javadoc contract.

Sequence-file tests should cover writer construction variants, key/value class reporting, compression codec reporting, append of `Writable` and object pairs, `appendRaw`, sync point creation, `getLength()` followed by reader seek, close idempotence/error paths, progress callbacks, metadata persistence, segment descriptor ordering/equality/hash, raw key/value iteration, sync checks, preserve-input behavior, and cleanup deletion vs preservation.

Set-file and sorted-map tests should cover writer strict ordering, deprecated and configured constructors, comparator-based construction, compression type propagation, reader seek/next/get semantics for existing and missing keys, sorted map copy construction, all `SortedMap` view methods, mutation methods, serialization round trips, and class-ID handling inherited from `AbstractMapWritable`.

Text/UTF8 tests should cover constructors from strings, bytes, and copies; backing-array length vs active length; byte-position `charAt`; substring `find` with and without start offset; setters and append ranges; clear; `readFields`/`write`; static read/write string helpers; decode/encode with replacement true/false; malformed UTF-8 validation failures; `bytesToCodePoint`; `utf8Length`; raw comparator ordering; and deprecated `UTF8` compatibility with old serialized data.

Writable primitive and utility tests should cover `VIntWritable`/`VLongWritable` set/get/read/write/compare/equality, `VersionedWritable` successful and mismatched version reads, `WritableComparator` registry definition and lookup, object vs raw comparisons, byte parsing helpers, `WritableFactories` custom factory lookup and configured construction, `WritableName` aliases and class resolution, compressed byte/string arrays, string arrays, clone/cloneInto, vint/vlong boundary values, enum read/write, `skipFully` short-skip behavior, and `toByteArray`.

Compression tests should cover codec factory discovery from configuration, suffix matching/removal, default/gzip/bzip2/lzo/lzop codec default extensions, stream close/finish/reset behavior, compressor/decompressor pool checkout and return, direct and pooled stream creation, byte counters, dictionary requirements, native and non-native zlib selection, built-in deflater/inflater adapters, native LZO unavailable behavior, lzop header parsing/writing, data and compressed checksum verification, bzip2 block-size selection, bzip2 read/write round trips, and resource cleanup after `end`/`close`/finalize paths.

Retry tests should cover try-once-fail, try-once-dont-fail, retry-forever with bounded test hooks, fixed-count and fixed-time policies, proportional and exponential sleeps with fake time or small intervals, exception-class policy maps, remote-exception class-name policy maps, per-method policy selection, retry count propagation, exception propagation when retry stops, and non-idempotent method documentation or guard tests in callers.

Serialization tests should cover `WritableSerialization` acceptance and round trips, `JavaSerialization` acceptance and round trips, factory selection order, serializer/deserializer open-close lifecycle, deserialize-into-reuse behavior, stream closure behavior, missing serializer/deserializer returns, `DeserializerComparator` and `JavaSerializationComparator` ordering, and malformed serialized input failures.

IPC/RPC tests should cover `Client` construction with default and custom socket factories, ping interval configuration, single calls with and without `UserGroupInformation`, parallel calls, timeout/interruption behavior, client stop releasing resources, `RemoteException` XML write/valueOf and typed unwrap behavior, proxy creation overloads, `waitForProxy`, version mismatch reporting, `stopProxy`, reflective parallel RPC calls, server construction, bind failure diagnostics, start/stop/join lifecycle, listener address reporting, remote IP/address visibility inside handlers, call queue and open connection metrics, and wire header/version compatibility.

RPC metrics and logging tests should cover `RpcMetrics` registration, queue/processing time increments and `doUpdates`, shutdown, public metrics-list visibility, JMX MBean getters for operation counts and averages/min/max, reset behavior, connection and call queue delegation to `Server`, metrics contexts with and without periodic update threads, `LogLevel.main` argument handling, servlet `doGet` read/change flows, servlet error handling, and HTTP response formatting.

`ClusterStatus` tests for this visible fragment should at least cover `Writable` serialization compatibility and getters for task tracker count, running map count, and running reduce count, with adjacent chunks needed for full class coverage.
