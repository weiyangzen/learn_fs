<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc

## Purpose

This file implements reconciliation between currently available chunk parts and a target `Goal`, including operation counts, target permutation optimization, redundancy evaluation, removal safety, and full-copy counting.

## Important APIs, Types, and Functions

Implemented public methods include constructors, `setTarget()`, `addPart()` via header inline, `removePart()`, `optimize()`, `evalRedundancyLevel()`, `isSafeEnoughToWrite()`, `updateRedundancyLevel()`, `countPartsToMove()`, `canRemovePart()`, `canMovePartToDifferentLabel()`, `getLabelsToRecover()`, `getRemovePool()`, and `getFullCopiesCount()`. Key helpers are `operationCount()`, `evalOperationCount()`, `evalSliceRedundancyLevel()`, and `removePartBasicTest()`.

## Control Flow

`optimize()` uses a linear-assignment optimizer per slice to permute target parts to minimize recover/remove operations. It then evaluates operation counts and redundancy. Operation counting compares available and target label multisets, with wildcard labels absorbing otherwise-extra copies. Redundancy treats standard copies as `copies - 1`, XOR/EC slices as available distinct part count minus required data count, and combines slices into whole-chunk redundancy.

## State and Persistence Behavior

State is in-memory `Goal available_`, `Goal target_`, cached redundancy levels, per-slice operation counts, and total operation count. Nothing is persisted directly.

## Dependencies and Integration Points

It depends on `Goal`, `MediaLabel`, `slice_traits`, `linear_assignment_optimizer`, `ChunksAvailabilityState`, and flat/small containers. Master chunk maintenance logic can use it to schedule replication/deletion.

## Risks and Edge Cases

Query methods assume `optimize()` or `evalRedundancyLevel()` has been called. `removePart()` copies the label map proxy into `auto labels` and erases from that copy-like object; correctness depends on `Goal::Slice` proxy semantics. Wildcard handling is subtle and easy to regress. Unknown slice types are treated as lost.

## Test Signals

`chunk_copies_calculator_unittest.cc` covers add/remove, state transitions, optimization, redundancy updates, removal safety, recovery label selection, remove pools, and move counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator.cc -->
