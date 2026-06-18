# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/set_tab.cpp

Purpose: Implements the Filesets tab in the server manager UI, including list/tree display, context menus, selection-sensitive buttons, notification refresh, and drag/drop move/replica workflows.

Important APIs/functions: `Filesets_DlgProc` is the tab dialog procedure. `Filesets_OnSelect` and `Filesets_OnEndTask_Select` enable buttons after `taskSET_SELECT` returns fileset type/status. `Filesets_OnNotifyFromDispatch` refreshes display on fileset/status/alert/destroy events. `Filesets_Subclass_OnCommand` routes list commands to view changes, move/replica drop commands, or generic `StartContextCommand`. Drag helpers manage FastList drag images and target highlighting. `Filesets_ShowPopupMenu` and `Filesets_OnEndTask_Menu` build context menus based on focused identity and task-returned fileset status.

Control flow: On init, the tab is resized into the parent tab area, restores `gr.viewSet`, registers `GetItemText`, subclasses the list, applies view style, and initializes selection state. `WM_SERVER_CHANGED` updates header text based on selected server/cell/subset and monitors all object changes. Context menus delegate menu-state computation to `taskSET_MENU`; drag right-drop delegates to `taskSET_DRAGMENU`.

State and persistence: Stores list view layout in `gr.viewSet`, icon view in `gr.ivSet`, and server/aggregate expand state in per-object preferences through `Server_SavePreferences` and `Aggregates_SavePreferences`. Drag state is a file-static struct with drag source, target, image list, and target item.

Dependencies/integration: Integrates with server, service, aggregate, fileset display, move, create-replica, command dispatch, and column-management modules. It depends heavily on `FastList`, `UpdateDisplay_Filesets`, `Filesets_GetSelected/Focused`, and notification dispatch.

Risks: Drag state is global to the module and assumes one active fileset list. Context-menu enablement depends on async status; stale tasks may affect UI if selection changes before completion. `IdentifyPoint` trusts a FastList item from any target window, so only callers constrain target windows by identity type. Menu logic disables operations for clones/non-RW filesets but task handlers still need validation.

Test signals: Tree/list/report view switching, selection changes for RW/replica/clone, double-click behavior on expandable vs leaf items, server/cell/subset header text, expand persistence, context menus on header/items/empty area, drag move and drag replica targets, and dispatch refresh events.
