# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop_0.20.0.xml lines 12399-18725

## Scope

This chunk is a JDiff/API XML slice for Hadoop 0.20.0. It begins in the middle of the public API entry for `org.apache.hadoop.io.SequenceFile.Reader`, continues through sequence-file sorting/writing, set and sorted-map Writables, text and primitive Writable support, compression, retry, serialization, and the beginning of Hadoop IPC/RPC. It ends inside `org.apache.hadoop.ipc.Server` at the public static `bind(ServerSocket, InetSocketAddress, int)` entry.

The file is generated API metadata, not Java implementation source. The research surface is therefore the compatibility contract: exported packages, classes, nested types, constructors, methods, fields, visibility/static/final/synchronized/abstract flags, inheritance, implemented interfaces, declared exceptions, deprecation markers, and embedded Javadoc.

## Purpose

The `org.apache.hadoop.io` section defines the core binary serialization and comparison contracts used throughout Hadoop 0.20.0. It covers `SequenceFile` read/write/sort mechanics, `SetFile` storage, sorted map Writables, UTF-8 text containers, variable-length integer Writables, version-checked Writables, raw byte comparators, Writable factories/names, and shared serialization utilities.

The `org.apache.hadoop.io.compress` section exposes the codec abstraction used by SequenceFiles, MapReduce input/output, and extension-based codec discovery. It includes block and stream compression wrappers, bzip2/gzip/default codecs, compressor/decompressor pooling, abstract compression streams, codec lookup, and zlib-backed compressor/decompressor implementations.

The `org.apache.hadoop.io.retry` and `org.apache.hadoop.io.serializer` sections provide reusable infrastructure for retrying interface method calls and for pluggable object serialization. These APIs integrate with RPC clients, MapReduce shuffle/sort paths, and configurable Hadoop data encodings.

The `org.apache.hadoop.ipc` section begins Hadoop's Writable-based IPC/RPC framework. It documents the client call surface, remote exception wrapping, dynamic protocol proxies, RPC server construction/authorization, protocol version mismatch reporting, and the start of the abstract server contract.

## Important APIs, Types, and Functions

### SequenceFile and SetFile

- `SequenceFile.Reader` tail APIs expose synchronized current-value retrieval, `next` overloads for Writable or object keys/values, raw key/value reads through `DataOutputBuffer` and `SequenceFile.ValueBytes`, deprecated raw `next(DataOutputBuffer)`, `seek`, `sync`, `syncSeen`, `getPosition`, and `toString`.
- `SequenceFile.Sorter` sorts and merges sequence files using key/value classes or a supplied `RawComparator`. It exposes merge fan-in and memory controls, progress reporting, file sort methods, `sortAndIterate`, several merge overloads, attribute-cloning writer creation, and `writeFile` from a raw iterator.
- `SequenceFile.Sorter.RawKeyValueIterator` is the raw sorted stream contract: `next`, `getKey`, `getValue`, `close`, and `getProgress`.
- `SequenceFile.Sorter.SegmentDescriptor` models a merge segment by offset, length, and path. It supports sync handling, input-preservation flags, ordering/equality/hash, raw key/value iteration, key access, and cleanup that can be customized by subclassing.
- `SequenceFile.ValueBytes` abstracts raw sequence-file values with methods to write uncompressed bytes, write already-compressed bytes, and report stored size.
- `SequenceFile.Writer` creates sequence-format files with filesystem/configuration/path/key/value parameters, optional progress and metadata, and optional replication/block-size settings. It exposes key/value class getters, compression codec getter, sync point creation, synchronized close, synchronized object/Writable append, synchronized raw append, synchronized length reporting, and protected serializers for keys and compressed/uncompressed values.
- `SetFile` is a `MapFile`-based file set. `SetFile.Reader` supports seek, sequential next-key reads, and exact key lookup. `SetFile.Writer` creates sorted key-only files and requires appended keys to be strictly greater than the previous key; the older constructor without `Configuration` is deprecated.

