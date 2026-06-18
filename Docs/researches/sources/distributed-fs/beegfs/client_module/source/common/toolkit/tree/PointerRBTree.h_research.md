# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.h

## Purpose
Defines and mostly implements a generic red-black tree mapping `void*` keys to `void*` values.

## Important APIs and control flow
`PointerRBTree_init` sets an empty `rb_root`, length zero, and comparator. `_PointerRBTree_findElem` descends left/right based on comparator results. `PointerRBTree_insert` walks to an insertion point, rejects duplicate keys, allocates an `RBTreeElem`, links it, colors it, and increments length. `PointerRBTree_erase` finds, erases, frees the element, and decrements length. `clear` repeatedly erases the root. `PointerRBTree_keyCompare` compares raw pointer values.

## State, dependencies, integration
State is an RB root, length, and comparator. The tree owns only `RBTreeElem` nodes; key/value ownership is left to typed wrappers or callers.

## Risks and test signals
Allocation failure is not checked before storing key/value. Pointer comparison is only meaningful for pointer-cast value maps. Tests should cover duplicate rejection, erase missing key, clear with wrapper-owned keys, and allocation-failure behavior.
