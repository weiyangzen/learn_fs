<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard.h -->
# sources/distributed-fs/lizardfs/src/common/lambda_guard.h

## Purpose
Defines a move-only RAII guard that invokes a supplied callable in its destructor unless ownership was moved away. The source was read completely for this report.

## Important APIs, Types, And Functions
`LambdaGuard<Function>`, move constructor, destructor, and `makeLambdaGuard` are the API.

## Control Flow
Construction stores a callable and marks it valid. Move construction transfers the callable and invalidates the source. Destruction calls the callable only when valid.

## State And Persistence Behavior
State is just a bool plus the callable. No persistence.

## Dependencies And Integration Points
Used by code paths needing cleanup on multiple exits, such as connection or resource handling.

## Risks And Edge Cases
The callable must be safe in a destructor; throwing from it would propagate during destruction and can terminate if another exception is active. Copy is disabled for safety.

## Test Signals
`lambda_guard_unittest.cc` confirms moved-from guards do not execute and moved-to guards execute at scope exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lambda_guard.h -->
