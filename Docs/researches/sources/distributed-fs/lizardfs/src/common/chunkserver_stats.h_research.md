<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h

## Purpose

This header declares chunkserver load/defect statistics and a scoped proxy for operation registration.

## Important APIs, Types, and Functions

`ChunkserverStats::ChunkserverEntry` exposes pending read/write counts, total operation count, and `score()`. `ChunkserverStats` exposes read/write register/unregister and defect/working markers. `ChunkserverStatsProxy` exposes the same operation methods plus `allPendingDefective()` and unregisters tracked operations on destruction.

## Control Flow

Users register operations before IO, unregister afterward, and use scores/counts to prefer less loaded/nondefective chunkservers. The proxy is intended for scoped cleanup.

## State and Persistence Behavior

The stats object owns an address-to-entry map protected by a mutex. Entries track pending counters, defect count, and timeout. No disk persistence exists.

## Dependencies and Integration Points

It integrates with chunk readers/writers and global mount-instance stats through `extern ChunkserverStats globalChunkserverStats`.

## Risks and Edge Cases

The proxy is explicitly not thread-safe. Register/unregister balancing is required to avoid unsigned underflow. Because `getStatisticsFor()` returns by value, callers cannot mutate entries directly.

## Test Signals

Unit tests validate basic behavior. Additional tests should cover underflow attempts, defect timeout expiry, and concurrent register/unregister operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats.h -->
