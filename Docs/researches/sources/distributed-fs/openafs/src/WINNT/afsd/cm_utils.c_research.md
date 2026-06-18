# sources/distributed-fs/openafs/src/WINNT/afsd/cm_utils.c

## Purpose
`cm_utils.c` provides miscellaneous Windows cache-manager utilities: global utility initialization, RPC/error-code mapping, reusable scratch-space allocation, 8.3 short-name generation and wildcard matching, hook DLL loading, OS file-version probing, SMB redirector capability detection, thread-priority adjustment for long requests, Windows/Unix/DOS time conversions, and a power-of-two helper.

## Important APIs and functions
- `cm_utilsInit()` and `cm_utilsCleanup()` initialize/finalize `cm_utilsLock` and the TLS request-start slot.
- `init_et_to_sys_error()` and `et_to_sys_error()` map unified AFS error-table values to errno values.
- `cm_MapRPCError()`, `cm_MapRPCErrorRmdir()`, and `cm_MapVLRPCError()` translate RX, Unix, volume, and VLDB errors to cache-manager error codes, honoring saved request errors on timeout.
- `cm_GetSpace()` and `cm_FreeSpace()` manage a freelist of `cm_space_t` scratch buffers.
- `cm_Is8Dot3()`, `cm_Gen8Dot3NameInt()`, `cm_Gen8Dot3NameIntW()`, and `cm_Gen8Dot3VolNameW()` validate and synthesize DOS 8.3 names.
- `cm_MatchMask()` and `szWildCardMatchFileName()` implement Windows-style wildcard matching with optional case folding and 8.3 restriction.
- `cm_TargetPerceivedAsDirectory()`, `cm_LoadAfsdHookLib()`, `cm_GetOSFileVersion()`, and `msftSMBRedirectorSupportsExtendedTimeouts()` provide Windows integration helpers.
- `cm_SetRequestStartTime()`, `cm_UpdateServerPriority()`, and `cm_ResetServerPriority()` adjust thread priority based on request duration using TLS state.
- Time helpers convert Unix time to/from Windows `FILETIME` and DOS search time.
- `cm_NextHighestPowerOf2()` rounds a 32-bit value upward to a power of two.

## Control flow
Utility initialization is lazy via `osi_Once`; `cm_GetSpace()` calls it before using the scratch-space freelist. Error mapping first resolves AFS error-table values to errno, then maps transport/server/application failures into `CM_ERROR_*` values. Wildcard matching normalizes some Windows wildcard metacharacters, compresses redundant wildcard sequences, optionally folds case, then recursively matches `*` and `?`. SMB redirector timeout detection checks OS version/service pack, possibly disables WoW64 filesystem redirection, reads `mrxsmb.sys` version, and caches the result.

## State and persistence behavior
State is limited to process memory: `cm_utilsOnce`, `cm_utilsLock`, `cm_spaceListp`, `et2sys`, and `cm_TlsRequestSlot`. Scratch spaces are recycled but never globally drained here. Timeout support detection is cached in static local variables. No persistent files are written.

## Dependencies and integration points
It depends on Windows APIs (`TlsAlloc`, file-version APIs, path helpers, module loading, thread priority, OS version, WoW64 redirection), RX error codes, OpenAFS unified error tables, cache-manager request structs, string macros from `cm_nls.h`, directory FID structures, registry/build constants, and OSI locks/time.

## Risks and edge cases
- `init_et_to_sys_error()` must be called before error-table mappings are expected; otherwise table entries remain zero.
- `cm_GetSpace()` does not check `malloc` failure before `memset`.
- `cm_FreeSpace()` accepts any pointer and does not validate it came from `cm_GetSpace()`.
- `cm_MatchMask()` allocates a new mask without NULL checking.
- `msftSMBRedirectorSupportsExtendedTimeouts()` appears to use `if (cm_GetOSFileVersion(...) || (fvFile >= min))`, which can mark support true when version retrieval succeeds even if the version is below the threshold; the likely intended condition is success and version >= minimum.
- `GetVersionEx` behavior depends on application manifesting on newer Windows versions.
- `cm_NextHighestPowerOf2(0)` returns 0 through unsigned wrap; callers must decide if that is acceptable.

## Test signals
Tests should cover RX timeout saved-error precedence, VLDB no-entry mapping, rmdir `ENOTEMPTY` variants, scratch freelist reuse, 8.3 validation/generation including high-bit and illegal characters, wildcard metacharacter normalization, case-folded matching, hook DLL path construction, SMB redirector version-threshold behavior, TLS priority reset, all time round trips, and power-of-two edge values.
