# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSInputStreamTest.java

## Purpose
This test validates `OBSInputStream` range-read behavior against a mocked `ObsClient`.

## Important APIs, Types, And Functions
The fixture creates mocked `ObsObject` instances and range-sensitive `getObject(GetObjectRequest)` answers. Test methods cover `close`, `readInt`, `readByteArray`, and `skip`.

## Control Flow
Setup prepares three byte positions, each returning a stream over the remaining bytes. Reads should open the correct range lazily, skip should advance position, and close should make later reads fail with `IOException("Stream closed")`.

## State And Persistence
All state is in mocks, byte arrays, and the tested stream's in-memory cursor. No external OBS state is used.

## Dependencies And Integration Points
It depends on JUnit, Mockito, Hamcrest, `CountingRetry`, global Alluxio configuration, and OBS SDK request/object types. It exercises the same `MultiRangeObjectInputStream` pattern used by OSS and Swift.

## Risks
The mock only checks range starts and does not validate range end, retry, or provider exceptions. It gives a good signal for cursor handling but not real OBS protocol behavior.

## Test Signals
Passing tests indicate that basic single-byte, buffer, skip, and closed-stream semantics remain stable for OBS reads.
