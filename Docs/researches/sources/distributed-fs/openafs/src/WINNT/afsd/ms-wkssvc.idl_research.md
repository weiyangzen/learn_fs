# sources/distributed-fs/openafs/src/WINNT/afsd/ms-wkssvc.idl

Purpose: defines the MIDL workstation-service (`wkssvc`) RPC contract so the custom AFSD MSRPC transport can negotiate the well-known WKSSVC interface even if AFSD implements little or none of the workstation-management behavior.

Important APIs/types/functions: declares UUID `6BFFD098-A112-3610-9833-46C3F87E345A`, version 1.0, workstation info structures (`WKSTA_INFO_100/101/102/502` and specific setting levels), user and transport enum containers, workstation statistics, domain join status/name enums, encrypted join-password structures, `UNICODE_STRING`, computer-name arrays, and opnums such as `NetrWkstaGetInfo`, `NetrWkstaUserEnum`, `NetrGetJoinInformation`, join/unjoin/rename/validate-name, and alternate computer-name operations.

Control flow: like `ms-srvsvc.idl`, this is a compile-time wire contract. Generated server tables are included in the MSRPC interface list and selected during bind negotiation.

State/persistence: no local state. The IDL defines NDR memory and string layout for callers and generated stubs.

Dependencies/integration: imports `wtypes.idl`; generated `wkssvc_v1_0_s_ifspec` is referenced by `msrpc.c`. It shares the same custom allocation and NDR initialization shims as SRVSVC.

Risks: if clients call WKSSVC opnums without concrete server implementations, dispatch may return faults or link to missing/stub functions depending on generated code coverage elsewhere in the tree. Domain join operations are sensitive; AFSD should avoid accidentally claiming support without enforcing semantics.

Test signals: MIDL generation, bind/alter-context negotiation for WKSSVC, unsupported operation behavior, and Windows IPC clients that probe `\wkssvc`.
