# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTree.c

## Purpose
Implements exported begin/find wrappers for the generic pointer-key red-black tree.

## Important APIs and control flow
`PointerRBTree_find` calls `_PointerRBTree_findElem` and wraps the result in an `RBTreeIter`. `PointerRBTree_begin` finds the first node with `rb_first` and initializes an iterator or end iterator.

## State, dependencies, integration
The generic tree stores `void*` keys/values and a comparator defined at init. Typed maps such as `IntMap`, `StrCpyMap`, `AckStoreMap`, and `WaitAckMap` layer semantics above it.

## Risks and test signals
The generic iterator exposes raw values. Tests should cover empty tree begin, missing find, and sorted begin for each comparator.
