## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.cpp

Purpose: dialog procedure for the Groups tab, including list setup, search debounce, context menu routing, and button enablement.

Important APIs/types/functions: `Groups_DlgProc`, `Groups_EnableButtons`, local timer constants `ID_SEARCH_TIMER` and `msecSEARCH_TIMER`, and a small static state record tracking last typed tick.

Control flow: init applies image lists/view settings, configures list callbacks, restores the group search pattern, and populates. Pattern edits start a debounce timer before calling `Display_PopulateGroupList`. Context-menu messages call `OnRightClick(pmGROUP, ...)`. Button/menu commands delegate to `OnContextCommand`. FastList item selection refreshes main menus and buttons; double-click posts Properties.

State and persistence behavior: writes the current group pattern into `g.szPatternGroups` through display population and uses restored group view/icon state in `gr.viewGrp`/`gr.ivGrp`.

Dependencies and integration points: depends on FastList, display helpers, command routing, main menu state, resource IDs, and AfsAppLib image lists.

Risks: debounce/timer behavior can issue refreshes after the tab is destroyed if timers are not killed on destroy paths. Button enablement is based only on selected count, while command dispatch later validates object type.

Test signals: type search filters quickly, switch tabs during debounce, use right-click and keyboard context menu, double-click group, select/deselect rows, and verify properties/membership buttons track selection.
