# sources/distributed-fs/beegfs/client_module/source/common/toolkit/ackstore/AckStoreMapIter.h

## Purpose
Provides a typed iterator wrapper over `PointerRBTreeIter` for `AckStoreMap`.

## Important APIs and control flow
`AckStoreMapIter_init` initializes the embedded RB-tree iterator. `AckStoreMapIter_value` returns the current `AckStoreEntry*`. `AckStoreMapIter_end` reports whether iteration is complete.

## State, dependencies, integration
Iterator state is a generic RB-tree iterator cast to typed accessors. It is used by acknowledgment store lookup paths.

## Risks and test signals
Calling `value` on an end iterator dereferences a null tree element through the generic iterator. Tests should assert callers check `end` before value access.
