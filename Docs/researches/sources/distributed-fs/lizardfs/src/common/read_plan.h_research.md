<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan.h -->
# sources/distributed-fs/lizardfs/src/common/read_plan.h

## Purpose
Defines the abstract read-plan model for complex reads involving waves, redundant chunk parts, recovery, and post-processing. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadPlan`, `PartsContainer`, `ReadOperation`, `readOffset`, `readBufferSize`, `fullBufferSize`, pure virtual `isReadingFinished`, `isFinishingPossible`, `postProcessRead`, virtual `postProcessData`, and `to_string` are the core API.

## Control Flow
Read operations specify request offset/size, destination buffer offset, and wave. `postProcessData` lays out post-process buffers before the read buffer, runs `postProcessRead`, then walks configured post-process operations backward toward the final output buffer.

## State And Persistence Behavior
State is plan-owned vectors of read operations and post-process functions plus buffer sizes/prefetch flag. No persistence.

## Dependencies And Integration Points
Implemented by XOR/EC/simple read plan classes elsewhere and executed by `ReadPlanExecutor`.

## Risks And Edge Cases
Buffer layout is delicate: post-process sizes and function contracts must match exactly. Debug-only bounds asserts catch overlap/layout errors only in non-release builds.

## Test Signals
Tests should use concrete plan implementations to cover finish predicates, recovery post-processing, and buffer layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan.h -->
