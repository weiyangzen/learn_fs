<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h -->
# sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h

## Purpose

`SliceRecoveryPlanner` builds `ReadPlan` objects that recover a single missing chunk part from available parts. It chooses between direct slice reads, chunk-data reconstruction, and parity recomputation.

## Important APIs, Types, and Functions

Important members are `prepare()`, `setScores()`, `isReadingPossible()`, and `buildPlan()`. The internal `BlockConverter` copies selected blocks from reconstructed full chunk data into the recovered part. Recovery modes are `kReadDataPart`, `kRecoverDataPart`, and `kRecoverParityPart`.

## Control Flow

`prepare()` first tries `SliceReadPlanner` for the exact requested part. If that fails and the target is a data part, it prepares `ChunkReadPlanner` for the corresponding full-chunk block positions. If the target is parity, it prepares `ChunkReadPlanner` for the data blocks needed to recompute parity. `buildPlan()` then either returns a direct slice plan, attaches `BlockConverter`, or attaches XOR/EC parity recovery functors.

## State and Persistence Behavior

Planner state is transient and stores the requested part, block range, selected mode, and helper planners. It does not persist data; returned plans describe reads and postprocessing.

## Dependencies and Integration Points

It depends on `ChunkReadPlanner`, `SliceReadPlanner`, `slice_traits`, `XorReadPlan`, `ECReadPlan`, `ReadPlan`, and `MFSBLOCKSIZE`.

## Risks and Edge Cases

Most validation is assert-only. Calling `buildPlan()` without a successful `prepare()` can hit impossible-state assertions. Correctness relies on `slice_traits` mapping part indices and data/parity counts exactly for standard, XOR, and EC layouts.

## Test Signals

`slice_recovery_planner_unittest.cc` covers XOR direct recovery, standard-to-XOR conversion, parity recovery, and recovery from other XOR levels. EC-specific coverage is not present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/chunkserver/slice_recovery_planner.h -->
