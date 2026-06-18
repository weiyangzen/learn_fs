# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.19.2.xml lines 12405-18689

## Scope And Purpose

This chunk is a JDiff XML API snapshot for Hadoop 0.19.2, not production implementation source. It records the public and protected type surface, method signatures, fields, inheritance, interface implementations, deprecation metadata, checked exceptions, synchronization flags, and selected Javadoc for a large slice of `hadoop-common`. The research value is therefore compatibility-oriented: this file tells later comparison and migration lanes which APIs existed, which contracts were documented, and which behaviors downstream callers could reasonably depend on.

The slice starts in the middle of `org.apache.hadoop.io.SequenceFile.Sorter.SegmentDescriptor`, continues through the remainder of `org.apache.hadoop.io`, covers compression, retry, and serializer packages, then records Hadoop IPC/RPC APIs, RPC metrics/JMX APIs, runtime log-level control, and the start of `org.apache.hadoop.mapred.ClusterStatus`. The chunk ends before `ClusterStatus` is complete, so any final per-file report must reconcile the rest of that class with adjacent chunks.

Because the file is generated API metadata, it does not expose method bodies. Control flow, persistence, and risk notes below are inferred from signatures, type relationships, names, and embedded Javadocs in the XML.

## API Surface Covered

### `org.apache.hadoop.io` Boundary And SequenceFile APIs

The chunk begins inside `SequenceFile.Sorter.SegmentDescriptor`, a merge segment descriptor used by `SequenceFile.Sorter`. Visible APIs include `doSync`, `preserveInput(boolean)`, `shouldPreserveInput`, `compareTo(Object)`, `equals`, `hashCode`, `nextRawKey`, `nextRawValue(ValueBytes)`, `getKey`, and `cleanup`. The Javadoc states that cleanup closes file handles and deletes the file by default, with subclasses allowed to customize cleanup behavior. This makes the descriptor both an iteration primitive over sorted raw key/value data and a lifecycle owner for temporary merge segment files.

`SequenceFile.ValueBytes` is the raw-value interface used when copying values without fully deserializing them. It exposes `writeUncompressedBytes(DataOutputStream)`, `writeCompressedBytes(DataOutputStream)`, and `getSize`. The documentation explicitly says `writeCompressedBytes` does not compress uncompressed data, so callers must know whether the underlying bytes are already compressed.

`SequenceFile.Writer` is a public closeable writer for sequence-format files. Constructors accept `FileSystem`, `Configuration`, `Path`, key/value classes, optional replication/block-size arguments, `Progressable`, and `SequenceFile.Metadata`. Public methods include `getKeyClass`, `getValueClass`, `getCompressionCodec`, `sync`, synchronized `close`, synchronized `append(Writable, Writable)`, synchronized `append(Object, Object)`, synchronized `appendRaw(byte[], int, int, ValueBytes)`, and synchronized `getLength`. Protected fields expose the active key serializer plus uncompressed and compressed value serializers. The `getLength` doc is important: returned offsets are synchronized positions usable for `Reader.seek`, but with block compression the next readable key may be earlier than the most recently written key.

### Map-Like And Writable Data Types

`SetFile` is a file-backed set implemented as a `MapFile`. `SetFile.Reader` extends `MapFile.Reader` and exposes constructors with `FileSystem`, directory name, optional `WritableComparator`, and `Configuration`; it supports `seek`, `next`, and `get` for `WritableComparable` keys. `SetFile.Writer` extends `MapFile.Writer`, has constructors by key class or comparator and `SequenceFile.CompressionType`, and exposes `append(WritableComparable)`. The old writer constructor without `Configuration` is explicitly deprecated with the reason `pass a Configuration too`. The writer contract says appended keys must be strictly greater than the previous key.

`SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap<WritableComparable, Writable>`. It exposes the full sorted-map surface (`comparator`, `firstKey`, `lastKey`, `headMap`, `subMap`, `tailMap`, `clear`, `containsKey`, `containsValue`, `entrySet`, `get`, `isEmpty`, `keySet`, `put`, `putAll`, `remove`, `size`, `values`) plus `readFields` and `write`. This class is both an in-memory sorted map and a `Writable` serialization container whose keys and values must be Hadoop writable types registered through `AbstractMapWritable`.

