# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StringListIter.h

## Purpose
Provides typed iteration over `StringList`.

## Important APIs and control flow
Wraps `PointerListIter`, returning `char*` values and exposing `init`, `next`, and `end`.

## State, dependencies, integration
Used directly by string list consumers and indirectly by `StrCpyListIter`.

## Risks and test signals
Iterator values are borrowed payload pointers. Tests should cover empty-list end behavior and iteration order.
