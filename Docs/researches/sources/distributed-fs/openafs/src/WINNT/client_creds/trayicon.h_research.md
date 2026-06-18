# sources/distributed-fs/openafs/src/WINNT/client_creds/trayicon.h

Purpose: declares the tray icon update function.

Important APIs: `void ChangeTrayIcon(int nim)` accepts Shell API `NIM_ADD`, `NIM_MODIFY`, or `NIM_DELETE` operations.

Control flow: no implementation. It is called from startup, credential refresh, and shutdown paths.

State/persistence: none in the header; implementation reads global credential state and keeps in-process add/delete flags.

Dependencies/integration: uses Shell notification constants and `WM_TRAYICON` callback integration from `window.h`.

Risks: callers may assume it is a cheap UI update, but implementation can run expiration checks.

Test signals: compile references and shell notification behavior.
