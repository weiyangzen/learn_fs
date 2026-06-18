# Research: subset-b-007356

This grouped report covers the Hadoop `org.apache.hadoop.io.compress` codec and bzip2 implementation files assigned to subset B. Each file section is bounded for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BZip2Codec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BZip2Codec.java

## Purpose
`BZip2Codec` is Hadoop's public bzip2 `SplittableCompressionCodec`. It exposes normal `CompressionCodec` streams plus split-aware input streams for MapReduce-style parallel reads. It chooses native bzip2 for ordinary pooled streams when available, but always uses the pure-Java `CBZip2InputStream` path for split reads because splitability depends on scanning bzip2 block markers.

## Important APIs and Types
The class implements `Configurable` and `SplittableCompressionCodec`. Public methods include `createOutputStream`, `createInputStream`, `createInputStream(InputStream, Decompressor, long, long, READ_MODE)`, `getCompressorType`, `createCompressor`, `getDecompressorType`, `createDecompressor`, `getDefaultExtension`, and the visible-for-testing `writeHeader`. Nested `BZip2CompressionOutputStream` wraps `CBZip2OutputStream`; nested `BZip2CompressionInputStream` extends `SplitCompressionInputStream` and wraps `CBZip2InputStream`.

## Control Flow
Normal output uses `CompressionCodec.Util.createOutputStreamWithCodecPool`, then either a native `CompressorStream` or pure-Java `BZip2CompressionOutputStream`. Normal input similarly uses the pool, then either native `DecompressorStream` or pure-Java `BZip2CompressionInputStream`. Split input validates that the supplied stream is `Seekable`, seeks to `start`, and constructs a pure-Java split stream. The pure-Java input strips the leading `BZ` header only when starting at file offset zero; in `BYBLOCK` mode it also handles the `h9` subheader and advances starts close to the file header so the first block is not duplicated.

## State and Persistence
Codec configuration is held in `conf`. Output stream state is `needsReset` plus the active `CBZip2OutputStream`; `finish()` writes an empty valid bzip2 stream if no data was written. Input stream state tracks header stripping, `READ_MODE`, starting compressed position, whether an initial read was synthesized, and a position-advertisement state machine that reports compressed positions only after one byte past an end-of-block marker. No persistent storage is updated.

## Dependencies and Integration
The class depends on `Bzip2Factory`, `CBZip2InputStream`, `CBZip2OutputStream`, `BZip2Constants`, `CodecPool`, Hadoop `Seekable`, and `IO_FILE_BUFFER_SIZE_*`. It integrates with `CompressionCodecFactory` through the `.bz2` extension and with record readers through `SplitCompressionInputStream.getAdjustedStart/getAdjustedEnd` and `getPos()`.

## Risks
Native and pure-Java paths have different capabilities: split reads never use native bzip2, while pure-Java mode returns dummy compressor/decompressor types that throw for direct compressor API use. Position reporting is intentionally delayed around block boundaries, so record readers must understand this contract. Header handling is permissive for headerless streams, which is useful for `CBZip2*` internals but can mask malformed inputs until deeper reads fail.

## Test Signals
`TestBZip2Codec` exercises split start/end behavior, BYBLOCK position updates, header-adjacent starts, and continuous-mode behavior. `TestCompressionStreamReuse` covers stream reset for bzip2. `TestCodecFactory` checks `.bz2` discovery and case-insensitive extension matching. Native compressor/decompressor behavior is covered separately in bzip2 native tests when the native library is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BZip2Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockCompressorStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockCompressorStream.java

## Purpose
`BlockCompressorStream` adapts a `Compressor` to Hadoop's block-framed compression format for codecs such as Snappy and LZ4 whose native compression operates on bounded blocks rather than indefinite zlib-style streams.

## Important APIs and Types
It extends `CompressorStream`. Constructors accept an `OutputStream`, `Compressor`, output buffer size, and compression overhead; the default constructor uses a 512-byte buffer and 18-byte zlib-style overhead. The key overrides are `write(byte[], int, int)`, `finish()`, and `compress()`.

## Control Flow
Each logical block begins with a big-endian 4-byte uncompressed length. The stream then writes one or more big-endian length-prefixed compressed chunks. `write()` flushes the current block when adding more input would exceed `MAX_INPUT_SIZE`, splits oversized user buffers into separate compressed chunks, and resets the compressor after completed blocks. `finish()` emits the current uncompressed length, marks the compressor finished, and drains compressed output.

## State and Persistence
The only local immutable state is `MAX_INPUT_SIZE = bufferSize - compressionOverhead`; inherited state includes the compressor, output buffer, and closed flag. There is no durable persistence, but the emitted wire format is stateful and must be decoded by `BlockDecompressorStream`.

## Dependencies and Integration
`SnappyCodec` and `Lz4Codec` construct this stream with codec-specific overhead calculations. It depends on `Compressor.getBytesRead()` to know the current block's uncompressed byte count and on `Compressor.reset()` being safe after each completed block.

## Risks
The framing format is Hadoop-specific; raw Snappy/LZ4 readers cannot decode it directly. Incorrect overhead values can make compressed chunks exceed buffer expectations or reduce block size unnecessarily. A compressor that reports bytes-read incorrectly will corrupt block lengths. `finish()` can emit a zero-length block for empty compressed files, which the paired block decompressor treats as EOF.

## Test Signals
`TestBlockDecompressorStream`, `TestSnappyCompressorDecompressor`, `TestLz4CompressorDecompressor`, and `CompressDecompressTester` exercise round trips, EOF handling, and the block stream pair under codec-specific compressors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockCompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockDecompressorStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockDecompressorStream.java

## Purpose
`BlockDecompressorStream` is the inverse of `BlockCompressorStream`. It reads Hadoop's block-framed compressed stream and feeds length-prefixed compressed chunks into a `Decompressor`.

## Important APIs and Types
It extends `DecompressorStream` and overrides `decompress`, `getCompressedData`, and `resetState`. It tracks `originalBlockSize` and `noUncompressedBytes` to know when a logical uncompressed block is complete.

## Control Flow
At the start of each block, `decompress()` reads a 4-byte uncompressed block length. A zero length is treated as EOF for a compressed empty file. It repeatedly calls `decompressor.decompress`; when the decompressor needs input, `getCompressedData()` reads the next 4-byte compressed chunk length and then exactly that many bytes from the underlying stream. The block ends once `noUncompressedBytes` reaches `originalBlockSize`.

