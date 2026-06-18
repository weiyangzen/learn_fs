# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSOutputStreamTest.java

## Purpose
This test covers the local-buffered OSS output stream.

## Important APIs, Types, And Functions
The fixture mocks `OSS`, temp `File`, local `BufferedOutputStream`, and `PutObjectResult`. Tests cover constructor validation, `write(int)`, full-array write, ranged write, close failure, close success, and flush.

## Control Flow
Writes should delegate directly to the local stream. Successful close closes local output, uploads with `putObject`, stores ETag as content hash, and deletes the temporary file. Failure close paths are expected to raise an exception.

## State And Persistence
The production class persists to local disk until close; the test replaces that with mocks and verifies interactions.

## Dependencies And Integration Points
It uses PowerMock/Mockito and Aliyun OSS SDK request/result types. It complements streaming upload tests by covering the non-streaming path.

## Risks
The test does not validate real MD5 metadata, actual temp directory selection, or deletion failure handling.

## Test Signals
Passing tests show correct write delegation, flush behavior, close idempotence basics, and upload-on-close semantics.
