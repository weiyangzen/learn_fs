# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/UInt16List.h

## Purpose
Defines a `uint16_t` value list backed by pointer-slot casts rather than per-value allocation.

## Important APIs and control flow
Lifecycle and clear delegate to `PointerList`. `UInt16List_append` casts the value through `size_t` into a node payload pointer. `length` returns node count.

## State, dependencies, integration
Used for preferred target lists and UInt16 serialization. The list owns nodes only.

## Risks and test signals
This pattern is safe for 16-bit values but not for arbitrary pointer payloads. Tests should cover zero, max `UINT16_MAX`, and serialization round trips.