## State and Persistence
Local state is the current logical block size and number of uncompressed bytes already returned for that block. The inherited buffer can grow if a compressed chunk length exceeds the current buffer. `resetState()` clears block counters and resets the decompressor.

## Dependencies and Integration
It depends on the exact big-endian framing emitted by `BlockCompressorStream`. It is used by `SnappyCodec` and `Lz4Codec`, and test fakes validate edge cases independent of native libraries.

## Risks
Malformed lengths can force large buffer allocation or lead to EOF exceptions. A decompressor that returns zero without `needsInput`, `finished`, or `needsDictionary` changing can spin. The class reports EOF if compressed input ends while fetching a chunk, so truncated data may be seen as EOF in some paths and as `EOFException` in others depending on where truncation occurs.

## Test Signals
`TestBlockDecompressorStream` checks block stream EOF paths and fake decompressor behavior. Snappy and LZ4 compressor/decompressor tests exercise this stream with real block codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/BlockDecompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecConstants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecConstants.java

## Purpose
`CodecConstants` centralizes default file extensions for Hadoop compression codecs.

## Important APIs and Types
It is a final utility class with a private constructor and public constants: `.deflate`, `.bz2`, `.gz`, `.lz4`, `.passthrough`, `.snappy`, and `.zst`.

## Control Flow
There is no runtime control flow beyond class loading. Codec implementations return these constants from `getDefaultExtension()`.

## State and Persistence
All state is immutable static final string data. No persistence is involved.

## Dependencies and Integration
`DefaultCodec`, `BZip2Codec`, `GzipCodec`, `Lz4Codec`, `PassthroughCodec`, `SnappyCodec`, and `ZStandardCodec` depend on these constants. `CompressionCodecFactory` indirectly uses them when registering codecs by suffix.

## Risks
Changing any constant changes extension-based codec discovery and can break compatibility with existing compressed files and configured jobs.

## Test Signals
`TestCodecFactory` exercises extension discovery for gzip, bzip2, deflate, Snappy, and LZ4. Any extension change should be reflected there and in configuration documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecConstants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecPool.java

## Purpose
`CodecPool` is a global in-process pool for reusable `Compressor` and `Decompressor` instances, especially native codec wrappers whose construction and teardown are expensive.

## Important APIs and Types
Public APIs are `getCompressor(codec, conf)`, `getCompressor(codec)`, `getDecompressor(codec)`, `returnCompressor`, `returnDecompressor`, `getLeasedCompressorsCount`, and `getLeasedDecompressorsCount`. It maintains class-keyed `Map<Class<T>, Set<T>>` pools and Guava `LoadingCache<Class<T>, AtomicInteger>` lease counters.

## Control Flow
Borrowing checks the pool for an instance of the codec's implementation class. If absent, the codec creates a new object; if present, compressors are reinitialized using either the provided configuration or the codec's `Configurable` configuration. Returning resets reusable instances and puts them back in the class set. Types annotated with `@DoNotPool` are ended and not added to the pool.

## State and Persistence
The pool is static process-local state. Pool maps are synchronized at the map and set levels; lease counts are updated only for non-`DoNotPool` instances and only decremented when `payback` actually adds the object to the set, preventing double-return from underflowing counts.

## Dependencies and Integration
`CompressionCodec.Util` calls the pool and attaches borrowed codecs to streams so close returns them. Concrete codecs provide the implementation class keys through `getCompressorType` and `getDecompressorType`. `ReflectionUtils.getClass` is used to key returned instances.

## Risks
The pool is global and unbounded by size, so workloads using many codec classes or large native buffers can retain memory. Correctness depends on reset/reinit implementations clearing all per-stream state. Borrowing and returning the same object multiple times is guarded by set semantics for counts but can still make application misuse visible as closed or corrupted compressors.

## Test Signals
`TestCodecPool` covers lease counts, duplicate returns, multithreaded borrow/return, compressor reconfiguration on reuse, and `DoNotPool` behavior for built-in gzip classes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CodecPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodec.java

## Purpose
`CompressionCodec` is Hadoop's core codec contract tying together compression streams, decompression streams, compressor/decompressor factory methods, implementation types, and default filename extension.

## Important APIs and Types
The interface declares stream creation methods with and without supplied `Compressor`/`Decompressor`, type factories, `createCompressor`, `createDecompressor`, and `getDefaultExtension`. Nested `Util` creates streams using `CodecPool` and ensures borrowed instances are returned on stream close.

## Control Flow
Implementations either construct streams directly or delegate no-argument stream creation to `Util`. `Util.createOutputStreamWithCodecPool` borrows a compressor, calls the codec's compressor-specific stream factory, returns the compressor on construction failure, or records it as tracked on success. Input follows the same pattern for decompressors.

## State and Persistence
The interface itself has no state. The nested utility temporarily owns pooled instances and transfers close-time ownership to `CompressionInputStream`/`CompressionOutputStream` via package-private tracking setters.

## Dependencies and Integration
Every Hadoop codec implementation in this subset implements this interface. `CompressionCodecFactory`, SequenceFile/TFile code, MapReduce input and output formats, and file extension discovery depend on it.

## Risks
Implementations must keep `getCompressorType`/`createCompressor` and `getDecompressorType`/`createDecompressor` consistent or `CodecPool` reuse will be wrong. Streams constructed with user-supplied compressors are not automatically returned to the pool unless created through `Util`.

## Test Signals
`TestCodecFactory`, `TestCodecPool`, `TestCompressionStreamReuse`, SequenceFile tests, and codec-specific round-trip tests collectively validate this contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodecFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodecFactory.java

## Purpose
`CompressionCodecFactory` discovers and selects codecs by filename suffix, canonical class name, or short alias.

## Important APIs and Types
It holds a reversed-suffix `SortedMap<String, CompressionCodec>`, a name/alias map, and a canonical class-name map. Public APIs include `getCodecClasses`, `setCodecClasses`, constructor registration, `getCodec(Path)`, `getCodecByClassName`, `getCodecByName`, `getCodecClassByName`, `removeSuffix`, and a small CLI `main`.

## Control Flow
Discovery first loads `CompressionCodec` providers through Java `ServiceLoader`, then appends classes listed in `io.compression.codecs`, allowing configured classes to override by suffix when registered later. If no providers or configured classes exist, gzip and default deflate are registered. `getCodec(Path)` reverses and lowercases the filename, uses a head-map lookup, and selects the longest matching registered suffix.

