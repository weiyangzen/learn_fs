# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/PointerRBTreeIter.h

## Purpose
Provides generic in-order iteration over `PointerRBTree`.

## Important APIs and control flow
`PointerRBTreeIter_init` stores the tree and current element. `next` advances with `rb_next` and returns the new element pointer. `key`, `value`, and `end` expose current element state.

## State, dependencies, integration
Used directly by generic callers and wrapped by typed map iterators. Iterator validity depends on the underlying tree not erasing the current element unexpectedly.

## Risks and test signals
`next`, `key`, and `value` require a non-end current element. Tests should validate in-order traversal and safe caller patterns around erase.
