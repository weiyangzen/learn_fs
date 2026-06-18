# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/admin_info_dlg.cpp

## Purpose
Implements a modal Windows dialog that collects administrator credentials and, optionally, the system control server hostname for the OpenAFS server configuration application.

## Important APIs, Types, And Functions
`GetAdminInfo` sets the requested mode and opens `IDD_ADMIN_INFO` through `ModalDialog`. `AdminInfoDlgProc` handles help, initialization, command notifications, cancel, and OK. Static helpers are `OnInitDialog`, `CheckEnableButtons`, `SaveDlgInfo`, and `ShowPageInfo`. The dialog reads/writes global `g_CfgData` fields: `szAdminName`, `szAdminPW`, and optionally `szSysControlMachine`.

## Control Flow
On initialization, the dialog stores its `HWND`, hides hostname controls when only login data is needed, moves buttons upward, and shrinks the window. It then populates controls from `g_CfgData`. Edit changes in admin name/password/hostname/SCS controls trigger `CheckEnableButtons`, which enables OK only when admin name and password are nonempty. OK saves control text into `g_CfgData` and ends with `IDOK`; cancel ends with `IDCANCEL`.

## State And Persistence
State is UI-local `hDlg`, static `eOptions`, and a static layout offset cached across invocations. User-entered values are persisted into the process-global configuration data structure; no registry or disk write occurs here.

## Dependencies And Integration Points
The file depends on Win32 dialog messaging, Winsock includes inherited by the application, `afscfg.h`, `resource.h`, UI helper functions (`ModalDialog`, `HideAndDisable`, `MoveWnd`, `SetEnable`, `GetWndText`, `SetWndText`), help integration through `AfsAppLib_HandleHelp`, and constants for maximum field lengths.

## Risks And Test Signals
Risks include password retention in global memory, `lstrncpy` truncation without explicit visible validation, OK enablement not requiring the SCS hostname even in `GAIO_GET_SCS` mode, static offset reuse if dialog resources change, and layout issues after hiding controls. Test signals include both modes rendering correctly, OK enable/disable behavior, saved field truncation boundaries, cancel preserving prior data, and help routing.
