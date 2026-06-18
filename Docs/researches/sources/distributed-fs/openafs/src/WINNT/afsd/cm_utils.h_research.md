# sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.h

## Purpose
`cm_utils.h` declares miscellaneous utility structures, VLDB error-code constants, error mapping APIs, scratch-space allocation, 8.3 and wildcard helpers, Windows integration helpers, time conversion helpers, interlocked bitwise helpers, and power-of-two rounding for the Windows cache manager.

## Important APIs and types
- `cm_space_t` is an 8192-character scratch buffer that can hold either client UTF-16 data or narrow data and link into a freelist.
- `VL_*` constants provide local VLDB error-code definitions used by mapping paths.
- Error APIs: `cm_MapRPCError`, `cm_MapRPCErrorRmdir`, `cm_MapVLRPCError`, and `init_et_to_sys_error`.
- Filename APIs: `cm_Is8Dot3`, `cm_Gen8Dot3Name`, `cm_Gen8Dot3NameInt`, `cm_Gen8Dot3NameIntW`, `cm_Gen8Dot3VolNameW`, and `cm_MatchMask`.
- Windows helpers: `cm_TargetPerceivedAsDirectory`, `cm_LoadAfsdHookLib`, `cm_GetOSFileVersion`, `msftSMBRedirectorSupportsExtendedTimeouts`.
- Request-priority APIs: `cm_UpdateServerPriority`, `cm_SetRequestStartTime`, and `cm_ResetServerPriority`.
- Time helpers convert between Unix, Windows search/FILETIME, and DOS search time encodings.
- Inline `cm_InterlockedAnd` and `cm_InterlockedOr` implement compare-exchange loops for debug x86 builds.
- `cm_NextHighestPowerOf2()` rounds up a 32-bit integer.

## Control flow and state behavior
The header declares the utility module's public behavior but owns no runtime state. Its inline interlocked helpers perform lock-free read-modify-write loops and are conditionally aliased to `_InterlockedOr`/`_InterlockedAnd` for debug x86 builds.

## Dependencies and integration points
It depends on `clientchar_t`, `cm_req_t`, directory FID types, Windows `HANDLE`, `FILETIME`, `LARGE_INTEGER`, and cache-manager flags such as `CM_FLAG_8DOT3` and `CM_FLAG_CASEFOLD` from surrounding includes. It is used broadly by RPC callers, directory enumeration, SMB/redirector code, and daemon/request priority paths.

## Risks and edge cases
The VLDB constants duplicate external error meanings; they must stay consistent with the VLDB protocol. The `cm_Gen8Dot3Name` macro rewrites to `cm_Gen8Dot3NameInt`, so debuggers and static analyzers should account for the macro indirection. Inline interlocked helpers assume `LONG` operands and Windows compare-exchange semantics.

## Test signals
Tests should validate macro expansion for short-name generation, VLDB error mapping constants, interlocked helper behavior under concurrent bit updates, time conversion declarations across 32-bit and 64-bit `time_t`, and compatibility with modules that include this header before or after other cache-manager headers.
