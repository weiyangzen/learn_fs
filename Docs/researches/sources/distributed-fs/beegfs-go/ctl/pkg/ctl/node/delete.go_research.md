# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/node/delete.go

## Purpose
Thin management RPC wrapper for deleting a BeeGFS node.

## Important APIs, Types, And Functions
Exports `Delete(ctx, req)` accepting a protobuf `pm.DeleteNodeRequest` and returning `pm.DeleteNodeResponse`.

## Control Flow
The function obtains a management client from `config.ManagementClient`, calls `DeleteNode`, and returns the response or error.

## State And Persistence
No local state. Persistent effects are entirely controlled by the management service's node deletion semantics.

## Dependencies And Integration Points
Depends on CTL global management client configuration and protobuf management API.

## Risks And Edge Cases
There is no local validation, idempotency handling, or response interpretation; callers must construct valid requests and handle service-level errors.

## Test Signals
No direct tests. A mock management client would be needed to test request pass-through and error propagation.
