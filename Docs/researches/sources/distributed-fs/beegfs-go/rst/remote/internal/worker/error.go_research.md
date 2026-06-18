# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/error.go

## Purpose
This file defines worker-package sentinel errors.

## Important APIs, Types, and Functions
`ErrWorkRequestNotFound` indicates that a requested work item does not exist on the worker node. It is used to distinguish a successful cleanup-equivalent condition from transport or state errors.

## Control Flow
There is no executable control flow beyond variable initialization.

## State and Persistence Behavior
No state is persisted. The sentinel supports `errors.Is` checks across worker and worker-manager layers.

## Dependencies and Integration Points
`BeeSyncNode.UpdateWork` returns `ErrWorkRequestNotFound` for gRPC `NotFound`. `workermgr.Manager.UpdateJob` treats this as a cancellation-equivalent outcome and marks the work request cancelled rather than unknown.

## Risks and Edge Cases
The sentinel conflates "not found because already gone" and "not found because the wrong node was contacted"; the caller currently treats it as safe cancellation. Correctness depends on worker assignment metadata being accurate.

## Test Signals
No direct tests target this file. Its behavior is indirectly covered by cancellation paths where worker update results are interpreted by `workermgr.UpdateJob`.
