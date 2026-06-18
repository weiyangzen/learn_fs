## sources/distributed-fs/openafs/src/WINNT/client_osi/dbrpc.idl

Purpose: Defines the RPC interface for remote OSI debug/statistics inspection.

Important APIs/types: Constants define remote error codes, string/int array sizes, lock type IDs, format regions, and format flags. Structures include `osi_remFormat_t`, `osi_remHyper_t`, string arrays, and `osi_remGetInfoParms_t`. RPC methods include `dbrpc_Ping`, `Open`, `GetInfo`, `Close`, and `GetFormat`.

Control flow/state: Clients open a named debug object to receive a remote file descriptor, repeatedly fetch status/info, query formatting metadata, and close the descriptor.

Dependencies/integration: Consumed by MIDL and implemented by OSI debug code elsewhere (`osidb`). Uses explicit array sizes and NDR attributes.

Risks/tests: The commented `[length_is]` for `__int64 idata` means the full fixed integer array is transmitted. Test generated stubs, 32/64-bit NDR layout, bounds on `icount`/`scount`, invalid descriptors, EOF/no-entry paths, and format metadata for each region.
