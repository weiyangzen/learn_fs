<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.h -->
# sources/distributed-fs/lizardfs/src/common/read_operation_executor.h

## Purpose
Declares the per-part read operation executor and its state machine fields. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadOperationExecutor` constructor, move-only semantics, `sendReadRequest`, `continueReading`, `readAll`, `isFinished`, `chunkType`, `server`, and the private `ReadOperationState` enum/state processors are visible internally.

## Control Flow
The header documents single-step `continueReading` versus blocking `readAll` flow.

## State And Persistence Behavior
Owns no socket lifetime by itself; it stores the fd and writes into caller-provided buffer memory.

## Dependencies And Integration Points
Integrated by `ReadPlanExecutor` and chunkserver connection pools.

## Risks And Edge Cases
Move operations are defaulted while containing raw pointers/fd ids, so container moves must preserve external ownership expectations.

## Test Signals
Compile tests plus executor integration tests protect constructor and state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.h -->
