
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
