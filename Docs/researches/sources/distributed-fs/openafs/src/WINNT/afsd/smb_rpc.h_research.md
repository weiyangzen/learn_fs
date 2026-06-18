# sources/distributed-fs/openafs/src/WINNT/afsd/smb_rpc.h

## Purpose
Declares the SMB named-pipe RPC interface used by afsd. With `SMB_RPC_IMPL`, it defines `smb_rpc_t`, a per-FID wrapper around `msrpc_conn`.

## Important APIs, Types, And Functions
Public functions are `smb_SetupRPCFid`, `smb_CleanupRPCFid`, `smb_RPCRead`, `smb_RPCWrite`, `smb_RPCV3Read`, `smb_RPCV3Write`, and `smb_RPCNmpipeTransact`. Setup returns SMB pipe `file_type` and `device_state`.

## Control Flow
SMB open code calls setup for supported pipe endpoints. Later SMB read/write and transaction receive paths branch on `SMB_FID_RPC` and call these functions instead of normal file I/O.

## State And Persistence
No global state is declared. The implementation-owned `smb_rpc_t` persists with the FID until close and contains MSRPC connection state.

## Dependencies And Integration Points
Depends on SMB FID/VC/packet types and `smb_tran2Packet_t`; the concrete struct depends on `msrpc.h`. It connects SMB named pipes to MSRPC service dispatch.

## Risks
Opaque inclusion is intentional; only implementation code should see the concrete struct. Cleanup lock expectations must be followed. Signature drift breaks SMB receive integration.

## Test Signals
Build with opaque and implementation includes, verify pipe open metadata, core/V3 pipe I/O, transaction transceive, and no leaks after repeated closes.
