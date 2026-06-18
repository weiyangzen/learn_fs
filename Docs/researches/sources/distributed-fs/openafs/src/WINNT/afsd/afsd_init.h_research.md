# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_init.h

## Purpose

`afsd_init.h` is the public local header for Windows AFSD initialization. It exposes startup, cache manager, SMB, daemon, shutdown, trace, crash dump, and selected global identity variables to the service wrapper and neighboring modules.

## Important APIs, Types, and Functions

- `afsi_start()` starts the initialization log.
- `afsd_InitCM(char **reasonP)` initializes the cache manager and returns failure context through `reasonP`.
- `afsd_InitSMB(char **reasonP, void *aMBfunc)` initializes or skips the SMB interface using a caller-provided message box callback.
- `GenerateMiniDump(PEXCEPTION_POINTERS ep)`, `afsd_ForceTrace(BOOL flush)`, and `afsd_SetUnhandledExceptionFilter()` expose diagnostics.
- `afsd_InitDaemons(char **reasonP)` starts background daemons.
- `afsd_ShutdownCM(void)` tears down cache-manager state.
- Extern globals include `cm_HostName`, `cm_callbackport`, `cm_NetbiosName`, and `cm_NetbiosNameC`.

## Control Flow

Consumers call these declarations in staged service startup: initialize logging, install exception handling, initialize CM, start SMB or redirector interfaces, start daemons, and later shut down CM. The header itself contains no control flow.

## State and Persistence Behavior

The header exposes mutable process-global identity/network state but does not persist anything. Its declarations allow other compilation units to read or alter the host name, callback port, and NetBIOS names initialized in `afsd_init.c`.

## Dependencies and Integration Points

The prototypes depend on Windows types (`PEXCEPTION_POINTERS`, `BOOL`) and OpenAFS `clientchar_t`. It is included by `afsd_service.c`, binding the Windows service lifecycle to initialization implementation.

## Risks

- There is no include guard in this header, so repeated inclusion relies on compatible declarations.
- The old-style `void afsi_start();` declaration does not specify a prototype argument list in C, which is weaker than `void afsi_start(void)`.
- Exposing global buffers encourages cross-module mutation without local invariants.

## Test Signals

- Build tests should compile with strict prototype warnings.
- Link tests should verify the service binary resolves all declarations from `afsd_init.c`.
- Static analysis should flag global buffer access paths and missing include guard if project policy requires guards.
