# sources/distributed-fs/openafs/src/ptserver/ptuser.h research

## Purpose
`ptuser.h` declares the public libprot client API for interacting with the OpenAFS Protection Server. It is the supported header for callers that need to create/delete users and groups, manage memberships, list entries, inspect quotas/access flags, and initialize or tear down the protection client.

## Important APIs, types, and functions
Connection lifecycle APIs are `pr_Initialize`, `pr_Initialize2`, and `pr_End`. Creation/deletion/mutation APIs are `pr_CreateUser`, `pr_CreateGroup`, `pr_Delete`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetFieldsEntry`, `pr_SetMaxUserId`, and `pr_SetMaxGroupId`. Lookup and listing APIs are `pr_NameToId`, `pr_SNameToId`, `pr_IdToName`, `pr_SIdToName`, `pr_GetCPS`, `pr_GetCPS2`, `pr_GetHostCPS`, `pr_ListMembers`, `pr_IDListMembers`, `pr_IDListExpandedMembers`, `pr_ListOwned`, `pr_ListEntry`, `pr_ListEntries`, `pr_CheckEntryByName`, `pr_CheckEntryById`, `pr_IsAMemberOf`, `pr_ListMaxUserId`, `pr_ListMaxGroupId`, and `pr_ListSuperGroups`.

Several declarations include `AFS_NONNULL` annotations to document required pointers and help static analysis.

## Control flow, state, and persistence
The header does not define state, but the declared functions operate through the global client maintained in `ptuser.c`. Callers must initialize the library before issuing operations and free XDR-allocated result buffers according to the conventions of the underlying generated types. Persistent changes happen remotely on the ptserver through RPCs.

## Dependencies and integration points
The header includes `afs/ptint.h` for generated PT types such as `prname`, `namelist`, `idlist`, `prlist`, `prcheckentry`, and `prlistentries`. It is used by command-line tools (`pts`, `readpwd`, `readgroup`, `testpt`) and can be used by other OpenAFS components.

## Risks and test signals
The API shape depends on fixed-size PT names and generated XDR ownership conventions; callers can leak memory or pass invalid buffers if they ignore those rules. Because the header exposes both name-based and id-based operations, tests should cover not-found mapping through `ANONYMOUSID`, output list ownership, max-id setters, supergroup fallback behavior, and lifecycle behavior across repeated `pr_Initialize`/`pr_End` calls.
