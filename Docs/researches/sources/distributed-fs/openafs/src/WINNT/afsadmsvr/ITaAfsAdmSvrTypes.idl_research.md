# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/ITaAfsAdmSvrTypes.idl

Purpose: shared MIDL type definitions for the OpenAFS Windows administration server RPC interface.

Important APIs/types/functions: defines `ASID`, `ASOBJTYPE`, fixed `STRING[256]`, volume/account/service/file-set enums, `ASACTION` with discriminated union by action type, `ASOBJPROP` with discriminated union by object type, variable-sized `ASIDLIST`, `ASOBJPROPLIST`, and `ASACTIONLIST`, search/get enums, and parameter structs for changing cells/users/groups and creating/deleting users/groups.

Control flow: these structures are marshaled between client and server for searches, property queries, updates, callbacks, and list management. Version fields such as `verPROP_NO_OBJECT`, `verPROP_RUDIMENTARY`, and `verPROP_FIRST_SCAN` let clients request only changed cached properties.

State/persistence: the file defines wire-format state, not storage. ASIDs are pointer-sized identifiers tied to a server process, and object-property versions represent server cache freshness.

Dependencies/integration: imports `wtypes.idl` for Windows types and uses `cpp_quote` to avoid clashes with Windows/AFS class headers. It is included by the main admin-server IDL and generated client/server C++ code.

Risks/test signals: fixed string lengths can truncate names/passwords; pointer-sized `UINT_PTR` in RPC structures is ABI-sensitive; duplicate `FILESETSTATE_LOCKED` definition appears in the file. Tests should exercise MIDL generation on target compilers, 32-bit pointer assumptions, union discriminants, list allocation lengths, and versioned cache update behavior.
