## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/creds.h

Purpose: declares the credential and cell-opening operations shared by startup, commands, and status refresh code.

Important APIs/types/functions: `OpenCellDialog` opens/selects a cell and returns dialog status; `NewCredsDialog` obtains replacement credentials; `CheckForExpiredCredentials` prompts on expiration; `CheckCredentials(BOOL fComplain)` validates current credentials; `ShowCurrentCredentials` updates the main window credential label.

Control flow: consumers call these functions around cell lifecycle events and before admin operations that require valid tokens.

State and persistence behavior: functions work against global current credentials (`g.hCreds`) and bad-credential warning preference (`gr.fWarnBadCreds`).

Dependencies and integration points: depends on AfsAppLib credential dialogs and on main-window controls such as `IDC_CREDS`.

Risks: the declaration says `OpenCellDialog` returns `int` while implementation returns `BOOL`; call sites compare to `IDOK`, so type/semantic drift is a maintenance hazard.

Test signals: compile with warnings for prototype/implementation mismatch and exercise startup/open-cell flows using the returned value.
