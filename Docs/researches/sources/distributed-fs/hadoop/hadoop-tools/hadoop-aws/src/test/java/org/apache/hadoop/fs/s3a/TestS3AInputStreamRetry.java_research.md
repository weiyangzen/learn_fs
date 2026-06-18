# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AInputStreamRetry.java

## Purpose

Unit tests for `S3AInputStream` recovery when reads or reopen GET requests fail. The suite validates retry behavior for single-byte reads, buffer reads, `readFully()`, repeated seek/read operations, range parsing, and out-of-range responses.

## Important APIs, Types, and Functions

The file constructs `S3AInputStream` directly using `ObjectReadParameters`, `ObjectInputStreamCallbacks`, `S3ObjectAttributes`, and `S3AReadOpContext`. Helpers include `failingInputStreamCallbacks()`, `maybeFailInGetCallback()`, `mockInputStreamCallback()`, `awsServiceException()`, and `mockedInputStream()`.

## Control Flow

Basic tests inject streams that fail during early reads and one GET attempt, then eventually return the test string `012345678ABCDEF`; reads must return correct bytes after retries. Repeated seek tests fail every second GET with a no-response SDK exception and verify ten seek/read cycles still read offset zero. Callback logic increments attempt count, optionally throws, parses the Range header, rejects invalid ranges with 416, skips to the requested start, and returns an AWS `ResponseInputStream`.

## State, Dependencies, and Integration Points

State includes callback attempt counters, mock filesystem read context, S3 object metadata such as eTag/version ID, and synthetic response streams. It integrates S3A read contexts, object attributes, AWS SDK response streams, audit noop spans, future submission callbacks, and `S3ATestUtils.requestRange()`.

## Risks and Test Signals

The two repeated seek tests currently have identical failure setup despite different names, so they may not distinguish stream-closed failures from no-response failures. Strong signals include correct bytes after retries, retry of GET failures during reopen, 416 handling for invalid ranges, and preservation of position semantics.
