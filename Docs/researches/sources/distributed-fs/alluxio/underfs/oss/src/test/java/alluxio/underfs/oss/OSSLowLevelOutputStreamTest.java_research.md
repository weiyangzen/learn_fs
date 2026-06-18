# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSLowLevelOutputStreamTest.java

## Purpose
This test verifies Aliyun OSS low-level streaming upload behavior.

## Important APIs, Types, And Functions
It uses PowerMock to intercept file and stream construction and Mockito to mock `OSS`, executor futures, and multipart result objects. Tests cover byte writes, small file writes, large multipart writes, empty file close, flush, and close.

## Control Flow
The tested stream should keep small writes local until close and use `putObject`. When data crosses the partition threshold, it should initiate multipart upload, submit part uploads, increment part numbers, wait on futures during flush, and complete multipart upload on close.

## State And Persistence
State under assertion includes mocked temp buffering, part number, upload id, executor submissions, and content hash. Real filesystem and OSS persistence are avoided.

## Dependencies And Integration Points
It validates the `ObjectLowLevelOutputStream` subclass hooks implemented by `OSSLowLevelOutputStream`.

## Risks
The test does not exercise abort or exception paths. PowerMock constructor interception can break when implementation details change.

## Test Signals
Passing tests give high confidence that the threshold split between single put and multipart upload remains intact.
