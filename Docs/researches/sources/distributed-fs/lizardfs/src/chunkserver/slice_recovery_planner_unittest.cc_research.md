<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc -->
# sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc

## Purpose

This file verifies that `SliceRecoveryPlanner` can build executable plans that reproduce expected chunk-part bytes.

## Important APIs, Types, and Functions

Helpers are `xor_part()`, `checkPartRecovery(...)` overloads, and tests `VerifyRecovery1` through `VerifyRecovery4`. It uses `ReadPlanTester::buildData()`, `executePlan()`, and `compareBlocks()`.

## Control Flow

Each helper prepares synthetic part data, calls `SliceRecoveryPlanner::prepare()`, asserts recovery is possible, builds a plan, executes it through the tester, and compares the output to the target part block range.

## State and Persistence Behavior

State is test-local maps of `ChunkPartType` to byte vectors. No persistent state is touched.

## Dependencies and Integration Points

It integrates with chunk type constants, the planner, and the unit-test read-plan executor.

## Risks and Edge Cases

The tests focus on XOR layouts and do not cover EC parity recovery, unavailable plans, nonzero first-block ranges broadly, invalid block counts except the helper's `-1` shorthand, or score-based selection.

## Test Signals

Passing tests signal that generated read plans and postprocessors produce correct bytes for representative XOR data/parity recovery scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner_unittest.cc -->