`Stringifier<T>` is a small conversion interface with `toString(T)`, `fromString(String)`, and `close`. It provides a pluggable string serialization facade, likely used by configuration and tooling code.

`Text` is the primary UTF-8 text value type. It extends `BinaryComparable` and exposes constructors from empty, `String`, another `Text`, and byte array values. Important APIs include `getBytes`, `getLength`, `charAt`, `find`, several `set` overloads, `append`, `clear`, `toString`, `readFields`, static `skip`, `write`, `equals`, `hashCode`, static `decode`, static `encode`, static `readString`, static `writeString`, static `validateUTF8`, `bytesToCodePoint`, and `utf8Length`. `Text.Comparator` extends `WritableComparator` and compares byte ranges directly.

`TwoDArrayWritable` stores rectangular or jagged two-dimensional arrays of `Writable`. It exposes constructors by value class and optional `Writable[][]`, `set`, `get`, `toArray`, `readFields`, and `write`.

`UTF8` is the older string type. It implements `WritableComparable` and has constructors from empty, `String`, and `UTF8`; accessors and mutators include `getBytes`, `getLength`, `set(String)`, `set(UTF8)`, `readFields`, static `skip`, `write`, `compareTo`, `toString`, `equals`, `hashCode`, static `getBytes(String)`, `readString`, and `writeString`. The class is explicitly deprecated as `replaced by Text`, but `UTF8.Comparator` remains listed for raw comparison compatibility.

`VersionedWritable` is an abstract base for serialized types with a version byte. It exposes abstract `getVersion`, plus `write` and `readFields`. `VersionMismatchException` records expected and found version bytes and formats them in `toString`.

`VIntWritable` and `VLongWritable` are mutable variable-length integer wrappers. Both implement `WritableComparable`, provide default and value constructors, `set`, `get`, `readFields`, `write`, `equals`, `hashCode`, `compareTo`, and `toString`. They depend on Hadoop's variable-length integer encoding helpers.

`Writable` is the base serialization interface with `write(DataOutput)` and `readFields(DataInput)`. `WritableComparable` combines `Writable` and `Comparable`.

`WritableComparator` is the core comparison and raw-comparison utility. It has constructors for key class and optional instance creation, static comparator lookup/registration via `get` and `define`, `getKeyClass`, `newKey`, object and byte-array `compare` overloads, `compareBytes`, `hashBytes`, primitive byte readers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`). This is a critical API for sort/shuffle paths because it can compare serialized keys without materializing Java objects.

`WritableFactories`, `WritableFactory`, and `WritableName` provide object creation and legacy name mapping. `WritableFactories` lets clients `setFactory`, `getFactory`, and create new writable instances by class and optional `Configuration`. `WritableFactory` exposes `newInstance`. `WritableName` maps classes to compact or stable names through `setName`, `addName`, `getName`, and `getClass`.

`WritableUtils` collects serialization helpers: compressed byte arrays and strings, string arrays, display helpers, cloning via `Configuration`, `cloneInto`, variable-length integer read/write, sign and encoded-size helpers, enum read/write by string, exact skipping, and conversion of writables to byte arrays. These helpers are wire-format sensitive and are used throughout Hadoop's IPC, metadata, and file formats.

### Compression APIs

`org.apache.hadoop.io.compress` defines the stream codec abstraction and concrete codecs.

`CompressionCodec` is the central interface. It creates compression and decompression streams with or without pooled `Compressor`/`Decompressor` instances, exposes compressor/decompressor implementation classes, creates new compressor/decompressor instances, and returns the default file extension. `CompressionCodecFactory` discovers codecs from `io.compression.codecs`, defaults to gzip and zip per Javadoc, maps filename suffixes to codecs, can read/write codec class lists in `Configuration`, strips suffixes, and includes a diagnostic `main`.

`CodecPool` is a global pool for reusing compressor and decompressor instances. Its APIs are `getCompressor`, `getDecompressor`, `returnCompressor`, and `returnDecompressor`. The pool exists to save allocation and native codec initialization cost, so callers must return objects after use and must not reuse objects after returning them.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream bases. Input streams wrap a protected final `InputStream`, require byte-buffer `read`, and expose `resetState` for repositioned underlying streams. Output streams wrap a protected final `OutputStream`, require byte-buffer `write`, and expose `finish` and `resetState`; `finish` writes remaining compressed data without closing the underlying stream.

`Compressor` and `Decompressor` define the codec state machines. `Compressor` supports `setInput`, `needsInput`, `setDictionary`, byte counters, `finish`, `finished`, `compress`, `reset`, and `end`. `Decompressor` mirrors this with `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `reset`, and `end`. These APIs imply a loop in which callers provide bytes when needed, drain compressed/decompressed bytes, finish or detect end, then reset or end native state.

