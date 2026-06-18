# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/Int64CpyListIter.h

## Purpose
Provides typed iteration over `Int64CpyList`.

## Important APIs and control flow
The iterator wraps `PointerListIter`. `init` starts at the list head, `next` advances, `value` dereferences the stored `int64_t*`, and `end` checks for completion.

## State, dependencies, integration
Iterator state is generic list iterator state. Serialization uses it to emit int64 list contents.

## Risks and test signals
`value` is invalid on end iterators or after current node removal. Tests should verify iteration order and no use-after-free during list clear.
