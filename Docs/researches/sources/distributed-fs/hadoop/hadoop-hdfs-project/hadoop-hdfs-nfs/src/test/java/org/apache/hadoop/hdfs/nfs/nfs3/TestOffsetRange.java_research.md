# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestOffsetRange.java

## Purpose
`TestOffsetRange` verifies validation and ordering behavior for `OffsetRange`, the key type used by `OpenFileCtx.pendingWrites`.

## Important APIs, Types, And Functions
It constructs `OffsetRange` instances and uses `OffsetRange.ReverseComparatorOnMin`.

## Control Flow
Four constructor tests assert invalid ranges throw `IllegalArgumentException`: empty, negative start, both negative, and negative-to-positive. `testCompare` checks equality for identical ranges and reverse ordering by minimum offset.

## State And Persistence
There is no state beyond local objects.

## Dependencies And Integration Points
The comparator contract directly affects `ConcurrentSkipListMap` ordering in `OpenFileCtx`, including dump traversal and contiguous write-back selection.

## Risks
The test only checks min-offset ordering, not overlap behavior, max boundaries, or map interactions with equal minimum and different maximum values.

## Test Signals
Passing protects basic range invariants and reverse comparator semantics needed for out-of-order write buffering.
