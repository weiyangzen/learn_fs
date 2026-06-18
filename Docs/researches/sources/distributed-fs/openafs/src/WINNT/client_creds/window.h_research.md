# sources/distributed-fs/openafs/src/WINNT/client_creds/window.h

Purpose: declares main window APIs and the tray callback message.

Important APIs/constants: `WM_TRAYICON` is defined as `WM_USER+100`; exported functions include `Main_DlgProc`, `Main_RepopulateTabs`, `Main_EnableRemindTimer`, `Main_Show`, and `Main_FindExpiredCreds`.

Control flow: no implementation. Consumers use these helpers to refresh UI, show/hide the main window, manage the reminder timer, and query expiration status.

State/persistence: none in the header. Implementations mutate global window/credential/startup state.

Dependencies/integration: included by `afscreds.h`, `trayicon.cpp`, `main.cpp`, and tab modules. Message value must not collide with other app-defined messages.

Risks: `Main_FindExpiredCreds` sounds like a query but can attempt renewals, so callers should expect side effects.

Test signals: message dispatch to tray handler and successful tab/timer function calls from other modules.
