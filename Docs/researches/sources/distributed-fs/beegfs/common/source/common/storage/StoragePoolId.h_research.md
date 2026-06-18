# sources/distributed-fs/beegfs/common/source/common/storage/StoragePoolId.h

## Purpose
Defines the strongly typed numeric storage pool ID.

## Important APIs, Types, And Functions
`StoragePoolId` is `NumericID<uint16_t, StoragePoolIdTag>` with list/vector typedefs and iterators.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. The type must remain synchronized with the client.

## Integration Points
Used by `StoragePool`, `StoragePoolStore`, `TargetMapper`, and storage-pool messages.

## Risks
The 16-bit width bounds the maximum number of pools and is protocol-visible.

## Test Signals
Zero invalid/default semantics, ordering, serialization, and client compatibility.
