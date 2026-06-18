
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
