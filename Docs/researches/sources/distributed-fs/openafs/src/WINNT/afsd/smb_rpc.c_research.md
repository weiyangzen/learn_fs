# sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.c

## Purpose
Implements SMB named-pipe RPC support for afsd. It maps selected pipe endpoint names to internal MSRPC connections, marks SMB FIDs as RPC pipes, serializes per-FID calls, and implements core, AndX, and transaction read/write/transceive paths.

## Important APIs, Types, And Functions
`smb_RPC_SetupEndpointByname` accepts `wkssvc` and `srvsvc`, mapping to `.\\PIPE\\wkssvc` and `.\\PIPE\\srvsvc`. `smb_SetupRPCFid` strips leading path components, marks `SMB_FID_RPC`, attaches `fakeSCache`, allocates `smb_rpc_t`, initializes the endpoint, and returns message-mode pipe metadata. `smb_CleanupRPCFid` frees the MSRPC connection. I/O wrappers call `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`, and `MSRPC_WriteMessage`.

## Control Flow
Each operation calls `smb_RPC_BeginOp` under the FID mutex; concurrent callers sleep while `SMB_FID_RPC_INCALL` is set. Writes obtain the SMB user and pass request bytes to MSRPC. Reads prepare a response, cap length by client count/max return data, set SMB response parameters, and copy MSRPC bytes. `smb_RPCNmpipeTransact` writes transaction data, reads the response, creates a transaction response packet, and sends it, preserving `CM_ERROR_RPC_MOREDATA`.

## State And Persistence
`smb_rpc_t` stores the owning FID and `msrpc_conn`. The MSRPC conversation persists for the open pipe. `SMB_FID_RPC_INCALL` serializes operations and is cleared by `smb_RPC_EndOp`.

## Dependencies And Integration Points
Depends on `msrpc.h`, SMB FID/packet/user APIs, transaction helpers from `smb3.h`, Windows/NT headers, and cache-manager users. Integrates SMB named pipes with workstation and server service RPC implementations.

## Risks
Only two endpoints are accepted. Missing `smb_RPC_EndOp` can deadlock a pipe. Length safety relies on MSRPC checks and SMB client counts. User lookup failure must abort processing.

## Test Signals
Open `wkssvc`/`srvsvc`, run core and AndX pipe I/O, transaction transceive with more-data responses, concurrent same-FID requests, invalid endpoints, and disconnect/cleanup cycles.
