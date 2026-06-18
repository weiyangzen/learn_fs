# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSInputStreamTest.java

## Purpose
This test validates `OSSInputStream` basic cursor and range-read behavior.

## Important APIs, Types, And Functions
Setup creates an `OSS` mock and one `OSSObject` per starting position. Tests cover closing, single-byte reads, byte-array reads, and skipping.

## Control Flow
Each mocked `getObject` answer is keyed by request range start and returns a stream over the remaining bytes. The stream should lazily issue ranged reads as its cursor advances and throw `IOException("Stream closed")` after close.

## State And Persistence
Only in-memory byte arrays and mocks are used. No real OSS object or local file is created.

## Dependencies And Integration Points
It uses Mockito, JUnit, Hamcrest, `CountingRetry`, and Alluxio configuration for multi-range chunk size.

## Risks
The test does not cover range end clamping, metadata lookup behavior, retry on `NoSuchKey`, or non-missing OSS errors.

## Test Signals
Passing tests confirm that the OSS input stream preserves ordinary Java `InputStream` semantics for read, skip, and close.