`BZip2Codec` implements `CompressionCodec` but documents that compressor/decompressor-object variants are unsupported and throw `UnsupportedOperationException`; it only creates BZip2 streams and advertises `.bz2`. `DefaultCodec`, `GzipCodec`, and nested `GzipInputStream`/`GzipOutputStream` expose standard stream creation, compressor/decompressor creation, extensions, available/read/write/skip/finish/reset/close lifecycle APIs.

`LzoCodec` implements configurable LZO compression and exposes `isNativeLzoLoaded`, stream creation, native compressor/decompressor creation, and extension. `LzopCodec` extends it for LZOP framing and includes nested `LzopDecompressor`, `LzopInputStream`, and `LzopOutputStream` APIs for header parsing/writing and checksum verification/reset. The LZO compressor/decompressor implementations in `org.apache.hadoop.io.compress.lzo` expose native-load checks, input/dictionary state, finish/finished, compress/decompress, byte counters, reset/end/finalize, `LZO_LIBRARY_VERSION`, and enum strategy types.

`org.apache.hadoop.io.compress.bzip2` exposes the BZip2 implementation details. `BZip2Constants` is public for historical reasons and includes public constants plus a public `rNums` array; its documentation explicitly warns that `rNums` should not be public because malicious code can modify it. `BZip2DummyCompressor` and `BZip2DummyDecompressor` implement the interfaces but are dummy implementations. `CBZip2InputStream` and `CBZip2OutputStream` implement raw BZip2 payload processing where callers are responsible for the outer `BZ` magic bytes. The output stream exposes block-size selection, `finish`, `close`, `flush`, write methods, block-size constants, and historically protected sorting constants.

`org.apache.hadoop.io.compress.zlib` includes wrappers around Java zlib and Hadoop native-aware factories. `BuiltInZlibDeflater` and `BuiltInZlibInflater` adapt `java.util.zip.Deflater` and `Inflater` to the Hadoop interfaces. `ZlibCompressor` and `ZlibDecompressor` expose synchronized stateful native compression/decompression methods, byte counters, reset/end/finalize, and enum types for compression header, level, and strategy. `ZlibFactory` chooses appropriate zlib implementations from `Configuration` and reports whether native zlib is loaded.

### Retry And Serialization APIs

`org.apache.hadoop.io.retry` defines retry policy construction and dynamic retry proxies. `RetryPolicies` exposes fixed-sleep, maximum-time, proportional-sleep, exponential-backoff, exception-map, and remote-exception-map policies, plus constants `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`. `RetryPolicy.shouldRetry(Exception, int)` returns whether to retry, whether to suppress failure for void methods, or throws the original/derived exception to fail. The interface documentation requires implementations to be immutable. `RetryProxy.create` wraps an implementation of an interface with either one policy for all methods or a method-name-to-policy map with a default `TRY_ONCE_THEN_FAIL`.

`org.apache.hadoop.io.serializer` defines generic serialization plug-ins. `Serializer<T>` has `open(OutputStream)`, `serialize(T)`, and `close`; `Deserializer<T>` has `open(InputStream)`, `deserialize(T)`, and `close`. The deserializer contract is explicit that instances are stateful but must not buffer input because other producers may read from the same stream between calls.

