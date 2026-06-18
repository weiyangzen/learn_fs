# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/delete.go

## Purpose
Thin management RPC wrapper for deleting a storage pool.

## Important APIs, Types, And Functions
Exports `Delete(ctx, req)` for `pm.DeletePoolRequest`.

## Control Flow
Gets the management client, calls `DeletePool`, and returns response/error.

## State And Persistence
No local state. Persistent deletion behavior is controlled by management.

## Dependencies And Integration Points
Depends on CTL management client and protobuf management API.

## Risks And Edge Cases
No local safety checks for non-empty or default pools.

## Test Signals
No direct tests.
