# sources/distributed-fs/beegfs-go/rst/remote/internal/workermgr/errors.go

## Purpose
This file defines sentinel errors used by the BeeRemote worker manager and worker pools.

## Important APIs, Types, and Functions
The exported errors are `ErrNoWorkersConnected`, `ErrFromAllWorkers`, `ErrNoWorkersInPool`, `ErrNoPoolsForNodeType`, and `ErrWorkerNotInPool`.

## Control Flow
There is no executable control flow beyond variable initialization. Callers wrap these sentinels with context and can inspect them with `errors.Is`.

## State and Persistence Behavior
No state is persisted. The errors annotate scheduling and cancellation failures that are stored later in work-result status messages by the manager.

## Dependencies and Integration Points
`pool.go` uses these errors when no workers can accept work or a target worker is missing. `manager.go` stores them in generated `flex.Work` statuses and uses them to decide whether all work requests were scheduled or updated.

## Risks and Edge Cases
The errors intentionally describe broad classes. Recovery behavior depends on higher layers preserving enough contextual message text, such as worker type and node ID, when wrapping them.

## Test Signals
No direct tests target the error declarations. They are indirectly exercised by scheduling and cancellation error paths in job-manager tests.
