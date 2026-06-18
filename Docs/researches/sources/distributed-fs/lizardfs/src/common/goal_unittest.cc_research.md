# sources/distributed-fs/lizardfs/src/common/goal_unittest.cc

Purpose: tests the goal/slice data model and merge algorithm.

Important APIs/types/functions: macro `sneakyPartType`; tests `BasicSliceOperations`, `BasicSliceMerge`, `BasicXorMerge` variants, and `GoalMerge`.

Control flow: tests construct standard and XOR slices, assign media labels and wildcard labels, check expected copy counts and string rendering, merge slices with different part-label arrangements, and verify merged results.

State and persistence: test-only goal objects.

Dependencies and integration: includes `common/goal.h` and `gtest`.

Risks: coverage is focused on standard/xor cases; EC slice types and invalid-goal paths are not directly exercised. The tests use expected exact string output, which is useful but can be brittle if formatting changes.

Test signals: good signal for the assignment/union behavior that preserves minimal target parts during goal merge.
