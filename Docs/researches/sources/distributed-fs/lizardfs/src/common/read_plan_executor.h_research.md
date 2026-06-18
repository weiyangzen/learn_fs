<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.h -->
# sources/distributed-fs/lizardfs/src/common/read_plan_executor.h

## Purpose
Declares the coordinator that executes a complete read plan against located chunk parts. The source was read completely for this report.

## Important APIs, Types, And Functions
`ReadPlanExecutor`, `ChunkTypeLocations`, constructor, `executePlan`, `partsFailed`, static counters, and protected execution helper declarations define the API.

## Control Flow
Header flow is declarative; implementation owns orchestration.

## State And Persistence Behavior
Holds references/ids/owned plan plus execution maps and part containers for the last run.

## Dependencies And Integration Points
Used by client read paths after planners produce `ReadPlan` objects and chunk locations.

## Risks And Edge Cases
The executor is stateful across calls and not documented as thread-safe. `partsFailed` reports last execution only.

## Test Signals
Compile and integration tests should cover repeated `executePlan` calls and failed-part reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_plan_executor.h -->
