# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/OutputBuffer.java

Purpose: `OutputBuffer` is a reusable in-memory `FilterOutputStream` that exposes its backing byte array and valid length for repeated serialization without creating new `ByteArrayOutputStream` instances.

Important APIs and types: the private `Buffer` extends `ByteArrayOutputStream`, exposing `getData()`, `getLength()`, an overridden `reset()`, and `write(InputStream, int)` for direct bulk reads into the buffer. Public `OutputBuffer` exposes `getData`, `getLength`, chainable `reset`, and `write(InputStream, int)`.

Control flow: normal writes go through inherited `FilterOutputStream` behavior into the backing `Buffer`. `write(InputStream, int)` computes the new count, grows the backing array by doubling or exact fit, uses `IOUtils.readFully` to read exactly the requested number of bytes at the current count, then advances count.

State and persistence: state is an in-memory byte array and count. `reset` drops the count to zero but retains capacity. `getData()` returns the mutable internal buffer, valid only up to `getLength()`. There is no external resource persistence.

Dependencies and integration points: depends on `IOUtils.readFully` and Java IO. It is paired with `InputBuffer` and `DataOutputBuffer` for Hadoop internal serialization loops.

Risks and test signals: risks include exposed mutable internal storage, retained large buffers after spikes, exact-read failure leaving partial bytes in the buffer before count advances, and integer overflow for very large `count + len`. Tests should cover growth behavior, exact input length enforcement, reuse after reset, visible data length, and mutation through `getData`.
