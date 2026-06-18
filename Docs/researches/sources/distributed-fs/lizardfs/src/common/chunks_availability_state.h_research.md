<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h -->
# sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h

## Purpose

This header defines aggregate counters for chunk availability and replication/delete needs by goal.

## Important APIs, Types, and Functions

`detail::SerializableGoalIdArray<T>` stores arrays indexed by goal id but serializes only non-default entries as a map. `ChunksAvailabilityState` tracks safe, endangered, and lost counts per goal. `ChunksReplicationState` tracks chunks to replicate by missing-part count and chunks to delete by redundant-part count.

## Control Flow

Add/remove methods increment/decrement indexed counters. Serialization compacts sparse goal arrays. Replication state clamps missing/redundant part counts at `kMaxPartsCount - 1`.

## State and Persistence Behavior

State is in-memory counters that serialize for status/protocol transport. It does not guard underflow.

## Dependencies and Integration Points

It depends on `GoalId`, serialization helpers, and `Goal`. Master status, CGI, and replication accounting can consume these counters.

## Risks and Edge Cases

`SerializableGoalIdArray::deserialize()` asserts the array is default-initialized before loading, so reusing a nonempty object in release builds may merge stale data. Remove operations can underflow `uint64_t` counters if misbalanced. `kMaxPartsCount` is 11, matching legacy reporting rather than all modern part counts.

## Test Signals

`chunks_availability_state_unittest.cc` covers add/remove counters and clamping of large missing/redundant values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state.h -->
