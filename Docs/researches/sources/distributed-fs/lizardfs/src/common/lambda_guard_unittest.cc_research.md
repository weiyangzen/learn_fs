<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc

## Purpose
Validates the RAII cleanup behavior of `LambdaGuard`. The source was read completely for this report.

## Important APIs, Types, And Functions
Uses `makeLambdaGuard`, lambda captures, and move construction.

## Control Flow
The test nests guards, moves them, lets inner scope destruct, checks the side effect, then relies on outer destruction after the expectation.

## State And Persistence Behavior
No persistent state; state is a local integer counter.

## Dependencies And Integration Points
Depends on gtest and `lambda_guard.h`.

## Risks And Edge Cases
Coverage is intentionally minimal and does not test throwing callables or assignment, which is not defined.

## Test Signals
Passing test confirms single execution after move transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard_unittest.cc -->
