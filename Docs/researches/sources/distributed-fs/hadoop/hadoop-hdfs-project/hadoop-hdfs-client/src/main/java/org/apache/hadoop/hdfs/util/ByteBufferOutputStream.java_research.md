# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/util/ByteBufferOutputStream.java

Purpose: `ByteBufferOutputStream` adapts a `ByteBuffer` to the `OutputStream` API.

Important APIs/types/functions: constructor stores the target buffer. `write(int)` writes one byte via `ByteBuffer.put`. `write(byte[], int, int)` writes a byte range via `ByteBuffer.put(byte[], off, len)`.

Control flow: all writes advance the underlying buffer position and rely on `ByteBuffer` for bounds checking.

State and persistence behavior: no additional state beyond the target buffer; all data is stored in the caller-supplied buffer.

Dependencies and integration points: depends on Java NIO and is used where APIs require an `OutputStream` but HDFS code wants to fill an existing `ByteBuffer`.

Risks and test signals: `ByteBufferOverflowException` is unchecked and can escape despite `OutputStream` signatures declaring `IOException`. Tests should cover single/bulk writes, position advancement, and overflow behavior.