## State and Persistence
Factory state is per-instance maps populated at construction. The static `ServiceLoader` is synchronized during iteration because it is lazy. Configuration is read but not otherwise persisted; `setCodecClasses` writes a comma-separated class list to `Configuration`.

## Dependencies and Integration
Depends on `CommonConfigurationKeys.IO_COMPRESSION_CODECS_KEY`, `ReflectionUtils`, `StringUtils`, `Path`, and `ServiceLoader`. It is the bridge between file naming conventions and codec instantiation for Hadoop readers and tools.

## Risks
Suffix registration assumes codec extensions are normalized enough for reverse-string matching; a codec returning an extension without a dot can still be registered but may behave unexpectedly. Misconfigured classes throw `IllegalArgumentException` during discovery. Because the maps contain instances, configuration changes after factory construction do not affect existing factories.

## Test Signals
`TestCodecFactory` validates default discovery, case-insensitive suffix matching, longest suffix matching, alias lookup, configured overrides, and parsing of comma-separated codec class names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionCodecFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionInputStream.java

## Purpose
`CompressionInputStream` is the abstract base class for all Hadoop decompression streams. It prevents accidental raw reads from the underlying compressed stream and provides common close, position, seek, and IO statistics behavior.

## Important APIs and Types
It extends `InputStream` and implements `Seekable` plus `IOStatisticsSource`. Subclasses must implement `read(byte[], int, int)` and `resetState()`. It provides `getPos`, unsupported `seek`/`seekToNewSource`, `getIOStatistics`, and package-private `setTrackedDecompressor`.

## Control Flow
The constructor records the underlying stream and, for non-seekable/non-positioned streams, snapshots `available()` into `maxAvailableData` for approximate position calculations. `close()` closes the underlying stream and returns any tracked decompressor to `CodecPool`. `getPos()` delegates to `Seekable` when possible or estimates consumed bytes from the original available count.

## State and Persistence
State is the wrapped `InputStream`, `maxAvailableData`, and an optional tracked decompressor borrowed from `CodecPool`. No durable state is persisted.

## Dependencies and Integration
Used by `DecompressorStream`, `BlockDecompressorStream`, `SplitCompressionInputStream`, `BZip2Codec` nested streams, and passthrough streams. It integrates with `CodecPool` and the filesystem statistics API.

## Risks
The fallback position calculation is only as reliable as `InputStream.available()` and is unsuitable for large streams whose available count is not total length. Subclasses must implement `resetState()` correctly after underlying stream repositioning.

## Test Signals
Stream reuse tests call `resetState` through codec streams. BZip2 split tests validate overridden position behavior. IO statistics behavior is indirectly covered by filesystem stream wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionOutputStream.java

## Purpose
`CompressionOutputStream` is the abstract base for Hadoop compression streams. It enforces finish-before-close semantics and owns return of tracked pooled compressors.

## Important APIs and Types
It extends `OutputStream` and implements `IOStatisticsSource`. Subclasses implement `write(byte[], int, int)`, `finish()`, and `resetState()`. It provides `close`, `flush`, `getIOStatistics`, and package-private `setTrackedCompressor`.

## Control Flow
`close()` calls `finish()` first, then closes the wrapped stream, then returns any tracked compressor to `CodecPool`. `flush()` delegates to the wrapped stream without forcing a compression stream finish.

## State and Persistence
State is the wrapped `OutputStream` and an optional tracked `Compressor`. No durable state is persisted, but subclasses define the compressed byte stream format written to `out`.

## Dependencies and Integration
All concrete codec output streams inherit or wrap this class. `CompressionCodec.Util` sets the tracked compressor so pooled instances return on close. IO statistics are retrieved from the wrapped stream when available.

## Risks
Subclasses must make `finish()` idempotent enough for close-time invocation. If callers call `finish()` and keep writing, stream-specific logic must reject or reset correctly. Closing a stream with a tracked compressor transfers compressor lifecycle back to the global pool.

## Test Signals
`TestCompressionStreamReuse` covers `finish`, `flush`, and `resetState` for several codecs. `TestCodecPool` validates close-time and return behavior through pooled stream creation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressionOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Compressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Compressor.java

## Purpose
`Compressor` is the pluggable streaming compression engine interface used by `CompressorStream`, `BlockCompressorStream`, and `CodecPool`.

## Important APIs and Types
Methods include `setInput`, `needsInput`, `setDictionary`, `getBytesRead`, `getBytesWritten`, `finish`, `finished`, `compress`, `reset`, `end`, and `reinit(Configuration)`.

## Control Flow
Callers feed input when `needsInput()` is true, request finalization with `finish()`, drain compressed output using `compress()`, then either `reset()` for another stream or `end()` for permanent cleanup. `reinit()` lets pooled compressors adopt a new configuration before reuse.

## State and Persistence
Implementations own all compression state, byte counters, direct/native resources, and pending input/output buffers. The interface does not persist data itself.

## Dependencies and Integration
Implemented by zlib, gzip, Snappy, LZ4, ZStandard, native bzip2, and dummy bzip2 compressor classes. `CodecPool` relies on `reset`, `reinit`, and implementation class identity.

## Risks
Counter semantics are part of higher-level framing: `BlockCompressorStream` depends on `getBytesRead()` for block lengths. Incorrect `finished()` or `needsInput()` behavior can hang stream loops. `end()` must make native resources unreachable without leaving reusable pooled instances in a bad state.

## Test Signals
Codec-specific compressor/decompressor tests, `TestCodecPool`, block stream tests, and native bzip2 tests cover expected lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Compressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressorStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressorStream.java

## Purpose
`CompressorStream` is the standard `CompressionOutputStream` implementation for stream-oriented compressors such as zlib/gzip/zstd and a base for block framing.

## Important APIs and Types
It keeps a protected `Compressor`, output buffer, and closed flag. Constructors validate the output stream, compressor, and buffer size. It implements `write(byte[], int, int)`, `compress`, `finish`, `resetState`, `close`, and single-byte `write`.

## Control Flow
`write()` validates bounds, rejects writes after the compressor is finished, feeds data with `setInput`, and drains output while `needsInput()` is false. `finish()` marks the compressor finished and drains until `finished()` is true. `close()` delegates to `CompressionOutputStream.close()` once and then marks the stream closed.

## State and Persistence
State lives in the compressor and the reusable byte buffer. `resetState()` resets only the compressor, not the underlying output stream. No durable state beyond emitted compressed bytes.

## Dependencies and Integration
Constructed by `DefaultCodec`, `GzipCodec`, `ZStandardCodec`, and native bzip2 paths. `BlockCompressorStream` extends it and overrides framing behavior.

