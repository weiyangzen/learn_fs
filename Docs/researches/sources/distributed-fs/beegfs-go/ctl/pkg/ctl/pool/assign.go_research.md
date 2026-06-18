# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/assign.go

## Purpose
Thin management RPC wrapper for assigning storage targets or buddy groups to pools.

## Important APIs, Types, And Functions
Exports `Assign(ctx, req)` accepting `pm.AssignPoolRequest` and returning `pm.AssignPoolResponse`.

## Control Flow
Initializes a management client, calls `AssignPool`, and returns the service response.

## State And Persistence
No local state. Pool membership persistence is handled by the management service.

## Dependencies And Integration Points
Uses `config.ManagementClient` and protobuf management API.

## Risks And Edge Cases
No request validation or semantic checking in this layer; callers must handle partial or rejected assignments from management response semantics.

## Test Signals
No direct tests.
