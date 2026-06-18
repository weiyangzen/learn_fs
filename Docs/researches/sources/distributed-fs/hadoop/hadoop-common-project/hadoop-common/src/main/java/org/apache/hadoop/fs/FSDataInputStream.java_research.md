## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSDataInputStream.java

Purpose: `FSDataInputStream` wraps an `InputStream` as a data input stream with Hadoop seek, positioned read, byte-buffer read, vector read, unbuffer, stream capability, and IO statistics interfaces.

Important APIs and types: the constructor requires the wrapped stream to implement both `Seekable` and `PositionedReadable`. It delegates `seek`, `getPos`, `read(position, byte[])`, `readFully`, `seekToNewSource`, byte-buffer reads, file descriptor access, readahead/drop-behind, enhanced byte-buffer reads, unbuffer, stream capabilities, IO statistics, and vectored reads.

Control flow, state, and persistence: the only local mutable state is an `IdentityHashStore<ByteBuffer, ByteBufferPool>` tracking fallback enhanced-read buffers. If the wrapped stream lacks `HasEnhancedByteBufferAccess`, `read(ByteBufferPool, int, opts)` uses `ByteBufferUtil.fallbackRead` and records the returned buffer for later release. `releaseBuffer` either delegates or returns fallback buffers to their original pool, rejecting unknown buffers. No stream state is persisted by this wrapper.

Dependencies and integration: this is the standard public read stream returned by Hadoop filesystems. It integrates with optional interfaces, `StoreImplementationUtils`, `ByteBufferPool`, `IOStatisticsSupport`, and `PositionedReadable` vector APIs.

Risks and test signals: risk centers on optional capability casts, buffer lifecycle leaks, and unsupported operation messages. Tests should cover constructor rejection, delegation, fallback buffer release, unknown buffer release, null file descriptors, unbuffer policy, byte-buffer positioned reads, vectored reads, and IO statistics retrieval.
