<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc

## Purpose

This file tests availability and replication-state counters.

## Important APIs, Types, and Functions

Tests are `ChunksAvailabilityStateTests.AddRemoveChunk`, `ChunksReplicationStateTests.AddRemoveChunk`, and `ChunksReplicationStateTests.MaximumValues`.

## Control Flow

The tests add counters for multiple goals/states, move counts between states by remove/add, remove counts back to zero, and verify replication/delete matrix counters including clamping for very large part counts.

## State and Persistence Behavior

Only local counter objects are used; serialization is not tested.

## Dependencies and Integration Points

It uses GoogleTest and the state header.

## Risks and Edge Cases

Underflow and serialization sparse-map behavior are not covered. Goal ids near `GoalId::kMax` are not tested directly.

## Test Signals

Passing tests signal basic counter indexing and clamping correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunks_availability_state_unittest.cc -->