`Serialization<T>` accepts classes and returns serializers/deserializers. `SerializationFactory` extends `Configured`, loads implementations from the `io.serializations` configuration property, and returns matching serializers, deserializers, or the selected `Serialization`. `WritableSerialization` adapts Hadoop `Writable` by delegating to `Writable.write` and `Writable.readFields`. `JavaSerialization` is marked experimental and supports Java `Serializable`; `JavaSerializationComparator` and the abstract `DeserializerComparator` show how raw byte comparison can deserialize objects and then use normal `Comparator` logic, while warning that custom raw comparators are better for compare-heavy operations.

### IPC, RPC, Metrics, Logging, And MapReduce Status

`org.apache.hadoop.ipc.Client` is the low-level Writable RPC client. Constructors bind a `Writable` value class, `Configuration`, and optional `SocketFactory`. It exposes static `setPingInterval`, `stop`, single-call overloads with address and optional `UserGroupInformation`, and a parallel `call` over arrays of parameters and addresses. Parallel results may contain null for timed-out or errored calls.

`RemoteException` is a serializable wrapper for exceptions thrown by remote code. It records a class name and message, exposes `getClassName`, unwrap methods with optional lookup classes, XML serialization through `writeXml`, and reconstruction from SAX attributes via `valueOf`.

`RPC` is the higher-level proxy mechanism. It exposes `waitForProxy`, several `getProxy` overloads with protocol class, client version, address, optional user ticket, `Configuration`, and optional `SocketFactory`, `stopProxy`, an expert parallel reflective `call`, and `getServer` overloads to expose protocol implementation instances. The documentation defines the protocol restrictions: protocol methods are Java interface methods whose parameters and returns must be primitives, `String`, `Writable`, or arrays of those, and methods should throw only `IOException`. `RPC.Server` extends the generic `Server` and dispatches calls to an implementation instance. `RPC.VersionMismatch` records protocol/interface name, client version, and server version.

`Server` is the abstract IPC service. Constructors define bind address, port, parameter `Writable` class, handler count, `Configuration`, and optional server name. Static context APIs expose the current server, remote IP, and remote address while executing an RPC. `bind` wraps `ServerSocket.bind` with better `BindException` and `UnknownHostException` reporting. Instance APIs include socket send-buffer sizing, synchronized `start`, `stop`, `join`, synchronized `getListenerAddress`, abstract `call(Writable, long)`, connection and call-queue counters, public `HEADER`, `CURRENT_VERSION`, `LOG`, and protected `rpcMetrics`.

`VersionedProtocol` is the marker/super-interface for Hadoop RPC protocols. Implementations must expose `getProtocolVersion(String protocol, long clientVersion)` and are expected to have a static `versionID` field.

`org.apache.hadoop.ipc.metrics.RpcMetrics` implements `org.apache.hadoop.metrics.Updater`, registers RPC/JMX metrics, and exposes public mutable `MetricsTimeVaryingRate` fields for queue and processing times plus a metrics map. `RpcMgtMBean` exposes sampled operation counts, average/min/max processing time, average/min/max queue time, min/max reset, open connection count, and call queue length. Its documentation notes that the default null metrics context does not periodically update sampled averages unless configured with `NullContextWithUpdateThread`.

`org.apache.hadoop.log.LogLevel` provides runtime log-level adjustment. It exposes `main(String[])`, public `USAGES`, and a nested servlet `LogLevel.Servlet` with `doGet(HttpServletRequest, HttpServletResponse)`. This integrates both CLI and HTTP servlet control paths.

The chunk ends in `org.apache.hadoop.mapred.ClusterStatus`. Visible APIs include `getTaskTrackers`, `getMapTasks`, `getReduceTasks`, `getMaxMapTasks`, `getMaxReduceTasks`, `getJobTrackerState`, `write(DataOutput)`, and `readFields(DataInput)`. The class implements `Writable`, so the remaining adjacent chunk must complete its serialization and any additional status accessors.

## Control Flow And Data Flow Inferred From The API

