# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSImageCompression.java

## Purpose

`FSImageCompression` is a small container around optional fsimage compression. It decides whether an fsimage should be compressed from configuration or from an on-disk image header, records the chosen Hadoop `CompressionCodec`, writes the compression header, and wraps input/output streams so the rest of fsimage serialization can read or write uncompressed bytes regardless of the stored representation.

## Important APIs, Types, and Functions

The only state is `imageCodec`, which is `null` for no compression and a `CompressionCodec` instance when compression is enabled. `getImageCodec()` exposes it for callers/tests. `createNoopCompression()` returns the uncompressed variant.

`createCompression(Configuration)` reads `dfs.image.compress` (`DFS_IMAGE_COMPRESS_KEY`) and, when enabled, reads the configured codec class name from `DFS_IMAGE_COMPRESSION_CODEC_KEY` with Hadoop's default. `createCompression(Configuration,String)` resolves the class name through `CompressionCodecFactory.getCodecByClassName` and throws an `IOException` if the codec is unavailable.

`readCompressionHeader(Configuration,DataInput)` reads a boolean stored in the image. If false, it returns no-op compression. If true, it reads a codec class name via `Text.readString` and resolves that codec.

`unwrapInputStream(InputStream)` returns a `DataInputStream` over either `imageCodec.createInputStream(is)` or a `BufferedInputStream`. `writeHeaderAndWrapStream(OutputStream)` writes the boolean and optional codec class name to an unbuffered output stream, then returns a `DataOutputStream` over either the codec output stream or a `BufferedOutputStream`. `toString()` reports either the codec canonical name or `no compression`.

## Control Flow

During save, fsimage code calls `FSImageCompression.createCompression(conf)`. The saver passes the resulting object to the image format writer, which calls `writeHeaderAndWrapStream` before writing the image body. The header is always uncompressed and precedes the compressed body. When compression is enabled, the codec class canonical name is persisted so readers can select the same codec. When disabled, the returned body stream is still buffered.

During load, image format code reads early image metadata and calls `readCompressionHeader(conf,in)`. The boolean determines whether a codec class name follows. Then `unwrapInputStream` produces a stream yielding the uncompressed image payload for downstream deserialization.

## State and Persistence Behavior

The persistent compression metadata is minimal: one boolean followed, when true, by a codec class name encoded with Hadoop `Text`. The compressed data itself starts immediately after that header. This design makes compression self-describing per image file but still dependent on the reader's classpath and Hadoop codec configuration.

A no-op compression object is represented by `imageCodec == null`; there is no separate enum or flag after construction. Stream buffering differs by mode: uncompressed paths add Java buffering here, while compressed paths rely on the codec stream returned by `CompressionCodec`.

One subtle implementation detail is that `writeHeaderAndWrapStream` creates a `DataOutputStream dos` for the header, writes the header through it, and then wraps the original `OutputStream` for the body. This works because the header stream is not separately buffered, but callers must pass an unbuffered output stream as documented.

## Dependencies and Integration Points

The class depends on `Configuration`, `DFSConfigKeys`, `CompressionCodec`, `CompressionCodecFactory`, and Hadoop `Text`. It is used by `FSImage.saveFSImage` through `FSImageFormatProtobuf.Saver`, by `saveLegacyOIVImage`, and by fsimage format loaders/savers that own the concrete image wire format. It is not used for edit logs.

## Risks

The main operational risk is codec availability. A NameNode can write an image with a codec that a later NameNode process cannot resolve, causing load failure. Configuration changes must therefore be coordinated with installed codecs. Header compatibility is also important: changing the boolean/string order would make existing compressed images unreadable.

Because this class wraps streams, premature closing/flushing behavior is important in callers. The body stream returned by `writeHeaderAndWrapStream` must be closed or flushed by the saver so codec trailers and buffered bytes reach disk. Passing an already buffered or transformed stream can violate the method's assumption and make header/body ordering harder to reason about.

## Test Signals

Fsimage save/load restart tests indirectly cover compression when run with `dfs.image.compress=true` and a codec available in the test classpath. `TestSaveNamespace` and MiniDFSCluster restart/checkpoint tests are the strongest integration signals because they force image write, md5 sidecar creation, reload, and edit replay. Additional focused validation should exercise no-op compression, a configured supported codec, an unsupported codec class producing `IOException`, and reading a compressed image after changing unrelated fsimage settings.
