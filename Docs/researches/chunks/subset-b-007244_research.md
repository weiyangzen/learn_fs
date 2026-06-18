# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/hadoop-core_0.20.0.xml lines 12388-18733

## Scope And Purpose

This chunk is a JDiff XML API inventory for Hadoop Core 0.20.0, not implementation source. It captures the public and protected contracts exposed by the tail of `org.apache.hadoop.io`, the compression subpackages, retry and serializer APIs, and the opening IPC APIs. The practical research value is therefore compatibility-focused: it records which classes, interfaces, constructors, methods, fields, deprecations, synchronization markers, checked exceptions, and documentation promises formed the 0.20.0 binary/source API surface.

The covered source range begins immediately after most of `SequenceFile.Metadata`, then lists `SequenceFile.Reader`, `SequenceFile.Sorter`, `SequenceFile.Writer`, set/map/text/writable utilities, compression codecs and zlib/bzip2 adapters, retry proxies, pluggable serialization, and the first IPC client/RPC contracts. These APIs are central to Hadoop's storage format compatibility, MapReduce shuffle/sort pipelines, RPC payload encoding, file compression, and client/server protocol dispatch.

Because this is generated JDiff XML, control flow and state behavior must be inferred from API shape and embedded Javadocs. The document does not expose private fields or method bodies except where JDiff includes public/protected fields and documentation.

## `org.apache.hadoop.io` Data And File Format APIs

`SequenceFile.Reader` is the read-side contract for Hadoop sequence files. It opens a `Path` through a `FileSystem` and `Configuration`, exposes key/value class names and loaded classes, reports compression mode (`isCompressed`, `isBlockCompressed`, `getCompressionCodec`), exposes file metadata, and provides object, `Writable`, and raw-record read paths. The raw API uses `DataOutputBuffer` plus `SequenceFile.ValueBytes`, and one old `next(DataOutputBuffer)` overload is explicitly deprecated in favor of `nextRaw(DataOutputBuffer, SequenceFile.ValueBytes)`. Positioning APIs (`seek`, `sync`, `syncSeen`, `getPosition`) show the persistent on-disk format includes sync markers and byte offsets; callers must use positions returned by `SequenceFile.Writer.getLength()` for exact `seek`, or use `sync` for arbitrary offsets.

`SequenceFile.Writer` is the write-side contract. It records key/value classes, compression codec, and exposes `append(Writable, Writable)`, object-based `append(Object, Object)`, and `appendRaw(byte[], int, int, ValueBytes)` paths. `sync()` and `getLength()` form the paired contract used by readers for split-safe seeking. Public/protected serializer fields (`keySerializer`, `uncompressedValSerializer`, `compressedValSerializer`) show integration with `org.apache.hadoop.io.serializer.Serializer` rather than hard-coding only `Writable` serialization.

`SequenceFile.Sorter` provides external sort and merge over sequence files. Its constructors accept either key/value classes or a `RawComparator`, tying sort order to Hadoop's byte-level comparison system. It exposes tuning knobs for merge fan-in (`setFactor`/`getFactor`), memory (`setMemory`/`getMemory`), and progress callbacks (`setProgressable`). Sort/merge overloads operate on arrays of `Path`, `SegmentDescriptor` lists, temp directories, and `deleteInput` flags. `cloneFileAttributes`, `writeFile`, and merge overloads indicate this API preserves sequence-file attributes while materializing sorted output.

`SequenceFile.Sorter.RawKeyValueIterator` is the streaming merge iterator contract. It returns current key bytes, current `ValueBytes`, advances with `next()`, reports `Progress`, and must be closed. `SequenceFile.Sorter.SegmentDescriptor` models a file segment with offset/length/path, supports sync alignment (`doSync`), input preservation, ordering/equality, raw key/value reads, and cleanup. These APIs are sensitive to resource ownership because cleanup may delete inputs unless preservation is requested.

`SequenceFile.ValueBytes` abstracts value payloads without requiring immediate deserialization. It can write uncompressed or compressed bytes to a `DataOutputStream` and report size. This is important for raw sort/merge paths: keys can be compared as bytes while values are copied through without object allocation.

