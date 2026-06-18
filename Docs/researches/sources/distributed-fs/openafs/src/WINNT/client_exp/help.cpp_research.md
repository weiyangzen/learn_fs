## sources/distributed-fs/openafs/src/WINNT/client_exp/help.cpp

Purpose: Chooses the appropriate legacy WinHelp file for the shell extension and dispatches help-context requests.

Important APIs/functions: `SetHelpPath` derives a help-file path from the DLL/default help path and chooses `afs-nt.hlp` on NT-family systems or `afs-light.hlp` otherwise. `ShowHelp` calls `WinHelp` with `HELP_CONTEXT`.

Control flow/state: `IsWindowsNT` caches the OS-platform check in static booleans. `strHelpPath` is global process state initialized once by application startup before dialogs invoke help.

Dependencies/integration: Uses MFC `CString`, Win32 `GetVersionEx`, and constants from `help.h`. Dialogs call `ShowHelp` in `IDHELP` handlers.

Risks/tests: `WinHelp` is legacy and may be absent on modern Windows. `SetHelpPath` assumes a backslash exists in the input path. Test startup before help invocation, NT/light selection, missing help file behavior, and every dialog help ID.