## Risks
The stream assumes the compressor's `needsInput` and `finished` contracts are accurate. It does not explicitly check `closed` in `write()`, so writes after close fail through underlying stream or compressor state rather than a local guard.

## Test Signals
`TestCompressionStreamReuse`, SequenceFile compression tests, and codec-specific round-trip tests validate stream reuse, finish, and data integrity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/CompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Decompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Decompressor.java

## Purpose
`Decompressor` is the pluggable streaming decompression engine interface used by decompression streams and pooled codec instances.

## Important APIs and Types
Methods include `setInput`, `needsInput`, `setDictionary`, `needsDictionary`, `finished`, `decompress`, `getRemaining`, `reset`, and `end`.

## Control Flow
Callers provide compressed input when `needsInput()` is true, call `decompress()` until bytes are produced or terminal state changes, inspect `finished()` and `getRemaining()` to handle concatenated streams, and reset or end the instance for reuse or cleanup.

## State and Persistence
Implementations own compressed input buffers, decompressed output buffers, byte counters, and native state. The interface itself has no storage.

## Dependencies and Integration
Implemented by zlib, gzip, Snappy, LZ4, ZStandard, native bzip2, dummy bzip2, and passthrough stubs. `DecompressorStream` depends on `getRemaining()` to preserve concatenated stream data.

## Risks
Callers must keep the input buffer stable until `needsInput()` becomes true. Incorrect remaining-byte accounting breaks concatenated streams. Implementations that require dictionaries cannot be satisfied by generic Hadoop streams and currently cause EOF-like behavior in `DecompressorStream`.

## Test Signals
Codec-specific decompressor tests, `TestCodecPool`, `TestBlockDecompressorStream`, and native bzip2 tests exercise this lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Decompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DecompressorStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DecompressorStream.java

## Purpose
`DecompressorStream` is the standard `CompressionInputStream` implementation for stream-oriented decompressors and the base class for block-framed decompression.

## Important APIs and Types
It keeps a protected `Decompressor`, input buffer, EOF and closed flags, skip buffer, single-byte buffer, and `lastBytesSent` for concatenated stream handling. It implements `read`, `decompress`, `getCompressedData`, `resetState`, `skip`, `available`, `close`, and mark/reset disabling.

## Control Flow
`read()` validates the stream and arguments, then calls `decompress()`. The default decompression loop calls the decompressor until bytes are produced. If the decompressor is finished with remaining input, it resets and resends leftover bytes to support concatenated members; if finished with no remaining input, it tries to read more compressed data before EOF. If input is needed, it reads from the underlying stream and feeds the decompressor.

## State and Persistence
The stream stores current compressed input bytes in `buffer`, the last amount sent to the decompressor for leftover offset calculation, and EOF/closed flags. No persistent state is written.

## Dependencies and Integration
Used by `DefaultCodec`, `GzipCodec`, `ZStandardCodec`, native `BZip2Codec`, and as a superclass for `BlockDecompressorStream` and passthrough stream. It depends on `Decompressor.getRemaining()` semantics for concatenated streams.

## Risks
A decompressor that repeatedly returns zero without changing state can cause a loop. The leftover offset logic depends on `lastBytesSent` representing the original buffer load, so changes here can break concatenated streams. `available()` returns only 0 or 1, which is conventional but not a byte count.

## Test Signals
Gzip and zlib concatenation behavior is covered through gzip/zlib tests and SequenceFile reads. `TestCodecPool` verifies `DoNotPool` closed decompressor behavior. `TestBlockDecompressorStream` covers subclass behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DecompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DefaultCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DefaultCodec.java

## Purpose
`DefaultCodec` is Hadoop's default deflate/zlib codec. It exposes zlib compression and decompression through standard Hadoop streams and supports direct decompression.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. It delegates compressor/decompressor type and instance creation to `ZlibFactory`, constructs `CompressorStream`/`DecompressorStream`, and returns `.deflate`.

## Control Flow
No-argument stream creation uses `CompressionCodec.Util` and `CodecPool`. Supplied-compressor streams use the configured `io.file.buffer.size`. Direct decompressor creation calls `ZlibFactory.getZlibDirectDecompressor(conf)`.

## State and Persistence
State is the mutable `Configuration conf`. No persistent data is stored; compressed output is zlib/deflate stream data.

## Dependencies and Integration
Depends on `ZlibFactory` and `IO_FILE_BUFFER_SIZE_*`. It is registered by default in `CompressionCodecFactory` when no codec list is supplied and is widely used by SequenceFile/TFile tests.

## Risks
Many methods assume `conf` is non-null; normal construction through `ReflectionUtils` with `Configurable` should set it, but direct callers must do so. Behavior varies with native zlib availability and zlib configuration.

## Test Signals
`TestSequenceFile`, `TestSequenceFileAppend`, `TestCodecPool`, `TestCodecFactory`, and stream reuse tests exercise the default codec heavily.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DefaultCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DeflateCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DeflateCodec.java

## Purpose
`DeflateCodec` is an alias subclass of `DefaultCodec` that enables discovery by the `deflate` codec name/class while preserving the same implementation.

## Important APIs and Types
It declares no methods or state and inherits all behavior from `DefaultCodec`.

## Control Flow
All stream creation, type lookup, compression, decompression, pooling, and extension behavior are inherited unchanged.

## State and Persistence
No local state exists. Inherited state is the `DefaultCodec` configuration.

## Dependencies and Integration
It integrates with `CompressionCodecFactory` class-name and alias lookup. Configurations can list `org.apache.hadoop.io.compress.DeflateCodec` to distinguish the alias from `DefaultCodec`.

## Risks
Because `getDefaultExtension()` is inherited, both default and deflate aliases map to `.deflate`; registering both in a factory can cause last-registration-wins behavior for that suffix.

## Test Signals
`TestCodecFactory` validates discovery of `DeflateCodec` by class/name in configured factories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DeflateCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressionCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressionCodec.java

## Purpose
`DirectDecompressionCodec` marks codecs that can create direct `ByteBuffer` decompressors for zero-copy or native-buffer workflows.

## Important APIs and Types
It extends `CompressionCodec` and adds `createDirectDecompressor()`.

## Control Flow
There is no implementation logic; concrete codecs decide whether direct decompression is supported and return either a direct decompressor instance or, in some implementations, `null` when unavailable.

## State and Persistence
The interface has no state or persistence.

