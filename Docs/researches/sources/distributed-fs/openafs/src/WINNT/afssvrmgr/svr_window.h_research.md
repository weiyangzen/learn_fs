# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svr_window.h

Purpose: declares the server-window and preview-pane interface used throughout AFS Server Manager.

Important API/types: `SERVERWINDOW_PREVIEWPANE` aliases `g.hMain` so shared server-tab code can treat the main preview pane as a server window. `SVR_SETWINDOWPOS_PARAMS` carries an identity, window rectangle, and open/closed flag for asynchronous preference updates. Public functions cover open/close, tab preparation/display, server selection lookup, redraw/uncover, and keyboard commands.

Control flow contract: callers use `Server_Open` after retrieving a saved rectangle through `taskSVR_GETWINDOWPOS`; close paths call `Server_SaveRect` indirectly. Child dialogs use `Server_GetServerForChild` and `Server_GetWindowForChild` to resolve context.

State and persistence: this header exposes the packet used to persist `SERVER_PREF.rLast` and `fOpen`.

Dependencies/integration: depends on `CHILDTAB`, `LPIDENT`, `RECT`, and global `g` from `svrmgr.h`; used by main window, command handlers, and task code.

Risks/test signals: the preview-pane macro hides a dependency on global state. Tests should verify child-to-server resolution works for both preview and standalone windows.
