## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_error.cpp

Purpose: Provides asynchronous and immediate error dialogs for the Windows app library, including fatal-error behavior.

Important APIs and functions: Overloaded `ErrorDialog` and `FatalErrorDialog` accept either string pointers or resource IDs plus varargs. `ImmediateErrorDialog` shows a modal dialog synchronously. `vErrorDialog` allocates an `ERRORPARAMS` packet and routes creation through the main window via `WM_CREATE_ERROR_DIALOG`. `Error_DlgProc` formats and displays the description/status controls.

Control flow: Asynchronous calls allocate formatted text, then either call `OnCreateErrorDialog` immediately if no main window exists or post to the main window so UI is created on the main thread. `OnCreateErrorDialog` opens `IDD_APPLIB_ERROR`, posts quit for fatal dialogs, and frees allocated strings/packets. The dialog hides the status field when `dwError == 0`; otherwise it formats the status using `%e`.

State and persistence: No durable state. Transient state is an allocated `ERRORPARAMS` object transferred by message. Fatal state is represented by `fFatal` and results in `PostQuitMessage`.

Dependencies and integration points: Uses `AfsAppLib_GetMainWindow`, `AfsAppLib_GetAppName`, `AfsAppLib_TranslateError`, `FormatString`, `ModalDialogParam`, and resource IDs from `al_resource.h`/localized resources. Integrated through `WM_CREATE_ERROR_DIALOG`.

Risks: Varargs wrappers do not call `va_end`. Posting heap pointers to the main window assumes the destination outlives the packet and handles the custom message. `(LONG)(LONG_PTR)pszError` is pointer-to-integer storage and is sensitive to platform width assumptions in older code. Fatal dialogs terminate message loop after user dismissal.

Test signals: Verify resource-ID and literal-string overloads, zero/nonzero status layout, fatal quit behavior, no-main-window behavior, main-window-posted behavior, and translation fallback for unknown errors.
