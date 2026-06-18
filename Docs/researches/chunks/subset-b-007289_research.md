# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.0.xml lines 12391-18682

## Scope and source type

This chunk is a JDiff XML API snapshot for Hadoop 0.19.0, not Java implementation source. It records public/protected API signatures, inheritance, selected fields, checked exceptions, deprecation markers, synchronization markers, and embedded Javadoc. Behavioral notes below are therefore grounded in the API contract and comments visible in this chunk, with implementation details inferred only where the contract is explicit.

The range starts in `org.apache.hadoop.io.SequenceFile.Sorter.SegmentDescriptor`, covers the rest of many `org.apache.hadoop.io` writable and text APIs, the public compression codec stack, retry and serialization APIs, Hadoop IPC/RPC APIs and metrics, runtime log-level controls, and ends at the beginning of `org.apache.hadoop.mapred.Counters`.

## Purpose

The chunk documents core Hadoop data interchange and transport surfaces:

- Sequence and map/set file utilities for persisted key/value data.
- The `Writable` serialization contract used across MapReduce, filesystem metadata, and IPC.
- Raw comparators and variable-length integer helpers used by sort-heavy paths.
- UTF-8 string containers and string serialization utilities.
- Compression codec abstractions and concrete BZip2, gzip/zlib, and LZO/lzop adapters.
- Retry proxies for wrapping unreliable method calls.
- Serializer/deserializer factories for `Writable` and Java serialization.
- IPC/RPC client/server contracts, version negotiation, remote exceptions, and server metrics.
- Log-level runtime adjustment entry points.
- MapReduce cluster status and the beginning of counter aggregation APIs.

## Important APIs, types, and functions

### SequenceFile and set/map data

`SequenceFile.Sorter.SegmentDescriptor` represents one merge segment. It can perform sync checks via `doSync()`, control cleanup semantics with `preserveInput(boolean)` and `shouldPreserveInput()`, compare/equality/hash segments, stream raw keys and values via `nextRawKey()`, `nextRawValue(SequenceFile.ValueBytes)`, expose the buffered raw key through `getKey()`, and clean up by closing file handles and deleting input unless preservation is requested. Subclasses may override `cleanup()`.

`SequenceFile.ValueBytes` abstracts raw sequence-file values. `writeUncompressedBytes(DataOutputStream)` writes uncompressed payload bytes, `writeCompressedBytes(DataOutputStream)` writes stored compressed bytes without performing compression when data is not already compressed, and `getSize()` reports stored data size. This interface is central to raw append/merge flows where values can be copied without object deserialization.

`SequenceFile.Writer` writes key/value sequence files to a `FileSystem`/`Path`, with constructors accepting `Configuration`, key/value classes, optional replication/block size, `Progressable`, and `SequenceFile.Metadata`. Its key methods are `append(Writable, Writable)`, generic `append(Object, Object)` through serializers, `appendRaw(byte[], int, int, ValueBytes)`, `sync()`, `close()`, `getLength()`, `getKeyClass()`, `getValueClass()`, and `getCompressionCodec()`. `close`, `append`, `appendRaw`, and `getLength` are synchronized. Protected serializer fields (`keySerializer`, `uncompressedValSerializer`, `compressedValSerializer`) show integration with the serializer framework. `getLength()` promises a reader-seekable synchronized position, although block compression can make the next readable key earlier than the last appended key.

