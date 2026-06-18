# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ADeleteOnExit.java

## Purpose

Unit tests for S3A delete-on-exit close processing and request-factory initialization failure for invalid checksum algorithm configuration.

## Important APIs, Types, and Functions

Nested `TestS3AFileSystem` extends `S3AFileSystem`, counts `deleteOnExit()` calls, and decrements count in `deleteWithoutCloseCheck()`. Tests use S3 mock `headObject()`, `deleteOnExit()`, `close()`, and `S3AFileSystem.initialize()`.

## Control Flow

`testDeleteOnExit()` initializes a test filesystem against the mock bucket, stubs `headObject()` for `/file`, registers delete-on-exit, closes the filesystem, and asserts the counter returns to zero through close-time deletion. `testCreateRequestFactoryWithInvalidChecksumAlgorithm()` sets `fs.s3a.checksum.algorithm` to `INVALID` and expects initialization to throw a clear `IllegalArgumentException`.

## State, Dependencies, and Integration Points

State includes filesystem delete-on-exit tracking, mocked S3 object metadata, and configuration. It integrates S3A close processing, delete without close checks, request factory creation, checksum algorithm parsing, and Mockito request matching.

## Risks and Test Signals

The counter-based subclass directly observes internal close path behavior. It catches regressions where delete-on-exit entries are skipped on close, close checks prevent cleanup, or invalid checksum configuration fails later with less useful errors.
