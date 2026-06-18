# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/HasEnhancedByteBufferAccess.java

Purpose: `HasEnhancedByteBufferAccess` marks input streams that can return direct/enhanced `ByteBuffer` reads, often mmap-backed, with explicit release semantics.

Important APIs: `read(ByteBufferPool, int, EnumSet<ReadOption>)` and `releaseBuffer(ByteBuffer)`.

Control flow and state: as an interface it defines the contract only. Implementations may allocate buffers from the stream itself or use a provided pool. `maxLength == 0` must return an empty buffer; positive reads return null at EOF; returned buffers must be released by callers.

Dependencies and integration: implemented by `FSDataInputStream` internals and filesystem-specific streams that support zero-copy or pooled reads. Uses `ByteBufferPool` and `ReadOption`.

Risks: buffer lifecycle is critical: callers must not use buffers after release, and streams may warn/leak if buffers remain unreleased at close. Passing a null factory can force `UnsupportedOperationException` when fallback allocation is needed.

Test signals: zero-length read, EOF null, pooled fallback, null-factory unsupported path, release idempotence/validation in implementations, close-with-unreleased-buffer behavior, and option handling.
