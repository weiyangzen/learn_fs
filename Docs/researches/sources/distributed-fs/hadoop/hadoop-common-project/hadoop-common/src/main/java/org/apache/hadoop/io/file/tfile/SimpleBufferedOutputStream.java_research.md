# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/SimpleBufferedOutputStream.java

Purpose: lightweight buffered output stream that borrows a caller-provided buffer and exposes current buffered byte count.

Important APIs/types/functions: constructor with downstream `OutputStream` and `byte[]`; `write(int)`, `write(byte[], int, int)`, `flush()`, and `size()`.

Control flow: single-byte writes flush when the buffer is full. Bulk writes larger than the buffer bypass buffering after flushing; smaller writes flush first if they do not fit, then copy into the borrowed buffer. `flush()` drains buffered bytes and flushes downstream. `size()` reports buffered bytes not yet written.

State and persistence: in-memory borrowed buffer and count; downstream receives persisted bytes only on flush/bypass.

Dependencies and integration: used by `BCFile.Writer.WBlockState` so compressed-size accounting can include `fsBufferedOutput.size()` before downstream flush.

Risks: no internal bounds checks beyond normal arraycopy behavior for bulk arguments; borrowed buffer must outlive the stream. Tests should cover buffered count, flush behavior, large-write bypass, boundary writes exactly filling the buffer, and downstream exception propagation.
