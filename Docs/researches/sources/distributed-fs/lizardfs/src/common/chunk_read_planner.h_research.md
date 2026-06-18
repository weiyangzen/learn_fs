<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h

## Purpose

`ChunkReadPlanner` builds a `ReadPlan` that reads a contiguous full-chunk block range from available chunk parts, including split XOR/EC layouts.

## Important APIs, Types, and Functions

Public APIs are constructor, `prepare()`, `setScores()`, `isReadingPossible()`, and `buildPlan()`. Internal helpers are `BlockConverter`, `getTypeList()`, and `getRequiredParts()`.

## Control Flow

`prepare()` collects slice types present in available parts, then scans each type. For each type it computes required data part indices for the requested full-chunk block range, asks `SliceReadPlanner` if those parts are readable, and records block/part ranges for the first successful type. `buildPlan()` gets a part-level plan and, for nonstandard types, appends `BlockConverter` to reorder split part blocks into contiguous chunk order.

## State and Persistence Behavior

The planner stores transient selected type, required parts, and range metadata. Returned plans own executable read/postprocess steps; no persistent state is written.

## Dependencies and Integration Points

It depends on `SliceReadPlanner`, `slice_traits`, `ReadPlan`, `small_vector`, and `MFSBLOCKSIZE`. `SliceRecoveryPlanner` uses it for reconstructing missing parts from full chunk data.

## Risks and Edge Cases

Type selection is first-successful, not globally cheapest, despite score support inside `SliceReadPlanner`. TODOs note over-reading for multi-lane requests. Validation is mostly assert-only; invalid ranges in release builds can produce bad plans.

## Test Signals

`chunk_read_planner_unittest.cc` exercises representative XOR reads and output byte comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_read_planner.h -->