### Writable Core and Text Types

- `SortedMapWritable` extends `AbstractMapWritable` and implements `SortedMap`, exposing comparator/key-range views, map mutation/accessors, and Writable `readFields`/`write`.
- `Stringifier` is a closeable object-to-string and string-to-object conversion interface.
- `Text` is the main UTF-8 byte-backed `WritableComparable`. It has string, copy, and byte-array constructors; raw byte/length access; byte-position `charAt`; byte-level `find`; `set` overloads; byte-range `append`; `clear`; string conversion; read/write/skip; equality/hash; strict or replacement UTF-8 `decode`; `encode`; `readString`/`writeString`; UTF-8 validation; byte-buffer code-point traversal; and encoded-length calculation.
- `Text.Comparator` extends `WritableComparator` to compare serialized `Text` bytes directly.
- `TwoDArrayWritable` serializes rectangular or nested `Writable[][]` data with a declared value class.
- `UTF8` is the deprecated predecessor to `Text`, still public and `WritableComparable`. It exposes raw bytes/length, string/copy construction, setters, read/write/skip, compare/equality/hash/string conversion, and static string helpers. `UTF8.Comparator` is its raw comparator.
- `VersionedWritable` adds a single-byte version gate to Writable records. `readFields` checks the serialized version against `getVersion()` and throws `VersionMismatchException` on mismatch.
- `VIntWritable` and `VLongWritable` wrap `int` and `long` values with Hadoop variable-length encodings and `WritableComparable` ordering.
- `Writable` defines `write(DataOutput)` and `readFields(DataInput)`. `WritableComparable` combines `Writable` with Java comparison for sort keys.
- `WritableComparator` provides the comparator registry, reflective/new-key construction, object comparison, raw serialized-byte comparison, byte-array primitive parsing, vint/vlong parsing, and byte hashing.
- `WritableFactories`/`WritableFactory` register and construct Writable instances, including non-public Writable classes used by `ObjectWritable`.
- `WritableName` registers alternate stable names for Writable classes so serialized class-name references can survive class renames.
- `WritableUtils` contains compressed byte/string array helpers, plain string/string-array helpers, byte display formatting, serialization-based clone and deprecated `cloneInto`, vint/vlong read/write/sign/size helpers, enum name serialization, exact skipping, and conversion of Writable arrays to bytes.

### Compression

- `BlockCompressorStream` and `BlockDecompressorStream` adapt block-oriented compressors/decompressors to Hadoop compression streams. Blocks carry uncompressed length followed by length-prefixed compressed chunks.
- `BZip2Codec` implements `CompressionCodec` with bzip2 streams and `.bz2` extension, but its compressor/decompressor factory and supplied-compressor stream APIs are documented as unsupported.
- `CodecPool` is the global pool for reusable compressor and decompressor instances.
- `CompressionCodec` defines the codec contract: create compression/decompression streams with or without supplied state objects, report compressor/decompressor classes, create state objects, and provide a default extension.
- `CompressionCodecFactory` loads configured codec classes from `Configuration`, maps filename suffixes to codecs, exposes static codec-class list accessors, removes suffixes, and has a command-line diagnostic entry point.
- `CompressionInputStream` and `CompressionOutputStream` are abstract stream bases with protected wrapped `in`/`out` fields, lifecycle hooks, and reset/finish contracts.
- `Compressor` and `Decompressor` define zlib-like state machines: `setInput`, optional dictionary, input/dictionary needs, byte counters where applicable, `finish`/`finished`, `compress`/`decompress`, `reset`, and `end`.
- `CompressorStream` and `DecompressorStream` implement stream wrappers around those state machines, with protected buffers, closed/eof state, reset behavior, and normal stream operations.
- `DefaultCodec` implements `CompressionCodec` and `Configurable` for Hadoop's default deflate path. `GzipCodec` extends it for gzip and provides nested `GzipInputStream`/`GzipOutputStream` wrappers.
- `org.apache.hadoop.io.compress.bzip2` exposes bzip2 constants, dummy compressor/decompressor implementations for unsupported pool integration, `CBZip2InputStream`, and `CBZip2OutputStream` with block-size constants and bzip2 block writing/finalization helpers.
- `org.apache.hadoop.io.compress.zlib` includes Java built-in adapters (`BuiltInZlibDeflater`, `BuiltInZlibInflater`), native-oriented `ZlibCompressor`/`ZlibDecompressor`, enum types for zlib headers, levels, and strategies, and `ZlibFactory` for native availability and implementation selection.

