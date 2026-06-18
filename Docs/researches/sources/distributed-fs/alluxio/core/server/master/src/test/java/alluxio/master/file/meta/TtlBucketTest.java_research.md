# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketTest.java

## Purpose
`TtlBucketTest` validates individual TTL bucket interval math, membership uniqueness, retry-attempt metadata, ordering, equality, and hash behavior.

## Important APIs, Types, and Functions
It exercises `TtlBucket` construction, `getTtlIntervalStartTimeMs`, `getTtlIntervalEndTimeMs`, static `getTtlIntervalMs`, `addInode`, `removeInode`, `getInodeIds`, `getInodeExpiries`, `size`, `compareTo`, `equals`, and `hashCode`.

## Control Flow, State, and Persistence
Tests add duplicate and distinct inode ids to one bucket, remove them, re-add with default and explicit retry attempts, then compare buckets with equal and different start times.

## Dependencies and Integration Points
The test uses `TtlTestUtils` inode factories and validates the in-memory data structure that `TtlBucketList` orders and expires.

## Risks
Bucket equality and ordering are based only on interval start time, not contents. Retry attempt storage must stay attached to inode expiry entries, or TTL retry scheduling can drift.

## Test Signals
Signals cover interval end calculation, start-time comparison, duplicate suppression, file and directory-like membership, retry-attempt updates, compare/equality symmetry, and hash consistency.
