<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c -->
# sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c

## Purpose
Implements the public libadmin Protection Server (PTS) administration API declared in `afs_ptsAdmin.h`. It validates admin cell handles, translates PTS names and IDs, wraps ubik PR RPCs for user/group create/delete/rename/modify/member operations, and exposes iterator-style list APIs for memberships, owned groups, all users, and all groups.

## Important APIs, Types, And Functions
Public entry points include `pts_GroupMemberAdd`, `pts_GroupOwnerChange`, `pts_GroupCreate`, `pts_GroupGet`, `pts_GroupDelete`, `pts_GroupMaxGet`, `pts_GroupMaxSet`, `pts_GroupMemberListBegin/Next/Done`, `pts_GroupMemberRemove`, `pts_GroupRename`, `pts_GroupModify`, `pts_UserCreate`, `pts_UserDelete`, `pts_UserGet`, `pts_UserRename`, `pts_UserModify`, `pts_UserMaxGet`, `pts_UserMaxSet`, `pts_UserMemberListBegin/Next/Done`, `pts_OwnedGroupListBegin/Next/Done`, `pts_UserListBegin/Next/Done`, and `pts_GroupListBegin/Next/Done`. Internal helpers include `IsValidCellHandle`, `TranslatePTSNames`, `TranslateTwoNames`, `TranslateOneName`, `TranslatePTSIds`, `EntryDelete`, `GetGroupAccess`, `SetGroupAccess`, `GetUserAccess`, `SetUserAccess`, and `IsAdministrator`.

## Control Flow
Most functions follow a common pattern: cast the opaque `cellHandle` to `afs_cell_handle_p`, validate it with `CellHandleIsValid` plus PTS-specific fields, validate caller arguments, translate names through `ubik_PR_NameToID`, execute one PR RPC, map RPC status into `afs_status_t`, and free any ubik-allocated arrays before returning boolean success. Group and user getters call `ubik_PR_ListEntry`, decode PTS flag bits into libadmin access enums, then translate owner and creator IDs back to names with `string_PR_IDToName`. Modify functions build `PR_SF_*` masks and call `ubik_PR_SetFieldsEntry`.

Membership iteration is split between two models. Group/user membership lists are fetched in one `ubik_PR_ListElements` RPC during `Begin`, translated to names immediately, and `Next` just copies from an in-memory namelist under a per-iterator mutex. Owned-group and all-user/all-group listings use the generic `afs_admin_iterator_t` from adminutil; their RPC callbacks page through `ubik_PR_ListOwned` or `ubik_PR_ListEntries`, translate/cache batches, and let `IteratorNext` deliver one name at a time.

## State And Persistence
The file does not persist data locally; all durable state is in the PTS database reached through the cell handle's ubik PR client. Transient state includes ubik `namelist`, `idlist`, and `prlist` buffers, custom membership iterators with magic values and pthread mutexes, and generic admin iterator private structs (`owned_group_list_t`, `pts_list_t`). The mutation APIs change PTS entries, max user/group IDs, flags, memberships, owners, and names on the server.

## Dependencies And Integration Points
It depends on `afs_AdminInternal.h` for cell handles, iterator machinery, magic constants, and cached-item sizing; `afs_AdminErrors.h` for libadmin status codes; `afs_utilAdmin.h` for shared admin conventions; and `ptint.h`/`ptserver.h` for PR RPC types/constants. Integration is through libadmin clients that already opened a cell with a valid PTS connection.

## Risks And Test Signals
There are visible maintenance risks: `TranslateTwoNames` checks `names.namelist_val[0]` twice, so the second name length guard appears wrong; `MemberListBegin` receives custom error codes but hardcodes group-name errors in some branches; and several paths trust caller output buffers to be at least `PTS_MAX_NAME_LEN`. Iterator cleanup must free ubik-allocated arrays exactly once. Test signals should cover invalid handles, too-long first and second names, user/group create with explicit and generated IDs, membership add/remove, flag decoding/encoding, owner/creator translation, admin quota reporting, exhausted iterators returning `ADMITERATORDONE`, and cleanup after failed ubik calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/pts/afs_ptsAdmin.c -->
