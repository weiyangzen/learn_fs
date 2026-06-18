# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/UInt16Vec.h

## Purpose
Defines an indexed append-only vector for `uint16_t` values while retaining list compatibility.

## Important APIs and control flow
`init` initializes the underlying `UInt16List` and a four-element array. `append` appends to the list, grows the array by doubling when needed, and writes the new value at index `length - 1`. `at` returns an indexed value. `clear` clears the list but keeps the allocated vector array.

## State, dependencies, integration
State is a pointer-cast value list plus a `uint16_t*` index array. Used by serialization and preferred-target style arrays.

## Risks and test signals
After `clear`, array contents are stale but inaccessible through valid length. Allocation failures are unchecked. Tests should cover capacity growth, max value, clear/reuse, and list/vector serialization compatibility.
