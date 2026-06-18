# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyListIter.h

## Purpose
Provides typed iteration over owning copied-string lists.

## Important APIs and control flow
Wraps `StringListIter` to return `char*` values. `init`, `next`, `value`, and `end` mirror the underlying iterator.

## State, dependencies, integration
Used by filter parsing and serialization to walk configuration string rows.

## Risks and test signals
Returned strings are owned by the list and become invalid after list clear/uninit. Tests should cover iteration over empty and multi-element lists.
