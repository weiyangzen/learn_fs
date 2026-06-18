<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc

## Purpose

This file tests chunkserver operation counters, defect scoring, and proxy cleanup behavior.

## Important APIs, Types, and Functions

Tests are `ChunkserverStatsCounters`, `ChunkserverStatsDefectTracking`, `ChunkserverStatsProxy`, `AllPendingDefectiveRead`, `AllPendingDefectiveWrite`, and `AllPendingDefectiveLonger`.

## Control Flow

Tests register/unregister reads and writes against sample addresses, inspect copied stats, mark defective/working, scope a proxy to trigger destructor cleanup, and mark only still-pending proxy operations defective.

## State and Persistence Behavior

Only local `ChunkserverStats` and proxy objects are used. Timeout expiry is not tested because checks happen immediately.

## Dependencies and Integration Points

It uses GoogleTest, `NetworkAddress`, and the stats classes.

## Risks and Edge Cases

The tests do not cover unregister underflow, concurrent access, or defect-score recovery after timeout. They verify immediate score reduction but not exact score values except equality to 1.

## Test Signals

Passing tests signal correct normal balanced operation accounting and proxy destructor cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunkserver_stats_unittest.cc -->
