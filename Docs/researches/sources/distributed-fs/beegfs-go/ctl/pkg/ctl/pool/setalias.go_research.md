# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/pool/setalias.go

## Purpose
Sets a management alias for a storage pool entity.

## Important APIs, Types, And Functions
Exports `SetAlias(ctx, eid, newAlias)`.

## Control Flow
Obtains management client, converts entity ID to protobuf, and calls `SetAlias` with `EntityType_POOL`.

## State And Persistence
No local state. Alias persistence is handled by management.

## Dependencies And Integration Points
Uses common BeeGFS entity conversion and protobuf management API.

## Risks And Edge Cases
No local alias validation or conflict handling.

## Test Signals
No direct tests.
