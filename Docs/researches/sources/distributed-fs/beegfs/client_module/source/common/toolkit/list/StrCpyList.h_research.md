# sources/distributed-fs/beegfs/client_module/source/common/toolkit/list/StrCpyList.h

## Purpose
Defines an owning string-copy list built on `StringList`.

## Important APIs and control flow
`StrCpyList_addHead` and `append` allocate a copy of the input C string, then store it in the underlying list. `uninit` and `clear` free all copied strings before clearing list nodes. `length` delegates to `StringList_length`.

## State, dependencies, integration
The list owns copied string payloads. Config loading, string splitting, filters, and serialization use it for mutable lists of independent strings.

## Risks and test signals
Allocation failures are not checked before `memcpy`. Tests should cover copy independence from source buffers, clear/uninit freeing, empty strings, and allocation-failure handling.
