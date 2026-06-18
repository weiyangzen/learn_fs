
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