`SetFile` is a `MapFile` specialization for sets. Its reader seeks and iterates keys and its writer appends only keys, with values implied by the set representation. The constructors preserve older configuration ordering as well as newer `Configuration, FileSystem, String, ...` signatures and support custom `WritableComparator` plus `SequenceFile.CompressionType`.

`SortedMapWritable` extends `AbstractMapWritable` and implements the `SortedMap` surface: comparator, first/last key, head/sub/tail maps, map mutation/query methods, and `readFields`/`write`. It persists class metadata through `AbstractMapWritable` and actual entries through `Writable` serialization, while exposing Java collection views.

`Stringifier` is a small lifecycle interface for converting objects to and from strings. It includes `toString(Object)`, `fromString(String)`, and `close()`, which implies implementations may hold configuration or parser state despite representing string conversion.

`Text` is the primary UTF-8 byte-backed string type. It exposes byte buffer access (`getBytes`, `getLength`), Unicode code point lookup (`charAt`), substring search (`find` overloads), multiple setters from `String`, `Text`, byte arrays, and byte-array slices, append/clear, `Writable` read/write, equality/hash, static UTF-8 encode/decode helpers with replacement control, `readString`/`writeString`, UTF-8 validation, `bytesToCodePoint`, and `utf8Length`. `Text.Comparator` extends `WritableComparator` for byte-level ordering. The API makes clear that `Text` length is byte length, not Java `String.length()`, which is a compatibility and correctness boundary for non-ASCII data.

`UTF8` is the older string wrapper. It has similar constructors, byte/length accessors, setters, `readFields`, `write`, `skip`, `compareTo`, `toString`, equality/hash, and static byte/string helpers. Its presence beside `Text` is a legacy compatibility signal; callers migrating old sequence files and writable payloads may still encounter `UTF8`.

`TwoDArrayWritable` persists rectangular or jagged two-dimensional arrays of `Writable` with a configured value class. Its methods convert to `Object`, set/get the `Writable[][]`, and implement `readFields`/`write`.

`VersionedWritable` adds a byte version header around `Writable` persistence. Subclasses implement `getVersion()`, and `readFields` can throw `VersionMismatchException` when serialized data has an incompatible version. `VersionMismatchException` records expected/found bytes and formats that mismatch through `toString()`.

`VIntWritable` and `VLongWritable` are mutable wrappers over Hadoop's variable-length integer encoding. They provide default and value constructors, `set`, `get`, `readFields`, `write`, equality/hash, comparison, and string conversion. These are the object forms of the vint/vlong wire encoding used throughout Hadoop metadata.

## Writable Core, Naming, Factories, And Utility Encoding

`Writable` is the base serialization contract: `write(DataOutput)` and `readFields(DataInput)`. The documentation emphasizes that implementations should assume the instance is being reused and must overwrite all persistent fields during `readFields`. `WritableComparable` combines `Writable` with `Comparable` and is the common key type for sorted Hadoop data.

`WritableComparator` is the comparator registry and byte-comparison base class for `WritableComparable` keys. It has constructors with optional key instance creation, static `get` and `define` registry hooks, key-class access, `newKey`, object and byte-array comparison overloads, `compareBytes`, `hashBytes`, and primitive parsing helpers (`readUnsignedShort`, `readInt`, `readFloat`, `readLong`, `readDouble`, `readVLong`, `readVInt`). This is the bridge between serialized file/shuffle bytes and logical key order; optimized subclasses can avoid deserializing records.

`WritableFactories` is a synchronized global registry from class to `WritableFactory`, with `setFactory`, `getFactory`, and `newInstance` overloads that optionally take `Configuration`. It exists so `ObjectWritable` can instantiate non-public classes. `WritableFactory` is the single-method factory interface.

`WritableName` is a synchronized alias registry for writable class names. `setName`, `addName`, `getName`, and `getClass` allow class renaming without invalidating persisted files that contain old class names. This is a long-term storage compatibility hook and can affect deserialization of old sequence files or RPC payloads.

