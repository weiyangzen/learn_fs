# sources/distributed-fs/beegfs-go/rst/sync/internal/workmgr/errors.go

## Purpose
This file defines BeeSync work-manager sentinel errors.

## Important APIs, Types, and Functions
`ErrNotReady` indicates work operations were requested before BeeRemote-provided runtime config was applied. `ErrConfigUpdateNotAllowed` describes unsupported post-initial configuration changes, although this particular sentinel is not used in the selected manager code.

## Control Flow
There is no executable control flow beyond variable initialization.

## State and Persistence Behavior
No state is persisted. The errors give stable markers for readiness and config-update failures.

## Dependencies and Integration Points
`manager.go` wraps `ErrNotReady` in gRPC `FailedPrecondition` responses from `SubmitWorkRequest` and `UpdateWork`. Config update restrictions are mostly enforced by RST client-store and BeeRemote client behavior.

## Risks and Edge Cases
Unused sentinels can drift from actual enforcement. Callers receiving `ErrNotReady` should retry after BeeRemote sends configuration.

## Test Signals
No direct tests target this file. Readiness failures are not a major focus in the included manager tests, which call `UpdateConfig` during setup.
