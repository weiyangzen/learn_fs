# sources/distributed-fs/beegfs/common/source/common/nodes/NumNodeID.h

## Purpose
Defines the strongly typed numeric node ID used across BeeGFS node, target, and store code.

## Important APIs, Types, And Functions
`NumNodeID` is `NumericID<uint32_t, NumNodeIDTag>`. The header also defines list/vector typedefs and iterators.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No owned state. It depends on `NumericID.h`. The comment requires sync with the client module.

## Integration Points
Used by node stores, target maps, root info, capacity pools, and serialization contracts.

## Risks
Changing underlying width or semantics breaks on-wire and client-kernel compatibility.

## Test Signals
Serialization, ordering, zero-invalid semantics, and client-module ABI consistency should be checked.
