<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc

## Purpose

This file validates `ChunkCopiesCalculator` behavior for goal matching, redundancy, optimization, and operation queries.

## Important APIs, Types, and Functions

Tests include `addPart`, `removePart`, `getState`, `evalRedundancyLevel`, `optimize`, `updateRedundancyLevel`, `canRemoveExtraPartsFromSliceSimple`, `canRemoveExtraPartsFromSlice`, `getLabelsToRecover`, `getRemovePool`, and `countPartsToMove`. It uses `goal_config::parseLine()` and chunk type constants.

## Control Flow

Tests build goals from text, add/remove parts with media labels, call `optimize()` or redundancy methods, and assert state/operation/label results.

## State and Persistence Behavior

All state is test-local `Goal` and calculator objects. No disk persistence is involved.

## Dependencies and Integration Points

It integrates the calculator with goal parsing, `slice_traits`, media labels, and chunk type constants.

## Risks and Edge Cases

Coverage is strong for XOR and standard cases but does not visibly cover EC slices, wildcard-only targets broadly, or mutation after cached optimization. Several tests mutate internal `Goal&` references, matching real usage but also bypassing encapsulation.

## Test Signals

Passing tests signal that scheduling counts and safety decisions match expected XOR/standard goal behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_copies_calculator_unittest.cc -->
