# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.h

Purpose: Declares the Filesets tab dialog procedure and popup-menu helper.

Important APIs/types: `Filesets_DlgProc` plugs into the server manager tab UI. `Filesets_ShowParticularPopupMenu` lets other UI components show a fileset-specific or empty-area menu at a screen point.

Control flow/state: The popup helper allocates a menu task and starts async menu state calculation.

Dependencies/integration: Used by server/aggregate/fileset list components that need fileset context menus.

Risks/test signals: Verify callers pass a parent HWND whose parent is the expected tab/window so `StartTask(taskSET_MENU, GetParent(hParent), ...)` returns to a live handler.
