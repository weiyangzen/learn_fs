# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/crypto/TestCryptoStreamsNormal.java

## Purpose
`TestCryptoStreamsNormal` runs the shared crypto stream tests against plain Java byte-array streams. It isolates crypto stream behavior when the wrapped streams do not implement Hadoop-specific interfaces such as `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `Syncable`, readahead/drop-behind controls, enhanced byte-buffer access, file descriptors, or `unbuffer`.

## Important APIs, Types, and Functions
The class extends `CryptoStreamsTestBase`. `init()` resolves the default `CryptoCodec`. `getOutputStream()` wraps an anonymous `ByteArrayOutputStream` in `CryptoOutputStream`; the anonymous stream snapshots its internal `buf` and `count` into instance fields on `flush()` and `close()`. `getInputStream()` creates a `ByteArrayInputStream` over the captured encrypted bytes and wraps it with `CryptoInputStream`.

## Control Flow
Base tests write through the crypto output stream, causing bytes to be captured on flush or close. Later reads construct a byte-array input stream over the saved bytes. Hadoop-interface tests are overridden as empty disabled JUnit methods so the inherited base suite only exercises generic stream behavior.

## State and Persistence
Encrypted test data is kept in memory in `buffer` and `bufferLen`; there is no filesystem persistence. Because the anonymous output stream exposes its backing array, correctness depends on using `bufferLen` to delimit valid data.

## Dependencies and Integration Points
The file integrates Java `ByteArrayInputStream`/`ByteArrayOutputStream`, Hadoop `CryptoInputStream`/`CryptoOutputStream`, `CryptoCodec`, `Configuration`, and JUnit 5. Its main integration point is the shared base class, not a concrete filesystem.

## Risks and Edge Cases
The test deliberately avoids Hadoop-only capabilities. It guards against accidental assumptions that all crypto stream users can seek, pread, byte-buffer-read, sync, or unbuffer. The buffer capture pattern is also a reminder that the backing array may be larger than the written payload.

## Test Signals
Enabled inherited tests signal that crypto streams work over minimal Java streams. Disabled tests signal expected `UnsupportedOperationException` or absent-interface behavior for seek, readFully, positioned reads, byte-buffer reads, sync, enhanced buffer access, `seekToNewSource`, combined operations, and `unbuffer`.