`SetFile` extends `MapFile` for file-backed sets of sorted keys. `SetFile.Reader` supports constructors with a filesystem/path/config and optional `WritableComparator`, plus `seek`, `next`, and `get` operations over `WritableComparable` keys. `SetFile.Writer` extends `MapFile.Writer`; it accepts key class or comparator and compression type, and `append(WritableComparable)` requires strictly increasing keys. One constructor lacking `Configuration` is deprecated.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes normal sorted-map operations (`firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `put`, `remove`, `entrySet`, `keySet`, `values`, etc.) plus `readFields` and `write`. The copy constructor and writable inheritance imply it persists both map entries and the writable class-id mappings maintained by `AbstractMapWritable`.

### Text, UTF-8, and writable values

`Stringifier<T>` is a closeable conversion contract with `toString(T)`, `fromString(String)`, and `close()`, all throwing `IOException`.

`Text` is the non-deprecated UTF-8 byte container. It extends `BinaryComparable` and implements `WritableComparable<BinaryComparable>`. Constructors accept empty state, `String`, another `Text`, or raw bytes. Methods expose raw bytes and byte length, byte-position string search, code point traversal without building a Java `String`, mutation from strings or byte ranges, append/clear, conversion to Java `String`, writable `readFields`/`write`, static `skip`, UTF-8 `decode`/`encode` with optional replacement behavior, string read/write helpers, UTF-8 validation, code point extraction from `ByteBuffer`, and `utf8Length(String)`. Length is serialized using zero-compressed integer encoding.

`Text.Comparator` is an optimized raw-byte `WritableComparator` for `Text` keys. It avoids object materialization in compare-heavy sort paths.

`UTF8` is the legacy/deprecated predecessor to `Text`. It implements `WritableComparable`, stores UTF-8 bytes, exposes `getBytes`, `getLength`, `set`, `readFields`, `write`, `compareTo`, `equals`, `hashCode`, and static string read/write helpers. `UTF8.Comparator` provides an optimized raw comparator for legacy keys.

`TwoDArrayWritable` persists a two-dimensional matrix of `Writable` instances of a declared value class. It exposes `set`, `get`, `toArray`, `readFields`, and `write`.

`VersionedWritable` is an abstract `Writable` base that writes a version byte and verifies it on read. Subclasses supply `getVersion()`. `VersionMismatchException` is thrown when serialized and current versions differ, and callers are expected to catch it when implementing backward compatibility.

`VIntWritable` and `VLongWritable` are `WritableComparable` wrappers for variable-length encoded `int` and `long` values. They expose mutable `set`/`get`, serialization, equality, hashing, comparison, and string conversion. The docs say smaller values take fewer bytes; the `VLongWritable` comment says one to five bytes even though long variable-length encodings can require more bytes, so tests should verify actual format behavior rather than relying on that sentence.

### Writable framework utilities

`Writable` is Hadoop's compact `DataInput`/`DataOutput` serialization interface. `readFields` is expected to reuse existing object storage where possible. The docs identify this as the required key/value contract for MapReduce types.

`WritableComparable<T>` combines `Writable` and `Comparable<T>` and is the normal key contract for MapReduce sorting.

`WritableComparator` implements `RawComparator`. It maintains a synchronized static registry (`get`, `define`) of comparators by key class. It can instantiate new keys, compare deserialized `WritableComparable` objects, compare raw byte spans, and provides static helpers for lexicographic byte comparison, hashing, and reading primitive or variable-length values from byte arrays. This is the primary extension point for optimized sorting and `SequenceFile.Sorter` performance.

`WritableFactories` stores synchronized factory registrations for non-public writable classes and can instantiate with or without `Configuration`. `WritableFactory` is the one-method factory contract. `WritableName` maps writable classes to stable symbolic names and alternate names so serialized files can survive class renames.

`WritableUtils` contains compressed byte/string array helpers, string array helpers, clone/cloneInto via serialization buffers, vint/vlong write/read/sign/size functions, enum string serialization, `skipFully`, and conversion of writable arrays to bytes. Its variable-length integer docs define the on-wire encoding thresholds and first-byte sign/length interpretation.

### Compression stack

`CompressionCodec` is the streaming codec interface. It creates compression and decompression streams with or without reusable `Compressor`/`Decompressor` objects, exposes compressor/decompressor implementation types, creates new codec state, and reports default file extensions.

`CodecPool` is a global reuse pool for `Compressor` and `Decompressor` instances. Callers obtain instances by codec and must return them through `returnCompressor`/`returnDecompressor`.

`CompressionCodecFactory` discovers configured codecs from `io.compression.codecs`, defaults to gzip and zip per the docs, maps filename suffixes to codecs, exposes `getCodecClasses` and `setCodecClasses`, strips suffixes, and has a small CLI/test `main`.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases wrapping final underlying streams. Input streams must implement `read(byte[], int, int)` and `resetState()` to handle repositioned underlying streams. Output streams must implement `write(byte[], int, int)`, `finish()` without closing the wrapped stream, and `resetState()` without resetting the wrapped stream.

`Compressor` and `Decompressor` define deflater/inflater-like state machines: `setInput`, `needsInput`, optional dictionaries, byte counters, `finish`/`finished`, `compress` or `decompress`, `reset`, and `end`. `Decompressor` also has `needsDictionary`.

Concrete codecs and adapters in this chunk:

- `BZip2Codec` implements `CompressionCodec` but explicitly does not support the `Compressor`/`Decompressor` object APIs; those paths throw `UnsupportedOperationException`. It creates BZip2 streams and uses `.bz2` as the default extension.
- `DefaultCodec` is configurable and provides zlib-backed default compression/decompression APIs.
- `GzipCodec` extends `DefaultCodec`, with gzip stream creation, compressor/decompressor factory methods, and `.gz` style extension behavior implied by the codec name. Nested `GzipInputStream` and `GzipOutputStream` bridge Hadoop compression streams to Java deflater/inflater streams, including `resetState`.
- `LzoCodec` is configurable, checks native LZO availability, and creates LZO streams/compressor/decompressor state. `LzopCodec` extends it for lzop-compatible file format behavior. `LzopDecompressor` adds checksum flag initialization, checksum reset/verification for compressed and decompressed data, synchronized input/decompress paths, and LZO1X strategy. `LzopInputStream` reads and verifies lzop headers; `LzopOutputStream` writes lzop headers and closes by writing a null word.
- `CBZip2InputStream` and `CBZip2OutputStream` implement raw BZip2 streams below `BZip2Codec`. They require callers/codecs to manage the two-byte `BZ` magic around the constructors. Their docs call out large memory usage and lack of thread safety.
- `LzoCompressor` and `LzoDecompressor` are native LZO-backed `Compressor`/`Decompressor` implementations with direct buffer sizes, strategies, byte counters, synchronized mutation/compression paths, no-op or explicit `end`, and native library version fields.
- `BuiltInZlibDeflater`/`BuiltInZlibInflater` adapt Java `Deflater`/`Inflater` to Hadoop interfaces. `ZlibCompressor`/`ZlibDecompressor` expose native zlib style direct-buffer implementations with configurable header, level, strategy, counters, reset, and lifecycle. `ZlibFactory` chooses native or built-in zlib implementations based on configuration and native availability.

### Retry and serialization

`RetryPolicies` is a static factory/constant holder for immutable `RetryPolicy` instances: try once and fail, try once without failing void methods, retry forever, fixed-count fixed-sleep, maximum-time fixed-sleep, proportional sleep, exponential randomized backoff, policy by local exception type, and policy by `RemoteException`.

`RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, returns false for swallowable void-method failures, or rethrows to fail. `RetryProxy.create` builds dynamic proxies over an interface and implementation using either one policy for all methods or a method-name-to-policy map with default `TRY_ONCE_THEN_FAIL`.

`Serializer<T>` and `Deserializer<T>` are stateful stream adapters. Serializers are explicitly not allowed to buffer output because other producers may write between serialization calls. `Serialization<T>` pairs serializers and deserializers and declares whether a class is accepted.

`SerializationFactory` loads implementations from the comma-delimited `io.serializations` configuration property and returns the matching `Serialization`, `Serializer`, or `Deserializer`.

`WritableSerialization` delegates to `Writable.write` and `Writable.readFields`. `JavaSerialization` is marked experimental for Java `Serializable`. `DeserializerComparator` and `JavaSerializationComparator` deserialize byte streams and compare resulting `Comparable` objects, which is simpler but generally more expensive than raw-byte comparators.

### IPC, RPC, metrics, and logging

`Client` is the lower-level IPC client for `Writable` request/response values. It can set ping interval in configuration, stop all client threads, make a single call to an address with optional `UserGroupInformation`, or make parallel calls to multiple addresses. Parallel calls return an array with nulls for timeouts/errors.

`RemoteException` serializes remote exception class names/messages. It can unwrap to selected lookup types or any throwable with a string constructor, write XML through `XMLOutputter`, and reconstruct from SAX attributes.

`RPC` is the Java-interface-oriented RPC layer over IPC. It constructs client-side `VersionedProtocol` proxies with version negotiation, user tickets, and socket factories; waits for a proxy; stops proxies; performs expert parallel reflective calls; and constructs `RPC.Server` instances for protocol implementation objects. Protocol methods are restricted to primitives/void, `String`, `Writable`, or arrays of those, should throw only `IOException`, and do not transmit implementation field data.

`RPC.Server` extends `Server`, dispatching reflected protocol calls against an implementation instance. `RPC.VersionMismatch` records interface name, client version, and server version for protocol version failures.

`Server` is the abstract IPC service. It binds/listens on host and port for a single `Writable` parameter class, starts/stops handler threads, joins shutdown, exposes listener address, remote IP/address context for code running inside an RPC call, and requires subclasses to implement `call(Writable, long)`. It publishes `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`, plus open connection and call queue length gauges.

`VersionedProtocol` is the superclass for Hadoop RPC protocols and requires `getProtocolVersion(String, long)`. Implementations are also expected to define a static `versionID` field.

`RpcMetrics` registers and publishes RPC queue and processing time metrics through the Hadoop metrics subsystem and JMX. Its rate metrics are public mutable fields. `RpcMgtMBean` exposes operation counts, average/min/max processing and queue times, min/max reset, open connection count, and call queue length. The docs note that metrics are collected regardless of metrics context, but sampled averaging requires an updating context such as `NullContextWithUpdateThread`.

`LogLevel` provides runtime log-level changes via a command-line `main` and a servlet `doGet` entry point. The servlet depends on `javax.servlet.http.HttpServlet`.

### MapReduce status and counters

`ClusterStatus` is a `Writable` snapshot of the MapReduce cluster: number of task trackers, running map/reduce tasks, maximum map/reduce task capacity, and current `JobTracker.State`. Clients obtain it through `JobClient.getClusterStatus()`.

The chunk begins `Counters`, which is a synchronized `Writable` and `Iterable<Counters.Group>`. Visible methods include `getGroupNames`, `iterator`, `getGroup`, `findCounter` by enum, by group/name, and deprecated group/id/name, plus `incrCounter` by enum and the start of another `incrCounter` overload. This partial range establishes counters as mutable grouped job metrics with synchronized access.

## Control flow and state behavior

The common control pattern is stream-oriented and stateful:

- Writables mutate existing object instances during `readFields` to reduce allocation.
- SequenceFile writers serialize key/value records, optionally raw-copying value bytes, insert sync points, and expose seekable file positions for readers.
- Comparators either deserialize objects or operate directly over serialized byte slices for sort performance.
- Compression streams wrap input/output streams while compressor/decompressor objects hold native or Java codec state. `resetState`, `reset`, `finish`, `finished`, and `end` delimit lifecycle boundaries.
- Retry proxies intercept interface method calls and use policy decisions to sleep, retry, swallow void failures, or rethrow exceptions.
- IPC clients send one writable request to server addresses; servers accept calls into handler queues and invoke `call`. RPC layers encode Java interface calls into this writable transport and enforce protocol version compatibility.

State and persistence contracts are mostly binary:

- `Writable`, `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `ClusterStatus`, and `Counters` persist to `DataOutput` and recover from `DataInput`.
- `WritableName` persists compatibility indirectly by stabilizing class names in serialized streams.
- `VersionedWritable` persists a version byte and fails fast on mismatches unless subclasses handle compatibility.
- Compression codecs persist compressed stream formats identified by file suffixes and headers. BZip2/lzop header handling is particularly visible.
- RPC state is not durable; it is connection/request state plus metrics. Remote exceptions can be serialized to XML.

Synchronization appears on mutable shared or lifecycle-sensitive APIs: `SequenceFile.Writer` append/close/length methods, `WritableComparator` and factory/name registries, LZO/zlib compression state mutation, IPC server start/stop/join/listener access, and `Counters` group/counter access.

## Dependencies and integration points

Key dependencies visible in the signatures:

- Hadoop filesystem/configuration/progress: `FileSystem`, `Path`, `Configuration`, `Progressable`.
- Hadoop I/O: `Writable`, `WritableComparable`, `RawComparator`, `BinaryComparable`, `DataOutputBuffer`, `SequenceFile`, `MapFile`.
- Java stream and NIO primitives: `DataInput`, `DataOutput`, `InputStream`, `OutputStream`, `DataOutputStream`, `ByteBuffer`, `CharacterCodingException`, `MalformedInputException`.
- Compression and native integration: `java.util.zip.Deflater`/`Inflater`, zlib, LZO native libraries, bzip2 stream code.
- Security/networking: `InetSocketAddress`, `InetAddress`, `ServerSocket`, `SocketFactory`, `UserGroupInformation`.
- Metrics/JMX: `MetricsContext`, `Updater`, `MetricsTimeVaryingRate`, management MBeans.
- XML/servlet support: SAX `Attributes`, `org.znerd.xmlenc.XMLOutputter`, servlet request/response classes.
- MapReduce: `JobClient`, `JobTracker.State`, `Counters.Group`, `Counters.Counter`.

The APIs are deeply integrated: SequenceFile and MapFile rely on Writable serialization, WritableComparator, and compression codecs; MapReduce keys/counters/status rely on Writable; IPC/RPC uses Writable payloads and `VersionedProtocol`; metrics observe IPC server behavior; retry proxies can wrap RPC protocol clients; compression codecs are selected by configuration and filename suffix.

## Risks and edge cases

- This is an API snapshot. It does not prove implementation correctness, only intended public/protected contracts.
- `SequenceFile.Writer.getLength()` returns a synchronized seek point, but block compression may seek to a key earlier than the most recently appended key. Tests must account for this.
- `SetFile.Writer.append` requires strictly increasing keys; violating sorted order likely corrupts search semantics.
- `Text.getBytes()` exposes a buffer larger than valid content; consumers must honor `getLength()`.
- `Text.charAt` and `find` use byte positions, not Java char indexes. Multi-byte UTF-8 callers can easily pass invalid trailing-byte positions.
- `UTF8` is deprecated in favor of `Text`; compatibility may still matter for old persisted data.
- `VersionedWritable` can reject old data unless subclasses catch `VersionMismatchException` and explicitly migrate fields.
- Static registries in `WritableComparator`, `WritableFactories`, and `WritableName` are global mutable state. Registration order and classloader behavior can affect behavior.
- BZip2Codec does not support pooled `Compressor`/`Decompressor` methods; generic codec users must tolerate `UnsupportedOperationException`.
- `BZip2Constants.rNums` is public and mutable as an array; the docs explicitly flag malicious-code risk.
- Raw `CBZip2InputStream`/`OutputStream` constructors require external handling of `BZ` magic bytes and are not thread-safe.
- LZO/lzop and zlib native paths depend on native library availability and configuration. Fallback and direct-buffer lifecycle should be tested.
- CodecPool requires callers to return compressor/decompressor instances; leaks can hold native resources.
- `Serializer` implementations must not buffer output, or interleaved stream writers can produce corrupt data.
- Java serialization and deserializing comparators are slower and may have compatibility/security concerns compared with Writable/raw comparators.
- Retry policies can hide failures for void methods (`TRY_ONCE_DONT_FAIL`) or retry indefinitely (`RETRY_FOREVER`); call sites need bounded policy choices.
- RPC protocol signatures are constrained; unsupported parameter/return types or non-IOException throws violate the RPC contract.
- `Client.call` parallel mode returns null for timed out or errored calls, so callers must not treat null as a valid response without disambiguation.
- Server `join()` explicitly does not wait for all subthreads, only for stop state.
- Metrics averages depend on an updating metrics context; with a null context, raw collection continues but averaging may not be visible.
- Runtime log-level servlet changes require web exposure controls outside this API surface.
- The chunk ends mid-`Counters`, so the full counter persistence/merge behavior must be completed by adjacent chunk research.

## Test signals

Useful validation targets derived from this API surface:

- Writable round trips: `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `TwoDArrayWritable`, `SortedMapWritable`, `VersionedWritable` subclasses, `ClusterStatus`, and `Counters`.
- UTF-8 correctness: valid/invalid byte validation, replacement versus exception behavior in `Text.decode`/`encode`, `charAt` on multi-byte boundaries, `find` byte offsets, and `utf8Length`.
- Raw comparator equivalence: `Text.Comparator`, `UTF8.Comparator`, and custom `WritableComparator` raw comparisons must match object comparison order.
- Variable-length integer boundaries: one-byte thresholds, negative encodings, max/min int and long, `getVIntSize`, byte-array readers, and stream readers.
- SequenceFile writer/reader flows: normal append, object serializer append, raw append, sync points, `getLength` seekability, compressed and block-compressed behavior, and segment cleanup/preservation.
- SetFile sorted-key contract: append increasing keys, reject or expose failure on out-of-order keys, seek/get/next behavior with custom comparators.
- Compression matrix: codec factory suffix lookup, configured codec class lists, pool get/return lifecycle, BZip2 unsupported pooled methods, BZip2 magic handling, gzip reset/finish semantics, lzop header/checksum verification, native LZO/zlib availability fallbacks, and stream close/finish not losing trailing bytes.
- Retry policies: exact retry counts/timing decisions using controlled policies, exception-specific and remote-exception-specific policy maps, void-method swallow behavior, and default method policy in `RetryProxy`.
- Serialization factory: `io.serializations` loading order, `WritableSerialization` round trips, `JavaSerialization` acceptance, serializer no-buffering behavior under interleaved writes, and deserializer comparator equivalence.
- IPC/RPC: client stop prevents further calls, single and parallel calls, null results for failed parallel calls, protocol version negotiation, `RPC.VersionMismatch`, remote exception unwrap/writeXml/valueOf, server start/stop/join lifecycle, remote address context inside calls, socket bind error reporting, and call queue/open connection metrics.
- Metrics/JMX: `RpcMetrics.doUpdates`, public rate mutation, MBean min/max reset, queue/processing time averages with and without an updating metrics context.
- LogLevel: CLI argument validation, servlet `doGet` behavior, permission/exposure assumptions in embedding web apps.
