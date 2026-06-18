## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.cpp

Purpose: owns cell-opening and credential-management dialogs and status display.

Important APIs/types/functions: `OpenCell_Hook_*` implements a hook procedure for the AfsAppLib open-cell dialog. Public operations are `OpenCellDialog`, `NewCredsDialog`, `CheckForExpiredCredentials`, `CheckCredentials`, and `ShowCurrentCredentials`. Helpers `GetBadCredsDlgParams` and `GetCredentialsDlgParams` build AfsAppLib parameter blocks.

Control flow: on OK in the open-cell dialog, controls are disabled, user/cell/password text is read, credentials are acquired with `AfsAppLib_SetCredentials`, then validated with `AfsAppLib_CheckCredentials`. If validation succeeds, `g.hCreds` is set and an async `taskOPENCELL` starts; the hook only closes the dialog after `WM_ENDTASK` reports success. Failures re-enable controls and show an error.

State and persistence behavior: updates `g.hCreds` and fills default credential dialog fields from `g.idCell` or the local cell. Bad-credential warning behavior points at `gr.fWarnBadCreds`, so user preference persists with restored settings.

Dependencies and integration points: depends on AfsAppLib credential/cell dialogs, admin server task queue, `ErrorDialog`, localized strings, and global `g`/`gr`. It is called from startup, menu commands, and periodic credential checks.

Risks: passwords are held in stack `TCHAR` buffers and not explicitly wiped. `g.hCreds` is assigned before `taskOPENCELL` succeeds, so failed open attempts rely on later handling to avoid misleading state. UI disabling/enabling must match every failure path.

Test signals: test good credentials, bad passwords, insufficient credentials with warnings enabled/disabled, task open failure after credentials succeed, expired credentials, no current cell, and status display for none/expired/valid credentials.
