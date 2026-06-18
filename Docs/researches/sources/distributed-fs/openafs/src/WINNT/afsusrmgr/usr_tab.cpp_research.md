# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.cpp

Purpose: implements the Users tab dialog in the main AFS User Manager window.

Important APIs and control flow: `Users_DlgProc` initializes tab sizing, image lists, sort and text callbacks, restores `gr.viewUsr`, loads the pattern edit from `g.szPatternUsers`, and calls `Display_PopulateUserList`. Pattern changes start a debounce timer (`msecSEARCH_TIMER`) before repopulating. The Advanced button opens `Users_ShowAdvancedSearch`; context commands are routed through `OnContextCommand`; selection notifications update menus and buttons; double-click opens properties.

State and dependencies: stores last type tick in a file-static `l`. View state is persisted externally in `gr.viewUsr` through `FL_RestoreView`/`FL_StoreView`. Dependencies include FastList, display callbacks, command routing, window menu updates, and resize helpers.

Risks and test signals: timer debounce and global pattern synchronization are likely UI regressions. Tests should cover view restoration, selection-driven button/menu enablement, double-click behavior, and refresh after search text edits.
