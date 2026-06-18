# sources/distributed-fs/openafs/src/ptserver/ptclient.c

## Purpose
Provides an interactive low-level protection-server client for testing and administration. It connects through the protection library/Ubik client and exposes compact commands for entry creation, deletion, membership, ID/name translation, hash repair, and database entry dumping.

## Important APIs, Types, And Functions
Important helpers are `osi_audit`, `GetToken`, `GetString`, `CodeOk`, `PrintEntry`, `PrintHelp`, `skip`, and `main`. Commands call `ubik_PR_INewEntry`, `ubik_PR_SetFieldsEntry`, `ubik_PR_ChangeEntry`, `ubik_PR_WhereIsIt`, `ubik_PR_DumpEntry`, `ubik_PR_AddToGroup`, `ubik_PR_IDToName`, `ubik_PR_NameToID`, `ubik_PR_Delete`, `ubik_PR_RemoveFromGroup`, `ubik_PR_GetCPS`, `ubik_PR_GetHostCPS`, `ubik_PR_ListSuperGroups`, `ubik_PR_ListElements`, `ubik_PR_NewEntry`, `ubik_PR_ListMax`, `ubik_PR_SetMax`, `ubik_PR_UpdateEntry`, and high-level `pr_*` helpers.

## Control Flow
Startup parses configuration directory, server/client mode, security level, rxgk level, ignore-exist mode, and target cell. It initializes protection errors and `pr_Initialize2`, then repeatedly reads a line, tokenizes an opcode, parses typed arguments, invokes the matching RPC/library call, and prints results or errors. `PrintEntry` compensates for old byte-swapped continuation dump behavior before delegating to display formatting.

## State And Persistence
Persistent external state is the live protection database changed through server RPCs. Local state includes command buffer, parser cursor, security/confdir globals, and optional `ignoreExist`.

## Dependencies And Integration Points
Depends on Rx, Ubik protection stubs, ptuser library, pterror, display helpers, CellServDB/config files, and optional rxgk security level. It is useful for exercising ptserver operations below the polished `pts` interface.

## Risks And Test Signals
Risks include terse/unsafe commands, duplicate `fih`/`fnh` command blocks under supergroups, fixed input buffers, partial quoted-string handling, and direct hash repair operations. Test signals are successful connection at each security mode, create/change/delete/member operations, ID/name translation, CPS listing, host CPS, dump entry formatting, and hash repair on a test database.
