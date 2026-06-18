# sources/distributed-fs/openafs/src/WINNT/afsd/ms-srvsvc.idl

Purpose: defines the MIDL server-service (`srvsvc`) RPC contract used by the custom AFSD MSRPC transport. It mirrors Microsoft SRVSVC structures and opnums enough for Windows clients to ask the AFS SMB endpoint about shares and server metadata.

Important APIs/types/functions: declares UUID `4B324FC8-1670-01D3-1278-5A47BF6EE188`, version 3.0, `ms_union`, `SRVSVC_HANDLE`, `NET_API_STATUS`, connection/file/session/share/server/transport/security/time/DFS/alias structures, discriminated unions for enum/get-info levels, `SHARE_DEL_HANDLE`, and all SRVSVC operations. Important operations for the current implementation are `NetrShareEnum`, `NetrShareGetInfo`, and `NetrServerGetInfo`; most other declared operations are stubbed in `rpc_srvsvc.c`.

Control flow: this file is compiled by MIDL into server stubs and an interface spec consumed by `msrpc.c`. The custom MSRPC dispatcher uses the generated dispatch table after a DCE/RPC bind to this abstract syntax.

State/persistence: no runtime state in the IDL. It defines wire-level memory ownership, `[size_is]`, `[string]`, `[switch_is]`, and context-handle contracts used during marshaling.

Dependencies/integration: imports `wtypes.idl`; generated files expose `srvsvc_v3_0_s_ifspec` and server entry-point signatures. It must stay in sync with `rpc_srvsvc.c` implementations and the custom `MIDL_user_allocate`/RPC allocation shims.

Risks: the contract is large while implementation coverage is narrow; Windows clients may bind and call unsupported opnums. Any mismatch between union cases, level structs, and `rpc_srvsvc.c` allocation/population can cause marshaling faults. The file includes Microsoft-derived protocol definitions, so changes should track protocol documentation carefully.

Test signals: MIDL compile, bind negotiation via `msrpc.c`, `net view`/share enumeration client behavior, unsupported-opnum error mapping, and marshaling tests for levels 0/1/2/100/101/102/103.
