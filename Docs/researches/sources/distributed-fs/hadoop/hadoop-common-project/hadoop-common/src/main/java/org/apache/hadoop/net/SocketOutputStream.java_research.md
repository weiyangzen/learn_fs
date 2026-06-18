# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/net/SocketOutputStream.java

Purpose: `OutputStream` and `WritableByteChannel` wrapper that writes to selectable socket channels with explicit timeouts and supports zero-copy file transfer.

Important APIs/types/functions: constructors, `write(int)`, `write(byte[], int, int)`, `write(ByteBuffer)`, `close`, `getChannel`, `isOpen`, `waitForWritable`, `transferToFully`, and `setTimeout`.

Control flow: nested `Writer.performIO` delegates to `WritableByteChannel.write`. Byte-array writes loop until the buffer drains; if an exception occurs after a partial write, the writer is marked closed because `OutputStream` cannot report partial progress. `transferToFully` waits for writability, calls `FileChannel.transferTo`, advances position/count, and records wait and transfer timings.

State and persistence: holds a `Writer`; no persistence. Construction puts the channel in nonblocking mode.

Dependencies and integration: used by HDFS data transfer paths and `NetUtils.getOutputStream`. Integrates with `LongWritable` timing counters.

Risks: transfer count is `int`, limiting single call size. EOF detection depends on file size when `transferTo` returns zero. Mixing original blocking socket streams with this wrapper is unsafe after nonblocking mode.

Test signals: `TestSocketIOWithTimeout` covers writes, timeouts, and close behavior; data-transfer tests usually exercise `transferToFully`.
