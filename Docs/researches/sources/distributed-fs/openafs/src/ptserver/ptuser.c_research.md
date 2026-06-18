# sources/distributed-fs/openafs/src/ptserver/ptuser.c research

## Purpose
`ptuser.c` implements the public libprot client API declared in `ptuser.h`. It initializes authenticated or unauthenticated Ubik RPC clients for the Protection Server and provides convenience wrappers that translate names to ids, enforce fixed-string safety, call generated `ubik_PR_*` RPCs, and convert ids back to names for callers.

## Important APIs, types, and functions
Initialization is handled by `pr_Initialize` and `pr_Initialize2`, which open AFS configuration, resolve cell info for `afsprot`, choose Rx security classes for noauth/token/localauth/encrypt/rxgk cases, create Rx connections to all protection servers, and initialize global `pruclient`. `pr_End` destroys that client.

CRUD and membership wrappers include `pr_CreateUser`, `pr_CreateGroup`, `pr_Delete`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetFieldsEntry`, and `pr_IsAMemberOf`. Lookup/listing wrappers include `pr_NameToId`, `pr_SNameToId`, `string_PR_IDToName`, `pr_IdToName`, `pr_SIdToName`, `pr_GetCPS`, `pr_GetCPS2`, `pr_GetHostCPS`, `pr_ListMembers`, `pr_IDListMembers`, `pr_IDListExpandedMembers`, `pr_ListOwned`, `pr_ListEntry`, `pr_ListEntries`, `pr_CheckEntryByName`, `pr_CheckEntryById`, and `pr_ListSuperGroups`.

The local `idhash`/`idchain` structures support expanded membership traversal without duplicates.

## Control flow, state, and persistence
The only durable state affected by this file is remote ptserver state reached through RPCs. Local state is the global `pruclient`, cached security level `lastLevel`, cached config directory/cell strings, and static `afsconf_dir`/cell info. `check_length` protects APIs from non-NUL-terminated or too-long `prname` values before they reach RPC code or after fixed-width names return from the server.

Many name-based operations first call `pr_NameToId` to convert one or two names, check `ANONYMOUSID` as the not-found sentinel, then call an id-based generated RPC. Listing operations often receive `prlist` ids, cast or copy them into `idlist`, call `pr_IdToName`, and free XDR allocations. `pr_IDListExpandedMembers` traverses nested groups/supergroups with a stack and hash set, tolerating `RXGEN_OPCODE` for servers without supergroup support.

## Dependencies and integration points
The file depends on Rx, Ubik client APIs, AFS config/auth/token APIs, rxgk interfaces, generated `ptclient.h`, `ptuser.h`, and `pterror.h`. It is consumed by the `pts` CLI, import tools, tests, and other OpenAFS components needing protection data.

## Risks and test signals
Global client state makes repeated initialization sensitive to cell/config/security changes and not obviously thread-local. Security-level behavior should be tested for noauth, token auth, localauth, encrypt, and rxgk paths, including fallback when tokens are unavailable. String-length checks are critical because the wire protocol carries fixed-size character vectors; tests should include boundary-length names and malformed server replies. Expanded membership traversal needs cycle/duplicate tests, supergroup and non-supergroup server tests, and memory cleanup checks for XDR results on errors.
