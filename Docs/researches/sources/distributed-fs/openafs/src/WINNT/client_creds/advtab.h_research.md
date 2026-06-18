# sources/distributed-fs/openafs/src/WINNT/client_creds/advtab.h

Purpose: declares the Advanced tab dialog procedure for the credentials UI.

Important APIs/types: `BOOL CALLBACK Advanced_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)` is the exported module-level handler used when `window.cpp` creates the `IDD_TAB_ADVANCED` modeless dialog.

Control flow: no implementation; routing is from `Main_CreateTabDialog` to this callback.

State/persistence: none in the header. Runtime state lives in `advtab.cpp` and shared `GLOBALS g`.

Dependencies/integration: included by `afscreds.h`, making the dialog procedure available throughout the client credentials app.

Risks: ABI depends on Win32 callback signature. Since the Advanced tab is conditionally compiled out of UAC-compatible builds in `window.cpp`, references must stay consistent.

Test signals: compilation and tab creation when the advanced tab is enabled.
