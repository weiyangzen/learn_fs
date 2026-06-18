# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMap.c

## Purpose
Implements lookup, begin, and comparison functions for the copied-string map.

## Important APIs and control flow
`StrCpyMap_find` wraps generic RB-tree lookup by string key. `StrCpyMap_begin` starts iteration at `rb_first`. `compareStrCpyMapElems` orders keys using `strcmp`.

## State, dependencies, integration
The owning key/value behavior is implemented in the header. This C file supplies non-inline wrappers needed by users.

## Risks and test signals
Tests should cover lookup by a different string pointer with equal contents, because comparison is content-based.
