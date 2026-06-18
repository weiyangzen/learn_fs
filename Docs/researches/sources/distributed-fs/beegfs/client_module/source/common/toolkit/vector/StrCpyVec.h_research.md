# sources/distributed-fs/beegfs/client_module/source/common/toolkit/vector/StrCpyVec.h

## Purpose
Defines an append-only vector facade over an owning copied-string list.

## Important APIs and control flow
`init` initializes `StrCpyList` and a four-slot `char**` array. `append` copies a string into the list, grows the array by doubling when length exceeds capacity, and stores the latest copied string pointer at its index. `at` returns the indexed string. `clear` clears list contents.

## State, dependencies, integration
State is an owning string list plus an index array. Serialization treats it as list-compatible; indexed users use `at`.

## Risks and test signals
Array entries become stale after `clear` until overwritten. Allocation failures are unchecked. Tests should cover growth, copy independence, list/vector wire compatibility, and bounds behavior.