SequenceFile and SetFile flows are file-format flows. Writers are constructed with filesystem/configuration/path/type metadata, append typed or raw key/value records, optionally emit sync points, report a synchronized seekable length, and close. Sorter segment descriptors iterate raw keys and values from sorted merge segments, optionally preserve temporary input, and clean up segment resources after merging. SetFile writes sorted keys as a MapFile-backed set and reads by seek, next, or exact get.

Writable serialization flows are `write(DataOutput)` followed by `readFields(DataInput)` into an existing object. `WritableComparator` and `Text.Comparator` allow sort and lookup code to compare raw serialized bytes directly, avoiding object allocation. `WritableFactories` and `WritableName` support deserializers that only know a class or legacy wire name and need to instantiate a writable before reading fields.

Text/UTF8 data flow centers on byte-backed UTF-8 storage. `Text` maintains a byte array plus logical length, supports setting from strings, byte slices, and other `Text` values, appending raw UTF-8 bytes, validating UTF-8, decoding/encoding through `ByteBuffer`, and reading/writing length-prefixed strings. `UTF8` remains for backward compatibility but should not be used for new APIs.

Compression flows have a consistent lifecycle: choose a `CompressionCodec` directly or through `CompressionCodecFactory`, optionally borrow a compressor/decompressor from `CodecPool`, create a compression/decompression stream, repeatedly write/read bytes, call `finish` when needed, close streams, reset state if reusing over repositioned streams, then return or end codec state. Native-capable codecs add load checks and configuration-driven implementation selection.

Retry flow is proxy-mediated. Client code wraps an implementation with `RetryProxy`; invocation failures are passed to the configured `RetryPolicy.shouldRetry` with the current retry count; the policy either allows another attempt, suppresses a void-method failure, or throws to fail the call. Remote-exception-aware policies can route based on wrapped remote exception class names.

SerializationFactory flow is configuration-driven. The factory reads a configured list of `Serialization` implementations, asks each whether it accepts a target class, then returns an appropriate `Serializer` or `Deserializer`. The serializer/deserializer lifecycle is explicit: open a stream, process one or more objects, close and release resources.

IPC flow is split between low-level Writable calls and protocol proxy calls. `Client.call` sends a Writable parameter to a `Server` address and receives a Writable result, while `RPC.getProxy` creates a Java dynamic proxy for a `VersionedProtocol`. Server-side code receives a Writable call parameter, dispatches through `Server.call` or `RPC.Server.call`, records queue/processing metrics, and exposes request context through static accessors. `RemoteException` carries remote failures across the wire and can be unwrapped into local IOException subclasses when possible.

Metrics flow is push-based through `RpcMetrics.doUpdates(MetricsContext)`, with JMX-facing values exposed through `RpcMgtMBean`. Log-level flow is command or servlet driven, changing logging configuration at runtime through `LogLevel`.

## State And Persistence Behavior

Persistent state in this chunk is mostly serialized byte streams and filesystem-backed Hadoop container formats. `SequenceFile.Writer`, `SetFile.Writer`, `MapFile` inheritance, and `ClusterStatus.write/readFields` all encode stable wire/file formats. Changes to field order, variable-length integer encoding, text length encoding, sync marker behavior, compression framing, or writable class names would break compatibility with data written by Hadoop 0.19.2.

`SequenceFile.Sorter.SegmentDescriptor` owns merge-segment state: path, offset, length, raw key buffer, reader position, sync behavior, and cleanup policy are implied by the API. The `preserveInput` flag controls whether temporary segment files are deleted when no longer needed, making it relevant to disk cleanup and post-failure debugging.

Compression classes hold mutable stream and native state. Compressor/decompressor objects track input buffers, dictionaries, finish flags, byte counters, and native resources; `reset` reuses them, while `end` releases resources. `CodecPool` adds process-global pooled state, so state leakage between users is a risk unless callers reset and return instances correctly. `CBZip2InputStream` documentation notes significant memory allocation and lack of thread safety.

`SortedMapWritable`, `VIntWritable`, `VLongWritable`, `Text`, and `UTF8` are mutable value holders. Reusing instances during deserialization is expected and efficient, but callers must avoid retaining references when later reads mutate the same object.