### Retry, Serialization, and IPC

- `RetryPolicies` exposes stock immutable policies: try once and fail, try once without failing void methods, retry forever, bounded fixed sleep, maximum-time fixed sleep, proportional sleep, exponential backoff, exception-class maps, and remote-exception maps.
- `RetryPolicy.shouldRetry(Exception, int)` either returns true to retry, returns false to suppress a void-method failure, or throws to stop retrying.
- `RetryProxy.create` builds dynamic proxies for an interface and implementation using either one policy for all methods or a method-name to policy map with a default fail-once policy.
- `Serializer`, `Deserializer`, and `Serialization` define stream-bound object serialization. `SerializationFactory` reads `io.serializations` from `Configuration` and chooses a supporting implementation for a class.
- `WritableSerialization` adapts Hadoop `Writable` objects to the generic serialization framework. `JavaSerialization` and `JavaSerializationComparator` provide experimental Java `Serializable` support.
- `DeserializerComparator` is a raw comparator that deserializes byte slices before comparing, intended as a generic but slower fallback compared with true byte-level comparators.
- `Client` is the low-level IPC client for one-Writable request/response calls. It supports optional `SocketFactory`, ping interval configuration, single calls with protocol and `UserGroupInformation`, deprecated credential-less calls, parallel calls to multiple addresses, `stop`, and a public Commons Logging `LOG`.
- `RemoteException` carries remote exception class names and messages, can unwrap known remote exception types or instantiate local exception classes by string constructor, and can serialize to/from XML attributes.
- `RPC` creates and waits for `VersionedProtocol` proxies, stops proxies, performs parallel reflective calls, and constructs `RPC.Server` instances. The class documentation defines supported protocol parameter/return types as primitives, `String`, `Writable`, and arrays of those types, with IOException-only protocol methods.
- `RPC.Server` extends `Server`, dispatches protocol calls to an implementation instance, and exposes authorization against `Subject` and `ConnectionHeader`.
- `RPC.VersionMismatch` records protocol name, client version, and server version.
- `Server` begins here with protected constructors, static current-server and remote-address accessors, and the public static socket `bind` utility. The remaining server lifecycle and abstract call methods are outside this chunk.

## Control Flow

Sequence-file read flow is cursor oriented. `Reader.next` advances to a key or key/value pair, `getCurrentValue` retrieves the value for the last key, raw readers fill caller-provided buffers, and `sync(position)` moves to the next sync marker. `seek(position)` is constrained to positions previously returned by `Writer.getLength()`, while arbitrary positioning should use sync.

Sequence-file write flow creates a `Writer` with filesystem, configuration, classes, metadata, and optional storage parameters. Callers append Writable/object pairs or raw key/value bytes, optionally create sync markers, query a synchronized length suitable for later seek, and close the writer. Sorter flow reads raw sequence-file records, sorts with a `RawComparator`, spills and merges according to memory/fan-in settings, returns a raw iterator or writes a final output file, and optionally deletes inputs or temporary segments during cleanup.

Writable control flow is read/write reuse: objects serialize themselves to `DataOutput` and restore into existing instances from `DataInput`. Raw comparison flow bypasses allocation by comparing serialized byte slices through `WritableComparator` or specialized comparators such as `Text.Comparator`.

