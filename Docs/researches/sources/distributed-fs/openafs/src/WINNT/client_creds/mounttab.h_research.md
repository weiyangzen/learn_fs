# sources/distributed-fs/openafs/src/WINNT/client_creds/mounttab.h

Purpose: declares the mount tab dialog procedure.

Important APIs: `BOOL CALLBACK Mount_DlgProc(HWND hDlg, UINT msg, WPARAM wp, LPARAM lp)` handles the tab and mapping dialog interactions implemented in `mounttab.cpp`.

Control flow: no implementation; `window.cpp` uses it when creating `IDD_TAB_MOUNT`.

State/persistence: none in the header. The implementation reads/writes drive-map persistence.

Dependencies/integration: included by `afscreds.h` and indirectly by the main window code.

Risks: minimal; correctness depends on preserving the Win32 callback signature.

Test signals: build and runtime creation of the mount tab when `ShowMountTab` registry policy enables it.
