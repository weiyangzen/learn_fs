## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/mch_tab.h

Purpose: declares the Machines tab dialog procedure.

Important APIs/types/functions: `BOOL CALLBACK Machines_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)`.

Control flow: main tab creation uses this procedure to handle machine-tab messages.

State and persistence behavior: header contains no state; implementation reads/writes global machine tab view/search state.

Dependencies and integration points: Win32 `DLGPROC` callback signature and main window tab infrastructure.

Risks: must remain ABI-compatible with dialog procedure expectations.

Test signals: create Machines tab and verify init, timer, command, notify, and context-menu messages reach this callback.
