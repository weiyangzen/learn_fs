## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/main.cpp

Purpose: application entry point, global state owner, startup/shutdown coordinator, message pump adapter, and thread helper.

Important APIs/types/functions: defines global `GLOBALS g` and `GLOBALS_RESTORED gr`. Implements `WinMain`, `InitApplication`, `ExitApplication`, `Quit`, `PumpMessage`, and `StartThread`.

Control flow: `WinMain` converts ANSI command line to `TCHAR`, initializes, runs `AfsAppLib_MainPump`, exits, frees the command line, and returns `g.rc`. Initialization loads locale resources, prevents duplicate instances via `FindWindow`, configures AfsAppLib and the task queue, registers help, restores or initializes persisted UI/default state, registers a custom dialog class, parses command line, creates the main modeless dialog, and optionally opens the cell dialog. Exit closes current cell and admin server. Quit saves main-window placement and restored settings, then posts quit.

State and persistence behavior: `gr` is restored from and stored to registry settings (`REGSTR_SETTINGS_*`, `REGVAL_SETTINGS`) with `wVerGLOBALS_RESTORED`. First-run defaults initialize create parameters, action/user/group/machine views, icon modes, refresh interval, and user search settings.

Dependencies and integration points: ties together locale loading, AfsAppLib task queue, command-line parsing, main window dialog proc, help, credentials, admin server lifecycle, user/group/machine defaults, action window defaults, and Windows thread/message APIs.

Risks: returning `FALSE` after creating `g.hMain` or acquiring credentials depends on `ExitApplication` handling partial initialization. Duplicate-instance detection relies on class/title consistency. `StartThread` does not close the created thread handle, which can leak handles if used often.

Test signals: fresh start, restored settings start, duplicate launch, `/close` or no-cell command-line paths, failed main dialog creation, cell-open cancel, normal quit with settings persistence, and task queue/thread creation behavior.