`WritableUtils` is the dense utility surface for Hadoop wire encoding. It covers compressed byte arrays and strings, string arrays, byte-array display, cloning through serialization, deprecated `cloneInto` in favor of `ReflectionUtils.cloneInto`, vint/vlong write and read, sign/length decoding (`isNegativeVInt`, `decodeVIntSize`, `getVIntSize`), enum read/write by string name, strict skipping (`skipFully`), and converting writable arrays to raw bytes. Its vint/vlong documentation defines the signed one-byte range and the leading-byte scheme used by both stream and comparator parsing.

## Compression APIs

`CompressionCodec` is the central codec abstraction. It creates compression/decompression streams with or without caller-supplied `Compressor`/`Decompressor`, reports compressor/decompressor implementation classes, creates those stateful codec objects, and declares the default file extension. This interface is used by sequence files and higher-level input/output formats to discover compression behavior from configuration or file names.

`CompressionCodecFactory` loads codec classes from `io.compression.codecs`, exposes `getCodecClasses`/`setCodecClasses`, resolves a codec from a `Path` suffix, removes a matched suffix, implements `toString`, and has a command-line `main`. The `LOG` field indicates diagnostics are part of codec discovery. This is the integration point between configuration, file extensions, and concrete codecs.

`CompressionInputStream` and `CompressionOutputStream` are abstract stream wrappers with protected underlying `in`/`out` fields. They define common lifecycle hooks: `close`, single-byte or byte-array `read`/`write`, `finish`, `flush`, and `resetState`. `CompressorStream` and `DecompressorStream` specialize these wrappers around stateful `Compressor` and `Decompressor` objects. Their public/protected fields (`compressor`, `decompressor`, `buffer`, `closed`, `eof`) and methods (`compress`, `decompress`, `getCompressedData`, `checkStream`, `available`, `skip`, mark/reset handling) show stream correctness depends on close/reset semantics and not reusing ended codec state.

`Compressor` and `Decompressor` are stateful block interfaces. Compressors accept input, optional dictionaries, report input/output byte counters, finish, detect finished state, compress into caller buffers, reset, and release resources with `end`. Decompressors mirror input/dictionary handling, `needsDictionary`, `finished`, decompression, reset, and `end`. Correct pooling must reset state before reuse and call `end` when the native or Java backing object is no longer needed.

`CodecPool` is a global pool for `Compressor` and `Decompressor` instances keyed by codec. It returns pooled or new objects and accepts returned instances. This reduces allocation/native setup cost but raises lifecycle risk: callers must return objects only after streams are finished/reset and must not use them after return.

`BlockCompressorStream` and `BlockDecompressorStream` define Hadoop's block-oriented codec framing. The compressor stream writes blocks with an uncompressed length followed by one or more length-prefixed compressed chunks, bounded by buffer size minus overhead. The decompressor stream reads those framed blocks and supports `resetState`. This framing is distinct from codec-native streaming formats.

`DefaultCodec` is configurable (`setConf`, `getConf`) and supplies the default deflate/zlib codec behavior. `GzipCodec` extends it to produce gzip streams, compressor/decompressor types, and the gzip extension. Nested `GzipInputStream` and `GzipOutputStream` bridge Java gzip/deflater streams into Hadoop's compression stream API, including `available`, `close`, `read`, `write`, `skip`, `flush`, `finish`, and `resetState`.

`BZip2Codec` implements `CompressionCodec` but documents that compressor/decompressor object methods are not supported and throw `UnsupportedOperationException`; only direct stream creation is supported. That means generic code using `CodecPool` cannot assume every codec supports pooled compressor objects. The default extension is `.bz2`.

## BZip2 And Zlib Implementations

`org.apache.hadoop.io.compress.bzip2` exposes a historical pure-Java BZip2 implementation. `BZip2Constants` contains public constants and `rNums`; its documentation explicitly warns that `rNums` should not be public because malicious code can mutate it. `BZip2DummyCompressor` and `BZip2DummyDecompressor` implement the compressor/decompressor interfaces as placeholders.

