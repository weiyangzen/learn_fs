## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferPositionedReadable.java

Purpose: evolving stream interface for positioned reads into a `ByteBuffer`, including a read-fully variant.

Important APIs and types: `read(long position, ByteBuffer buf)` returns bytes read or EOF; `readFully(long position, ByteBuffer buf)` fills the remaining buffer or throws `EOFException`.

Control flow: interface only. Contract says reads must not change the stream's current offset, should be thread-safe, must advance buffer position on success, and must treat zero-length requests as valid.

State and persistence behavior: no interface state. Implementations read from the underlying file without modifying the sequential stream cursor.

Dependencies and integration points: complements `PositionedReadable`, `ByteBufferReadable`, and `StreamCapabilities.PREADBYTEBUFFER`.

Risks: buffer state after exceptions is undefined. Callers must probe capability before downcasting or invoking.

Test signals: implementation tests should cover zero-length reads, EOF returns vs `EOFException`, buffer position/limit changes, thread-safety, current-position preservation, and direct vs heap buffers.
