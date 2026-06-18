# sources/distributed-fs/alluxio/underfs/obs/src/test/java/alluxio/underfs/obs/OBSOutputStreamTest.java

## Purpose
This unit test validates the non-streaming OBS output stream that buffers to a local temporary file and uploads on close.

## Important APIs, Types, And Functions
The fixture mocks `ObsClient`, `File`, `BufferedOutputStream`, and `PutObjectResult`. Tests cover constructor preconditions, `write(int)`, full-array write, ranged write, failed close, successful close, and flush forwarding.

## Control Flow
Writes are expected to pass through to the local buffered stream. `close` closes the local stream, uploads the file through `putObject`, records the returned ETag/content hash, and deletes the temp file. Error tests force OBS exceptions and expect I/O failure.

## State And Persistence
The production stream persists bytes temporarily on local disk until close. In this test, disk objects are mocked; state assertions focus on calls, deletion, closed status, and optional content hash.

## Dependencies And Integration Points
It depends on PowerMock to intercept file and stream construction and on OBS SDK model classes. It complements the low-level streaming output tests.

## Risks
The test is implementation-sensitive because constructor calls are mocked. It does not cover actual filesystem cleanup failures or large-object behavior.

## Test Signals
Passing tests verify local buffering semantics, upload-on-close, flush delegation, and basic failure propagation for OBS non-streaming writes.