Retry policies are documented as immutable, while retry proxy instances keep invocation policy state externally through retry counts. `RetryPolicies.RETRY_FOREVER` can intentionally make calls persistent across transient failures but can also hide permanent failures.

IPC clients and servers own network connections, handler threads, call queues, socket buffers, metrics, and protocol version negotiation state. `Client.stop`, `Server.stop`, and `Server.join` are the lifecycle boundaries. Static server context (`Server.get`, remote IP/address accessors) is per-call ambient state and must be correct under concurrent handler threads.

`RpcMetrics` stores sampled queue and processing time state. Its public metric fields are intentionally mutable and readable by JMX. `RpcMgtMBean.resetAllMinMax` mutates min/max tracking state, and metrics update behavior depends on configured metrics context.

## Dependencies And Integration Points

This chunk sits at the intersection of most Hadoop common subsystems:

- Filesystem and file formats: `FileSystem`, `Path`, `SequenceFile`, `MapFile`, `SetFile`, sync points, sorted merge segments, and compressed sequence values.
- Configuration: `Configuration` configures writers, codecs, serialization factories, zlib/native behavior, IPC clients/servers, and metrics.
- Hadoop serialization: `Writable`, `WritableComparable`, `RawComparator`, `WritableComparator`, `WritableFactory`, `WritableName`, variable-length integer utilities, and text encoding utilities.
- Java IO and networking: `DataInput`, `DataOutput`, streams, `Closeable`, `ServerSocket`, `InetSocketAddress`, `InetAddress`, `SocketFactory`, and servlet request/response types.
- Compression libraries: Java zlib (`Deflater`/`Inflater`), Hadoop native zlib, LZO native bindings, LZOP framing, BZip2 stream implementation, and codec pooling.
- Reflection and proxies: `RPC`, `RetryProxy`, protocol interfaces, method dispatch, remote exception reconstruction, and version negotiation.
- Security/user identity: IPC call overloads accept `UserGroupInformation` tickets.
- Metrics and management: Hadoop metrics contexts, metrics utility rates, JMX MBean exposure, and runtime log-level servlet/CLI integration.
- MapReduce: `ClusterStatus` exposes job tracker and task capacity state through a `Writable` API consumed by MapReduce clients.

## Risks And Edge Cases

The biggest risk is treating this XML as implementation source. It is an API manifest: it can identify contracts and compatibility surfaces, but not actual branching, locking correctness, exception paths, or resource cleanup details beyond documentation and modifiers.

The chunk boundaries are partial. The start omits the class header and constructor details immediately before the visible `SegmentDescriptor` methods unless reconciled with the previous chunk. The end omits the tail of `ClusterStatus`, including the rest of `readFields` and any following methods or fields. A final merged report must not overstate completeness for those two boundary types.

Several APIs are wire-format sensitive. `WritableUtils` vint/vlong encoding, `Text` UTF-8 validation and string length handling, `UTF8` compatibility, `VersionedWritable`, `WritableName`, and `ClusterStatus` serialization must remain stable for old data and RPC compatibility. Even small changes can make old sequence files, map files, or IPC payloads unreadable.

Raw comparator APIs are performance and correctness critical. `WritableComparator.compareBytes`, primitive byte readers, `Text.Comparator`, and `DeserializerComparator` affect sorting, partitioning, map output shuffle behavior, and MapFile/SetFile ordering. Incorrect byte ordering or signedness handling can corrupt sorted-file invariants.

Resource lifecycle is prominent. `SequenceFile.Writer.close`, `SegmentDescriptor.cleanup`, `CompressionOutputStream.finish`, compressor/decompressor `reset` and `end`, `CodecPool.return*`, serializer/deserializer `close`, `Client.stop`, and `Server.stop/join` are all cleanup points. Leaks here would manifest as file descriptor leaks, native memory leaks, hanging IPC threads, or temporary file buildup.

Compression has many compatibility traps. BZip2 codec methods with compressor/decompressor arguments are documented as unsupported; code that assumes every `CompressionCodec` supports pooled codec objects will fail for BZip2. CBZip2 streams intentionally exclude the outer `BZ` magic bytes, requiring callers to handle headers exactly. LZO and zlib behavior depends on native libraries and configuration, so tests must cover native-loaded and fallback paths.

