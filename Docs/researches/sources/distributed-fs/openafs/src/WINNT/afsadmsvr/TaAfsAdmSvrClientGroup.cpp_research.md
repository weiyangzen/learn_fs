# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrClientGroup.cpp

Purpose: implements client-side wrappers for PTS group administration through the admin-server RPC interface.

Important APIs/types/functions: wrappers include `asc_GroupChange()`, `asc_GroupMembersGet()`, `asc_GroupMemberAdd()`, `asc_GroupMemberRemove()`, `asc_GroupRename()`, `asc_GroupMembershipGet()`, `asc_GroupOwnershipGet()`, `asc_GroupCreate()`, and `asc_GroupDelete()`.

Control flow: each wrapper calls the corresponding `AfsAdmSvr_*` RPC inside `RpcTryExcept`. Mutating operations refresh or probe object properties afterward: change/rename/create request full group properties for cache update; delete intentionally tries a property get and ignores failure to clean up cached state/listeners.

State/persistence: local cache may be updated after operations. Persistent group membership, ownership, names, and existence are changed on the remote AFS cell by server-side handlers.

Dependencies/integration: depends on generated group RPCs, client cache/property wrappers, and RPC exception macros.

Risks/test signals: post-mutation cache refresh can turn a successful mutation into a failed client return. Fixed `STRING` copy in rename can overflow if caller supplies an oversized name. Tests should cover each RPC wrapper, exception-to-status mapping, cache refresh paths, delete stale-cache behavior, and returned ASID list ownership.