Text flow operates on UTF-8 byte positions. Search, append, code-point lookup, validation, and bytewise comparison can avoid Java `String` construction; decode/encode helpers bridge to strings when needed. Deprecated `UTF8` follows older string serialization semantics and remains part of the compatibility surface.

Compression flow is stream and state-machine based. Codecs create streams directly or with pooled state. A compressor receives input when `needsInput()` is true, can receive a dictionary, emits bytes through `compress`, and transitions through `finish`/`finished`, `reset`, and `end`. Decompressors mirror this with dictionary-needs and eof handling. Block compression adds an outer framing of uncompressed block lengths and compressed sub-block lengths.

Retry flow wraps an implementation with a dynamic proxy. Each thrown exception is passed with the current retry count to a `RetryPolicy`; the policy chooses retry, suppression for void methods, or rethrow/failure. Remote-exception policies depend on `RemoteException` class-name unwrapping.

Serialization flow starts with `SerializationFactory`, which loads configured serialization classes and selects the first whose `accept(Class)` matches. Serializers/deserializers bind streams with `open`, process objects one at a time, and release resources with `close`. Deserializers are explicitly stateful but must not buffer beyond the object boundary because other producers may read from the same stream.

IPC flow starts with `Client.call` or an `RPC.getProxy` proxy. The client serializes a Writable request, sends it to an address with protocol and user credentials, and receives a Writable response or remote/network exception. `RPC.Server` receives a `Writable` call through `Server`, authorizes the subject/connection, invokes the protocol implementation, and returns a Writable response. Parallel call APIs send corresponding parameters to corresponding addresses and return null array entries for timed-out or errored calls.

## State and Persistence Behavior

This XML persists Hadoop 0.20.0's public API for compatibility checking. Runtime behavior must be verified against implementation sources, but the exported APIs define durable state contracts.

`SequenceFile.Reader`, `Writer`, `Sorter`, `ValueBytes`, and `SegmentDescriptor` define persistent sequence-file formats and raw key/value movement. Key/value class names, metadata, sync markers, compression type/codec, record lengths, raw value representation, and writer length positions are compatibility-sensitive.

`SetFile` persists sorted key-only data on top of `MapFile`; writer append order is part of the data invariant. `SortedMapWritable`, `Text`, `UTF8`, `TwoDArrayWritable`, `VersionedWritable`, `VIntWritable`, `VLongWritable`, and other Writables persist binary layouts through `DataInput`/`DataOutput`.

`Text` and `UTF8` expose raw backing arrays and logical lengths. Callers must treat only bytes before `getLength()` as valid. UTF-8 strictness, encoded length, and byte-position semantics affect persisted keys and sort order.

`WritableComparator`, `WritableFactories`, and `WritableName` maintain process-global registries. Registration order and test isolation can affect object construction, sorting, and class-name compatibility.

`WritableUtils` encodes compressed arrays/strings, vint/vlong values, enum names, and cloned objects. VInt/VLong boundary behavior is a shared wire-format dependency across many Hadoop APIs.

`CodecPool` holds process-global mutable compressor/decompressor instances. Compression streams hold buffers and codec state; `finish` writes final compressed data without necessarily closing the underlying stream, while `close` owns resource closure. zlib and bzip2 implementations may hold native or large internal state until `end`, reset, close, or finalization.

`CompressionCodecFactory` persists codec selection through `Configuration` and filename suffix conventions. Wrong suffix mappings or class-list changes alter which decompressor reads a file.

`RetryPolicies` are intended to be immutable, while `RetryProxy` keeps per-proxy method policy maps. Bad policy choice changes observable failure semantics, especially policies that suppress void failures or retry indefinitely.

`SerializationFactory` persists serialization choices through `io.serializations`. Durable bytes depend on the chosen serialization implementation and class availability.

