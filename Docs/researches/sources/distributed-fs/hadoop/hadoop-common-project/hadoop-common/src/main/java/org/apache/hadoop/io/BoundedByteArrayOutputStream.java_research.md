<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java

Purpose: reusable byte-array-backed `OutputStream` that enforces a write limit smaller than or equal to its backing capacity.

Important APIs, types, and functions: constructors allocate or accept a buffer. `resetBuffer()` validates offset/limit and initializes positions. `write(int)` and `write(byte[], off, len)` append while throwing `EOFException` on limit overflow. `reset(int)` and `reset()` reuse the buffer with a new limit. `getLimit()`, `getBuffer()`, `size()`, and `available()` expose buffer state.

Control flow: every write checks bounds before mutating the buffer and advances `currentPointer` on success.

State and persistence: state is the backing byte array, start offset, absolute limit, and current pointer. No external persistence; callers may consume the backing buffer.

Dependencies and integration points: limited-private utility for HDFS/MapReduce serialization paths.

Risks and test signals: `reset(int)` stores `limit` as the provided value rather than `startOffset + newlim`, unlike `resetBuffer()`, which is risky for non-zero start offsets. Tests should cover overflow exceptions, offset-backed buffers, reset semantics, available/size, zero-length writes, and bounds checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BoundedByteArrayOutputStream.java -->
