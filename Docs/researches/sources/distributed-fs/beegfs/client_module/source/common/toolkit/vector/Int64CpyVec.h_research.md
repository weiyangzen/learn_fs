# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/Int64CpyVec.h

## Purpose
Defines an append-only vector facade for copied int64 values, combining list ownership with array indexing.

## Important APIs and control flow
`init` initializes the underlying `Int64CpyList` and allocates an initial pointer array of four. `append` appends to the list, doubles the pointer array when needed, and stores the newest list element's value pointer at the matching index. `at` returns the dereferenced value. `clear` clears the list but does not reset or rebuild the vector array.

## State, dependencies, integration
State includes the owning list plus `int64_t** vecArray` and capacity. Serialization reuses list-compatible wire format while consumers can index values.

## Risks and test signals
After `clear`, old array entries point to freed values until new appends overwrite them; `length` prevents valid access but stale pointers remain. Allocation failures are unchecked. Tests should cover growth, clear-then-append, bounds checks in debug builds, and uninit freeing both array and list values.
