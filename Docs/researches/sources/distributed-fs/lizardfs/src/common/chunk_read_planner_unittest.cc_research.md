<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc

## Purpose

This file verifies that `ChunkReadPlanner` can reconstruct contiguous chunk data from available split parts.

## Important APIs, Types, and Functions

Helpers are `xor_part()` and `checkReadingChunk()` overloads. Active tests are `VerifyRead1` through `VerifyRead4`.

## Control Flow

Tests build synthetic part data, prepare a planner for a full-chunk block range, assert readability, execute the returned plan through `ReadPlanTester`, and compare output bytes with the standard chunk data.

## State and Persistence Behavior

Only local byte maps and planner/tester objects are used.

## Dependencies and Integration Points

It depends on the planner, chunk type constants, and `ReadPlanTester`.

## Risks and Edge Cases

Unrecoverable tests are present but commented out. EC layouts, score preference, invalid ranges, and no-plan cases are not covered here.

## Test Signals

Passing tests signal correct block extraction/reordering for representative XOR layouts and block ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner_unittest.cc -->
