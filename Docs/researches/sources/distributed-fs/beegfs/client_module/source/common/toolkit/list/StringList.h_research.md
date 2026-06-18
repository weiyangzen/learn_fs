# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringList.h

## Purpose
Defines a non-copying list of `char*` pointers.

## Important APIs and control flow
`StringList_init/uninit/clear` delegate to `PointerList`. `StringList_addHead` and `append` store the provided string pointer without copying. `length` returns node count.

## State, dependencies, integration
The list owns only list nodes; string payload ownership remains with callers. `StrCpyList` layers copying/freeing semantics on top.

## Risks and test signals
Using `StringList` when copied ownership is needed can create dangling pointers. Tests should verify clear does not free payloads and that `StrCpyList` is used for config-loaded strings that need ownership.
