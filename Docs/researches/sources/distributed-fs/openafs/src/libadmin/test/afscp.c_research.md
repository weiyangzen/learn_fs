<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/afscp.c -->
# sources/distributed-fs/openafs/src/libadmin/test/afscp.c

## Purpose
Provides the main `afscp` test driver for libadmin command modules. It initializes libadmin, registers shared before/after hooks, installs command syntaxes for BOS, client, KAS, PTS, util, and VOS tests, and dispatches the selected command.

## Important APIs, Types, And Functions
Global state is `void *cellHandle`, `void *tokenHandle`, and `existing_tokens`. `MyBeforeProc` interprets common auth arguments and opens the token/cell handles. `MyAfterProc` closes them. `SetupCommonCmdArgs` appends common options at `USER_PARAM` through `USEEXISTTOKENS_PARAM`. `main` calls `afsclient_Init`, `cmd_SetBeforeProc`, `cmd_SetAfterProc`, `Setup*AdminCmd`, and `cmd_Dispatch`.

## Control Flow
Each subcommand that calls `SetupCommonCmdArgs` gets `-authuser`, `-authpassword`, `-authcell`, `-execcell`, `-noauth`, and `-usetokens`. Before command execution, the hook rejects incompatible auth combinations, defaults missing auth/exec cells to the local cell, obtains no-auth, existing, or password-derived tokens, and opens the execution cell. After the command, it closes the global handles.

## State And Persistence
The driver itself persists nothing, but it creates authenticated token and cell handles around each command. Subcommands may mutate remote AFS state through those handles. `existing_tokens` is a process-global flag set by the before hook.

## Dependencies And Integration Points
It depends on the OpenAFS command parser, client admin token/cell APIs, utility error translation via `common.h`, and setup functions declared in sibling command-module headers.

## Risks And Test Signals
There is a bug-prone path for `-noauth`: `auth_cell` is not initialized before `afsclient_TokenGetNew` if no auth cell was accepted, since `-noauth` also rejects `-authcell`. Password auth requires `-authuser`; there is no interactive prompt. Test signals should cover every auth mode, incompatible-option errors, default local-cell resolution, after-hook cleanup, and all setup modules appearing in `afscp help`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/afscp.c -->
