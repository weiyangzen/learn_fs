# sources/distributed-fs/openafs/src/WINNT/client_creds/window.cpp

Purpose: implements the main hidden/modeless window, tray menu handling, tab management, reminder timer, service-start messages, and termination dialog for `afscreds.exe`.

Important APIs/functions: `Main_DlgProc`, `Main_Show`, `Main_OnInitDialog`, `Main_OnCheckMenuRemind`, `Main_OnRemindTimer`, `Main_OnMouseOver`, `Main_OnSelectTab`, `Main_OnCheckTerminate`, `Main_CreateTabDialog`, `Main_RepopulateTabs`, `Main_EnableRemindTimer`, `Main_FindExpiredCreds`, and termination dialog handlers.

Control flow: the dialog reacts to command/menu/tray/timer/custom messages. Tab repopulation refreshes credentials, builds cell/mount/advanced tab lParams, recreates tab controls, and creates the active child dialog. The reminder timer refreshes tabs, detects expiring credentials, probes reachability, and launches credential acquisition if needed. Tray clicks show the window, wizard, or menu. `WM_START_SERVICE` starts AFSD and renews tokens.

State/persistence: reads version/user and startup policy registry values, updates `g.hMain`, `g.aCreds`, `g.fShowingMessage`, and startup registry/shortcut state in termination flows. Uses mutexes for credential and expiration state.

Dependencies/integration: central hub for `creds`, `credstab`, `advtab`, `mounttab`, `afswiz`, `trayicon`, `shortcut`, `ipaddrchg`, KFW, SCM, and localized resources.

Risks: tab lParams mix pointers and sentinel integer values cast to `LPTSTR`, which is pointer-width fragile. `WM_OBTAIN_TOKENS` casts `LPARAM` to `char *`. Expiration checks perform network/KFW work on UI timer paths. Some service stop code opens the service with `SERVICE_START` access while stopping.

Test signals: tray left/right/mousemove, tab refresh with zero/multiple cells, reminder toggle and expiration prompts, service start custom message, startup policy termination, modal termination options, and 64-bit pointer-sentinel behavior.
