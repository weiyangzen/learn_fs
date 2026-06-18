# sources/distributed-fs/openafs/src/WINNT/afsrdr/user/RDRPipe.c

## Purpose
Implements user-mode state for redirector named-pipe/MSRPC endpoints. It maps kernel pipe request indexes to `RDR_pipe_t` instances, initializes MSRPC connections, proxies read/write operations to the MSRPC layer, and returns basic file/pipe information expected by Windows pipe clients.

## Important APIs, Types, And Functions
The main functions are `RDR_InitPipe`, `RDR_ShutdownPipe`, `RDR_FindPipe`, `RDR_SetupPipe`, `RDR_CleanupPipe`, `RDR_Pipe_Read`, `RDR_Pipe_Write`, `RDR_Pipe_QueryInfo`, and `RDR_Pipe_SetInfo`. `RDR_SetupPipe` converts the incoming UTF-16 pipe name to UTF-8, initializes `msrpc_conn` with `MSRPC_InitConn`, records parent/root FIDs and scache, and configures message-mode client-end device state. Read/write functions call `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`, and `MSRPC_WriteMessage`.

## Control Flow
Initialization creates a global RW lock. Setup runs under the write lock, reuses an existing pipe by index or allocates a new one, resolves/holds the parent scache, initializes the RPC connection by pipe name, and links the instance only after successful RPC init. Cleanup unlinks the instance, releases the scache, zeroes/free input/output buffers if allocated, frees the RPC connection, and frees the structure. Read, write, query-info, and set-info requests look up the instance under the lock and return `STATUS_INVALID_PIPE_STATE` when missing. Query-info supports basic, standard, and name information; set-info supports `FilePipeInformation` read/completion mode updates.

## State And Persistence
State is an in-memory doubly linked list guarded by `RDR_globalPipeLock`. Each pipe stores request index, name, parent/root FIDs, parent scache, flags, device state, and `msrpc_conn`. No registry or disk state is written. Buffers are zeroed on cleanup, although the current implementation mostly delegates payload storage to `msrpc_conn`.

## Dependencies And Integration Points
This module depends on Windows status codes and file-information layouts, OpenAFS cache-manager FIDs/scaches, `msrpc.h`, `cm_rpc.h`, `afs/afsrpc.h`, auth structures, SMB/NLS helpers, and `RDRPipe.h`. It is reached from `RDR_ProcessRequest` cases for pipe open, read, write, close, transceive, query info, and set info.

## Risks And Test Signals
Risks include lock granularity around potentially blocking MSRPC operations, exact `FILE_INFORMATION_CLASS` layout compatibility with kernel expectations, cleanup correctness when RPC init fails, and mode flag mismatches because `devstate` is initialized but only `flags` are later modified. Test signals include named-pipe open/close, message-mode read/write/transceive, file-name query buffer overflow handling, pipe mode set/query behavior, and shutdown cleanup with multiple live pipe instances.
