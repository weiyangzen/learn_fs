## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.h

Purpose: public command-layer interface for the Account Manager UI.

Important APIs/types/functions: defines `POPUPMENU` with `pmUSER`, `pmGROUP`, and `pmMACHINE`, plus `OnRightClick(POPUPMENU pm, HWND hList, POINT *pptScreen = NULL)` and `OnContextCommand(WORD wCmd)`.

Control flow: callers pass the active logical list type to `OnRightClick`; the implementation chooses the proper menu and either uses explicit screen coordinates or synthesizes coordinates for keyboard context-menu use. `OnContextCommand` receives `resource.h` command IDs from menus, buttons, and accelerators.

State and persistence behavior: no direct state in the header; implementation updates global restored settings and launches tasks/dialogs.

Dependencies and integration points: used by tab dialog procedures (`grp_tab.cpp`, `mch_tab.cpp`, and the analogous user tab) to route toolbar/button/menu IDs without duplicating command logic.

Risks: adding a new tab/object class requires extending `POPUPMENU` and the implementation switch. The default `POINT *` argument ties this header to C++.

Test signals: invoke `OnRightClick` from mouse and keyboard paths for all three popup types and confirm `OnContextCommand` routes all advertised `M_*` command IDs.
