# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/NumNodeIDListIter.h

## Purpose
Provides typed iteration over `NumNodeIDList`.

## Important APIs and control flow
Wraps `PointerListIter`; `value` converts the pointer slot back into `NumNodeID`. `init`, `next`, and `end` mirror the generic iterator.

## State, dependencies, integration
Used by `InternodeSyncer` logging of added/removed nodes and any other node-list consumers.

## Risks and test signals
As with pointer-cast value lists, this is not suitable for values wider than pointer size. Tests should verify ordered iteration and correct reconstruction of IDs.
