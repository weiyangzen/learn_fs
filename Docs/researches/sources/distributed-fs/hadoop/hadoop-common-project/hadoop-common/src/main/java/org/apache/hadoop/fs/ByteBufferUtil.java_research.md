## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferUtil.java

Purpose: private helper for fallback reads when zero-copy reads are unavailable, using a `ByteBufferPool`.

Important APIs and types: `fallbackRead(InputStream, ByteBufferPool, int)` allocates direct buffers when the stream supports true byte-buffer reads and heap buffers otherwise. `streamHasByteBufferRead` avoids treating `FSDataInputStream` wrapper support as sufficient unless the wrapped stream also implements `ByteBufferReadable`.

Control flow: validate pool and allocated buffer; choose directness; cap requested length to capacity. For direct/byte-buffer-readable streams, loop until max length or EOF, then flip. For heap fallback, read once into the backing array and set the limit. On error or EOF without data, return the buffer to the pool and return null.

State and persistence behavior: stateless. Buffer ownership transfers to the caller only on success; otherwise returned to the pool.

Dependencies and integration points: integrates with `ByteBufferPool`, `ByteBufferReadable`, `FSDataInputStream`, and zero-copy read paths.

Risks: heap fallback assumes `buffer.array()` is available; this is enforced indirectly by `useDirect=false` and pool compliance. Direct loop can spin if a buggy stream repeatedly returns zero before filling the buffer. Returning null at EOF must be handled by callers.

Test signals: cover null pool, pool returning null, direct vs heap allocation validation, EOF before data, partial EOF after data, buffer return on failure, zero-return stream behavior, and `FSDataInputStream` wrapping rules.
