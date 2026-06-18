<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java

## Purpose
Compatibility tests for `DataOutputBuffer`, `DataInputBuffer`, and `DataInputByteBuffer` across Java `DataInput`/`DataOutput` primitive operations.

## Important APIs, Types, and Functions
`writeJunk()` writes deterministic random bytes, shorts, ints, longs, doubles, floats, and byte arrays to a `DataOutput`. `readJunk()` replays the same random sequence and validates reads from a `DataInput`. Tests use `ByteBuffer.wrap` and `DataInputByteBuffer.reset`.

## Control Flow and State
A static `Random` is reset to seed 31 before each write/read phase. `testBaseBuffers()` writes and reads through Hadoop byte-array buffers, resets, and repeats. `testDataInputByteBufferCompatibility()` writes with `DataOutputBuffer`, wraps the result in `ByteBuffer`, and reads through `DataInputByteBuffer`.

## Dependencies and Integration Points
Integrates buffer classes used by writable serialization and nio-backed readers. It validates bit-level compatibility for primitive types.

## Risks and Test Signals
Risk areas are byte order, floating-point bit preservation, buffer offset/limit handling, and reset semantics. Signals are exact primitive equality and byte-array equality over 1000 randomized operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestDataByteBuffers.java -->
