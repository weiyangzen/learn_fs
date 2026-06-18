# sources/distributed-fs/lizardfs/src/master/task_manager.h

## Purpose

`task_manager.h` declares `TaskManager`, its abstract `Task`, and nested `Job` container used to process background filesystem work incrementally. The source was read as a complete 178-line header.

## Important APIs, Types, and Functions

`Task` declares pure virtual `execute` and `isFinished`. `Job` owns an intrusive task list, job ID, description, finish callback, and methods to finalize/process/add tasks. `TaskManager` exposes two `submitTask` overloads, `processJobs`, `getCurrentJobsInfo`, `cancelJob`, `workAvailable`, and `reserveJobId`.

## Control Flow

The header defines a cooperative model where each task receives the current timestamp and a work queue to which it may append/prepend more tasks. Jobs group the original task and all generated subtasks.

## State and Persistence Behavior

The manager state is runtime-only. Job descriptions and IDs are exposed for status; filesystem persistence belongs to tasks.

## Dependencies and Integration Points

It depends on intrusive lists, `JobInfo`, callbacks, memory/string/list/vector support, and is included by all task implementations in this subset.

## Risks and Edge Cases

Tasks must be heap-allocated and compatible with intrusive-list ownership. Misbehaving tasks that never finish or generate unbounded work can monopolize job capacity until watchdog/budget stops each processing tick.

## Test Signals

Compile coverage, lifecycle tests with mock tasks, and filesystem integration tests that inspect `JobInfo` while long operations run.
