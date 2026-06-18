# sources/distributed-fs/openafs/src/WINNT/afsd/afsrpc.idl

## Purpose
`afsrpc.idl` defines a small Microsoft RPC interface named `afsrpc` for setting and retrieving an 8-byte AFS session key associated with a UUID. It is part of Windows-specific token/session-key exchange support.

## Important APIs And Types
The interface uses an implicit binding handle `hAfsHandle`, UUID `2131bed0-5484-11d2-b6c6-006097221e3d`, and version `1.0`. It declares a local copy of a DCE-style UUID structure as `afs_uuid_t`. The two remote procedures are `AFSRPC_SetToken([in] afs_uuid_t uuid, [in] unsigned char sessionKey[8])` and `AFSRPC_GetToken([in] afs_uuid_t uuid, [out] unsigned char sessionKey[8])`, both returning `long` status codes.

## Control Flow, State, And Integration
The IDL only specifies the wire contract. Runtime behavior depends on generated MIDL stubs and server/client implementations elsewhere in the Windows AFSD tree. Conceptually, callers bind through `hAfsHandle`, identify a token/session by UUID, and exchange the fixed rxkad/DES-sized session key. State is external to this file and likely lives in the RPC server or cache-manager process.

## Dependencies, Risks, And Test Signals
The file depends on Microsoft RPC/MIDL semantics and DCE UUID layout compatibility. The fixed 8-byte key size reflects rxkad/DES-era token material and should be treated as legacy-sensitive. Test signals include MIDL generation, client/server ABI compatibility, successful set/get round trips for multiple UUIDs, not-found handling, and access-control checks in the implementation using these stubs.