`CBZip2InputStream` and `CBZip2OutputStream` perform BZip2 data transformation without the leading file magic bytes. Callers must skip `"BZ"` before constructing the input stream and must write `"BZ"` before constructing the output stream. The output stream supports block sizes 1 through 9, `chooseBlockSize`, `finish`, `close`, `flush`, and exposes several protected algorithm constants for historical subclass access. The docs call out large memory requirements, recommend prompt close, and state instances are not thread-safe.

`org.apache.hadoop.io.compress.zlib` provides both Java-wrapper and native-capable zlib contracts. `BuiltInZlibDeflater` and `BuiltInZlibInflater` adapt `java.util.zip.Deflater`/`Inflater` to Hadoop `Compressor`/`Decompressor`. `ZlibCompressor` and `ZlibDecompressor` expose synchronized stateful methods around zlib with direct buffer size configuration, byte counters, reset/end, and optional dictionaries.

`ZlibCompressor.CompressionHeader` defines `NO_HEADER`, `DEFAULT_HEADER`, and `GZIP_FORMAT`, each with a `windowBits()` value. `ZlibDecompressor.CompressionHeader` adds `AUTODETECT_GZIP_ZLIB`. `ZlibCompressor.CompressionLevel` defines no compression, best speed, best compression, and default compression. `ZlibCompressor.CompressionStrategy` defines filtered, Huffman-only, RLE, fixed, and default strategies. `ZlibFactory` chooses native or built-in zlib availability and returns the appropriate compressor/decompressor class or instance.

## Retry APIs

`RetryPolicy` is the decision interface: `shouldRetry(Exception e, int retries)` returns whether a failed call should be retried. The boolean-only return means delay/sleep behavior is encapsulated inside the policy implementation rather than returned to the caller.

`RetryPolicies` is the static factory/constant holder. It defines `TRY_ONCE_THEN_FAIL`, `TRY_ONCE_DONT_FAIL`, and `RETRY_FOREVER`, plus factories for fixed-sleep retry by maximum count, fixed-sleep retry by maximum elapsed time, proportional sleep, exponential backoff, retry-by-exception map, and retry-by-remote-exception map. Time units are part of the factory signatures, tying retry timing to `java.util.concurrent.TimeUnit`.

`RetryProxy` creates dynamic proxies for an implementation and interface, either with one default retry policy or a map of method names to policies plus a default. It is the integration point that applies retry behavior to RPC-like or filesystem client APIs without changing the implementation class.

## Serialization APIs

The serializer package provides a pluggable framework controlled by the `io.serializations` configuration property. A `Serialization` implementation advertises `accept(Class)`, then returns a `Serializer` and `Deserializer` for matching classes. `SerializationFactory` loads configured implementations and returns the selected serializer/deserializer for a class.

`Serializer` is stateful: `open(OutputStream)`, `serialize(Object)`, and `close()`. Its docs require that serializers must not buffer output because other producers may write to the same stream between serialize calls. `Deserializer` is similarly stateful: `open(InputStream)`, `deserialize(Object reuse)`, and `close()`, with the reusable object parameter providing an allocation-saving path.

`WritableSerialization` adapts Hadoop `Writable` objects by delegating to `Writable.write(DataOutput)` and `Writable.readFields(DataInput)`. `JavaSerialization` adapts Java `Serializable`. `DeserializerComparator` compares serialized byte slices through a supplied deserializer, and `JavaSerializationComparator` specializes that for Java serialization. The comparator APIs are useful but risky for performance because deserialization may happen during comparison unless a byte-level comparator exists.

## IPC APIs

`org.apache.hadoop.ipc.Client` is the low-level Writable-based IPC client. Constructors bind a response value class, `Configuration`, and optionally a `SocketFactory`. `setPingInterval(Configuration, int)` stores ping behavior in configuration. `stop()` terminates all client threads and makes the client unusable afterward. `call` overloads support single calls and parallel calls to arrays of `InetSocketAddress`, with protocol class and `UserGroupInformation` credentials on the non-deprecated overloads. Older overloads without protocol or ticket are deprecated in favor of protocol-aware, credential-aware calls. The public `LOG` field is a diagnostic integration point.

`RemoteException` represents an exception thrown by remote IPC code. It records the remote class name, can unwrap to matching lookup types or instantiate the wrapped exception when possible, can serialize to XML through `XMLOutputter`, and can be reconstructed from SAX attributes. This is both a wire compatibility type and a user-facing error translation layer.

