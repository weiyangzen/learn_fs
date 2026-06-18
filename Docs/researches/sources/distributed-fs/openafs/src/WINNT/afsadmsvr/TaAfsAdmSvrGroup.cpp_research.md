<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp

Purpose: implements server-side RPC handlers for PTS group mutation and relationship queries.

Important APIs/types/functions: mutation handlers include `AfsAdmSvr_ChangeGroup()`, `AddGroupMember()`, `RemoveGroupMember()`, `RenameGroup()`, `CreateGroup()`, and `DeleteGroup()`. Query handlers include `GetGroupMembers()`, `GetGroupMembership()`, and `GetGroupOwnership()`. The code builds `ASACTION` records for mutating operations and uses `AfsClass_*` group APIs. Relationship queries return `ASIDLIST` structures translated from PTS string lists.

Control flow: each handler begins an operation, logs, validates the client, opens the relevant `LPIDENT` object, performs AfsClass work, maps failures through `FALSE_()`, and ends the operation on success. `ChangeGroup()` compares incoming requested values with cached current properties to build a `GROUPPROPERTIES.dwMask` before calling `AfsClass_SetGroupProperties()`.

State and persistence: no file-local state. Persistent effects occur in AFS PTS/KAS databases through AfsClass calls. Creating a group may alter max group id, so the cell properties cache is re-tested.

Dependencies/integration: depends on `AfsClass_SetGroupProperties`, PTS group/user open methods, `IDENT::FindGroup`, `IDENT::FindUser`, `USER::SplitUserName`, list helpers, action tracking, property cache, and admin-server logging.

Risks and test signals: `GetGroupMembers()` first tries `IDENT::FindGroup()` for member names, then falls back to user lookup, which can mask ambiguous names. Several early returns after object open rely on wrapper cleanup. Ordering is not preserved in returned lists beyond enumeration order. Tests should cover valid/invalid client ids, no-op change masks, owner lookup by user or group, membership translation, create/delete property-cache updates, and failures from AfsClass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsadmsvr/TaAfsAdmSvrGroup.cpp -->
