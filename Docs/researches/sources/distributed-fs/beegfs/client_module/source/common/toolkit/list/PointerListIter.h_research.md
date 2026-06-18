# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerListIter.h

## Purpose
Defines the generic iterator for `PointerList`.

## Important APIs and control flow
`PointerListIter_init` starts at the head. `next` advances to `elem->next`. `value` returns the current payload pointer. `end` checks for null. `remove` returns a new iterator pointing after the erased element while deleting the old current node.

## State, dependencies, integration
The iterator stores a list pointer and current element pointer. Component queues use the remove-return pattern while processing mutable queues.

## Risks and test signals
`next` and `value` assume the iterator is not at end. Tests should cover removal of head, tail, middle, and last element while iterating.