`RPC` is the higher-level dynamic proxy/server API over IPC. It can wait for a proxy, create proxies with protocol class, client version, address, configuration, optional `UserGroupInformation`, and optional `SocketFactory`, stop proxies, make parallel reflective method calls to multiple servers, and construct `RPC.Server` instances for protocol implementation objects. The visible class documentation states that protocol methods are Java interface methods whose parameters and returns must be primitives, `String`, `Writable`, or arrays of those types. Older `call(Method, Object[][], InetSocketAddress[], Configuration)` is deprecated in favor of the overload with `UserGroupInformation`.

## Control Flow And State Inferred From The API

Sequence-file control flow is append/read/seek oriented. Writers append typed or raw records, periodically sync, and expose byte lengths for later exact positioning. Readers load header metadata, key/value classes, and compression settings, then iterate records either by deserializing into reusable objects or by streaming raw key/value bytes. Sorters consume one or more sequence files, spill sorted segments to temp paths under a memory budget, merge bounded by fan-in, and optionally delete input segments during cleanup.

Writable control flow is object-reuse oriented. `readFields` mutates existing instances; factories and name registries provide late construction; comparators may compare either objects or raw byte slices; utility functions encode small signed integers compactly. These patterns are fundamental to Hadoop's performance model because object allocation and full deserialization are avoided on hot paths.

Compression control flow is stream and codec-state oriented. Codecs create streams, streams feed stateful compressors/decompressors, callers finish/close/reset, and `CodecPool` recycles codec state. Block compression adds explicit block length framing, while gzip/bzip2/zlib classes each have format-specific header, reset, and native fallback rules.

Retry proxy control flow wraps method invocation with policy decisions after exceptions. Serialization factory control flow selects a serialization implementation by configured order and class acceptance. IPC control flow creates protocol proxies, sends writable invocation requests to servers, unwraps remote exceptions, and stops proxies/clients to release threads and sockets.

## State And Persistence Behavior

Persistent on-disk state appears most strongly in sequence files, set/map files, writable payloads, text encodings, compressed streams, and IPC exception XML. `SequenceFile.Metadata` stores `Text` key/value attributes; reader/writer APIs preserve key/value class names, compression codec identity, sync markers, raw record framing, and metadata. `WritableName` exists specifically to keep old files readable after class renames.

Process-global state exists in comparator definitions, writable factories, writable names, codec pools, codec class configuration, and retry proxy policy maps. Several registry methods are synchronized, which suggests concurrent clients are expected. Global codec pooling can improve throughput but can also retain native resources until returned or ended.

Object-local mutable state exists throughout: `Text`, `UTF8`, vint/vlong writables, sorted maps, two-dimensional arrays, serializers/deserializers, compressors/decompressors, compression streams, sequence-file readers/writers, and IPC clients. Many methods are explicitly synchronized in JDiff for reader positioning, zlib state, and registry mutation; other classes document that they are not thread-safe.

Network and security state enters in IPC through `SocketFactory`, ping intervals in `Configuration`, protocol class/version, server addresses, and `UserGroupInformation` tickets. Remote exceptions persist class names and messages across process boundaries and may be serialized as XML.

## Dependencies And Integration Points

This chunk depends on Hadoop filesystem classes (`FileSystem`, `Path`, `FSDataInputStream`), configuration (`Configuration`, `Configured`), utility progress interfaces (`Progress`, `Progressable`), security identity (`UserGroupInformation`), and common logging (`org.apache.commons.logging.Log`).

Java platform dependencies include `java.io` streams and data input/output, `Closeable`, `IOException`, `OutputStream`/`InputStream`, `java.net.InetSocketAddress`, `javax.net.SocketFactory`, Java reflection `Method`, `java.util` collections and maps, `java.util.concurrent.TimeUnit`, `java.util.zip.Deflater`/`Inflater`, SAX `Attributes`, and XML output through `org.znerd.xmlenc.XMLOutputter`.

