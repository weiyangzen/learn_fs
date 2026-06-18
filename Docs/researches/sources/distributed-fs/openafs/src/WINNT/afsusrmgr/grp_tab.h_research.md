## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/grp_tab.h

Purpose: declares the Groups tab dialog procedure.

Important APIs/types/functions: `BOOL CALLBACK Groups_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

Control flow: main tab construction uses this dialog proc for group-tab messages.

State and persistence behavior: implementation interacts with global search/view state but the header carries none.

Dependencies and integration points: Win32 dialog callback signature; integrated by main window/tab creation code.

Risks: signature must remain compatible with `DLGPROC`.

Test signals: tab creation should instantiate the Groups tab and route init, command, timer, notify, and context-menu messages to this proc.
