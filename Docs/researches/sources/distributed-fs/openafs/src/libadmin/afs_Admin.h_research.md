# sources/distributed-fs/openafs/src/libadmin/afs_Admin.h

## Purpose
Defines common public libadmin types shared by the OpenAFS administrative libraries. It provides platform-specific export/calling-convention macros, the common `afs_status_t` status type, RPC statistics result structures, cache-manager configuration result structures, and the portable `rxdebugHandle_t`.

## Important APIs, Types, And Functions
`ADMINAPI` is `__cdecl` on Windows and empty on Unix; `ADMINEXPORT` defaults to `__declspec(dllimport)` on Windows and empty elsewhere. `afs_status_t` is an unsigned integer status code. `afs_RPCStatsState_t`, `afs_RPCStatsVersion_t`, `afs_RPCStatsClearFlag_t`, `afs_RPCUnion_t`, and `afs_RPCStats_t` define the public RPC statistics model. `afs_ClientConfigUnion_t` and `afs_ClientConfig_t` define cache-manager configuration retrieval results. `rxdebugHandle_t` stores socket, address, port, first-query flag, and supported-statistics mask; its socket type differs between Windows and Unix.

## Control Flow
The file contains no executable control flow. It establishes the type contract used by utility, BOS, VOS, KAS, PTS, client, and configuration admin APIs.

## State And Persistence
No runtime or persistent state exists here. The structures are snapshots or handles owned by callers and populated by implementation files such as `afs_utilAdmin.c`.

## Dependencies And Integration Points
The header includes `afs/param.h`, `afs/afs_args.h`, and `rx/rx.h`. It couples libadmin public structures to Rx definitions such as `rx_function_entry_v1_t`, `cm_initparams_v1`, and Windows `SOCKET` when building on NT. All public libadmin headers include or depend on this file for consistent status and calling-convention behavior.

## Risks And Test Signals
Any change here is ABI-sensitive because it changes public structure layout or exported function decoration. Useful signals are full libadmin rebuilds on Unix and Windows, compile tests for DLL import/export mode, and binary compatibility checks for public structures consumed by external admin tools.
