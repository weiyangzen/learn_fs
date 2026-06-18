# sources/distributed-fs/openafs/src/ptserver/pts.c research

## Purpose
`pts.c` implements the interactive and command-line Protection Server administration client. It registers the user-facing `pts` subcommands, parses global authentication/configuration options, calls the public `ptuser.c` API, and formats results for operators.

## Important APIs, types, and functions
Command handlers include `CreateGroup`, `CreateUser`, `AddToGroup`, `RemoveFromGroup`, `ListMembership`, `Delete`, `CheckEntry`, `ListEntries`, `ChownGroup`, `ChangeName`, `ListMax`, `SetMaxCommand`, `SetFields`, and `ListOwned`. Interactive helpers are `pts_Interactive`, `pts_Quit`, `pts_Source`, `pts_Sleep`, and `popsource`. `GetGlobals` is the command before-proc that initializes or refreshes the ptuser client according to `-cell`, `-noauth`, `-auth`, `-encrypt`, `-localauth`, `-config`, `-rxgk`, and retry rules.

`GetNameOrId` is a central resolver: it accepts mixed names and numeric ids, calls `pr_NameToId` and `pr_IdToName`, and returns aligned `idlist`/`namelist` arrays for downstream commands. Access-bit presentation and parsing are driven by `flags_upcase`, `flags_dncase`, and `flags_shift`.

## Control flow, state, and persistence
The process maintains a small mutable `authstate` with security level, initialization status, and selected cell. Every command goes through `GetGlobals`, which tears down and recreates the global `pruclient` when security or configuration changes. Persistent PT database changes happen only through `ptuser.c` wrappers such as `pr_CreateUser`, `pr_CreateGroup`, `pr_DeleteByID`, `pr_AddToGroup`, `pr_RemoveUserFromGroup`, `pr_ChangeEntry`, `pr_SetMax*`, and `pr_SetFieldsEntry`.

Interactive mode sets `source` to stdin and loops through parsed command lines until `quit`, EOF, or a source-stack unwind. The source command supports nested command files with `MAX_SOURCE_STACK_SIZE` to avoid unbounded recursion. `force` is global per command and lets batch operations continue after reasonable per-item failures.

## Dependencies and integration points
The file depends on the OpenAFS command parser, Rx, AFS config paths, `ptclient.h`, `ptuser.h`, `pterror.h`, and XDR free routines. It is the main operator entry point for the RPCs implemented in `ptprocs.c`. It also mirrors server-side access-bit encoding from `ptserver.h`, so flag parsing must remain consistent with `PRP_*` definitions and `PRIVATE_SHIFT`.

## Risks and test signals
Input handling is security-relevant because names are copied into fixed PT buffers and mixed name/id parsing has to preserve alignment between ids and names. The code relies on lower-level `ptuser.c` length checks for many operations but still allocates local fixed-size name arrays. Source-file recursion, authentication refresh, and fallback from client to server config directories should be tested. CLI regression tests should cover all subcommands, `-force`, `-rxgk`, interactive/source execution, access-string parsing, list pagination through `ListOwned`, supergroup display on servers with and without the opcode, and cleanup of XDR allocations after failures.
