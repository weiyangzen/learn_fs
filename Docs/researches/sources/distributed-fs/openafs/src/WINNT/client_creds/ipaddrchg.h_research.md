# sources/distributed-fs/openafs/src/WINNT/client_creds/ipaddrchg.h

Purpose: exposes network-change/token-prompt integration points to C++ credentials modules.

Important APIs/types: defines custom messages `WM_OBTAIN_TOKENS` and `WM_START_SERVICE`; declares `ObtainTokensFromUserIfNeeded(HWND hWnd)` and `IpAddrChangeMonitorInit(HWND hWnd)` with C linkage for C++ callers.

Control flow: callers initialize the monitor or invoke token checks; message handling is implemented by `window.cpp`.

State/persistence: none in the header. Message payload ownership is part of the implicit contract: `WM_OBTAIN_TOKENS` carries allocated cell text to be freed by the receiver.

Dependencies/integration: requires Win32 `HWND`/`DWORD` types and shared `WM_USER` message range coordination.

Risks: message IDs can collide with other app-defined messages if not centrally managed. Pointer payloads must be width-safe and ownership-safe.

Test signals: build integration from `main.cpp` and `window.cpp`, and runtime validation that posted messages produce service start/token UI actions.
