# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/create.go

## Purpose
Thin management RPC wrapper for creating a storage pool.

## Important APIs, Types, And Functions
Exports `Create(ctx, req)` for `pm.CreatePoolRequest`.

## Control Flow
Gets the management client, calls `CreatePool`, and returns response/error unchanged.

## State And Persistence
No local state. Pool creation is persisted by the management service.

## Dependencies And Integration Points
Depends on CTL management client and protobuf management API.

## Risks And Edge Cases
No local validation or alias/id conflict handling.

## Test Signals
No direct tests.
