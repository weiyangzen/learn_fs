## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/messages.h

Purpose: defines private main-window messages used by the application.

Important APIs/types/functions: `WM_SHOW_YOURSELF` is `WM_USER + 0x100` and asks `g.hMain` to show itself after a cell is selected/opened; `WM_SHOW_ACTIONS` is `WM_USER + 0x101` and asks the main window to open the Operations In Progress window.

Control flow: startup/secondary-instance code and task/action code post or send these messages to the main window. `WM_SHOW_YOURSELF` carries a boolean force flag in `lp`.

State and persistence behavior: no direct state; messages trigger changes in visible window/action-window state.

Dependencies and integration points: included by `main.cpp` and main-window/action handling code. Numeric values must not collide with other app-private messages.

Risks: message payload convention is documented in comments but not type-checked. Future `WM_USER` ranges must avoid these IDs.

Test signals: duplicate launch should send/show the existing window; action tasks should open the actions window through `WM_SHOW_ACTIONS`.
