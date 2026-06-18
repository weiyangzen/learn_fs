<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java

Purpose: `DataInputStream` implementation over one or more `ByteBuffer` instances.

Important APIs, types, and functions: nested `Buffer` is an `InputStream` over a `ByteBuffer[]`, tracks current buffer index, position, and total length. `reset(ByteBuffer...)` installs input buffers and computes remaining bytes. `read()` and `read(byte[],off,len)` consume from current buffers. Accessors expose underlying buffers, consumed position, and total length.

Control flow: reads advance the positions of the supplied ByteBuffers. Multi-buffer reads continue into later buffers until requested length is satisfied or buffers are exhausted.

State and persistence: state is the ByteBuffer array and read cursors. It mutates the positions of caller-provided buffers and has no persistence.

Dependencies and integration points: useful for deserializing data already held in NIO buffers.

Risks and test signals: `read(byte[],off,len)` can return 0 if the current buffer has no remaining bytes and len is positive before advancing, which can surprise InputStream users. Tests should cover empty buffers, multi-buffer boundaries, position mutation, readFully behavior, and reset reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataInputByteBuffer.java -->
