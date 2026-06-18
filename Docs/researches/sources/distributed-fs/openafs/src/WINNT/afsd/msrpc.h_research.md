# sources/distributed-fs/openafs/src/WINNT/afsd/msrpc.h

Purpose: declares the custom MSRPC transport API, common DCE/RPC PDU structures, connection/call state, allocation shims, and well-known service helpers used by AFSD SMB IPC handling and generated MIDL stubs.

Important APIs/types/functions: maps RPC runtime names `I_RpcGetBuffer`, `I_RpcFreeBuffer`, and `NdrServerInitializeNew` to local implementations. Defines `MAX_RPC_MSG_SIZE`, `DEF_RPC_MSG_SIZE`, call statuses, PDU types, bind reject reasons, DCE/RPC scalar typedefs, `E_CommonHeader`, `msrpc_buffer`, `msrpc_call`, and `msrpc_conn`. Exports connection lifecycle (`MSRPC_InitConn`, `MSRPC_FreeConn`), transport I/O (`MSRPC_WriteMessage`, `MSRPC_PrepareRead`, `MSRPC_ReadMessageLength`, `MSRPC_ReadMessage`), RPC allocation/NDR initialization shims, `MSRPC_GetCmUser`, service init/shutdown, and `MSRPC_IsWellKnownService`.

Control flow: transport callers initialize a connection, write inbound messages, then prepare/read outbound messages until the queued call is consumed. Service implementations can call `MSRPC_GetCmUser` during dispatch to recover the authenticated/cache-manager user attached by the transport.

State/persistence: structures define in-memory queues and buffers. Ownership is explicit at connection/call level but not enforced by type system; `MSRPC_FreeConn` must drain queued calls and release held users.

Dependencies/integration: includes Windows RPC headers and `cm_nls.h`; forward-declares `cm_user_t`; generated MIDL headers depend on the local RPC shim name remapping.

Risks: public structures expose internal queue and buffer fields, so callers can corrupt invariants. Buffer length/allocation positions use unsigned int and must stay within `MAX_RPC_MSG_SIZE`. The API assumes one thread manages a connection at a time; no locks are embedded.

Test signals: compile generated stubs against remapped RPC functions, initialize/free empty and populated connections, round-trip queue status transitions, and validate `MSRPC_IsWellKnownService` matching for case-insensitive named-pipe names.
