# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSInputStreamTest.java

## Purpose
This JUnit/Mockito suite validates basic read behavior for `TOSInputStream`.

## Important Tests
Setup mocks `TOSV2.getObject` to return byte-array streams for positional ranges and constructs a `TOSInputStream` with `CountingRetry(1)`. `close` expects reads after close to throw `IOException("Stream closed")`. `readInt` reads three bytes sequentially. `readByteArray` reads into a buffer. `skip` confirms skipping one byte advances the stream.

## Dependencies and Integration
The test depends on Alluxio global configuration for multi-range chunk size, Volcengine SDK model classes, Mockito argument matching, and JUnit `ExpectedException`.

## Signals and Gaps
The tests exercise `MultiRangeObjectInputStream` integration more than TOS metadata handling. They do not cover 404 retry exhaustion, non-404 TOS errors, empty objects, range clamping, or `headObject` metadata failures.
