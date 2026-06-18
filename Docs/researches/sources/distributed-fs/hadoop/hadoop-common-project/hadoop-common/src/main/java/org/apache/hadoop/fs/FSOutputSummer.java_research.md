## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FSOutputSummer.java

Purpose: `FSOutputSummer` is an abstract output stream that generates checksums for data chunks before writing chunks and checksum bytes to an underlying implementation.

Important APIs and types: subclasses implement `writeChunk(byte[], int, int, byte[], int, int)` and `checkClosed()`. Public and protected APIs include `write(int)`, `write(byte[], int, int)`, `flush`, `flushBuffer`, `flushBuffer(keep, flushPartial)`, `getBufferedDataSize`, `getChecksumSize`, `getDataChecksum`, `setChecksumBufSize`, `resetChecksumBufSize`, `convertToByteStream`, and `createWriteTraceScope`.

Control flow, state, and persistence: the class maintains a data checksum, a data buffer sized to nine checksum chunks, a checksum buffer, and a byte count. Large writes bypass copying when the internal buffer is empty and the input length covers the whole buffer. `flush()` writes only complete chunks, while `flushBuffer(..., flushPartial)` controls whether trailing partial chunks are written or kept. `writeChecksumChunks` calculates chunked sums and invokes `writeChunk` per chunk inside an optional tracing scope. No durable persistence exists.

Dependencies and integration: HDFS output streams subclass this to pair data packet writes with checksums. It depends on `DataChecksum`, `TraceScope`, `StreamCapabilities`, and `Checksum`.

Risks and test signals: risks include partial chunk handling, buffer resizing, checksum-size assumptions in `int2byte`, close-state checks only on array writes, and write failures after checksums are computed. Tests should cover single-byte writes, direct large writes, partial flush keep/drop behavior, buffer resize/reset, checksum bytes, tracing scope close, and subclass close enforcement.
