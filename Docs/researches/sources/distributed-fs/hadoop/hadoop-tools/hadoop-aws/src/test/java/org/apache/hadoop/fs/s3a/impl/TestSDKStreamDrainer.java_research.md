# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/TestSDKStreamDrainer.java

## Purpose
`TestSDKStreamDrainer` validates `SDKStreamDrainer`, which either drains unread bytes from an AWS SDK input stream for connection reuse or aborts the stream when requested or on failure.

## Important APIs, Types, and Functions
- Tests `SDKStreamDrainer.applyRaisingException()`, `aborted()`, and `getDrained()`.
- Uses `InternalConstants.DRAIN_BUFFER_SIZE` to cover buffer-boundary cases.
- `FakeSDKInputStream` extends `InputStream` and implements AWS SDK `Abortable`, tracking capacity, bytes read, close state, and abort state.
- Uses `EMPTY_INPUT_STREAM_STATISTICS` for statistics dependency injection.

## Control Flow
Abort tests verify requested abort does not drain. Drain tests cover normal length, empty stream, single byte, exactly one buffer, multiple buffers, and stream underflow. Failure tests configure the fake stream to throw after a threshold: normal draining surfaces `IOException` and aborts, while explicit abort suppresses read exceptions because no read occurs. A sanity test confirms fake single-byte reads produce the expected count.

## State and Persistence Behavior
State is fully in the fake input stream and drainer instance. No external persistence or network access occurs.

## Dependencies and Integration Points
The test integrates S3A stream close/drain behavior with AWS SDK abortable streams and input stream statistics plumbing.

## Risks and Edge Cases
`FakeSDKInputStream.read(byte[],...)` swallows exceptions after partial reads to mimic stream behavior, so failure only surfaces when exception occurs before any byte in a buffer read. This is intentional but subtle.

## Test Signals
Passing confirms stream close handling drains remaining bytes when safe, aborts when requested, and aborts on read failures without hiding unexpected drain exceptions.