## Dependencies and Integration
Implemented by `DefaultCodec`, `GzipCodec`, `SnappyCodec`, and `ZStandardCodec`. Downstream readers can check this interface before using `DirectDecompressor`.

## Risks
The contract does not require non-null return, so callers must handle unavailable native/direct support. Direct decompression has stricter buffer requirements than byte-array streams.

## Test Signals
Snappy and ZStandard tests cover direct decompressor classes. Gzip/default direct behavior depends on native zlib availability and is exercised through zlib-related tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressionCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressor.java

## Purpose
`DirectDecompressor` defines the direct `ByteBuffer` decompression operation used by codecs with native or direct-buffer paths.

## Important APIs and Types
The single method is `decompress(ByteBuffer src, ByteBuffer dst)`. The contract says it moves source and destination positions by bytes consumed/written, does not modify limits, and may require multiple calls.

## Control Flow
Implementations read from `src` and write to `dst` using internal codec state. Some block codecs require enough destination space for a complete decompressed block.

## State and Persistence
The interface has no state. Implementations may hold codec context between calls and must be reset or recreated according to their own contracts.

## Dependencies and Integration
Implemented by direct variants in zlib, Snappy, and ZStandard packages. Created by codecs implementing `DirectDecompressionCodec`.

## Risks
The method assumes non-null direct buffers with remaining space/data; implementations often reject heap-backed arrays. Callers must handle partial consumption and avoid assuming one call completes a stream.

## Test Signals
`TestSnappyCompressorDecompressor` and `TestZStandardCompressorDecompressor` include direct decompressor paths and error cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DirectDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DoNotPool.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DoNotPool.java

## Purpose
`DoNotPool` is a marker annotation for compressor/decompressor classes that must not be reused through `CodecPool`.

## Important APIs and Types
It is a runtime-retained, type-targeted, documented annotation with no elements.

## Control Flow
`CodecPool` checks for this annotation when borrowing counts and returning instances. Annotated instances are ended instead of reset and stored.

## State and Persistence
The annotation adds class metadata only; no runtime mutable state or persistence.

## Dependencies and Integration
Used by `CodecPool` and by implementations such as built-in gzip classes where return-to-pool should close resources rather than permit reuse.

## Risks
Omitting the annotation from non-reusable implementations can cause stale state or closed-resource reuse. Adding it to reusable native wrappers can reduce performance by defeating pooling.

## Test Signals
`TestCodecPool` explicitly verifies annotated built-in gzip compressor/decompressor instances are not usable after return and are not pooled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/DoNotPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/GzipCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/GzipCodec.java

## Purpose
`GzipCodec` provides gzip-format compression/decompression by specializing `DefaultCodec` with gzip headers and gzip-capable zlib or built-in implementations.

## Important APIs and Types
It overrides stream creation, compressor/decompressor type and creation, direct decompressor creation, and default extension. Nested `GzipZlibCompressor` and `GzipZlibDecompressor` specialize zlib wrappers for gzip format and autodetect gzip/zlib input.

## Control Flow
No-argument stream creation uses `CodecPool`. Supplied-compressor output creates a `CompressorStream` when the compressor is non-null, otherwise delegates. Compressor and decompressor creation branch on `ZlibFactory.isNativeZlibLoaded(conf)` to choose native zlib gzip wrappers or built-in gzip classes. Direct decompression is available only with native zlib.

## State and Persistence
State is inherited `conf`; nested zlib wrappers own native stream state. The output format uses `.gz` and gzip framing.

## Dependencies and Integration
Depends on zlib package classes, `IO_FILE_BUFFER_SIZE_*`, and `CodecConstants.GZIP_CODEC_EXTENSION`. Used by default codec discovery, SequenceFile append tests, and output formats requiring gzip compression.

## Risks
Native and built-in paths differ in pooling behavior and direct decompression support. Built-in gzip compressor/decompressor types are annotated not to pool in their classes, so lifecycle differs from native wrappers. `createInputStream(in, null)` creates a decompressor directly and does not attach it to pool tracking.

## Test Signals
`TestGzipCodec`, `TestCodecPool`, `TestCodecFactory`, `TestSequenceFileAppend`, and stream reuse tests cover gzip stream creation, pooling, discovery, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/GzipCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Lz4Codec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Lz4Codec.java

## Purpose
`Lz4Codec` provides Hadoop's LZ4 compression using block-framed streams.

## Important APIs and Types
It implements `Configurable` and `CompressionCodec`. It creates `Lz4Compressor`, `Lz4Decompressor`, `BlockCompressorStream`, and `BlockDecompressorStream`, and returns `.lz4`.

## Control Flow
No-argument streams use `CompressionCodec.Util` and the pool. Output computes buffer size from `io.compression.codec.lz4.buffersize`, computes compression overhead as `bufferSize / 255 + 16`, and constructs a block compressor stream. Compressor creation also reads `io.compression.codec.lz4.use.lz4hc` to select high-compression mode. Input uses the same configured buffer size for block decompression.

## State and Persistence
State is the mutable `Configuration conf`. The wire format is Hadoop's block framing around LZ4 compressed chunks, not necessarily a raw `.lz4` container format.

## Dependencies and Integration
Depends on `Lz4Compressor`, `Lz4Decompressor`, `CommonConfigurationKeys`, `CodecPool`, and `CodecConstants`. It is discoverable through configured codec lists and factory tests.

## Risks
Methods assume `conf` is set. Buffer size and overhead must remain consistent enough between compressor and decompressor. The `.lz4` extension may suggest interoperability, but the stream framing is Hadoop-specific.

## Test Signals
`TestLz4CompressorDecompressor`, `CompressDecompressTester`, and `TestCodecFactory` validate LZ4 round trips, block streams, and discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/Lz4Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/PassthroughCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/PassthroughCodec.java

## Purpose
`PassthroughCodec` is a special read-only codec that registers an extension but performs no decompression. It lets jobs disable automatic decompression for files whose extension would otherwise map to a real codec.

## Important APIs and Types
It implements `Configurable` and `CompressionCodec`. Public constants are `CLASSNAME`, `OPT_EXTENSION`, and `DEFAULT_EXTENSION`. Nested `PassthroughDecompressorStream` delegates reads/skips/availability directly to the wrapped input. Nested `StubDecompressor` satisfies the codec interface but performs no real decompression.

## Control Flow
`setConf()` reads `io.compress.passthrough.extension`, prepending a dot if needed. `getDefaultExtension()` returns and logs the registered fake extension. All output/compressor APIs throw `UnsupportedOperationException`. Input stream creation returns a passthrough stream regardless of the supplied decompressor.

