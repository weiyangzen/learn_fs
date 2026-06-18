# sources/distributed-fs/openafs/src/WINNT/afssvrmgr/svc_tab.cpp

Purpose: Implements the Services tab list UI, including selection-sensitive buttons, display refresh, context menus, and command routing.

Important APIs/functions: `Services_DlgProc` is the tab procedure. `Services_OnSelect` enables restart/delete based on selected service and disables delete for BOS. `Services_OnNotifyFromDispatch` refreshes list display. `Services_SubclassListProc` routes list commands to `StartContextCommand`. `Services_ShowPopupMenu` chooses service/server/header/empty menus. `Services_OnEndTask_Menu` enables/disables start/stop/restart menu commands based on service status returned by `taskSVC_MENU`.

Control flow: On init, the tab is resized, `gr.viewSvc` restored, text callback installed, list subclassed, and selection updated. `WM_SERVER_CHANGED` subscribes to service changes for the selected server and updates header text based on server/cell/subset monitoring. Context menus on selected server identities defer to server menus; service menus are built asynchronously.

State and persistence: Stores list layout in `gr.viewSvc` on destroy and reads icon view `gr.ivSvc` for empty-area menu checkmarks. No direct service persistence.

Dependencies/integration: Uses `svr_window.h`, `svr_general.h`, `display.h`, command dispatcher, FastList, notification dispatch, and service status task data.

Risks: Menu state logic appears to use `else if (state != RUNNING)` after `if (state != STOPPED)`, which disables stop only when stopped but may leave stop enabled for starting/stopping unless task statuses constrain elsewhere. Selection actions depend on `FL_GetSelectedData` identity validity.

Test signals: Service list refresh events, BOS selection, no selection, server identity in list, start/stop menu enablement for each state, header context menu, and double-click properties.
