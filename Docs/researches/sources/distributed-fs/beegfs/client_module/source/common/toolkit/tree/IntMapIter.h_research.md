# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/IntMapIter.h

## Purpose
Provides typed iteration over `IntMap`.

## Important APIs and control flow
Wraps `PointerRBTreeIter`; `key` casts the current tree key back to `int`, `value` returns the stored `char*`, and `next` advances in RB-tree order.

## State, dependencies, integration
Iterator state is the generic RB-tree iterator. It is valid until the current tree element is erased.

## Risks and test signals
End iterator dereference is invalid. Tests should cover sorted iteration order and iterator behavior after erasing non-current entries.
