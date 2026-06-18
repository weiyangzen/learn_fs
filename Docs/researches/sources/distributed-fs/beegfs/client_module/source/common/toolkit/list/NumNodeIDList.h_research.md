# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDList.h

## Purpose
Defines a list of `NumNodeID` values backed by `PointerList` without per-value allocation.

## Important APIs and control flow
`NumNodeIDList_append` casts the numeric ID value through `size_t` into a pointer slot. Lifecycle and clear operations only manage list nodes. `length` delegates to the underlying pointer list.

## State, dependencies, integration
Used by node-sync code to report added/removed node IDs. Values are embedded in pointer fields rather than owned heap objects.

## Risks and test signals
The representation assumes `NumNodeID.value` fits in `size_t`; this is fine for current numeric IDs but should remain explicit. Tests should cover zero IDs and round-trip through iterator value conversion.
