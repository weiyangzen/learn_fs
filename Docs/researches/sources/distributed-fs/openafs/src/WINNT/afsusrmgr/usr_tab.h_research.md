# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/usr_tab.h

Purpose: exposes the Users tab dialog procedure.

Important APIs/types: declares `Users_DlgProc(HWND, UINT, WPARAM, LPARAM)`, the child dialog proc installed by `window.cpp` for the users tab.

State and dependencies: no state in the header. The implementation depends on FastList/display/command infrastructure.

Risks and test signals: the dialog proc is called by the tab framework, so signature compatibility and resource ID wiring are the main integration checks.
