## sources/distributed-fs/alluxio/underfs/hdfs/src/test/java/alluxio/underfs/hdfs/PreadSeekableStream.java

### Purpose
`PreadSeekableStream` is a test helper that exposes both `Seekable` and `PositionedReadable` over a wrapped `FSDataInputStream` so tests can spy on normal versus positioned reads.

### Important APIs, Types, And Functions
It extends `FilterInputStream` and implements `read(long, byte[], int, int)`, both `readFully` overloads, `seek`, `getPos`, and `seekToNewSource` by delegating to the wrapped `FSDataInputStream`.

### Control Flow
Every method casts `in` to `FSDataInputStream` and delegates immediately.

### State, Persistence, And Dependencies
State is the wrapped stream. It depends on Hadoop seekable/positioned interfaces and is only used in tests.

### Integration Points
`HdfsUnderFileSystemTest.verifyPread` wraps the real stream with this helper and then a Mockito spy to count call types.

### Risks
The helper assumes the wrapped stream is always an `FSDataInputStream`; misuse with a different stream would fail by `ClassCastException`.

### Test Signals
Its value is in enabling verification that `HdfsPositionedUnderFileInputStream` chooses the intended read API after skip/seek patterns.