`BZip2Constants.rNums` is a public mutable array and the documentation calls out malicious modification risk. Any code relying on this constant must assume external mutation is possible in the same JVM.

Threading and synchronization differ by API. `SequenceFile.Writer` synchronizes append/close/getLength, zlib compressor/decompressor methods are partly synchronized, `CBZip2InputStream` is explicitly not thread-safe, and `Server.start/stop/join/getListenerAddress` are synchronized. Pooled compressors, serializers, and writable value instances should not be shared concurrently unless documented.

Retry policies can change failure semantics. `TRY_ONCE_DONT_FAIL` suppresses void-method failures, `RETRY_FOREVER` can hang indefinitely, and exception-map policies rely on local or remote exception classification. Misclassification can cause retry storms or premature failure.

RPC protocol constraints are narrow. `RPC` supports primitives, `String`, `Writable`, and arrays of those, with protocol methods expected to throw only `IOException`. Adding unsupported types or unchecked exception behavior can break proxy serialization or remote exception handling. `RPC.VersionMismatch` and `VersionedProtocol.getProtocolVersion` are central to rolling upgrades.

Metrics can be misleading if the metrics context does not periodically call updates. The MBean documentation explicitly warns that the default null context does not average sampled data unless configured with an update thread.

The explicit deprecations are important migration signals: new code should prefer `Text` over `UTF8`, and `SetFile.Writer` construction should pass `Configuration`.

## Test Signals

For this JDiff XML itself, useful validation is structural: XML parsing, package/type ordering, signature extraction, deprecation extraction, and comparison against adjacent JDiff versions. Tests should assert that expected classes, methods, fields, checked exceptions, synchronization flags, and deprecation messages are present.

For implementations described by this API surface, strong test signals include:

- SequenceFile tests that write/read typed and raw records, use sync points and `getLength`/seek, exercise block compression, sort/merge segments, verify `preserveInput` cleanup behavior, and confirm metadata and serializers are selected correctly.
- SetFile/MapFile tests that require strictly increasing keys, comparator-based lookup, `seek`, `next`, and exact `get` behavior.
- Writable tests that round-trip `Text`, `UTF8`, `VIntWritable`, `VLongWritable`, `SortedMapWritable`, `TwoDArrayWritable`, versioned writables, enum/string helpers, compressed strings, and variable-length integer edge cases.
- Raw comparator tests that compare serialized and object forms for the same keys, including negative numbers, multi-byte UTF-8, invalid UTF-8 rejection, and boundary byte slices.
- Compression tests for codec lookup by extension, codec class configuration, BZip2 unsupported pooled methods, CBZip2 header handling, gzip/default streams, LZO native availability, LZOP checksum/header behavior, zlib native/fallback factory selection, compressor reset/end, and `CodecPool` reuse.
- Retry tests that verify fixed, maximum-time, proportional, exponential, exception-map, remote-exception-map, no-retry, no-fail, and forever policies through `RetryProxy`.
- SerializationFactory tests that load configured serialization implementations, select `WritableSerialization` and `JavaSerialization`, and ensure deserializers do not over-buffer shared streams.
- IPC/RPC tests that cover direct Writable calls, parallel calls with timeout/error nulls, proxy creation and stop, protocol version negotiation, `VersionMismatch`, `RemoteException` unwrap/XML round-trip, server context remote address access, bind error quality, lifecycle stop/join, and call queue/open connection metrics.
- Metrics/JMX tests that call `RpcMetrics.doUpdates`, read `RpcMgtMBean` sampled values, reset min/max, and verify behavior under a null context versus an update-thread context.
- LogLevel tests that exercise both CLI argument handling and servlet `doGet` behavior.
- ClusterStatus compatibility tests that serialize with Hadoop 0.19.2-compatible data and read back task tracker counts, running map/reduce counts, max capacities, and `JobTracker.State`.

The merge/reconciliation lane should combine this chunk with neighboring chunks before making file-level claims about complete package coverage, especially for `SequenceFile.Sorter.SegmentDescriptor` and `ClusterStatus`.
