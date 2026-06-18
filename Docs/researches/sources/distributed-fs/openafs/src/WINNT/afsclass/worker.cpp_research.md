# sources/distributed-fs/openafs/src/WINNT/afsclass/worker.cpp

## Purpose
`worker.cpp` implements the `afsclass` worker dispatch bridge. It dynamically loads the OpenAFS Windows admin DLLs, resolves their exported C APIs, initializes the client admin library, and exposes a single typed dispatcher, `Worker_DoTask`, that converts `WORKERTASK`/`WORKERPACKET` requests into vos, bos, kas, pts, client, and util admin calls.

## Important APIs, types, and functions
The public entry points are `Worker_Initialize` and `Worker_DoTask`. Internal functions are `Worker_LoadLibraries`, `Worker_FreeLibraries`, and `Worker_PerformTask`. Static DLL handles track `AfsVosAdmin.dll`, `AfsBosAdmin.dll`, `AfsKasAdmin.dll`, `AfsPtsAdmin.dll`, `AfsAdminUtil.dll`, and `AfsClientAdmin.dll`.

The file defines many function-pointer typedefs and static function pointers for vos volume/VLDB/server operations, bos server/process/key/log/salvage operations, kas principal/key operations, pts user/group operations, afsclient cell/server/token operations, and util database-server enumeration.

## Control flow
`Worker_DoTask` first calls `Worker_Initialize`, then wraps `Worker_PerformTask` in a catch-all C++ exception handler and reports `ERROR_UNEXP_NET_ERR` on unexpected exceptions. `Worker_Initialize` is a one-time gate around `Worker_LoadLibraries`.

`Worker_LoadLibraries` loads all required admin DLLs, resolves each required symbol with `GetProcAddress`, validates that no required pointer is null, and calls `afsclient_Init`. Loading is all-or-fail, but partial load failures return immediately without invoking `Worker_FreeLibraries`.

`Worker_PerformTask` is a large switch. Most cases map one `WORKERTASK` to one admin function call. The wrapper also converts `TCHAR` strings to ANSI and back, maps sentinel values such as `NO_PARTITION` and `NO_VOLUME` to null optional pointers, translates service/process/auth/salvage enum values, converts Unix time to/from `SYSTEMTIME`, copies encryption keys, transforms socket addresses, grows BOS log buffers until large enough, and normalizes success to status zero.

## State and persistence behavior
Worker state is process-local: DLL `HINSTANCE` handles, resolved function pointers, and the static `fInitialized` flag. The worker itself does not persist configuration. The admin calls it invokes can mutate AFS cell/server state, including volumes, VLDB entries, BOS process definitions, keys, users, groups, server host lists, executable files, authentication requirements, and salvage state.

## Dependencies and integration points
This file is the central dynamic-binding point for OpenAFS Windows admin libraries. It depends on Win32 dynamic loading, `afsclass.h`, `internal.h`, `vlserver.h`, and the admin C APIs represented in `worker.h`. It integrates UI/class-level `TCHAR` data with ANSI admin APIs and returns AFS or Win32 status codes to higher-level callers through `pStatus`.

## Risks and edge cases
The switch has a very large manual mapping surface; adding or changing a worker task requires synchronized edits in the enum, packet union, typedefs, static pointers, symbol resolution, null validation, and dispatch case. Many output buffers are caller-owned with implicit size assumptions. Some fixed temporary buffers are small for modern names or command parameters. Partial DLL-load failures leave previously loaded DLLs resident. `fInitialized` is not synchronized, so concurrent first use can race. Catch-all exception handling prevents crashes but can hide the failing task and cleanup context. Security-sensitive operations expose key, principal, BOS command, and salvage actions through a generic dispatcher, so packet correctness and caller authorization are critical.

## Test signals
Tests should cover DLL-missing and symbol-missing initialization failures, successful symbol resolution, `afsclient_Init` failure propagation, task dispatch status propagation, ANSI/TCHAR round trips, `NO_PARTITION`/`NO_VOLUME` optional pointer behavior, BOS service state/type conversions, restart-time conversions, BOS log dynamic buffer growth, address conversions, and representative vos/bos/kas/pts/client enumeration begin/next/done lifecycles. Fault-injection tests around admin call failure should assert output handles are nulled where the code promises that behavior.
