# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/dynimport.c

## Purpose
Centralizes delayed loading of Windows/security support libraries needed by the AFS NetIDMgr plugin.

## Important APIs, Types, And Functions
Global `AfsAvailable` records import availability. `init_imports()` calls `DelayLoadLibrary()` for `advapi32.dll`, `secur32.dll`, and, on NT-family Windows, `psapi.dll`. `exit_imports()` is a placeholder for delayed import cleanup.

## Control Flow
Initialization short-circuits to `KHM_ERROR_NOT_FOUND` on any delayed-load failure, otherwise marks AFS as available and returns success. OS version detection gates PSAPI loading.

## State And Persistence
Only runtime process state is affected: delayed DLL imports and the global availability flag.

## Dependencies And Integration Points
Depends on `delayload_library.h`, `krbcompat_delayload.h`, Windows version APIs, and constants from `dynimport.h`. Called by `main.c` during module initialization and cleanup.

## Risks
`GetVersionEx()` is legacy and version-manifest sensitive. `AfsAvailable` is set even though commented code suggests a former `afscompat_init()` check. Cleanup currently does not unload delayed libraries.

## Test Signals
Module startup on NT and non-NT target variants, missing-library simulation, and verifying dependent Kerberos/security imports resolve after `init_imports()`.
