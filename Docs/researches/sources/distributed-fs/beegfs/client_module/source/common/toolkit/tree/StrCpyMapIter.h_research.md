# sources/distributed-fs/beegfs/client_module/source/common/toolkit/tree/StrCpyMapIter.h

## Purpose
Provides typed iteration over `StrCpyMap`.

## Important APIs and control flow
Wraps `PointerRBTreeIter`; `key` and `value` return the copied strings, `next` advances, and `end` checks completion.

## State, dependencies, integration
Returned key/value pointers are owned by the map and valid until erasure or clear.

## Risks and test signals
Tests should validate sorted string order and ensure callers do not retain returned pointers after erasing map entries.
