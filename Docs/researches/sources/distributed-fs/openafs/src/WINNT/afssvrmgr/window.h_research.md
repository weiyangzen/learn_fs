# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/window.h

Purpose: declares the main-window API for AFS Server Manager.

Important API/functions: `Main_DialogProc`, preview and server-view commands, menu refresh helpers, tab-child lookup, redraw thread entry, `GetTabDialog`, busy animation start/stop, icon animation, and server-view menu update.

Control flow contract: `svrmgr.cpp` passes `Main_DialogProc` to `ModelessDialog`; other modules call these helpers to update global UI state and invoke refreshes. `Main_Redraw_ThreadProc` is intended for `StartThread`.

State and persistence: the functions operate on global `g` and `gr`; the header itself declares no state. `WORKING_FPS` defines animation target cadence used by animation helpers/libraries.

Dependencies/integration: depends on Windows types and global definitions from `svrmgr.h`; used by startup, actions, server windows, and command handlers.

Risks/test signals: functions expose broad global UI mutation. Tests should verify calls are made on expected UI/thread contexts and menu states track `gr` changes.
