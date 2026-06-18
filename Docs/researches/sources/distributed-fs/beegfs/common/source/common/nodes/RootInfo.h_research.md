# sources/distributed-fs/beegfs/common/source/common/nodes/RootInfo.h

## Purpose
Stores the current filesystem root owner node ID and whether the root is buddy mirrored.

## Important APIs, Types, And Functions
`getID()`, `getIsMirrored()`, `set()`, and `setIfDefault()` are the complete API.

## Control Flow
Every operation locks a `std::mutex`. `setIfDefault()` writes only when `id` is still invalid/zero.

## State, Persistence, And Dependencies
State is `NumNodeID id` and `bool isMirrored`. No serialization is defined here; persistence is external. Depends on `NumNodeID` and `<mutex>`.

## Integration Points
Used by management/metadata code that needs root ownership and mirroring status.

## Risks
`set()` can overwrite established root info unconditionally. Callers relying on first-writer-wins must use `setIfDefault()`.

## Test Signals
Concurrent get/set, first-writer behavior, mirrored flag propagation, and zero-ID initialization should be validated.
