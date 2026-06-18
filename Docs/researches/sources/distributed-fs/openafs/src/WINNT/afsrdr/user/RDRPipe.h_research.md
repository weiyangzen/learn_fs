# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.h

## Purpose
Declares the redirector pipe API and, under `RDR_PIPE_PRIVATE`, the private pipe state structure plus local copies of Windows DDK pipe information types needed by user-mode code that cannot include DDK headers.

## Important APIs, Types, And Functions
Public declarations include pipe lifecycle (`RDR_InitPipe`, `RDR_ShutdownPipe`, `RDR_SetupPipe`, `RDR_CleanupPipe`) and I/O/info calls (`RDR_Pipe_Read`, `RDR_Pipe_Write`, `RDR_Pipe_QueryInfo`, `RDR_Pipe_SetInfo`). `RDR_pipe_t` stores list links, request index, UTF-16 name, parent/root FIDs, held parent scache, flags, device state, `msrpc_conn`, and optional input/output buffers. The header defines pipe flags, device-state bits, `RDR_PIPE_MAXDATA`, `RDR_pipeProc_t`, `FILE_INFORMATION_CLASS`, and structures such as `FILE_BASIC_INFORMATION`, `FILE_STANDARD_INFORMATION`, `FILE_NAME_INFORMATION`, and `FILE_PIPE_INFORMATION`.

## Control Flow
The declared API supports the flow where redirector dispatch opens a pipe with a request index, performs multiple reads/writes and info calls against that index, and closes it later. Private declarations let `RDRPipe.c` find an instance and format Windows-compatible responses.

## State And Persistence
The header itself persists no state, but it defines the shape of per-pipe memory retained between kernel requests. Flag constants track data direction, logon/UTF-8 state, RPC/message/blocking modes, and in-call state.

## Dependencies And Integration Points
It relies on surrounding includes for `DWORD`, `ULONG`, `WCHAR`, `cm_fid_t`, `cm_req_t`, `cm_user_t`, `cm_scache_t`, and `msrpc_conn`. It bridges redirector request dispatch to MSRPC pipe handling and Windows file-information semantics.

## Risks And Test Signals
Risks are ABI/layout drift in replicated DDK structures and inconsistencies between flag constants and implementation. Compile checks on user-mode pipe code and runtime query/set-info tests are the useful signals.
