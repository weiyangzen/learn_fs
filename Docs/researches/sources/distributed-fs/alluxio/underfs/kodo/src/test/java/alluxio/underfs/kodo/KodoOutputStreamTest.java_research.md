## sources/distributed-fs/alluxio/underfs/kodo/src/test/java/alluxio/underfs/kodo/KodoOutputStreamTest.java

### Purpose
`KodoOutputStreamTest` validates local buffering behavior and close-time cleanup for Kodo writes.

### Important APIs, Types, And Functions
Tests use PowerMock to intercept constructors for `File`, `FileOutputStream`, and `BufferedOutputStream`, plus Mockito mocks for `KodoClient` and streams.

### Control Flow
`testConstructor` forces `FileOutputStream` to throw and expects an `IOException`. Write tests construct a stream, write using each overload, close it, and verify local write calls. `testClose` verifies temp-file deletion. `testFlush` verifies flush delegation.

### State, Persistence, And Dependencies
No real Kodo state is used. Some tests use mocked temp files; others use configured tmp dirs. Dependencies include PowerMockRunner, Mockito, and JUnit rules.

### Integration Points
The tests protect `KodoOutputStream`, which is returned by `KodoUnderFileSystem.createObject`.

### Risks
They do not assert upload invocation, upload failure swallowing, duplicate close behavior, or MD5 behavior.

### Test Signals
Passing tests show that writes are buffered locally, flush reaches the local stream, constructor IO errors propagate, and close attempts cleanup.
