# sources/distributed-fs/beegfs-go/rst/sync/internal/beeremote/errors.go

## Purpose
This file defines sentinel errors for BeeSync's BeeRemote client.

## Important APIs, Types, and Functions
`ErrNilConfiguration` identifies missing dynamic BeeRemote config. `ErrInvalidAddress` identifies an empty/invalid Remote address. `ErrUnableToConnect` wraps connection setup failures.

## Control Flow
There is no executable control flow beyond error initialization.

## State and Persistence Behavior
No state is persisted. The errors define stable conditions for client initialization/update logic.

## Dependencies and Integration Points
`client.go` returns `ErrNilConfiguration` for deferred setup and `ErrInvalidAddress` for unusable config. `grpc.go` wraps transport setup failures with `ErrUnableToConnect`.

## Risks and Edge Cases
The errors are broad and rely on wrapping messages for operational detail. Callers should use `errors.Is` when they need to distinguish deferred configuration from fatal setup.

## Test Signals
No direct tests target these sentinels. They are indirectly used by work-manager startup and BeeRemote client initialization paths.
