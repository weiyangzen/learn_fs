# sources/distributed-fs/lizardfs/src/master/task_manager.cc

## Purpose

`task_manager.cc` implements a small cooperative job manager for filesystem tasks that may need to be split across event-loop iterations. The file was read as a complete 128-line implementation.

## Important APIs, Types, and Functions

Implemented methods include `TaskManager::Job::finalize`, `finalizeTask`, `processTask`, `getInfo`, `TaskManager::submitTask` overloads, `processJobs`, `getCurrentJobsInfo`, and `cancelJob`.

## Control Flow

Submitting a task creates a `Job`, attaches a temporary callback to detect immediate completion, processes up to `initial_batch_size` tasks synchronously, and either returns the final status or enqueues the job with the caller callback and returns `WAITING`. `processJobs` rotates through the job list, executing one task per job until a task budget or `SignalLoopWatchdog` expiry. Finished tasks are erased; status errors finalize the entire job. Cancelling finalizes a matching job with `NOTDONE`.

## State and Persistence Behavior

The manager stores an in-memory list of jobs and a monotonically increasing job ID counter. It owns dynamically allocated tasks through intrusive lists and disposes them on job finalization/destruction. Persistent filesystem effects are performed by task implementations.

## Dependencies and Integration Points

Dependencies include `intrusive_list`, `JobInfo`, loop watchdog, filesystem metadata/node includes, and protocol status codes. It is integrated by remove, snapshot, setgoal, settrashtime, and other long-running filesystem operations.

## Risks and Edge Cases

Callback semantics differ for immediate versus queued completion: caller callback is only used if work remains after the initial batch. `cancelJob` finalizes but does not erase immediately; the next process pass removes finished jobs. Task implementations can push more tasks into the same intrusive list during execution, so iterator validity and task self-finish behavior are critical.

## Test Signals

Unit tests should cover immediate completion, queued completion callback, task-generated subtasks, error finalization, cancellation, job info reporting, rotation fairness across jobs, and watchdog-limited processing.