`Client`, `RPC`, `RPC.Server`, and `Server` manage sockets, protocol classes, user tickets, handler counts, bind addresses, call queues, and per-call static/thread-local context. `RemoteException` persists a remote class name and message rather than a local exception object.

## Dependencies and Integration Points

- Java platform dependencies include `DataInput`, `DataOutput`, streams, `Closeable`, `IOException`, `ByteBuffer`, collections, `Comparator`, `Comparable`, `Serializable`, enums, reflection `Method`, sockets, `ServerSocket`, `InetSocketAddress`, `InetAddress`, `SocketFactory`, `Deflater`, `Inflater`, and `TimeUnit`.
- Hadoop configuration (`Configuration`, `Configured`, `Configurable`) drives sequence-file creation, Writable construction, codec discovery, zlib selection, serialization factory loading, IPC ping settings, and RPC proxy/client setup.
- Hadoop filesystem types (`FileSystem`, `Path`) are central to `SequenceFile`, `SetFile`, sorter segment paths, and output/input file handling.
- Hadoop IO dependencies include `Writable`, `WritableComparable`, `RawComparator`, `DataOutputBuffer`, `SequenceFile.Metadata`, serializers/deserializers, and compression interfaces.
- Hadoop utility integration includes `Progressable` and `Progress` for sequence-file sorting/writing progress.
- Security and authorization integration appears through `UserGroupInformation`, `Subject`, `ConnectionHeader`, and `AuthorizationException` in IPC/RPC paths.
- Logging uses Apache Commons Logging in `Client` and `CompressionCodecFactory`.
- XML integration for `RemoteException` uses SAX `Attributes` and `org.znerd.xmlenc.XMLOutputter`.
- Native or platform codec integration is represented by zlib factory selection and the bzip2 stream implementation.

## Risks and Edge Cases

- The chunk starts mid-`SequenceFile.Reader` and ends mid-`Server`; adjacent chunks are required for complete class-level coverage of those two API entries.
- JDiff metadata does not include method bodies. Exact sequence-file layout, compression framing details, RPC framing, socket lifecycle, synchronization internals, and cleanup behavior require implementation review.
- `SequenceFile.Reader.seek` only accepts writer-synchronized positions; using arbitrary offsets instead of `sync` can corrupt reader state or fail.
- `Writer.getLength()` may return the first key in a block-compression block rather than the last key just written; tests and split logic must not assume exact record-level positioning.
- Raw `ValueBytes.writeCompressedBytes` explicitly does not compress data if it is not already compressed; callers must know the value representation.
- Sorter merge fan-in, memory limits, temporary directories, delete-input flags, and segment cleanup can lose data if error paths are mishandled.
- `SetFile.Writer.append` requires strictly increasing keys. A comparator mismatch or duplicate key can make lookup behavior invalid.
- `Text.getBytes()` exposes backing storage beyond logical length. Treating capacity bytes as content can leak stale data into comparisons or serialization.
- UTF-8 strict versus replacement decode and byte-position `charAt` behavior must be pinned for malformed or multi-byte data.
- `UTF8` is deprecated but still part of the 0.20.0 API and serialized-data compatibility surface.
- `VersionedWritable` has a hard version mismatch gate. Backward-compatible migrations must work around or customize that behavior.
- VInt/VLong encodings have delicate first-byte sign/size boundaries; incompatibility breaks many Hadoop wire and file formats.
- `WritableComparator` raw comparison must agree with object comparison. Divergence causes sort/grouping bugs.
- Global registries in comparators, factories, names, and codec pools can leak state between tests or applications in the same JVM.
- `WritableUtils.cloneInto` is deprecated and its Javadoc parameter wording is easy to misread; implementation semantics should be checked before use.
- BZip2 codec methods with supplied `Compressor`/`Decompressor` are documented as unsupported; generic codec callers must handle `UnsupportedOperationException`.
- Compression `finish`, `flush`, `close`, `resetState`, `reset`, and `end` are separate lifecycle operations. Incorrect ordering can truncate output, leak resources, or reuse stale dictionaries.
- Native zlib availability is environment-sensitive, and `ZlibFactory` may choose different implementations across deployments.
- Decompressor byte counter docs in this old API are easy to confuse because compressor/decompressor input/output perspectives differ.
- Retry policies that return false suppress void failures; retry-forever can hang callers indefinitely.
- `RetryProxy` maps by method name, so overloaded methods cannot receive distinct policies through the simple name map.
- Java serialization is experimental and sensitive to Java class compatibility and `serialVersionUID`.
- `DeserializerComparator` deserializes during raw comparison and can be expensive in sort-heavy paths.
- Parallel IPC/RPC calls return null for timed-out or errored calls; callers must not treat null as a successful null response.
- `RemoteException.unwrapRemoteException` depends on local class availability and string constructors; otherwise specificity is lost.
- `Server.getRemoteIp` and `getRemoteAddress` can return null outside RPC context or on error.
- `RPC` protocol compatibility depends on protocol interfaces exposing and honoring version information through `VersionedProtocol`.