The APIs integrate internally across packages: sequence files depend on compression codecs, raw comparators, writable serialization, file systems, and progress reporting; writable comparators and utilities define the byte encodings used by sequence files, map files, and IPC; retry proxies can wrap IPC-facing protocol implementations; serialization factory implementations feed sequence-file writer serializers and comparator helpers.

## Risks And Edge Cases

Storage compatibility risk is high. Changing `WritableUtils` vint/vlong encoding, `Text` UTF-8 validation, `WritableName` aliases, `VersionedWritable` version handling, sequence-file sync/position semantics, or compression stream framing would make existing Hadoop data unreadable or incorrectly sorted.

Comparator correctness is a major risk. `WritableComparator` byte-level helpers must match `Writable` serialization exactly. Any mismatch can corrupt sort order in map output, sequence-file sort/merge, set/map file lookup, or RPC key handling. Optimized byte comparators need tests against object comparisons for signed integers, variable-length encodings, UTF-8 data, and boundary offsets.

Resource lifecycle risk appears in `SequenceFile.Reader`/`Writer`, `RawKeyValueIterator`, compression streams, codec pools, serializers/deserializers, BZip2 streams, zlib native objects, and IPC clients/proxies. Missing `close`, `finish`, `reset`, `returnCompressor`, `returnDecompressor`, `end`, or `stop` calls can leak file handles, native buffers, memory-heavy BZip2 work arrays, sockets, or threads.

Thread-safety boundaries are uneven. Some registry and zlib methods are synchronized, `SequenceFile.Reader` synchronizes core movement/value methods, but BZip2 stream docs state non-thread-safety and many mutable writable wrappers expose unsynchronized setters/getters. Shared instances should be treated carefully.

Compression format edge cases include BZip2's missing `"BZ"` header handling, unsupported BZip2 pooled compressor/decompressor methods, zlib header variants, gzip reset behavior, block compression overhead calculations, dictionaries, zero-length writes, and byte counters. Codec discovery by suffix can also be ambiguous if multiple configured codecs share extensions.

IPC compatibility risk includes deprecated overload migration, protocol version mismatches, UGI ticket propagation, ping interval configuration, parallel call partial failures returning nulls, and remote exception unwrapping by class name. `RemoteException.unwrapRemoteException` depends on exception classes and constructors being available locally.

Security risk is explicitly documented for `BZip2Constants.rNums`, a public mutable array that should have been private. Serialization also carries risk: Java serialization acceptance may instantiate arbitrary `Serializable` payloads, and remote exception XML/class names cross process boundaries.

## Test Signals

Useful test signals for this API surface include sequence-file round trips with uncompressed, record-compressed, and block-compressed data; metadata preservation; raw key/value iteration; `seek` to writer lengths; `sync` from arbitrary offsets; sorter merge with deleted and preserved inputs; and set/map file lookup with custom comparators.

Writable tests should assert `write`/`readFields` reuse semantics, vint/vlong boundary values, `Text` non-ASCII code points and invalid UTF-8 validation, `UTF8` legacy compatibility, `WritableName` alias deserialization, `WritableFactories` construction of non-public classes, and `WritableComparator` byte comparisons matching object comparisons.

Compression tests should cover codec factory discovery from configuration and suffixes, `CodecPool` borrow/return reuse, default/gzip/zlib header modes, BZip2 streams with explicit magic-byte handling, unsupported BZip2 compressor-object paths, block compression round trips across small and large buffers, close/finish/reset behavior, and native-zlib fallback via `ZlibFactory`.

Retry tests should wrap implementations with `RetryProxy` and verify fixed-count, fixed-time, proportional, exponential, exception-map, and remote-exception-map decisions, including no-retry and retry-forever policies under bounded test clocks.

Serializer tests should verify configured `io.serializations` ordering, `WritableSerialization` reuse, Java serialization comparator behavior, serializer non-buffering expectations when multiple producers write to one stream, and close semantics.

IPC tests should validate client lifecycle (`stop` prevents further calls), ping interval configuration, single and parallel calls, deprecated-to-current overload behavior where still supported, protocol/UGI propagation, remote exception XML/value reconstruction, unwrapping to known exception classes, proxy stop resource release, and server construction with default and explicit handler counts.
