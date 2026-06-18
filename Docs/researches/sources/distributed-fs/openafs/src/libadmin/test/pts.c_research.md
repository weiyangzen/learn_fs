# sources/distributed-fs/openafs/src/libadmin/test/pts.c

## Purpose

`pts.c` implements PTS-related command handlers for the `afscp` libadmin test client. It adapts parsed command arguments to `afs_ptsAdmin` calls and prints group/user entries and iterator results for manual validation.

## Important APIs, Types, and Functions

The file covers group membership and metadata operations (`DoPtsGroupMemberAdd`, `DoPtsGroupOwnerChange`, `DoPtsGroupCreate`, `DoPtsGroupGet`, `DoPtsGroupDelete`, `DoPtsGroupModify`, `DoPtsGroupRename`, `DoPtsGroupMemberList`, `DoPtsGroupMemberRemove`, `DoPtsGroupMaxGet`, `DoPtsGroupMaxSet`) and user operations (`DoPtsUserCreate`, `DoPtsUserDelete`, `DoPtsUserGet`, `DoPtsUserRename`, `DoPtsUserModify`, `DoPtsUserMaxGet`, `DoPtsUserMaxSet`, `DoPtsUserMemberList`, `DoPtsOwnedGroupList`). `SetupPtsAdminCmd` binds all handlers to command names and parameter specifications.

Local helpers parse numeric ids (`GetIntFromString`), parse access labels into `pts_groupAccess_t` and `pts_userAccess_t`, and print `pts_GroupEntry_t` / `pts_UserEntry_t` structures.

## Control Flow

Handlers are thin and synchronous. They fetch required command parameters by enum index, convert text where needed, call a libadmin function using the global `cellHandle`, and report errors through `ERR_ST_EXT`. List operations use begin/next/done iterators and expect `ADMITERATORDONE` after the final item. `DoPtsUserModify` uses an update flag bitmask: quota changes set `PTS_USER_UPDATE_GROUP_CREATE_QUOTA`, permission changes set `PTS_USER_UPDATE_PERMISSIONS`, and partial permission updates are rejected unless all three user permission fields are supplied.

## State and Persistence Behavior

There is no local persistence. Group/user create, delete, rename, owner-change, membership, max-id, and permission calls mutate the remote protection database through libadmin. Get/list commands are read-only.

## Dependencies and Integration Points

`pts.c` includes `pts.h`, which supplies admin and command headers plus `common.h`. The file integrates with the shared test-client command registry through `SetupPtsAdminCmd` and with the global `cellHandle`.

## Risks and Edge Cases

`DoPtsGroupCreate` reports `pts_GroupMemberAdd` on group-create failure, which makes diagnostics misleading. `DoPtsGroupMaxGet` and `DoPtsUserMaxGet` retrieve values but do not print them, reducing the usefulness of those commands. `GetIntFromString` has the same weak overflow/negative handling and missing plain-C error-path return shape seen in other test files.

The group permission parser accepts `"owner"`, `"group"`, and `"any"` for all group permission fields, but the command help for some fields advertises narrower sets. Enforcement is entirely by parser, so this may accept values the command text implies should be invalid. The group update command requires all five group permissions and has a typo in the enum name (`LISTDELTE`), although the enum index still matches registration order.

## Test Signals

Regression coverage should create a user and group, add/remove membership, list both directions, rename objects, update group and user permissions, and verify iterator termination. Negative tests should cover invalid access strings, partial user permission updates, and max-id commands producing useful observable output if behavior is improved.
