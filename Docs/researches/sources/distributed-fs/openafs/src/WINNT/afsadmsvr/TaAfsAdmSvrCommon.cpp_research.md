<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp

Purpose: provides shared allocation and manipulation routines for RPC-friendly growable list structures: `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST`.

Important APIs/types/functions: `AfsAdmSvr_ReallocFunction()` reallocates structures with a fixed header and trailing flexible array, using header offset, count offset, element size, required count, increment, and fill byte. `AfsAdmSvr_Create*List()`, `Copy*List()`, `AddTo*List()`, `RemoveFrom*List()`, `IsIn*List()`, and `Free*List()` cover object ids, object properties, and actions. Removal compacts by copying the last entry over the removed slot.

Control flow: callers create an empty list, append entries as they enumerate or search, optionally copy/test/remove, and free with the matching free routine. Reallocation only grows; counts track used entries separately from allocated entries.

State and persistence: no global state. All data is heap memory allocated through OpenAFS `Allocate`/`Free`, suitable for RPC marshaling because the element array is contiguous after the structure header.

Dependencies/integration: depends on `WINNT/TaAfsAdmSvr.h` list structures, OpenAFS memory helpers, and RPC IDL conventions (`size_is`/`length_is` style arrays).

Risks and test signals: copy routines copy `cEntriesAllocated` entries, not just `cEntries`, so zero-fill correctness matters. Several add functions return `NULL` in Boolean contexts on allocation failure. Removal changes ordering, which must not matter to callers. Tests should exercise empty-list creation, growth granularity, duplicate IDs, order-insensitive removal, copy counts, and freeing null/non-null lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrCommon.cpp -->
