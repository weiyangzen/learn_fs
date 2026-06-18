# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svrmgr.cpp

Purpose: contains the Windows entry point and application lifecycle for AFS Server Manager.

Important APIs/functions: `WinMain` converts the ANSI command line and delegates to `InitApplication`, then runs `AfsAppLib_MainPump` and `ExitApplication`. `InitApplication` loads locale resources, enforces a single main window, initializes the AfsAppLib task queue, restores or defaults global UI settings, initializes `AfsClass`, creates notification dispatch, registers dialog classes, parses command-line options, creates the main dialog, and optionally prompts for a cell. `Quit` persists settings and decides whether to hide while actions remain active. `PumpMessage` applies accelerators and filters memory-manager messages. `StartThread` wraps `CreateThread`.

Control flow: startup builds `GLOBALS g` and `GLOBALS_RESTORED gr` before any dialogs. Defaults initialize all view definitions and behavior flags. Once `Main_DialogProc` exists, cell selection can proceed through `OpenCellDialog` or command-line opening.

State and persistence: `RestoreSettings`/`StoreSettings` serialize `gr` under `HKCU\Software\OpenAFS\AFS Server Manager`. `Quit` stores main-window placement and server-list view before leaving. `g` holds handles, selected cell identity, current subset, and credentials.

Dependencies/integration: depends on Windows, Winsock/Roken/OpenAFS config headers, AfsAppLib, AfsClass, resource modules, command-line parsing, notifications, credentials, propcache, and every default-view initializer.

Risks: `StartThread` never closes the thread handle after `CreateThread`, causing handle leaks on repeated use. Startup references `opLOOKUPERRORCODE`, which is not declared in the shown `cmdline.h` subset and must come from included headers or conditional code. Tests should cover first-run defaults, settings version migration, duplicate-instance activation, AfsClass initialization failures, command-line paths, and quit behavior with active actions.