## Test Signals

- JDiff/API compatibility checks should cover every public/protected class, nested type, constructor, method, field, implemented interface, declared exception, synchronization flag, final/static flag, and deprecation marker in this line range.
- SequenceFile tests should cover Writable/object append and read, raw key/value read/write, `ValueBytes` compressed and uncompressed paths, sync marker creation, `seek` on `getLength()` positions, `sync` from arbitrary offsets, `syncSeen`, metadata and codec preservation, close behavior, and block-compression positioning.
- Sorter tests should cover comparator-based ordering, memory/factor settings, multi-input sort, `sortAndIterate`, merge overloads, progress reporting, temporary segment cleanup, delete-input true/false, and raw iterator close behavior.
- SetFile tests should cover strictly increasing append, duplicate/out-of-order rejection, comparator-specific lookup, sequential next, seek, and deprecated constructor compatibility.
- Writable tests should cover `SortedMapWritable` round trips, `Stringifier` close/error behavior, `TwoDArrayWritable` empty and ragged arrays, `VersionedWritable` mismatch failures, `VIntWritable`/`VLongWritable` min/max and boundary encodings, and `WritableUtils` compressed arrays, string arrays, enum names, cloning, and exact skip failures.
- Text/UTF8 tests should cover raw byte length versus capacity, byte-position search, multi-byte code points, malformed UTF-8 strict and replacement decode, encode/decode round trips, validation, comparators, static string helpers, and legacy `UTF8` serialized compatibility.
- Comparator/factory/name tests should prove raw comparison equals object comparison, registry lookup works under custom registrations, non-public Writable factories construct instances, aliases resolve, and registries do not leak across isolated tests.
- Compression tests should cover codec factory suffix resolution, configured codec classes, default extensions, `CodecPool` get/return/reuse/reset, block compression framing, stream reset after seek, gzip/default round trips, bzip2 unsupported compressor methods, zlib built-in versus native factory selection, dictionary paths, byte counters, finish/close ordering, and truncated/corrupt input.
- Retry tests should cover each stock policy at retry limits, sleep/backoff behavior with controlled time, exception and remote-exception maps, void suppression, retry-forever guard conditions in tests, and overloaded method-name mapping behavior.
- Serialization tests should cover `SerializationFactory` configuration ordering, Writable serialization object reuse, Java serialization comparator behavior, deserializer no-overbuffering expectations, close propagation, and unsupported class handling.
- IPC/RPC tests should cover single and parallel `Client.call`, deprecated and credential-aware overloads, ping interval configuration, proxy creation/stop, protocol version mismatch, remote exception unwrap, authorization failure, null results for failed parallel calls, server bind behavior, and remote address access inside and outside an RPC call.