## State and Persistence
State is the configuration and selected extension string. The stream keeps the original input stream reference and does not maintain decompression state.

## Dependencies and Integration
Designed for `io.compression.codecs` registration and `CompressionCodecFactory` suffix selection. It intentionally does not implement `SplittableCompressionCodec`.

## Risks
This codec only disables decompression; it does not validate that bytes are compressed or uncompressed. Registering it for a common extension like `.gz` changes job semantics globally for that factory configuration. Output APIs are unsupported and will fail if used by writers.

## Test Signals
Coverage is mainly through codec factory behavior and consumers that configure passthrough. The class has clear unsupported-operation paths that should be tested when used in write-capable contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/PassthroughCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SnappyCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SnappyCodec.java

## Purpose
`SnappyCodec` provides Hadoop's Snappy compression using block-framed streams and direct decompression support.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. It creates `SnappyCompressor`, `SnappyDecompressor`, `SnappyDirectDecompressor`, `BlockCompressorStream`, and `BlockDecompressorStream`, and returns `.snappy`.

## Control Flow
No-argument streams borrow compressors/decompressors from `CodecPool`. Output reads `io.compression.codec.snappy.buffersize`, computes overhead as `bufferSize / 6 + 32`, and uses `BlockCompressorStream`. Input uses `BlockDecompressorStream` with the same configured buffer size. Direct decompression always creates a new `SnappyDirectDecompressor`.

## State and Persistence
State is the mutable `Configuration conf`. Stream output is Hadoop's length-prefixed block format containing Snappy-compressed chunks.

## Dependencies and Integration
Depends on Snappy compressor/decompressor classes and `CommonConfigurationKeys`. Integrated with factory discovery, block stream tests, and direct decompression consumers.

## Risks
Methods assume `conf` is set. Direct decompressor behavior differs from `BlockDecompressorStream` and may require complete block destination space. Hadoop framing may not be interoperable with non-Hadoop Snappy file formats.

## Test Signals
`TestSnappyCompressorDecompressor`, `CompressDecompressTester`, and `TestCodecFactory` cover block round trips, direct decompression, edge cases, and discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SnappyCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplitCompressionInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplitCompressionInputStream.java

## Purpose
`SplitCompressionInputStream` is the base class for compressed input streams whose actual readable range may be adjusted to codec-specific boundaries.

## Important APIs and Types
It extends `CompressionInputStream` and stores `start` and `end`. Public methods are `getAdjustedStart()` and `getAdjustedEnd()`; protected setters allow codecs to adjust these values.

## Control Flow
The constructor initializes the wrapped input stream and the requested/adjusted range. Subclasses perform all actual decompression and may call setters when aligning to block boundaries.

## State and Persistence
State is only the adjusted start/end offsets in the compressed stream. No persistence is performed.

## Dependencies and Integration
Returned by `SplittableCompressionCodec.createInputStream`; `BZip2Codec`'s split stream is the primary implementation in this subset. Hadoop input formats use adjusted offsets to coordinate split ownership.

## Risks
If a codec does not correctly adjust start/end, record readers can duplicate or drop records at split boundaries. The base class does not enforce end-of-split reads itself.

## Test Signals
`TestBZip2Codec` validates split stream positions for bzip2. Broader MapReduce line reader tests provide integration signals for split handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplitCompressionInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplittableCompressionCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplittableCompressionCodec.java

## Purpose
`SplittableCompressionCodec` marks codecs that can decompress from arbitrary or codec-adjusted positions in a compressed stream, enabling parallel processing of compressed files.

## Important APIs and Types
It extends `CompressionCodec`, defines `READ_MODE { CONTINUOUS, BYBLOCK }`, and declares split-aware `createInputStream(InputStream, Decompressor, long, long, READ_MODE)`.

## Control Flow
Implementations seek or scan the compressed stream to a valid boundary and return a `SplitCompressionInputStream`. `READ_MODE.BYBLOCK` allows codecs such as bzip2 to surface block-boundary events, while `CONTINUOUS` hides block structure.

## State and Persistence
The interface has no state. Implementations maintain split offset and block-state tracking.

## Dependencies and Integration
Implemented by `BZip2Codec` in this subset. Hadoop input formats and record readers use this interface to split compressed inputs safely.

## Risks
The contract is difficult for codecs with stream-global state. Implementations must coordinate compressed positions with record boundaries, or consumers can miss/duplicate records.

## Test Signals
`TestBZip2Codec` directly exercises BYBLOCK and CONTINUOUS mode semantics for the bzip2 implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/SplittableCompressionCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/ZStandardCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/ZStandardCodec.java

## Purpose
`ZStandardCodec` provides Zstandard compression/decompression, including configurable compression level, optional worker threads, buffer sizing, pooling, and direct decompression.

## Important APIs and Types
It implements `Configurable`, `CompressionCodec`, and `DirectDecompressionCodec`. Static helpers include `getLibraryName`, `getCompressionLevel`, `getCompressionWorkers`, `getCompressionBufferSize`, and `getDecompressionBufferSize`. It creates `ZStandardCompressor`, `ZStandardDecompressor`, and `ZStandardDirectDecompressor`, and returns `.zst`.

## Control Flow
Buffer size comes from `io.compression.codec.zstd.buffersize`; zero means use compressor/decompressor recommended sizes. Compression level and worker count are read from configuration, with negative workers rejected immediately. Output/input stream creation uses `CodecPool`; supplied-compressor streams use standard `CompressorStream`/`DecompressorStream`.

## State and Persistence
State is the mutable `Configuration conf`. Native/JNI state is owned by the compressor/decompressor implementations. No persistent metadata is stored by the codec itself.

## Dependencies and Integration
Depends on `ZStandardCompressor`, `ZStandardDecompressor`, `CommonConfigurationKeys`, and the zstd-jni library name. Integrated with codec factory extension discovery and direct decompression consumers.

## Risks
Methods assume `conf` is set. Negative worker configuration throws, so validation should happen near job setup. Threaded compression can alter resource usage significantly. Buffer size zero delegates to native recommendations, which may vary across library versions.

## Test Signals
`TestZStandardCompressorDecompressor` covers codec streams, direct decompression, buffer sizes, compression workers, and invalid negative worker configuration. `TestCompressionStreamReuse` covers zstd stream reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/ZStandardCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2Constants.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2Constants.java

## Purpose
`BZip2Constants` holds shared constants for the pure-Java bzip2 compressor and decompressor.

