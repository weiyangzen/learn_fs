<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c

Purpose: Implements utility functions for deterministic UUID construction/comparison, RPC stub allocation hooks, and compatibility `LARGE_INTEGER` arithmetic functions for newer MSVC builds.

Important APIs, types, and functions: `osi_LongToUID` writes a generic Cazamar UUID template with `Data1` replaced by a long value. `osi_UIDCmp` lexicographically compares UUID fields. `MIDL_user_allocate` and `MIDL_user_free` route RPC allocations to `malloc`/`free`. For `_MSC_VER >= 1300`, the file defines `LargeIntegerAdd`, `LargeIntegerSubtract`, `ExtendedLargeIntegerDivide`, `LargeIntegerDivide`, and `ConvertLongToLargeInteger`.

Control flow and state: UUID conversion is stateless. Comparisons check `Data1`, `Data2`, `Data3`, and then eight `Data4` bytes in order. Division helpers convert `LARGE_INTEGER` values to `ULONGLONG`, compute quotient/remainder, and rebuild `LARGE_INTEGER`.

Persistence and dependencies: No persistence. Dependencies include Windows/RPC UUID types, C runtime allocation, and `osiutils.h`.

Integration points: `osidebug.c` uses `osi_LongToUID` for instance ids; RPC stubs require MIDL allocation hooks; sleep/log/stat code relies on large-integer helpers when platform headers do not provide them.

Risks: `osi_UIDCmp` treats `Data4` bytes through `char *`, so signed-char platforms could affect ordering. Large integer division collapses to unsigned 64-bit arithmetic and has limited handling for divide-by-zero. `ExtendedLargeIntegerDivide` contains a placeholder overflow comment but no action.

Test signals: UUID roundtrip/ordering tests, RPC allocation/free smoke tests, large integer arithmetic compared with native operations, and divide-by-zero behavior tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/osiutils.c -->
