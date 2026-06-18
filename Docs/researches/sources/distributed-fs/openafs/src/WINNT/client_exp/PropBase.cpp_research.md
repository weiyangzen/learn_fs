# sources/distributed-fs/openafs/src/WINNT/client_exp/PropBase.cpp

Purpose: provides the base implementation shared by shell extension property pages.

Important APIs/functions: `PropertyPage::PropertyPage` copies the selected filename array; `~PropertyPage` is empty; `SetHwnd` stores the dialog window handle; base `PropPageProc` returns `FALSE`.

Control flow: derived property pages call or override these minimal behaviors. The base callback is a no-op fallback.

State/persistence: stores selected filenames and window handle in object state. No persistent writes.

Dependencies/integration: uses MFC `CStringArray` and Win32 `HWND`; derived by file, ACL, and volume property page classes.

Risks: member fields such as `m_hInst`, `m_bIsSymlink`, `m_bIsMountpoint`, and `m_bIsDir` are declared in the header but not initialized here, so creators must set them before use.

Test signals: construction copies filenames rather than aliasing, derived pages receive/set HWND, and uninitialized flags are explicitly populated by property sheet creation code.
