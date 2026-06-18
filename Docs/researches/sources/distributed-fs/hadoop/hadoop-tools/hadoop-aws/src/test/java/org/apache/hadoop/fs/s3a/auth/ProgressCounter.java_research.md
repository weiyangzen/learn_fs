# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/ProgressCounter.java

## Purpose

`ProgressCounter.java` is a small `Progressable` test helper for asserting progress callback counts during S3A commit/upload operations.

## Important APIs, Types, and Functions

The class implements `Progressable`, stores an `AtomicLong count`, increments it in `progress()`, exposes `getCount()`, and provides `assertCount(String, int)`.

## Control Flow

Any caller passes the instance as a progress callback. Each callback increments the counter atomically. Tests query or assert the final count after upload attempts.

## State and Persistence Behavior

State is a thread-safe in-memory counter. It is not resettable except by creating a new instance.

## Dependencies and Integration Points

It integrates with Hadoop progress callback APIs and S3A commit operation tests, especially assumed-role commit restrictions.

## Risks and Edge Cases

Atomicity allows parallel callbacks, but assertions use integer expected values. If upload implementations change callback frequency, tests may need adjustment.

## Test Signals

Signals are exact progress counts, such as zero after a forbidden upload initiation and one-per-successful pending commit upload in commit tests.
