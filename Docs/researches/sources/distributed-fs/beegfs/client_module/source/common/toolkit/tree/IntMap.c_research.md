# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.c

## Purpose
Implements find and begin operations for integer-key maps backed by `PointerRBTree`.

## Important APIs and control flow
`IntMap_find` casts the integer search key through `size_t` to a pointer key and wraps the matching tree element in `IntMapIter`. `IntMap_begin` starts at the first RB-tree node.

## State, dependencies, integration
The tree state and comparator are set in the header. This map is a utility container for code needing ordered integer keys with pointer values.

## Risks and test signals
Pointer ordering is used for integer comparison through casts. Test negative keys, zero, and large positive keys if callers use signed domains.
