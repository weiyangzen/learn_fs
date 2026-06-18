# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/store/ByteBufferInputStream.java

Purpose: `InputStream` wrapper over a `ByteBuffer` with synchronized reads, mark/reset support, close-state enforcement, and bounded seeking through `skip()`.

Important APIs, types, and functions: constructor, `close()`, `isOpen()`, `read()`, `read(byte[],int,int)`, `skip()`, `available()`, `position()`, `hasRemaining()`, `mark()`, `reset()`, `markSupported()`, and `toString()`.

Control flow: read methods verify open state, return `-1` at EOF, and advance the underlying buffer position. `skip()` treats its argument as an absolute offset from current position and rejects negative or beyond-EOF positions. `close()` nulls the buffer reference so later operations fail.

State and persistence: stores declared size and mutable buffer reference/position. No persistence; it is used as an upload stream over off-heap or pooled buffers.

Dependencies and integration points: depends on `ByteBuffer`, Hadoop `FSExceptionMessages`, preconditions, and SLF4J. Created by `DataBlocks.ByteBufferBlock.startUpload()`.

Risks and test signals: `read(byte[], offset, length)` does not explicitly reject negative offset before calculating destination capacity; ByteBuffer will still enforce bounds but error shape may vary. Tests should cover close behavior, mark/reset, EOF, zero-length reads, invalid offsets/lengths, skip boundaries, and buffer release lifecycle in `DataBlocks`.
