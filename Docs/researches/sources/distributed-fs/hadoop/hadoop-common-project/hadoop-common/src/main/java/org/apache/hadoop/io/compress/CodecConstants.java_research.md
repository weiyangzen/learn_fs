
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
