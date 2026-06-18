# sources/distributed-fs/beegfs-go/rst/remote/internal/worker/requests.go

## Purpose
This file defines internal work-result metadata stored by BeeRemote for every work request assigned to a worker node.

## Important APIs, Types, and Functions
`WorkResult` stores `AssignedNode`, `AssignedPool`, and the latest protobuf `*flex.Work`. `Status` returns the mutable embedded status pointer. `InTerminalState` recognizes completed and cancelled work. `RequiresUserIntervention` recognizes failed work.

## Control Flow
The helper methods are simple status predicates used by job and worker managers. `Status` centralizes access to the protobuf status so callers can update state/message in place.

## State and Persistence Behavior
`WorkResult` is designed to be copied and Gob-encoded in job records. The comments note that `flex.Work` currently has no protobuf oneof fields, so custom Gob methods are not required for this wrapper. The latest worker result is persisted as part of `job.Job`.

## Dependencies and Integration Points
The type is used by `job.Manager`, `workermgr.Manager`, response utilities, and tests. It depends on worker `Type` and protobuf `flex.Work`.

## Risks and Edge Cases
Only `COMPLETED` and `CANCELLED` are considered terminal; `FAILED` requires user intervention and blocks automatic cleanup. If protobuf `flex.Work` changes shape, Gob compatibility may break. The mutable status pointer is convenient but allows callers to modify persisted state in place, so lock discipline must be maintained by owners.

## Test Signals
`requests_test.go` validates Gob round-tripping and checks expected protobuf field descriptors to catch shape changes that could break serialization.
