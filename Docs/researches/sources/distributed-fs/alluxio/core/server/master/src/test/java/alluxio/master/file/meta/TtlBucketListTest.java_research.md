# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/TtlBucketListTest.java

## Purpose
`TtlBucketListTest` verifies grouping of TTL-bearing inodes into interval buckets and polling/removing expired buckets.

## Important APIs, Types, and Functions
The test exercises `TtlBucketList.insert`, `remove`, and `pollExpiredBuckets`. It uses `TtlIntervalRule` to set a 10 ms bucket interval and `TtlTestUtils` to construct inode views with specific TTL values.

## Control Flow, State, and Persistence
The test inserts files whose TTLs fall into bucket `[0,10)` and `[10,20)`, polls at boundary and interior times, reinserts after polling to continue assertions, and removes individual inodes before polling again.

## Dependencies and Integration Points
`TtlBucketList` depends on an `InodeStore` for production behavior, but this test uses a mock because it is focused on bucket membership and expiration order.

## Risks
Boundary handling is the main risk: TTL equal to the bucket end belongs to the next bucket, and polling at end time expires the previous interval. Reinsert-after-poll patterns can hide single-shot lifecycle mistakes if changed.

## Test Signals
Signals include no early expiry, correct grouping within bucket 1, bucket 2 separation, all-bucket expiry at the second boundary, removal of one or all entries, and empty final state.
