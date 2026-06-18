<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java

Purpose: reusable `DataOutputStream` over an in-memory growing byte array.

Important APIs, types, and functions: nested `Buffer` exposes backing data and length, grows when writing from `DataInput`, and can temporarily set count. Outer methods include `getData()`, `getLength()`, `reset()`, `write(DataInput,int)`, `writeTo(OutputStream)`, and `writeInt(int, offset)` for patching an existing four-byte slot.

Control flow: callers write through normal `DataOutput` methods, then consume the valid prefix of `getData()`. `writeInt(v, offset)` rewinds the internal count to overwrite bytes and restores the old count without increasing `DataOutputStream.written`.

State and persistence: state is the backing byte array, count, and inherited written byte count. No persistence except data copied by callers.

Dependencies and integration points: heavily used by writable serialization, BloomMapFile key encoding, and in-memory copy paths.

Risks and test signals: `getData()` exposes mutable extra-capacity bytes. `writeInt(offset)` can only overwrite existing bytes. Tests should cover growth, reset clearing written count, direct DataInput transfer, offset patching, and backing-array aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputBuffer.java -->
