<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java

Purpose: adapter that presents a `DataOutput` as an `OutputStream`.

Important APIs, types, and functions: static `constructOutputStream(DataOutput)` returns the argument directly if it is already an `OutputStream`, otherwise wraps it in `DataOutputOutputStream`. `write(int)`, `write(byte[],off,len)`, and `write(byte[])` delegate to the underlying `DataOutput`.

Control flow: stream writes become `DataOutput` byte writes, enabling APIs that require `OutputStream` to target `DataOutput` implementations.

State and persistence: state is the wrapped `DataOutput` reference. Persistence depends on the wrapped target.

Dependencies and integration points: useful for serializers and compression streams that accept only `OutputStream`.

Risks and test signals: no flush or close behavior is added when wrapping non-stream `DataOutput`. Tests should cover direct return for existing streams, byte and array writes, and interaction with `DataOutputBuffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/DataOutputOutputStream.java -->
