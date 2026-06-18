# sources/distributed-fs/eos/unit_tests/mgm/FusexCastBatchTests.cc

## Purpose
Tests basic batching and execution of deferred FUSEX cast callbacks. It verifies callback registration count and execution behavior for captured-by-value and captured-by-reference lambdas.

## Important APIs, types, and functions
The test uses `eos::mgm::FusexCastBatch::Register`, `GetSize`, and `Execute`.

## Control flow
It first registers two mutable lambdas that capture `value` by copy, executes them, and asserts the outer value is unchanged. It then registers three reference-capturing lambdas, executes them, and asserts the accumulated side effect is six.

## State and persistence
State is the batch's in-memory callback list. The test implies `Execute()` clears or replaces previous callbacks because `GetSize()` after the second registration sequence is expected to be three rather than five.

## Dependencies and integration points
Depends on Google Test and MGM FUSE server cast batching. It supports FUSEX notification batching paths.

## Risks and test signals
The test covers basic semantics but not exception behavior, execution order, callback removal, repeated `Execute()`, or thread safety. Those areas matter if batches are used across asynchronous FUSE broadcast paths.
