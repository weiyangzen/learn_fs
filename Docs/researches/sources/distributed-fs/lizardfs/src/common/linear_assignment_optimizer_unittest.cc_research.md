<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc

## Purpose
Tests the auction optimizer against exhaustive search for small random assignment matrices. The source was read completely for this report.

## Important APIs, Types, And Functions
`getMaximumAssignmentValue` recursively enumerates all assignments; tests call `auctionOptimization` and compare objective values.

## Control Flow
For sizes 2 through 10, the test fills random values, copies the matrix, solves with auction, and compares to brute force on the original copy.

## State And Persistence Behavior
No persistence; all matrices are stack arrays.

## Dependencies And Integration Points
Depends on gtest and `common/random.h` for random input generation.

## Risks And Edge Cases
Brute force grows factorially, so coverage is intentionally bounded. It does not check overflow or negative/extreme values systematically.

## Test Signals
Passing tests are strong algorithmic correctness signals for small integer cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/linear_assignment_optimizer_unittest.cc -->
