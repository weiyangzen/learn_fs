# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/PathPropertiesView.java

## Purpose
`PathPropertiesView` is an immutable-style value object returned by `PathProperties.snapshot`. It packages a point-in-time view of path properties with the corresponding hash and last update time.

## Important APIs and Types
- Fields: `Map<String, Map<String,String>> mProperties`, `String mHash`, `long mLastUpdateTime`.
- Constructor accepts the full properties map, hash, and timestamp.
- Getters expose properties, hash, and last update time.

## Control Flow
There is no behavior beyond construction and getters. Snapshot consistency is provided by `PathProperties`, which builds this object under a read lock.

## State and Persistence
This class is not journaled. It carries copied state from `PathProperties`; callers should treat the map as a snapshot payload.

## Dependencies and Integration Points
Used by meta master configuration hash and path configuration response building. It depends only on Java collections.

## Risks and Edge Cases
The class does not defensively copy or wrap its constructor argument. Correct immutability depends on the producer passing a copy and consumers not mutating it unexpectedly.

## Test Signals
Tests are simple value-object checks: getters return constructor values and `PathProperties.snapshot` supplies an isolated map.
