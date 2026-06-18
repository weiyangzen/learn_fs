<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp

## Purpose
Parses server-manager command-line switches and turns them into startup actions.

## Important APIs, Types, And Functions
`ParseCommandLine` recognizes `cell`, `subset`, `server`, `reset`, `confirm`, `user`, `password`, `lookup`, and `useexisting`. `CommandLineHelp` displays syntax/errors.

## Control Flow
The parser scans `/` or `-` switches, handles optional colon values and quotes, rejects invalid combinations, then performs reset, credential setup, lookup mode, existing-credential open-cell, explicit cell/subset/server open-cell, or normal startup.

## State And Persistence
Static `aSWITCHES` holds parse state. Reset erases persisted preferences/settings. Credential switches update AFS credentials and possibly `g.hCreds`; cell-open flows allocate task packets/subsets.

## Dependencies And Integration Points
Uses AFS app-library credentials, subset storage, action confirmations, task framework, global credentials, and message dialogs.

## Risks And Edge Cases
Fixed-size value buffers can overflow. Prefix-style switch matching can surprise users. `useexisting` closes the app silently on credential lookup failure. Async packet ownership depends on task handling.

## Test Signals
Valid/invalid switches, quoting, duplicates, required cell/user-password combinations, reset scopes, credential failures, and `useexisting` paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrmgr/cmdline.cpp -->
