# sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.h

Purpose: declares the public interface for the OpenAFS `Time` custom control implemented in `ctl_time.cpp`.

Important APIs/types/functions: `RegisterTimeClass()` registers the window class. `TM_GETTIME` and `TM_SETTIME` are private `WM_USER` messages that pass a `SYSTEMTIME *` through `LPARAM`. `TN_CHANGE` and `TN_UPDATE` are notification codes sent to the parent through `WM_COMMAND`; this implementation actively uses `TN_UPDATE`. `TI_GetTime()` and `TI_SetTime()` are convenience macros over `SendMessage()`. The header also supplies fallback utility macros such as `THIS_HINST`, `EXPORTED`, `limit`, `inlimit`, `cxRECT`, and `cyRECT`.

Control flow: callers must register the class, create a window of class `Time`, and then use `TI_SetTime()`/`TI_GetTime()` to synchronize a `SYSTEMTIME`. Parent dialogs receive notification codes in `HIWORD(wParam)` from `WM_COMMAND`.

State and persistence behavior: the header owns no state. Its message contract exposes transient process-local state held by the control instance.

Dependencies and integration points: intended for Win32 dialog code. It relies on `windows.h`-style types and is consumed alongside `WINNT/dialog.h`, `WINNT/ctl_spinner.h`, and the OpenAFS Windows application library.

Risks: the macros do not validate HWNDs or pointers. `TM_GETTIME`/`TM_SETTIME` depend on a valid writable/readable `SYSTEMTIME *`, and the message IDs occupy a fixed `WM_USER+311/312` namespace that must not conflict with other custom control messages in the same window class.

Test signals: compile clients that include only this header after Win32 headers; verify class registration and message macros work from C/C++ dialog code; confirm callers see parent `TN_UPDATE` after changes and that the `SYSTEMTIME` pointer convention remains compatible.
