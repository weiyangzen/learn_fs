# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMap.h

## Purpose
Defines an integer-key map facade over the generic pointer red-black tree.

## Important APIs and types
`IntMap` contains an `RBTree`. Inline lifecycle helpers initialize the generic tree with `PointerRBTree_keyCompare`. `IntMap_insert` stores integer keys directly in pointer slots and stores caller-provided `char*` values without copying. `erase`, `length`, and `clear` delegate to the generic tree.

## State, dependencies, integration
The map owns only tree elements, not value payloads. It is used as a simple utility map where caller ownership is explicit.

## Risks and test signals
Signed integer to pointer casts can be problematic for negative values. Duplicate inserts return false without replacing. Tests should cover value ownership, duplicate keys, and clear semantics.
