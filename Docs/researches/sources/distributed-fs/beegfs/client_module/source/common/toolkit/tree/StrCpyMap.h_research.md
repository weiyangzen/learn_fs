# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.h

## Purpose
Defines an owning string-to-string map on top of `PointerRBTree`.

## Important APIs and control flow
`StrCpyMap_insert` allocates copies of both key and value, inserts them, and frees copies on duplicate failure. `StrCpyMap_erase` finds the element, remembers key/value pointers, erases the tree node, then frees both copies. `clear` repeatedly erases root keys until empty. Lifecycle initializes and uninitializes the generic tree.

## State, dependencies, integration
The map owns copied key and value strings plus generic tree nodes. It is a utility for configuration and metadata-style string maps.

## Risks and test signals
Allocation failures are not checked before `memcpy`. `StrCpyMap_uninit` calls `StrCpyMap_clear` and then `PointerRBTree_uninit`, whose clear is harmless on empty but redundant. Tests should cover duplicate insert, erase missing, clear freeing all strings, and allocation failure.
