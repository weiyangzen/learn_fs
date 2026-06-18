# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/PointerList.h

## Purpose
Implements the generic doubly linked list used by many BeeGFS kernel containers.

## Important APIs and control flow
`PointerList_init/uninit/clear` manage list nodes. `addHead`, `addTail`, and `append` allocate a `PointerListElem` and link it. Internal helpers support inserting/removing an existing node without freeing it, used by `moveToHead` and `moveToTail`. `removeHead`, `removeTail`, and `removeElem` unlink and free nodes. `getHead`, `getTail`, and `length` expose structure state.

## State, dependencies, integration
The list owns only element nodes, not `valuePointer` payloads. Many wrappers add ownership semantics above it: string-copy and int64-copy lists free payloads; raw string/pointer lists do not.

## Risks and test signals
Allocation failures are not checked. Removing from an empty list is guarded only in debug builds. Moving the sole element removes then re-adds with length transitions. Tests should cover head/tail/middle remove, move operations, clear payload ownership expectations, and failure injection.
