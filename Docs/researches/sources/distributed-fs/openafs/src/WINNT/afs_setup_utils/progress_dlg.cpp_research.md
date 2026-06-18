# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/progress_dlg.cpp

Purpose: displays a modal progress dialog with localized UI and animated logo for setup operations that may block.

Important APIs/types/functions: exported `ShowProgressDialog(char *pszMsg)` starts a new thread running `DisplayProgressDlg()`. `HideProgressDialog()` posts `WM_QUIT` to the dialog. `ProgressDlgProc()` handles initialization and quit. `OnInitDialog()` sets message text and starts logo animation; `OnQuit()` stops animation and ends the dialog.

Control flow: caller stores a message pointer in global `pszProgressMsg`, spawns the dialog thread, and later posts quit. The modal dialog is created via `ModalDialog()` with resource `IDD_PROGRESS`.

State/persistence: global `hDlg`, `pszProgressMsg`, and `hLogo` hold dialog state. There is no persistence beyond UI lifetime.

Dependencies/integration: depends on Windows threading/dialog APIs, `talocale`, `resource.h`, and `animate_icon`.

Risks/test signals: `ShowProgressDialog()` calls `CloseHandle(hThread)` before testing `hThread != 0`; if `CreateThread()` fails, closing a null handle is unsafe. The message pointer is not copied, so caller lifetime matters. Tests should cover creation failure, show/hide sequencing, repeated calls, dialog-thread exit, and animation cleanup.
