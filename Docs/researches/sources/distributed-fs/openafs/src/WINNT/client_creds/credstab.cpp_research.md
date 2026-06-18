# sources/distributed-fs/openafs/src/WINNT/client_creds/credstab.cpp

Purpose: implements credentials tab UI and the obtain-credentials modal dialog.

Important APIs/functions: `Creds_DlgProc`, `Creds_OnUpdate`, `Creds_OnCheckRemind`, `Creds_OnClickObtain`, `Creds_OnClickDestroy`, `ShowObtainCreds`, `NewCreds_DlgProc`, `NewCreds_OnInitDialog`, `NewCreds_OnEnable`, `NewCreds_OnOK`, and `NewCreds_OnCancel`.

Control flow: the tab receives a cell name in `DWLP_USER`, displays service/credential status, enables obtain/destroy/reminder controls, and updates reminder persistence. Obtain runs a new thread that opens a modal credential dialog. The dialog defaults the cell from the tab or root cell, pre-fills the known username, enables OK when credentials are plausible, calls `ObtainNewCredentials`, and refreshes tabs on success.

State/persistence: reads and writes `g.aCreds[i].fRemind` under `g.credsLock`, persists reminders through `SaveRemind`, uses `g.fShowingMessage` to suppress overlapping credential prompts, and mutates token state via credential APIs.

Dependencies/integration: depends on `creds.cpp`, `window.cpp` tab refresh, `TaLocale` formatting, OSI locking, and Win32 dialog controls.

Risks: `ShowObtainCreds` uses `strdup` on an `LPTSTR`, which is unsafe for Unicode builds. Dialog ownership/threading is unusual because modal dialogs are launched on a created thread. UI reads `g.aCreds[i]` after releasing the lock for checkbox state.

Test signals: no-credential tab, per-cell credential tab, reminder toggle persistence, obtain success/failure, destroy token, expired-prompt dialog, Unicode build behavior, and concurrent prompt suppression.