## Important APIs and Types
It is an interface with package/public historical constants for block size, alphabet size, Huffman limits, run markers, group sizes, selector counts, overshoot bytes, sentinel return values `END_OF_BLOCK` and `END_OF_STREAM`, and the `rNums` randomization table.

## Control Flow
There is no executable control flow. Implementations reference constants during sorting, Huffman coding, randomization, and BYBLOCK sentinel handling.

## State and Persistence
All fields are static final interface constants. The `rNums` array is mutable at runtime because Java array contents are not immutable, and the source comments call this out as a historical weakness.

## Dependencies and Integration
Implemented by `CBZip2InputStream` and `CBZip2OutputStream`. `BZip2Codec` checks `END_OF_BLOCK` sentinel values from `CBZip2InputStream`.

## Risks
Public mutable `rNums` can be modified by malicious or buggy code in the same JVM, corrupting randomized block handling. Changing sentinel values or format constants would break pure-Java bzip2 compatibility.

## Test Signals
BZip2 stream tests indirectly exercise constants through block generation, block marker scanning, and randomized/non-randomized decompression paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2Constants.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyCompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyCompressor.java

## Purpose
`BZip2DummyCompressor` is the placeholder compressor type returned when native bzip2 is unavailable and the pure-Java bzip2 codec path does not implement the `Compressor` interface.

## Important APIs and Types
It implements `Compressor`. Most compressor methods throw `UnsupportedOperationException`; `reset()` and `reinit(Configuration)` are no-ops.

## Control Flow
The class is not intended to compress. It exists so `BZip2Codec.getCompressorType()` and `createCompressor()` can satisfy the interface in pure-Java mode while stream creation bypasses compressor-based APIs.

## State and Persistence
It has no fields and no persistent state.

## Dependencies and Integration
Returned by `Bzip2Factory` when `isNativeBzip2Loaded(conf)` is false. It may pass through `CodecPool`, but because pure-Java `BZip2Codec.createOutputStream(out, compressor)` ignores the supplied compressor when native is unavailable, ordinary stream creation still works.

## Risks
Direct callers that borrow a bzip2 compressor in pure-Java mode and call compressor methods will get unsupported-operation failures. The class is not annotated `DoNotPool`, but its no-op reset/reinit makes pooling harmless for placeholder use.

## Test Signals
`BZip2Codec` and stream reuse tests cover pure-Java stream behavior. Failure behavior is implicit in the documented unsupported compressor API for pure-Java bzip2 mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyCompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyDecompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyDecompressor.java

## Purpose
`BZip2DummyDecompressor` is the placeholder decompressor type returned when native bzip2 is unavailable and pure-Java bzip2 decompression does not use the `Decompressor` interface.

## Important APIs and Types
It implements `Decompressor`. Most methods throw `UnsupportedOperationException`; `reset()` is a no-op.

## Control Flow
It is not used to actually decompress data in pure-Java `BZip2Codec` stream creation; the codec constructs `BZip2CompressionInputStream` around `CBZip2InputStream` instead.

## State and Persistence
It has no fields and no persistent state.

## Dependencies and Integration
Returned by `Bzip2Factory` when native bzip2 is not loaded. `CodecPool.getDecompressor(codec)` may return it, and `BZip2Codec.createInputStream(in, decompressor)` ignores it in pure-Java mode.

## Risks
Direct decompressor API use in pure-Java bzip2 mode throws. As with the dummy compressor, it is not marked `DoNotPool`, but the no-op reset makes placeholder pooling low risk.

## Test Signals
`TestBZip2Codec` obtains a decompressor from `CodecPool` and passes it into split input creation, validating that pure-Java bzip2 ignores the dummy for actual reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/BZip2DummyDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.java

## Purpose
`Bzip2Compressor` is the native/JNI-backed `Compressor` implementation for bzip2.

## Important APIs and Types
It implements `Compressor`. Constructors configure block size, work factor, and direct buffer size. Important methods include `reinit`, `setInput`, `needsInput`, `finish`, `finished`, `compress`, byte counters, `reset`, `end`, static `initSymbols`, and native `getLibraryName`.

## Control Flow
Input bytes are copied from the user buffer into a direct uncompressed buffer. `compress()` first drains any remaining compressed direct-buffer output, then rewinds the output buffer, calls native `deflateBytesDirect()`, and exposes produced bytes to the caller. `finish()` sets a flag consumed by native code. `reset()` and `reinit()` tear down and recreate the native stream.

## State and Persistence
State includes a native stream pointer, block size, work factor, direct buffers, user buffer offsets/lengths, flags for retained uncompressed buffer data, and finish/finished flags. State is synchronized per instance and process-local only.

## Dependencies and Integration
Loaded through `Bzip2Factory` after `NativeCodeLoader` and native symbol initialization. Used by `BZip2Codec` native stream paths and `CodecPool`.

## Risks
Native resource lifecycle depends on `end(stream)` being called during reset/reinit/end. `checkStream()` throws `NullPointerException` after `end()`, which can surface if closed compressors are reused incorrectly. Direct buffer sizes and native counters must remain consistent with Java buffer bookkeeping.

## Test Signals
`TestBzip2CompressorDecompressor` exercises native bzip2 round trips and a multithreaded smoke test when native bzip2 is available. CodecPool tests cover generic pooling mechanics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Compressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.java

## Purpose
`Bzip2Decompressor` is the native/JNI-backed `Decompressor` implementation for bzip2.

## Important APIs and Types
It implements `Decompressor`. Constructors configure conserve-memory mode and direct buffer size. Key methods include `setInput`, `needsInput`, `finished`, `decompress`, `getBytesWritten`, `getBytesRead`, `getRemaining`, `reset`, `end`, and static `initSymbols`.

## Control Flow
`setInput()` copies compressed user bytes into a direct input buffer and resets the direct output buffer to empty. `decompress()` drains any remaining direct output, otherwise calls native `inflateBytesDirect()` unless already finished, then exposes bytes to the user buffer. `needsInput()` refills the direct compressed buffer from the saved user buffer when needed.

## State and Persistence
State includes a native stream pointer, direct buffers, compressed buffer offsets/lengths, user buffer offsets/lengths, conserve-memory setting, and finished flag. Methods are synchronized. There is no durable persistence.

## Dependencies and Integration
Loaded and selected by `Bzip2Factory` when native bzip2 is configured and available. Used by `BZip2Codec` native input paths and pooled by `CodecPool`.

