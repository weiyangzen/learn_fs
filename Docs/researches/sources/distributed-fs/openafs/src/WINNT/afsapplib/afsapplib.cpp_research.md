<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp

Purpose: implements top-level AfsAppLib application identity and main-window hook behavior.

Important APIs/types/functions: static `g_hMain` and `g_szAppName` hold the current main window and display name. `AfsAppLib_SetAppName()`/`GetAppName()` copy the app name. `AfsAppLib_SetMainWindow()` subclasses the chosen window with `AfsAppLib_MainHook()` and removes the old hook. `AfsAppLib_MainHook()` dispatches library-private messages for cover windows, expired credentials, and modeless error dialogs, and clears the main window on `WM_DESTROY`.

Control flow: applications set the main window once during UI startup. Background threads can post library messages to that window so UI work runs on the UI thread. The hook forwards unhandled messages to the next subclass hook or default window procedure.

State and persistence: process-local app name and window handle only. No registry or file persistence.

Dependencies/integration: depends on `subclass.h` hook chaining, cover-window, credentials, and error-dialog implementations, plus Windows message dispatch.

Risks and test signals: global state means only one main window is supported. Destroy handling removes the hook by calling `AfsAppLib_SetMainWindow(NULL)` from inside the hook. Tests should cover hook install/remove, message dispatch to cover/credential/error handlers, chained subclass forwarding, and main-window destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/afsapplib.cpp -->