## Risks
As with the compressor, native lifecycle errors can leak or invalidate the stream. `getRemaining()` combines Java and native remaining bytes and is important for concatenated-stream handling in `DecompressorStream`. Dictionaries are unsupported.

## Test Signals
`TestBzip2CompressorDecompressor` validates native bzip2 decompression and multithreaded independent instances when native support is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Decompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Factory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Factory.java

## Purpose
`Bzip2Factory` centralizes selection between native bzip2 compressor/decompressor implementations and pure-Java dummy placeholders.

## Important APIs and Types
Static APIs include `isNativeBzip2Loaded`, `getLibraryName`, compressor/decompressor type and instance factories, and configuration helpers for block size and work factor.

## Control Flow
`isNativeBzip2Loaded(conf)` reads `io.compression.codec.bzip2.library`, resets cached load state when the library name changes, uses pure Java immediately for `java-builtin`, and otherwise attempts native symbol initialization if Hadoop native code is loaded. Failures log a warning and fall back to pure Java. Factory methods branch on cached native availability.

## State and Persistence
Static state stores the last requested bzip2 library name and whether native bzip2 loaded. Configuration keys for block size/work factor are stored in `Configuration`, not globally persisted.

## Dependencies and Integration
Depends on `NativeCodeLoader`, `Bzip2Compressor`, `Bzip2Decompressor`, dummy classes, and SLF4J. `BZip2Codec` calls it for all native-vs-Java decisions.

## Risks
Load state is static and keyed only by library name, so changing configurations in the same JVM intentionally resets load state but still shares state across users. Native initialization catches `Throwable`, which favors fallback availability over surfacing native problems. Pure-Java mode exposes dummy compressor/decompressor types for interface compatibility.

## Test Signals
`TestCommonConfigurationFields` references the config keys. `TestBzip2CompressorDecompressor` uses `assumeTrue(Bzip2Factory.isNativeBzip2Loaded(...))` to gate native tests. BZip2 codec tests cover Java fallback stream behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/Bzip2Factory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2InputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2InputStream.java

## Purpose
`CBZip2InputStream` is Hadoop's pure-Java bzip2 decompressor, adapted from Apache Ant and enhanced for Hadoop split processing. It expects the leading `BZ` bytes to be handled by the caller.

## Important APIs and Types
It extends `InputStream` and implements `BZip2Constants`. Public/visible APIs include constructors with `READ_MODE`, `read`, `skipToNextMarker`, visible `skipToNextBlockMarker`, `numberOfBytesTillNextMarker`, `getProcessedByteCount`, `updateReportedByteCount`, `close`, and CRC error reporting. Internal `STATE` drives decompression phases, and nested `Data` holds large per-block arrays.

## Control Flow
In `CONTINUOUS` mode, the constructor initializes stream headers unless lazy initialization is needed for empty input. In `BYBLOCK` mode, it scans to the next block delimiter and then initializes one block. `read(byte[], int, int)` emits decompressed bytes until the buffer fills or the internal state returns end-of-block/end-of-stream; in BYBLOCK mode it returns `END_OF_BLOCK` after a block so `BZip2Codec` can update compressed positions. Decoding reads Huffman tables, move-to-front data, reconstructs the Burrows-Wheeler transform, applies randomized or non-randomized output setup, and validates CRCs.

## State and Persistence
State includes bit buffer/live bits, raw and reported compressed byte counters, current block metadata, CRCs, current output character/state-machine variables, and large block decode arrays (`ll8`, `tt`, Huffman tables, selectors). Closing nulls data and the input stream. No durable state is written.

## Dependencies and Integration
Used by `BZip2Codec.BZip2CompressionInputStream` for pure-Java normal and split reads. Test utilities use `numberOfBytesTillNextMarker` and block marker scanning to validate split offsets.

## Risks
Instances are not thread-safe and allocate several MB per max-size block. Marker scanning works at bit granularity and must maintain byte counters exactly for split correctness. CRC errors are fatal. Public mutable constants from `BZip2Constants` can affect randomized block handling. Lazy initialization based on `available()` can be sensitive to unusual input stream implementations.

## Test Signals
`TestBZip2Codec` validates BYBLOCK and CONTINUOUS behavior through `BZip2Codec`. `BZip2Utils` and bzip2 text writer tests exercise block marker offsets. Corruption/CRC behavior should be covered when modifying decode paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2InputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2OutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2OutputStream.java

## Purpose
`CBZip2OutputStream` is Hadoop's pure-Java bzip2 compressor, adapted from Apache Ant. It writes bzip2 data after the caller has emitted the leading `BZ` magic bytes.

## Important APIs and Types
It extends `OutputStream` and implements `BZip2Constants`. Public APIs include constructors, `chooseBlockSize`, `write`, `finish`, `close`, `flush`, `getBlockSize`, and visible `getAllowableBlockSize`. Internals implement run-length encoding, block sorting, move-to-front transform, Huffman table generation, bit output, CRCs, randomization fallback, and nested `Data` arrays.

## Control Flow
Construction validates block size, allocates block data, writes the `h` format byte and block-size digit, and initializes the first block. Writes accumulate runs and encode them into the block; when the block reaches its allowable size, the current block is ended and a new block starts. `finish()` flushes any pending run, ends the block, writes the end-of-stream marker and combined CRC, then releases state. Compression flow is RLE -> block sort/BWT -> MTF generation -> Huffman table selection/refinement -> bitstream emission.

## State and Persistence
State includes current block index, original pointer, block size, bit buffer/live bits, CRCs, run tracking, sort work limits, block randomization flag, output stream, and memory-intensive arrays (`block`, `fmap`, `sfmap/quadrant`, frequency tables, selectors, heaps, sort stacks). Finish/close null out `out` and `data`.

## Dependencies and Integration
Used by `BZip2Codec.BZip2CompressionOutputStream` and bzip2 test utilities. It depends on `CRC`, `BZip2Constants`, and Hadoop `IOUtils` for close handling.

## Risks
Instances are not thread-safe and can allocate around 8.5 MB for 900k compression blocks. The `finalize()` method calls `finish()`, which is legacy and should not be relied on for resource management. Sorting is performance-sensitive and contains heavily unrolled code; small changes can affect compression ratio, speed, or correctness. The caller must write the `BZ` header separately.

## Test Signals
`TestBZip2Codec`, `BZip2TextFileWriter`, and stream reuse tests exercise valid stream generation, block boundaries, reset handling, and interoperability with `CBZip2InputStream`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CBZip2OutputStream.java -->
